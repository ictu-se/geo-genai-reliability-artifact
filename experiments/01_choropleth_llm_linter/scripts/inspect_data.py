#!/usr/bin/env python3
"""Inspect the Portugal wildfire choropleth inputs."""

from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT / "data/repos/Materials-for-Creating-maps-by-Artificial-Intelligence/data_choropleth"
OUT_DIR = ROOT / "experiments/01_choropleth_llm_linter/outputs"


def summarize_frame(df: pd.DataFrame) -> dict:
    return {
        "rows": int(len(df)),
        "columns": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "missing_values": {col: int(count) for col, count in df.isna().sum().items()},
    }


def summarize_geo(path: Path) -> dict:
    gdf = gpd.read_file(path)
    return {
        "file": str(path.relative_to(ROOT)),
        "rows": int(len(gdf)),
        "columns": list(gdf.columns),
        "crs": str(gdf.crs) if gdf.crs else None,
        "geometry_types": {k: int(v) for k, v in gdf.geom_type.value_counts().items()},
        "bounds": [float(x) for x in gdf.total_bounds],
        "invalid_geometries": int((~gdf.geometry.is_valid).sum()),
        "empty_geometries": int(gdf.geometry.is_empty.sum()),
        "non_geometry_preview": gdf.drop(columns="geometry").head(5).to_dict(orient="records"),
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    csv_path = DATA_DIR / "MCD64.006.yearly-ba-nf.2002-2022.PRT_Portugal.csv"
    csv_df = pd.read_csv(csv_path)

    report = {
        "data_dir": str(DATA_DIR.relative_to(ROOT)),
        "csv": {
            "file": str(csv_path.relative_to(ROOT)),
            **summarize_frame(csv_df),
            "numeric_summary": csv_df.describe().to_dict(),
            "preview": csv_df.head(8).to_dict(orient="records"),
        },
        "shapefiles": {
            "boundary": summarize_geo(DATA_DIR / "boundary.shp"),
            "mainlandburn": summarize_geo(DATA_DIR / "mainlandburn.shp"),
        },
    }

    out_path = OUT_DIR / "data_inspection.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote {out_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

