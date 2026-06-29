# Results Index

This directory is a lightweight index for the summarized results used in the manuscript. The canonical machine-readable outputs remain in their experiment and manuscript folders.

## Manuscript-Ready Tables

- `manuscripts/q1_geo_genai_reliability/tables/`
- `manuscripts/q1_geo_genai_reliability/tables/manuscript_tables.md`

## Core Experiment Summaries

- Dataset reproducibility audit: `experiments/00_dataset_reproducibility_audit/outputs/`
- Choropleth geodata and artifact linting: `experiments/01_choropleth_llm_linter/outputs/`
- MapGenerator caption and VLM audit summaries: `experiments/02_mapgenerator_image_text_audit/outputs/`
- SCGM tile, baseline, and seam-continuity summaries: `experiments/03_scgm_subset_reproduction/outputs/`
- Choropleth code-generation, repair, screenshot QA, and VLM review summaries: `experiments/05_choropleth_reliability_benchmark/outputs/`

Heavy generated maps, rendered screenshots, raw HTML files, raw datasets, and cloned third-party repositories are excluded from Git and documented through the data/source manifests.
