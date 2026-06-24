#!/usr/bin/env python3
"""Run generated choropleth benchmark scripts after safety scanning."""

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
DATA_DIR = ROOT / "data/repos/Materials-for-Creating-maps-by-Artificial-Intelligence/data_choropleth"
CODE_ROOT = ROOT / "experiments/05_choropleth_reliability_benchmark/outputs/generated_code"
REPAIR_ROOT = ROOT / "experiments/05_choropleth_reliability_benchmark/outputs/generated_code_repaired"
RUN_ROOT = ROOT / "experiments/05_choropleth_reliability_benchmark/outputs/runs"
SCORES_DIR = ROOT / "experiments/05_choropleth_reliability_benchmark/outputs/scores"


def load_safe_scripts(repaired: bool) -> set[str]:
    scan_path = SCORES_DIR / ("repaired_code_safety_scan.csv" if repaired else "generated_code_safety_scan.csv")
    if not scan_path.exists():
        return set()
    with scan_path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return {row["script"] for row in rows if row["safe_to_run"] == "True"}


def parse_script(script: Path) -> tuple[str, str, str]:
    # .../<model>/<mode>/<prompt_id>_<mode>.py
    mode = script.parent.name
    model = script.parent.parent.name
    stem = script.stem
    if stem.endswith("_repair"):
        stem = stem[: -len("_repair")]
    suffix = f"_{mode}"
    prompt_id = stem[: -len(suffix)] if stem.endswith(suffix) else stem
    return model, mode, prompt_id


def run_one(script: Path, timeout: int, repaired: bool = False) -> dict[str, object]:
    model, mode, prompt_id = parse_script(script)
    run_id = f"{model}_{mode}_{prompt_id}_{time.strftime('%Y%m%d_%H%M%S')}"
    run_dir = RUN_ROOT / model / mode / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["CHOROPLETH_DATA_DIR"] = str(DATA_DIR)
    env["CHOROPLETH_OUTPUT_DIR"] = str(run_dir)

    started = time.time()
    try:
        proc = subprocess.run(
            [sys.executable, str(script)],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            timeout=timeout,
        )
        timed_out = False
        stdout = proc.stdout or ""
        stderr = proc.stderr or ""
        returncode = proc.returncode
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        returncode = None

    elapsed = time.time() - started
    (run_dir / "stdout.txt").write_text(stdout, encoding="utf-8", errors="replace")
    (run_dir / "stderr.txt").write_text(stderr, encoding="utf-8", errors="replace")
    meta = {
        "model": model,
        "mode": mode,
        "prompt_id": prompt_id,
        "script": str(script.relative_to(ROOT)),
        "run_dir": str(run_dir.relative_to(ROOT)),
        "returncode": returncode,
        "timed_out": timed_out,
        "elapsed_seconds": round(elapsed, 3),
        "created_files": sorted(str(p.relative_to(run_dir)) for p in run_dir.rglob("*") if p.is_file()),
        "repaired": repaired,
    }
    (run_dir / "metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="qwen2.5-coder:7b")
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--include-unsafe", action="store_true")
    parser.add_argument("--repaired", action="store_true")
    args = parser.parse_args()

    model_slug = args.model.replace(":", "_")
    root = REPAIR_ROOT / model_slug if args.repaired else CODE_ROOT / model_slug
    scripts = sorted(root.rglob("*.py"))
    safe_scripts = load_safe_scripts(args.repaired)
    metas = []
    for script in scripts:
        rel = str(script.relative_to(ROOT))
        if not args.include_unsafe and rel not in safe_scripts:
            print(f"skip unsafe: {rel}")
            continue
        meta = run_one(script, args.timeout, repaired=args.repaired)
        metas.append(meta)
        print(f"ran: {rel} return={meta['returncode']} timeout={meta['timed_out']}")

    manifest_path = RUN_ROOT / model_slug / ("repair_run_manifest.json" if args.repaired else "run_manifest.json")
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(metas, indent=2), encoding="utf-8")
    print(f"Wrote {manifest_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
