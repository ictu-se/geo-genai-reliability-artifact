#!/usr/bin/env python3
"""Build final human-label summaries after adjudication, without fabricating labels."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MS_DIR = ROOT / "manuscripts/q1_geo_genai_reliability"
PANEL_DIR = MS_DIR / "submission/human_validation_panels"
OUT_DIR = PANEL_DIR / "summaries"
FINAL_TEMPLATE = OUT_DIR / "human_validation_final_label_template.csv"
DEFAULT_COMPLETED = PANEL_DIR / "human_validation_agreement_completed.csv"


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


def completed_final_by_key(path: Path) -> dict[tuple[str, str], dict[str, str]]:
    rows = {}
    for row in read_csv(path):
        task = clean(row.get("task"))
        panel_id = clean(row.get("panel_id"))
        if not task or not panel_id:
            continue
        rows[(task, panel_id)] = row
    return rows


def final_value(template_row: dict[str, str], completed_row: dict[str, str] | None) -> tuple[str, str, str, str]:
    if completed_row:
        label = clean(completed_row.get("final_label")) or clean(completed_row.get("adjudicator_label"))
        score = clean(completed_row.get("final_score")) or clean(completed_row.get("adjudicator_score"))
        source = "adjudicator_completed_file" if label or score else ""
        notes = clean(completed_row.get("adjudication_notes"))
        return label, score, source, notes
    label = clean(template_row.get("final_label"))
    score = clean(template_row.get("final_score"))
    source = clean(template_row.get("final_source"))
    return label, score, source, ""


def build_rows(completed_path: Path | None) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    template_rows = read_csv(FINAL_TEMPLATE)
    completed = completed_final_by_key(completed_path) if completed_path and completed_path.exists() else {}
    ledger_rows: list[dict[str, str]] = []
    by_task: dict[str, list[dict[str, str]]] = {}
    for row in template_rows:
        task = clean(row.get("task"))
        panel_id = clean(row.get("panel_id"))
        label, score, source, notes = final_value(row, completed.get((task, panel_id)))
        ready = bool(label)
        ledger = {
            "task": task,
            "panel_id": panel_id,
            "priority": clean(row.get("priority")),
            "final_label": label,
            "final_score": score,
            "final_source": source,
            "ready_for_manuscript": str(ready),
            "remaining_action": "none" if ready else clean(row.get("remaining_action")) or "missing_final_label",
            "adjudication_notes": notes,
        }
        ledger_rows.append(ledger)
        by_task.setdefault(task, []).append(ledger)

    summary_rows: list[dict[str, str]] = []
    for task, rows in sorted(by_task.items()):
        urgent = [row for row in rows if row["priority"] == "urgent_vlm_disagreement"]
        final_rows = [row for row in rows if row["final_label"]]
        urgent_final = [row for row in urgent if row["final_label"]]
        labels = Counter(row["final_label"] for row in final_rows)
        scores: list[float] = []
        for row in final_rows:
            if row["final_score"]:
                try:
                    scores.append(float(row["final_score"]))
                except ValueError:
                    pass
        if not final_rows:
            status = "no_final_labels_collected"
        elif len(urgent_final) < len(urgent):
            status = "urgent_final_labels_incomplete"
        elif len(final_rows) < len(rows):
            status = "partial_final_labels_collected"
        else:
            status = "ready_for_manuscript_claim_update"
        summary_rows.append(
            {
                "task": task,
                "total_items": str(len(rows)),
                "urgent_items": str(len(urgent)),
                "final_labels": str(len(final_rows)),
                "urgent_final_labels": str(len(urgent_final)),
                "label_counts": ";".join(f"{label}:{count}" for label, count in sorted(labels.items())),
                "mean_final_score": f"{sum(scores) / len(scores):.3f}" if scores else "",
                "completed_agreement_file": str(completed_path.relative_to(ROOT)) if completed_path and completed_path.exists() else "",
                "status": status,
            }
        )
    return ledger_rows, summary_rows


def write_report(summary_rows: list[dict[str, str]]) -> None:
    lines = [
        "# Human Validation Final Label Summary",
        "",
        "This file summarizes final human labels after two-annotator agreement or adjudication. It is allowed to report zero final labels; that state means the manuscript must keep the human-label gate open.",
        "",
        "| Task | Final labels | Urgent final labels | Label counts | Mean score | Status |",
        "|---|---:|---:|---|---:|---|",
    ]
    for row in summary_rows:
        lines.append(
            f"| {row['task']} | {row['final_labels']}/{row['total_items']} | {row['urgent_final_labels']}/{row['urgent_items']} | {row['label_counts'] or 'none'} | {row['mean_final_score'] or ''} | {row['status']} |"
        )
    lines += [
        "",
        "## Manuscript Rule",
        "",
        "Do not replace VLM/CLIP screening caveats with human-supported claims until both task rows have complete urgent final labels and a completed agreement/adjudication file is retained.",
        "",
    ]
    (OUT_DIR / "human_validation_final_label_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--completed-agreement", type=Path, default=DEFAULT_COMPLETED)
    args = parser.parse_args(argv)
    completed = args.completed_agreement if args.completed_agreement.exists() else None
    ledger_rows, summary_rows = build_rows(completed)
    write_csv(
        OUT_DIR / "human_validation_final_label_ledger.csv",
        ledger_rows,
        [
            "task",
            "panel_id",
            "priority",
            "final_label",
            "final_score",
            "final_source",
            "ready_for_manuscript",
            "remaining_action",
            "adjudication_notes",
        ],
    )
    write_csv(
        OUT_DIR / "human_validation_final_label_summary.csv",
        summary_rows,
        [
            "task",
            "total_items",
            "urgent_items",
            "final_labels",
            "urgent_final_labels",
            "label_counts",
            "mean_final_score",
            "completed_agreement_file",
            "status",
        ],
    )
    write_report(summary_rows)
    print(f"Wrote human validation final label summary to {OUT_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
