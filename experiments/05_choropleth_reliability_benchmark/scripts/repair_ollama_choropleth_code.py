#!/usr/bin/env python3
"""Repair failed generated choropleth scripts using Ollama feedback."""

from __future__ import annotations

import argparse
import json
import re
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RUN_ROOT = ROOT / "experiments/05_choropleth_reliability_benchmark/outputs/runs"
REPAIR_ROOT = ROOT / "experiments/05_choropleth_reliability_benchmark/outputs/generated_code_repaired"
TASKS_PATH = ROOT / "experiments/05_choropleth_reliability_benchmark/inputs/prompts_expanded.json"


DATA_PROFILE = """
The repaired script must use only local data through these environment variables:
- CHOROPLETH_DATA_DIR
- CHOROPLETH_OUTPUT_DIR

Available files:
- MCD64.006.yearly-ba-nf.2002-2022.PRT_Portugal.csv
- mainlandburn.shp
- boundary.shp

Known columns:
- CSV: Year, Burned Area [ha], Number of Fires
- mainlandburn.shp: Burned_Are, of_Fires, geometry

Known data issues:
- mainlandburn.shp may have missing CRS. If missing, set EPSG:4326.
- boundary.shp has an invalid geometry. Use shapely.make_valid if available, otherwise buffer(0).

Use these rules:
- Return only executable Python code, no Markdown fences.
- Do not download data.
- Do not hard-code path/to/data or fake filenames.
- Use pathlib.Path(os.environ["CHOROPLETH_DATA_DIR"]) and pathlib.Path(os.environ["CHOROPLETH_OUTPUT_DIR"]).
- Import all modules you use.
- For GeoPandas spatial joins, use predicate=, not op=.
- If a task asks for diagnostics, write diagnostics.json.
- If static map is required, write map_static.png.
- If interactive map is required, write map_interactive.html.
- If a time series is required, write time_series.png.
"""


def load_tasks() -> dict[str, dict]:
    tasks = json.loads(TASKS_PATH.read_text(encoding="utf-8"))
    return {task["prompt_id"]: task for task in tasks}


def required_artifacts(meta: dict, tasks: dict[str, dict]) -> list[str]:
    task = tasks.get(meta["prompt_id"], {})
    output_map = {
        "static_png": "map_static.png",
        "interactive_html": "map_interactive.html",
        "time_series_png": "time_series.png",
        "diagnostic_json": "diagnostics.json",
    }
    return [output_map[name] for name in task.get("required_outputs", []) if name in output_map]


def is_incomplete(meta: dict, tasks: dict[str, dict]) -> bool:
    if meta.get("model") == "validator_repair_reference" or meta.get("repaired"):
        return False
    if meta.get("returncode") != 0 or meta.get("timed_out"):
        return True
    run_dir = ROOT / meta["run_dir"]
    return any(not (run_dir / artifact).exists() or (run_dir / artifact).stat().st_size == 0 for artifact in required_artifacts(meta, tasks))


def load_current_incomplete_runs(tasks: dict[str, dict]) -> list[dict]:
    metas: list[dict] = []
    for manifest_path in sorted(RUN_ROOT.glob("*/run_manifest.json")):
        model_metas = json.loads(manifest_path.read_text(encoding="utf-8"))
        metas.extend(meta for meta in model_metas if is_incomplete(meta, tasks))
    return metas


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


def repair(model: str, code: str, stderr: str, metadata: dict, timeout: int) -> str:
    prompt = f"""You are repairing a failed Python GIS mapping script.

{DATA_PROFILE}

Run metadata:
{json.dumps(metadata, indent=2)}

Required output files:
{json.dumps(required_artifacts(metadata, load_tasks()))}

Original code:
```python
{code}
```

Runtime stderr:
```
{stderr[-5000:]}
```

Write a corrected full Python script that satisfies the same task and avoids the error.
"""
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False, "options": {"temperature": 0.0}}).encode("utf-8")
    req = urllib.request.Request("http://127.0.0.1:11434/api/generate", data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return extract_code(data.get("response", ""))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="qwen2.5-coder:32b")
    parser.add_argument("--run-limit", type=int, default=None)
    parser.add_argument("--timeout", type=int, default=240)
    args = parser.parse_args()

    tasks = load_tasks()
    failed = load_current_incomplete_runs(tasks)
    if args.run_limit:
        failed = failed[: args.run_limit]

    manifest = []
    repair_model_slug = args.model.replace(":", "_")
    for meta in failed:
        source_path = ROOT / meta["script"]
        code = source_path.read_text(encoding="utf-8", errors="replace")
        run_dir = ROOT / meta["run_dir"]
        stderr = (run_dir / "stderr.txt").read_text(encoding="utf-8", errors="replace")
        out_dir = REPAIR_ROOT / repair_model_slug / meta["model"] / meta["mode"]
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / f"{meta['prompt_id']}_{meta['mode']}_repair.py"
        if out_file.exists() and out_file.stat().st_size > 0:
            status = "cached"
        else:
            try:
                repaired = repair(args.model, code, stderr, meta, args.timeout)
                out_file.write_text(repaired, encoding="utf-8")
                status = "repaired"
            except Exception as exc:
                out_file.write_text(f"# REPAIR_FAILED: {exc}\n", encoding="utf-8")
                status = "failed"
        manifest.append({**meta, "repair_model": args.model, "repaired_script": str(out_file.relative_to(ROOT)), "repair_status": status})
        print(f"{status}: {meta['mode']} {meta['prompt_id']}")

    manifest_path = REPAIR_ROOT / repair_model_slug / "repair_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Wrote {manifest_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
