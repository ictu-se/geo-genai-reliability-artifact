#!/usr/bin/env python3
"""Build VLM adjudication ledgers and human-priority queues.

The outputs summarize where independent VLM reviewers agree, where they differ,
and which cases should be prioritized for human adjudication. They are not
human labels and should not be treated as ground truth.
"""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MS_DIR = ROOT / "manuscripts/q1_geo_genai_reliability"
PANEL_DIR = MS_DIR / "submission/human_validation_panels"
OUT_DIR = PANEL_DIR / "summaries"

MAPGEN_PANEL = PANEL_DIR / "mapgenerator_caption_human_panel.csv"
CHORO_PANEL = PANEL_DIR / "choropleth_cartographic_human_panel.csv"
MAPGEN_A = ROOT / "experiments/02_mapgenerator_image_text_audit/outputs/mapgenerator_vlm_caption_review_granite3.2-vision_latest.csv"
MAPGEN_B = ROOT / "experiments/02_mapgenerator_image_text_audit/outputs/mapgenerator_vlm_caption_review_qwen2.5vl_3b.csv"
CHORO_A = ROOT / "experiments/05_choropleth_reliability_benchmark/outputs/scores/choropleth_vlm_cartographic_review_granite3.2-vision_latest.csv"
CHORO_B = ROOT / "experiments/05_choropleth_reliability_benchmark/outputs/scores/choropleth_vlm_cartographic_review_qwen2.5vl_3b.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def truthy(value: str) -> bool:
    return value.strip().lower() == "true"


def score(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def caption_coarse(verdict: str) -> str:
    return "supported" if verdict == "supported" else "below_supported"


def choropleth_coarse(verdict: str) -> str:
    return "usable_or_minor" if verdict in {"usable", "usable_with_minor_issues"} else "below_usable"


def priority_bucket(exact_agree: bool, coarse_agree: bool, score_gap: float, component_agreement: str, already_stable_group: bool = False) -> str:
    if already_stable_group:
        return "low_priority_stable_positive_control"
    if not coarse_agree:
        return "urgent_human_adjudication"
    if not exact_agree or score_gap >= 0.25:
        return "high_human_priority"
    if component_agreement.startswith("all"):
        return "low_priority_stable"
    return "medium_priority_component_check"


def build_mapgenerator_ledger() -> list[dict[str, str]]:
    panel = {(row["split"], row["image"]): row for row in read_csv(MAPGEN_PANEL)}
    a = {(row["split"], row["image"]): row for row in read_csv(MAPGEN_A)}
    b = {(row["split"], row["image"]): row for row in read_csv(MAPGEN_B)}
    rows: list[dict[str, str]] = []
    feature_fields = [
        "vlm_visible_water",
        "vlm_visible_roads",
        "vlm_visible_green_area",
        "vlm_visible_named_label",
    ]
    for key in sorted(set(a) & set(b)):
        row_a = a[key]
        row_b = b[key]
        panel_row = panel.get(key, {})
        exact = row_a["vlm_verdict"] == row_b["vlm_verdict"]
        coarse = caption_coarse(row_a["vlm_verdict"]) == caption_coarse(row_b["vlm_verdict"])
        compared = [
            field
            for field in feature_fields
            if row_a.get(field, "") not in {"", "None"} and row_b.get(field, "") not in {"", "None"}
        ]
        agreed = sum(row_a.get(field) == row_b.get(field) for field in compared)
        component_agreement = f"{agreed}/{len(compared)}" if compared else "0/0"
        gap = abs(score(row_a["vlm_alignment_score"]) - score(row_b["vlm_alignment_score"]))
        rows.append(
            {
                "panel_id": panel_row.get("panel_id", ""),
                "split": key[0],
                "image": key[1],
                "proxy_severity": panel_row.get("proxy_severity", row_a.get("review_severity", "")),
                "proxy_score": panel_row.get("proxy_fidelity_score", row_a.get("proxy_fidelity_score", "")),
                "granite_verdict": row_a["vlm_verdict"],
                "qwen_verdict": row_b["vlm_verdict"],
                "exact_verdict_agreement": str(exact),
                "coarse_supported_agreement": str(coarse),
                "granite_score": row_a["vlm_alignment_score"],
                "qwen_score": row_b["vlm_alignment_score"],
                "score_gap_abs": f"{gap:.3f}",
                "feature_agreement": component_agreement,
                "human_priority": priority_bucket(exact, coarse, gap, "all" if agreed == len(compared) and compared else component_agreement),
                "adjudication_note": "VLMs agree on visible features but differ on semantic support threshold" if not exact and agreed >= max(1, len(compared) - 1) else "",
            }
        )
    return rows


def build_choropleth_ledger() -> list[dict[str, str]]:
    panel = {row["artifact_path"]: row for row in read_csv(CHORO_PANEL)}
    a = {row["artifact_path"]: row for row in read_csv(CHORO_A)}
    b = {row["artifact_path"]: row for row in read_csv(CHORO_B)}
    rows: list[dict[str, str]] = []
    component_fields = [
        "vlm_map_content_visible",
        "vlm_has_title",
        "vlm_has_legend_or_colorbar",
        "vlm_text_readable",
        "vlm_layout_not_occluded",
        "vlm_appears_choropleth",
    ]
    for artifact_path in sorted(set(a) & set(b)):
        row_a = a[artifact_path]
        row_b = b[artifact_path]
        panel_row = panel.get(artifact_path, {})
        exact = row_a["vlm_verdict"] == row_b["vlm_verdict"]
        coarse = choropleth_coarse(row_a["vlm_verdict"]) == choropleth_coarse(row_b["vlm_verdict"])
        compared = [
            field
            for field in component_fields
            if row_a.get(field, "") not in {"", "None"} and row_b.get(field, "") not in {"", "None"}
        ]
        agreed = sum(row_a.get(field) == row_b.get(field) for field in compared)
        gap = abs(score(row_a["vlm_cartographic_quality_score"]) - score(row_b["vlm_cartographic_quality_score"]))
        stable_positive_control = row_a.get("source_group") == "validator_repair_reference" and exact and coarse
        rows.append(
            {
                "panel_id": panel_row.get("panel_id", ""),
                "artifact": row_a["artifact"],
                "source_group": row_a["source_group"],
                "source": row_a["source"],
                "kind": row_a["kind"],
                "artifact_path": artifact_path,
                "granite_verdict": row_a["vlm_verdict"],
                "qwen_verdict": row_b["vlm_verdict"],
                "exact_verdict_agreement": str(exact),
                "coarse_usable_agreement": str(coarse),
                "granite_score": row_a["vlm_cartographic_quality_score"],
                "qwen_score": row_b["vlm_cartographic_quality_score"],
                "score_gap_abs": f"{gap:.3f}",
                "component_agreement": f"{agreed}/{len(compared)}" if compared else "0/0",
                "human_priority": priority_bucket(exact, coarse, gap, f"{agreed}/{len(compared)}", stable_positive_control),
                "adjudication_note": "stable positive-control artifact group" if stable_positive_control else "",
            }
        )
    return rows


def summarize(task: str, rows: list[dict[str, str]], coarse_field: str) -> dict[str, str]:
    n = len(rows)
    exact = sum(truthy(row["exact_verdict_agreement"]) for row in rows)
    coarse = sum(truthy(row[coarse_field]) for row in rows)
    priorities: dict[str, int] = {}
    for row in rows:
        priorities[row["human_priority"]] = priorities.get(row["human_priority"], 0) + 1
    mean_gap = sum(score(row["score_gap_abs"]) for row in rows) / n if n else 0.0
    return {
        "Task": task,
        "Items": str(n),
        "Exact VLM agreement": f"{exact}/{n}",
        "Coarse VLM agreement": f"{coarse}/{n}",
        "Urgent human adjudication": str(priorities.get("urgent_human_adjudication", 0)),
        "High human priority": str(priorities.get("high_human_priority", 0)),
        "Medium priority": str(priorities.get("medium_priority_component_check", 0)),
        "Low priority/stable": str(priorities.get("low_priority_stable", 0) + priorities.get("low_priority_stable_positive_control", 0)),
        "Mean score gap": f"{mean_gap:.3f}",
        "Interpretation": "VLM threshold instability; use as triage only" if task.startswith("MapGenerator") else "more stable for rendered-map usability than caption semantics",
    }


def write_report(summary_rows: list[dict[str, str]]) -> None:
    lines = [
        "# Evaluator Adjudication Summary",
        "",
        "Generated from paired local VLM reviews and human-validation panels. These outputs prioritize human adjudication; they do not convert VLM agreement into ground truth.",
        "",
        "| Task | Items | Exact VLM agreement | Coarse VLM agreement | Urgent human adjudication | High human priority | Low priority/stable | Mean score gap |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary_rows:
        lines.append(
            f"| {row['Task']} | {row['Items']} | {row['Exact VLM agreement']} | {row['Coarse VLM agreement']} | {row['Urgent human adjudication']} | {row['High human priority']} | {row['Low priority/stable']} | {row['Mean score gap']} |"
        )
    lines += [
        "",
        "## Interpretation",
        "",
        "- MapGenerator caption cases show high low-level feature agreement but weak semantic-support agreement, so they remain high priority for human adjudication.",
        "- Choropleth rendered artifacts show stronger coarse agreement, especially for the validator/reference positive-control group, but score scales differ substantially.",
        "- Final Q1 claims should report these ledgers as evaluator-sensitivity evidence and keep human labels as a remaining validation gate until collected.",
        "",
    ]
    (OUT_DIR / "evaluator_adjudication_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    mapgen_rows = build_mapgenerator_ledger()
    choro_rows = build_choropleth_ledger()
    summary_rows = [
        summarize("MapGenerator caption fidelity", mapgen_rows, "coarse_supported_agreement"),
        summarize("Choropleth cartographic quality", choro_rows, "coarse_usable_agreement"),
    ]
    write_csv(OUT_DIR / "mapgenerator_evaluator_adjudication_ledger.csv", mapgen_rows)
    write_csv(OUT_DIR / "choropleth_evaluator_adjudication_ledger.csv", choro_rows)
    write_csv(OUT_DIR / "evaluator_adjudication_summary.csv", summary_rows)
    write_report(summary_rows)
    print(f"Wrote evaluator adjudication summaries to {OUT_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
