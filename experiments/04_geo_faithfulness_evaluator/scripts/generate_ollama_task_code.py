#!/usr/bin/env python3
"""Generate Python candidate scripts for GeoGuard task prompts with Ollama."""

from __future__ import annotations

import argparse
import json
import re
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TASKS_PATH = ROOT / "experiments/04_geo_faithfulness_evaluator/inputs/llm_tasks_30.json"
OUT_ROOT = ROOT / "experiments/04_geo_faithfulness_evaluator/outputs/llm_code_benchmark/generated_code"


SYSTEM_PROMPTS = {
    "basic": "You are a GIS coding assistant. Write concise Python code to complete the user's geospatial task.",
    "planner": "You are a careful GIS planner and coding assistant. Plan CRS handling before metric operations, then write robust Python code.",
    "geoguard": "You are GeoGuard-Copilot. Write Python code with CRS checks, schema validation, geometry repair, nodata handling, and map-quality safeguards where relevant.",
}


COMMON_INSTRUCTIONS = """
Return only executable Python code, with no Markdown fences.

The code will run with these environment variables:
- GEOGUARD_DATA_DIR: folder containing hospital_points.gpkg, study_boundary.gpkg, census_tracts.gpkg, flood_zones.gpkg, school_points.gpkg, temperature_raster.tif, zonal_input_for_map.gpkg
- GEOGUARD_OUTPUT_DIR: folder where the required output file must be written

Use available Python libraries: geopandas, pandas, shapely, rasterio, rasterstats, matplotlib, mapclassify.
Use pathlib.Path and os.environ to read paths.
Always write the exact requested output filename into GEOGUARD_OUTPUT_DIR.
Do not download data.
Do not require user interaction.
"""


DATA_PROFILE = """
Verified data profile:
- hospital_points.gpkg: Point, CRS EPSG:4326, fields include source_id, name, org_name, addrln1, city, state, zip, url
- study_boundary.gpkg: MultiPolygon, CRS EPSG:4269, fields include boundary_id, name, label
- census_tracts.gpkg: MultiPolygon, CRS EPSG:4269, fields include tract_id, tract_name, land_area_m2, water_area_m2
- flood_zones.gpkg: Polygon, CRS EPSG:4326, fields include source_id, dfirm_id, zone_code, zone_subty, sfha_tf
- school_points.gpkg: Point, CRS EPSG:4326, fields include school_id, name, city, state, zip, county_name
- temperature_raster.tif: raster, CRS EPSG:4326
- zonal_input_for_map.gpkg: MultiPolygon, CRS EPSG:4326, fields include tract_id, temp_mean, temp_sum

GeoPandas guardrails:
- Do not use CRS.is_valid; pyproj CRS objects do not provide that property here.
- Use gdf.crs is None to check missing CRS.
- Use gdf.to_crs(epsg=3857) before metric buffers/areas.
- For spatial join use gpd.sjoin(..., predicate="intersects"), not op=.
- After overlay, fields named name may become name_1/name_2; restore required fields before saving.
- For buffering points, keep a GeoDataFrame with geometry as the buffered geometry.
- For raster masking, reproject vector masks to src.crs before rasterio.mask.mask.
"""


def extract_code(text: str) -> str:
    text = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", text)
    text = re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", text)
    text = text.replace("\x1b[", "")
    stripped = text.strip()
    if "```" not in stripped:
        return stripped + "\n"
    parts = stripped.split("```")
    for part in parts:
        candidate = part
        if candidate.lstrip().startswith("python"):
            candidate = candidate.lstrip()[len("python"):]
        if "import " in candidate or "from " in candidate:
            return candidate.strip() + "\n"
    return stripped.replace("```python", "").replace("```", "").strip() + "\n"


def generate(model: str, mode: str, task: dict, timeout: int) -> str:
    profile = DATA_PROFILE if mode == "geoguard" else ""
    prompt = f"""{SYSTEM_PROMPTS[mode]}

{COMMON_INSTRUCTIONS}

{profile}

Task ID: {task['task_id']}
Task type: {task['type']}
Required output filename: {task['output']}
Required output fields when vector output is requested: {task.get('required_fields', [])}

User request:
{task['prompt']}
"""
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False, "options": {"temperature": 0.0}}).encode("utf-8")
    req = urllib.request.Request("http://127.0.0.1:11434/api/generate", data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return extract_code(data.get("response", ""))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="qwen2.5-coder:7b")
    parser.add_argument("--modes", nargs="+", default=["basic", "planner", "geoguard"])
    parser.add_argument("--task-limit", type=int, default=None)
    parser.add_argument("--task-ids", nargs="*", default=None)
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()

    tasks = json.loads(TASKS_PATH.read_text(encoding="utf-8"))
    if args.task_ids:
        keep = set(args.task_ids)
        tasks = [t for t in tasks if t["task_id"] in keep]
    if args.task_limit:
        tasks = tasks[: args.task_limit]

    manifest = []
    for mode in args.modes:
        for task in tasks:
            out_dir = OUT_ROOT / args.model.replace(":", "_") / mode
            out_dir.mkdir(parents=True, exist_ok=True)
            out_file = out_dir / f"{task['task_id']}_{mode}.py"
            if out_file.exists() and out_file.stat().st_size > 0:
                code = out_file.read_text(encoding="utf-8")
                status = "cached"
            else:
                try:
                    code = generate(args.model, mode, task, args.timeout)
                    out_file.write_text(code, encoding="utf-8")
                    status = "generated"
                except Exception as exc:
                    out_file.write_text(f"# GENERATION_FAILED: {exc}\n", encoding="utf-8")
                    status = "failed"
            manifest.append({
                "model": args.model,
                "mode": mode,
                "task_id": task["task_id"],
                "task_type": task["type"],
                "output": task["output"],
                "script": str(out_file.relative_to(ROOT)),
                "status": status,
            })
            print(f"{status}: {args.model} {mode} {task['task_id']}")

    manifest_path = OUT_ROOT / args.model.replace(":", "_") / "generation_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Wrote {manifest_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
