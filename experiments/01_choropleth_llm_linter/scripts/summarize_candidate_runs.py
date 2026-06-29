#!/usr/bin/env python3
"""Summarize candidate execution runs into CSV and Markdown tables."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RUNS_DIR = ROOT / "experiments/01_choropleth_llm_linter/outputs/candidate_runs"
OUT_DIR = ROOT / "experiments/01_choropleth_llm_linter/outputs"


def classify_files(files: list[str]) -> dict[str, bool]:
    return {
        "has_static_png": any(name.endswith(".png") and "static" in name for name in files),
        "has_interactive_html": any(name.endswith(".html") for name in files),
        "has_time_series_png": any(name == "time_series.png" for name in files),
    }


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def main() -> None:
    rows: list[dict[str, object]] = []
    for meta_path in sorted(RUNS_DIR.glob("*/metadata.json")):
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        run_dir = meta_path.parent
        files = meta.get("created_files", [])
        file_flags = classify_files(files)
        stderr = read_text(run_dir / "stderr.txt")
        stdout = read_text(run_dir / "stdout.txt")
        rows.append(
            {
                "run_id": run_dir.name,
                "prompt_id": meta["prompt_id"],
                "candidate": Path(meta["candidate"]).name,
                "returncode": meta["returncode"],
                "timed_out": meta["timed_out"],
                "elapsed_seconds": meta["elapsed_seconds"],
                **file_flags,
                "stdout_preview": " | ".join(stdout.strip().splitlines()[:3]),
                "stderr_preview": " | ".join(stderr.strip().splitlines()[-3:]),
            }
        )

    rows.sort(key=lambda r: (str(r["prompt_id"]), str(r["candidate"]), str(r["run_id"])))
    csv_path = OUT_DIR / "candidate_run_summary.csv"
    md_path = OUT_DIR / "candidate_run_summary.md"

    fieldnames = [
        "run_id",
        "prompt_id",
        "candidate",
        "returncode",
        "timed_out",
        "elapsed_seconds",
        "has_static_png",
        "has_interactive_html",
        "has_time_series_png",
        "stdout_preview",
        "stderr_preview",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# Candidate Run Summary",
        "",
        f"Total runs: {len(rows)}",
        "",
        "| Prompt | Candidate | Return | Static PNG | Interactive HTML | Time Series | Notes |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        notes = row["stdout_preview"] or row["stderr_preview"]
        if notes and len(str(notes)) > 120:
            notes = str(notes)[:117] + "..."
        lines.append(
            "| {prompt_id} | {candidate} | {returncode} | {has_static_png} | {has_interactive_html} | {has_time_series_png} | {notes} |".format(
                **{**row, "notes": str(notes).replace("|", "/")}
            )
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {csv_path.relative_to(ROOT)}")
    print(f"Wrote {md_path.relative_to(ROOT)}")
    print(f"runs={len(rows)} success={sum(1 for r in rows if r['returncode'] == 0)} failed={sum(1 for r in rows if r['returncode'] != 0)}")


if __name__ == "__main__":
    main()

