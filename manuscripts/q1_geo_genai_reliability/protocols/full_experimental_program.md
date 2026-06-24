# Full Experimental Program

## Overview

The manuscript should answer one broad question:

> How reliable are current public Geo-GenAI map-generation artifacts when evaluated as cartographic, geospatial, and reproducible artifacts rather than only as visually plausible outputs?

The experimental program is organized into four layers.

## Layer 1: Reproducibility and Artifact Availability

### Research Question

RQ1. Are public Geo-GenAI map-generation artifacts reproducible from their released data, code, and metadata?

### Datasets

- SCGM / CSCMG
- MapGenerator MGTrain/MGEval
- ChatGPT choropleth materials
- Generative AI mapmaking code
- GeoGuard local benchmark as local evaluator testbed

### Current Artifacts

- `experiments/00_dataset_reproducibility_audit/outputs/dataset_inventory.csv`
- `experiments/00_dataset_reproducibility_audit/outputs/reproducibility_matrix.csv`
- `manuscripts/q1_geo_genai_reliability/tables/table_08_claims_vs_artifacts.csv`

### Metrics

- data availability;
- code availability;
- model weights availability;
- sample count;
- split completeness;
- metadata/license/readme availability;
- exact evaluation reproducibility.

### Remaining Work

- Add license/provenance parsing beyond simple file existence.
- Citation-check paper-claim comparison against final full paper texts.

## Layer 2: Text-to-Map Caption Fidelity

### Research Question

RQ2. Do text-to-map datasets provide captions that faithfully and specifically describe the paired map images?

### Dataset

- MapGenerator MapTrain and MGEval.

### Current Artifacts

- `experiments/02_mapgenerator_image_text_audit/outputs/mapgenerator_pairs_audit.csv`
- `experiments/02_mapgenerator_image_text_audit/outputs/mapgenerator_flagged_contact_sheet.jpg`
- `experiments/02_mapgenerator_image_text_audit/outputs/mapgenerator_proxy_caption_review.csv`
- `experiments/02_mapgenerator_image_text_audit/outputs/mapgenerator_proxy_caption_review_summary.json`
- `experiments/02_mapgenerator_image_text_audit/outputs/mapgenerator_proxy_review_contact_sheet.jpg`
- `experiments/02_mapgenerator_image_text_audit/outputs/mapgenerator_vlm_caption_review_granite3.2-vision_latest.csv`
- `experiments/02_mapgenerator_image_text_audit/outputs/mapgenerator_vlm_caption_review_summary_granite3.2-vision_latest.json`

### Current Metrics

- image existence;
- image dimensions;
- caption word count;
- feature keyword mentions;
- named-feature heuristic;
- direction/relation heuristic;
- generic no-feature claim heuristic.
- deterministic visual proxies for water, green areas, dark/textlike detail, bright low-saturation areas, and edge density;
- proxy caption-fidelity score on 200 sampled pairs.
- local VLM alignment score and supported/partly-supported verdict on a 20-pair pilot.

### Remaining Metrics

- CLIP/SigLIP image-text similarity;
- OCR/entity extraction from map labels;
- expanded and calibrated VLM-based entity presence;
- spatial relation consistency;
- caption hallucination/redundancy rate;
- stratified error by feature type: road, water, green area, POI, label, relation.

### Stronger Add-On

Extend the current 20-pair VLM pilot to the existing 200-pair proxy sample and have a calibrated VLM ensemble or human reviewer score:

- entity correctness;
- relation correctness;
- missing salient feature;
- hallucinated feature;
- caption usefulness for generation.

## Layer 3: Remote-Sensing-to-Map Tile Continuity

### Research Question

RQ3. Can public remote-sensing-to-map datasets support evaluation of multi-scale consistency and tile-edge continuity?

### Dataset

- SCGM / CSCMG, `data/raw/SCGM/extracted/TMGN_1814`.

### Current Artifacts

- `experiments/03_scgm_subset_reproduction/outputs/scgm_split_summary.json`
- `experiments/03_scgm_subset_reproduction/outputs/scgm_complete_reference_subset_train_first200.csv`
- `experiments/03_scgm_subset_reproduction/outputs/scgm_complete_reference_subset_val_first200.csv`
- `experiments/03_scgm_subset_reproduction/outputs/scgm_edge_continuity_summary.json`
- `experiments/03_scgm_subset_reproduction/outputs/scgm_retrieval_baseline_metrics.csv`
- `experiments/03_scgm_subset_reproduction/outputs/scgm_retrieval_baseline_summary.json`
- `experiments/03_scgm_subset_reproduction/outputs/scgm_retrieval_baseline_contact_sheet.jpg`
- `experiments/03_scgm_subset_reproduction/outputs/scgm_multifeature_retrieval_metrics.csv`
- `experiments/03_scgm_subset_reproduction/outputs/scgm_multifeature_retrieval_summary.json`
- `experiments/03_scgm_subset_reproduction/outputs/scgm_multifeature_retrieval_contact_sheet.jpg`

### Current Metrics

- split counts;
- complete base RS-map pairing;
- cascade-reference coverage;
- RGB edge-continuity baseline for val tiles.
- generated-output retrieval baseline with exact tile-id leakage guard;
- multi-feature retrieval baseline for metric-sensitivity comparison;
- RGB MAE and PSNR for generated vs target map tiles;
- global luma SSIM proxy;
- generated-output edge continuity.

### Remaining Metrics

- local-window SSIM and LPIPS between generated and target map tiles;
- FID/KID for generated tile distributions;
- road/line continuity across tile borders;
- feature-presence score for roads, water, parks, dense urban blocks;
- error stratification by zoom level and tile content cluster.

### Current Publishable Add-On

GPU-free non-trained baseline implemented:

- color-statistic nearest-neighbor retrieval from train RS tiles;
- deterministic multi-feature nearest-neighbor retrieval from train RS tiles.
- paired train map tile used as generated validation output;
- 6 exact tile-id candidates excluded to avoid leakage;
- generated-output metrics and contact sheet produced.

This provides generated outputs for continuity metrics without training SCGM. The multi-feature comparison shows metric trade-offs rather than universal improvement. The current package adds lightweight learned forest and compact neural MLP diagnostics; a stronger Q1 version should still add a CNN, diffusion-style, or embedding-supervised model.

## Layer 4: LLM-Generated GIS/Choropleth Maps

### Research Question

RQ4. Can LLM-generated GIS/code maps be made reliable through structured cartographic linting and repair?

### Dataset

- Portugal wildfire choropleth materials.

### Current Artifacts

- `experiments/01_choropleth_llm_linter/outputs/lint_report.json`
- `experiments/01_choropleth_llm_linter/outputs/released_map_artifact_audit_summary.json`
- `experiments/01_choropleth_llm_linter/outputs/candidate_scores.csv`
- `experiments/05_choropleth_reliability_benchmark/outputs/generated_code`
- `experiments/05_choropleth_reliability_benchmark/outputs/runs`
- `experiments/05_choropleth_reliability_benchmark/outputs/scores/expanded_choropleth_benchmark_scores.csv`
- `experiments/05_choropleth_reliability_benchmark/outputs/scores/rendered_artifact_qa_summary.csv`
- `experiments/05_choropleth_reliability_benchmark/outputs/scores/screenshot_level_qa_summary.csv`
- `experiments/05_choropleth_reliability_benchmark/outputs/scores/choropleth_vlm_cartographic_review_summary_granite3.2-vision_latest.json`
- `experiments/05_choropleth_reliability_benchmark/outputs/scores/iterative_validator_repair_summary_qwen2.5-coder_32b.json`
- `experiments/05_choropleth_reliability_benchmark/outputs/scores/screenshot_qa/screenshot_qa_contact_sheet.jpg`
- `experiments/05_choropleth_reliability_benchmark/outputs/reference_baseline`
- `experiments/05_choropleth_reliability_benchmark/outputs/generated_code/validator_repair_reference`

### Current Metrics

- code execution success;
- static PNG presence;
- interactive HTML presence;
- CRS repair;
- diagnostic report;
- wrong-column failure detection;
- raw geodata lint: invalid geometry and missing CRS.
- static safety scan;
- use of known files and environment variables;
- time-series output presence;
- diagnostic JSON parseability;
- rendered image nonblankness;
- HTML Leaflet/GeoJSON/tooltip markers;
- error taxonomy.
- screenshot-level visual-proxy QA for static PNGs, time-series PNGs, and rendered interactive HTML;
- 18-artifact local VLM cartographic-quality pilot over screenshot-passing outputs.

### Remaining Metrics

- correct join between CSV and geometry;
- correct thematic variable;
- classification and color ramp suitability;
- legend/title/source/north arrow/scale bar completeness;
- missing/unjoined regions;
- invalid geometries after processing;
- calibrated multi-VLM or human map readability from screenshot;
- repair success and regression rate.

### Implemented Experimental Conditions

- 12 prompts covering static maps, CRS/geometry, joins, design, interactivity, multi-output, wrong-column guard, and time series.
- 2 prompting modes:
  - basic;
  - cartographic rules.
- 2 local models:
  - `qwen2.5-coder:7b`;
  - `deepseek-coder:6.7b`.
- deterministic reference baseline.
- one-pass 7B repair pilot on first qwen prompts.
- one-pass 32B repair condition on 46 failed/incomplete LLM-generated runs.
- iterative 32B validator-gated repair sweep on all 40 incomplete one-pass repairs.
- deterministic validator/reference positive-control repair target for all 12 prompts.

### Candidate Prompt Difficulty Extensions

1. static choropleth;
2. interactive choropleth;
3. time-series chart plus map;
4. CRS repair;
5. missing/invalid geometry repair;
6. wrong-column bait;
7. classification method selection;
8. accessibility/color-blind-safe ramp;
9. bilingual map title/legend;
10. final report with diagnostic metadata.

### Remaining Model Conditions

- one general LLM/API model if available;
- human/reference solution;
- intentionally flawed baseline.

### Remaining Repair Conditions

- additional repair-model comparison or third-iteration LLM repair;
- multi-iteration LLM-based combined execution + cartographic repair with calibrated visual labels.

### Current Publishable Add-On

The current benchmark runs 12 prompts across 2 models and 2 prompting modes, plus reference baselines, a 7B repair pilot, a 32B one-pass repair condition, a 40-case iterative validator-gated incomplete-case repair sweep, screenshot-level visual-proxy QA, an 18-artifact VLM cartographic-quality pilot, and a deterministic validator/reference positive control. The 32B one-pass repair condition recovers six complete tasks and five screenshot-passing static maps; the iterative sweep recovers 25 of the 40 remaining incomplete one-pass repairs after up to three additional iterations, including three interactive-tooltip tasks, three time-series reports, two quantile-classification tasks, one static-plus-interactive multi-output task, and all four colorblind-safe design cases; and the deterministic positive control reaches all 12 tasks and 36 screenshot-level visual passes. The VLM pilot provides a first map-specific visual sanity check, but the next strengthening step remains broader repair-model comparison and calibrated multi-VLM or human cartographic-quality labels.

## Cross-Paradigm Evaluation

### Research Question

RQ5. Which map-generation paradigm fails in which way, and which evaluation methods are appropriate for each?

### Comparison Axes

| Paradigm | Main artifact | Strength | Main failure | Best evaluator |
|---|---|---|---|---|
| Text-to-map image | raster image | style and visual plausibility | caption mismatch, fake topology, unreadable labels | VLM/OCR/feature checks |
| Remote-sensing-to-map | paired raster tiles | spatial conditioning | edge discontinuity, feature omission, scale inconsistency | pixel + continuity + feature metrics |
| LLM GIS/code map | code, vector/raster output | editability and reproducibility | CRS/schema/join/design errors | execution + GIS lint + screenshot QA |
| Style-agent map | stylesheet/config | preserves source geometry | subjective style and legend semantics | human/VLM + style constraints |

## Manuscript-Level Hypotheses

H1. Public Geo-GenAI artifacts are more reproducible at the file level than at the exact evaluation level.

H2. Text-to-map captions are syntactically descriptive but often under-specify spatial relations or make unverifiable negative claims.

H3. Remote-sensing-to-map datasets can support continuity metrics, but cascade-reference coverage must be audited before reproduction.

H4. LLM-generated code maps fail in geospatially diagnosable ways, especially CRS, schema, join, and cartographic completeness.

H5. A unified evaluator must be multi-modal and artifact-aware; no single metric can compare all Geo-GenAI paradigms fairly.
