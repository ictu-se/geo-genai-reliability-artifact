#!/usr/bin/env python3
"""Run generated task scripts and capture artifacts/logs."""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT / "data/raw/geoguard/geoguard/data"
TASKS_PATH = ROOT / "experiments/04_geo_faithfulness_evaluator/inputs/llm_tasks_30.json"
GEN_ROOT = ROOT / "experiments/04_geo_faithfulness_evaluator/outputs/llm_code_benchmark/generated_code"
RUN_ROOT = ROOT / "experiments/04_geo_faithfulness_evaluator/outputs/llm_code_benchmark/runs"


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

    rows = []
    model_slug = args.model.replace(":", "_")
    for mode in args.modes:
        for task in tasks:
            script = GEN_ROOT / model_slug / mode / f"{task['task_id']}_{mode}.py"
            run_dir = RUN_ROOT / model_slug / mode / task["task_id"]
            run_dir.mkdir(parents=True, exist_ok=True)
            env = os.environ.copy()
            env["GEOGUARD_DATA_DIR"] = str(DATA_DIR)
            env["GEOGUARD_OUTPUT_DIR"] = str(run_dir)
            started = time.time()
            try:
                proc = subprocess.run([sys.executable, str(script)], cwd=ROOT, env=env, text=True, capture_output=True, timeout=args.timeout)
                returncode, timed_out, stdout, stderr = proc.returncode, False, proc.stdout, proc.stderr
            except subprocess.TimeoutExpired as exc:
                returncode, timed_out, stdout, stderr = None, True, exc.stdout or "", exc.stderr or ""
            (run_dir / "stdout.txt").write_text(stdout or "", encoding="utf-8")
            (run_dir / "stderr.txt").write_text(stderr or "", encoding="utf-8")
            row = {
                "model": args.model,
                "mode": mode,
                "task_id": task["task_id"],
                "task_type": task["type"],
                "expected_output": task["output"],
                "script": str(script.relative_to(ROOT)),
                "run_dir": str(run_dir.relative_to(ROOT)),
                "returncode": returncode,
                "timed_out": timed_out,
                "elapsed_seconds": round(time.time() - started, 3),
                "output_exists": (run_dir / task["output"]).exists(),
            }
            rows.append(row)
            print(row)

    out_csv = RUN_ROOT / model_slug / "execution_manifest.csv"
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {out_csv.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

