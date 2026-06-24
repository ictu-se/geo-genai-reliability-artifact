# DOI/Public Repository Release Checklist

Use this checklist immediately before creating the public repository release or DOI deposit.

## Metadata

- [ ] Replace every `TODO` in `zenodo_metadata_draft.json`, `CITATION.cff`, and `codemeta_draft.json`.
- [ ] Choose a repository license after confirming third-party data constraints.
- [ ] Add the final public repository URL and release tag.
- [ ] Add the final DOI after the archive is minted.
- [ ] Link the release to the submitted manuscript, preprint, or article DOI when available.

## Contents

- [ ] Include project-created scripts, prompts, safety scans, derived CSV/JSON summaries, tables, figures, manifests, and QA ledgers.
- [ ] Exclude raw third-party datasets unless redistribution rights are confirmed.
- [ ] Exclude local model caches, raw model weights, private keys, shell histories, and machine-specific paths.
- [ ] Include `DATA_SOURCES.md`, `environment_minimal.yml`, `environment_optional_embedding.yml`, and `reproducibility_manifest.csv`.
- [ ] Include a note that local LLM/VLM generations are preserved as evidence and reruns may not be bit-reproducible.

## Final Checks

- [ ] Run `python3 manuscripts/q1_geo_genai_reliability/scripts/build_submission_package.py`.
- [ ] Run `python3 manuscripts/q1_geo_genai_reliability/scripts/audit_manuscript_readiness.py`.
- [ ] Run the residue sweep for local paths and removed conference/template artifacts.
- [ ] Recompute SHA-256 manifest after the final file set is frozen.
- [ ] Confirm whether the review upload should use anonymized repository links or a private reviewer link.
