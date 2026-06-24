#!/usr/bin/env python3
"""Summarize expanded choropleth benchmark into initial vs best-repair conditions."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCORES = ROOT / "experiments/05_choropleth_reliability_benchmark/outputs/scores"


def read_rows() -> list[dict[str, str]]:
    path = SCORES / "expanded_choropleth_benchmark_scores.csv"
    if not path.exists():
        path = SCORES / "expanded_choropleth_pilot_scores.csv"
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main() -> None:
    rows = read_rows()
    rows = select_benchmark_rows(rows)
    grouped: dict[tuple[str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        if row.get("repaired") == "True":
            repair_model = row.get("repair_model") or "unknown"
            condition = f"repair_by_{repair_model}"
        else:
            condition = "initial"
        grouped[(row["model"], row["mode"], row["prompt_id"], condition)].append(row)

    out_rows = []
    for (model, mode, prompt_id, condition), group in sorted(grouped.items()):
        best = max(group, key=lambda row: float(row["score"]))
        out_rows.append(
            {
                "model": model,
                "mode": mode,
                "prompt_id": prompt_id,
                "condition": condition,
                "attempts": str(len(group)),
                "best_score": best["score"],
                "best_passed": best["passed"],
                "best_required": best["required"],
                "execution_success_any": str(any(row["check_execution_success"] == "True" for row in group)),
                "static_png_any": str(any(row["check_static_png"] == "True" for row in group)),
                "diagnostic_json_any": str(any(row["check_diagnostic_json"] == "True" for row in group)),
                "failed_checks_best": best["failed_checks"],
            }
        )

    out_path = SCORES / "expanded_choropleth_condition_summary.csv"
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        writer.writeheader()
        writer.writerows(out_rows)

    lines = [
        "# Expanded Choropleth Benchmark Condition Summary",
        "",
        "| Model | Mode | Prompt | Condition | Attempts | Best score | Best passed | Execution any | Failed checks |",
        "|---|---|---|---|---:|---:|---:|---|---|",
    ]
    for row in out_rows:
        lines.append(
            f"| {row['model']} | {row['mode']} | {row['prompt_id']} | {row['condition']} | {row['attempts']} | {row['best_score']} | {row['best_passed']}/{row['best_required']} | {row['execution_success_any']} | {row['failed_checks_best']} |"
        )
    (SCORES / "expanded_choropleth_condition_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out_path.relative_to(ROOT)}")
    print(f"Wrote {(SCORES / 'expanded_choropleth_condition_summary.md').relative_to(ROOT)}")


def select_benchmark_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Use the latest initial run per prompt/mode, while preserving repair attempts."""
    selected: list[dict[str, str]] = []
    latest_initial: dict[tuple[str, str, str], dict[str, str]] = {}
    for row in rows:
        if row.get("repaired") == "True":
            selected.append(row)
            continue
        key = (row["model"], row["mode"], row["prompt_id"])
        current = latest_initial.get(key)
        if current is None or row["run_id"] > current["run_id"]:
            latest_initial[key] = row
    selected.extend(latest_initial.values())
    return selected


if __name__ == "__main__":
    main()
