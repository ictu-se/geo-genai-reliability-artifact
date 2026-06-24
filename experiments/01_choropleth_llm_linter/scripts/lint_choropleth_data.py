#!/usr/bin/env python3
"""Rule-based lint checks for the choropleth input data and rendered outputs."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import geopandas as gpd
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT / "data/repos/Materials-for-Creating-maps-by-Artificial-Intelligence/data_choropleth"
OUT_DIR = ROOT / "experiments/01_choropleth_llm_linter/outputs"
MAP_DIR = OUT_DIR / "baseline_maps"


@dataclass
class Finding:
    severity: str
    check: str
    message: str


def add(findings: list[Finding], severity: str, check: str, message: str) -> None:
    findings.append(Finding(severity=severity, check=check, message=message))


def lint_csv(findings: list[Finding]) -> None:
    path = DATA_DIR / "MCD64.006.yearly-ba-nf.2002-2022.PRT_Portugal.csv"
    df = pd.read_csv(path)
    required = {"Year", "Burned Area [ha]", "Number of Fires"}
    missing = required.difference(df.columns)
    if missing:
        add(findings, "error", "csv.required_columns", f"CSV is missing required columns: {sorted(missing)}")
    if df.empty:
        add(findings, "error", "csv.nonempty", "CSV has no rows.")
    if "Year" in df and (df["Year"].duplicated().any()):
        add(findings, "warning", "csv.unique_year", "CSV contains duplicate years.")
    for col in required.intersection(df.columns):
        if df[col].isna().any():
            add(findings, "warning", "csv.missing_values", f"Column {col!r} contains missing values.")


def lint_geodata(findings: list[Finding], shp_name: str, thematic_columns: list[str]) -> gpd.GeoDataFrame:
    path = DATA_DIR / shp_name
    gdf = gpd.read_file(path)
    if gdf.empty:
        add(findings, "error", f"{shp_name}.nonempty", "Shapefile has no features.")
    if gdf.crs is None:
        add(
            findings,
            "error",
            f"{shp_name}.crs",
            "Shapefile has no CRS. The coordinates look like lon/lat, but a renderer should explicitly set EPSG:4326.",
        )
    invalid = int((~gdf.geometry.is_valid).sum())
    if invalid:
        add(findings, "error", f"{shp_name}.valid_geometry", f"{invalid} geometries are invalid.")
    empty = int(gdf.geometry.is_empty.sum())
    if empty:
        add(findings, "error", f"{shp_name}.empty_geometry", f"{empty} geometries are empty.")
    for col in thematic_columns:
        if col not in gdf.columns:
            add(findings, "error", f"{shp_name}.thematic_column", f"Missing thematic column {col!r}.")
            continue
        if not pd.api.types.is_numeric_dtype(gdf[col]):
            add(findings, "error", f"{shp_name}.{col}.numeric", f"Thematic column {col!r} is not numeric.")
        if gdf[col].isna().any():
            add(findings, "warning", f"{shp_name}.{col}.missing", f"Thematic column {col!r} has missing values.")
    if "Region" in gdf.columns and gdf["Region"].duplicated().any():
        add(findings, "warning", f"{shp_name}.unique_region", "Region names are not unique.")
    return gdf


def lint_outputs(findings: list[Finding]) -> None:
    expected = [
        MAP_DIR / "portugal_burned_area_static.png",
        MAP_DIR / "portugal_burned_area_interactive.html",
    ]
    for path in expected:
        if not path.exists():
            add(findings, "warning", "outputs.expected_file", f"Expected rendered output is missing: {path.relative_to(ROOT)}")
        elif path.stat().st_size == 0:
            add(findings, "error", "outputs.nonempty_file", f"Rendered output is empty: {path.relative_to(ROOT)}")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    findings: list[Finding] = []
    lint_csv(findings)
    lint_geodata(findings, "boundary.shp", [])
    mainland = lint_geodata(findings, "mainlandburn.shp", ["Burned_Are", "of_Fires"])
    if len(mainland) < 10:
        add(findings, "warning", "mainlandburn.coverage", f"Only {len(mainland)} regions found; confirm this matches mainland Portugal districts.")
    lint_outputs(findings)

    summary = {
        "error_count": sum(1 for f in findings if f.severity == "error"),
        "warning_count": sum(1 for f in findings if f.severity == "warning"),
        "findings": [asdict(f) for f in findings],
    }
    out_path = OUT_DIR / "lint_report.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"Wrote {out_path.relative_to(ROOT)}")
    print(f"errors={summary['error_count']} warnings={summary['warning_count']}")
    for f in findings:
        print(f"[{f.severity}] {f.check}: {f.message}")


if __name__ == "__main__":
    main()

