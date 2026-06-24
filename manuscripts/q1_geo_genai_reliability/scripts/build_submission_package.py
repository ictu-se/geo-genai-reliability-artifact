#!/usr/bin/env python3
"""Build a lightweight selected journal-oriented submission package."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from build_submission_abstract_pack import main as build_submission_abstract_pack_main
from build_claim_evidence_crosswalk import main as build_claim_evidence_crosswalk_main
from build_cross_paradigm_reliability_matrix import main as build_cross_paradigm_reliability_matrix_main
from build_compact_main_manuscript import main as build_compact_main_manuscript_main
from build_evaluator_adjudication import main as build_evaluator_adjudication_main
from build_goal_completion_audit import main as build_goal_completion_audit_main
from build_human_validation_adjudication_queue import main as build_human_validation_adjudication_queue_main
from build_human_validation_final_summary import main as build_human_validation_final_summary_main
from build_human_validation_panels import main as build_human_validation_panels_main
from build_journal_style_preflight import main as build_journal_style_preflight_main
from build_journal_target_recheck import main as build_journal_target_recheck_main
from build_latex_submission import main as build_latex_submission_main
from build_main_text_compression_plan import main as build_main_text_compression_plan_main
from build_multijudge_consensus import main as build_multijudge_consensus_main
from build_page_budget import main as build_page_budget_main
from build_public_release_skeleton import main as build_public_release_skeleton_main
from build_q1_submission_gate_tracker import main as build_q1_submission_gate_tracker_main
from build_release_license_audit import main as build_release_license_audit_main
from build_release_preflight import main as build_release_preflight_main
from build_reproduction_runbook import main as build_reproduction_runbook_main
from build_reproducibility_manifest import main as build_reproducibility_manifest_main
from build_repair_model_suite import main as build_repair_model_suite_main
from build_reviewer_prebuttal_audit import main as build_reviewer_prebuttal_audit_main
from build_rq_evidence_map import main as build_rq_evidence_map_main
from build_scgm_official_feasibility_probe import main as build_scgm_official_feasibility_probe_main
from build_scgm_official_local_overrides import main as build_scgm_official_local_overrides_main
from build_scgm_official_reproduction_audit import main as build_scgm_official_reproduction_audit_main
from build_scgm_official_reproduction_contract import main as build_scgm_official_reproduction_contract_main
from build_vlm_judge_robustness_audit import main as build_vlm_judge_robustness_audit_main
from export_citations import main as export_citations_main
from summarize_human_validation import main as summarize_human_validation_main
from synthesize_tables import main as synthesize_tables_main
from validate_human_validation_packets import main as validate_human_validation_packets_main
from stage_zenodo_release import main as stage_zenodo_release_main
from preflight_zenodo_release import main as preflight_zenodo_release_main


ROOT = Path(__file__).resolve().parents[3]
MS_DIR = ROOT / "manuscripts/q1_geo_genai_reliability"
DRAFT = MS_DIR / "draft/manuscript_draft.md"
TABLE_DIR = MS_DIR / "tables"
FIG_DIR = MS_DIR / "figures"
OUT_DIR = MS_DIR / "submission"

MAIN_TABLES = [
    "Table 1. Cross-paradigm metric taxonomy",
    "Table 2. SCGM generated-output baseline comparison",
    "Table 3. Choropleth benchmark model-mode aggregate",
    "Table 4. Screenshot-level choropleth artifact QA",
    "Table 5. Matched repair-model suite",
]

LEGACY_MAIN_TABLE_NEEDLES = {
    "table_05c",
    "table_11_cross_paradigm_metric_taxonomy_slim",
    "table_13",
    "table_16",
    "table_25",
}

MAIN_FIGURES = [
    "Figure 1. Cross-paradigm artifact chain",
    "Figure 2. Dataset inventory",
    "Figure 5. Choropleth benchmark score bars",
    "Figure 7. Screenshot-level QA bar chart",
    "Figure 9. SCGM generated-output baseline comparison",
]

BANNED_PATTERNS = [
    "/" + "Users/",
    "nguyen" + "thevinh",
    r"Geo-LLM",
    r"\bORCID\b",
    r"^##\s+Acknowledg",
    r"^##\s+Funding\b",
    r"^##\s+Conflict of Interest\b",
    "IC" + "TA",
    "Over" + "leaf",
    "LN" + "CS",
    "ll" + "ncs",
    "sp" + "lncs",
]


def build_scgm_mosaic_neighbor_stress() -> None:
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "experiments/03_scgm_subset_reproduction/scripts/compute_scgm_mosaic_continuity_stress.py"),
        ],
        cwd=ROOT,
        check=True,
    )


def word_count(text: str) -> int:
    return len(text.split())


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def anonymize_draft(text: str) -> str:
    replacements = {
        str(ROOT): "[REPOSITORY ROOT]",
        "/" + "Users/" + "nguyen" + "thevinh/Documents/Geo-LLM": "[REPOSITORY ROOT]",
        "Geo-LLM": "[REPOSITORY]",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(
        r"\n## Acknowledg[e]?ments.*?(?=\n## |\Z)",
        "\n## Acknowledgments\n\nNot applicable.\n",
        text,
        flags=re.S | re.I,
    )
    text = re.sub(r"\n## Funding.*?(?=\n## |\Z)", "\n", text, flags=re.S | re.I)
    text = re.sub(r"\n## Conflict[s]? of Interest.*?(?=\n## |\Z)", "\n", text, flags=re.S | re.I)
    banner = [
        "# Blinded Main Manuscript",
        "",
        "Review mode: double-anonymous. Author names, affiliations, thanks statements, and non-blinded repository metadata are intentionally omitted from this file.",
        "",
        "---",
        "",
    ]
    return "\n".join(banner) + text.lstrip()


def anonymize_compact_draft(text: str) -> str:
    if text.startswith("# Compact Main Manuscript Draft"):
        text = text.split("\n---\n", 1)[-1]
    text = anonymize_draft(text)
    return text.replace(
        "# Blinded Main Manuscript",
        "# Blinded Compact Main Manuscript",
        1,
    ).replace(
        "Review mode: double-anonymous. Author names, affiliations, thanks statements, and non-blinded repository metadata are intentionally omitted from this file.",
        "Review mode: double-anonymous. Author names, affiliations, thanks statements, and non-blinded repository metadata are intentionally omitted from this review manuscript file.",
        1,
    )


def table_rows() -> list[tuple[str, str]]:
    rows = []
    for path in sorted(TABLE_DIR.glob("table_*.csv")):
        rows.append((path.stem, str(path.relative_to(MS_DIR))))
    return rows


def figure_rows() -> list[tuple[str, str]]:
    rows = []
    for line in read(FIG_DIR / "figure_index.md").splitlines():
        if not line.startswith("| Figure ") or line.startswith("| Figure |"):
            continue
        parts = [part.strip() for part in line.strip("|").split("|")]
        if len(parts) >= 2:
            rows.append((parts[0], parts[1].strip("`")))
    return rows


def build_supplement_manifest() -> str:
    lines = [
        "# Supplementary Material Manifest",
        "",
        "This manifest separates the compact main manuscript from the full reproducibility evidence package.",
        "",
        "## Main-Text Tables",
        "",
    ]
    lines.extend(f"- {item}" for item in MAIN_TABLES)
    lines += ["", "## Main-Text Figures", ""]
    lines.extend(f"- {item}" for item in MAIN_FIGURES)
    lines += [
        "",
        "## Supplementary Tables",
        "",
        "| File | Intended role |",
        "|---|---|",
    ]
    for stem, rel in table_rows():
        if any(stem.startswith(prefix) for prefix in LEGACY_MAIN_TABLE_NEEDLES):
            continue
        lines.append(f"| `{rel}` | Supporting audit/detail table |")
    lines += [
        "",
        "## Supplementary Figures and Contact Sheets",
        "",
        "| Figure | File |",
        "|---|---|",
    ]
    for figure, rel in figure_rows():
        lines.append(f"| {figure} | `{rel}` |")
    lines += [
        "",
        "## Machine-Readable Evidence",
        "",
        "- Dataset inventory, reproducibility matrix, and claim-vs-artifact CSV files.",
        "- MapGenerator proxy review CSVs, VLM review CSVs, paired agreement table, evaluator-adjudication ledger, calibrated multi-judge VLM consensus, VLM judge robustness audit, and contact sheets.",
        "- SCGM manifests, edge-continuity CSVs, generated-output metrics, generated maps, and contact sheets for retrieval, forest, MLP, local-context, convolutional-filter, patch-embedding, and trained tiny-CNN baselines.",
        "- SCGM official-reproduction readiness audit, local override bridge, feasibility probe, and run contract separating current diagnostics from the unresolved checkpoint/runtime/cascade-conditioned reproduction gate.",
        "- Choropleth generated-code safety scans, run manifests, stderr/stdout logs, artifact QA, screenshot QA, VLM reviews, iterative repair tables, and matched repair-model suite ledgers.",
        "- Citation audit, structured citation metadata CSV, BibTeX export, citation verification report, manuscript consistency audit, main/supplement split, page-budget audit, journal-targeting notes, and submission-readiness audit.",
        "- Dated journal-target source recheck recording special-issue deadlines, source confidence, and final manual quartile/route verification gates.",
        "- Journal style preflight ledger translating current Taylor & Francis/selected journal submission expectations into automated local checks and retained manual gates.",
        "- Cross-paradigm reliability matrix and summary scores linking artifact families to shared reliability dimensions.",
        "- Main-text compression plan with section word budgets and compact display plan.",
        "- Compact main manuscript draft and review-facing blinded manuscript.",
        "- LaTeX submission package with compiled PDF for the primary manuscript route.",
        "- RQ-to-evidence map, objective completion audit, and goal-completion audit linking research questions, manuscript artifacts, and remaining manual/external gates.",
        "- Claim-to-evidence crosswalk with reviewer caveats and explicit non-overclaim boundaries.",
        "- Q1 submission gate tracker consolidating final manual/external gates, closure criteria, and file-update targets.",
        "- Reviewer prebuttal audit mapping likely Q1 objections to evidence, response posture, and overclaim guards.",
        "- Review-facing data-source manifest and minimal environment file.",
        "- Reproduction runbook and command ledger separating deterministic rebuild steps from optional model-dependent reruns.",
        "- Release preflight with DOI/public-repository metadata drafts, checklist, and redistribution checks.",
        "- Release-license audit separating author-controlled code/evidence from source-linked third-party data, model outputs, and weights.",
        "- Public release skeleton with repository-facing README, release file map, third-party exclusions, license-decision checklist, and manifest summary.",
        "- Reproducibility manifest with SHA-256 checksums for manuscript, submission, and derived experiment evidence.",
        "- Human/adjudication validation panels, blind exports, two-annotator assignment sheet, priority queue, agreement template, adjudication queue, final-label template, final-label summary, metric-summary template, VLM adjudication ledgers, calibrated VLM consensus ledgers, and rubric for the remaining caption-fidelity and cartographic-quality validation gates.",
        "- Human-validation visual galleries, gallery index, and per-annotator ready-to-fill packet CSVs for caption-fidelity and cartographic-quality review.",
        "- Human-validation packet preflight validating packet schema, panel coverage, artifact links, and optional completed-label value constraints.",
        "- Human-validation execution plan, acceptance criteria, and annotator file contract for converting the remaining human-label gate into a reproducible two-annotator/adjudication workflow.",
        "",
        "## Data and Code Release Notes",
        "",
        "Large third-party datasets should not be redistributed unless their licenses explicitly permit it. A public reproducibility release should contain scripts, derived summaries, prompts, manifests, and instructions for obtaining the original datasets from their source repositories. See `submission/reproducibility_release_plan.md`, `submission/DATA_SOURCES.md`, and `submission/environment_minimal.yml` for the operational release plan.",
        "",
    ]
    return "\n".join(lines)


def build_metadata_placeholder() -> str:
    return """# Non-Blinded Submission Metadata Placeholder

This file is intentionally separate from `blinded_main_manuscript.md`.

## Authors

- TODO: Author name, affiliation, email, ORCID.

## Funding

- TODO: Funding statement or `No external funding`.

## Conflicts of Interest

- TODO: Conflict-of-interest statement.

## Data Availability Statement

- Data supporting the study are available from the corresponding author upon reasonable request.

## Software Availability Statement

- Software supporting the study is available from the corresponding author upon reasonable request.

## AI Use Disclosure

- TODO: Target-journal-compliant disclosure of AI assistance in drafting, coding, and local model experiments.
"""


def build_cover_letter() -> str:
    return """# Cover Letter Skeleton

Dear Editors,

Please consider the manuscript `From Map-Like Images to Trustworthy Cartographic Artifacts: A Cross-Paradigm Reliability Audit of Geo-Generative AI` for publication.

The manuscript contributes an artifact-aware evaluation framework for GeoAI map generation and tests it across text-to-map image data, remote-sensing-to-map tiles, and LLM/code-generated choropleth maps. The study emphasizes reproducibility, data grounding, spatial continuity, cartographic artifact validity, visual QA, and validator-gated repair.

For the `Critical Challenges in GeoAI` special issue, the manuscript addresses evaluation paradigms, robustness, uncertainty, and constructive pathways by showing why generated maps must be assessed as reproducible artifact chains rather than only as plausible images or executable code.

The review-facing manuscript is double-anonymized. Non-blinded metadata, funding, conflicts of interest, author contributions, repository DOI/URL, and AI-use disclosure should be entered separately in the submission system.

Sincerely,

TODO: Corresponding author
"""


def build_ijgis_compliance_checklist() -> str:
    return """# selected journal / Taylor & Francis Compliance Checklist

Prepared for the selected submission path.

## Current Package Status

- [x] Double-anonymized full review manuscript generated as `submission/blinded_main_manuscript.md`.
- [x] Double-anonymized compact review manuscript generated as `submission/blinded_compact_main_manuscript.md`.
- [x] Supplementary material manifest generated as `submission/supplementary_material_manifest.md`.
- [x] Data availability, code availability, supplementary material, and AI-use/ethics statements included in the manuscript draft.
- [x] Data-source manifest and restricted/public release plan prepared.
- [x] Reproduction runbook and command ledger prepared.
- [x] DOI/public-repository release preflight and metadata drafts prepared.
- [x] Release-license and redistribution matrix prepared.
- [x] Public release skeleton prepared.
- [x] Reproducibility manifest with SHA-256 checksums prepared.
- [x] Minimal environment file prepared.
- [x] Optional embedding-scoring environment file prepared.
- [x] Human validation panels, blind exports, rubric, and label-summary workflow prepared.
- [x] Human validation packet with priority queue, two-annotator assignment sheet, and agreement template prepared.
- [x] Human validation execution plan, acceptance criteria, and file contract prepared.
- [x] Evaluator-adjudication ledgers and human-priority queues prepared from paired VLM reviews.
- [x] Calibrated multi-judge VLM consensus ledgers prepared from schema-conformant reviews.
- [x] VLM judge robustness and schema-adherence audit prepared.
- [x] Cross-paradigm reliability matrix prepared.
- [x] Dated selected journal/special-issue source recheck prepared.
- [x] Journal style preflight ledger prepared.
- [x] selected journal author-guidelines reading note prepared.
- [x] Structured citation metadata and BibTeX export prepared.
- [x] Citation verification report prepared from Crossref/arXiv/DOI resolver checks.
- [x] Manuscript numerical consistency audit prepared.
- [x] Main/supplement split and page-budget audit prepared.
- [x] Main-text compression plan prepared.
- [x] Compact main manuscript draft prepared.
- [x] LaTeX submission package and compiled PDF prepared.
- [x] RQ-to-evidence map, objective completion audit, and goal-completion audit prepared.
- [x] Claim-to-evidence crosswalk prepared.
- [x] Q1 submission gate tracker prepared.
- [x] Reviewer prebuttal audit prepared.
- [x] SCGM official-reproduction readiness audit and run contract prepared.
- [x] Submission abstract/significance/keyword pack prepared.
- [x] Cover letter skeleton identifies the selected journal submission venue and special-issue framing.

## Remaining Before Portal Submission

- [ ] Convert references to the final Taylor & Francis/selected journal reference style after the submission route is fixed.
- [ ] Recheck every DOI, online-first page range, volume, issue, article number, and capitalization.
- [ ] Replace repository placeholders with the final public repository URL, DOI, or restricted-access statement.
- [ ] Fill non-blinded author metadata, researcher identifiers, funding, conflicts of interest, acknowledgements, and author contributions.
- [ ] Confirm the selected submission route: regular selected journal article or `Critical Challenges in GeoAI` special issue.
- [ ] For the special issue route, email the abstract directly to a guest editor before the abstract deadline.
- [ ] For the full manuscript route, select Article Type `Special Issue` in the Taylor & Francis Submission Portal.
- [ ] Name the `Critical Challenges in GeoAI` special issue explicitly in the cover letter.
- [ ] Confirm that no public repository, preprint, supplement, or data/code link exposes author identity during double-anonymous review.
- [ ] Recheck the special issue abstract and full-manuscript deadlines immediately before submission.
- [ ] Recheck journal quartile/category evidence immediately before submission because Q1 status is database/category/year dependent.
- [ ] Recheck double-anonymous requirements for data/code links before uploading review files.
- [ ] Export final manuscript to the journal-requested file format once figures/tables are fixed.

## Source Links To Recheck

- selected journal journal page: https://www.tandfonline.com/journals/tgis20
- selected journal about page: https://www.tandfonline.com/journals/tgis20/about-this-journal
- Special issue call: https://think.taylorandfrancis.com/special_issues/critical-challenges-in-geoai/
- Taylor & Francis manuscript layout guide: https://authorservices.taylorandfrancis.com/publishing-your-research/writing-your-paper/journal-manuscript-layout-guide/
- Taylor & Francis data availability statements: https://authorservices.taylorandfrancis.com/data-sharing/share-your-data/data-availability-statements/
- Taylor & Francis open data policy: https://authorservices.taylorandfrancis.com/data-sharing-policies/open-data/
- Local selected journal guideline reading note: `notes/ijgis_author_guidelines_reading_2026_06_24.md`
"""


def audit_file(path: Path) -> list[str]:
    if path.suffix.lower() in {".pdf", ".png", ".jpg", ".jpeg"}:
        return []
    text = read(path)
    findings = []
    for pattern in BANNED_PATTERNS:
        if re.search(pattern, text, flags=re.I | re.M):
            findings.append(pattern)
    return findings


def build_audit(blinded_text: str, blinded_compact_text: str) -> str:
    table_count = len(list(TABLE_DIR.glob("table_*.csv")))
    figure_count = len(figure_rows())
    files = [
        OUT_DIR / "blinded_main_manuscript.md",
        OUT_DIR / "blinded_compact_main_manuscript.md",
        OUT_DIR / "supplementary_material_manifest.md",
        OUT_DIR / "ijgis_compliance_checklist.md",
        OUT_DIR / "journal_target_recheck_2026-06-24.md",
        OUT_DIR / "journal_style_preflight/journal_style_preflight.csv",
        OUT_DIR / "journal_style_preflight/journal_style_preflight.md",
        OUT_DIR / "reproducibility_release_plan.md",
        OUT_DIR / "reproduction_runbook.md",
        OUT_DIR / "reproduction_runbook_commands.csv",
        OUT_DIR / "release_preflight/release_preflight_checks.csv",
        OUT_DIR / "release_preflight/release_preflight.md",
        OUT_DIR / "release_preflight/zenodo_metadata_draft.json",
        OUT_DIR / "release_preflight/CITATION.cff",
        OUT_DIR / "release_preflight/codemeta_draft.json",
        OUT_DIR / "release_preflight/doi_release_checklist.md",
        OUT_DIR / "release_preflight/zenodo_release_preflight.csv",
        OUT_DIR / "release_preflight/zenodo_release_preflight.md",
        OUT_DIR / "release_license_audit/release_license_matrix.csv",
        OUT_DIR / "release_license_audit/release_license_audit.md",
        OUT_DIR / "public_release_skeleton/README_release_skeleton.md",
        OUT_DIR / "public_release_skeleton/RELEASE_FILE_MAP.csv",
        OUT_DIR / "public_release_skeleton/THIRD_PARTY_EXCLUSIONS.md",
        OUT_DIR / "public_release_skeleton/LICENSE_DECISION_REQUIRED.md",
        OUT_DIR / "public_release_skeleton/release_manifest_summary.csv",
        OUT_DIR / "reproducibility_manifest.csv",
        OUT_DIR / "reproducibility_manifest.md",
        OUT_DIR / "DATA_SOURCES.md",
        OUT_DIR / "environment_minimal.yml",
        OUT_DIR / "environment_optional_embedding.yml",
        OUT_DIR / "citation_metadata.csv",
        OUT_DIR / "references.bib",
        OUT_DIR / "citation_verification_report.csv",
        OUT_DIR / "main_supplement_split.csv",
        OUT_DIR / "main_text_word_budget.csv",
        OUT_DIR / "compact_main_display_plan.csv",
        OUT_DIR / "main_text_compression_plan.md",
        OUT_DIR / "compact_main_manuscript.md",
        OUT_DIR / "latex/main.tex",
        OUT_DIR / "latex/main.pdf",
        OUT_DIR / "latex/references.bib",
        OUT_DIR / "latex/README_latex.md",
        OUT_DIR / "latex/Makefile",
        OUT_DIR / "submission_abstract_pack.md",
        OUT_DIR / "submission_abstract_fields.csv",
        OUT_DIR / "human_validation_panels/human_validation_protocol.md",
        OUT_DIR / "human_validation_panels/human_validation_execution_plan.md",
        OUT_DIR / "human_validation_panels/human_validation_acceptance_criteria.csv",
        OUT_DIR / "human_validation_panels/human_validation_file_contract.csv",
        OUT_DIR / "human_validation_panels/human_validation_packet_readme.md",
        OUT_DIR / "human_validation_panels/human_validation_rubric.json",
        OUT_DIR / "human_validation_panels/human_validation_priority_queue.csv",
        OUT_DIR / "human_validation_panels/human_validation_assignment_sheet.csv",
        OUT_DIR / "human_validation_panels/human_validation_annotator_packet_manifest.csv",
        OUT_DIR / "human_validation_panels/annotator_packets/annotator_A_assignment_sheet.csv",
        OUT_DIR / "human_validation_panels/annotator_packets/annotator_B_assignment_sheet.csv",
        OUT_DIR / "human_validation_panels/annotator_packets/mapgenerator_caption_fidelity_A_completed.csv",
        OUT_DIR / "human_validation_panels/annotator_packets/mapgenerator_caption_fidelity_B_completed.csv",
        OUT_DIR / "human_validation_panels/annotator_packets/choropleth_cartographic_quality_A_completed.csv",
        OUT_DIR / "human_validation_panels/annotator_packets/choropleth_cartographic_quality_B_completed.csv",
        OUT_DIR / "human_validation_panels/human_validation_agreement_template.csv",
        OUT_DIR / "human_validation_panels/human_validation_gallery_index.csv",
        OUT_DIR / "human_validation_panels/mapgenerator_caption_gallery.html",
        OUT_DIR / "human_validation_panels/choropleth_cartographic_gallery.html",
        OUT_DIR / "human_validation_panels/preflight/human_validation_packet_preflight.csv",
        OUT_DIR / "human_validation_panels/preflight/human_validation_packet_preflight.md",
        OUT_DIR / "human_validation_panels/summaries/evaluator_adjudication_summary.md",
        OUT_DIR / "human_validation_panels/summaries/evaluator_adjudication_summary.csv",
        OUT_DIR / "human_validation_panels/summaries/mapgenerator_evaluator_adjudication_ledger.csv",
        OUT_DIR / "human_validation_panels/summaries/choropleth_evaluator_adjudication_ledger.csv",
        OUT_DIR / "human_validation_panels/summaries/human_validation_label_summary.md",
        OUT_DIR / "human_validation_panels/summaries/human_validation_metric_summary.csv",
        OUT_DIR / "human_validation_panels/summaries/mapgenerator_human_label_summary.csv",
        OUT_DIR / "human_validation_panels/summaries/choropleth_human_label_summary.csv",
        OUT_DIR / "human_validation_panels/summaries/human_validation_adjudication_queue.csv",
        OUT_DIR / "human_validation_panels/summaries/human_validation_adjudication_summary.csv",
        OUT_DIR / "human_validation_panels/summaries/human_validation_final_label_template.csv",
        OUT_DIR / "human_validation_panels/summaries/human_validation_final_label_ledger.csv",
        OUT_DIR / "human_validation_panels/summaries/human_validation_final_label_summary.csv",
        OUT_DIR / "human_validation_panels/summaries/human_validation_final_label_summary.md",
        OUT_DIR / "human_validation_panels/summaries/human_validation_adjudication_queue.md",
        OUT_DIR / "evaluator_reliability/mapgenerator_multijudge_consensus.csv",
        OUT_DIR / "evaluator_reliability/choropleth_multijudge_consensus.csv",
        OUT_DIR / "evaluator_reliability/multijudge_consensus_summary.csv",
        OUT_DIR / "evaluator_reliability/multijudge_consensus_report.md",
        OUT_DIR / "evaluator_reliability/vlm_judge_robustness_audit.csv",
        OUT_DIR / "evaluator_reliability/vlm_judge_robustness_audit.md",
        OUT_DIR / "cross_paradigm/cross_paradigm_reliability_matrix.csv",
        OUT_DIR / "cross_paradigm/cross_paradigm_reliability_summary.csv",
        OUT_DIR / "cross_paradigm/cross_paradigm_reliability_matrix.md",
        OUT_DIR / "evidence_map/rq_evidence_map.csv",
        OUT_DIR / "evidence_map/objective_completion_audit.csv",
        OUT_DIR / "evidence_map/rq_evidence_map.md",
        OUT_DIR / "evidence_map/goal_completion_audit.csv",
        OUT_DIR / "evidence_map/goal_completion_audit.md",
        OUT_DIR / "claim_evidence_crosswalk/claim_evidence_crosswalk.csv",
        OUT_DIR / "claim_evidence_crosswalk/claim_evidence_crosswalk.md",
        OUT_DIR / "q1_submission_gate_tracker/q1_submission_gate_tracker.csv",
        OUT_DIR / "q1_submission_gate_tracker/q1_submission_gate_tracker.md",
        OUT_DIR / "reviewer_prebuttal_audit/reviewer_prebuttal_audit.csv",
        OUT_DIR / "reviewer_prebuttal_audit/reviewer_prebuttal_audit.md",
        OUT_DIR / "scgm_official_reproduction_contract/scgm_runtime_dependency_contract.csv",
        OUT_DIR / "scgm_official_reproduction_contract/scgm_official_config_mapping.csv",
        OUT_DIR / "scgm_official_reproduction_contract/scgm_official_run_commands.csv",
        OUT_DIR / "scgm_official_reproduction_contract/environment_scgm_official_reproduction.yml",
        OUT_DIR / "scgm_official_reproduction_contract/scgm_official_reproduction_contract.md",
        OUT_DIR / "scgm_official_reproduction_contract/local_overrides/reference_map_test_level_2c_oz_local.yaml",
        OUT_DIR / "scgm_official_reproduction_contract/local_overrides/reference_map_test_level_4c_oz_local.yaml",
        OUT_DIR / "scgm_official_reproduction_contract/local_overrides/scgm_official_local_override_manifest.csv",
        OUT_DIR / "scgm_official_reproduction_contract/local_overrides/scgm_official_local_overrides.md",
        OUT_DIR / "scgm_official_reproduction_audit/scgm_official_reproduction_audit.csv",
        OUT_DIR / "scgm_official_reproduction_audit/scgm_official_reproduction_audit.md",
        OUT_DIR / "scgm_official_reproduction_audit/scgm_official_feasibility_probe.csv",
        OUT_DIR / "scgm_official_reproduction_audit/scgm_official_feasibility_probe.md",
        OUT_DIR / "repair_model_suite/matched_repair_model_summary.csv",
        OUT_DIR / "repair_model_suite/matched_repair_case_ledger.csv",
        OUT_DIR / "repair_model_suite/matched_repair_model_suite.md",
        OUT_DIR / "nonblinded_metadata_placeholder.md",
        OUT_DIR / "cover_letter_skeleton.md",
    ]
    lines = [
        "# Submission Package Audit",
        "",
        f"- blinded manuscript word count: {word_count(blinded_text)}",
        f"- blinded compact manuscript word count: {word_count(blinded_compact_text)}",
        f"- table CSV files: {table_count}",
        f"- indexed figures/contact sheets: {figure_count}",
        "",
        "## Files",
        "",
        "| File | Exists | Anonymization findings |",
        "|---|---:|---|",
    ]
    for path in files:
        findings = audit_file(path) if path.exists() else ["missing"]
        if path.name in {"nonblinded_metadata_placeholder.md", "cover_letter_skeleton.md"}:
            findings = ["non-blinded/admin file; keep outside review manuscript"]
        if "release_preflight" in path.parts:
            findings = ["release/admin metadata draft; replace TODO fields outside blinded review manuscript"]
        lines.append(f"| `{path.relative_to(MS_DIR)}` | {path.exists()} | {'; '.join(findings) if findings else 'none'} |")
    lines += [
        "",
        "## Review Notes",
        "",
        "- `blinded_main_manuscript.md` is the full evidence-rich review manuscript draft.",
        "- `blinded_compact_main_manuscript.md` is the review-facing compact manuscript.",
        "- `nonblinded_metadata_placeholder.md` and `cover_letter_skeleton.md` are administrative files and should not be uploaded as blinded manuscript content.",
        "- Final journal formatting, reference style, actual public repository DOI/URL, and human validation gates remain outside this automated package build.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    build_repair_model_suite_main()
    build_scgm_mosaic_neighbor_stress()
    synthesize_tables_main()
    export_citations_main()
    build_submission_abstract_pack_main()
    build_vlm_judge_robustness_audit_main()
    build_multijudge_consensus_main()
    build_human_validation_panels_main()
    validate_human_validation_packets_main()
    build_evaluator_adjudication_main()
    summarize_human_validation_main()
    build_human_validation_adjudication_queue_main()
    build_human_validation_final_summary_main()
    build_cross_paradigm_reliability_matrix_main()
    build_page_budget_main()
    build_main_text_compression_plan_main()
    build_compact_main_manuscript_main()
    build_rq_evidence_map_main()
    build_claim_evidence_crosswalk_main()
    build_q1_submission_gate_tracker_main()
    build_goal_completion_audit_main()
    build_reviewer_prebuttal_audit_main()
    build_scgm_official_reproduction_contract_main()
    build_scgm_official_reproduction_audit_main()
    build_scgm_official_local_overrides_main()
    build_scgm_official_feasibility_probe_main()
    build_journal_target_recheck_main()
    blinded = anonymize_draft(read(DRAFT))
    blinded_compact = anonymize_compact_draft(read(OUT_DIR / "compact_main_manuscript.md"))
    write(OUT_DIR / "blinded_main_manuscript.md", blinded)
    write(OUT_DIR / "blinded_compact_main_manuscript.md", blinded_compact)
    build_latex_submission_main()
    write(OUT_DIR / "supplementary_material_manifest.md", build_supplement_manifest())
    write(OUT_DIR / "ijgis_compliance_checklist.md", build_ijgis_compliance_checklist())
    write(OUT_DIR / "nonblinded_metadata_placeholder.md", build_metadata_placeholder())
    write(OUT_DIR / "cover_letter_skeleton.md", build_cover_letter())
    build_reproduction_runbook_main()
    build_journal_style_preflight_main()
    build_release_license_audit_main()
    build_reproducibility_manifest_main()
    build_release_preflight_main()
    build_public_release_skeleton_main()
    build_reproducibility_manifest_main()
    build_release_preflight_main()
    build_public_release_skeleton_main()
    build_reproducibility_manifest_main()
    stage_zenodo_release_main()
    preflight_zenodo_release_main()
    write(OUT_DIR / "submission_package_audit.md", build_audit(blinded, blinded_compact))
    print(f"Wrote submission package to {OUT_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
