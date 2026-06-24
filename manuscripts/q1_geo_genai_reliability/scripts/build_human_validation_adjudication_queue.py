#!/usr/bin/env python3
"""Build adjudication queue and final-label template for human validation."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MS_DIR = ROOT / "manuscripts/q1_geo_genai_reliability"
PANEL_DIR = MS_DIR / "submission/human_validation_panels"
OUT_DIR = PANEL_DIR / "summaries"
PRIORITY_QUEUE = PANEL_DIR / "human_validation_priority_queue.csv"
ANNOTATOR_DIR = PANEL_DIR / "annotator_packets"


TASKS = {
    "mapgenerator_caption_fidelity": {
        "label_field": "human_caption_support",
        "score_field": "",
        "default_a": ANNOTATOR_DIR / "mapgenerator_caption_fidelity_A_completed.csv",
        "default_b": ANNOTATOR_DIR / "mapgenerator_caption_fidelity_B_completed.csv",
    },
    "choropleth_cartographic_quality": {
        "label_field": "human_verdict",
        "score_field": "human_cartographic_quality",
        "default_a": ANNOTATOR_DIR / "choropleth_cartographic_quality_A_completed.csv",
        "default_b": ANNOTATOR_DIR / "choropleth_cartographic_quality_B_completed.csv",
    },
}


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def clean(value: str | None) -> str:
    return (value or "").strip()


def usable_band(label: str) -> str:
    if label in {"usable", "usable_with_minor_issues"}:
        return "usable_or_minor"
    if label in {"weak", "failed"}:
        return "below_usable"
    return label


def by_panel(path: Path) -> dict[str, dict[str, str]]:
    return {clean(row.get("panel_id")): row for row in read_csv(path) if clean(row.get("panel_id"))}


def agreement_status(task: str, a_label: str, b_label: str, a_score: str, b_score: str) -> str:
    if not a_label and not b_label:
        return "missing_labels"
    if not a_label or not b_label:
        return "single_label_only"
    if task == "choropleth_cartographic_quality":
        score_gap = ""
        if a_score and b_score:
            try:
                score_gap = abs(float(a_score) - float(b_score))
            except ValueError:
                score_gap = ""
        if a_label == b_label and usable_band(a_label) == usable_band(b_label) and (score_gap == "" or score_gap <= 1):
            return "agreement"
        return "adjudication_required"
    if a_label == b_label:
        return "agreement"
    return "adjudication_required"


def final_from_status(status: str, a_label: str, b_label: str, a_score: str, b_score: str) -> tuple[str, str]:
    if status != "agreement":
        return "", ""
    final_label = a_label or b_label
    if a_score and b_score:
        try:
            return final_label, f"{(float(a_score) + float(b_score)) / 2:.3f}"
        except ValueError:
            return final_label, ""
    return final_label, a_score or b_score


def build_rows(
    mapgen_a: Path,
    mapgen_b: Path,
    choro_a: Path,
    choro_b: Path,
) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    labels = {
        "mapgenerator_caption_fidelity": (by_panel(mapgen_a), by_panel(mapgen_b)),
        "choropleth_cartographic_quality": (by_panel(choro_a), by_panel(choro_b)),
    }
    queue_rows: list[dict[str, str]] = []
    final_rows: list[dict[str, str]] = []
    summary: dict[str, dict[str, int]] = {
        task: {
            "priority_items": 0,
            "urgent_items": 0,
            "agreement": 0,
            "adjudication_required": 0,
            "single_label_only": 0,
            "missing_labels": 0,
            "final_ready": 0,
            "urgent_missing_labels": 0,
            "urgent_final_ready": 0,
        }
        for task in TASKS
    }
    for priority in read_csv(PRIORITY_QUEUE):
        task = clean(priority.get("task"))
        if task not in TASKS:
            continue
        panel_id = clean(priority.get("panel_id"))
        fields = TASKS[task]
        a_rows, b_rows = labels[task]
        a = a_rows.get(panel_id, {})
        b = b_rows.get(panel_id, {})
        a_label = clean(a.get(fields["label_field"]))
        b_label = clean(b.get(fields["label_field"]))
        a_score = clean(a.get(fields["score_field"])) if fields["score_field"] else ""
        b_score = clean(b.get(fields["score_field"])) if fields["score_field"] else ""
        status = agreement_status(task, a_label, b_label, a_score, b_score)
        final_label, final_score = final_from_status(status, a_label, b_label, a_score, b_score)
        row = {
            "task": task,
            "panel_id": panel_id,
            "priority": clean(priority.get("priority")),
            "annotator_a_label": a_label,
            "annotator_b_label": b_label,
            "annotator_a_score": a_score,
            "annotator_b_score": b_score,
            "agreement_status": status,
            "adjudicator_label": "",
            "adjudicator_score": "",
            "final_label": final_label,
            "final_score": final_score,
            "adjudication_notes": "",
        }
        queue_rows.append(row)
        final_rows.append(
            {
                "task": task,
                "panel_id": panel_id,
                "priority": row["priority"],
                "final_label": final_label,
                "final_score": final_score,
                "final_source": "two_annotator_agreement" if status == "agreement" else "",
                "ready_for_manuscript": str(status == "agreement"),
                "remaining_action": "none" if status == "agreement" else status,
            }
        )
        summary[task]["priority_items"] += 1
        is_urgent = row["priority"] == "urgent_vlm_disagreement"
        if is_urgent:
            summary[task]["urgent_items"] += 1
        summary[task][status] += 1
        if status == "agreement":
            summary[task]["final_ready"] += 1
            if is_urgent:
                summary[task]["urgent_final_ready"] += 1
        if status == "missing_labels" and is_urgent:
            summary[task]["urgent_missing_labels"] += 1
    summary_rows = [
        {
                "task": task,
                "priority_items": str(values["priority_items"]),
                "urgent_items": str(values["urgent_items"]),
                "agreement": str(values["agreement"]),
                "adjudication_required": str(values["adjudication_required"]),
                "single_label_only": str(values["single_label_only"]),
                "missing_labels": str(values["missing_labels"]),
                "final_ready": str(values["final_ready"]),
                "urgent_missing_labels": str(values["urgent_missing_labels"]),
                "urgent_final_ready": str(values["urgent_final_ready"]),
                "status": "ready_for_final_summary" if values["final_ready"] == values["priority_items"] else "awaiting_labels_or_adjudication",
            }
        for task, values in summary.items()
    ]
    return queue_rows, final_rows, summary_rows


def write_report(summary_rows: list[dict[str, str]]) -> None:
    lines = [
        "# Human Validation Adjudication Queue",
        "",
        "This report is generated from the two annotator packet files and the priority queue. It does not invent labels; blank annotator files remain explicit `missing_labels` cases.",
        "",
        "| Task | Priority items | Urgent items | Agreement | Needs adjudication | Single-label only | Missing labels | Urgent missing | Final ready | Urgent final ready | Status |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in summary_rows:
        lines.append(
            f"| {row['task']} | {row['priority_items']} | {row['urgent_items']} | {row['agreement']} | {row['adjudication_required']} | {row['single_label_only']} | {row['missing_labels']} | {row['urgent_missing_labels']} | {row['final_ready']} | {row['urgent_final_ready']} | {row['status']} |"
        )
    lines += [
        "",
        "## Closure Rule",
        "",
        "A task is ready for manuscript-level human-label claims only when every priority item has either two-annotator agreement or adjudicator-provided final labels in the completed agreement file.",
        "",
    ]
    (OUT_DIR / "human_validation_adjudication_queue.md").write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mapgenerator-a", type=Path, default=TASKS["mapgenerator_caption_fidelity"]["default_a"])
    parser.add_argument("--mapgenerator-b", type=Path, default=TASKS["mapgenerator_caption_fidelity"]["default_b"])
    parser.add_argument("--choropleth-a", type=Path, default=TASKS["choropleth_cartographic_quality"]["default_a"])
    parser.add_argument("--choropleth-b", type=Path, default=TASKS["choropleth_cartographic_quality"]["default_b"])
    args = parser.parse_args(argv)

    queue_rows, final_rows, summary_rows = build_rows(
        args.mapgenerator_a,
        args.mapgenerator_b,
        args.choropleth_a,
        args.choropleth_b,
    )
    fields = [
        "task",
        "panel_id",
        "priority",
        "annotator_a_label",
        "annotator_b_label",
        "annotator_a_score",
        "annotator_b_score",
        "agreement_status",
        "adjudicator_label",
        "adjudicator_score",
        "final_label",
        "final_score",
        "adjudication_notes",
    ]
    write_csv(OUT_DIR / "human_validation_adjudication_queue.csv", queue_rows, fields)
    write_csv(
        OUT_DIR / "human_validation_final_label_template.csv",
        final_rows,
        ["task", "panel_id", "priority", "final_label", "final_score", "final_source", "ready_for_manuscript", "remaining_action"],
    )
    write_csv(
        OUT_DIR / "human_validation_adjudication_summary.csv",
        summary_rows,
        [
            "task",
            "priority_items",
            "urgent_items",
            "agreement",
            "adjudication_required",
            "single_label_only",
            "missing_labels",
            "final_ready",
            "urgent_missing_labels",
            "urgent_final_ready",
            "status",
        ],
    )
    write_report(summary_rows)
    print(f"Wrote human validation adjudication queue to {OUT_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
