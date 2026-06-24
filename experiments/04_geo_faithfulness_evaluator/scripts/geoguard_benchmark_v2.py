#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import rasterio
from rasterio.mask import mask
from rasterstats import zonal_stats


@dataclass
class SystemVariant:
    group: str
    name: str
    precheck_crs: bool
    repair_geometry: bool
    schema_guard: bool
    map_critic: bool
    reflector: bool


SYSTEMS = [
    SystemVariant("baseline", "basic_gis_copilot", False, False, False, False, False),
    SystemVariant("baseline", "planner_reflector", True, False, False, False, True),
    SystemVariant("baseline", "geoguard_copilot", True, True, True, True, True),
    SystemVariant("ablation", "without_data_profiler", False, True, False, True, True),
    SystemVariant("ablation", "without_geoguard_validator", True, False, False, True, True),
    SystemVariant("ablation", "without_map_quality_critic", True, True, True, False, True),
    SystemVariant("ablation", "without_reflector", True, True, True, True, False),
]


@dataclass
class RunRecord:
    run_id: int
    task_id: str
    task_name: str
    task_type: str
    category: str
    difficulty: str
    system_group: str
    system: str
    ES: int
    SC: float
    PHR: float
    CRSC: float
    TV: float
    SCH: float
    MCS: Optional[float]
    output_path: str
    notes: str


def normalize_path(p: str) -> str:
    return os.path.expandvars(os.path.expanduser(p))


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def read_dataset(spec: Dict):
    path = normalize_path(spec["path"])
    if spec["type"] == "vector":
        return gpd.read_file(path, layer=spec.get("layer"))
    if spec["type"] == "raster":
        return rasterio.open(path)
    raise ValueError(f"Unsupported dataset type: {spec['type']}")


def write_gdf(gdf: gpd.GeoDataFrame, path: Path, layer_name: Optional[str] = None):
    ensure_dir(path.parent)
    if path.suffix.lower() == ".gpkg":
        gdf.to_file(path, layer=layer_name or path.stem, driver="GPKG")
    else:
        gdf.to_file(path)


def geometry_family(gdf: gpd.GeoDataFrame) -> str:
    if len(gdf) == 0:
        return "Unknown"
    geom = str(gdf.geom_type.iloc[0])
    if "Point" in geom:
        return "Point"
    if "Line" in geom:
        return "LineString"
    if "Polygon" in geom:
        return "Polygon"
    return geom


def topology_validity(gdf: gpd.GeoDataFrame) -> float:
    if len(gdf) == 0:
        return 0.0
    return float(gdf.geometry.is_valid.mean())


def schema_consistency(columns: List[str], required: List[str]) -> float:
    if not required:
        return 1.0
    actual = set(columns)
    expected = set(required)
    return len(actual & expected) / len(expected)


def mean_ignore_none(values):
    vals = [v for v in values if v is not None]
    return sum(vals) / len(vals) if vals else None


def parameter_hallucination_score(issues: int, checks: int) -> float:
    if checks <= 0:
        return 0.0
    return round(issues / checks, 4)


def crs_safety_score(issues: int, checks: int, has_crs: bool) -> float:
    if checks > 0:
        return round(max(0.0, 1.0 - issues / checks), 4)
    return 1.0 if has_crs else 0.0


def apply_schema_guard(gdf: gpd.GeoDataFrame, required_fields: List[str], enabled: bool, notes: List[str]) -> gpd.GeoDataFrame:
    if not enabled or not required_fields:
        return gdf
    out = gdf.copy()
    repaired = []
    for field in required_fields:
        if field in out.columns:
            continue
        for candidate in (f"{field}_1", f"{field}_left", f"{field}_x"):
            if candidate in out.columns:
                out[field] = out[candidate]
                repaired.append(f"{candidate}->{field}")
                break
    if repaired:
        notes.append("Schema guard restored fields: " + ", ".join(repaired) + ".")
    return out


def repair_if_needed(gdf: gpd.GeoDataFrame, enabled: bool) -> gpd.GeoDataFrame:
    if enabled and len(gdf) > 0:
        out = gdf.copy()
        out["geometry"] = out.buffer(0)
        return out
    return gdf


def ensure_projected(gdf: gpd.GeoDataFrame, target_epsg: Optional[int], system, notes, issues_checks):
    issues, checks = issues_checks
    used_safe_projection = False
    if gdf.crs is not None and gdf.crs.is_geographic:
        checks += 1
        if system.precheck_crs and target_epsg:
            gdf = gdf.to_crs(epsg=int(target_epsg))
            used_safe_projection = True
            notes.append(f"Reprojected to EPSG:{target_epsg}.")
        else:
            issues += 1
            notes.append("Geographic CRS used without safe metric reprojection.")
    return gdf, used_safe_projection, issues, checks


def align_crs(gdf_a, gdf_b, target_epsg, system, notes, issues_checks):
    issues, checks = issues_checks
    used_safe_projection = False
    if gdf_a.crs != gdf_b.crs:
        checks += 1
        if system.precheck_crs and target_epsg:
            gdf_a = gdf_a.to_crs(epsg=int(target_epsg))
            gdf_b = gdf_b.to_crs(epsg=int(target_epsg))
            used_safe_projection = True
            notes.append(f"Aligned both layers to EPSG:{target_epsg}.")
        else:
            issues += 1
            notes.append("CRS mismatch without safe alignment.")
    return gdf_a, gdf_b, used_safe_projection, issues, checks


def evaluate_vector_expectations(gdf, expectations):
    checks, notes = [], []
    if expectations.get("require_non_empty", False):
        ok = 1.0 if len(gdf) > 0 else 0.0
        checks.append(ok)
        if not ok:
            notes.append("Output is empty.")
    expected_geom = expectations.get("expected_geometry")
    if expected_geom:
        ok = 1.0 if geometry_family(gdf) == expected_geom else 0.0
        checks.append(ok)
        if not ok:
            notes.append(f"Expected geometry {expected_geom}, got {geometry_family(gdf)}.")
    min_features = expectations.get("min_features")
    if min_features is not None:
        ok = 1.0 if len(gdf) >= int(min_features) else 0.0
        checks.append(ok)
        if not ok:
            notes.append("Feature count below minimum.")
    req_fields = expectations.get("required_output_fields", [])
    if req_fields:
        sch = schema_consistency(list(gdf.columns), req_fields)
        checks.append(sch)
        if sch < 1.0:
            notes.append("Missing required output fields.")
    return (sum(checks) / len(checks) if checks else 1.0), notes


def evaluate_raster_expectations(meta, expectations):
    checks, notes = [], []
    width, height = meta["width"], meta["height"]
    if expectations.get("require_non_empty", False):
        ok = 1.0 if width > 0 and height > 0 else 0.0
        checks.append(ok)
        if not ok:
            notes.append("Raster output is empty.")
    if expectations.get("min_width") is not None:
        checks.append(1.0 if width >= int(expectations["min_width"]) else 0.0)
    if expectations.get("min_height") is not None:
        checks.append(1.0 if height >= int(expectations["min_height"]) else 0.0)
    return (sum(checks) / len(checks) if checks else 1.0), notes


def score_map_communication(gdf, field_name, map_critic):
    score = 1.0
    if field_name in gdf.columns:
        score += 1.0
    if len(gdf) > 0:
        score += 1.0
    if map_critic:
        score += 1.5
    if field_name in gdf.columns and gdf[field_name].notna().mean() > 0.8:
        score += 1.5
    return min(round(score, 4), 5.0)


def make_metric_result(out, expectations, used_safe, issues, checks, artifact, notes, is_map=False, map_field=None):
    sc_rule, sc_notes = evaluate_vector_expectations(out, expectations)
    notes.extend(sc_notes)
    tv = topology_validity(out)
    sch = schema_consistency(list(out.columns), expectations.get("required_output_fields", []))
    crsc = crs_safety_score(issues, checks, out.crs is not None)
    phr = parameter_hallucination_score(issues, max(checks, 1))
    if is_map:
        sc = round(min(1.0, 0.6 * sc_rule + 0.2 * tv + 0.2 * sch), 4)
        mcs = score_map_communication(out, map_field, True)
    else:
        sc = round(0.5 * sc_rule + 0.25 * tv + 0.25 * sch, 4)
        mcs = None
    return {
        "ES": 1,
        "SC": sc,
        "PHR": phr,
        "CRSC": crsc,
        "TV": round(tv, 4),
        "SCH": round(sch, 4),
        "MCS": mcs,
        "notes": " ".join(notes),
        "artifact": str(artifact),
    }


def task_buffer_service_area(config, task, system, out_dir):
    notes = []
    issues, checks = 0, 0
    src = read_dataset(config["datasets"][task["inputs"]["source"]])
    bnd = read_dataset(config["datasets"][task["inputs"]["clip_boundary"]]) if task["inputs"].get("clip_boundary") else None
    params, expectations = task.get("params", {}), task.get("expectations", {})
    distance, target_epsg = float(params["distance"]), params.get("target_epsg")
    src, used_safe, issues, checks = ensure_projected(src, target_epsg, system, notes, (issues, checks))
    if bnd is not None and src.crs != bnd.crs:
        src, bnd, _, issues, checks = align_crs(src, bnd, target_epsg, system, notes, (issues, checks))
    if task.get("required_input_fields"):
        checks += 1
        missing = [f for f in task["required_input_fields"] if f not in src.columns]
        if missing:
            issues += 1
            notes.append("Missing input fields: " + ", ".join(missing))
    out = src.copy()
    out["geometry"] = out.geometry.buffer(distance)
    if params.get("dissolve", False):
        out = out.dissolve().reset_index(drop=True)
    if bnd is not None:
        out = gpd.overlay(out, bnd, how="intersection")
    out = apply_schema_guard(out, expectations.get("required_output_fields", []), system.schema_guard, notes)
    out = repair_if_needed(out, system.repair_geometry)
    path = out_dir / "buffer_output.gpkg"
    write_gdf(out, path, "buffer_output")
    return make_metric_result(out, expectations, used_safe, issues, checks, path, notes)


def task_overlay_intersection(config, task, system, out_dir):
    notes = []
    issues, checks = 0, 0
    a = read_dataset(config["datasets"][task["inputs"]["input_a"]])
    b = read_dataset(config["datasets"][task["inputs"]["input_b"]])
    params, expectations = task.get("params", {}), task.get("expectations", {})
    target_epsg = params.get("target_epsg")
    a, b, used_safe, issues, checks = align_crs(a, b, target_epsg, system, notes, (issues, checks))
    out = gpd.overlay(a, b, how="intersection")
    prefix = params.get("overlay_prefix", "fz_")
    rename_map = {}
    for c in b.columns:
        if c != "geometry" and c in out.columns and c not in expectations.get("required_output_fields", []):
            rename_map[c] = prefix + c
    out = out.rename(columns=rename_map)
    out = apply_schema_guard(out, expectations.get("required_output_fields", []), system.schema_guard, notes)
    out = repair_if_needed(out, system.repair_geometry)
    path = out_dir / "overlay_output.gpkg"
    write_gdf(out, path, "overlay_output")
    return make_metric_result(out, expectations, used_safe, issues, checks, path, notes)


def task_point_count_join(config, task, system, out_dir):
    notes = []
    issues, checks = 0, 0
    polys = read_dataset(config["datasets"][task["inputs"]["target"]])
    points = read_dataset(config["datasets"][task["inputs"]["join"]])
    params, expectations = task.get("params", {}), task.get("expectations", {})
    target_epsg = params.get("target_epsg")
    polys, points, used_safe, issues, checks = align_crs(polys, points, target_epsg, system, notes, (issues, checks))
    predicate = params.get("predicate", "intersects")
    joined = gpd.sjoin(points[[c for c in points.columns if c != "geometry"] + ["geometry"]], polys[[params.get("group_field", "tract_id"), "geometry"]], how="inner", predicate=predicate)
    count_col = params.get("count_field", "school_count")
    group_field = params.get("group_field", "tract_id")
    counts = joined.groupby(group_field).size().rename(count_col).reset_index()
    out = polys.merge(counts, on=group_field, how="left")
    out[count_col] = out[count_col].fillna(0).astype(int)
    out = apply_schema_guard(out, expectations.get("required_output_fields", []), system.schema_guard, notes)
    out = repair_if_needed(out, system.repair_geometry)
    path = out_dir / "point_count_join_output.gpkg"
    write_gdf(out, path, "point_count_join_output")
    return make_metric_result(out, expectations, used_safe, issues, checks, path, notes)


def task_raster_clip(config, task, system, out_dir):
    notes = []
    issues, checks = 0, 0
    raster = read_dataset(config["datasets"][task["inputs"]["raster"]])
    mask_gdf = read_dataset(config["datasets"][task["inputs"]["mask"]])
    params, expectations = task.get("params", {}), task.get("expectations", {})
    used_safe = False
    if mask_gdf.crs != raster.crs:
        checks += 1
        if system.precheck_crs:
            mask_gdf = mask_gdf.to_crs(raster.crs)
            used_safe = True
            notes.append("Reprojected mask to raster CRS before clipping.")
        else:
            issues += 1
            notes.append("Raster/mask CRS mismatch without safe alignment.")
    geoms = [geom.__geo_interface__ for geom in mask_gdf.geometry]
    out_image, out_transform = mask(raster, geoms, crop=True, nodata=params.get("nodata", raster.nodata))
    meta = raster.meta.copy()
    meta.update({
        "driver": "GTiff",
        "height": out_image.shape[1],
        "width": out_image.shape[2],
        "transform": out_transform,
        "nodata": params.get("nodata", raster.nodata),
    })
    path = out_dir / "raster_clip_output.tif"
    ensure_dir(path.parent)
    with rasterio.open(path, "w", **meta) as dest:
        dest.write(out_image)
    sc_rule, sc_notes = evaluate_raster_expectations(meta, expectations)
    notes.extend(sc_notes)
    phr = parameter_hallucination_score(issues, max(checks, 1))
    return {
        "ES": 1,
        "SC": round(sc_rule, 4),
        "PHR": phr,
        "CRSC": crs_safety_score(issues, checks, mask_gdf.crs == raster.crs),
        "TV": 1.0,
        "SCH": 1.0,
        "MCS": None,
        "notes": " ".join(notes),
        "artifact": str(path),
    }


def task_zonal_statistics(config, task, system, out_dir):
    notes = []
    issues, checks = 0, 0
    polys = read_dataset(config["datasets"][task["inputs"]["polygons"]])
    raster = read_dataset(config["datasets"][task["inputs"]["raster"]])
    params, expectations = task.get("params", {}), task.get("expectations", {})
    used_safe = False
    if polys.crs != raster.crs:
        checks += 1
        if system.precheck_crs:
            polys = polys.to_crs(raster.crs)
            used_safe = True
            notes.append("Reprojected polygons to raster CRS for zonal statistics.")
        else:
            issues += 1
            notes.append("Zonal statistics CRS mismatch without safe alignment.")
    stats = zonal_stats(polys, raster.name, stats=params.get("stats", ["mean", "sum"]), nodata=raster.nodata)
    out = polys.copy()
    prefix = params.get("column_prefix", "temp_")
    for s in params.get("stats", ["mean", "sum"]):
        out[f"{prefix}{s}"] = [row.get(s) for row in stats]
    out = apply_schema_guard(out, expectations.get("required_output_fields", []), system.schema_guard, notes)
    out = repair_if_needed(out, system.repair_geometry)
    path = out_dir / "zonal_stats_output.gpkg"
    write_gdf(out, path, "zonal_stats_output")
    return make_metric_result(out, expectations, used_safe, issues, checks, path, notes)


def task_choropleth_export(config, task, system, out_dir):
    gdf = read_dataset(config["datasets"][task["inputs"]["layer"]])
    params, expectations = task.get("params", {}), task.get("expectations", {})
    field = params["field"]
    if field not in gdf.columns:
        raise RuntimeError(f"Field not found for choropleth: {field}")
    fig, ax = plt.subplots(figsize=(10, 7))
    plot_kwargs = {
        "column": field,
        "cmap": params.get("cmap", "Blues"),
        "legend": bool(system.map_critic),
        "ax": ax,
        "linewidth": 0.1,
        "edgecolor": "white",
    }
    scheme = params.get("scheme")
    classes = params.get("classes")
    if scheme and classes:
        plot_kwargs["scheme"] = scheme
        plot_kwargs["k"] = int(classes)
    gdf.plot(**plot_kwargs)
    ax.set_axis_off()
    if system.map_critic:
        ax.set_title(params.get("title", "GeoGuard-Copilot Choropleth"))
    plt.tight_layout()
    path = out_dir / "choropleth.png"
    plt.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    tv = topology_validity(gdf)
    sch = schema_consistency(list(gdf.columns), expectations.get("required_output_fields", []))
    sc_rule, notes = evaluate_vector_expectations(gdf, expectations)
    sc = round(min(1.0, 0.6 * sc_rule + 0.2 * tv + 0.2 * sch), 4)
    mcs = score_map_communication(gdf, field, system.map_critic)
    return {
        "ES": 1,
        "SC": sc,
        "PHR": 0.0,
        "CRSC": 1.0,
        "TV": round(tv, 4),
        "SCH": round(sch, 4),
        "MCS": round(mcs, 4),
        "notes": "Map critic enabled with legend/title." if system.map_critic else "Plain map export without map critic.",
        "artifact": str(path),
    }


TASK_RUNNERS = {
    "buffer_service_area": task_buffer_service_area,
    "overlay_intersection": task_overlay_intersection,
    "point_count_join": task_point_count_join,
    "raster_clip": task_raster_clip,
    "zonal_statistics": task_zonal_statistics,
    "choropleth_export": task_choropleth_export,
}


def execute_task(config, task, system, task_dir):
    runner = TASK_RUNNERS[task["type"]]
    try:
        return runner(config, task, system, task_dir)
    except Exception as exc:
        if system.reflector:
            retry_dir = task_dir / "reflect_retry"
            ensure_dir(retry_dir)
            safe = SystemVariant(system.group, system.name, True, True, True, system.map_critic, False)
            result = runner(config, task, safe, retry_dir)
            result["notes"] = f"Reflector retry after error: {exc}. " + result.get("notes", "")
            return result
        raise


def aggregate(records):
    rows = []
    buckets = {}
    for r in records:
        buckets.setdefault((r.system_group, r.system), []).append(r)
    for (group, system), items in buckets.items():
        rows.append({
            "system_group": group,
            "system": system,
            "ES": round(sum(i.ES for i in items) / len(items), 4),
            "SC": round(sum(i.SC for i in items) / len(items), 4),
            "PHR": round(sum(i.PHR for i in items) / len(items), 4),
            "CRSC": round(sum(i.CRSC for i in items) / len(items), 4),
            "TV": round(sum(i.TV for i in items) / len(items), 4),
            "SCH": round(sum(i.SCH for i in items) / len(items), 4),
            "MCS": round(mean_ignore_none([i.MCS for i in items]) or 0.0, 4),
            "runs": len(items),
        })
    return rows


def aggregate_task_level(records):
    rows = []
    groups = {}
    for r in records:
        groups.setdefault((r.task_id, r.system), []).append(r)
    for (task_id, system), items in groups.items():
        one = items[0]
        rows.append({
            "task_id": task_id,
            "task_name": one.task_name,
            "task_type": one.task_type,
            "system_group": one.system_group,
            "system": system,
            "ES": round(sum(i.ES for i in items) / len(items), 4),
            "SC": round(sum(i.SC for i in items) / len(items), 4),
            "PHR": round(sum(i.PHR for i in items) / len(items), 4),
            "CRSC": round(sum(i.CRSC for i in items) / len(items), 4),
            "TV": round(sum(i.TV for i in items) / len(items), 4),
            "SCH": round(sum(i.SCH for i in items) / len(items), 4),
            "MCS": round(mean_ignore_none([i.MCS for i in items]) or 0.0, 4),
        })
    return rows


def write_csv(path: Path, rows: List[Dict]):
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def maybe_plot(summary_csv, out_dir):
    df = pd.read_csv(summary_csv)
    if df.empty:
        return
    pos = ["ES", "SC", "CRSC", "TV", "SCH", "MCS"]
    ax = df.set_index("system")[pos].plot(kind="bar", figsize=(12, 6))
    ax.set_title("GeoGuard real-data benchmark summary")
    plt.tight_layout()
    plt.savefig(Path(out_dir) / "summary_positive_metrics.png", dpi=180)
    plt.close()
    ax = df.set_index("system")[["PHR"]].plot(kind="bar", figsize=(8, 5), color=["#c0392b"])
    ax.set_title("Parameter Hallucination Rate (lower is better)")
    plt.tight_layout()
    plt.savefig(Path(out_dir) / "summary_phr.png", dpi=180)
    plt.close()


def compare_with_reference(summary_all: pd.DataFrame, reference_csv: Optional[Path], output_dir: Path):
    if not reference_csv or not reference_csv.exists():
        return
    ref = pd.read_csv(reference_csv)
    merged = ref.merge(summary_all, on="system", how="left", suffixes=("_paper", "_run"))
    for metric in ["ES", "SC", "PHR", "CRSC", "TV", "SCH", "MCS"]:
        if f"{metric}_run" in merged.columns and f"{metric}_paper" in merged.columns:
            merged[f"delta_{metric}"] = merged[f"{metric}_run"] - merged[f"{metric}_paper"]
    merged.to_csv(output_dir / "paper_vs_run_summary.csv", index=False)



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--systems", nargs="*", default=None)
    parser.add_argument("--runs", type=int, default=None)
    parser.add_argument("--reference-csv", default=None)
    args = parser.parse_args()

    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    output_dir = Path(normalize_path(args.output))
    ensure_dir(output_dir)
    task_outputs = output_dir / "task_outputs"
    ensure_dir(task_outputs)

    systems = SYSTEMS
    if args.systems:
        keep = set(args.systems)
        systems = [s for s in systems if s.name in keep]
    runs = int(args.runs or config.get("runs", 3))

    records = []
    for run_id in range(1, runs + 1):
        for system in systems:
            for task in config["tasks"]:
                task_dir = task_outputs / f"run_{run_id}" / system.name / task["task_id"]
                ensure_dir(task_dir)
                try:
                    metrics = execute_task(config, task, system, task_dir)
                    rec = RunRecord(
                        run_id,
                        task["task_id"],
                        task.get("name", task["task_id"]),
                        task["type"],
                        task.get("category", ""),
                        task.get("difficulty", ""),
                        system.group,
                        system.name,
                        int(metrics["ES"]),
                        float(metrics["SC"]),
                        float(metrics["PHR"]),
                        float(metrics["CRSC"]),
                        float(metrics["TV"]),
                        float(metrics["SCH"]),
                        metrics.get("MCS"),
                        metrics.get("artifact", ""),
                        metrics.get("notes", ""),
                    )
                except Exception as exc:
                    rec = RunRecord(
                        run_id,
                        task["task_id"],
                        task.get("name", task["task_id"]),
                        task["type"],
                        task.get("category", ""),
                        task.get("difficulty", ""),
                        system.group,
                        system.name,
                        0,
                        0.0,
                        1.0,
                        0.0,
                        0.0,
                        0.0,
                        None,
                        str(task_dir),
                        "ERROR: " + str(exc),
                    )
                records.append(rec)

    run_logs = [asdict(r) for r in records]
    summary_all = aggregate(records)
    summary_task = aggregate_task_level(records)
    summary_baselines = [r for r in summary_all if r["system_group"] == "baseline"]
    summary_ablation = [r for r in summary_all if r["system_group"] == "ablation"]

    write_csv(output_dir / "run_logs.csv", run_logs)
    write_csv(output_dir / "summary_all_systems.csv", summary_all)
    write_csv(output_dir / "summary_baselines.csv", summary_baselines)
    write_csv(output_dir / "summary_ablation.csv", summary_ablation)
    write_csv(output_dir / "summary_task_level.csv", summary_task)

    pd.DataFrame(summary_all).to_excel(output_dir / "summary_all_systems.xlsx", index=False)
    maybe_plot(output_dir / "summary_all_systems.csv", output_dir)
    reference_csv = Path(normalize_path(args.reference_csv)) if args.reference_csv else None
    compare_with_reference(pd.DataFrame(summary_all), reference_csv, output_dir)
    (output_dir / "benchmark_metadata.json").write_text(
        json.dumps(
            {
                "runs": runs,
                "systems": [asdict(s) for s in systems],
                "task_count": len(config["tasks"]),
                "note": "Bundle aligned to the GeoGuard paper structure. The paper's Table 4 values are draft placeholder results, so use paper_vs_run_summary.csv only as a reference comparison.",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print("[OK] Finished benchmark.")
    print(output_dir / "summary_all_systems.csv")


if __name__ == "__main__":
    main()
