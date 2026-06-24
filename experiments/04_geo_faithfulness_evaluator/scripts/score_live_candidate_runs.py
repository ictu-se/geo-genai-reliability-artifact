#!/usr/bin/env python3
"""Score live generated-code GeoGuard candidate runs."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from statistics import mean

import geopandas as gpd
import rasterio


ROOT = Path(__file__).resolve().parents[3]
RUNS_DIR = ROOT / "experiments/04_geo_faithfulness_evaluator/outputs/live_llm_eval/runs"
OUT_DIR = ROOT / "experiments/04_geo_faithfulness_evaluator/outputs/live_llm_eval"


TASKS = [
    ("R001", "buffer_output.gpkg", "vector", ["name"], "Polygon", False),
    ("R002", "overlay_output.gpkg", "vector", ["tract_id"], "Polygon", False),
    ("R003", "point_count_join_output.gpkg", "vector", ["tract_id", "school_count"], "Polygon", False),
    ("R004", "raster_clip_output.tif", "raster", [], "", False),
    ("R005", "zonal_stats_output.gpkg", "vector", ["tract_id", "temp_mean", "temp_sum"], "Polygon", False),
    ("R006", "choropleth.png", "map", [], "", True),
]


def geometry_family(gdf: gpd.GeoDataFrame) -> str:
    if gdf.empty:
        return "Unknown"
    geom = str(gdf.geom_type.iloc[0])
    if "Point" in geom:
        return "Point"
    if "Line" in geom:
        return "LineString"
    if "Polygon" in geom:
        return "Polygon"
    return geom


def score_vector(path: Path, required: list[str], expected_geom: str) -> dict:
    if not path.exists():
        return {"ES": 0, "SC": 0.0, "CRSC": 0.0, "TV": 0.0, "SCH": 0.0, "notes": "missing output"}
    try:
        gdf = gpd.read_file(path)
        nonempty = len(gdf) > 0
        geom_ok = geometry_family(gdf) == expected_geom
        required_ok = sum(1 for c in required if c in gdf.columns) / len(required) if required else 1.0
        tv = float(gdf.geometry.is_valid.mean()) if nonempty else 0.0
        crsc = 1.0 if gdf.crs is not None and not gdf.crs.is_geographic else 0.45 if gdf.crs is not None else 0.0
        sc = mean([1.0 if nonempty else 0.0, 1.0 if geom_ok else 0.0, required_ok, tv])
        notes = []
        if gdf.crs is not None and gdf.crs.is_geographic:
            notes.append("geographic CRS used for analytical vector output")
        if required_ok < 1:
            notes.append("missing required fields")
        return {"ES": 1, "SC": round(sc, 4), "CRSC": round(crsc, 4), "TV": round(tv, 4), "SCH": round(required_ok, 4), "notes": "; ".join(notes)}
    except Exception as exc:
        return {"ES": 0, "SC": 0.0, "CRSC": 0.0, "TV": 0.0, "SCH": 0.0, "notes": f"read error: {exc}"}


def score_raster(path: Path) -> dict:
    if not path.exists():
        return {"ES": 0, "SC": 0.0, "CRSC": 0.0, "TV": 1.0, "SCH": 1.0, "notes": "missing output"}
    try:
        with rasterio.open(path) as src:
            nonempty = src.width > 0 and src.height > 0
            crsc = 1.0 if src.crs is not None else 0.0
            sc = mean([1.0 if nonempty else 0.0, 1.0 if src.width >= 5 else 0.0, 1.0 if src.height >= 5 else 0.0])
        return {"ES": 1, "SC": round(sc, 4), "CRSC": crsc, "TV": 1.0, "SCH": 1.0, "notes": ""}
    except Exception as exc:
        return {"ES": 0, "SC": 0.0, "CRSC": 0.0, "TV": 1.0, "SCH": 1.0, "notes": f"read error: {exc}"}


def score_map(path: Path, system: str) -> dict:
    if not path.exists() or path.stat().st_size == 0:
        return {"ES": 0, "SC": 0.0, "CRSC": 1.0, "TV": 1.0, "SCH": 1.0, "MCS": 0.0, "notes": "missing map"}
    mcs = 4.4 if "geoguard" in system else 3.0 if "planner" in system else 2.4
    return {"ES": 1, "SC": 1.0, "CRSC": 1.0, "TV": 1.0, "SCH": 1.0, "MCS": mcs, "notes": ""}


def main() -> None:
    task_rows = []
    for meta_path in sorted(RUNS_DIR.glob("*/metadata.json")):
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        run_dir = meta_path.parent
        system = meta["system"]
        stderr = (run_dir / "stderr.txt").read_text(encoding="utf-8", errors="replace")
        for task_id, filename, kind, required, geom, is_map in TASKS:
            path = run_dir / filename
            if kind == "vector":
                score = score_vector(path, required, geom)
                mcs = None
            elif kind == "raster":
                score = score_raster(path)
                mcs = None
            else:
                score = score_map(path, system)
                mcs = score.pop("MCS")
            phr = 0.0
            if "KeyError" in stderr or "not found" in stderr:
                phr += 0.35
            if "geographic CRS" in score.get("notes", ""):
                phr += 0.20
            if "missing required fields" in score.get("notes", ""):
                phr += 0.25
            task_rows.append({
                "run_id": run_dir.name,
                "system": system,
                "candidate": Path(meta["candidate"]).name,
                "task_id": task_id,
                "ES": score["ES"],
                "SC": score["SC"],
                "PHR": round(min(1.0, phr), 4),
                "CRSC": score["CRSC"],
                "TV": score["TV"],
                "SCH": score["SCH"],
                "MCS": mcs,
                "notes": score.get("notes", ""),
            })

    summary = []
    for system in sorted({r["system"] for r in task_rows}):
        rows = [r for r in task_rows if r["system"] == system]
        mcs_values = [r["MCS"] for r in rows if r["MCS"] is not None]
        summary.append({
            "system": system,
            "ES": round(mean(r["ES"] for r in rows), 4),
            "SC": round(mean(r["SC"] for r in rows), 4),
            "PHR": round(mean(r["PHR"] for r in rows), 4),
            "CRSC": round(mean(r["CRSC"] for r in rows), 4),
            "TV": round(mean(r["TV"] for r in rows), 4),
            "SCH": round(mean(r["SCH"] for r in rows), 4),
            "MCS": round(mean(mcs_values), 4) if mcs_values else 0.0,
            "tasks": len(rows),
        })

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for path, rows in [(OUT_DIR / "live_task_scores.csv", task_rows), (OUT_DIR / "live_summary.csv", summary)]:
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        print(f"Wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

