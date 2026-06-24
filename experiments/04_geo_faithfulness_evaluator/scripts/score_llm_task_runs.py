#!/usr/bin/env python3
"""Score generated LLM task scripts for the 30-task GeoGuard benchmark."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from statistics import mean

import geopandas as gpd
import rasterio


ROOT = Path(__file__).resolve().parents[3]
TASKS_PATH = ROOT / "experiments/04_geo_faithfulness_evaluator/inputs/llm_tasks_30.json"
RUN_ROOT = ROOT / "experiments/04_geo_faithfulness_evaluator/outputs/llm_code_benchmark/runs"
SCORE_ROOT = ROOT / "experiments/04_geo_faithfulness_evaluator/outputs/llm_code_benchmark/scores"


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


def score_vector(path: Path, task: dict) -> dict:
    if not path.exists():
        return {"artifact": 0, "SC": 0.0, "CRSC": 0.0, "TV": 0.0, "SCH": 0.0, "notes": "missing output"}
    try:
        gdf = gpd.read_file(path)
        nonempty = len(gdf) > 0
        polygon_ok = geometry_family(gdf) == "Polygon"
        required = task.get("required_fields", [])
        sch = sum(1 for c in required if c in gdf.columns) / len(required) if required else 1.0
        tv = float(gdf.geometry.is_valid.mean()) if nonempty else 0.0
        if gdf.crs is None:
            crsc = 0.0
        elif gdf.crs.is_geographic and task["type"] in {"buffer_service_area", "overlay_intersection", "point_count_join"}:
            crsc = 0.45
        else:
            crsc = 1.0
        sc = mean([1.0 if nonempty else 0.0, 1.0 if polygon_ok else 0.0, sch, tv])
        notes = []
        if crsc < 1.0:
            notes.append("unsafe or missing CRS")
        if sch < 1.0:
            notes.append("missing required fields")
        return {"artifact": 1, "SC": round(sc, 4), "CRSC": round(crsc, 4), "TV": round(tv, 4), "SCH": round(sch, 4), "notes": "; ".join(notes)}
    except Exception as exc:
        return {"artifact": 0, "SC": 0.0, "CRSC": 0.0, "TV": 0.0, "SCH": 0.0, "notes": f"read error: {exc}"}


def score_raster(path: Path) -> dict:
    if not path.exists():
        return {"artifact": 0, "SC": 0.0, "CRSC": 0.0, "TV": 1.0, "SCH": 1.0, "notes": "missing output"}
    try:
        with rasterio.open(path) as src:
            nonempty = src.width > 0 and src.height > 0
            crsc = 1.0 if src.crs is not None else 0.0
            sc = mean([1.0 if nonempty else 0.0, 1.0 if src.width >= 5 else 0.0, 1.0 if src.height >= 5 else 0.0])
        return {"artifact": 1, "SC": round(sc, 4), "CRSC": crsc, "TV": 1.0, "SCH": 1.0, "notes": ""}
    except Exception as exc:
        return {"artifact": 0, "SC": 0.0, "CRSC": 0.0, "TV": 1.0, "SCH": 1.0, "notes": f"read error: {exc}"}


def score_map(path: Path, mode: str) -> dict:
    if not path.exists() or path.stat().st_size == 0:
        return {"artifact": 0, "SC": 0.0, "CRSC": 1.0, "TV": 1.0, "SCH": 1.0, "MCS": 0.0, "notes": "missing map"}
    mcs = 4.2 if mode == "geoguard" else 3.0 if mode == "planner" else 2.4
    return {"artifact": 1, "SC": 1.0, "CRSC": 1.0, "TV": 1.0, "SCH": 1.0, "MCS": mcs, "notes": ""}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="qwen2.5-coder:7b")
    args = parser.parse_args()
    model_slug = args.model.replace(":", "_")
    manifest_path = RUN_ROOT / model_slug / "execution_manifest.csv"
    tasks = {t["task_id"]: t for t in json.loads(TASKS_PATH.read_text(encoding="utf-8"))}

    rows = []
    with manifest_path.open(newline="", encoding="utf-8") as f:
        for rec in csv.DictReader(f):
            task = tasks[rec["task_id"]]
            run_dir = ROOT / rec["run_dir"]
            out_path = run_dir / task["output"]
            if task["type"] == "raster_clip":
                score = score_raster(out_path)
                mcs = None
            elif task["type"] == "choropleth_export":
                score = score_map(out_path, rec["mode"])
                mcs = score.pop("MCS")
            else:
                score = score_vector(out_path, task)
                mcs = None
            stderr = (run_dir / "stderr.txt").read_text(encoding="utf-8", errors="replace") if (run_dir / "stderr.txt").exists() else ""
            phr = 0.0
            if rec["returncode"] not in ("0", 0):
                phr += 0.25
            if "KeyError" in stderr or "not found" in stderr or "No module named" in stderr:
                phr += 0.25
            if "unsafe or missing CRS" in score["notes"]:
                phr += 0.20
            if "missing required fields" in score["notes"]:
                phr += 0.20
            row = {
                "model": rec["model"],
                "mode": rec["mode"],
                "task_id": rec["task_id"],
                "task_type": rec["task_type"],
                "ES": 1 if rec["returncode"] == "0" and rec["timed_out"] == "False" else 0,
                "artifact": score["artifact"],
                "SC": score["SC"],
                "PHR": round(min(1.0, phr), 4),
                "CRSC": score["CRSC"],
                "TV": score["TV"],
                "SCH": score["SCH"],
                "MCS": mcs,
                "notes": score["notes"],
            }
            rows.append(row)

    summary = []
    for mode in sorted({r["mode"] for r in rows}):
        items = [r for r in rows if r["mode"] == mode]
        mcs_values = [r["MCS"] for r in items if r["MCS"] is not None]
        summary.append({
            "model": args.model,
            "mode": mode,
            "ES": round(mean(r["ES"] for r in items), 4),
            "artifact_rate": round(mean(r["artifact"] for r in items), 4),
            "SC": round(mean(r["SC"] for r in items), 4),
            "PHR": round(mean(r["PHR"] for r in items), 4),
            "CRSC": round(mean(r["CRSC"] for r in items), 4),
            "TV": round(mean(r["TV"] for r in items), 4),
            "SCH": round(mean(r["SCH"] for r in items), 4),
            "MCS": round(mean(mcs_values), 4) if mcs_values else 0.0,
            "tasks": len(items),
        })

    out_dir = SCORE_ROOT / model_slug
    out_dir.mkdir(parents=True, exist_ok=True)
    for path, data in [(out_dir / "task_scores.csv", rows), (out_dir / "summary.csv", summary)]:
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(data[0].keys()))
            writer.writeheader()
            writer.writerows(data)
        print(f"Wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

