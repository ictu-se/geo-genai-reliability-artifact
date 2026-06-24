# Reproducibility Release Plan

This plan defines the review and public-release package for the Geo-GenAI reliability manuscript. It is intended to satisfy data/code availability without redistributing third-party datasets whose licenses or hosting terms are not controlled by this project.

## Release Principle

Release the complete audit logic and all derived evidence that this study created. Do not redistribute large third-party datasets, pretrained weights, or upstream repositories unless their original licenses explicitly allow redistribution. Instead, provide source URLs, retrieval instructions, checksums where possible, and scripts that rebuild the local manifests from a reader's own copy.

## Public Package

The public repository or DOI archive should include:

- `manuscripts/q1_geo_genai_reliability/draft/manuscript_draft.md`
- `manuscripts/q1_geo_genai_reliability/tables/`
- `manuscripts/q1_geo_genai_reliability/figures/`
- `manuscripts/q1_geo_genai_reliability/notes/`
- `manuscripts/q1_geo_genai_reliability/protocols/`
- `manuscripts/q1_geo_genai_reliability/scripts/`
- `experiments/00_dataset_reproducibility_audit/scripts/` and derived CSV/JSON summaries
- `experiments/01_choropleth_llm_linter/scripts/` and derived lint summaries
- `experiments/02_mapgenerator_image_text_audit/scripts/`, derived reviews, VLM review CSVs, and contact sheets
- `experiments/03_scgm_subset_reproduction/scripts/`, split manifests, metrics CSVs, generated-output summaries, and contact sheets
- `experiments/05_choropleth_reliability_benchmark/scripts/`, prompt definitions, safety scans, run manifests, repair manifests, screenshot QA, VLM reviews, and summary tables
- `submission/DATA_SOURCES.md`
- `submission/reproducibility_manifest.csv` and `submission/reproducibility_manifest.md`
- `submission/reproduction_runbook.md` and `submission/reproduction_runbook_commands.csv`
- `submission/public_release_skeleton/`
- `submission/environment_minimal.yml`
- `submission/environment_optional_embedding.yml`

Generated images and screenshots that are purely derived from local experiments may be released when they do not embed restricted third-party content. If upstream data licenses are ambiguous, release metrics, thumbnails/contact sheets only when permitted, or provide a restricted-access supplement for reviewers.

## Excluded or Restricted Items

The package should exclude:

- raw third-party remote-sensing/map tile datasets unless redistribution is explicitly permitted;
- raw third-party image-caption datasets unless redistribution is explicitly permitted;
- cloned upstream repositories that should instead be referenced by URL, commit, release tag, or access date;
- local model caches, model weights, private API keys, shell histories, and machine-specific absolute paths;
- non-blinded administrative metadata in the double-anonymous review package.

For each excluded dataset, the final public repository should include a short `DATA_SOURCES.md` entry with source name, source URL, expected directory layout, access date, license note, and the script used to rebuild the derived manifest. The current review-facing version is `submission/DATA_SOURCES.md`.

## Minimal Environment

The release should provide either `environment.yml` or `requirements.txt`. The current minimal Conda environment is `submission/environment_minimal.yml`. Optional CLIP/SigLIP-style embedding scoring uses `submission/environment_optional_embedding.yml`. The minimum documented stack is:

- Python 3.10 or newer;
- pandas, numpy, pillow, matplotlib, scikit-image, scikit-learn;
- geopandas, shapely, pyproj, fiona or pyogrio, rasterio where choropleth and geospatial lint scripts require them;
- playwright or an equivalent browser renderer for screenshot-level QA;
- optional local Ollama models for reproducing LLM/VLM generations and reviews.
- optional PyTorch/Transformers CLIP or SigLIP-compatible models for image-text embedding scoring.

LLM/VLM outputs are not guaranteed bit-reproducible across machines. The release should therefore preserve generated code, prompts, model names, timestamps, safety scans, logs, and derived QA tables as primary evidence, while treating reruns as replication checks.

## Reviewer Package

For double-anonymous review, upload:

- `submission/blinded_main_manuscript.md`;
- `submission/supplementary_material_manifest.md`;
- the machine-readable tables and figures needed by the supplement;
- this release plan with author-identifying paths removed;
- a restricted-access note for any artifact that cannot be redistributed publicly.

Keep `submission/nonblinded_metadata_placeholder.md` and `submission/cover_letter_skeleton.md` outside the blinded review manuscript.

## Pre-Release Audit

Before upload or DOI deposit, run:

```bash
python3 manuscripts/q1_geo_genai_reliability/scripts/build_reproduction_runbook.py
python3 manuscripts/q1_geo_genai_reliability/scripts/synthesize_tables.py
python3 manuscripts/q1_geo_genai_reliability/scripts/make_figures.py
python3 manuscripts/q1_geo_genai_reliability/scripts/build_submission_package.py
python3 manuscripts/q1_geo_genai_reliability/scripts/build_reproducibility_manifest.py
python3 manuscripts/q1_geo_genai_reliability/scripts/build_public_release_skeleton.py
python3 manuscripts/q1_geo_genai_reliability/scripts/write_status_dashboard.py
python3 manuscripts/q1_geo_genai_reliability/scripts/audit_manuscript_readiness.py
python3 -m py_compile manuscripts/q1_geo_genai_reliability/scripts/*.py experiments/02_mapgenerator_image_text_audit/scripts/*.py experiments/03_scgm_subset_reproduction/scripts/*.py experiments/05_choropleth_reliability_benchmark/scripts/*.py
```

Then verify that no review-facing file contains local usernames, absolute machine paths, non-blinded acknowledgements, or removed conference/template artifacts.
