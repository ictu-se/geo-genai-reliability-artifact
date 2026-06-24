#!/usr/bin/env python3
"""Build a unified tracker for remaining Q1 submission gates.

The automated manuscript package is intentionally conservative: several gates
must remain manual until live external state or human labels exist. This script
turns those open gates into a concrete closure tracker with dependencies,
evidence, and file-update targets.
"""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MS_DIR = ROOT / "manuscripts/q1_geo_genai_reliability"
OUT_DIR = MS_DIR / "submission/q1_submission_gate_tracker"
CSV_OUT = OUT_DIR / "q1_submission_gate_tracker.csv"
MD_OUT = OUT_DIR / "q1_submission_gate_tracker.md"


def exists(rel: str) -> bool:
    path = ROOT / rel
    return path.exists() and path.stat().st_size > 0


def gate_rows() -> list[dict[str, str]]:
    return [
        {
            "gate_id": "G01",
            "gate": "Final publisher/Crossref citation recheck",
            "status": "open_manual",
            "current_evidence": "submission/citation_verification_report.csv; notes/citation_metadata_ledger.md",
            "blocking_dependency": "Live DOI/Crossref/publisher metadata immediately before submission.",
            "closure_criterion": "All references have verified DOI/arXiv/publisher metadata, current online-first status, and no placeholder note.",
            "files_to_update": "submission/citation_metadata.csv; submission/references.bib; notes/citation_metadata_ledger.md; draft/manuscript_draft.md",
            "overclaim_guard": "Do not state publisher-final bibliographic metadata until the just-in-time recheck has been run.",
        },
        {
            "gate_id": "G02",
            "gate": "Final Taylor & Francis/selected journal native reference style",
            "status": "open_manual",
            "current_evidence": "submission/journal_style_preflight/journal_style_preflight.md; submission/references.bib",
            "blocking_dependency": "Final portal route and reference-manager/export style decision.",
            "closure_criterion": "Final manuscript uses the journal-requested citation/reference style and passes a final reference-format QA pass.",
            "files_to_update": "submission/compact_main_manuscript.md; submission/latex/main.tex; submission/latex/references.bib; submission/references.bib",
            "overclaim_guard": "Keep current references as structured draft references, not final journal-native formatting.",
        },
        {
            "gate_id": "G03",
            "gate": "MapGenerator human caption-fidelity labels",
            "status": "open_manual",
            "current_evidence": "submission/human_validation_panels; submission/evaluator_reliability; tables/table_15c_mapgenerator_clip_caption_embedding.csv",
            "blocking_dependency": "Two independent human annotators or expert adjudicator time.",
            "closure_criterion": "Completed caption labels meet human_validation_acceptance_criteria.csv, including closure of urgent VLM-disagreement cases.",
            "files_to_update": "submission/human_validation_panels/summaries; draft/manuscript_draft.md; submission/claim_evidence_crosswalk",
            "overclaim_guard": "Do not convert VLM/CLIP screening claims into human-validated claims before completed labels exist.",
        },
        {
            "gate_id": "G04",
            "gate": "Choropleth human cartographic-quality labels",
            "status": "open_manual",
            "current_evidence": "submission/human_validation_panels; tables/table_18_choropleth_vlm_cartographic_review.csv; tables/table_18b_choropleth_vlm_agreement.csv",
            "blocking_dependency": "Two independent human annotators or expert adjudicator time.",
            "closure_criterion": "Completed cartographic-quality labels meet human_validation_acceptance_criteria.csv and final labels exist for urgent disagreement cases.",
            "files_to_update": "submission/human_validation_panels/summaries; draft/manuscript_draft.md; submission/claim_evidence_crosswalk",
            "overclaim_guard": "Do not treat calibrated VLM consensus as expert cartographic ground truth.",
        },
        {
            "gate_id": "G05",
            "gate": "Official/cascade-conditioned SCGM reproduction",
            "status": "open_external_or_compute",
            "current_evidence": "submission/scgm_official_reproduction_audit; submission/scgm_official_reproduction_contract; experiments/03_scgm_subset_reproduction/outputs",
            "blocking_dependency": "Official checkpoints or a documented training path, instantiated SCGM runtime, and generated official outputs.",
            "closure_criterion": "Official or cascade-conditioned outputs are generated and scored by MAE/PSNR/SSIM, edge-continuity, and mosaic-seam scripts.",
            "files_to_update": "experiments/03_scgm_subset_reproduction/outputs; tables; draft/manuscript_draft.md; submission/evidence_map",
            "overclaim_guard": "Report current SCGM outputs as diagnostics, not official SCGM reproduction.",
        },
        {
            "gate_id": "G06",
            "gate": "Final public repository URL",
            "status": "open_manual",
            "current_evidence": "submission/release_preflight; submission/reproducibility_manifest.csv",
            "blocking_dependency": "Author-created public repository or private reviewer repository policy decision.",
            "closure_criterion": "Repository URL, release tag, and access policy are inserted into release metadata and manuscript availability statements.",
            "files_to_update": "submission/release_preflight/*; submission/nonblinded_metadata_placeholder.md; draft/manuscript_draft.md",
            "overclaim_guard": "Do not include author-identifying repository links in blinded review files until route policy is confirmed.",
        },
        {
            "gate_id": "G07",
            "gate": "Final DOI/archive deposit",
            "status": "open_manual",
            "current_evidence": "submission/release_preflight/zenodo_metadata_draft.json; submission/release_preflight/CITATION.cff",
            "blocking_dependency": "Final frozen public repository/deposit and archive minting step.",
            "closure_criterion": "DOI is minted, metadata files have no TODO fields, and manuscript data/code availability points to the DOI or accepted restricted-access path.",
            "files_to_update": "submission/release_preflight/*; draft/manuscript_draft.md; submission/DATA_SOURCES.md",
            "overclaim_guard": "Do not write a DOI placeholder as if it were minted.",
        },
        {
            "gate_id": "G08",
            "gate": "Final top-level license decision",
            "status": "open_manual",
            "current_evidence": "submission/release_license_audit/release_license_audit.md; submission/release_preflight/release_preflight.md",
            "blocking_dependency": "Author decision on code/evidence license and final review of third-party redistribution constraints.",
            "closure_criterion": "Top-level project license is chosen; third-party source-link/restricted exclusions are documented in repository README and metadata.",
            "files_to_update": "LICENSE; README; submission/release_preflight/*; submission/release_license_audit/*",
            "overclaim_guard": "Do not imply raw third-party datasets or model weights are relicensed by this project.",
        },
        {
            "gate_id": "G09",
            "gate": "Final journal route, Q1/quartile, and deadline recheck",
            "status": "open_external_live",
            "current_evidence": "submission/journal_target_recheck_2026-06-24.md; submission/journal_style_preflight/journal_style_preflight.md",
            "blocking_dependency": "Live journal portal, special-issue page, and quartile/index database status near upload.",
            "closure_criterion": "Target route, special-issue status/deadlines, and Q1/category evidence are rechecked and dated immediately before upload.",
            "files_to_update": "submission/journal_target_recheck_*.md; notes/status_dashboard.md; cover_letter_skeleton.md",
            "overclaim_guard": "Do not treat the 2026-06-24 source-confidence ledger as final portal-day evidence.",
        },
    ]


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def build_markdown(rows: list[dict[str, str]]) -> str:
    open_rows = [row for row in rows if row["status"].startswith("open")]
    lines = [
        "# Q1 Submission Gate Tracker",
        "",
        "This tracker consolidates the remaining gates that cannot honestly be closed by local automation alone. It is the handoff checklist for moving the current strong manuscript track into an actual portal submission.",
        "",
        "## Summary",
        "",
        f"- Gates tracked: {len(rows)}",
        f"- Open gates: {len(open_rows)}",
        "- Current status: strong automated package; not final submission-ready until these gates close.",
        "",
        "## Gate Ledger",
        "",
        "| Gate | Status | Blocking dependency | Closure criterion | Files to update |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| {gate_id} {gate} | {status} | {blocking_dependency} | {closure_criterion} | {files_to_update} |".format(
                gate_id=row["gate_id"],
                gate=row["gate"].replace("|", "/"),
                status=row["status"],
                blocking_dependency=row["blocking_dependency"].replace("|", "/"),
                closure_criterion=row["closure_criterion"].replace("|", "/"),
                files_to_update=row["files_to_update"].replace("|", "/"),
            )
        )
    lines += [
        "",
        "## Non-Overclaim Rule",
        "",
        "Each gate carries an `overclaim_guard` in the CSV. Manuscript prose should not be strengthened beyond the current evidence layer until the matching closure criterion is satisfied.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    rows = gate_rows()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(CSV_OUT, rows)
    MD_OUT.write_text(build_markdown(rows), encoding="utf-8")
    print(f"Wrote {CSV_OUT.relative_to(ROOT)}")
    print(f"Wrote {MD_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
