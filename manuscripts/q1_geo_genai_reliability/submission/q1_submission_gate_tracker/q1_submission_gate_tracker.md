# Q1 Submission Gate Tracker

This tracker consolidates the remaining gates that cannot honestly be closed by local automation alone. It is the handoff checklist for moving the current strong manuscript track into an actual portal submission.

## Summary

- Gates tracked: 9
- Open gates: 9
- Current status: strong automated package; not final submission-ready until these gates close.

## Gate Ledger

| Gate | Status | Blocking dependency | Closure criterion | Files to update |
|---|---|---|---|---|
| G01 Final publisher/Crossref citation recheck | open_manual | Live DOI/Crossref/publisher metadata immediately before submission. | All references have verified DOI/arXiv/publisher metadata, current online-first status, and no placeholder note. | submission/citation_metadata.csv; submission/references.bib; notes/citation_metadata_ledger.md; draft/manuscript_draft.md |
| G02 Final Taylor & Francis/selected journal native reference style | open_manual | Final portal route and reference-manager/export style decision. | Final manuscript uses the journal-requested citation/reference style and passes a final reference-format QA pass. | submission/compact_main_manuscript.md; submission/latex/main.tex; submission/latex/references.bib; submission/references.bib |
| G03 MapGenerator human caption-fidelity labels | open_manual | Two independent human annotators or expert adjudicator time. | Completed caption labels meet human_validation_acceptance_criteria.csv, including closure of urgent VLM-disagreement cases. | submission/human_validation_panels/summaries; draft/manuscript_draft.md; submission/claim_evidence_crosswalk |
| G04 Choropleth human cartographic-quality labels | open_manual | Two independent human annotators or expert adjudicator time. | Completed cartographic-quality labels meet human_validation_acceptance_criteria.csv and final labels exist for urgent disagreement cases. | submission/human_validation_panels/summaries; draft/manuscript_draft.md; submission/claim_evidence_crosswalk |
| G05 Official/cascade-conditioned SCGM reproduction | open_external_or_compute | Official checkpoints or a documented training path, instantiated SCGM runtime, and generated official outputs. | Official or cascade-conditioned outputs are generated and scored by MAE/PSNR/SSIM, edge-continuity, and mosaic-seam scripts. | experiments/03_scgm_subset_reproduction/outputs; tables; draft/manuscript_draft.md; submission/evidence_map |
| G06 Final public repository URL | open_manual | Author-created public repository or private reviewer repository policy decision. | Repository URL, release tag, and access policy are inserted into release metadata and manuscript availability statements. | submission/release_preflight/*; submission/nonblinded_metadata_placeholder.md; draft/manuscript_draft.md |
| G07 Final DOI/archive deposit | open_manual | Final frozen public repository/deposit and archive minting step. | DOI is minted, metadata files have no TODO fields, and manuscript data/code availability points to the DOI or accepted restricted-access path. | submission/release_preflight/*; draft/manuscript_draft.md; submission/DATA_SOURCES.md |
| G08 Final top-level license decision | open_manual | Author decision on code/evidence license and final review of third-party redistribution constraints. | Top-level project license is chosen; third-party source-link/restricted exclusions are documented in repository README and metadata. | LICENSE; README; submission/release_preflight/*; submission/release_license_audit/* |
| G09 Final journal route, Q1/quartile, and deadline recheck | open_external_live | Live journal portal, special-issue page, and quartile/index database status near upload. | Target route, special-issue status/deadlines, and Q1/category evidence are rechecked and dated immediately before upload. | submission/journal_target_recheck_*.md; notes/status_dashboard.md; cover_letter_skeleton.md |

## Non-Overclaim Rule

Each gate carries an `overclaim_guard` in the CSV. Manuscript prose should not be strengthened beyond the current evidence layer until the matching closure criterion is satisfied.
