# Completion Roadmap for Q1 Submission

## Target

Produce a compact journal manuscript with a coherent cross-paradigm experimental story, not a loose collection of audits.

Recommended target length:

- Abstract: 250 words
- Introduction: 3 pages
- Related work/taxonomy: 5 pages
- Framework: 3 pages
- Data and methods: 6 pages
- Results: 7 pages
- Discussion: 4 pages
- Limitations/conclusion: 2 pages

## Manuscript Claim Ladder

### Claim 1: Geo-GenAI evaluation must be artifact-aware

Evidence now:

- survey synthesis;
- cross-paradigm framework in draft.

Needs:

- final taxonomy figure.

### Claim 2: Public artifacts are available but unevenly reproducible

Evidence now:

- dataset inventory;
- reproducibility matrix;
- MapGenerator count mismatch;
- missing original data for ControlNet-style mapmaking repo.

Needs:

- paper-claim extraction table for all included papers.

### Claim 3: Text-to-map data need caption-fidelity auditing

Evidence now:

- MapGenerator file/count audit;
- heuristic caption flags;
- contact sheet;
- deterministic proxy caption-fidelity review on 200 sampled pairs;
- local Granite VLM pilot on 20 proxy-selected pairs.

Needs:

- CLIP/SigLIP baseline;
- expanded calibrated VLM/human review on sampled pairs.

### Claim 4: Remote-sensing-to-map evaluation needs continuity metrics

Evidence now:

- SCGM pair/cascade coverage;
- validation edge-continuity baseline;
- lightweight retrieval generated-output baseline on 100 validation tiles;
- multi-feature retrieval generated-output baseline on 100 validation tiles;
- exact tile-id leakage guard excluding 6 train-validation exact matches in the retrieval candidate pool.

Needs:

- road/line continuity metric or segmentation proxy.

### Claim 5: LLM-code mapmaking benefits from cartographic lint and repair

Evidence now:

- geodata lint;
- 6 seed candidate runs;
- wrong-column failure case;
- artifact audit.
- expanded two-model benchmark on 12 prompts x 2 prompting conditions;
- qwen2.5-coder:7b has 24/24 safe scripts, 0/24 execution success, and 0 complete artifacts;
- deepseek-coder:6.7b has 22/24 safe scripts, 2/22 execution success among safe scripts, and 0 complete artifacts;
- prompt rules improve average partial rubric score for both models but do not guarantee valid artifacts;
- deterministic reference baseline produces static PNG, interactive HTML, time-series PNG, and diagnostics from the same local data;
- rendered artifact QA confirms the reference artifacts are nonblank/valid while clean generated runs produce no PNG or HTML artifacts;
- one-pass 7B repair pilot on the first three prompts shows partial grounding improvement but no execution success;
- one-pass 32B repair condition on 46 failed/incomplete runs produces 6 complete tasks and 11 existing rendered artifacts;
- iterative 32B validator-gated incomplete-case repair sweep completes 25/40 remaining one-pass incomplete cases after up to three additional iterations;
- screenshot-level QA shows 5 static-map passes for 32B repair, 3/3 passes for deterministic reference, and 36/36 passes for validator/reference visual artifacts;
- Granite VLM cartographic-quality pilot reviews 18 screenshot-passing choropleth artifacts and separates usable repair screenshots from weak/failed cases;
- deterministic validator/reference positive-control repair produces 12/12 complete tasks and 48 valid artifacts, demonstrating task feasibility without counting as LLM success.

Needs:

- calibrated multi-VLM or human cartographic-quality labels beyond the current 18-artifact pilot;
- full-sweep validator-gated repair loop measured against the deterministic positive control.

## Required Figures

### Figure 1. Cross-paradigm Geo-GenAI artifact chain

Panels:

1. text-to-map image;
2. remote-sensing-to-map tile;
3. LLM-code choropleth;
4. evaluator/repair loop.

Purpose:

- Establish the conceptual frame.

### Figure 2. Dataset landscape and reproducibility matrix

Possible design:

- left: artifact groups by size/file count;
- right: data/code/model/evaluation availability heatmap.

Inputs:

- `tables/table_01_dataset_inventory.csv`
- `tables/table_02_reproducibility_matrix.csv`

### Figure 3. MapGenerator flagged caption contact sheet

Existing:

- `experiments/02_mapgenerator_image_text_audit/outputs/mapgenerator_flagged_contact_sheet.jpg`

Needs:

- possibly add annotations for entity/relation failures after manual/VLM review.

### Figure 4. SCGM cascade-reference coverage and edge-continuity

Panels:

- split coverage bars for RS/map/ref2/ref4;
- edge-difference boxplot for RS vs map target tiles.

Inputs:

- `scgm_split_summary.json`
- `scgm_edge_continuity_val.csv`

### Figure 5. Choropleth QA and repair workflow

Panels:

- raw data lint findings;
- candidate output examples;
- repair-loop flow;
- before/after score bars after repair experiment.

Existing:

- initial benchmark score bars for 12 prompts x 2 modes;
- one-pass repair pilot for C001-C003.
- 32B one-pass repair condition;
- screenshot-level QA contact sheet.

Needs:

- multi-iteration validator-gated repair-loop results on the full 12-task set;
- final publication-ready screenshot panel selection.

### Figure 6. Cross-paradigm failure taxonomy

Matrix:

- rows: paradigms;
- columns: reproducibility, data grounding, spatial faithfulness, topology/continuity, cartographic design, editability.

## Required Tables

Already generated:

- Table 1. Local Geo-GenAI artifact inventory.
- Table 2. Reproducibility matrix.
- Table 3. MapGenerator caption audit.
- Table 4. SCGM coverage.
- Table 5. SCGM edge continuity.
- Table 5b. SCGM lightweight retrieval generated-output baseline.
- Table 5c. SCGM generated-output baseline comparison.
- Table 6. Choropleth data/artifact QA.
- Table 7. Seed choropleth candidates.

Already generated:

- Table 8. Paper claim vs released artifact comparison.
- Table 9. MapGenerator proxy caption-fidelity review.
- Table 10. Choropleth expanded benchmark by model/prompt/repair condition.
- Table 11. Cross-paradigm metric taxonomy.
- Table 12. Deterministic choropleth reference baseline.
- Table 13. Choropleth benchmark model-mode aggregate.
- Table 14. Rendered artifact QA summary.
- Table 15. MapGenerator VLM caption-fidelity pilot.
- Table 16. Screenshot-level choropleth artifact QA.
- Table 17. Geo-GenAI map-generation literature taxonomy.
- Table 18. Choropleth VLM cartographic-quality pilot.
- Table 19. Iterative validator-gated choropleth repair pilot.

Needed:

- expanded VLM/human validation beyond Table 15 pilot;
- calibrated multi-VLM/human cartographic-quality labels beyond Table 18 pilot.

## Experiment Work Packages

### WP1: Paper-Claim Extraction

Objective:

- Turn survey notes into a structured claim-vs-artifact table.

Output:

- `manuscripts/q1_geo_genai_reliability/tables/table_08_claims_vs_artifacts.csv`

Fields:

- paper;
- paradigm;
- claimed dataset;
- claimed sample count;
- released data;
- released code;
- released weights;
- local availability;
- reproducibility status;
- notes.

### WP2: MapGenerator Semantic Caption Review

Objective:

- Validate whether heuristic/proxy flags correspond to real caption-image problems.

Current implementation:

- 200-pair deterministic proxy review:
  - 100 MapTrain pairs;
  - 100 MGEval pairs;
  - visual proxies for water, green areas, dark/textlike detail, and edge density.
- Output:
  - `experiments/02_mapgenerator_image_text_audit/outputs/mapgenerator_proxy_caption_review.csv`
  - `experiments/02_mapgenerator_image_text_audit/outputs/mapgenerator_proxy_caption_review.md`
  - `experiments/02_mapgenerator_image_text_audit/outputs/mapgenerator_proxy_review_contact_sheet.jpg`
- 20-pair Granite VLM pilot:
  - `experiments/02_mapgenerator_image_text_audit/outputs/mapgenerator_vlm_caption_review_granite3.2-vision_latest.csv`
  - `experiments/02_mapgenerator_image_text_audit/outputs/mapgenerator_vlm_caption_review_granite3.2-vision_latest.md`

Design:

- 100 flagged pairs + 100 unflagged pairs.
- Expanded human or calibrated VLM labels:
  - entities correct;
  - spatial relations correct;
  - salient feature missing;
  - hallucinated feature;
  - useful generation prompt.

Output:

- review CSV;
- agreement if multiple reviewers;
- revised contact sheet with examples.

### WP3: Choropleth Expanded Benchmark

Objective:

- Test whether cartographic linting and repair improve LLM-code map reliability.

Current implementation:

- 12 prompts covering static maps, CRS/geometry, joins, cartographic design, interactivity, multi-output, and time-series tasks.
- Conditions:
  - basic prompt;
  - cartographic rules prompt.
- Models:
  - `qwen2.5-coder:7b` through Ollama;
  - `deepseek-coder:6.7b` through Ollama.
- Initial finding:
  - qwen: 0/24 execution success;
  - deepseek: 2/22 execution success after safety filtering;
  - both models: 0 complete benchmark artifacts;
  - rules prompting improves partial score but not final artifact validity.

Next design:

- Run validator-gated repair on all failed initial scripts.
- Keep repair attempts separated from deterministic normalization.

Metrics:

- execution success;
- correct data join;
- CRS/schema validity;
- static/interactivity output;
- cartographic completeness;
- repair improvement;
- repair regression.

### WP4: Screenshot-Level QA

Objective:

- Move beyond file existence for rendered maps.

Checks:

- visual blankness;
- layout occlusion.
- image dimensions;
- dynamic range;
- non-white coverage;
- color diversity;
- edge/detail signal;
- HTML renderability.

Implementation:

- static PNG inspection with image processing;
- HTML screenshot rendering with headless Chromium;
- contact sheet for passing artifacts.

Remaining:

- expand the current Granite pilot to calibrated multi-VLM or human labels for title, legend, source note, color ramp, classification, readable labels, and missing/unjoined regions.

### WP5: SCGM Lightweight Baseline

Objective:

- Generate tile outputs without full diffusion training if GPU is unavailable.

Current implementation:

- nearest-neighbor retrieval from 200 train RS color-statistic features;
- nearest-neighbor retrieval from 200 train RS multi-feature vectors;
- 100 validation generated outputs;
- exact tile-id leakage guard;
- MAE/PSNR/global SSIM proxy and generated edge-continuity scoring.

Output:

- `experiments/03_scgm_subset_reproduction/outputs/scgm_retrieval_baseline_metrics.csv`
- `experiments/03_scgm_subset_reproduction/outputs/scgm_retrieval_baseline_edge_continuity.csv`
- `experiments/03_scgm_subset_reproduction/outputs/scgm_retrieval_baseline_summary.json`
- `experiments/03_scgm_subset_reproduction/outputs/scgm_retrieval_baseline_contact_sheet.jpg`
- `experiments/03_scgm_subset_reproduction/outputs/scgm_multifeature_retrieval_metrics.csv`
- `experiments/03_scgm_subset_reproduction/outputs/scgm_multifeature_retrieval_summary.json`
- `experiments/03_scgm_subset_reproduction/outputs/scgm_multifeature_retrieval_contact_sheet.jpg`

Next baselines:

- simple pix2pix/UNet if GPU is available.
- road/line continuity metric or segmentation proxy.

Metrics:

- PSNR/SSIM;
- edge continuity;
- feature cluster performance;
- zoom-level stratification.

## Decision Gates

### Gate A: Minimum Strong Manuscript

Proceed to full writing if complete:

- WP1 claim table;
- WP2 caption review;
- WP3 expanded choropleth benchmark;
- WP4 screenshot QA.

SCGM can remain dataset/metric contribution if no generated baseline is possible.

### Gate B: Strong Q1 Manuscript

Proceed as Q1 target if complete:

- Gate A plus WP5 generated-output baseline;
- human or VLM validation on at least one output family;
- coherent statistical summaries and confidence intervals where sample size allows.

## Immediate Next Task

Implement WP1 claim-vs-artifact table and WP3 expanded prompt specification. These are low-compute and clarify the manuscript spine.
