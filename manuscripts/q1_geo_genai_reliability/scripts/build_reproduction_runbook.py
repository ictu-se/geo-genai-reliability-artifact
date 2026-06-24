#!/usr/bin/env python3
"""Build a reviewer-facing reproduction runbook and command ledger."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MS_DIR = ROOT / "manuscripts/q1_geo_genai_reliability"
OUT_DIR = MS_DIR / "submission"
RUNBOOK_MD = OUT_DIR / "reproduction_runbook.md"
RUNBOOK_CSV = OUT_DIR / "reproduction_runbook_commands.csv"


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def command_rows() -> list[dict[str, str]]:
    return [
        {
            "phase": "environment",
            "order": "1",
            "required": "yes",
            "command": "conda env create -f manuscripts/q1_geo_genai_reliability/submission/environment_minimal.yml",
            "expected_artifacts": "Python environment with geospatial, image, and browser-rendering dependencies",
            "notes": "Use an equivalent Python 3.10+ environment if Conda is unavailable.",
        },
        {
            "phase": "source_data",
            "order": "2",
            "required": "yes",
            "command": "Read manuscripts/q1_geo_genai_reliability/submission/DATA_SOURCES.md and place third-party data in the documented layout.",
            "expected_artifacts": "Local source-linked data tree; raw third-party data are not redistributed in the public package",
            "notes": "This is a manual acquisition step because redistribution rights are external to this project.",
        },
        {
            "phase": "dataset_audit",
            "order": "3",
            "required": "yes",
            "command": "python3 experiments/00_dataset_reproducibility_audit/scripts/audit_datasets.py",
            "expected_artifacts": "dataset_inventory.csv; reproducibility_matrix.csv",
            "notes": "Regenerates release availability evidence for RQ1.",
        },
        {
            "phase": "mapgenerator_caption",
            "order": "4",
            "required": "yes",
            "command": "python3 experiments/02_mapgenerator_image_text_audit/scripts/audit_mapgenerator_pairs.py && python3 experiments/02_mapgenerator_image_text_audit/scripts/review_caption_visual_proxies.py",
            "expected_artifacts": "MapGenerator pair audit, proxy caption-fidelity review, contact sheets, summary JSON",
            "notes": "Uses deterministic image/caption heuristics and local visual proxies.",
        },
        {
            "phase": "mapgenerator_caption",
            "order": "5",
            "required": "optional",
            "command": "python3 experiments/02_mapgenerator_image_text_audit/scripts/run_clip_siglip_caption_scoring.py",
            "expected_artifacts": "mapgenerator_clip_caption_embedding_scores.csv; mapgenerator_clip_caption_embedding_summary.json",
            "notes": "Optional embedding environment may be required; scores are screening evidence, not human ground truth.",
        },
        {
            "phase": "scgm",
            "order": "6",
            "required": "yes",
            "command": "python3 experiments/03_scgm_subset_reproduction/scripts/build_scgm_manifest.py && python3 experiments/03_scgm_subset_reproduction/scripts/compute_edge_continuity.py",
            "expected_artifacts": "SCGM split manifests, complete-reference subsets, edge-continuity summaries",
            "notes": "Rebuilds RQ3 source coverage and target-neighbor continuity baselines.",
        },
        {
            "phase": "scgm",
            "order": "7",
            "required": "yes",
            "command": "python3 experiments/03_scgm_subset_reproduction/scripts/run_scgm_retrieval_baseline.py && python3 experiments/03_scgm_subset_reproduction/scripts/run_scgm_multifeature_retrieval_baseline.py && python3 experiments/03_scgm_subset_reproduction/scripts/run_scgm_learned_forest_baseline.py",
            "expected_artifacts": "SCGM retrieval, multi-feature retrieval, and learned-forest generated-output metrics and summaries",
            "notes": "Leakage guards exclude overlapping train/validation tile identifiers where applicable.",
        },
        {
            "phase": "scgm",
            "order": "8",
            "required": "yes",
            "command": "python3 experiments/03_scgm_subset_reproduction/scripts/run_scgm_mlp_baseline.py && python3 experiments/03_scgm_subset_reproduction/scripts/run_scgm_local_context_ridge_baseline.py && python3 experiments/03_scgm_subset_reproduction/scripts/run_scgm_convolutional_filter_ridge_baseline.py",
            "expected_artifacts": "SCGM MLP, local-context ridge, and convolutional-filter ridge metrics and summaries",
            "notes": "CPU-friendly learned and fixed-feature baselines for spatial-faithfulness diagnostics.",
        },
        {
            "phase": "scgm",
            "order": "9",
            "required": "optional",
            "command": "python3 experiments/03_scgm_subset_reproduction/scripts/run_scgm_patch_embedding_retrieval_baseline.py && python3 experiments/03_scgm_subset_reproduction/scripts/run_scgm_tiny_cnn_baseline.py",
            "expected_artifacts": "Patch-embedding retrieval and tiny-CNN generated-output metrics and summaries",
            "notes": "Requires additional dependencies/compute; outputs are preserved in the current evidence package.",
        },
        {
            "phase": "scgm",
            "order": "10",
            "required": "yes",
            "command": "python3 experiments/03_scgm_subset_reproduction/scripts/compute_scgm_mosaic_continuity_stress.py",
            "expected_artifacts": "scgm_mosaic_neighbor_stress_pairs.csv; scgm_mosaic_neighbor_stress_summary.json",
            "notes": "Measures generated neighbor seams; low seam discontinuity can also indicate over-smoothing.",
        },
        {
            "phase": "scgm",
            "order": "11",
            "required": "yes",
            "command": "python3 manuscripts/q1_geo_genai_reliability/scripts/build_scgm_official_reproduction_contract.py",
            "expected_artifacts": "submission/scgm_official_reproduction_contract/*.csv; environment_scgm_official_reproduction.yml; scgm_official_reproduction_contract.md",
            "notes": "Drafts the runtime, complete-reference subset, config, and command contract for a future official SCGM run without claiming it has been run.",
        },
        {
            "phase": "scgm",
            "order": "12",
            "required": "yes",
            "command": "python3 manuscripts/q1_geo_genai_reliability/scripts/build_scgm_official_local_overrides.py",
            "expected_artifacts": "submission/scgm_official_reproduction_contract/local_overrides/*; scgm_official_local_bridge/val/tilelist_18_16_3L.csv",
            "notes": "Creates a non-mutating local dataroot bridge, complete-reference datalist, and data-config overrides for future official inference.",
        },
        {
            "phase": "scgm",
            "order": "13",
            "required": "yes",
            "command": "python3 manuscripts/q1_geo_genai_reliability/scripts/build_scgm_official_reproduction_audit.py",
            "expected_artifacts": "submission/scgm_official_reproduction_audit/scgm_official_reproduction_audit.csv; .md",
            "notes": "Separates current SCGM diagnostics from the unresolved official checkpoint/runtime/cascade-conditioned reproduction gate.",
        },
        {
            "phase": "scgm",
            "order": "14",
            "required": "yes",
            "command": "python3 manuscripts/q1_geo_genai_reliability/scripts/build_scgm_official_feasibility_probe.py",
            "expected_artifacts": "submission/scgm_official_reproduction_audit/scgm_official_feasibility_probe.csv; .md",
            "notes": "Probes local runtime imports, checkpoint references, config paths, datalists, cascade paths, and planned official output directories without running heavy inference.",
        },
        {
            "phase": "choropleth",
            "order": "15",
            "required": "yes",
            "command": "python3 experiments/01_choropleth_llm_linter/scripts/lint_choropleth_data.py && python3 experiments/01_choropleth_llm_linter/scripts/audit_released_map_artifacts.py",
            "expected_artifacts": "Geodata lint report and released map artifact audit",
            "notes": "Establishes raw-data and released-output QA before generated-code benchmarking.",
        },
        {
            "phase": "choropleth",
            "order": "16",
            "required": "yes",
            "command": "python3 experiments/05_choropleth_reliability_benchmark/scripts/score_generated_runs.py && python3 experiments/05_choropleth_reliability_benchmark/scripts/audit_rendered_artifacts.py && python3 experiments/05_choropleth_reliability_benchmark/scripts/screenshot_level_qa.py",
            "expected_artifacts": "Expanded benchmark scores, rendered artifact QA, screenshot-level QA",
            "notes": "Uses preserved generated code and run outputs; local LLM reruns may not be bit-reproducible.",
        },
        {
            "phase": "choropleth",
            "order": "17",
            "required": "optional",
            "command": "Run local LLM/VLM generation, repair, and review scripts only when the same local model stack is available.",
            "expected_artifacts": "Generated scripts, safety scans, repair ledgers, VLM review CSVs",
            "notes": "The package preserves model outputs as evidence because reruns can vary across machines.",
        },
        {
            "phase": "human_validation",
            "order": "18",
            "required": "yes",
            "command": "python3 manuscripts/q1_geo_genai_reliability/scripts/validate_human_validation_packets.py",
            "expected_artifacts": "human_validation_packet_preflight.csv; human_validation_packet_preflight.md",
            "notes": "Validates annotator packet schemas, panel coverage, local artifact links, and rubric value constraints before labels are summarized.",
        },
        {
            "phase": "human_validation",
            "order": "19",
            "required": "optional",
            "command": "python3 manuscripts/q1_geo_genai_reliability/scripts/summarize_human_validation.py --mapgenerator-labels manuscripts/q1_geo_genai_reliability/submission/human_validation_panels/annotator_packets/mapgenerator_caption_fidelity_A_completed.csv manuscripts/q1_geo_genai_reliability/submission/human_validation_panels/annotator_packets/mapgenerator_caption_fidelity_B_completed.csv --choropleth-labels manuscripts/q1_geo_genai_reliability/submission/human_validation_panels/annotator_packets/choropleth_cartographic_quality_A_completed.csv manuscripts/q1_geo_genai_reliability/submission/human_validation_panels/annotator_packets/choropleth_cartographic_quality_B_completed.csv",
            "expected_artifacts": "human_validation_metric_summary.csv; mapgenerator_human_label_summary.csv; choropleth_human_label_summary.csv; human_validation_label_summary.md",
            "notes": "Run after completed annotator CSVs pass validate_human_validation_packets.py --require-completed; current blank packet outputs remain explicit no-label placeholders.",
        },
        {
            "phase": "human_validation",
            "order": "20",
            "required": "optional",
            "command": "python3 manuscripts/q1_geo_genai_reliability/scripts/build_human_validation_adjudication_queue.py",
            "expected_artifacts": "human_validation_adjudication_queue.csv; human_validation_adjudication_summary.csv; human_validation_final_label_template.csv",
            "notes": "Builds the adjudication and final-label queue from completed A/B annotator packets without inventing missing labels.",
        },
        {
            "phase": "human_validation",
            "order": "21",
            "required": "optional",
            "command": "python3 manuscripts/q1_geo_genai_reliability/scripts/build_human_validation_final_summary.py",
            "expected_artifacts": "human_validation_final_label_ledger.csv; human_validation_final_label_summary.csv; human_validation_final_label_summary.md",
            "notes": "Reduces agreed/adjudicated final labels into manuscript-ready summaries while preserving an explicit no-label status when labels remain blank.",
        },
        {
            "phase": "submission_package",
            "order": "22",
            "required": "yes",
            "command": "python3 manuscripts/q1_geo_genai_reliability/scripts/build_submission_package.py",
            "expected_artifacts": "Tables, compact/blinded manuscripts, submission ledgers, release preflight, reproducibility manifest",
            "notes": "Primary one-command rebuild for the manuscript evidence package.",
        },
        {
            "phase": "release",
            "order": "23",
            "required": "yes",
            "command": "python3 manuscripts/q1_geo_genai_reliability/scripts/build_release_license_audit.py && python3 manuscripts/q1_geo_genai_reliability/scripts/build_q1_submission_gate_tracker.py && python3 manuscripts/q1_geo_genai_reliability/scripts/build_reviewer_prebuttal_audit.py && python3 manuscripts/q1_geo_genai_reliability/scripts/build_public_release_skeleton.py && python3 manuscripts/q1_geo_genai_reliability/scripts/build_release_preflight.py && python3 manuscripts/q1_geo_genai_reliability/scripts/stage_zenodo_release.py && python3 manuscripts/q1_geo_genai_reliability/scripts/preflight_zenodo_release.py",
            "expected_artifacts": "release_license_audit; q1_submission_gate_tracker; reviewer_prebuttal_audit; release_preflight checks and DOI metadata drafts; public_release_skeleton; staged Zenodo bundle and preflight",
            "notes": "Keeps final DOI/license/human-label/journal-route decisions manual while making closure criteria auditable.",
        },
        {
            "phase": "release",
            "order": "24",
            "required": "yes",
            "command": "python3 manuscripts/q1_geo_genai_reliability/scripts/build_reproducibility_manifest.py && python3 manuscripts/q1_geo_genai_reliability/scripts/build_public_release_skeleton.py && python3 manuscripts/q1_geo_genai_reliability/scripts/stage_zenodo_release.py && python3 manuscripts/q1_geo_genai_reliability/scripts/preflight_zenodo_release.py && python3 manuscripts/q1_geo_genai_reliability/scripts/build_reproducibility_manifest.py",
            "expected_artifacts": "Checksum manifest and public-release skeleton regenerated after release artifacts are present",
            "notes": "Refreshes the file map and manifest summary without selecting the final DOI, repository URL, or license.",
        },
        {
            "phase": "verification",
            "order": "25",
            "required": "yes",
            "command": "python3 manuscripts/q1_geo_genai_reliability/scripts/audit_manuscript_consistency.py && python3 manuscripts/q1_geo_genai_reliability/scripts/audit_manuscript_readiness.py",
            "expected_artifacts": "manuscript_consistency_audit.md; manuscript_readiness_audit.md",
            "notes": "Automated gates verify numerical consistency and package completeness.",
        },
        {
            "phase": "verification",
            "order": "26",
            "required": "yes",
            "command": "python3 -m py_compile manuscripts/q1_geo_genai_reliability/scripts/*.py experiments/02_mapgenerator_image_text_audit/scripts/*.py experiments/03_scgm_subset_reproduction/scripts/*.py experiments/05_choropleth_reliability_benchmark/scripts/*.py",
            "expected_artifacts": "No syntax errors in manuscript, MapGenerator, SCGM, choropleth, and release scripts",
            "notes": "Run after any script edits.",
        },
    ]


def build_markdown(rows: list[dict[str, str]]) -> str:
    required = sum(row["required"] == "yes" for row in rows)
    optional = sum(row["required"] == "optional" for row in rows)
    lines = [
        "# Reproduction Runbook",
        "",
        "This runbook is the practical rebuild path for the Geo-GenAI reliability manuscript evidence package. It separates required deterministic rebuild steps from optional model-dependent reruns.",
        "",
        "## Scope",
        "",
        "- Required steps rebuild source-linked audits, deterministic metrics, generated-output summaries, manuscript tables, submission ledgers, and verification audits.",
        "- Optional steps involve embedding models, local LLM/VLM runs, or additional compute. Their existing outputs are preserved as evidence because reruns may not be bit-reproducible.",
        "- Raw third-party datasets are not redistributed; obtain them using `submission/DATA_SOURCES.md`.",
        "",
        "## Summary",
        "",
        f"- Command phases: {len(rows)}",
        f"- Required phases: {required}",
        f"- Optional/model-dependent phases: {optional}",
        "",
        "## Command Ledger",
        "",
        "| Order | Phase | Required | Command | Expected artifacts | Notes |",
        "|---:|---|---|---|---|---|",
    ]
    for row in rows:
        command = row["command"].replace("|", "\\|")
        expected = row["expected_artifacts"].replace("|", "\\|")
        notes = row["notes"].replace("|", "\\|")
        lines.append(f"| {row['order']} | {row['phase']} | {row['required']} | `{command}` | {expected} | {notes} |")
    lines += [
        "",
        "## Completion Criteria",
        "",
        "- `notes/manuscript_readiness_audit.md` reports all automated gates passing.",
        "- `notes/manuscript_consistency_audit.md` reports all consistency checks passing.",
        "- `submission/reproducibility_manifest.csv` has SHA-256 checksums for all tracked release artifacts.",
        "- `submission/latex/main.tex` and `submission/latex/main.pdf` are the primary manuscript route for ongoing submission work.",
        "- Manual gates remain explicit: human labels, DOI/public repository URL, license decision, journal-native reference style, and final journal/quartile recheck.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    rows = command_rows()
    write_csv(RUNBOOK_CSV, rows)
    RUNBOOK_MD.write_text(build_markdown(rows), encoding="utf-8")
    print(f"Wrote {RUNBOOK_CSV.relative_to(ROOT)}")
    print(f"Wrote {RUNBOOK_MD.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
