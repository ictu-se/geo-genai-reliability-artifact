#!/usr/bin/env python3
"""Audit manuscript package readiness from current local artifacts."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MS_DIR = ROOT / "manuscripts/q1_geo_genai_reliability"
NOTES_DIR = MS_DIR / "notes"
TABLE_DIR = MS_DIR / "tables"
FIG_DIR = MS_DIR / "figures"
SUBMISSION_DIR = MS_DIR / "submission"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def word_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").split())


def text_word_count(text: str) -> int:
    return len(re.findall(r"\b[\w-]+\b", text))


def status(ok: bool) -> str:
    return "PASS" if ok else "TODO"


def exists(path: Path) -> bool:
    return path.exists() and path.stat().st_size > 0


def main() -> None:
    draft = MS_DIR / "draft/manuscript_draft.md"
    draft_text = draft.read_text(encoding="utf-8")
    table_files = sorted(TABLE_DIR.glob("table_*.csv"))
    figure_index = FIG_DIR / "figure_index.md"
    figure_count = sum(
        line.startswith("| Figure ") and not line.startswith("| Figure |")
        for line in figure_index.read_text(encoding="utf-8").splitlines()
    )
    table19 = read_csv(TABLE_DIR / "table_19_iterative_validator_repair.csv")
    table18 = read_csv(TABLE_DIR / "table_18_choropleth_vlm_cartographic_review.csv")
    table18b = read_csv(TABLE_DIR / "table_18b_choropleth_vlm_agreement.csv")
    table15 = read_csv(TABLE_DIR / "table_15_mapgenerator_vlm_caption_review.csv")
    table15b = read_csv(TABLE_DIR / "table_15b_mapgenerator_vlm_agreement.csv")
    table16 = read_csv(TABLE_DIR / "table_16_screenshot_level_choropleth_qa.csv")
    table20_path = TABLE_DIR / "table_20_iterative_repair_model_comparison.csv"
    table20 = read_csv(table20_path) if table20_path.exists() else []
    iterative_summary = json.loads(
        (ROOT / "experiments/05_choropleth_reliability_benchmark/outputs/scores/iterative_validator_repair_summary_qwen2.5-coder_32b.json").read_text()
    )
    scgm_mlp_summary_path = ROOT / "experiments/03_scgm_subset_reproduction/outputs/scgm_mlp_summary.json"
    scgm_mlp_summary = json.loads(scgm_mlp_summary_path.read_text()) if scgm_mlp_summary_path.exists() else {}
    scgm_local_ridge_summary_path = ROOT / "experiments/03_scgm_subset_reproduction/outputs/scgm_local_context_ridge_summary.json"
    scgm_local_ridge_summary = json.loads(scgm_local_ridge_summary_path.read_text()) if scgm_local_ridge_summary_path.exists() else {}
    scgm_conv_ridge_summary_path = ROOT / "experiments/03_scgm_subset_reproduction/outputs/scgm_convolutional_filter_ridge_summary.json"
    scgm_conv_ridge_summary = json.loads(scgm_conv_ridge_summary_path.read_text()) if scgm_conv_ridge_summary_path.exists() else {}
    scgm_patch_summary_path = ROOT / "experiments/03_scgm_subset_reproduction/outputs/scgm_patch_embedding_retrieval_summary.json"
    scgm_patch_summary = json.loads(scgm_patch_summary_path.read_text()) if scgm_patch_summary_path.exists() else {}
    scgm_tiny_cnn_summary_path = ROOT / "experiments/03_scgm_subset_reproduction/outputs/scgm_tiny_cnn_summary.json"
    scgm_tiny_cnn_summary = json.loads(scgm_tiny_cnn_summary_path.read_text()) if scgm_tiny_cnn_summary_path.exists() else {}
    scgm_mosaic_summary_path = ROOT / "experiments/03_scgm_subset_reproduction/outputs/scgm_mosaic_neighbor_stress_summary.json"
    scgm_mosaic_summary = json.loads(scgm_mosaic_summary_path.read_text()) if scgm_mosaic_summary_path.exists() else []
    embedding_summary_path = ROOT / "experiments/02_mapgenerator_image_text_audit/outputs/mapgenerator_clip_caption_embedding_summary.json"
    embedding_summary = json.loads(embedding_summary_path.read_text()) if embedding_summary_path.exists() else {}
    blinded = SUBMISSION_DIR / "blinded_main_manuscript.md"
    blinded_compact = SUBMISSION_DIR / "blinded_compact_main_manuscript.md"
    supplement_manifest = SUBMISSION_DIR / "supplementary_material_manifest.md"
    ijgis_compliance = SUBMISSION_DIR / "ijgis_compliance_checklist.md"
    journal_target_recheck = SUBMISSION_DIR / "journal_target_recheck_2026-06-24.md"
    journal_style_preflight = SUBMISSION_DIR / "journal_style_preflight/journal_style_preflight.csv"
    journal_style_preflight_report = SUBMISSION_DIR / "journal_style_preflight/journal_style_preflight.md"
    package_audit = SUBMISSION_DIR / "submission_package_audit.md"
    consistency_audit = NOTES_DIR / "manuscript_consistency_audit.md"
    page_budget_audit = NOTES_DIR / "page_budget_audit.md"
    main_supplement_split = SUBMISSION_DIR / "main_supplement_split.csv"
    main_text_word_budget = SUBMISSION_DIR / "main_text_word_budget.csv"
    compact_main_display_plan = SUBMISSION_DIR / "compact_main_display_plan.csv"
    main_text_compression_plan = SUBMISSION_DIR / "main_text_compression_plan.md"
    compact_main_manuscript = SUBMISSION_DIR / "compact_main_manuscript.md"
    latex_main = SUBMISSION_DIR / "latex/main.tex"
    latex_pdf = SUBMISSION_DIR / "latex/main.pdf"
    latex_bib = SUBMISSION_DIR / "latex/references.bib"
    latex_readme = SUBMISSION_DIR / "latex/README_latex.md"
    latex_build_log = SUBMISSION_DIR / "latex/latex_build.log"
    latex_interact_cls = SUBMISSION_DIR / "latex/interact.cls"
    latex_tfv_bst = SUBMISSION_DIR / "latex/tfv.bst"
    abstract_pack = SUBMISSION_DIR / "submission_abstract_pack.md"
    abstract_fields = SUBMISSION_DIR / "submission_abstract_fields.csv"
    citation_metadata = SUBMISSION_DIR / "citation_metadata.csv"
    references_bib = SUBMISSION_DIR / "references.bib"
    citation_ledger = NOTES_DIR / "citation_metadata_ledger.md"
    citation_verification = SUBMISSION_DIR / "citation_verification_report.csv"
    release_plan = SUBMISSION_DIR / "reproducibility_release_plan.md"
    reproduction_runbook = SUBMISSION_DIR / "reproduction_runbook.md"
    reproduction_runbook_commands = SUBMISSION_DIR / "reproduction_runbook_commands.csv"
    release_preflight = SUBMISSION_DIR / "release_preflight/release_preflight_checks.csv"
    release_preflight_report = SUBMISSION_DIR / "release_preflight/release_preflight.md"
    release_license_matrix = SUBMISSION_DIR / "release_license_audit/release_license_matrix.csv"
    release_license_audit = SUBMISSION_DIR / "release_license_audit/release_license_audit.md"
    public_release_readme = SUBMISSION_DIR / "public_release_skeleton/README_release_skeleton.md"
    public_release_file_map = SUBMISSION_DIR / "public_release_skeleton/RELEASE_FILE_MAP.csv"
    public_release_exclusions = SUBMISSION_DIR / "public_release_skeleton/THIRD_PARTY_EXCLUSIONS.md"
    public_release_license_note = SUBMISSION_DIR / "public_release_skeleton/LICENSE_DECISION_REQUIRED.md"
    public_release_manifest_summary = SUBMISSION_DIR / "public_release_skeleton/release_manifest_summary.csv"
    reproducibility_manifest = SUBMISSION_DIR / "reproducibility_manifest.csv"
    reproducibility_manifest_report = SUBMISSION_DIR / "reproducibility_manifest.md"
    data_sources = SUBMISSION_DIR / "DATA_SOURCES.md"
    environment_file = SUBMISSION_DIR / "environment_minimal.yml"
    optional_embedding_environment = SUBMISSION_DIR / "environment_optional_embedding.yml"
    human_mapgen_panel = SUBMISSION_DIR / "human_validation_panels/mapgenerator_caption_human_panel.csv"
    human_choro_panel = SUBMISSION_DIR / "human_validation_panels/choropleth_cartographic_human_panel.csv"
    blind_mapgen_panel = SUBMISSION_DIR / "human_validation_panels/mapgenerator_caption_blind_panel.csv"
    blind_choro_panel = SUBMISSION_DIR / "human_validation_panels/choropleth_cartographic_blind_panel.csv"
    human_rubric = SUBMISSION_DIR / "human_validation_panels/human_validation_rubric.json"
    human_packet_readme = SUBMISSION_DIR / "human_validation_panels/human_validation_packet_readme.md"
    human_priority_queue = SUBMISSION_DIR / "human_validation_panels/human_validation_priority_queue.csv"
    human_assignment_sheet = SUBMISSION_DIR / "human_validation_panels/human_validation_assignment_sheet.csv"
    human_annotator_packet_manifest = SUBMISSION_DIR / "human_validation_panels/human_validation_annotator_packet_manifest.csv"
    human_agreement_template = SUBMISSION_DIR / "human_validation_panels/human_validation_agreement_template.csv"
    human_packet_preflight = SUBMISSION_DIR / "human_validation_panels/preflight/human_validation_packet_preflight.csv"
    human_packet_preflight_report = SUBMISSION_DIR / "human_validation_panels/preflight/human_validation_packet_preflight.md"
    human_gallery_index = SUBMISSION_DIR / "human_validation_panels/human_validation_gallery_index.csv"
    mapgen_gallery = SUBMISSION_DIR / "human_validation_panels/mapgenerator_caption_gallery.html"
    choro_gallery = SUBMISSION_DIR / "human_validation_panels/choropleth_cartographic_gallery.html"
    human_acceptance_criteria = SUBMISSION_DIR / "human_validation_panels/human_validation_acceptance_criteria.csv"
    human_file_contract = SUBMISSION_DIR / "human_validation_panels/human_validation_file_contract.csv"
    human_execution_plan = SUBMISSION_DIR / "human_validation_panels/human_validation_execution_plan.md"
    human_label_summary = SUBMISSION_DIR / "human_validation_panels/summaries/human_validation_label_summary.md"
    human_metric_summary = SUBMISSION_DIR / "human_validation_panels/summaries/human_validation_metric_summary.csv"
    human_adjudication_queue = SUBMISSION_DIR / "human_validation_panels/summaries/human_validation_adjudication_queue.csv"
    human_adjudication_summary = SUBMISSION_DIR / "human_validation_panels/summaries/human_validation_adjudication_summary.csv"
    human_final_label_template = SUBMISSION_DIR / "human_validation_panels/summaries/human_validation_final_label_template.csv"
    human_final_label_ledger = SUBMISSION_DIR / "human_validation_panels/summaries/human_validation_final_label_ledger.csv"
    human_final_label_summary = SUBMISSION_DIR / "human_validation_panels/summaries/human_validation_final_label_summary.csv"
    human_final_label_report = SUBMISSION_DIR / "human_validation_panels/summaries/human_validation_final_label_summary.md"
    human_adjudication_report = SUBMISSION_DIR / "human_validation_panels/summaries/human_validation_adjudication_queue.md"
    evaluator_adjudication_summary = SUBMISSION_DIR / "human_validation_panels/summaries/evaluator_adjudication_summary.csv"
    mapgen_adjudication_ledger = SUBMISSION_DIR / "human_validation_panels/summaries/mapgenerator_evaluator_adjudication_ledger.csv"
    choro_adjudication_ledger = SUBMISSION_DIR / "human_validation_panels/summaries/choropleth_evaluator_adjudication_ledger.csv"
    vlm_judge_robustness = SUBMISSION_DIR / "evaluator_reliability/vlm_judge_robustness_audit.csv"
    multijudge_consensus = SUBMISSION_DIR / "evaluator_reliability/multijudge_consensus_summary.csv"
    mapgen_multijudge = SUBMISSION_DIR / "evaluator_reliability/mapgenerator_multijudge_consensus.csv"
    choro_multijudge = SUBMISSION_DIR / "evaluator_reliability/choropleth_multijudge_consensus.csv"
    cross_paradigm_matrix = SUBMISSION_DIR / "cross_paradigm/cross_paradigm_reliability_matrix.csv"
    cross_paradigm_summary = SUBMISSION_DIR / "cross_paradigm/cross_paradigm_reliability_summary.csv"
    matched_repair_summary = SUBMISSION_DIR / "repair_model_suite/matched_repair_model_summary.csv"
    matched_repair_ledger = SUBMISSION_DIR / "repair_model_suite/matched_repair_case_ledger.csv"
    rq_evidence_map = SUBMISSION_DIR / "evidence_map/rq_evidence_map.csv"
    objective_completion_audit = SUBMISSION_DIR / "evidence_map/objective_completion_audit.csv"
    goal_completion_audit = SUBMISSION_DIR / "evidence_map/goal_completion_audit.csv"
    goal_completion_audit_report = SUBMISSION_DIR / "evidence_map/goal_completion_audit.md"
    claim_evidence_crosswalk = SUBMISSION_DIR / "claim_evidence_crosswalk/claim_evidence_crosswalk.csv"
    claim_evidence_crosswalk_report = SUBMISSION_DIR / "claim_evidence_crosswalk/claim_evidence_crosswalk.md"
    q1_gate_tracker = SUBMISSION_DIR / "q1_submission_gate_tracker/q1_submission_gate_tracker.csv"
    q1_gate_tracker_report = SUBMISSION_DIR / "q1_submission_gate_tracker/q1_submission_gate_tracker.md"
    reviewer_prebuttal = SUBMISSION_DIR / "reviewer_prebuttal_audit/reviewer_prebuttal_audit.csv"
    reviewer_prebuttal_report = SUBMISSION_DIR / "reviewer_prebuttal_audit/reviewer_prebuttal_audit.md"
    scgm_official_audit = SUBMISSION_DIR / "scgm_official_reproduction_audit/scgm_official_reproduction_audit.csv"
    scgm_official_audit_report = SUBMISSION_DIR / "scgm_official_reproduction_audit/scgm_official_reproduction_audit.md"
    scgm_feasibility_probe = SUBMISSION_DIR / "scgm_official_reproduction_audit/scgm_official_feasibility_probe.csv"
    scgm_feasibility_probe_report = SUBMISSION_DIR / "scgm_official_reproduction_audit/scgm_official_feasibility_probe.md"
    scgm_official_contract = SUBMISSION_DIR / "scgm_official_reproduction_contract/scgm_official_reproduction_contract.md"
    scgm_runtime_contract = SUBMISSION_DIR / "scgm_official_reproduction_contract/scgm_runtime_dependency_contract.csv"
    scgm_config_mapping = SUBMISSION_DIR / "scgm_official_reproduction_contract/scgm_official_config_mapping.csv"
    scgm_run_commands = SUBMISSION_DIR / "scgm_official_reproduction_contract/scgm_official_run_commands.csv"
    scgm_contract_environment = SUBMISSION_DIR / "scgm_official_reproduction_contract/environment_scgm_official_reproduction.yml"
    scgm_local_override_manifest = SUBMISSION_DIR / "scgm_official_reproduction_contract/local_overrides/scgm_official_local_override_manifest.csv"
    scgm_local_override_report = SUBMISSION_DIR / "scgm_official_reproduction_contract/local_overrides/scgm_official_local_overrides.md"
    human_mapgen_rows = read_csv(human_mapgen_panel) if human_mapgen_panel.exists() else []
    human_choro_rows = read_csv(human_choro_panel) if human_choro_panel.exists() else []
    blind_mapgen_rows = read_csv(blind_mapgen_panel) if blind_mapgen_panel.exists() else []
    blind_choro_rows = read_csv(blind_choro_panel) if blind_choro_panel.exists() else []
    human_priority_rows = read_csv(human_priority_queue) if human_priority_queue.exists() else []
    human_assignment_rows = read_csv(human_assignment_sheet) if human_assignment_sheet.exists() else []
    human_packet_rows = read_csv(human_annotator_packet_manifest) if human_annotator_packet_manifest.exists() else []
    human_agreement_rows = read_csv(human_agreement_template) if human_agreement_template.exists() else []
    human_packet_preflight_rows = read_csv(human_packet_preflight) if human_packet_preflight.exists() else []
    human_gallery_rows = read_csv(human_gallery_index) if human_gallery_index.exists() else []
    human_acceptance_rows = read_csv(human_acceptance_criteria) if human_acceptance_criteria.exists() else []
    human_file_contract_rows = read_csv(human_file_contract) if human_file_contract.exists() else []
    human_metric_rows = read_csv(human_metric_summary) if human_metric_summary.exists() else []
    human_adjudication_rows = read_csv(human_adjudication_queue) if human_adjudication_queue.exists() else []
    human_adjudication_summary_rows = read_csv(human_adjudication_summary) if human_adjudication_summary.exists() else []
    human_final_label_rows = read_csv(human_final_label_template) if human_final_label_template.exists() else []
    human_final_ledger_rows = read_csv(human_final_label_ledger) if human_final_label_ledger.exists() else []
    human_final_summary_rows = read_csv(human_final_label_summary) if human_final_label_summary.exists() else []
    citation_rows = read_csv(citation_metadata) if citation_metadata.exists() else []
    citation_verification_rows = read_csv(citation_verification) if citation_verification.exists() else []
    journal_style_rows = read_csv(journal_style_preflight) if journal_style_preflight.exists() else []
    journal_style_automated_rows = [row for row in journal_style_rows if row.get("mode") == "automated"]
    journal_style_manual_rows = [row for row in journal_style_rows if row.get("mode") == "manual"]
    reproducibility_manifest_rows = read_csv(reproducibility_manifest) if reproducibility_manifest.exists() else []
    reproduction_runbook_rows = read_csv(reproduction_runbook_commands) if reproduction_runbook_commands.exists() else []
    release_preflight_rows = read_csv(release_preflight) if release_preflight.exists() else []
    release_preflight_automated_rows = [row for row in release_preflight_rows if row.get("mode") == "automated"]
    release_preflight_manual_rows = [row for row in release_preflight_rows if row.get("mode") == "manual"]
    release_license_rows = read_csv(release_license_matrix) if release_license_matrix.exists() else []
    public_release_file_map_rows = read_csv(public_release_file_map) if public_release_file_map.exists() else []
    public_release_summary_rows = read_csv(public_release_manifest_summary) if public_release_manifest_summary.exists() else []
    adjudication_rows = read_csv(evaluator_adjudication_summary) if evaluator_adjudication_summary.exists() else []
    mapgen_adjudication_rows = read_csv(mapgen_adjudication_ledger) if mapgen_adjudication_ledger.exists() else []
    choro_adjudication_rows = read_csv(choro_adjudication_ledger) if choro_adjudication_ledger.exists() else []
    vlm_judge_rows = read_csv(vlm_judge_robustness) if vlm_judge_robustness.exists() else []
    multijudge_rows = read_csv(multijudge_consensus) if multijudge_consensus.exists() else []
    mapgen_multijudge_rows = read_csv(mapgen_multijudge) if mapgen_multijudge.exists() else []
    choro_multijudge_rows = read_csv(choro_multijudge) if choro_multijudge.exists() else []
    cross_paradigm_rows = read_csv(cross_paradigm_matrix) if cross_paradigm_matrix.exists() else []
    cross_paradigm_summary_rows = read_csv(cross_paradigm_summary) if cross_paradigm_summary.exists() else []
    matched_repair_rows = read_csv(matched_repair_summary) if matched_repair_summary.exists() else []
    matched_repair_ledger_rows = read_csv(matched_repair_ledger) if matched_repair_ledger.exists() else []
    rq_evidence_rows = read_csv(rq_evidence_map) if rq_evidence_map.exists() else []
    objective_completion_rows = read_csv(objective_completion_audit) if objective_completion_audit.exists() else []
    goal_completion_rows = read_csv(goal_completion_audit) if goal_completion_audit.exists() else []
    claim_evidence_rows = read_csv(claim_evidence_crosswalk) if claim_evidence_crosswalk.exists() else []
    q1_gate_rows = read_csv(q1_gate_tracker) if q1_gate_tracker.exists() else []
    reviewer_prebuttal_rows = read_csv(reviewer_prebuttal) if reviewer_prebuttal.exists() else []
    scgm_official_rows = read_csv(scgm_official_audit) if scgm_official_audit.exists() else []
    scgm_probe_rows = read_csv(scgm_feasibility_probe) if scgm_feasibility_probe.exists() else []
    scgm_runtime_rows = read_csv(scgm_runtime_contract) if scgm_runtime_contract.exists() else []
    scgm_config_rows = read_csv(scgm_config_mapping) if scgm_config_mapping.exists() else []
    scgm_command_rows = read_csv(scgm_run_commands) if scgm_run_commands.exists() else []
    scgm_local_override_rows = read_csv(scgm_local_override_manifest) if scgm_local_override_manifest.exists() else []
    split_rows = read_csv(main_supplement_split) if main_supplement_split.exists() else []
    word_budget_rows = read_csv(main_text_word_budget) if main_text_word_budget.exists() else []
    compact_display_rows = read_csv(compact_main_display_plan) if compact_main_display_plan.exists() else []
    abstract_field_rows = read_csv(abstract_fields) if abstract_fields.exists() else []
    abstract_fields_by_name = {row.get("field", ""): row for row in abstract_field_rows}
    short_abstract_words = text_word_count(abstract_fields_by_name.get("short_abstract", {}).get("value", ""))
    keyword_count = int(abstract_fields_by_name.get("keywords", {}).get("word_count", "0") or 0)
    blinded_text = blinded.read_text(encoding="utf-8") if blinded.exists() else ""
    blinded_compact_text = blinded_compact.read_text(encoding="utf-8") if blinded_compact.exists() else ""
    latex_text = latex_main.read_text(encoding="utf-8") if latex_main.exists() else ""
    latex_figure_count = latex_text.count("\\begin{figure}")
    latex_table_count = latex_text.count("\\begin{table}")
    review_banned = [
        "/" + "Users/",
        "nguyen" + "thevinh",
        "Geo-LLM",
        "IC" + "TA",
        "Over" + "leaf",
        "LN" + "CS",
        "ll" + "ncs",
        "sp" + "lncs",
    ]
    blinded_findings = [item for item in review_banned if item in blinded_text]
    blinded_compact_findings = [item for item in review_banned if item in blinded_compact_text]

    checks: list[tuple[str, bool, str]] = [
        ("Draft exists and is substantial", exists(draft) and word_count(draft) >= 9000, f"{word_count(draft)} words"),
        ("References section exists", "## References" in draft_text, ""),
        ("Acknowledgments section exists", "## Acknowledgments" in draft_text, ""),
        ("Declaration of interest statement exists", "## Declaration of Interest Statement" in draft_text, ""),
        ("Data availability statement exists", "## Data Availability Statement" in draft_text, ""),
        ("Software availability statement exists", "## Software Availability Statement" in draft_text, ""),
        ("Submission packaging plan exists", exists(NOTES_DIR / "submission_packaging_plan.md"), ""),
        ("Submission readiness checklist exists", exists(NOTES_DIR / "submission_readiness_checklist.md"), ""),
        ("Blinded submission manuscript exists", exists(blinded), ""),
        ("Blinded submission manuscript has no obvious identity/path leaks", exists(blinded) and not blinded_findings, "; ".join(blinded_findings)),
        ("Blinded compact submission manuscript exists", exists(blinded_compact), f"{word_count(blinded_compact) if blinded_compact.exists() else 0} words"),
        ("Blinded compact submission manuscript has no obvious identity/path leaks", exists(blinded_compact) and not blinded_compact_findings, "; ".join(blinded_compact_findings)),
        ("Supplementary material manifest exists", exists(supplement_manifest), ""),
        ("selected journal compliance checklist exists", exists(ijgis_compliance), ""),
        (
            "Dated journal-target source recheck exists",
            exists(journal_target_recheck)
            and "Checked date: 2026-06-24" in journal_target_recheck.read_text(encoding="utf-8")
            and "official-opened" in journal_target_recheck.read_text(encoding="utf-8")
            and "third-party/supporting evidence" in journal_target_recheck.read_text(encoding="utf-8"),
            "2026-06-24 source-confidence ledger",
        ),
        (
            "Journal style preflight exists",
            exists(journal_style_preflight_report)
            and len(journal_style_automated_rows) >= 10
            and all(row.get("status") == "pass" for row in journal_style_automated_rows)
            and len(journal_style_manual_rows) >= 3,
            f"automated passed={sum(row.get('status') == 'pass' for row in journal_style_automated_rows)}/{len(journal_style_automated_rows)}; manual gates={len(journal_style_manual_rows)}",
        ),
        ("Structured citation metadata export exists", len(citation_rows) >= 14 and exists(references_bib) and exists(citation_ledger), f"{len(citation_rows)} exported references"),
        (
            "Citation DOI/arXiv verification report is current",
            len(citation_verification_rows) == len(citation_rows)
            and all(row.get("verification_status") in {"verified", "resolver_verified", "publisher_url_verified"} for row in citation_verification_rows),
            "; ".join(sorted({row.get("verification_status", "missing") for row in citation_verification_rows})) if citation_verification_rows else "missing",
        ),
        ("Reproducibility release plan exists", exists(release_plan), ""),
        (
            "Reproduction runbook exists",
            exists(reproduction_runbook)
            and len(reproduction_runbook_rows) >= 15
            and sum(row.get("required") == "yes" for row in reproduction_runbook_rows) >= 10
            and sum(row.get("required") == "optional" for row in reproduction_runbook_rows) >= 3
            and any(row.get("phase") == "submission_package" for row in reproduction_runbook_rows)
            and any(row.get("phase") == "verification" for row in reproduction_runbook_rows),
            f"commands={len(reproduction_runbook_rows)}; required={sum(row.get('required') == 'yes' for row in reproduction_runbook_rows)}; optional={sum(row.get('required') == 'optional' for row in reproduction_runbook_rows)}",
        ),
        (
            "DOI/public repository release preflight exists",
            exists(release_preflight_report)
            and len(release_preflight_automated_rows) >= 7
            and all(row.get("status") == "pass" for row in release_preflight_automated_rows)
            and len(release_preflight_manual_rows) >= 3,
            f"automated passed={sum(row.get('status') == 'pass' for row in release_preflight_automated_rows)}/{len(release_preflight_automated_rows)}; manual gates={len(release_preflight_manual_rows)}",
        ),
        (
            "Release-license audit exists",
            exists(release_license_audit)
            and len(release_license_rows) >= 8
            and any(row.get("artifact_family") == "project_created_code" for row in release_license_rows)
            and any(row.get("artifact_family") == "MapGenerator" and "source-link" in row.get("release_posture", "") for row in release_license_rows)
            and any(row.get("artifact_family") == "model_weights_and_checkpoints" and "Do not upload" in row.get("public_release_action", "") for row in release_license_rows),
            f"release rows={len(release_license_rows)}",
        ),
        (
            "Public release skeleton exists",
            exists(public_release_readme)
            and exists(public_release_exclusions)
            and exists(public_release_license_note)
            and len(public_release_file_map_rows) >= 6
            and len(public_release_summary_rows) >= 5
            and any(row.get("release_family") == "third_party_raw_data" and row.get("include_in_public_release") == "no" for row in public_release_file_map_rows)
            and "No final top-level license is selected" in public_release_license_note.read_text(encoding="utf-8")
            and "Raw third-party datasets and cloned upstream repositories are source-linked" in public_release_readme.read_text(encoding="utf-8")
            and "/" + "Users/" not in public_release_readme.read_text(encoding="utf-8")
            and "/" + "Users/" not in public_release_exclusions.read_text(encoding="utf-8"),
            f"file-map rows={len(public_release_file_map_rows)}; summary rows={len(public_release_summary_rows)}",
        ),
        (
            "Reproducibility checksum manifest exists",
            exists(reproducibility_manifest_report)
            and len(reproducibility_manifest_rows) >= 100
            and all(len(row.get("sha256", "")) == 64 for row in reproducibility_manifest_rows[:50]),
            f"{len(reproducibility_manifest_rows)} tracked artifacts",
        ),
        ("Review-facing data-source manifest exists", exists(data_sources), ""),
        ("Minimal environment manifest exists", exists(environment_file), ""),
        ("Optional embedding environment manifest exists", exists(optional_embedding_environment), ""),
        ("Human/adjudication validation panels exist", len(human_mapgen_rows) >= 20 and len(human_choro_rows) >= 18, f"MapGenerator={len(human_mapgen_rows)}; choropleth={len(human_choro_rows)}"),
        ("Blind validation exports and rubric exist", len(blind_mapgen_rows) == len(human_mapgen_rows) and len(blind_choro_rows) == len(human_choro_rows) and exists(human_rubric), f"blind MapGenerator={len(blind_mapgen_rows)}; blind choropleth={len(blind_choro_rows)}"),
        (
            "Human validation packet is reviewer-ready",
            exists(human_packet_readme)
            and len(human_priority_rows) == len(human_mapgen_rows) + len(human_choro_rows)
            and len(human_assignment_rows) == 2 * len(human_priority_rows)
            and len(human_agreement_rows) == len(human_priority_rows)
            and any(row.get("priority") == "urgent_vlm_disagreement" for row in human_priority_rows),
            f"priority rows={len(human_priority_rows)}; assignments={len(human_assignment_rows)}; agreement rows={len(human_agreement_rows)}",
        ),
        (
            "Human validation annotator packets exist",
            len(human_packet_rows) == 6
            and all(exists(SUBMISSION_DIR / "human_validation_panels/annotator_packets" / row.get("packet_file", "")) for row in human_packet_rows)
            and sum(row.get("task") == "mapgenerator_caption_fidelity" and row.get("rows") == "20" for row in human_packet_rows) == 2
            and sum(row.get("task") == "choropleth_cartographic_quality" and row.get("rows") == "18" for row in human_packet_rows) == 2
            and sum(row.get("task") == "mixed_assignment_sheet" and row.get("rows") == "38" for row in human_packet_rows) == 2,
            f"packet rows={len(human_packet_rows)}",
        ),
        (
            "Human validation packet preflight passes",
            exists(human_packet_preflight_report)
            and len(human_packet_preflight_rows) == 4
            and all(row.get("status") == "pass" for row in human_packet_preflight_rows)
            and all(row.get("missing_artifacts") == "0" for row in human_packet_preflight_rows)
            and all(row.get("invalid_values") == "0" for row in human_packet_preflight_rows),
            f"preflight rows={len(human_packet_preflight_rows)}; passed={sum(row.get('status') == 'pass' for row in human_packet_preflight_rows)}",
        ),
        (
            "Human validation visual galleries exist",
            exists(mapgen_gallery)
            and exists(choro_gallery)
            and len(human_gallery_rows) == len(human_mapgen_rows) + len(human_choro_rows)
            and all(row.get("artifact_exists") == "True" for row in human_gallery_rows)
            and "/" + "Users/" not in mapgen_gallery.read_text(encoding="utf-8")
            and "/" + "Users/" not in choro_gallery.read_text(encoding="utf-8"),
            f"gallery rows={len(human_gallery_rows)}; missing artifacts={sum(row.get('artifact_exists') != 'True' for row in human_gallery_rows)}",
        ),
        (
            "Human validation execution plan exists",
            exists(human_execution_plan)
            and len(human_acceptance_rows) >= 7
            and len(human_file_contract_rows) >= 3
            and "Manuscript Update Trigger" in human_execution_plan.read_text(encoding="utf-8"),
            f"acceptance criteria={len(human_acceptance_rows)}; file contracts={len(human_file_contract_rows)}",
        ),
        ("Evaluator adjudication ledgers exist", len(adjudication_rows) == 2 and len(mapgen_adjudication_rows) == 20 and len(choro_adjudication_rows) == 18, f"summary={len(adjudication_rows)}; MapGenerator={len(mapgen_adjudication_rows)}; choropleth={len(choro_adjudication_rows)}"),
        (
            "VLM judge robustness audit exists",
            len(vlm_judge_rows) >= 5
            and sum(row.get("Panel role") == "agreement_panel" for row in vlm_judge_rows) >= 4
            and any(row.get("Panel role") == "failed_candidate" for row in vlm_judge_rows),
            f"models={len(vlm_judge_rows)}; agreement={sum(row.get('Panel role') == 'agreement_panel' for row in vlm_judge_rows)}",
        ),
        (
            "Calibrated multi-judge VLM consensus exists",
            len(multijudge_rows) == 2
            and len(mapgen_multijudge_rows) == 20
            and len(choro_multijudge_rows) == 18
            and all(int(row.get("Items with at least two usable judges", "0")) >= 18 for row in multijudge_rows),
            f"summary={len(multijudge_rows)}; MapGenerator={len(mapgen_multijudge_rows)}; choropleth={len(choro_multijudge_rows)}",
        ),
        (
            "Cross-paradigm reliability matrix exists",
            len(cross_paradigm_rows) == 21
            and len(cross_paradigm_summary_rows) == 3
            and {row.get("Paradigm") for row in cross_paradigm_summary_rows}
            == {"Text-to-map image data", "Remote-sensing-to-map tiles", "LLM-generated choropleth maps"},
            f"matrix rows={len(cross_paradigm_rows)}; summary rows={len(cross_paradigm_summary_rows)}",
        ),
        (
            "RQ-to-evidence map and objective audit exist",
            len(rq_evidence_rows) == 5
            and len(objective_completion_rows) >= 7
            and all(row.get("Status") == "evidence_present" for row in objective_completion_rows),
            f"RQs={len(rq_evidence_rows)}; objective rows={len(objective_completion_rows)}",
        ),
        (
            "Goal completion audit distinguishes track evidence from open gates",
            exists(goal_completion_audit_report)
            and len(goal_completion_rows) >= 8
            and any(row.get("requirement_id") == "R08" for row in goal_completion_rows)
            and any(row.get("verification_status") == "track_evidence_present_manual_gate_open" for row in goal_completion_rows)
            and all(row.get("authoritative_evidence") for row in goal_completion_rows)
            and "keep active until all manual/external Q1 gates are closed" in goal_completion_audit_report.read_text(encoding="utf-8"),
            f"goal rows={len(goal_completion_rows)}; open={sum(row.get('verification_status') != 'proven_for_manuscript_track' for row in goal_completion_rows)}",
        ),
        (
            "Claim-to-evidence crosswalk exists",
            exists(claim_evidence_crosswalk_report)
            and len(claim_evidence_rows) >= 7
            and all(row.get("reviewer_caveat") for row in claim_evidence_rows)
            and all(row.get("do_not_overclaim") for row in claim_evidence_rows),
            f"claims={len(claim_evidence_rows)}",
        ),
        (
            "Q1 submission gate tracker exists",
            exists(q1_gate_tracker_report)
            and len(q1_gate_rows) >= 9
            and all(row.get("closure_criterion") and row.get("overclaim_guard") for row in q1_gate_rows)
            and any(row.get("gate") == "MapGenerator human caption-fidelity labels" for row in q1_gate_rows)
            and any(row.get("gate") == "Official/cascade-conditioned SCGM reproduction" for row in q1_gate_rows)
            and any(row.get("gate") == "Final DOI/archive deposit" for row in q1_gate_rows)
            and any(row.get("gate") == "Final top-level license decision" for row in q1_gate_rows),
            f"gates={len(q1_gate_rows)}",
        ),
        (
            "Reviewer prebuttal audit exists",
            exists(reviewer_prebuttal_report)
            and len(reviewer_prebuttal_rows) >= 8
            and all(row.get("prebuttal_response") and row.get("overclaim_guard") for row in reviewer_prebuttal_rows)
            and any("VLM" in row.get("likely_reviewer_objection", "") for row in reviewer_prebuttal_rows)
            and any("SCGM" in row.get("likely_reviewer_objection", "") for row in reviewer_prebuttal_rows)
            and any("releasable" in row.get("likely_reviewer_objection", "") for row in reviewer_prebuttal_rows),
            f"risks={len(reviewer_prebuttal_rows)}",
        ),
        ("Human validation label summarizer status exists", exists(human_label_summary), ""),
        (
            "Human validation metric summarizer is acceptance-criteria ready",
            exists(human_metric_summary)
            and len(human_metric_rows) == 2
            and {row.get("task") for row in human_metric_rows}
            == {"mapgenerator_caption_fidelity", "choropleth_cartographic_quality"}
            and all("cohen_style_kappa" in row for row in human_metric_rows)
            and any(
                row.get("task") == "mapgenerator_caption_fidelity"
                and row.get("urgent_items") == "17"
                and row.get("status") == "no_labels_collected"
                for row in human_metric_rows
            )
            and any(
                row.get("task") == "choropleth_cartographic_quality"
                and row.get("urgent_items") == "5"
                and row.get("status") == "no_labels_collected"
                for row in human_metric_rows
            ),
            f"metric rows={len(human_metric_rows)}",
        ),
        (
            "Human validation adjudication queue is final-label ready",
            exists(human_adjudication_report)
            and len(human_adjudication_rows) == len(human_priority_rows)
            and len(human_final_label_rows) == len(human_priority_rows)
            and len(human_adjudication_summary_rows) == 2
            and any(
                row.get("task") == "mapgenerator_caption_fidelity"
                and row.get("priority_items") == "20"
                and row.get("urgent_items") == "17"
                and row.get("urgent_missing_labels") == "17"
                and row.get("final_ready") == "0"
                for row in human_adjudication_summary_rows
            )
            and any(
                row.get("task") == "choropleth_cartographic_quality"
                and row.get("priority_items") == "18"
                and row.get("urgent_items") == "5"
                and row.get("urgent_missing_labels") == "5"
                and row.get("final_ready") == "0"
                for row in human_adjudication_summary_rows
            )
            and "does not invent labels" in human_adjudication_report.read_text(encoding="utf-8"),
            f"queue rows={len(human_adjudication_rows)}; summary rows={len(human_adjudication_summary_rows)}; final rows={len(human_final_label_rows)}",
        ),
        (
            "Human validation final-label reducer preserves open claim gate",
            exists(human_final_label_report)
            and len(human_final_ledger_rows) == len(human_priority_rows)
            and len(human_final_summary_rows) == 2
            and any(
                row.get("task") == "mapgenerator_caption_fidelity"
                and row.get("total_items") == "20"
                and row.get("urgent_items") == "17"
                and row.get("final_labels") == "0"
                and row.get("urgent_final_labels") == "0"
                and row.get("status") == "no_final_labels_collected"
                for row in human_final_summary_rows
            )
            and any(
                row.get("task") == "choropleth_cartographic_quality"
                and row.get("total_items") == "18"
                and row.get("urgent_items") == "5"
                and row.get("final_labels") == "0"
                and row.get("urgent_final_labels") == "0"
                and row.get("status") == "no_final_labels_collected"
                for row in human_final_summary_rows
            )
            and "Do not replace VLM/CLIP screening caveats" in human_final_label_report.read_text(encoding="utf-8"),
            f"final ledger rows={len(human_final_ledger_rows)}; summary rows={len(human_final_summary_rows)}",
        ),
        ("Submission package audit exists", exists(package_audit), ""),
        ("Manuscript numerical consistency audit passes", exists(consistency_audit) and "TODO" not in consistency_audit.read_text(encoding="utf-8"), ""),
        (
            "Main/supplement split and page-budget audit exist",
            exists(page_budget_audit)
            and len([row for row in split_rows if row["artifact_type"] == "table" and row["placement"] == "main_text"]) == 7
            and len([row for row in split_rows if row["artifact_type"] == "figure" and row["placement"] == "main_text"]) == 5
            and "Compression Actions Before Submission" in page_budget_audit.read_text(encoding="utf-8"),
            f"split rows={len(split_rows)}",
        ),
        (
            "Main-text compression plan exists",
            exists(main_text_compression_plan)
            and len(word_budget_rows) >= 10
            and len([row for row in compact_display_rows if row["artifact_type"] == "table" and row["compact_placement"] == "main_text"]) == 6
            and len([row for row in compact_display_rows if row["artifact_type"] == "figure" and row["compact_placement"] == "main_text"]) == 4
            and "Estimated pages low/mid/high: 23.7/27.4/32.2" in main_text_compression_plan.read_text(encoding="utf-8"),
            f"word budget rows={len(word_budget_rows)}; compact display rows={len(compact_display_rows)}",
        ),
        (
            "Compact main manuscript draft exists",
            exists(compact_main_manuscript)
            and 8500 <= word_count(compact_main_manuscript) <= 10500
            and "## 10. Conclusion" in compact_main_manuscript.read_text(encoding="utf-8")
            and "## 9. Additional Strengthening Experiments" not in compact_main_manuscript.read_text(encoding="utf-8"),
            f"{word_count(compact_main_manuscript) if compact_main_manuscript.exists() else 0} words",
        ),
        (
            "LaTeX submission package compiles to PDF",
            exists(latex_main)
            and exists(latex_pdf)
            and exists(latex_bib)
            and exists(latex_readme)
            and exists(latex_build_log)
            and exists(latex_interact_cls)
            and exists(latex_tfv_bst)
            and (
                "Output written on main.pdf" in latex_build_log.read_text(encoding="utf-8", errors="replace")
                or "All targets (main.pdf) are up-to-date" in latex_build_log.read_text(encoding="utf-8", errors="replace")
            )
            and "Anonymous author(s)" in latex_text
            and r"\documentclass[]{interact}" in latex_text
            and r"\bibliographystyle{tfv}" in latex_text
            and latex_figure_count >= 10
            and latex_table_count >= 5,
            f"pdf_bytes={latex_pdf.stat().st_size if latex_pdf.exists() else 0}; figures={latex_figure_count}; tables={latex_table_count}",
        ),
        (
            "Submission abstract/significance/keyword pack exists",
            exists(abstract_pack)
            and len(abstract_field_rows) >= 8
            and 150 <= short_abstract_words <= 250
            and keyword_count >= 5
            and exists(abstract_pack)
            and "Significance statement" in abstract_pack.read_text(encoding="utf-8"),
            f"short abstract words={short_abstract_words}; keywords={keyword_count}",
        ),
        ("Manuscript tables generated", len(table_files) >= 25, f"{len(table_files)} table CSV files"),
        ("Figure index populated", figure_count >= 9, f"{figure_count} indexed figures"),
        ("MapGenerator VLM pilot table populated", sum(int(row["Reviewed"]) for row in table15) >= 20, f"{sum(int(row['Reviewed']) for row in table15)} reviewed pairs"),
        ("MapGenerator two-VLM agreement table populated", any(row["Scope"] == "overall" and row["Paired items"] == "20" for row in table15b), "20 paired caption reviews"),
        ("MapGenerator CLIP/SigLIP scoring completed", embedding_summary.get("status") == "completed" and embedding_summary.get("scored_pairs", 0) >= 200 and embedding_summary.get("errors", 1) == 0, f"status={embedding_summary.get('status', 'missing')}; scored={embedding_summary.get('scored_pairs', 0)}; errors={embedding_summary.get('errors', 'missing')}"),
        ("Choropleth VLM visual pilot populated", sum(int(row["Reviewed"]) for row in table18) >= 18, f"{sum(int(row['Reviewed']) for row in table18)} reviewed artifacts"),
        ("Choropleth two-VLM agreement table populated", any(row["Scope"] == "overall" and row["Paired artifacts"] == "18" for row in table18b), "18 paired visual reviews"),
        ("Screenshot QA includes validator/reference passes", any(row["Source"] == "validator_repair_reference" and int(row["Screenshot QA pass"]) > 0 for row in table16), ""),
        ("SCGM compact neural MLP baseline populated", scgm_mlp_summary.get("validation_outputs") == 100, f"{scgm_mlp_summary.get('validation_outputs', 0)} validation outputs"),
        ("SCGM local-context image baseline populated", scgm_local_ridge_summary.get("validation_outputs") == 100, f"{scgm_local_ridge_summary.get('validation_outputs', 0)} validation outputs"),
        ("SCGM convolutional filter-bank image baseline populated", scgm_conv_ridge_summary.get("validation_outputs") == 100 and scgm_conv_ridge_summary.get("input_feature_dimension", 0) >= 50, f"{scgm_conv_ridge_summary.get('validation_outputs', 0)} validation outputs; features={scgm_conv_ridge_summary.get('input_feature_dimension', 0)}"),
        ("SCGM patch-embedding retrieval baseline populated", scgm_patch_summary.get("validation_outputs") == 100 and scgm_patch_summary.get("patch_bank_size", 0) >= 10000, f"{scgm_patch_summary.get('validation_outputs', 0)} validation outputs; patch bank={scgm_patch_summary.get('patch_bank_size', 0)}"),
        ("SCGM trained tiny-CNN baseline populated", scgm_tiny_cnn_summary.get("status") == "completed" and scgm_tiny_cnn_summary.get("validation_outputs") == 100 and scgm_tiny_cnn_summary.get("model_family") == "trained_cnn", f"{scgm_tiny_cnn_summary.get('validation_outputs', 0)} validation outputs; final loss={scgm_tiny_cnn_summary.get('training_loss_final', 'missing')}"),
        (
            "SCGM mosaic neighbor-seam stress audit populated",
            len(scgm_mosaic_summary) == 8
            and all(int(row.get("neighbor_pairs_available", 0)) >= 12 for row in scgm_mosaic_summary)
            and exists(ROOT / "experiments/03_scgm_subset_reproduction/outputs/scgm_mosaic_neighbor_stress_pairs.csv"),
            f"baselines={len(scgm_mosaic_summary)}; pairs={sum(int(row.get('neighbor_pairs_available', 0)) for row in scgm_mosaic_summary)}",
        ),
        (
            "SCGM official reproduction contract exists",
            exists(scgm_official_contract)
            and len(scgm_runtime_rows) >= 7
            and len(scgm_config_rows) >= 2
            and len(scgm_command_rows) >= 3
            and exists(scgm_contract_environment)
            and all(row.get("subset_reference_status") == "ready" for row in scgm_config_rows)
            and any(row.get("status") == "external_blocker" for row in scgm_runtime_rows),
            f"runtime rows={len(scgm_runtime_rows)}; config rows={len(scgm_config_rows)}; commands={len(scgm_command_rows)}",
        ),
        (
            "SCGM official local overrides close dataroot and datalist prep",
            exists(scgm_local_override_report)
            and len(scgm_local_override_rows) == 5
            and all(row.get("status") == "ready" for row in scgm_local_override_rows)
            and any(row.get("artifact") == "bridge_datalist" and "rows=200" in row.get("evidence", "") for row in scgm_local_override_rows)
            and any(row.get("artifact") == "2c_local_data_config" for row in scgm_local_override_rows)
            and any(row.get("artifact") == "4c_local_data_config" for row in scgm_local_override_rows)
            and "do not supply model checkpoints" in scgm_local_override_report.read_text(encoding="utf-8"),
            f"override rows={len(scgm_local_override_rows)}; ready={sum(row.get('status') == 'ready' for row in scgm_local_override_rows)}",
        ),
        (
            "SCGM official-reproduction readiness audit exists",
            exists(scgm_official_audit_report)
            and len(scgm_official_rows) >= 10
            and any(row.get("component") == "official_weights_or_checkpoints" and row.get("status") == "blocking_gap" for row in scgm_official_rows)
            and any(row.get("component") == "official_run_contract" and row.get("status") == "contract_drafted" for row in scgm_official_rows)
            and any(row.get("component") == "current_generated_output_diagnostics" and row.get("status") == "present" for row in scgm_official_rows)
            and "should not claim official SCGM reproduction yet" in scgm_official_audit_report.read_text(encoding="utf-8"),
            f"components={len(scgm_official_rows)}; blocking={sum(row.get('status') in {'blocking_gap', 'missing', 'not_yet_run'} for row in scgm_official_rows)}",
        ),
        (
            "SCGM official feasibility probe localizes runtime and config blockers",
            exists(scgm_feasibility_probe_report)
            and len(scgm_probe_rows) == 15
            and any(row.get("check_id") == "runtime_imports" and row.get("status") == "blocking_gap" for row in scgm_probe_rows)
            and any(row.get("check_id") == "complete_reference_subset" and row.get("status") == "pass" for row in scgm_probe_rows)
            and sum(row.get("layer") == "checkpoint" and row.get("status") == "blocking_gap" for row in scgm_probe_rows) == 2
            and sum(row.get("check_id", "").endswith("_dataroot") and row.get("status") == "pass" for row in scgm_probe_rows) == 2
            and sum(row.get("check_id", "").endswith("_datalist") and row.get("status") == "pass" for row in scgm_probe_rows) == 2
            and sum(row.get("check_id", "").endswith("_cascade_path") and row.get("status") == "pass" for row in scgm_probe_rows) == 2
            and sum(row.get("check_id", "").endswith("_planned_outputs") and row.get("status") == "blocking_gap" for row in scgm_probe_rows) == 2
            and "official SCGM reproduction is not locally runnable yet" in scgm_feasibility_probe_report.read_text(encoding="utf-8"),
            f"probe rows={len(scgm_probe_rows)}; blocking={sum(row.get('status') == 'blocking_gap' for row in scgm_probe_rows)}; warnings={sum(row.get('status') == 'warning' for row in scgm_probe_rows)}",
        ),
        (
            "Iterative repair sweep covers all incomplete one-pass repairs",
            iterative_summary.get("cases") == 40 and len(table19) == 40,
            f"{iterative_summary.get('completed_cases')}/{iterative_summary.get('cases')} complete; table rows={len(table19)}",
        ),
        ("Repair-model comparison pilot table populated", all(any(row.get("Repair model") == model for row in table20) for model in {"qwen2.5-coder:14b", "qwen2.5-coder:7b", "deepseek-coder:6.7b"}), f"{len(table20)} model rows"),
        ("Matched repair-model suite populated", len(matched_repair_rows) == 3 and len(matched_repair_ledger_rows) == 24 and all(row.get("Matched cases") == "8" for row in matched_repair_rows), f"models={len(matched_repair_rows)}; ledger rows={len(matched_repair_ledger_rows)}"),
        ("Iterative repair attempts are safety-scanned", iterative_summary.get("safe_attempts") == iterative_summary.get("attempt_rows"), f"{iterative_summary.get('safe_attempts')}/{iterative_summary.get('attempt_rows')} safe"),
    ]

    remaining = [
        "Just-in-time publisher/Crossref citation recheck immediately before submission.",
        "Journal-specific formatting and native reference style.",
        "Human labels for MapGenerator caption fidelity beyond the current calibrated VLM consensus and CLIP screening layer.",
        "Human labels for choropleth visual quality beyond the current calibrated VLM consensus.",
        "Official or cascade-conditioned SCGM diffusion-style reproduction beyond the current retrieval/forest/MLP/local-context/convolutional-filter/patch/tiny-CNN diagnostics.",
        "Create final DOI/public repository immediately before submission.",
        "Final journal-target recheck immediately before portal upload; dated 2026-06-24 source-confidence ledger is present, but quartile/route status remains category- and database-dependent.",
    ]

    lines = [
        "# Manuscript Readiness Audit",
        "",
        "This report is generated from local manuscript and experiment artifacts.",
        "",
        "## Automated Checks",
        "",
        "| Gate | Status | Evidence |",
        "|---|---|---|",
    ]
    for name, ok, evidence in checks:
        lines.append(f"| {name} | {status(ok)} | {evidence} |")
    lines += [
        "",
        "## Remaining Manual/Q1 Gates",
        "",
    ]
    lines.extend(f"- {item}" for item in remaining)
    lines += [
        "",
        "## Overall",
        "",
        f"- Automated gates passed: {sum(ok for _, ok, _ in checks)}/{len(checks)}",
        "- Status: strong manuscript track, not final submission-ready until the manual/Q1 gates above are closed.",
        "",
    ]
    out = NOTES_DIR / "manuscript_readiness_audit.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
