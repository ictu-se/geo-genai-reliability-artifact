#!/usr/bin/env python3
"""One-step repair for failed generated task scripts using Ollama."""

from __future__ import annotations

import argparse
import csv
import json
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TASKS_PATH = ROOT / "experiments/04_geo_faithfulness_evaluator/inputs/llm_tasks_30.json"
GEN_ROOT = ROOT / "experiments/04_geo_faithfulness_evaluator/outputs/llm_code_benchmark/generated_code"
RUN_ROOT = ROOT / "experiments/04_geo_faithfulness_evaluator/outputs/llm_code_benchmark/runs"


def extract_code(text: str) -> str:
    if "```" not in text:
        return text.strip() + "\n"
    parts = text.split("```")
    for part in parts:
        candidate = part
        if candidate.lstrip().startswith("python"):
            candidate = candidate.lstrip()[len("python"):]
        if "import " in candidate or "from " in candidate:
            return candidate.strip() + "\n"
    return text.replace("```python", "").replace("```", "").strip() + "\n"


def ask_ollama(model: str, prompt: str, timeout: int) -> str:
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False, "options": {"temperature": 0.0}}).encode("utf-8")
    req = urllib.request.Request("http://127.0.0.1:11434/api/generate", data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return extract_code(data.get("response", ""))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="qwen2.5-coder:7b")
    parser.add_argument("--modes", nargs="+", default=["planner", "geoguard"])
    parser.add_argument("--timeout", type=int, default=240)
    args = parser.parse_args()

    model_slug = args.model.replace(":", "_")
    tasks = {t["task_id"]: t for t in json.loads(TASKS_PATH.read_text(encoding="utf-8"))}
    manifest = RUN_ROOT / model_slug / "execution_manifest.csv"
    repaired = []
    with manifest.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["mode"] not in args.modes or row["returncode"] == "0":
                continue
            task = tasks[row["task_id"]]
            script = ROOT / row["script"]
            run_dir = ROOT / row["run_dir"]
            stderr = (run_dir / "stderr.txt").read_text(encoding="utf-8", errors="replace")[:4000]
            code = script.read_text(encoding="utf-8", errors="replace")[:10000]
            prompt = f"""You are repairing generated Python GIS code.

Return only complete executable Python code, no Markdown.

The code must use:
- GEOGUARD_DATA_DIR for input data
- GEOGUARD_OUTPUT_DIR for output
- exact output filename: {task['output']}

Available files:
hospital_points.gpkg, study_boundary.gpkg, census_tracts.gpkg, flood_zones.gpkg, school_points.gpkg, temperature_raster.tif, zonal_input_for_map.gpkg

Task:
{task['prompt']}

Broken code:
{code}

Error traceback:
{stderr}

Repair the code robustly. Prefer geopandas/rasterio/rasterstats/matplotlib. Avoid osgeo/GDAL Python bindings.
"""
            fixed = ask_ollama(args.model, prompt, args.timeout)
            repair_dir = GEN_ROOT / model_slug / f"{row['mode']}_repair"
            repair_dir.mkdir(parents=True, exist_ok=True)
            out_script = repair_dir / f"{task['task_id']}_{row['mode']}_repair.py"
            out_script.write_text(fixed, encoding="utf-8")
            repaired.append({"model": args.model, "mode": f"{row['mode']}_repair", "task_id": task["task_id"], "script": str(out_script.relative_to(ROOT))})
            print(f"repaired {row['mode']} {task['task_id']}")
    out = GEN_ROOT / model_slug / "repair_manifest.json"
    out.write_text(json.dumps(repaired, indent=2), encoding="utf-8")
    print(f"Wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

