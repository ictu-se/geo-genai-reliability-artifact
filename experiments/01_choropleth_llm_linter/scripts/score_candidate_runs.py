#!/usr/bin/env python3
"""Score candidate runs with a lightweight task-specific rubric."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RUNS_DIR = ROOT / "experiments/01_choropleth_llm_linter/outputs/candidate_runs"
OUT_DIR = ROOT / "experiments/01_choropleth_llm_linter/outputs"


REQUIREMENTS = {
    "P01_static_basic": ["static"],
    "P02_static_with_crs_repair": ["static", "crs_repair"],
    "P03_interactive_basic": ["interactive"],
    "P04_csv_time_series": ["time_series", "max_year_report"],
    "P05_robust_cartographic_output": ["static", "interactive", "crs_repair", "diagnostic_report"],
    "P05_wrong_column": ["static", "interactive", "crs_repair", "diagnostic_report"],
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def has_nonempty(run_dir: Path, name: str) -> bool:
    path = run_dir / name
    return path.exists() and path.stat().st_size > 0


def score_run(run_dir: Path) -> dict[str, object]:
    meta = json.loads((run_dir / "metadata.json").read_text(encoding="utf-8"))
    prompt_id = meta["prompt_id"]
    stdout = read(run_dir / "stdout.txt")
    candidate_path = ROOT / meta["candidate"]
    source = read(candidate_path)
    static_ok = has_nonempty(run_dir, "map_static.png")
    interactive_ok = has_nonempty(run_dir, "map_interactive.html")
    time_series_ok = has_nonempty(run_dir, "time_series.png")
    returncode_ok = meta["returncode"] == 0 and not meta["timed_out"]

    checks: dict[str, bool] = {
        "execution_success": returncode_ok,
        "static": static_ok,
        "interactive": interactive_ok,
        "time_series": time_series_ok,
        "crs_repair": "set_crs" in source or "to_crs" in source or "missing_crs=True" in stdout,
        "diagnostic_report": all(token in stdout for token in ["features=", "missing_crs=", "invalid_geometries="]),
        "max_year_report": "max_burned_area_year=2017" in stdout,
    }

    required = ["execution_success"] + REQUIREMENTS.get(prompt_id, [])
    passed = sum(1 for key in required if checks.get(key, False))
    score = passed / len(required) if required else 0.0
    return {
        "run_id": run_dir.name,
        "prompt_id": prompt_id,
        "candidate": Path(meta["candidate"]).name,
        "score": round(score, 3),
        "passed": passed,
        "required": len(required),
        "failed_checks": ", ".join(key for key in required if not checks.get(key, False)),
        **{f"check_{key}": checks[key] for key in sorted(checks)},
    }


def main() -> None:
    rows = [score_run(path.parent) for path in sorted(RUNS_DIR.glob("*/metadata.json"))]
    rows.sort(key=lambda r: (str(r["prompt_id"]), str(r["candidate"]), str(r["run_id"])))

    csv_path = OUT_DIR / "candidate_scores.csv"
    md_path = OUT_DIR / "candidate_scores.md"
    fieldnames = sorted({key for row in rows for key in row})
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# Candidate Scores",
        "",
        "| Prompt | Candidate | Score | Passed | Failed checks |",
        "|---|---|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['prompt_id']} | {row['candidate']} | {row['score']:.3f} | {row['passed']}/{row['required']} | {row['failed_checks']} |"
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {csv_path.relative_to(ROOT)}")
    print(f"Wrote {md_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
