#!/usr/bin/env python3
"""Audit deterministic execution artifacts for readability and nonblank content."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import geopandas as gpd
import matplotlib.image as mpimg
import numpy as np
import pandas as pd
import rasterio


ROOT = Path(__file__).resolve().parents[3]
TASKS_PATH = ROOT / "experiments/04_geo_faithfulness_evaluator/inputs/llm_tasks_30.json"
EXEC_SCORES = ROOT / "experiments/04_geo_faithfulness_evaluator/outputs/workflow_spec_execution/scores"


def audit_vector(path: Path, required: list[str]) -> dict:
    gdf = gpd.read_file(path)
    schema_ok = all(field in gdf.columns for field in required)
    return {
        "readable": 1,
        "nonblank": int(len(gdf) > 0),
        "width": "",
        "height": "",
        "feature_count": len(gdf),
        "crs": str(gdf.crs),
        "required_fields_ok": int(schema_ok),
        "pixel_std": "",
        "value_std": "",
    }


def audit_raster(path: Path) -> dict:
    with rasterio.open(path) as src:
        arr = src.read(1, masked=True)
        valid = arr.compressed()
        value_std = float(np.std(valid)) if valid.size else 0.0
        return {
            "readable": 1,
            "nonblank": int(src.width > 0 and src.height > 0 and valid.size > 0),
            "width": src.width,
            "height": src.height,
            "feature_count": "",
            "crs": str(src.crs),
            "required_fields_ok": 1,
            "pixel_std": "",
            "value_std": round(value_std, 6),
        }


def audit_png(path: Path) -> dict:
    img = mpimg.imread(path)
    pixel_std = float(np.std(img))
    height, width = img.shape[:2]
    return {
        "readable": 1,
        "nonblank": int(width > 0 and height > 0 and pixel_std > 0.001),
        "width": width,
        "height": height,
        "feature_count": "",
        "crs": "",
        "required_fields_ok": 1,
        "pixel_std": round(pixel_std, 6),
        "value_std": "",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-slug", default="qwen2.5-coder_32b")
    parser.add_argument("--mode", default="geoguard_exec_repair")
    args = parser.parse_args()

    scores_path = EXEC_SCORES / args.model_slug / "execution_task_scores.csv"
    tasks = {t["task_id"]: t for t in pd.read_json(TASKS_PATH).to_dict("records")}
    scores = pd.read_csv(scores_path)
    rows = []
    for rec in scores[scores["mode"] == args.mode].to_dict("records"):
        task = tasks[rec["task_id"]]
        path = ROOT / rec["output_path"]
        row = {
            "mode": args.mode,
            "task_id": rec["task_id"],
            "task_type": rec["task_type"],
            "output_path": rec["output_path"],
            "exists": int(path.exists()),
        }
        try:
            if task["type"] == "raster_clip":
                row.update(audit_raster(path))
            elif task["type"] == "choropleth_export":
                row.update(audit_png(path))
            else:
                row.update(audit_vector(path, task.get("required_fields", [])))
            row["notes"] = ""
        except Exception as exc:
            row.update({
                "readable": 0,
                "nonblank": 0,
                "width": "",
                "height": "",
                "feature_count": "",
                "crs": "",
                "required_fields_ok": 0,
                "pixel_std": "",
                "value_std": "",
                "notes": str(exc),
            })
        rows.append(row)

    out_dir = EXEC_SCORES / args.model_slug
    detail_path = out_dir / f"{args.mode}_artifact_audit.csv"
    with detail_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    detail = pd.DataFrame(rows)
    summary = detail.groupby("task_type").agg(
        artifacts=("exists", "mean"),
        readable=("readable", "mean"),
        nonblank=("nonblank", "mean"),
        required_fields_ok=("required_fields_ok", "mean"),
        tasks=("task_id", "count"),
    ).reset_index()
    summary_path = out_dir / f"{args.mode}_artifact_audit_summary.csv"
    summary.to_csv(summary_path, index=False)
    print(detail_path.relative_to(ROOT))
    print(summary_path.relative_to(ROOT))


if __name__ == "__main__":
    main()
