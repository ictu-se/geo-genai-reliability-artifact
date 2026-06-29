#!/usr/bin/env python3
"""Generate choropleth benchmark candidate scripts with Ollama."""

from __future__ import annotations

import argparse
import json
import re
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TASKS_PATH = ROOT / "experiments/05_choropleth_reliability_benchmark/inputs/prompts_expanded.json"
OUT_ROOT = ROOT / "experiments/05_choropleth_reliability_benchmark/outputs/generated_code"


SYSTEM_PROMPTS = {
    "basic": "You are a Python mapping assistant. Write concise executable Python code for the user request.",
    "grounded": "You are a careful GIS coding assistant. Use the exact local files and columns provided. Validate inputs before mapping.",
    "rules": "You are a cartographic QA-aware GIS coding assistant. Write robust Python code with CRS checks, geometry repair, join diagnostics, map completeness checks, and reproducible outputs.",
}


DATA_PROFILE = """
Local data are available through environment variables:
- CHOROPLETH_DATA_DIR: directory containing the input files.
- CHOROPLETH_OUTPUT_DIR: directory where all outputs must be written.

Input files:
- MCD64.006.yearly-ba-nf.2002-2022.PRT_Portugal.csv
- mainlandburn.shp and sidecar files
- boundary.shp and sidecar files

Known columns from prior inspection:
- CSV columns include Year, Burned Area [ha], Number of Fires.
- mainlandburn.shp has thematic fields Burned_Are and of_Fires.

Known data issues:
- mainlandburn.shp may lack CRS metadata; coordinates look like lon/lat and should be treated as EPSG:4326 if missing.
- boundary.shp has one invalid geometry; repair invalid geometries before using boundary overlays.
"""


COMMON_INSTRUCTIONS = """
Return only executable Python code, with no Markdown fences.

Use only local files from CHOROPLETH_DATA_DIR. Do not download data. Do not require user input.
Use available Python libraries: geopandas, pandas, shapely, matplotlib, folium, branca, json, pathlib.
Always write outputs into CHOROPLETH_OUTPUT_DIR.

Naming convention:
- Static map: map_static.png
- Interactive map: map_interactive.html
- Time series: time_series.png
- Diagnostics: diagnostics.json

The script should create only the outputs requested by the task when possible.
If a requested field is missing, write diagnostics.json explaining the problem and exit gracefully.
"""


def extract_code(text: str) -> str:
    text = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", text)
    stripped = text.strip()
    if "```" not in stripped:
        return stripped + "\n"
    parts = stripped.split("```")
    for part in parts:
        candidate = part
        if candidate.lstrip().startswith("python"):
            candidate = candidate.lstrip()[len("python") :]
        if "import " in candidate or "from " in candidate:
            return candidate.strip() + "\n"
    return stripped.replace("```python", "").replace("```", "").strip() + "\n"


def generate(model: str, mode: str, task: dict, timeout: int) -> str:
    profile = DATA_PROFILE if mode in {"grounded", "rules"} else ""
    rule_block = ""
    if mode == "rules":
        rule_block = """
Cartographic and geospatial rules:
- Check CRS before spatial operations. If mainlandburn CRS is missing, set EPSG:4326.
- Repair invalid geometries with make_valid when available or buffer(0) fallback.
- Preserve all original geometry rows unless a diagnostic explicitly reports a drop.
- Use a sequential color ramp for burned area or number of fires.
- Include title and legend for static maps.
- For Folium, include tooltips and save a standalone HTML file.
- Always write diagnostics.json when requested.
"""
    prompt = f"""{SYSTEM_PROMPTS[mode]}

{COMMON_INSTRUCTIONS}

{profile}

{rule_block}

Task ID: {task['prompt_id']}
Task family: {task['family']}
Required outputs: {task['required_outputs']}

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
    parser.add_argument("--modes", nargs="+", default=["basic", "grounded", "rules"], choices=sorted(SYSTEM_PROMPTS))
    parser.add_argument("--task-limit", type=int, default=None)
    parser.add_argument("--task-ids", nargs="*", default=None)
    parser.add_argument("--timeout", type=int, default=240)
    args = parser.parse_args()

    tasks = json.loads(TASKS_PATH.read_text(encoding="utf-8"))
    if args.task_ids:
        keep = set(args.task_ids)
        tasks = [task for task in tasks if task["prompt_id"] in keep]
    if args.task_limit:
        tasks = tasks[: args.task_limit]

    manifest = []
    model_slug = args.model.replace(":", "_")
    for mode in args.modes:
        for task in tasks:
            out_dir = OUT_ROOT / model_slug / mode
            out_dir.mkdir(parents=True, exist_ok=True)
            out_file = out_dir / f"{task['prompt_id']}_{mode}.py"
            if out_file.exists() and out_file.stat().st_size > 0:
                status = "cached"
            else:
                try:
                    code = generate(args.model, mode, task, args.timeout)
                    out_file.write_text(code, encoding="utf-8")
                    status = "generated"
                except Exception as exc:
                    out_file.write_text(f"# GENERATION_FAILED: {exc}\n", encoding="utf-8")
                    status = "failed"
            manifest.append(
                {
                    "model": args.model,
                    "mode": mode,
                    "prompt_id": task["prompt_id"],
                    "family": task["family"],
                    "required_outputs": task["required_outputs"],
                    "script": str(out_file.relative_to(ROOT)),
                    "status": status,
                }
            )
            print(f"{status}: {args.model} {mode} {task['prompt_id']}")

    manifest_path = OUT_ROOT / model_slug / "generation_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Wrote {manifest_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

