#!/usr/bin/env python3
"""Run a generated GeoGuard candidate script in an isolated output folder."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT / "data/raw/geoguard/geoguard/data"
RUNS_DIR = ROOT / "experiments/04_geo_faithfulness_evaluator/outputs/live_llm_eval/runs"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--system", required=True)
    parser.add_argument("--timeout", type=int, default=240)
    args = parser.parse_args()

    candidate = args.candidate.resolve()
    run_id = f"{args.system}_{candidate.stem}_{time.strftime('%Y%m%d_%H%M%S')}"
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["GEOGUARD_DATA_DIR"] = str(DATA_DIR)
    env["GEOGUARD_OUTPUT_DIR"] = str(run_dir)

    started = time.time()
    try:
        proc = subprocess.run(
            [sys.executable, str(candidate)],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            timeout=args.timeout,
        )
        timed_out = False
        stdout, stderr, returncode = proc.stdout, proc.stderr, proc.returncode
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        stdout, stderr, returncode = exc.stdout or "", exc.stderr or "", None

    (run_dir / "stdout.txt").write_text(stdout or "", encoding="utf-8")
    (run_dir / "stderr.txt").write_text(stderr or "", encoding="utf-8")

    metadata = {
        "system": args.system,
        "candidate": str(candidate.relative_to(ROOT)),
        "run_dir": str(run_dir.relative_to(ROOT)),
        "returncode": returncode,
        "timed_out": timed_out,
        "elapsed_seconds": round(time.time() - started, 3),
        "created_files": sorted(str(p.relative_to(run_dir)) for p in run_dir.rglob("*") if p.is_file()),
    }
    (run_dir / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps(metadata, indent=2))
    raise SystemExit(124 if timed_out else (returncode or 0))


if __name__ == "__main__":
    main()

