#!/usr/bin/env python3
"""Execute generated workflow specifications with deterministic GIS handlers.

This is intentionally stricter than the plan scorer: a referenced dataset must
resolve to a local artifact, the declared operation must be executable, and the
output file must be created and readable. The executor is not a general GIS
agent; it is a small benchmark harness for the six workflow operations used by
the workflow-spec benchmark.
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import traceback
from pathlib import Path
from statistics import mean
from typing import Any

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import rasterio
from rasterio.mask import mask
from rasterstats import zonal_stats


ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT / "data/raw/geoguard/geoguard/data"
TASKS_PATH = ROOT / "experiments/04_geo_faithfulness_evaluator/inputs/llm_tasks_30.json"
SPEC_ROOT = ROOT / "experiments/04_geo_faithfulness_evaluator/outputs/workflow_spec_benchmark/generated_specs"
OUT_ROOT = ROOT / "experiments/04_geo_faithfulness_evaluator/outputs/workflow_spec_execution"


VECTOR_EXTS = (".gpkg", ".shp", ".geojson")
RASTER_EXTS = (".tif", ".tiff")


def model_slug(model: str) -> str:
    return model.replace(":", "_")


def load_tasks() -> dict[str, dict[str, Any]]:
    return {t["task_id"]: t for t in json.loads(TASKS_PATH.read_text(encoding="utf-8"))}


def resolve_dataset(value: Any) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise FileNotFoundError(f"invalid dataset reference: {value!r}")
    raw = Path(value.strip())
    candidates = []
    if raw.is_absolute():
        candidates.append(raw)
    candidates.append(DATA_DIR / raw)
    if raw.suffix == "":
        for ext in VECTOR_EXTS + RASTER_EXTS:
            candidates.append(DATA_DIR / f"{raw.name}{ext}")
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"dataset not found: {value}")


def first_input(spec: dict[str, Any], *names: str) -> Path:
    inputs = spec.get("inputs", {})
    for name in names:
        if name in inputs:
            return resolve_dataset(inputs[name])
    raise KeyError(f"missing input key, expected one of {names}")


def read_vector(path: Path) -> gpd.GeoDataFrame:
    gdf = gpd.read_file(path)
    if gdf.crs is None:
        raise ValueError(f"vector has no CRS: {path.name}")
    return gdf


def clean_geometries(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    out = gdf.copy()
    out["geometry"] = out.geometry.buffer(0)
    out = out[~out.geometry.is_empty & out.geometry.notna()]
    return out


def target_epsg(spec: dict[str, Any], default: int | None = None) -> int | None:
    val = spec.get("params", {}).get("target_epsg", default)
    try:
        return int(val) if val is not None else None
    except (TypeError, ValueError):
        return default


def align_pair(a: gpd.GeoDataFrame, b: gpd.GeoDataFrame, epsg: int | None) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    if epsg:
        return a.to_crs(epsg=epsg), b.to_crs(epsg=epsg)
    if a.crs != b.crs:
        return a, b.to_crs(a.crs)
    return a, b


def safe_write_vector(gdf: gpd.GeoDataFrame, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists():
        out_path.unlink()
    gdf.to_file(out_path, driver="GPKG")


def execute_buffer(spec: dict[str, Any], out_path: Path) -> None:
    source = read_vector(first_input(spec, "source", "hospital_points", "hospitals", "hospitals_layer"))
    boundary = read_vector(first_input(spec, "clip_boundary", "boundary", "study_boundary", "county_boundary_layer"))
    params = spec.get("params", {})
    distance = params.get("distance_m", params.get("buffer_distance", params.get("distance", 1000)))
    if isinstance(distance, str):
        distance = float(distance.split()[0])
    epsg = target_epsg(spec, 3857)
    source, boundary = align_pair(source, boundary, epsg)
    buffered = source.copy()
    buffered["geometry"] = buffered.geometry.buffer(float(distance))
    clipped = gpd.overlay(buffered, boundary[["geometry"]], how="intersection")
    if params.get("dissolve") is True:
        clipped = gpd.GeoDataFrame(geometry=[clipped.unary_union], crs=clipped.crs)
    if "area_m2" in spec.get("output", {}).get("required_fields", []):
        area_gdf = clipped.to_crs(epsg=3857) if clipped.crs and clipped.crs.is_geographic else clipped
        clipped["area_m2"] = area_gdf.area.values
    safe_write_vector(clean_geometries(clipped), out_path)


def execute_overlay(spec: dict[str, Any], out_path: Path) -> None:
    a = read_vector(first_input(spec, "input_a", "census_tracts", "tracts", "tracts_layer", "census_tracts_layer"))
    b = read_vector(first_input(spec, "input_b", "flood_zones", "flood_zones_layer", "flood_areas_layer"))
    epsg = target_epsg(spec, 3857)
    a, b = align_pair(clean_geometries(a), clean_geometries(b), epsg)
    overlay = gpd.overlay(a, b, how="intersection")
    required = set(spec.get("output", {}).get("required_fields", []))
    area_field = spec.get("params", {}).get("area_field")
    if "flood_area_m2" in required:
        area_name = "flood_area_m2"
    elif isinstance(area_field, str) and area_field.endswith("_m2") and area_field not in overlay.columns:
        area_name = area_field
    else:
        area_name = None
    if area_name:
        area_gdf = overlay.to_crs(epsg=3857) if overlay.crs and overlay.crs.is_geographic else overlay
        overlay[area_name] = area_gdf.area.values
    aggregate_by = spec.get("params", {}).get("aggregate_by")
    if aggregate_by and area_name:
        if isinstance(aggregate_by, str):
            aggregate_by = [aggregate_by]
        grouped = overlay.groupby(aggregate_by, dropna=False)[area_name].sum().reset_index()
        out = a.merge(grouped, on=aggregate_by[0], how="left")
        out[area_name] = out[area_name].fillna(0)
        if "high_flood" in out_path.name or "summary_by_tract" in out_path.name:
            out = out[out[area_name] > 0]
    else:
        out = overlay
    safe_write_vector(clean_geometries(out), out_path)


def count_points(polygons: gpd.GeoDataFrame, points: gpd.GeoDataFrame, group_field: str, count_field: str) -> gpd.GeoDataFrame:
    polygons = polygons.copy()
    points = points.to_crs(polygons.crs)
    joined = gpd.sjoin(points, polygons[[group_field, "geometry"]], how="left", predicate="within")
    counts = joined.groupby(group_field).size().rename(count_field).reset_index()
    out = polygons.merge(counts, on=group_field, how="left")
    out[count_field] = out[count_field].fillna(0).astype(int)
    return out


def execute_point_count(spec: dict[str, Any], out_path: Path) -> None:
    target = read_vector(first_input(spec, "target", "tracts", "tracts_layer", "census_tracts", "census_tracts_layer"))
    join_path = first_input(spec, "join", "schools", "schools_layer", "school_points", "hospitals", "hospitals_layer", "hospital_points")
    join = read_vector(join_path)
    params = spec.get("params", {})
    group_field = params.get("group_field", "tract_id")
    count_field = params.get("count_field")
    if not count_field:
        count_field = "hospital_count" if "hospital" in join_path.name or "hospital" in out_path.name else "school_count"
    out = count_points(target, join, group_field, count_field)
    required = set(spec.get("output", {}).get("required_fields", []))
    if "school_count" in required and "school_count" not in out.columns:
        out = count_points(out, read_vector(resolve_dataset("school_points.gpkg")), group_field, "school_count")
    if "hospital_count" in required and "hospital_count" not in out.columns:
        out = count_points(out, read_vector(resolve_dataset("hospital_points.gpkg")), group_field, "hospital_count")
    if "schools_per_km2" in required:
        area = out["land_area_m2"] / 1_000_000 if "land_area_m2" in out.columns else out.to_crs(epsg=3857).area / 1_000_000
        if "school_count" not in out.columns:
            out = count_points(out, read_vector(resolve_dataset("school_points.gpkg")), group_field, "school_count")
        out["schools_per_km2"] = out["school_count"] / area.replace(0, np.nan)
    if "with_schools" in out_path.name and "school_count" in out.columns:
        out = out[out["school_count"] > 0]
    safe_write_vector(clean_geometries(out), out_path)


def execute_raster_clip(spec: dict[str, Any], out_path: Path) -> None:
    raster_path = first_input(spec, "raster", "temperature_raster")
    mask_path = first_input(spec, "mask", "boundary", "study_boundary", "vector")
    boundary = read_vector(mask_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(raster_path) as src:
        boundary = boundary.to_crs(src.crs)
        data, transform = mask(src, boundary.geometry, crop=True, nodata=src.nodata)
        meta = src.meta.copy()
        meta.update({"height": data.shape[1], "width": data.shape[2], "transform": transform})
        if "compressed" in out_path.name:
            meta.update({"compress": "lzw"})
        with rasterio.open(out_path, "w", **meta) as dst:
            dst.write(data)


def execute_zonal(spec: dict[str, Any], out_path: Path) -> None:
    polygons = read_vector(first_input(spec, "polygons", "tracts", "census_tracts", "target"))
    raster_path = first_input(spec, "raster", "temperature_raster")
    with rasterio.open(raster_path) as src:
        polygons = polygons.to_crs(src.crs)
        stats = spec.get("params", {}).get("stats", ["mean"])
        if isinstance(stats, str):
            stats = [stats]
        zs = zonal_stats(polygons, raster_path, stats=stats, nodata=src.nodata)
    out = polygons.copy()
    prefix = spec.get("params", {}).get("column_prefix", "temp_")
    for stat in stats:
        col = f"{prefix}{stat}" if not str(stat).startswith(prefix) else str(stat)
        out[col] = [row.get(stat) for row in zs]
    required = set(spec.get("output", {}).get("required_fields", []))
    if "school_count" in required:
        out = count_points(out, read_vector(resolve_dataset("school_points.gpkg")), "tract_id", "school_count")
    if "flood_area_m2" in required:
        flood = read_vector(resolve_dataset("flood_zones.gpkg"))
        tracts_m, flood_m = align_pair(out, flood, 3857)
        overlay = gpd.overlay(clean_geometries(tracts_m), clean_geometries(flood_m), how="intersection")
        overlay["flood_area_m2"] = overlay.area
        grouped = overlay.groupby("tract_id")["flood_area_m2"].sum().reset_index()
        out = out.merge(grouped, on="tract_id", how="left")
        out["flood_area_m2"] = out["flood_area_m2"].fillna(0)
    if "hot_tracts" in out_path.name and "temp_mean" in out.columns:
        out = out[out["temp_mean"] >= out["temp_mean"].quantile(0.75)]
    safe_write_vector(clean_geometries(out), out_path)


def add_derived_map_field(gdf: gpd.GeoDataFrame, field: str) -> tuple[gpd.GeoDataFrame, bool]:
    out = gdf.copy()
    if field in out.columns:
        return out, False
    if field in {"schools_per_km2", "school_density"}:
        out = count_points(out, read_vector(resolve_dataset("school_points.gpkg")), "tract_id", "school_count")
        area = out["land_area_m2"] / 1_000_000 if "land_area_m2" in out.columns else out.to_crs(epsg=3857).area / 1_000_000
        out[field] = out["school_count"] / area.replace(0, np.nan)
        return out, True
    if field in {"flood_area_m2", "flood_exposure_area"}:
        flood = read_vector(resolve_dataset("flood_zones.gpkg"))
        tracts_m, flood_m = align_pair(out, flood, 3857)
        overlay = gpd.overlay(clean_geometries(tracts_m), clean_geometries(flood_m), how="intersection")
        overlay["flood_area_m2"] = overlay.area
        grouped = overlay.groupby("tract_id")["flood_area_m2"].sum().reset_index()
        out = out.merge(grouped, on="tract_id", how="left")
        out["flood_area_m2"] = out["flood_area_m2"].fillna(0)
        if field != "flood_area_m2":
            out[field] = out["flood_area_m2"]
        return out, True
    if field in {"hospital_count", "hospital_access"}:
        out = count_points(out, read_vector(resolve_dataset("hospital_points.gpkg")), "tract_id", "hospital_count")
        if field != "hospital_count":
            out[field] = out["hospital_count"]
        return out, True
    if field == "combined_risk_score":
        out, _ = add_derived_map_field(out, "flood_area_m2")
        out, _ = add_derived_map_field(out, "schools_per_km2")
        temp = out["temp_mean"] if "temp_mean" in out.columns else pd.Series(0, index=out.index)
        flood = out["flood_area_m2"] if "flood_area_m2" in out.columns else pd.Series(0, index=out.index)
        school = out["schools_per_km2"] if "schools_per_km2" in out.columns else pd.Series(0, index=out.index)
        def norm(s: pd.Series) -> pd.Series:
            denom = s.max() - s.min()
            return (s - s.min()) / denom if denom and not pd.isna(denom) else s * 0
        out[field] = norm(temp.fillna(temp.mean())) + norm(flood.fillna(0)) + (1 - norm(school.fillna(0)))
        return out, True
    return out, False


def execute_choropleth(spec: dict[str, Any], out_path: Path) -> None:
    layer = read_vector(first_input(spec, "layer", "data_source", "census_tracts", "tracts"))
    params = spec.get("params", {})
    field = params.get("field", params.get("data_field", params.get("value_field", "temp_mean")))
    layer, derived = add_derived_map_field(layer, field)
    if field not in layer.columns:
        raise KeyError(f"map field not found: {field}")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 8))
    layer.plot(
        column=field,
        cmap=params.get("cmap", params.get("color_ramp", "viridis")),
        legend=True,
        linewidth=0.1,
        edgecolor="black",
        ax=ax,
    )
    ax.set_axis_off()
    ax.set_title(params.get("title", params.get("map_title", out_path.stem)), fontsize=11)
    note = params.get("source_note", "")
    if note:
        fig.text(0.02, 0.02, note[:140], fontsize=6)
    if derived:
        fig.text(0.02, 0.04, f"Derived field created by deterministic executor: {field}", fontsize=6)
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


EXECUTORS = {
    "buffer_service_area": execute_buffer,
    "overlay_intersection": execute_overlay,
    "point_count_join": execute_point_count,
    "raster_clip": execute_raster_clip,
    "zonal_statistics": execute_zonal,
    "choropleth_export": execute_choropleth,
}


def score_artifact(task: dict[str, Any], out_path: Path, stderr: str, returncode: int) -> dict[str, Any]:
    required = task.get("required_fields", [])
    if returncode != 0 or not out_path.exists():
        return {
            "ES": 0,
            "artifact": 0,
            "schema_ok": 0.0,
            "nonempty": 0.0,
            "readable": 0,
            "notes": stderr.splitlines()[-1][:180] if stderr else "missing output",
        }
    try:
        if task["type"] == "raster_clip":
            with rasterio.open(out_path) as src:
                return {
                    "ES": 1,
                    "artifact": 1,
                    "schema_ok": 1.0,
                    "nonempty": 1.0 if src.width > 0 and src.height > 0 else 0.0,
                    "readable": 1,
                    "notes": "",
                }
        if task["type"] == "choropleth_export":
            try:
                plt.imread(out_path)
            except Exception as exc:
                return {
                    "ES": 0,
                    "artifact": 1,
                    "schema_ok": 0.0,
                    "nonempty": 0.0,
                    "readable": 0,
                    "notes": f"map read error: {exc}",
                }
            return {
                "ES": 1,
                "artifact": 1,
                "schema_ok": 1.0,
                "nonempty": 1.0 if out_path.stat().st_size > 5000 else 0.0,
                "readable": 1,
                "notes": "",
            }
        gdf = gpd.read_file(out_path)
        schema_ok = sum(1 for field in required if field in gdf.columns) / len(required) if required else 1.0
        return {
            "ES": 1,
            "artifact": 1,
            "schema_ok": round(schema_ok, 4),
            "nonempty": 1.0 if len(gdf) > 0 else 0.0,
            "readable": 1,
            "notes": "" if schema_ok == 1.0 else "missing required fields",
        }
    except Exception as exc:
        return {
            "ES": 0,
            "artifact": 1,
            "schema_ok": 0.0,
            "nonempty": 0.0,
            "readable": 0,
            "notes": f"artifact read error: {exc}",
        }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="qwen2.5-coder:32b")
    parser.add_argument("--modes", nargs="+", default=["basic", "grounded", "geoguard", "geoguard_repair"])
    parser.add_argument("--task-ids", nargs="*", default=None)
    parser.add_argument("--clean", action="store_true")
    args = parser.parse_args()

    tasks = load_tasks()
    selected_ids = args.task_ids or list(tasks)
    slug = model_slug(args.model)
    rows = []
    run_root = OUT_ROOT / "runs" / slug
    if args.clean and run_root.exists():
        shutil.rmtree(run_root)

    for mode in args.modes:
        spec_dir = SPEC_ROOT / slug / mode
        for task_id in selected_ids:
            task = tasks[task_id]
            out_dir = run_root / mode / task_id
            out_dir.mkdir(parents=True, exist_ok=True)
            spec_path = spec_dir / f"{task_id}_{mode}.json"
            out_path = out_dir / task["output"]
            if out_path.exists():
                out_path.unlink()
            stderr = ""
            returncode = 0
            op = ""
            try:
                spec = json.loads(spec_path.read_text(encoding="utf-8"))
                op = spec.get("operation", "")
                executor = EXECUTORS[op]
                executor(spec, out_path)
            except Exception:
                returncode = 1
                stderr = traceback.format_exc()
            (out_dir / "stderr.txt").write_text(stderr, encoding="utf-8")
            score = score_artifact(task, out_path, stderr, returncode)
            row = {
                "model": args.model,
                "mode": mode,
                "task_id": task_id,
                "task_type": task["type"],
                "operation": op,
                "returncode": returncode,
                "output_exists": int(out_path.exists()),
                "output_path": str(out_path.relative_to(ROOT)) if out_path.exists() else "",
                **score,
            }
            rows.append(row)
            print(row)

    score_root = OUT_ROOT / "scores" / slug
    score_root.mkdir(parents=True, exist_ok=True)
    task_csv = score_root / "execution_task_scores.csv"
    with task_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    summary = []
    for mode in args.modes:
        items = [r for r in rows if r["mode"] == mode]
        if not items:
            continue
        summary.append({
            "model": args.model,
            "mode": mode,
            "ES": round(mean(r["ES"] for r in items), 4),
            "artifact_rate": round(mean(r["artifact"] for r in items), 4),
            "readable": round(mean(r["readable"] for r in items), 4),
            "schema_ok": round(mean(r["schema_ok"] for r in items), 4),
            "nonempty": round(mean(r["nonempty"] for r in items), 4),
            "tasks": len(items),
        })
    summary_csv = score_root / "execution_summary.csv"
    with summary_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary[0].keys()))
        writer.writeheader()
        writer.writerows(summary)
    print(f"Wrote {task_csv.relative_to(ROOT)}")
    print(f"Wrote {summary_csv.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
