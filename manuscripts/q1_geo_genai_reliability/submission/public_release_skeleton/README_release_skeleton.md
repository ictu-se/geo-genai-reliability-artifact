# Public Release Skeleton

This folder is a repository-facing skeleton for the Geo-GenAI reliability manuscript package. It prepares the public release layout without selecting the final DOI, repository URL, author metadata, or top-level license.

## Intended Public Contents

- Project-created scripts for manuscript building, dataset audits, MapGenerator caption fidelity screening, SCGM diagnostics, choropleth code-generation QA, repair evaluation, and release checks.
- Derived CSV, JSON, Markdown, figure, table, prompt, safety-scan, QA, and manifest artifacts created by this study.
- Human-validation packet templates, rubrics, galleries, assignment files, adjudication queue, final-label template, and final-label reducer outputs.
- Environment manifests, reproduction runbook, data-source manifest, checksum manifest, release-license audit, DOI metadata drafts, and reviewer-facing documentation.

## Explicit Exclusions

- Raw third-party datasets and cloned upstream repositories are source-linked, not redistributed.
- Raw SCGM/CSCMG archives or extracted tile trees are not part of the public package unless final license review permits them.
- Raw MapGenerator images/captions are not part of the public package when their terms require source-linking or restricted use.
- Model checkpoints, local model caches, pretrained weights, private keys, shell histories, and machine-specific absolute paths are excluded.
- Bulky generated run folders should be represented by derived metrics, QA ledgers, selected permissible figures, or restricted reviewer material.

## Current Evidence Counts

- Current checksum manifest rows inspected: 1014
- Release-license matrix rows inspected: 9

## Files In This Skeleton

- `README_release_skeleton.md`: this public-facing release overview.
- `RELEASE_FILE_MAP.csv`: include/exclude rules by artifact family.
- `THIRD_PARTY_EXCLUSIONS.md`: source-link and exclusion rules for upstream data, repositories, and weights.
- `LICENSE_DECISION_REQUIRED.md`: final license decision checklist, intentionally unresolved here.
- `release_manifest_summary.csv`: manifest group counts for the current local evidence package.

## Manual Steps Before DOI Deposit

1. Choose the public repository route and update repository metadata.
2. Choose final top-level code/evidence license terms after checking third-party constraints.
3. Mint the DOI and replace TODO metadata in the release preflight files.
4. Rebuild the checksum manifest after the public file set is frozen.
5. Re-run the readiness audit and local-path residue sweep.
