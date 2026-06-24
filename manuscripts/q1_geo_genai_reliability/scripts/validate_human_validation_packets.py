#!/usr/bin/env python3
"""Validate human-validation packet structure and completed-label values.

By default this checks the prepared blank annotator packets. Optional completed
CSV paths can be passed later to catch missing required labels, invalid rubric
values, score range errors, duplicate panel IDs, or missing artifact links
before the label summarizer is run.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MS_DIR = ROOT / "manuscripts/q1_geo_genai_reliability"
PANEL_DIR = MS_DIR / "submission/human_validation_panels"
OUT_DIR = PANEL_DIR / "preflight"


MAPGEN_REQUIRED = [
    "panel_id",
    "image_path",
    "caption",
    "human_visible_water",
    "human_visible_roads",
    "human_visible_green_area",
    "human_visible_named_label",
    "human_caption_support",
    "human_unsupported_claims",
    "human_omissions",
    "human_notes",
]

CHORO_REQUIRED = [
    "panel_id",
    "review_image_path",
    "kind",
    "human_map_content_visible",
    "human_has_title",
    "human_has_legend_or_colorbar",
    "human_text_readable",
    "human_layout_not_occluded",
    "human_appears_choropleth",
    "human_cartographic_quality",
    "human_verdict",
    "human_main_issue",
    "human_notes",
]


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


def load_rubric() -> dict[str, object]:
    return json.loads((PANEL_DIR / "human_validation_rubric.json").read_text(encoding="utf-8"))


def expected_ids(path: Path) -> set[str]:
    return {row["panel_id"] for row in read_csv(path)}


def validate_schema(path: Path, required_fields: list[str]) -> list[str]:
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames or []
    return [field for field in required_fields if field not in fields]


def validate_packet(
    path: Path,
    task: str,
    required_fields: list[str],
    expected_panel_ids: set[str],
    label_values: set[str],
    feature_values: set[str],
    require_completed: bool,
) -> dict[str, str]:
    rows = read_csv(path)
    missing_schema = validate_schema(path, required_fields)
    panel_ids = [row.get("panel_id", "") for row in rows]
    duplicate_ids = sorted({panel_id for panel_id in panel_ids if panel_ids.count(panel_id) > 1})
    unexpected_ids = sorted(set(panel_ids) - expected_panel_ids)
    missing_ids = sorted(expected_panel_ids - set(panel_ids))
    missing_artifacts = 0
    invalid_values = 0
    incomplete_rows = 0
    score_errors = 0

    for row in rows:
        artifact_field = "image_path" if task == "mapgenerator_caption_fidelity" else "review_image_path"
        if artifact_field in row and not (ROOT / row[artifact_field]).exists():
            missing_artifacts += 1
        if task == "mapgenerator_caption_fidelity":
            feature_fields = [
                "human_visible_water",
                "human_visible_roads",
                "human_visible_green_area",
                "human_visible_named_label",
            ]
            label = nonempty(row.get("human_caption_support"))
            if require_completed and not label:
                incomplete_rows += 1
            if label and label not in label_values:
                invalid_values += 1
            for field in feature_fields:
                value = nonempty(row.get(field))
                if value and value not in feature_values:
                    invalid_values += 1
        else:
            feature_fields = [
                "human_map_content_visible",
                "human_has_title",
                "human_has_legend_or_colorbar",
                "human_text_readable",
                "human_layout_not_occluded",
                "human_appears_choropleth",
            ]
            label = nonempty(row.get("human_verdict"))
            if require_completed and not label:
                incomplete_rows += 1
            if label and label not in label_values:
                invalid_values += 1
            for field in feature_fields:
                value = nonempty(row.get(field))
                if value and value not in feature_values:
                    invalid_values += 1
            score = nonempty(row.get("human_cartographic_quality"))
            if require_completed and not score:
                incomplete_rows += 1
            if score:
                try:
                    score_value = float(score)
                    if score_value < 0.0 or score_value > 1.0:
                        score_errors += 1
                except ValueError:
                    score_errors += 1

    status = "pass"
    if missing_schema or duplicate_ids or unexpected_ids or missing_ids or missing_artifacts or invalid_values or score_errors:
        status = "fail"
    if require_completed and incomplete_rows:
        status = "fail"

    return {
        "file": str(path.relative_to(ROOT)),
        "task": task,
        "mode": "completed" if require_completed else "blank_or_partial",
        "rows": str(len(rows)),
        "expected_rows": str(len(expected_panel_ids)),
        "missing_schema": ";".join(missing_schema),
        "duplicate_panel_ids": ";".join(duplicate_ids),
        "unexpected_panel_ids": ";".join(unexpected_ids),
        "missing_panel_ids": ";".join(missing_ids),
        "missing_artifacts": str(missing_artifacts),
        "invalid_values": str(invalid_values),
        "incomplete_rows": str(incomplete_rows),
        "score_errors": str(score_errors),
        "status": status,
    }


def build_report(rows: list[dict[str, str]]) -> str:
    passed = sum(row["status"] == "pass" for row in rows)
    lines = [
        "# Human Validation Packet Preflight",
        "",
        "This preflight validates annotator packet schemas, panel coverage, local artifact links, and optional completed-label values against the rubric. Blank prepared packets may pass in `blank_or_partial` mode; completed packets must have required labels.",
        "",
        "## Summary",
        "",
        f"- files checked: {len(rows)}",
        f"- passed: {passed}/{len(rows)}",
        "",
        "## Checks",
        "",
        "| File | Task | Mode | Rows | Expected | Missing artifacts | Invalid values | Incomplete rows | Score errors | Status |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['file']}` | {row['task']} | {row['mode']} | {row['rows']} | {row['expected_rows']} | {row['missing_artifacts']} | {row['invalid_values']} | {row['incomplete_rows']} | {row['score_errors']} | {row['status']} |"
        )
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mapgenerator-labels", nargs="*", type=Path, default=[])
    parser.add_argument("--choropleth-labels", nargs="*", type=Path, default=[])
    parser.add_argument("--require-completed", action="store_true")
    args = parser.parse_args(argv)

    rubric = load_rubric()
    mapgen_expected = expected_ids(PANEL_DIR / "mapgenerator_caption_blind_panel.csv")
    choro_expected = expected_ids(PANEL_DIR / "choropleth_cartographic_blind_panel.csv")
    mapgen_labels = set(rubric["mapgenerator_caption_panel"]["caption_support_labels"])
    choro_labels = set(rubric["choropleth_cartographic_panel"]["verdict_labels"])
    feature_values = set(rubric["mapgenerator_caption_panel"]["feature_labels"])

    mapgen_paths = args.mapgenerator_labels or sorted((PANEL_DIR / "annotator_packets").glob("mapgenerator_caption_fidelity_*_completed.csv"))
    choro_paths = args.choropleth_labels or sorted((PANEL_DIR / "annotator_packets").glob("choropleth_cartographic_quality_*_completed.csv"))

    rows: list[dict[str, str]] = []
    for path in mapgen_paths:
        rows.append(
            validate_packet(
                path,
                "mapgenerator_caption_fidelity",
                MAPGEN_REQUIRED,
                mapgen_expected,
                mapgen_labels,
                feature_values,
                args.require_completed,
            )
        )
    for path in choro_paths:
        rows.append(
            validate_packet(
                path,
                "choropleth_cartographic_quality",
                CHORO_REQUIRED,
                choro_expected,
                choro_labels,
                feature_values,
                args.require_completed,
            )
        )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(
        OUT_DIR / "human_validation_packet_preflight.csv",
        rows,
        [
            "file",
            "task",
            "mode",
            "rows",
            "expected_rows",
            "missing_schema",
            "duplicate_panel_ids",
            "unexpected_panel_ids",
            "missing_panel_ids",
            "missing_artifacts",
            "invalid_values",
            "incomplete_rows",
            "score_errors",
            "status",
        ],
    )
    (OUT_DIR / "human_validation_packet_preflight.md").write_text(build_report(rows), encoding="utf-8")
    print(f"Wrote {(OUT_DIR / 'human_validation_packet_preflight.csv').relative_to(ROOT)}")
    print(f"Wrote {(OUT_DIR / 'human_validation_packet_preflight.md').relative_to(ROOT)}")
    if any(row["status"] != "pass" for row in rows):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
