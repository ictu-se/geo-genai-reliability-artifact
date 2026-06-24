#!/usr/bin/env python3
"""Summarize local VLM judge schema adherence and usable-review coverage."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MS_DIR = ROOT / "manuscripts/q1_geo_genai_reliability"
OUT_DIR = MS_DIR / "submission/evaluator_reliability"

MAPGEN_DIR = ROOT / "experiments/02_mapgenerator_image_text_audit/outputs"
CHORO_DIR = ROOT / "experiments/05_choropleth_reliability_benchmark/outputs/scores"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def pct(num: int, den: int) -> str:
    return f"{(100 * num / den):.1f}" if den else "0.0"


def row_from_summary(task: str, summary_path: Path) -> dict[str, str]:
    summary = read_json(summary_path)
    model = summary["model"]
    if task == "MapGenerator caption fidelity":
        groups = summary["by_split"].values()
        total = sum(int(item["reviewed_pairs"]) for item in groups)
        errors = sum(int(item["verdict_counts"].get("error", 0)) for item in summary["by_split"].values())
        usable = total - errors
        mean_scores = [
            float(item["mean_vlm_alignment_score"])
            for item in summary["by_split"].values()
            if int(item["reviewed_pairs"]) - int(item["verdict_counts"].get("error", 0)) > 0
        ]
        score_label = "mean alignment"
    else:
        groups = summary["by_source_group"].values()
        total = sum(int(item["reviewed_artifacts"]) for item in groups)
        errors = sum(int(item["verdict_counts"].get("error", 0)) for item in summary["by_source_group"].values())
        usable = total - errors
        mean_scores = [
            float(item["mean_vlm_cartographic_quality_score"])
            for item in summary["by_source_group"].values()
            if int(item["reviewed_artifacts"]) - int(item["verdict_counts"].get("error", 0)) > 0
        ]
        score_label = "mean quality"
    if usable == total and total >= 18:
        role = "agreement_panel"
    elif usable >= max(5, total // 2):
        role = "candidate_partial"
    else:
        role = "failed_candidate"
    return {
        "Task": task,
        "Model": model,
        "Reviewed": str(total),
        "Usable reviews": str(usable),
        "Errors": str(errors),
        "Usable rate pct": pct(usable, total),
        "Score field": score_label,
        "Mean score across groups": f"{sum(mean_scores) / len(mean_scores):.3f}" if mean_scores else "",
        "Panel role": role,
        "Summary file": str(summary_path.relative_to(ROOT)),
    }


def collect_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in sorted(MAPGEN_DIR.glob("mapgenerator_vlm_caption_review_summary_*.json")):
        rows.append(row_from_summary("MapGenerator caption fidelity", path))
    for path in sorted(CHORO_DIR.glob("choropleth_vlm_cartographic_review_summary_*.json")):
        rows.append(row_from_summary("Choropleth cartographic quality", path))
    rows.sort(key=lambda row: (row["Task"], row["Panel role"], row["Model"]))
    return rows


def build_report(rows: list[dict[str, str]]) -> str:
    task_rows: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        task_rows.setdefault(row["Task"], []).append(row)

    lines = [
        "# VLM Judge Robustness Audit",
        "",
        "This audit checks whether local vision-language models obeyed the JSON review schema well enough to serve as evaluators. It is an evaluator-validity artifact, not a substitute for human labels.",
        "",
        "## Summary",
        "",
    ]
    for task, group in sorted(task_rows.items()):
        agreement = [row for row in group if row["Panel role"] == "agreement_panel"]
        partial = [row for row in group if row["Panel role"] == "candidate_partial"]
        failed = [row for row in group if row["Panel role"] == "failed_candidate"]
        lines += [
            f"### {task}",
            "",
            f"- agreement-panel models: {', '.join(row['Model'] for row in agreement) or 'none'}",
            f"- partial candidate models: {', '.join(row['Model'] for row in partial) or 'none'}",
            f"- failed candidate models: {', '.join(row['Model'] for row in failed) or 'none'}",
            "",
        ]

    lines += [
        "## Model-Level Results",
        "",
        "| Task | Model | Reviewed | Usable | Errors | Usable rate pct | Role |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['Task']} | `{row['Model']}` | {row['Reviewed']} | {row['Usable reviews']} | {row['Errors']} | {row['Usable rate pct']} | {row['Panel role']} |"
        )
    lines += [
        "",
        "## Interpretation",
        "",
        "- The current agreement tables should remain based on Granite and Qwen because both produced complete schema-conformant reviews for the paired panels.",
        "- Additional local VLMs are useful as stress tests, but schema adherence is itself a reliability variable: weak JSON compliance can create evaluator failure even when an image model can describe maps conversationally.",
        "- This supports the manuscript's conservative use of VLMs as pilot evaluators and adjudication queues rather than ground-truth cartographic labels.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    rows = collect_rows()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(OUT_DIR / "vlm_judge_robustness_audit.csv", rows)
    (OUT_DIR / "vlm_judge_robustness_audit.md").write_text(build_report(rows), encoding="utf-8")
    print(f"Wrote {(OUT_DIR / 'vlm_judge_robustness_audit.csv').relative_to(ROOT)}")
    print(f"Wrote {(OUT_DIR / 'vlm_judge_robustness_audit.md').relative_to(ROOT)}")


if __name__ == "__main__":
    main()
