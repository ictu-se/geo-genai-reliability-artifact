# Experiments

This folder contains numbered experiment tracks for the Geo-GenAI map creation survey.

## 00_dataset_reproducibility_audit

Goal: inventory downloaded Geo-GenAI datasets and assess reproducibility from local artifacts.

Primary outputs:

- dataset inventory and size/count table
- reproducibility matrix
- dataset audit report

## 01_choropleth_llm_linter

Goal: benchmark LLM-generated choropleth map code and build cartographic linting/repair checks.

Primary data:

- `data/repos/Materials-for-Creating-maps-by-Artificial-Intelligence/data_choropleth`

Suggested first outputs:

- prompt set
- generated Python/Folium/GeoPandas code
- execution logs
- cartographic lint reports
- rendered static/interactive maps

## 02_mapgenerator_image_text_audit

Goal: audit image-text alignment and caption quality in MapGenerator.

Primary data:

- `data/raw/MapGenerator/MapTrain`
- `data/raw/MapGenerator/MGEval`

Suggested first outputs:

- parsed caption table
- feature/entity extraction
- image-text similarity scores
- VLM or rule-based consistency checks

## 03_scgm_subset_reproduction

Goal: reproduce SCGM-style remote-sensing-to-map generation on a manageable subset.

Primary data:

- `data/raw/SCGM/extracted/TMGN_1814`
- `data/repos/SCGM`

Suggested first outputs:

- subset manifest
- training/evaluation config copies
- baseline metrics
- tile-edge continuity metrics

## 04_geo_faithfulness_evaluator

Goal: build a cross-task evaluator for generated maps.

Primary data:

- outputs from experiments 01-03
- MapGenerator image-text pairs
- SCGM image-to-map pairs
- choropleth rendered outputs

Suggested first outputs:

- unified evaluation rubric
- metric implementations
- human/VLM review templates
- benchmark summary table
