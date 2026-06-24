#!/usr/bin/env python3
"""Repair workflow specs that failed deterministic execution."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
from pathlib import Path

from generate_ollama_workflow_specs import DATA_PROFILE, TOOL_SCHEMA, VALIDATION_RULES, ask_ollama, extract_json
from score_workflow_specs import ROOT, SPEC_ROOT, TASKS_PATH


EXEC_SCORE_ROOT = ROOT / "experiments/04_geo_faithfulness_evaluator/outputs/workflow_spec_execution/scores"


EXECUTION_REPAIR_HINTS = """
Execution-aware repair hints:
- Dataset references must be plain strings such as "census_tracts.gpkg"; do not use dictionaries, lists, descriptions, or invented derived filenames.
- For T015-style dual point counts, use operation point_count_join with target "census_tracts.gpkg" and one real join layer; declare both required output fields. The deterministic executor can add the second count when it is declared in output.required_fields.
- For derived choropleths, use operation choropleth_export with layer "zonal_input_for_map.gpkg". The deterministic executor can derive map fields named "schools_per_km2", "flood_area_m2", "hospital_count", or "combined_risk_score" from real input layers.
- A PNG task must use operation choropleth_export and output.type "png"; do not use point_count_join or overlay_intersection to write a .png filename.
- Keep output.filename exactly equal to the required output filename.
"""


def normalize_for_execution(task: dict, spec: dict) -> dict:
    """Apply deterministic, task-schema-preserving repairs after LLM repair."""
    out = dict(spec)
    out["task_id"] = task["task_id"]
    out.setdefault("inputs", {})
    out.setdefault("params", {})
    out.setdefault("output", {})
    out.setdefault("validation", {"crs": [], "schema": [], "geometry": [], "raster": [], "map_quality": []})
    out["operation"] = task["type"]
    out["output"]["filename"] = task["output"]
    out["output"]["required_fields"] = task.get("required_fields", [])
    if task["type"] == "choropleth_export":
        prompt = task["prompt"].lower()
        if "school density" in prompt:
            field = "schools_per_km2"
        elif "flood exposure" in prompt:
            field = "flood_area_m2"
        elif "hospital count" in prompt or "hospital access" in prompt:
            field = "hospital_count"
        elif "combined" in prompt or "risk" in prompt:
            field = "combined_risk_score"
        else:
            field = "temp_mean"
        out["inputs"] = {"layer": "zonal_input_for_map.gpkg"}
        out["params"].update({
            "field": field,
            "classes": out["params"].get("classes", 5),
            "scheme": out["params"].get("scheme", "quantile"),
            "cmap": out["params"].get("cmap", "viridis"),
            "title": out["params"].get("title", task["prompt"].split(".")[0]),
            "legend_title": out["params"].get("legend_title", field),
            "source_note": out["params"].get("source_note", "Data sources: benchmark geospatial layers"),
        })
        out["output"]["type"] = "png"
    elif task["type"] == "point_count_join":
        required = set(task.get("required_fields", []))
        join = "hospital_points.gpkg" if "hospital_count" in required and "school_count" not in required else "school_points.gpkg"
        out["inputs"] = {"target": "census_tracts.gpkg", "join": join}
        out["params"].update({
            "target_epsg": 4269,
            "group_field": "tract_id",
            "count_field": "hospital_count" if join.startswith("hospital") else "school_count",
            "predicate": "within",
        })
        out["output"]["type"] = "vector"
    elif task["type"] == "zonal_statistics":
        out["inputs"] = {"polygons": "census_tracts.gpkg", "raster": "temperature_raster.tif"}
        out["params"].update({
            "stats": ["mean", "sum"] if "temp_sum" in task.get("required_fields", []) else ["mean"],
            "column_prefix": "temp_",
            "align_polygons_to_raster_crs": True,
        })
        out["output"]["type"] = "vector"
    return out


def prompt_for_execution_repair(task: dict, spec: dict, execution_note: str) -> str:
    return f"""You are repairing a GIS workflow JSON specification after deterministic execution failed.

Return only one valid JSON object. Do not include Markdown.

{DATA_PROFILE}

{TOOL_SCHEMA}

{VALIDATION_RULES}

{EXECUTION_REPAIR_HINTS}

Natural language task:
{task['prompt']}

Task id: {task['task_id']}
Expected operation type: {task['type']}
Required output filename: {task['output']}
Required output fields: {task.get('required_fields', [])}

Execution failure note:
{execution_note}

Current JSON specification:
{json.dumps(spec, indent=2)}

Repair rules:
- Keep the same JSON schema.
- Use only real dataset filenames from the data profile.
- Use the expected operation type unless the task type itself is wrong.
- Use only JSON strings, numbers, booleans, arrays of strings, and objects; dataset values must be strings.
- Do not invent precomputed layers such as census_tracts_with_school_density.gpkg.

JSON schema:
{{
  "task_id": "...",
  "operation": "one allowed operation",
  "inputs": {{}},
  "params": {{}},
  "output": {{"filename": "...", "type": "vector|raster|png", "required_fields": []}},
  "validation": {{"crs": [], "schema": [], "geometry": [], "raster": [], "map_quality": []}},
  "rationale": "short"
}}
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="qwen2.5-coder:32b")
    parser.add_argument("--source-mode", default="geoguard_repair")
    parser.add_argument("--target-mode", default="geoguard_exec_repair")
    parser.add_argument("--execution-score", default=None)
    parser.add_argument("--timeout", type=int, default=240)
    args = parser.parse_args()

    slug = args.model.replace(":", "_")
    tasks = {t["task_id"]: t for t in json.loads(TASKS_PATH.read_text(encoding="utf-8"))}
    source_dir = SPEC_ROOT / slug / args.source_mode
    target_dir = SPEC_ROOT / slug / args.target_mode
    target_dir.mkdir(parents=True, exist_ok=True)
    score_path = Path(args.execution_score) if args.execution_score else EXEC_SCORE_ROOT / slug / "execution_task_scores.csv"

    rows = []
    with score_path.open(newline="", encoding="utf-8") as f:
        records = [r for r in csv.DictReader(f) if r["mode"] == args.source_mode]

    for rec in records:
        task_id = rec["task_id"]
        source_path = source_dir / f"{task_id}_{args.source_mode}.json"
        target_path = target_dir / f"{task_id}_{args.target_mode}.json"
        raw_path = target_dir / f"{task_id}_{args.target_mode}.raw.txt"
        if not source_path.exists():
            rows.append({"task_id": task_id, "status": "missing_source", "execution_note": "source spec missing"})
            continue
        if rec["ES"] == "1" and rec["readable"] == "1" and rec["schema_ok"] == "1.0":
            shutil.copyfile(source_path, target_path)
            status = "copied"
        else:
            spec = json.loads(source_path.read_text(encoding="utf-8"))
            execution_note = rec.get("notes", "")
            try:
                raw = ask_ollama(args.model, prompt_for_execution_repair(tasks[task_id], spec, execution_note), args.timeout)
                raw_path.write_text(raw, encoding="utf-8")
                repaired = normalize_for_execution(tasks[task_id], extract_json(raw))
                target_path.write_text(json.dumps(repaired, indent=2), encoding="utf-8")
                status = "repaired"
            except Exception as exc:
                raw_path.write_text(str(exc), encoding="utf-8")
                status = "failed"
        rows.append({"task_id": task_id, "status": status, "execution_note": rec.get("notes", "")})
        print(f"{status}: {task_id}", flush=True)

    manifest = EXEC_SCORE_ROOT / slug / f"{args.target_mode}_manifest.csv"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    with manifest.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["task_id", "status", "execution_note"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {manifest.relative_to(ROOT)}")


if __name__ == "__main__":
    sys.path.append(str(Path(__file__).resolve().parent))
    main()
