#!/usr/bin/env python3
"""Write a compact manuscript status dashboard from current artifacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MS_DIR = ROOT / "manuscripts/q1_geo_genai_reliability"
OUT = MS_DIR / "notes/status_dashboard.md"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def word_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").split())


def main() -> None:
    draft = MS_DIR / "draft/manuscript_draft.md"
    condition_rows = read_csv(MS_DIR / "tables/table_10_expanded_choropleth_condition_summary.csv")
    model_rows = read_csv(MS_DIR / "tables/table_13_choropleth_model_mode_summary.csv")
    mapgen_rows = read_csv(MS_DIR / "tables/table_09_mapgenerator_proxy_caption_review.csv")
    mapgen_vlm_rows = read_csv(MS_DIR / "tables/table_15_mapgenerator_vlm_caption_review.csv")
    mapgen_vlm_agreement = read_csv(MS_DIR / "tables/table_15b_mapgenerator_vlm_agreement.csv")
    mapgen_embedding_path = ROOT / "experiments/02_mapgenerator_image_text_audit/outputs/mapgenerator_clip_caption_embedding_summary.json"
    mapgen_embedding = json.loads(mapgen_embedding_path.read_text()) if mapgen_embedding_path.exists() else {}
    scgm = json.loads((ROOT / "experiments/03_scgm_subset_reproduction/outputs/scgm_retrieval_baseline_summary.json").read_text())
    scgm_multi = json.loads((ROOT / "experiments/03_scgm_subset_reproduction/outputs/scgm_multifeature_retrieval_summary.json").read_text())
    scgm_forest = json.loads((ROOT / "experiments/03_scgm_subset_reproduction/outputs/scgm_learned_forest_summary.json").read_text())
    scgm_mlp = json.loads((ROOT / "experiments/03_scgm_subset_reproduction/outputs/scgm_mlp_summary.json").read_text())
    scgm_local_ridge = json.loads((ROOT / "experiments/03_scgm_subset_reproduction/outputs/scgm_local_context_ridge_summary.json").read_text())
    scgm_conv_ridge = json.loads((ROOT / "experiments/03_scgm_subset_reproduction/outputs/scgm_convolutional_filter_ridge_summary.json").read_text())
    scgm_patch = json.loads((ROOT / "experiments/03_scgm_subset_reproduction/outputs/scgm_patch_embedding_retrieval_summary.json").read_text())
    scgm_tiny_cnn = json.loads((ROOT / "experiments/03_scgm_subset_reproduction/outputs/scgm_tiny_cnn_summary.json").read_text())
    scgm_mosaic = json.loads((ROOT / "experiments/03_scgm_subset_reproduction/outputs/scgm_mosaic_neighbor_stress_summary.json").read_text())
    choropleth_reference = read_csv(MS_DIR / "tables/table_12_reference_choropleth_baseline.csv")
    artifact_qa = read_csv(MS_DIR / "tables/table_14_rendered_artifact_qa_summary.csv")
    screenshot_qa = read_csv(MS_DIR / "tables/table_16_screenshot_level_choropleth_qa.csv")
    choropleth_vlm = read_csv(MS_DIR / "tables/table_18_choropleth_vlm_cartographic_review.csv")
    choropleth_vlm_agreement = read_csv(MS_DIR / "tables/table_18b_choropleth_vlm_agreement.csv")
    iterative_repair = read_csv(MS_DIR / "tables/table_19_iterative_validator_repair.csv")
    repair_comparison = read_csv(MS_DIR / "tables/table_20_iterative_repair_model_comparison.csv")
    matched_repair_suite_path = MS_DIR / "submission/repair_model_suite/matched_repair_model_summary.csv"
    matched_repair_suite = read_csv(matched_repair_suite_path) if matched_repair_suite_path.exists() else []
    figure_lines = (MS_DIR / "figures/figure_index.md").read_text(encoding="utf-8").splitlines()
    figure_count = sum(line.startswith("| Figure ") and not line.startswith("| Figure |") for line in figure_lines)
    blinded = MS_DIR / "submission/blinded_main_manuscript.md"
    blinded_compact = MS_DIR / "submission/blinded_compact_main_manuscript.md"
    supplement_manifest = MS_DIR / "submission/supplementary_material_manifest.md"
    ijgis_compliance = MS_DIR / "submission/ijgis_compliance_checklist.md"
    journal_target_recheck = MS_DIR / "submission/journal_target_recheck_2026-06-24.md"
    journal_style_preflight_path = MS_DIR / "submission/journal_style_preflight/journal_style_preflight.csv"
    journal_style_preflight = read_csv(journal_style_preflight_path) if journal_style_preflight_path.exists() else []
    journal_style_automated = [row for row in journal_style_preflight if row.get("mode") == "automated"]
    release_plan = MS_DIR / "submission/reproducibility_release_plan.md"
    reproduction_runbook_path = MS_DIR / "submission/reproduction_runbook_commands.csv"
    reproduction_runbook = read_csv(reproduction_runbook_path) if reproduction_runbook_path.exists() else []
    release_preflight_path = MS_DIR / "submission/release_preflight/release_preflight_checks.csv"
    release_preflight = read_csv(release_preflight_path) if release_preflight_path.exists() else []
    release_preflight_automated = [row for row in release_preflight if row.get("mode") == "automated"]
    release_license_matrix_path = MS_DIR / "submission/release_license_audit/release_license_matrix.csv"
    release_license_matrix = read_csv(release_license_matrix_path) if release_license_matrix_path.exists() else []
    public_release_file_map_path = MS_DIR / "submission/public_release_skeleton/RELEASE_FILE_MAP.csv"
    public_release_manifest_summary_path = MS_DIR / "submission/public_release_skeleton/release_manifest_summary.csv"
    public_release_file_map = read_csv(public_release_file_map_path) if public_release_file_map_path.exists() else []
    public_release_manifest_summary = read_csv(public_release_manifest_summary_path) if public_release_manifest_summary_path.exists() else []
    reproducibility_manifest_path = MS_DIR / "submission/reproducibility_manifest.csv"
    reproducibility_manifest = read_csv(reproducibility_manifest_path) if reproducibility_manifest_path.exists() else []
    data_sources = MS_DIR / "submission/DATA_SOURCES.md"
    environment_file = MS_DIR / "submission/environment_minimal.yml"
    optional_embedding_environment = MS_DIR / "submission/environment_optional_embedding.yml"
    citation_metadata = MS_DIR / "submission/citation_metadata.csv"
    references_bib = MS_DIR / "submission/references.bib"
    citation_ledger = MS_DIR / "notes/citation_metadata_ledger.md"
    citation_verification_path = MS_DIR / "submission/citation_verification_report.csv"
    citation_verification = read_csv(citation_verification_path) if citation_verification_path.exists() else []
    human_mapgen_panel = MS_DIR / "submission/human_validation_panels/mapgenerator_caption_human_panel.csv"
    human_choro_panel = MS_DIR / "submission/human_validation_panels/choropleth_cartographic_human_panel.csv"
    human_rubric = MS_DIR / "submission/human_validation_panels/human_validation_rubric.json"
    human_priority_queue_path = MS_DIR / "submission/human_validation_panels/human_validation_priority_queue.csv"
    human_priority_queue = read_csv(human_priority_queue_path) if human_priority_queue_path.exists() else []
    human_gallery_index_path = MS_DIR / "submission/human_validation_panels/human_validation_gallery_index.csv"
    human_gallery_index = read_csv(human_gallery_index_path) if human_gallery_index_path.exists() else []
    human_assignment_sheet_path = MS_DIR / "submission/human_validation_panels/human_validation_assignment_sheet.csv"
    human_assignment_sheet = read_csv(human_assignment_sheet_path) if human_assignment_sheet_path.exists() else []
    human_packet_manifest_path = MS_DIR / "submission/human_validation_panels/human_validation_annotator_packet_manifest.csv"
    human_packet_manifest = read_csv(human_packet_manifest_path) if human_packet_manifest_path.exists() else []
    human_packet_preflight_path = MS_DIR / "submission/human_validation_panels/preflight/human_validation_packet_preflight.csv"
    human_packet_preflight = read_csv(human_packet_preflight_path) if human_packet_preflight_path.exists() else []
    human_acceptance_criteria_path = MS_DIR / "submission/human_validation_panels/human_validation_acceptance_criteria.csv"
    human_acceptance_criteria = read_csv(human_acceptance_criteria_path) if human_acceptance_criteria_path.exists() else []
    human_file_contract_path = MS_DIR / "submission/human_validation_panels/human_validation_file_contract.csv"
    human_file_contract = read_csv(human_file_contract_path) if human_file_contract_path.exists() else []
    human_execution_plan = MS_DIR / "submission/human_validation_panels/human_validation_execution_plan.md"
    human_label_summary = MS_DIR / "submission/human_validation_panels/summaries/human_validation_label_summary.md"
    human_metric_summary_path = MS_DIR / "submission/human_validation_panels/summaries/human_validation_metric_summary.csv"
    human_metric_summary = read_csv(human_metric_summary_path) if human_metric_summary_path.exists() else []
    human_adjudication_summary_path = MS_DIR / "submission/human_validation_panels/summaries/human_validation_adjudication_summary.csv"
    human_adjudication_summary = read_csv(human_adjudication_summary_path) if human_adjudication_summary_path.exists() else []
    human_final_summary_path = MS_DIR / "submission/human_validation_panels/summaries/human_validation_final_label_summary.csv"
    human_final_summary = read_csv(human_final_summary_path) if human_final_summary_path.exists() else []
    evaluator_adjudication_summary_path = MS_DIR / "submission/human_validation_panels/summaries/evaluator_adjudication_summary.csv"
    evaluator_adjudication = read_csv(evaluator_adjudication_summary_path) if evaluator_adjudication_summary_path.exists() else []
    vlm_judge_robustness_path = MS_DIR / "submission/evaluator_reliability/vlm_judge_robustness_audit.csv"
    vlm_judge_robustness = read_csv(vlm_judge_robustness_path) if vlm_judge_robustness_path.exists() else []
    multijudge_consensus_path = MS_DIR / "submission/evaluator_reliability/multijudge_consensus_summary.csv"
    multijudge_consensus = read_csv(multijudge_consensus_path) if multijudge_consensus_path.exists() else []
    cross_paradigm_summary_path = MS_DIR / "submission/cross_paradigm/cross_paradigm_reliability_summary.csv"
    cross_paradigm_summary = read_csv(cross_paradigm_summary_path) if cross_paradigm_summary_path.exists() else []
    rq_evidence_map = MS_DIR / "submission/evidence_map/rq_evidence_map.csv"
    objective_completion_audit = MS_DIR / "submission/evidence_map/objective_completion_audit.csv"
    goal_completion_audit_path = MS_DIR / "submission/evidence_map/goal_completion_audit.csv"
    goal_completion_audit = read_csv(goal_completion_audit_path) if goal_completion_audit_path.exists() else []
    claim_evidence_crosswalk_path = MS_DIR / "submission/claim_evidence_crosswalk/claim_evidence_crosswalk.csv"
    claim_evidence_crosswalk = read_csv(claim_evidence_crosswalk_path) if claim_evidence_crosswalk_path.exists() else []
    q1_gate_tracker_path = MS_DIR / "submission/q1_submission_gate_tracker/q1_submission_gate_tracker.csv"
    q1_gate_tracker = read_csv(q1_gate_tracker_path) if q1_gate_tracker_path.exists() else []
    reviewer_prebuttal_path = MS_DIR / "submission/reviewer_prebuttal_audit/reviewer_prebuttal_audit.csv"
    reviewer_prebuttal = read_csv(reviewer_prebuttal_path) if reviewer_prebuttal_path.exists() else []
    scgm_official_audit_path = MS_DIR / "submission/scgm_official_reproduction_audit/scgm_official_reproduction_audit.csv"
    scgm_official_audit = read_csv(scgm_official_audit_path) if scgm_official_audit_path.exists() else []
    scgm_feasibility_probe_path = MS_DIR / "submission/scgm_official_reproduction_audit/scgm_official_feasibility_probe.csv"
    scgm_feasibility_probe = read_csv(scgm_feasibility_probe_path) if scgm_feasibility_probe_path.exists() else []
    scgm_official_contract_path = MS_DIR / "submission/scgm_official_reproduction_contract/scgm_official_config_mapping.csv"
    scgm_official_contract = read_csv(scgm_official_contract_path) if scgm_official_contract_path.exists() else []
    scgm_local_override_path = MS_DIR / "submission/scgm_official_reproduction_contract/local_overrides/scgm_official_local_override_manifest.csv"
    scgm_local_override = read_csv(scgm_local_override_path) if scgm_local_override_path.exists() else []
    consistency_audit = MS_DIR / "notes/manuscript_consistency_audit.md"
    page_budget_audit = MS_DIR / "notes/page_budget_audit.md"
    main_supplement_split = MS_DIR / "submission/main_supplement_split.csv"
    main_text_compression_plan = MS_DIR / "submission/main_text_compression_plan.md"
    compact_main_manuscript = MS_DIR / "submission/compact_main_manuscript.md"
    latex_main = MS_DIR / "submission/latex/main.tex"
    latex_pdf = MS_DIR / "submission/latex/main.pdf"
    latex_build_log = MS_DIR / "submission/latex/latex_build.log"
    latex_text = latex_main.read_text(encoding="utf-8") if latex_main.exists() else ""
    abstract_pack = MS_DIR / "submission/submission_abstract_pack.md"
    abstract_fields = MS_DIR / "submission/submission_abstract_fields.csv"

    initial_rows = [row for row in condition_rows if row["Condition"] == "initial" and row["Model"] != "validator_repair_reference"]
    repair_rows = [row for row in condition_rows if row["Condition"].startswith("repair_by_")]
    generated_model_rows = [row for row in model_rows if row["Model"] != "validator_repair_reference"]
    validator_rows = [row for row in model_rows if row["Model"] == "validator_repair_reference"]
    repair_complete = sum(
        float(row["Best score"]) >= 0.999 and row["Execution"] == "True"
        for row in repair_rows
    )
    initial_sources = {"deepseek-coder_6.7b", "qwen2.5-coder_7b"}
    repair_existing = sum(int(row["Existing"]) for row in artifact_qa if row["Source"].startswith("repair_"))
    initial_existing = sum(int(row["Existing"]) for row in artifact_qa if row["Source"] in initial_sources)
    screenshot_pass_by_source: dict[str, int] = {}
    for row in screenshot_qa:
        screenshot_pass_by_source[row["Source"]] = screenshot_pass_by_source.get(row["Source"], 0) + int(row["Screenshot QA pass"])
    mapgen_vlm_attempts = sum(int(row["Reviewed"]) for row in mapgen_vlm_rows)
    mapgen_vlm_errors = sum(int(row.get("Errors", 0)) for row in mapgen_vlm_rows)
    lines = [
        "# Manuscript Status Dashboard",
        "",
        f"- Draft word count: {word_count(draft)}",
        f"- Tables generated: {len(list((MS_DIR / 'tables').glob('table_*.csv')))}",
        f"- Figures indexed: {figure_count}",
        f"- Blinded submission manuscript: {'present' if blinded.exists() else 'missing'}.",
        f"- Blinded compact submission manuscript: {'present' if blinded_compact.exists() else 'missing'}.",
        f"- Supplementary material manifest: {'present' if supplement_manifest.exists() else 'missing'}.",
        f"- selected journal compliance checklist: {'present' if ijgis_compliance.exists() else 'missing'}.",
        f"- Dated journal-target source recheck: {'present' if journal_target_recheck.exists() else 'missing'}.",
        f"- Journal style preflight: {'present' if journal_style_preflight else 'missing'}; automated passed={sum(row.get('status') == 'pass' for row in journal_style_automated)}/{len(journal_style_automated)}.",
        f"- Reproducibility release plan: {'present' if release_plan.exists() else 'missing'}.",
        f"- Reproduction runbook: {'present' if reproduction_runbook else 'missing'}; commands={len(reproduction_runbook)}; required={sum(row.get('required') == 'yes' for row in reproduction_runbook)}.",
        f"- DOI/public repository release preflight: {'present' if release_preflight else 'missing'}; automated passed={sum(row.get('status') == 'pass' for row in release_preflight_automated)}/{len(release_preflight_automated)}.",
        f"- Release-license audit: {'present' if release_license_matrix else 'missing'}; rows={len(release_license_matrix)}.",
        f"- Public release skeleton: {'present' if public_release_file_map and public_release_manifest_summary else 'missing'}; file-map rows={len(public_release_file_map)}; summary rows={len(public_release_manifest_summary)}.",
        f"- Reproducibility checksum manifest: {'present' if reproducibility_manifest else 'missing'}; tracked artifacts={len(reproducibility_manifest)}.",
        f"- Data-source manifest: {'present' if data_sources.exists() else 'missing'}.",
        f"- Minimal environment manifest: {'present' if environment_file.exists() else 'missing'}.",
        f"- Optional embedding environment manifest: {'present' if optional_embedding_environment.exists() else 'missing'}.",
        f"- Citation metadata/BibTeX export: {'present' if citation_metadata.exists() and references_bib.exists() and citation_ledger.exists() else 'missing'}.",
        f"- Citation DOI/arXiv verification report: {'present' if citation_verification else 'missing'}.",
        f"- Human validation panels and rubric: {'present' if human_mapgen_panel.exists() and human_choro_panel.exists() and human_rubric.exists() else 'missing'}.",
        f"- Human validation packet: {'present' if human_priority_queue and human_assignment_sheet else 'missing'}; priority rows={len(human_priority_queue)}; assignments={len(human_assignment_sheet)}.",
        f"- Human validation annotator packets: {'present' if human_packet_manifest else 'missing'}; packet files={len(human_packet_manifest)}.",
        f"- Human validation packet preflight: {'present' if human_packet_preflight else 'missing'}; passed={sum(row.get('status') == 'pass' for row in human_packet_preflight)}/{len(human_packet_preflight)}.",
        f"- Human validation visual galleries: {'present' if human_gallery_index else 'missing'}; gallery rows={len(human_gallery_index)}; missing artifacts={sum(row.get('artifact_exists') != 'True' for row in human_gallery_index)}.",
        f"- Human validation execution plan: {'present' if human_execution_plan.exists() and human_acceptance_criteria and human_file_contract else 'missing'}; criteria={len(human_acceptance_criteria)}; file contracts={len(human_file_contract)}.",
        f"- Human validation label summary: {'present' if human_label_summary.exists() else 'missing'}.",
        f"- Human validation metric summary: {'present' if human_metric_summary else 'missing'}; rows={len(human_metric_summary)}; urgent closure={', '.join(row.get('task', '') + '=' + row.get('urgent_items_with_two_labels', '0') + '/' + row.get('urgent_items', '0') for row in human_metric_summary) if human_metric_summary else 'missing'}.",
        f"- Human validation adjudication queue: {'present' if human_adjudication_summary else 'missing'}; tasks={len(human_adjudication_summary)}; urgent final ready={', '.join(row.get('task', '') + '=' + row.get('urgent_final_ready', '0') + '/' + row.get('urgent_items', '0') for row in human_adjudication_summary) if human_adjudication_summary else 'missing'}.",
        f"- Human validation final label summary: {'present' if human_final_summary else 'missing'}; tasks={len(human_final_summary)}; final labels={', '.join(row.get('task', '') + '=' + row.get('final_labels', '0') + '/' + row.get('total_items', '0') for row in human_final_summary) if human_final_summary else 'missing'}.",
        f"- Evaluator adjudication summary: {'present' if evaluator_adjudication else 'missing'}.",
        f"- VLM judge robustness audit: {'present' if vlm_judge_robustness else 'missing'}.",
        f"- Calibrated multi-judge VLM consensus: {'present' if multijudge_consensus else 'missing'}.",
        f"- Cross-paradigm reliability matrix: {'present' if cross_paradigm_summary else 'missing'}.",
        f"- RQ-to-evidence map and objective audit: {'present' if rq_evidence_map.exists() and objective_completion_audit.exists() else 'missing'}.",
        f"- Goal completion audit: {'present' if goal_completion_audit else 'missing'}; requirements={len(goal_completion_audit)}; open/manual={sum(row.get('verification_status') != 'proven_for_manuscript_track' for row in goal_completion_audit)}.",
        f"- Claim-to-evidence crosswalk: {'present' if claim_evidence_crosswalk else 'missing'}; claims={len(claim_evidence_crosswalk)}.",
        f"- Q1 submission gate tracker: {'present' if q1_gate_tracker else 'missing'}; gates={len(q1_gate_tracker)}; open={sum(row.get('status', '').startswith('open') for row in q1_gate_tracker)}.",
        f"- Reviewer prebuttal audit: {'present' if reviewer_prebuttal else 'missing'}; risks={len(reviewer_prebuttal)}.",
        f"- SCGM official reproduction contract: {'present' if scgm_official_contract else 'missing'}; mapped runs={len(scgm_official_contract)}; ready subsets={sum(row.get('subset_reference_status') == 'ready' for row in scgm_official_contract)}.",
        f"- SCGM official local overrides: {'present' if scgm_local_override else 'missing'}; artifacts={len(scgm_local_override)}; ready={sum(row.get('status') == 'ready' for row in scgm_local_override)}.",
        f"- SCGM official-reproduction readiness audit: {'present' if scgm_official_audit else 'missing'}; components={len(scgm_official_audit)}; blocking={sum(row.get('status') in {'blocking_gap', 'missing', 'not_yet_run'} for row in scgm_official_audit)}.",
        f"- SCGM official feasibility probe: {'present' if scgm_feasibility_probe else 'missing'}; checks={len(scgm_feasibility_probe)}; blocking={sum(row.get('status') == 'blocking_gap' for row in scgm_feasibility_probe)}; warnings={sum(row.get('status') == 'warning' for row in scgm_feasibility_probe)}.",
        f"- Manuscript numerical consistency audit: {'pass' if consistency_audit.exists() and 'TODO' not in consistency_audit.read_text(encoding='utf-8') else 'missing_or_todo'}.",
        f"- Main/supplement split and page-budget audit: {'present' if page_budget_audit.exists() and main_supplement_split.exists() else 'missing'}.",
        f"- Main-text compression plan: {'present' if main_text_compression_plan.exists() else 'missing'}.",
        f"- Compact main manuscript draft: {'present' if compact_main_manuscript.exists() else 'missing'}.",
        f"- LaTeX submission package: {'present' if latex_main.exists() and latex_pdf.exists() else 'missing'}; compile={'pass' if latex_build_log.exists() and ('Output written on main.pdf' in latex_build_log.read_text(encoding='utf-8', errors='replace') or 'All targets (main.pdf) are up-to-date' in latex_build_log.read_text(encoding='utf-8', errors='replace')) else 'missing_or_fail'}; figures={latex_text.count(chr(92) + 'begin{figure}')}; tables={latex_text.count(chr(92) + 'begin{table}')}.",
        f"- Submission abstract/significance/keyword pack: {'present' if abstract_pack.exists() and abstract_fields.exists() else 'missing'}.",
        "",
        "## Current Submission Track",
        "",
        "- Primary submission venue: selected venue.",
        "- Special issue opportunity: `Critical Challenges in GeoAI`.",
        "- Abstract deadline: 01 August 2026.",
        "- Full manuscript deadline: 01 December 2026.",
        "- Target pack: `notes/ijgis_submission_target_pack.md`.",
        "- Dated source recheck: `submission/journal_target_recheck_2026-06-24.md`.",
        "- Draft special-issue abstract: `notes/ijgis_special_issue_abstract.md`.",
        "- Submission abstract pack: `submission/submission_abstract_pack.md`.",
        "",
        "## Current Evidence",
        "",
        f"- MapGenerator proxy review: {sum(int(row['Reviewed']) for row in mapgen_rows)} sampled pairs.",
        f"- Citation verification: {sum(row.get('verification_status') == 'verified' for row in citation_verification)} metadata verified; {sum(row.get('verification_status') == 'resolver_verified' for row in citation_verification)} DOI-resolver verified; {sum(row.get('verification_status') == 'publisher_url_verified' for row in citation_verification)} publisher-URL verified.",
        f"- MapGenerator VLM pilot review: {mapgen_vlm_attempts} review attempts across {len(set(row['Model'] for row in mapgen_vlm_rows))} local VLMs; non-error reviews={mapgen_vlm_attempts - mapgen_vlm_errors}.",
        f"- MapGenerator two-VLM paired agreement: {next(row['Exact verdict agreement'] for row in mapgen_vlm_agreement if row['Scope'] == 'overall')} exact verdict agreement; {next(row['Feature agreement'] for row in mapgen_vlm_agreement if row['Scope'] == 'overall')} feature agreement.",
        f"- MapGenerator evaluator adjudication queue: {next((row['Urgent human adjudication'] for row in evaluator_adjudication if row['Task'] == 'MapGenerator caption fidelity'), 'missing')} urgent human-adjudication cases.",
        f"- MapGenerator CLIP/SigLIP-style embedding scoring: status={mapgen_embedding.get('status', 'missing')}; scored pairs={mapgen_embedding.get('scored_pairs', 0)}; mean score={mapgen_embedding.get('mean_embedding_score', 'missing')}; errors={mapgen_embedding.get('errors', 'missing')}.",
        f"- SCGM retrieval baseline: {scgm['validation_outputs']} generated validation outputs; exact tile candidates excluded={scgm['exact_tile_candidates_excluded']}.",
        f"- SCGM multi-feature retrieval baseline: {scgm_multi['validation_outputs']} generated validation outputs; mean SSIM={scgm_multi['global_ssim_luma']['mean']}.",
        f"- SCGM learned forest baseline: {scgm_forest['validation_outputs']} generated validation outputs; train/val overlap excluded={scgm_forest['train_val_tile_overlap_excluded']}; mean SSIM={scgm_forest['global_ssim_luma']['mean']}.",
        f"- SCGM compact neural MLP baseline: {scgm_mlp['validation_outputs']} generated validation outputs; train/val overlap excluded={scgm_mlp['train_val_tile_overlap_excluded']}; mean SSIM={scgm_mlp['global_ssim_luma']['mean']}.",
        f"- SCGM local-context ridge baseline: {scgm_local_ridge['validation_outputs']} generated validation outputs; train/val overlap excluded={scgm_local_ridge['train_val_tile_overlap_excluded']}; mean SSIM={scgm_local_ridge['global_ssim_luma']['mean']}.",
        f"- SCGM convolutional filter-bank ridge baseline: {scgm_conv_ridge['validation_outputs']} generated validation outputs; train/val overlap excluded={scgm_conv_ridge['train_val_tile_overlap_excluded']}; mean SSIM={scgm_conv_ridge['global_ssim_luma']['mean']}; edge continuity={scgm_conv_ridge['generated_edge_continuity']['mean']}.",
        f"- SCGM patch-embedding retrieval baseline: {scgm_patch['validation_outputs']} generated validation outputs; patch bank={scgm_patch['patch_bank_size']}; train/val overlap excluded={scgm_patch['train_val_tile_overlap_excluded']}; mean MAE={scgm_patch['mae_rgb']['mean']}; mean SSIM={scgm_patch['global_ssim_luma']['mean']}; edge continuity={scgm_patch['generated_edge_continuity']['mean']}.",
        f"- SCGM trained tiny-CNN baseline: {scgm_tiny_cnn['validation_outputs']} generated validation outputs; train/val overlap excluded={scgm_tiny_cnn['train_val_tile_overlap_excluded']}; final training loss={scgm_tiny_cnn['training_loss_final']}; mean MAE={scgm_tiny_cnn['mae_rgb']['mean']}; mean SSIM={scgm_tiny_cnn['global_ssim_luma']['mean']}; edge continuity={scgm_tiny_cnn['generated_edge_continuity']['mean']}.",
        f"- SCGM mosaic neighbor-seam stress audit: {len(scgm_mosaic)} baselines; generated neighbor pairs={sum(int(row['neighbor_pairs_available']) for row in scgm_mosaic)}; best seam mean={min(row['generated_seam_absdiff']['mean'] for row in scgm_mosaic)}.",
        f"- SCGM official-reproduction audit: {len(scgm_official_audit)} components checked; contract runs={len(scgm_official_contract)}; feasibility blockers={sum(row.get('status') == 'blocking_gap' for row in scgm_feasibility_probe)}; checkpoint/official-output gaps remain explicit.",
        f"- Choropleth benchmark initial LLM conditions: {len(initial_rows)} prompt-model-mode rows.",
        f"- Choropleth complete LLM-generated artifacts: {sum(int(row['Complete']) for row in generated_model_rows)}.",
        f"- Choropleth complete LLM-repaired artifacts: {repair_complete}.",
        f"- Validator/reference repair complete artifacts: {sum(int(row['Complete']) for row in validator_rows)}.",
        f"- Deterministic choropleth reference artifacts: {sum(row['Exists'] == 'True' for row in choropleth_reference)}/{len(choropleth_reference)}.",
        f"- Rendered artifact QA initial LLM-generated existing artifacts: {initial_existing}.",
        f"- Rendered artifact QA LLM-repaired existing artifacts: {repair_existing}.",
        f"- Rendered artifact QA validator/reference existing artifacts: {sum(int(row['Existing']) for row in artifact_qa if row['Source'] == 'validator_repair_reference')}.",
        f"- Screenshot-level QA pass artifacts: initial LLM={sum(screenshot_pass_by_source.get(src, 0) for src in initial_sources)}, LLM repair={sum(count for src, count in screenshot_pass_by_source.items() if src.startswith('repair_'))}, validator/reference={screenshot_pass_by_source.get('validator_repair_reference', 0)}, reference={screenshot_pass_by_source.get('reference', 0)}.",
        f"- Choropleth VLM cartographic-quality pilot: {sum(int(row['Reviewed']) for row in choropleth_vlm)} review attempts across {len(set(row['Model'] for row in choropleth_vlm))} local VLMs on 18 screenshot-passing artifacts.",
        f"- Choropleth two-VLM paired agreement: {next(row['Exact verdict agreement'] for row in choropleth_vlm_agreement if row['Scope'] == 'overall')} exact verdict agreement; {next(row['Usable/below agreement'] for row in choropleth_vlm_agreement if row['Scope'] == 'overall')} usable/below agreement.",
        f"- Choropleth evaluator adjudication queue: {next((row['Urgent human adjudication'] for row in evaluator_adjudication if row['Task'] == 'Choropleth cartographic quality'), 'missing')} urgent human-adjudication cases; stable/low priority={next((row['Low priority/stable'] for row in evaluator_adjudication if row['Task'] == 'Choropleth cartographic quality'), 'missing')}.",
        f"- VLM judge robustness: {sum(row.get('Panel role') == 'agreement_panel' for row in vlm_judge_robustness)} agreement-panel task-model rows; {sum(row.get('Panel role') == 'candidate_partial' for row in vlm_judge_robustness)} partial candidates; {sum(row.get('Panel role') == 'failed_candidate' for row in vlm_judge_robustness)} failed candidates.",
        f"- Calibrated multi-judge VLM consensus: {', '.join(row['Task'] + ' high=' + row['High-confidence consensus'] + '/' + row['Consensus items'] + ', medium=' + row['Medium-confidence consensus'] for row in multijudge_consensus) if multijudge_consensus else 'missing'}.",
        f"- Cross-paradigm reliability summary: {', '.join(row['Paradigm'] + '=' + row['Mean score'] for row in cross_paradigm_summary) if cross_paradigm_summary else 'missing'}.",
        f"- Iterative validator-gated repair sweep: {sum(row['Complete'] == 'True' for row in iterative_repair)}/{len(iterative_repair)} incomplete one-pass repair cases completed after up to three additional iterations.",
        f"- Repair-model comparison pilot: qwen2.5-coder:7b completed {next((row['Completed'] + '/' + row['Cases'] for row in repair_comparison if row['Repair model'] == 'qwen2.5-coder:7b'), 'missing')}; qwen2.5-coder:14b completed {next((row['Completed'] + '/' + row['Cases'] for row in repair_comparison if row['Repair model'] == 'qwen2.5-coder:14b'), 'missing')}; deepseek-coder:6.7b completed {next((row['Completed'] + '/' + row['Cases'] for row in repair_comparison if row['Repair model'] == 'deepseek-coder:6.7b'), 'missing')}; full qwen2.5-coder:32b sweep remains {next((row['Completed'] + '/' + row['Cases'] for row in repair_comparison if row['Repair model'] == 'qwen2.5-coder:32b'), 'missing')}.",
        f"- Matched repair-model suite: {', '.join(row['Repair model'] + '=' + row['Completion rate'] + ' mean=' + row['Mean final score'] for row in matched_repair_suite) if matched_repair_suite else 'missing'}.",
        "",
        "## Remaining Q1-Strengthening Work",
        "",
        "- Expand MapGenerator calibrated VLM consensus and completed CLIP screening into human labels or an additional schema-stable VLM judge.",
        "- Expand the matched 7B/14B/DeepSeek repair-model suite to a broader full-case design if more local model time is available.",
        "- Expand the choropleth calibrated VLM consensus into human labels or an additional schema-stable VLM judge.",
        "- Strengthen SCGM beyond the current retrieval/forest/MLP/local-context/convolutional-filter/patch/tiny-CNN diagnostics with an official or cascade-conditioned diffusion-style reproduction when compute and model details permit.",
        "- Final publisher/Crossref citation recheck and journal-format pass.",
        "- Final journal-target/quartile recheck before portal upload; current dated source-confidence ledger is in `submission/journal_target_recheck_2026-06-24.md`.",
        "",
        "## Model-Mode Choropleth Summary",
        "",
        "| Model | Mode | Generated | Safe | Executed | Complete | Mean score |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in model_rows:
        lines.append(
            f"| {row['Model']} | {row['Mode']} | {row['Generated']} | {row['Safe']} | {row['Executed']} | {row['Complete']} | {row['Mean score']} |"
        )
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
