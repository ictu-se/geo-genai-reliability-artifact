#!/usr/bin/env python3
"""Summarize collected human validation labels for caption and cartographic panels.

The script accepts zero or more annotator CSV files. With no completed label
files, it writes an explicit no-label status so the manuscript audit can
distinguish prepared panels from collected evidence.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MS_DIR = ROOT / "manuscripts/q1_geo_genai_reliability"
PANEL_DIR = MS_DIR / "submission/human_validation_panels"
OUT_DIR = PANEL_DIR / "summaries"
PRIORITY_QUEUE = PANEL_DIR / "human_validation_priority_queue.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def nonempty(value: str | None) -> str:
    return (value or "").strip()


def usable_band(label: str) -> str:
    if label in {"usable", "usable_with_minor_issues"}:
        return "usable_or_minor"
    if label in {"weak", "failed"}:
        return "below_usable"
    return label


def cohen_kappa(pairs: list[tuple[str, str]]) -> str:
    if not pairs:
        return ""
    observed = sum(a == b for a, b in pairs) / len(pairs)
    labels = sorted({label for pair in pairs for label in pair})
    left = Counter(a for a, _ in pairs)
    right = Counter(b for _, b in pairs)
    expected = sum((left[label] / len(pairs)) * (right[label] / len(pairs)) for label in labels)
    if expected == 1.0:
        return "1.000" if observed == 1.0 else "0.000"
    return f"{(observed - expected) / (1 - expected):.3f}"


def task_priority_ids(task: str) -> set[str]:
    if not PRIORITY_QUEUE.exists():
        return set()
    return {
        row["panel_id"]
        for row in read_csv(PRIORITY_QUEUE)
        if row.get("task") == task and row.get("priority") == "urgent_vlm_disagreement"
    }


def summarize_labels(
    paths: list[Path],
    task: str,
    label_field: str,
    score_field: str | None = None,
) -> tuple[list[dict[str, str]], dict[str, str]]:
    by_item: dict[str, list[dict[str, str]]] = defaultdict(list)
    for path in paths:
        for row in read_csv(path):
            label = nonempty(row.get(label_field))
            if not label:
                continue
            item = nonempty(row.get("panel_id"))
            if not item:
                continue
            row = dict(row)
            row["_annotator_file"] = path.name
            by_item[item].append(row)

    rows: list[dict[str, str]] = []
    agreement_items = 0
    label_pairs: list[tuple[str, str]] = []
    band_pairs: list[tuple[str, str]] = []
    score_diffs: list[float] = []
    for item, item_rows in sorted(by_item.items()):
        item_rows = sorted(item_rows, key=lambda row: row.get("_annotator_file", ""))
        labels = [nonempty(row.get(label_field)) for row in item_rows]
        counts = Counter(labels)
        majority_label, majority_count = counts.most_common(1)[0]
        agreement = majority_count == len(labels) and len(labels) >= 2
        if agreement:
            agreement_items += 1
        score_values: list[float] = []
        if score_field:
            for row in item_rows:
                value = nonempty(row.get(score_field))
                if value:
                    try:
                        score_values.append(float(value))
                    except ValueError:
                        pass
        if len(labels) >= 2:
            label_pairs.append((labels[0], labels[1]))
            if task == "choropleth_cartographic_quality":
                band_pairs.append((usable_band(labels[0]), usable_band(labels[1])))
        if len(score_values) >= 2:
            score_diffs.append(abs(score_values[0] - score_values[1]))
        rows.append(
            {
                "panel_id": item,
                "annotations": str(len(labels)),
                "labels": ";".join(labels),
                "majority_label": majority_label,
                "majority_count": str(majority_count),
                "full_agreement": str(agreement),
                "mean_score": f"{sum(score_values) / len(score_values):.3f}" if score_values else "",
                "score_abs_diff": f"{score_diffs[-1]:.3f}" if len(score_values) >= 2 else "",
            }
        )

    total_annotations = sum(int(row["annotations"]) for row in rows)
    urgent_ids = task_priority_ids(task)
    urgent_closed = sum(1 for panel_id in urgent_ids if len(by_item.get(panel_id, [])) >= 2)
    summary = {
        "task": task,
        "annotator_files": str(len(paths)),
        "labeled_items": str(len(rows)),
        "total_annotations": str(total_annotations),
        "paired_items": str(len(label_pairs)),
        "items_with_full_agreement": str(agreement_items),
        "exact_agreement_rate": f"{agreement_items / len(label_pairs):.3f}" if label_pairs else "",
        "cohen_style_kappa": cohen_kappa(label_pairs),
        "usable_below_agreement_rate": f"{sum(a == b for a, b in band_pairs) / len(band_pairs):.3f}" if band_pairs else "",
        "mean_abs_score_diff": f"{sum(score_diffs) / len(score_diffs):.3f}" if score_diffs else "",
        "urgent_items": str(len(urgent_ids)),
        "urgent_items_with_two_labels": str(urgent_closed),
        "urgent_closure_rate": f"{urgent_closed / len(urgent_ids):.3f}" if urgent_ids else "",
        "status": "labels_collected" if total_annotations else "no_labels_collected",
    }
    return rows, summary


def write_metric_summary(mapgen_summary: dict[str, str], choro_summary: dict[str, str]) -> None:
    fields = [
        "task",
        "annotator_files",
        "labeled_items",
        "total_annotations",
        "paired_items",
        "items_with_full_agreement",
        "exact_agreement_rate",
        "cohen_style_kappa",
        "usable_below_agreement_rate",
        "mean_abs_score_diff",
        "urgent_items",
        "urgent_items_with_two_labels",
        "urgent_closure_rate",
        "status",
    ]
    write_csv(OUT_DIR / "human_validation_metric_summary.csv", [mapgen_summary, choro_summary], fields)


def write_status(mapgen_summary: dict[str, str], choro_summary: dict[str, str]) -> None:
    lines = [
        "# Human Validation Label Summary",
        "",
        "This file is generated from completed annotator CSVs. Prepared panels alone do not count as collected human evidence.",
        "",
        "## MapGenerator Caption Labels",
        "",
    ]
    lines.extend(f"- {key}: {value}" for key, value in mapgen_summary.items())
    lines += ["", "## Choropleth Cartographic Labels", ""]
    lines.extend(f"- {key}: {value}" for key, value in choro_summary.items())
    lines.append("")
    (OUT_DIR / "human_validation_label_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mapgenerator-labels", nargs="*", type=Path, default=[])
    parser.add_argument("--choropleth-labels", nargs="*", type=Path, default=[])
    args = parser.parse_args(argv)

    mapgen_rows, mapgen_summary = summarize_labels(
        args.mapgenerator_labels,
        "mapgenerator_caption_fidelity",
        "human_caption_support",
    )
    choro_rows, choro_summary = summarize_labels(
        args.choropleth_labels,
        "choropleth_cartographic_quality",
        "human_verdict",
        "human_cartographic_quality",
    )

    write_csv(
        OUT_DIR / "mapgenerator_human_label_summary.csv",
        mapgen_rows,
        ["panel_id", "annotations", "labels", "majority_label", "majority_count", "full_agreement", "mean_score", "score_abs_diff"],
    )
    write_csv(
        OUT_DIR / "choropleth_human_label_summary.csv",
        choro_rows,
        ["panel_id", "annotations", "labels", "majority_label", "majority_count", "full_agreement", "mean_score", "score_abs_diff"],
    )
    write_metric_summary(mapgen_summary, choro_summary)
    write_status(mapgen_summary, choro_summary)
    print(f"Wrote human validation summaries to {OUT_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
