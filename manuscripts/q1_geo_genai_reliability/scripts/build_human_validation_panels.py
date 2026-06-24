#!/usr/bin/env python3
"""Build human/adjudication annotation panels for the remaining Q1 validation gate."""

from __future__ import annotations

import csv
import html
import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MS_DIR = ROOT / "manuscripts/q1_geo_genai_reliability"
OUT_DIR = MS_DIR / "submission/human_validation_panels"
PACKET_DIR = OUT_DIR / "annotator_packets"

MAPGEN_PROXY = ROOT / "experiments/02_mapgenerator_image_text_audit/outputs/mapgenerator_proxy_caption_review.csv"
MAPGEN_VLM_A = ROOT / "experiments/02_mapgenerator_image_text_audit/outputs/mapgenerator_vlm_caption_review_granite3.2-vision_latest.csv"
MAPGEN_VLM_B = ROOT / "experiments/02_mapgenerator_image_text_audit/outputs/mapgenerator_vlm_caption_review_qwen2.5vl_3b.csv"

CHORO_VLM_A = ROOT / "experiments/05_choropleth_reliability_benchmark/outputs/scores/choropleth_vlm_cartographic_review_granite3.2-vision_latest.csv"
CHORO_VLM_B = ROOT / "experiments/05_choropleth_reliability_benchmark/outputs/scores/choropleth_vlm_cartographic_review_qwen2.5vl_3b.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, data: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def html_rel(path_text: str) -> str:
    path = ROOT / path_text
    return Path(os.path.relpath(path, OUT_DIR)).as_posix()


def artifact_exists(path_text: str) -> str:
    return str((ROOT / path_text).exists())


def mapgen_image_path(split: str, image: str) -> str:
    return str(Path("data/raw/MapGenerator") / split / "Images" / image)


def build_mapgenerator_panel() -> list[dict[str, str]]:
    proxy_rows = {(row["split"], row["image"]): row for row in read_csv(MAPGEN_PROXY)}
    vlm_a = {(row["split"], row["image"]): row for row in read_csv(MAPGEN_VLM_A)}
    vlm_b = {(row["split"], row["image"]): row for row in read_csv(MAPGEN_VLM_B)}
    common = sorted(set(vlm_a) & set(vlm_b))

    rows: list[dict[str, str]] = []
    for idx, key in enumerate(common, start=1):
        split, image = key
        proxy = proxy_rows[key]
        a = vlm_a[key]
        b = vlm_b[key]
        rows.append(
            {
                "panel_id": f"MG-{idx:03d}",
                "split": split,
                "image": image,
                "image_path": mapgen_image_path(split, image),
                "caption": proxy["description"],
                "proxy_severity": proxy["review_severity"],
                "proxy_fidelity_score": proxy["proxy_fidelity_score"],
                "proxy_issues": proxy["proxy_issues"],
                "granite_verdict": a.get("vlm_verdict", ""),
                "granite_score": a.get("vlm_alignment_score", ""),
                "qwen_verdict": b.get("vlm_verdict", ""),
                "qwen_score": b.get("vlm_alignment_score", ""),
                "vlm_disagreement": str(a.get("vlm_verdict", "") != b.get("vlm_verdict", "")),
                "human_visible_water": "",
                "human_visible_roads": "",
                "human_visible_green_area": "",
                "human_visible_named_label": "",
                "human_caption_support": "",
                "human_unsupported_claims": "",
                "human_omissions": "",
                "human_notes": "",
            }
        )
    rows.sort(
        key=lambda row: (
            row["vlm_disagreement"] != "True",
            {"high": 0, "medium": 1, "low": 2}.get(row["proxy_severity"], 3),
            float(row["proxy_fidelity_score"]),
            row["panel_id"],
        )
    )
    return rows


def build_choropleth_panel() -> list[dict[str, str]]:
    vlm_a = {row["artifact_path"]: row for row in read_csv(CHORO_VLM_A)}
    vlm_b = {row["artifact_path"]: row for row in read_csv(CHORO_VLM_B)}
    common = sorted(set(vlm_a) & set(vlm_b))

    rows: list[dict[str, str]] = []
    for idx, artifact_path in enumerate(common, start=1):
        a = vlm_a[artifact_path]
        b = vlm_b[artifact_path]
        rows.append(
            {
                "panel_id": f"CH-{idx:03d}",
                "artifact": a["artifact"],
                "source_group": a["source_group"],
                "source": a["source"],
                "kind": a["kind"],
                "review_image_path": a["review_image_path"],
                "artifact_path": artifact_path,
                "qa_pass": a["qa_pass"],
                "granite_verdict": a.get("vlm_verdict", ""),
                "granite_score": a.get("vlm_cartographic_quality_score", ""),
                "qwen_verdict": b.get("vlm_verdict", ""),
                "qwen_score": b.get("vlm_cartographic_quality_score", ""),
                "vlm_disagreement": str(a.get("vlm_verdict", "") != b.get("vlm_verdict", "")),
                "human_map_content_visible": "",
                "human_has_title": "",
                "human_has_legend_or_colorbar": "",
                "human_text_readable": "",
                "human_layout_not_occluded": "",
                "human_appears_choropleth": "",
                "human_cartographic_quality": "",
                "human_verdict": "",
                "human_main_issue": "",
                "human_notes": "",
            }
        )
    rows.sort(
        key=lambda row: (
            row["vlm_disagreement"] != "True",
            row["source_group"],
            row["kind"],
            row["panel_id"],
        )
    )
    return rows


def blind_mapgenerator_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    fields = [
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
    return [{field: row.get(field, "") for field in fields} for row in rows]


def blind_choropleth_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    fields = [
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
    return [{field: row.get(field, "") for field in fields} for row in rows]


def build_rubric() -> dict[str, object]:
    return {
        "mapgenerator_caption_panel": {
            "task": "Judge whether the caption is supported by the visible map image.",
            "feature_labels": ["yes", "no", "unclear"],
            "caption_support_labels": ["supported", "partly_supported", "unsupported", "unclear"],
            "caption_support_definitions": {
                "supported": "All central caption claims are visible or directly inferable from the map.",
                "partly_supported": "Some central claims are supported, but at least one important claim is missing, ambiguous, or too strong.",
                "unsupported": "The caption contradicts the image or most central claims are not visible.",
                "unclear": "The image/caption cannot be judged confidently.",
            },
            "minimum_independent_annotators": 2,
        },
        "choropleth_cartographic_panel": {
            "task": "Judge whether the rendered artifact is a usable choropleth-style cartographic artifact.",
            "component_labels": ["yes", "no", "unclear"],
            "quality_score_range": [0.0, 1.0],
            "verdict_labels": ["usable", "usable_with_minor_issues", "weak", "failed", "unclear"],
            "verdict_definitions": {
                "usable": "Map content, thematic encoding, title/context, legend/colorbar, and layout are all acceptable.",
                "usable_with_minor_issues": "Core map content is usable, with minor missing or imperfect cartographic elements.",
                "weak": "The artifact is visible but has substantial cartographic omissions or layout problems.",
                "failed": "The artifact is blank, not a map, not inspectable, or lacks core choropleth content.",
                "unclear": "The artifact cannot be judged confidently.",
            },
            "minimum_independent_annotators": 2,
        },
        "adjudication": {
            "primary_rule": "Use two independent human annotations where possible; adjudicate disagreements with a designated expert or third annotator.",
            "reporting_rule": "Report human agreement separately from VLM agreement and do not relabel VLM outputs as ground truth.",
        },
    }


def build_protocol(mapgen_rows: list[dict[str, str]], choro_rows: list[dict[str, str]]) -> str:
    return "\n".join(
        [
            "# Human Validation Panel Protocol",
            "",
            "These panels are designed to close the remaining evaluator-validity gate without changing the main experimental pipeline.",
            "",
            "## Files",
            "",
            f"- `mapgenerator_caption_human_panel.csv`: {len(mapgen_rows)} paired image-caption cases.",
            f"- `choropleth_cartographic_human_panel.csv`: {len(choro_rows)} screenshot-passing choropleth artifacts.",
            "- `mapgenerator_caption_blind_panel.csv`: blind annotator-facing caption panel.",
            "- `choropleth_cartographic_blind_panel.csv`: blind annotator-facing cartographic panel.",
            "- `human_validation_rubric.json`: machine-readable labels and adjudication rules.",
            "",
            "## MapGenerator Caption Panel",
            "",
            "Annotators should open `image_path`, read `caption`, and fill the `human_*` columns only. Use `mapgenerator_caption_blind_panel.csv` for blind annotation; use the full panel only for later adjudication.",
            "",
            "Recommended labels:",
            "",
            "- `human_visible_water`, `human_visible_roads`, `human_visible_green_area`, `human_visible_named_label`: `yes`, `no`, or `unclear`.",
            "- `human_caption_support`: `supported`, `partly_supported`, `unsupported`, or `unclear`.",
            "- `human_unsupported_claims` and `human_omissions`: short free text.",
            "",
            "## Choropleth Cartographic Panel",
            "",
            "Annotators should open `review_image_path` and fill the `human_*` columns only. Use `choropleth_cartographic_blind_panel.csv` for blind annotation; use the full panel only for later adjudication.",
            "",
            "Recommended labels:",
            "",
            "- Binary visual components: `yes`, `no`, or `unclear`.",
            "- `human_cartographic_quality`: numeric score from 0.0 to 1.0.",
            "- `human_verdict`: `usable`, `usable_with_minor_issues`, `weak`, `failed`, or `unclear`.",
            "- `human_main_issue`: one concise reason for the verdict.",
            "",
            "## Adjudication Rule",
            "",
            "For Q1-strengthened claims, report human agreement separately from VLM agreement. Treat a case as supported only when at least two independent human annotations agree or a designated expert adjudicates the disagreement.",
            "",
        ]
    )


def mapgen_priority(row: dict[str, str]) -> str:
    if row.get("vlm_disagreement") == "True":
        return "urgent_vlm_disagreement"
    if row.get("proxy_severity") == "high":
        return "high_proxy_severity"
    try:
        score = float(row.get("proxy_fidelity_score", "1"))
    except ValueError:
        score = 1.0
    if score < 0.6:
        return "high_low_proxy_score"
    return "standard_coverage"


def choro_priority(row: dict[str, str]) -> str:
    if row.get("vlm_disagreement") == "True":
        return "urgent_vlm_disagreement"
    if row.get("source_group") == "validator_repair_reference":
        return "positive_control_coverage"
    if row.get("source_group") == "reference":
        return "reference_control_coverage"
    return "generated_artifact_coverage"


def build_priority_queue(mapgen_rows: list[dict[str, str]], choro_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for row in mapgen_rows:
        rows.append(
            {
                "task": "mapgenerator_caption_fidelity",
                "panel_id": row["panel_id"],
                "priority": mapgen_priority(row),
                "primary_artifact": row["image_path"],
                "context": row["caption"],
                "vlm_disagreement": row["vlm_disagreement"],
                "control_group": "none",
                "recommended_resolution": "two independent annotators; expert adjudication if labels disagree",
            }
        )
    for row in choro_rows:
        rows.append(
            {
                "task": "choropleth_cartographic_quality",
                "panel_id": row["panel_id"],
                "priority": choro_priority(row),
                "primary_artifact": row["review_image_path"],
                "context": row["kind"],
                "vlm_disagreement": row["vlm_disagreement"],
                "control_group": row["source_group"],
                "recommended_resolution": "two independent annotators; expert adjudication if verdict or score band disagrees",
            }
        )
    priority_order = {
        "urgent_vlm_disagreement": 0,
        "high_proxy_severity": 1,
        "high_low_proxy_score": 2,
        "generated_artifact_coverage": 3,
        "positive_control_coverage": 4,
        "reference_control_coverage": 5,
        "standard_coverage": 6,
    }
    rows.sort(key=lambda row: (priority_order.get(row["priority"], 9), row["task"], row["panel_id"]))
    return rows


def build_assignment_rows(priority_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for index, row in enumerate(priority_rows, start=1):
        batch_id = f"B{((index - 1) // 10) + 1:02d}"
        for annotator_slot in ["A", "B"]:
            rows.append(
                {
                    "batch_id": batch_id,
                    "annotator_slot": annotator_slot,
                    "task": row["task"],
                    "panel_id": row["panel_id"],
                    "priority": row["priority"],
                    "input_artifact": row["primary_artifact"],
                    "input_context": row["context"],
                    "blank_form": "mapgenerator_caption_blind_panel.csv"
                    if row["task"] == "mapgenerator_caption_fidelity"
                    else "choropleth_cartographic_blind_panel.csv",
                    "expected_output_file": f"{row['task']}_{annotator_slot}_completed.csv",
                    "status": "unassigned",
                }
            )
    return rows


def build_agreement_template(priority_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for row in priority_rows:
        rows.append(
            {
                "task": row["task"],
                "panel_id": row["panel_id"],
                "priority": row["priority"],
                "annotator_a_label": "",
                "annotator_b_label": "",
                "annotator_a_score": "",
                "annotator_b_score": "",
                "agreement_status": "",
                "adjudicator_label": "",
                "adjudicator_score": "",
                "final_label": "",
                "final_score": "",
                "adjudication_notes": "",
            }
        )
    return rows


def build_acceptance_criteria() -> list[dict[str, str]]:
    return [
        {
            "task": "mapgenerator_caption_fidelity",
            "criterion": "minimum independent labels",
            "threshold": "2 annotations per panel item",
            "evidence_file": "human_validation_assignment_sheet.csv; completed annotator CSVs",
            "action_if_not_met": "Keep manuscript wording at VLM/CLIP screening level; do not call findings human validated.",
        },
        {
            "task": "mapgenerator_caption_fidelity",
            "criterion": "primary agreement metric",
            "threshold": "Report exact agreement and Cohen-style chance-corrected agreement for human_caption_support when labels are complete.",
            "evidence_file": "mapgenerator_human_label_summary.csv; human_validation_agreement_template.csv",
            "action_if_not_met": "Report disagreement rate and adjudication queue instead of a single consensus rate.",
        },
        {
            "task": "mapgenerator_caption_fidelity",
            "criterion": "urgent disagreement closure",
            "threshold": "All urgent_vlm_disagreement items receive two human labels or expert adjudication.",
            "evidence_file": "human_validation_priority_queue.csv; human_validation_agreement_template.csv",
            "action_if_not_met": "Retain urgent-adjudication language in limitations and do not strengthen RQ2 claim.",
        },
        {
            "task": "choropleth_cartographic_quality",
            "criterion": "minimum independent labels",
            "threshold": "2 annotations per panel item",
            "evidence_file": "human_validation_assignment_sheet.csv; completed annotator CSVs",
            "action_if_not_met": "Keep manuscript wording at calibrated VLM consensus level; do not call findings human validated.",
        },
        {
            "task": "choropleth_cartographic_quality",
            "criterion": "primary agreement metric",
            "threshold": "Report exact verdict agreement, usable/below agreement, and mean absolute score difference for human_cartographic_quality.",
            "evidence_file": "choropleth_human_label_summary.csv; human_validation_agreement_template.csv",
            "action_if_not_met": "Report score dispersion and adjudication queue; avoid binary pass/fail consensus claims.",
        },
        {
            "task": "choropleth_cartographic_quality",
            "criterion": "control coverage",
            "threshold": "Include generated, repair, validator/reference, and deterministic-reference artifacts.",
            "evidence_file": "choropleth_cartographic_human_panel.csv; human_validation_priority_queue.csv",
            "action_if_not_met": "Do not compare human judgments across source groups.",
        },
        {
            "task": "cross_task_reporting",
            "criterion": "separation from VLM evidence",
            "threshold": "Human agreement, VLM agreement, and calibrated multi-judge consensus are reported as separate evidence layers.",
            "evidence_file": "human_validation_execution_plan.md; claim_evidence_crosswalk.md",
            "action_if_not_met": "Keep evaluator-validity caveat in abstract, discussion, and limitations.",
        },
    ]


def build_file_contract() -> list[dict[str, str]]:
    return [
        {
            "file": "mapgenerator_caption_blind_panel.csv",
            "recipient": "caption annotators",
            "editable_columns": "human_visible_water; human_visible_roads; human_visible_green_area; human_visible_named_label; human_caption_support; human_unsupported_claims; human_omissions; human_notes",
            "locked_columns": "panel_id; image_path; caption",
            "expected_return_name": "mapgenerator_caption_fidelity_A_completed.csv or mapgenerator_caption_fidelity_B_completed.csv",
        },
        {
            "file": "choropleth_cartographic_blind_panel.csv",
            "recipient": "cartographic-quality annotators",
            "editable_columns": "human_map_content_visible; human_has_title; human_has_legend_or_colorbar; human_text_readable; human_layout_not_occluded; human_appears_choropleth; human_cartographic_quality; human_verdict; human_main_issue; human_notes",
            "locked_columns": "panel_id; review_image_path; kind",
            "expected_return_name": "choropleth_cartographic_quality_A_completed.csv or choropleth_cartographic_quality_B_completed.csv",
        },
        {
            "file": "human_validation_agreement_template.csv",
            "recipient": "adjudicator",
            "editable_columns": "annotator_a_label; annotator_b_label; annotator_a_score; annotator_b_score; agreement_status; adjudicator_label; adjudicator_score; final_label; final_score; adjudication_notes",
            "locked_columns": "task; panel_id; priority",
            "expected_return_name": "human_validation_agreement_completed.csv",
        },
    ]


def filter_by_assignment(
    rows: list[dict[str, str]],
    assignment_rows: list[dict[str, str]],
    task: str,
    annotator_slot: str,
) -> list[dict[str, str]]:
    selected = {
        row["panel_id"]
        for row in assignment_rows
        if row["task"] == task and row["annotator_slot"] == annotator_slot
    }
    return [row for row in rows if row["panel_id"] in selected]


def build_slot_assignment_rows(
    assignment_rows: list[dict[str, str]],
    annotator_slot: str,
) -> list[dict[str, str]]:
    return [row for row in assignment_rows if row["annotator_slot"] == annotator_slot]


def build_annotator_packet_manifest(
    mapgen_rows: list[dict[str, str]],
    choro_rows: list[dict[str, str]],
    assignment_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for annotator_slot in ["A", "B"]:
        slot_assignments = build_slot_assignment_rows(assignment_rows, annotator_slot)
        rows.append(
            {
                "packet_file": f"annotator_{annotator_slot}_assignment_sheet.csv",
                "annotator_slot": annotator_slot,
                "task": "mixed_assignment_sheet",
                "rows": str(len(slot_assignments)),
                "editable_columns": "status",
                "return_as": f"annotator_{annotator_slot}_assignment_sheet_completed.csv",
                "summarizer_argument": "not used directly",
            }
        )
        for task, task_rows, output_file, summarizer_arg in [
            (
                "mapgenerator_caption_fidelity",
                mapgen_rows,
                f"mapgenerator_caption_fidelity_{annotator_slot}_completed.csv",
                "--mapgenerator-labels",
            ),
            (
                "choropleth_cartographic_quality",
                choro_rows,
                f"choropleth_cartographic_quality_{annotator_slot}_completed.csv",
                "--choropleth-labels",
            ),
        ]:
            packet_rows = filter_by_assignment(task_rows, assignment_rows, task, annotator_slot)
            rows.append(
                {
                    "packet_file": output_file,
                    "annotator_slot": annotator_slot,
                    "task": task,
                    "rows": str(len(packet_rows)),
                    "editable_columns": "human_*",
                    "return_as": output_file,
                    "summarizer_argument": summarizer_arg,
                }
            )
    return rows


def write_annotator_packets(
    blind_mapgen: list[dict[str, str]],
    blind_choro: list[dict[str, str]],
    assignment_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    PACKET_DIR.mkdir(parents=True, exist_ok=True)
    for old in PACKET_DIR.glob("*.csv"):
        old.unlink()
    for annotator_slot in ["A", "B"]:
        slot_assignments = build_slot_assignment_rows(assignment_rows, annotator_slot)
        write_csv(
            PACKET_DIR / f"annotator_{annotator_slot}_assignment_sheet.csv",
            slot_assignments,
            list(slot_assignments[0].keys()) if slot_assignments else [],
        )
        mapgen_packet = filter_by_assignment(
            blind_mapgen,
            assignment_rows,
            "mapgenerator_caption_fidelity",
            annotator_slot,
        )
        write_csv(
            PACKET_DIR / f"mapgenerator_caption_fidelity_{annotator_slot}_completed.csv",
            mapgen_packet,
            list(mapgen_packet[0].keys()) if mapgen_packet else [],
        )
        choro_packet = filter_by_assignment(
            blind_choro,
            assignment_rows,
            "choropleth_cartographic_quality",
            annotator_slot,
        )
        write_csv(
            PACKET_DIR / f"choropleth_cartographic_quality_{annotator_slot}_completed.csv",
            choro_packet,
            list(choro_packet[0].keys()) if choro_packet else [],
        )
    return build_annotator_packet_manifest(blind_mapgen, blind_choro, assignment_rows)


def build_gallery_index(mapgen_rows: list[dict[str, str]], choro_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for row in mapgen_rows:
        rows.append(
            {
                "task": "mapgenerator_caption_fidelity",
                "panel_id": row["panel_id"],
                "gallery_file": "mapgenerator_caption_gallery.html",
                "html_anchor": row["panel_id"],
                "artifact_path": row["image_path"],
                "artifact_exists": artifact_exists(row["image_path"]),
                "context_field": "caption",
                "label_columns": "human_visible_water; human_visible_roads; human_visible_green_area; human_visible_named_label; human_caption_support; human_unsupported_claims; human_omissions; human_notes",
            }
        )
    for row in choro_rows:
        rows.append(
            {
                "task": "choropleth_cartographic_quality",
                "panel_id": row["panel_id"],
                "gallery_file": "choropleth_cartographic_gallery.html",
                "html_anchor": row["panel_id"],
                "artifact_path": row["review_image_path"],
                "artifact_exists": artifact_exists(row["review_image_path"]),
                "context_field": "kind",
                "label_columns": "human_map_content_visible; human_has_title; human_has_legend_or_colorbar; human_text_readable; human_layout_not_occluded; human_appears_choropleth; human_cartographic_quality; human_verdict; human_main_issue; human_notes",
            }
        )
    return rows


def gallery_style() -> str:
    return """
body { font-family: Arial, sans-serif; margin: 24px; color: #1f2933; }
h1 { font-size: 24px; margin-bottom: 4px; }
.note { max-width: 980px; color: #4b5563; line-height: 1.45; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 18px; margin-top: 22px; }
.item { border: 1px solid #d7dde5; border-radius: 8px; padding: 12px; page-break-inside: avoid; background: #fff; }
.meta { font-size: 13px; color: #52606d; margin-bottom: 8px; }
.panel { font-weight: 700; color: #0f4c81; }
img { max-width: 100%; height: auto; border: 1px solid #e5e7eb; background: #f8fafc; }
.caption { font-size: 13px; line-height: 1.4; margin-top: 10px; }
.fields { font-size: 12px; color: #52606d; margin-top: 10px; }
.missing { color: #b42318; font-weight: 700; }
"""


def build_mapgenerator_gallery(rows: list[dict[str, str]]) -> str:
    parts = [
        "<!doctype html>",
        "<html><head><meta charset=\"utf-8\"><title>MapGenerator Caption Human Validation Gallery</title>",
        f"<style>{gallery_style()}</style></head><body>",
        "<h1>MapGenerator Caption Human Validation Gallery</h1>",
        "<p class=\"note\">Blind review gallery for caption-fidelity annotation. Use this visual page together with <code>mapgenerator_caption_blind_panel.csv</code>. Fill only the <code>human_*</code> columns in the CSV; do not infer hidden VLM/proxy labels.</p>",
        "<div class=\"grid\">",
    ]
    for row in rows:
        artifact = row["image_path"]
        exists = (ROOT / artifact).exists()
        parts += [
            f"<section class=\"item\" id=\"{html.escape(row['panel_id'])}\">",
            f"<div class=\"meta\"><span class=\"panel\">{html.escape(row['panel_id'])}</span> &middot; {html.escape(artifact)}</div>",
        ]
        if exists:
            parts.append(f"<img src=\"{html.escape(html_rel(artifact))}\" alt=\"{html.escape(row['panel_id'])} map image\">")
        else:
            parts.append("<div class=\"missing\">Artifact file missing locally.</div>")
        parts += [
            f"<div class=\"caption\"><strong>Caption to judge:</strong> {html.escape(row['caption'])}</div>",
            "<div class=\"fields\"><strong>CSV fields:</strong> visible water / roads / green area / named label; caption support; unsupported claims; omissions; notes.</div>",
            "</section>",
        ]
    parts += ["</div></body></html>"]
    return "\n".join(parts)


def build_choropleth_gallery(rows: list[dict[str, str]]) -> str:
    parts = [
        "<!doctype html>",
        "<html><head><meta charset=\"utf-8\"><title>Choropleth Cartographic Human Validation Gallery</title>",
        f"<style>{gallery_style()}</style></head><body>",
        "<h1>Choropleth Cartographic Human Validation Gallery</h1>",
        "<p class=\"note\">Blind review gallery for cartographic-quality annotation. Use this visual page together with <code>choropleth_cartographic_blind_panel.csv</code>. Fill only the <code>human_*</code> columns in the CSV; do not infer hidden VLM/source labels.</p>",
        "<div class=\"grid\">",
    ]
    for row in rows:
        artifact = row["review_image_path"]
        exists = (ROOT / artifact).exists()
        parts += [
            f"<section class=\"item\" id=\"{html.escape(row['panel_id'])}\">",
            f"<div class=\"meta\"><span class=\"panel\">{html.escape(row['panel_id'])}</span> &middot; {html.escape(row['kind'])} &middot; {html.escape(artifact)}</div>",
        ]
        if exists:
            parts.append(f"<img src=\"{html.escape(html_rel(artifact))}\" alt=\"{html.escape(row['panel_id'])} choropleth artifact\">")
        else:
            parts.append("<div class=\"missing\">Artifact file missing locally.</div>")
        parts += [
            "<div class=\"fields\"><strong>CSV fields:</strong> map content visible; title; legend/colorbar; readable text; layout not occluded; appears choropleth; quality score; verdict; main issue; notes.</div>",
            "</section>",
        ]
    parts += ["</div></body></html>"]
    return "\n".join(parts)


def build_execution_plan(priority_rows: list[dict[str, str]], assignment_rows: list[dict[str, str]]) -> str:
    mapgen = [row for row in priority_rows if row["task"] == "mapgenerator_caption_fidelity"]
    choro = [row for row in priority_rows if row["task"] == "choropleth_cartographic_quality"]
    urgent_mapgen = [row for row in mapgen if row["priority"] == "urgent_vlm_disagreement"]
    urgent_choro = [row for row in choro if row["priority"] == "urgent_vlm_disagreement"]
    batches = sorted({row["batch_id"] for row in assignment_rows})
    return "\n".join(
        [
            "# Human Validation Execution Plan",
            "",
            "This plan converts the remaining human-label gate into an executable validation workflow. It does not claim that labels have been collected; it specifies how completed labels will be accepted, summarized, and allowed to change manuscript claims.",
            "",
            "## Scope",
            "",
            f"- MapGenerator caption-fidelity cases: {len(mapgen)}.",
            f"- Choropleth cartographic-quality cases: {len(choro)}.",
            f"- Total two-annotator assignments: {len(assignment_rows)}.",
            f"- Batch IDs: {', '.join(batches)}.",
            f"- Urgent MapGenerator VLM-disagreement cases: {len(urgent_mapgen)}.",
            f"- Urgent choropleth VLM-disagreement cases: {len(urgent_choro)}.",
            "",
            "## Execution Steps",
            "",
            "1. Freeze the blind panel CSV files and keep the full panel files hidden from annotators.",
            "2. Assign every `panel_id` to annotator slots A and B using `human_validation_assignment_sheet.csv`.",
            "3. Ask annotators to edit only the `human_*` columns listed in `human_validation_file_contract.csv`.",
            "4. Run `summarize_human_validation.py --mapgenerator-labels ... --choropleth-labels ...` on completed annotator files.",
            "5. Merge disagreements into `human_validation_agreement_template.csv` and record expert adjudication only where needed.",
            "6. Revise the manuscript claim strength only for items satisfying `human_validation_acceptance_criteria.csv`.",
            "",
            "## Reporting Rules",
            "",
            "- Report human labels as a separate evidence layer from VLM verdicts, CLIP/SigLIP-style scores, and deterministic proxies.",
            "- Preserve the original VLM disagreement counts even after human adjudication, because evaluator instability is part of the finding.",
            "- Use human labels to strengthen RQ2 and choropleth visual-quality claims only when the corresponding acceptance criteria are met.",
            "- If completed labels remain sparse, report them as a pilot validation layer and keep the current limitations language.",
            "",
            "## Manuscript Update Trigger",
            "",
            "The manuscript can replace `human-label gate pending` caveats with human-supported claims only after the label summary reports nonzero completed annotations for both tasks and the agreement/adjudication template records final labels for all urgent disagreement cases.",
            "",
        ]
    )


def build_packet_readme(priority_rows: list[dict[str, str]], assignment_rows: list[dict[str, str]]) -> str:
    mapgen = [row for row in priority_rows if row["task"] == "mapgenerator_caption_fidelity"]
    choro = [row for row in priority_rows if row["task"] == "choropleth_cartographic_quality"]
    urgent = [row for row in priority_rows if row["priority"].startswith("urgent")]
    batches = sorted({row["batch_id"] for row in assignment_rows})
    return "\n".join(
        [
            "# Human Validation Packet",
            "",
            "This packet is prepared for collecting real human labels. It deliberately contains blank annotation fields and should not be cited as completed human evidence until completed annotator files are summarized.",
            "",
            "## Packet Contents",
            "",
            "- `mapgenerator_caption_blind_panel.csv`: blind caption-fidelity form.",
            "- `choropleth_cartographic_blind_panel.csv`: blind cartographic-quality form.",
            "- `human_validation_priority_queue.csv`: merged priority queue across both tasks.",
            "- `human_validation_assignment_sheet.csv`: two-annotator assignment sheet with batch IDs.",
            "- `annotator_packets/`: ready-to-fill per-annotator CSV packets using the exact return filenames expected by the summarizer.",
            "- `human_validation_agreement_template.csv`: blank merge/adjudication template for completed labels.",
            "- `human_validation_acceptance_criteria.csv`: thresholds for when human labels may strengthen manuscript claims.",
            "- `human_validation_file_contract.csv`: annotator-facing editable/locked column contract.",
            "- `human_validation_execution_plan.md`: step-by-step label collection, summary, and manuscript-update plan.",
            "- `human_validation_rubric.json`: label definitions and adjudication rules.",
            "- `mapgenerator_caption_gallery.html`: blind visual gallery for caption annotators.",
            "- `choropleth_cartographic_gallery.html`: blind visual gallery for cartographic-quality annotators.",
            "- `human_validation_gallery_index.csv`: machine-readable gallery/artifact index.",
            "",
            "## Coverage",
            "",
            f"- MapGenerator caption cases: {len(mapgen)}.",
            f"- Choropleth cartographic cases: {len(choro)}.",
            f"- Total annotation assignments at two independent annotators per item: {len(assignment_rows)}.",
            f"- Batches: {', '.join(batches)}.",
            f"- Urgent VLM-disagreement cases: {len(urgent)}.",
            "",
            "## Recommended Workflow",
            "",
            "1. Give annotator A and annotator B separate copies of the relevant blind panel CSVs.",
            "2. Prefer the files in `annotator_packets/`, which are already split by annotator slot and task without exposing VLM/proxy labels.",
            "3. After both annotators return completed files, run `summarize_human_validation.py` with the completed CSV paths.",
            "4. Use `human_validation_agreement_template.csv` to record disagreements and expert adjudication.",
            "5. Only then revise manuscript claims from `human-label gate pending` to human-supported evidence.",
            "",
            "## Guardrails",
            "",
            "- Do not show annotators the full panel files, VLM verdicts, proxy scores, or priority labels.",
            "- Do not treat agreement between local VLMs as a substitute for human labels.",
            "- Keep the raw completed annotator files outside the blinded review manuscript unless the journal explicitly asks for them.",
            "",
        ]
    )


def main() -> None:
    mapgen_rows = build_mapgenerator_panel()
    choro_rows = build_choropleth_panel()
    write_csv(
        OUT_DIR / "mapgenerator_caption_human_panel.csv",
        mapgen_rows,
        list(mapgen_rows[0].keys()) if mapgen_rows else [],
    )
    write_csv(
        OUT_DIR / "choropleth_cartographic_human_panel.csv",
        choro_rows,
        list(choro_rows[0].keys()) if choro_rows else [],
    )
    blind_mapgen = blind_mapgenerator_rows(mapgen_rows)
    blind_choro = blind_choropleth_rows(choro_rows)
    write_csv(
        OUT_DIR / "mapgenerator_caption_blind_panel.csv",
        blind_mapgen,
        list(blind_mapgen[0].keys()) if blind_mapgen else [],
    )
    write_csv(
        OUT_DIR / "choropleth_cartographic_blind_panel.csv",
        blind_choro,
        list(blind_choro[0].keys()) if blind_choro else [],
    )
    write_json(OUT_DIR / "human_validation_rubric.json", build_rubric())
    (OUT_DIR / "human_validation_protocol.md").write_text(build_protocol(mapgen_rows, choro_rows), encoding="utf-8")
    priority_rows = build_priority_queue(mapgen_rows, choro_rows)
    assignment_rows = build_assignment_rows(priority_rows)
    agreement_rows = build_agreement_template(priority_rows)
    write_csv(
        OUT_DIR / "human_validation_priority_queue.csv",
        priority_rows,
        list(priority_rows[0].keys()) if priority_rows else [],
    )
    write_csv(
        OUT_DIR / "human_validation_assignment_sheet.csv",
        assignment_rows,
        list(assignment_rows[0].keys()) if assignment_rows else [],
    )
    packet_manifest_rows = write_annotator_packets(blind_mapgen, blind_choro, assignment_rows)
    write_csv(
        OUT_DIR / "human_validation_annotator_packet_manifest.csv",
        packet_manifest_rows,
        list(packet_manifest_rows[0].keys()) if packet_manifest_rows else [],
    )
    write_csv(
        OUT_DIR / "human_validation_agreement_template.csv",
        agreement_rows,
        list(agreement_rows[0].keys()) if agreement_rows else [],
    )
    acceptance_rows = build_acceptance_criteria()
    write_csv(
        OUT_DIR / "human_validation_acceptance_criteria.csv",
        acceptance_rows,
        list(acceptance_rows[0].keys()),
    )
    file_contract_rows = build_file_contract()
    write_csv(
        OUT_DIR / "human_validation_file_contract.csv",
        file_contract_rows,
        list(file_contract_rows[0].keys()),
    )
    (OUT_DIR / "human_validation_execution_plan.md").write_text(
        build_execution_plan(priority_rows, assignment_rows),
        encoding="utf-8",
    )
    (OUT_DIR / "human_validation_packet_readme.md").write_text(
        build_packet_readme(priority_rows, assignment_rows),
        encoding="utf-8",
    )
    gallery_rows = build_gallery_index(mapgen_rows, choro_rows)
    write_csv(
        OUT_DIR / "human_validation_gallery_index.csv",
        gallery_rows,
        list(gallery_rows[0].keys()) if gallery_rows else [],
    )
    (OUT_DIR / "mapgenerator_caption_gallery.html").write_text(
        build_mapgenerator_gallery(mapgen_rows),
        encoding="utf-8",
    )
    (OUT_DIR / "choropleth_cartographic_gallery.html").write_text(
        build_choropleth_gallery(choro_rows),
        encoding="utf-8",
    )
    print(f"Wrote human validation panels to {OUT_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
