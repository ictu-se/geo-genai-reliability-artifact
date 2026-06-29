# Experiment Opportunities with Downloaded Geo-GenAI Data

Updated: 2026-06-19

This note lists concrete experiments that can be done with the datasets currently downloaded in this workspace.

## Data Available Locally

- SCGM / CSCMG: `data/raw/SCGM/extracted/TMGN_1814`
  - Remote sensing image to map tile pairs.
  - Multi-scale/cascade references.
  - Large enough for training and ablation.
- MapGenerator / MGTrain + MGEval: `data/raw/MapGenerator`
  - Map image and natural-language description pairs.
  - Lightweight benchmark for text-to-map generation/evaluation.
- ChatGPT-4 choropleth materials: `data/repos/Materials-for-Creating-maps-by-Artificial-Intelligence/data_choropleth`
  - Portugal wildfire CSV plus shapefiles.
  - Good for LLM code-generation, map design, and cartographic linting experiments.
- Generative AI Mapmaking repo: `data/repos/generative-ai-mapmaking`
  - Code/workflow for ControlNet-style cartographic generation.
  - No original dataset, but useful as a template if new paired map tiles are built later.

## A. Experiments We Can Do Immediately

### A1. Dataset audit and reproducibility report

- Data: all downloaded datasets.
- Question: how reproducible are 2025 Geo-GenAI papers from public artifacts?
- Method:
  - Count actual samples, inspect image formats, split names, metadata, license notes.
  - Compare paper claims with released artifacts.
  - Record missing code, broken repositories, API-only data, and non-released benchmarks.
- Outputs:
  - Dataset card for each dataset.
  - Reproducibility matrix: data available, code available, model weights available, exact evaluation available.
- Why this is useful:
  - Already found one discrepancy: MapGenerator says 1000 train pairs, but the released `data.zip` currently has 750 train images.

### A2. MapGenerator image-text quality benchmark

- Data: `data/raw/MapGenerator/MapTrain` and `data/raw/MapGenerator/MGEval`.
- Question: do the natural-language descriptions actually capture map content and spatial relations?
- Method:
  - Run image-caption alignment scoring using CLIP/SigLIP or a VLM.
  - Extract entities from captions: roads, water, parks, intersections, buildings.
  - Use a VLM to check whether each entity/spatial relation is visible in the paired map image.
  - Stratify failures by feature type and relation type.
- Metrics:
  - Image-text similarity.
  - Entity presence accuracy.
  - Spatial relation consistency.
  - Caption redundancy or hallucination rate.
- Contribution angle:
  - A map-specific caption-quality audit for text-to-map datasets.

### A3. Baseline text-to-map generation on MGEval

- Data: MGEval captions from MapGenerator.
- Question: how well do current general image generators create map-like images from map descriptions without fine-tuning?
- Method:
  - Use MGEval prompts as input to a general text-to-image model.
  - Compare generated images against ground-truth MGEval images.
  - Score with CLIP/SigLIP, FID/KID, OCR/text artifacts, and VLM-based map-feature checks.
- Metrics:
  - Visual similarity: FID/KID or embedding distance.
  - Text-image alignment: CLIP/SigLIP.
  - Cartographic validity: roads connected, labels plausible, water/land separation, missing impossible symbols.
- Contribution angle:
  - Shows the gap between natural-image generative models and actual cartographic image generation.
- Requirement:
  - Needs access to an image generation model or local diffusion pipeline.

### A4. Choropleth LLM code-generation benchmark

- Data: Portugal wildfire CSV and shapefiles in the choropleth repository.
- Question: can LLMs reliably generate correct thematic maps from geospatial tabular/vector data?
- Method:
  - Create a set of prompts with increasing difficulty:
    - static choropleth
    - interactive Folium map
    - classification choice
    - legend, scale bar, title, source
    - handling missing values and CRS
  - Ask one or more LLMs to generate code.
  - Run code automatically and record errors.
  - Evaluate resulting maps using a cartographic checklist.
- Metrics:
  - Code execution success.
  - Correct join between CSV and geometry.
  - Correct classification and color ramp.
  - Completeness of title, legend, labels, source, projection/CRS handling.
  - Visual/cartographic checklist score.
- Contribution angle:
  - More rigorous version of the ChatGPT-4 choropleth paper, with automated reproducibility and linting.

### A5. Cartographic linting for generated maps

- Data: outputs from A4, plus existing generated maps in the choropleth repository.
- Question: can we automatically detect common cartographic mistakes in LLM-generated maps?
- Method:
  - Build a rule-based linter for GeoPandas/Folium outputs.
  - Check CRS, missing geometries, invalid geometries, unjoined records, color ramp type, legend presence, title/source, class count, and value normalization.
  - Optionally add VLM review for rendered map screenshots.
- Metrics:
  - Rule coverage.
  - False positive/negative rate against human review.
  - Improvement after feeding lint results back into an LLM repair loop.
- Contribution angle:
  - Moves from "LLM can create a map" to "LLM can create a map that passes cartographic QA."

## B. Experiments That Need GPU but Are Stronger

### B1. SCGM reproduction on a subset

- Data: CSCMG.
- Question: can we reproduce the SCGM claim that cascade references improve multi-scale map consistency?
- Method:
  - Train or fine-tune SCGM on a smaller subset.
  - Compare variants:
    - remote sensing image only
    - remote sensing + scale encoding
    - remote sensing + 2x cascade reference
    - remote sensing + 4x cascade reference
  - Evaluate on `val`.
- Metrics:
  - FID/KID or perceptual image metrics.
  - LPIPS/SSIM/PSNR against ground-truth tile maps.
  - Edge continuity across adjacent tiles.
  - VLM/cartographic feature score: roads, blocks, parks, water.
- Contribution angle:
  - Independent reproduction and ablation on public CSCMG data.
- Requirement:
  - GPU and environment setup for the SCGM diffusion code.

### B2. Seamlessness and tile-edge continuity metric

- Data: CSCMG, especially adjacent tile lists.
- Question: do generated map tiles join cleanly across tile boundaries?
- Method:
  - Use tile list CSVs to identify neighboring tiles.
  - Compute boundary mismatch between adjacent generated tiles and ground truth.
  - Score road/line continuation across tile edges using image gradients or segmentation.
- Metrics:
  - RGB boundary difference.
  - Structural boundary difference.
  - Road-continuity score.
  - Edge artifact score.
- Contribution angle:
  - A practical metric for one of the biggest weaknesses in tile-wise generative map models.
- Requirement:
  - Generated outputs from SCGM or another image-to-map model.

### B3. Natural-feature failure analysis in SCGM

- Data: CSCMG.
- Question: where do remote-sensing-to-map models fail: urban areas, natural landscapes, water, parks, roads, buildings?
- Method:
  - Cluster or classify tiles by content type using image embeddings or simple color/texture features.
  - Run model outputs or use available results if reproduced.
  - Analyze performance by tile type and scale level.
- Metrics:
  - Per-cluster LPIPS/SSIM/FID.
  - Feature omission/hallucination rate.
  - Error by scale level.
- Contribution angle:
  - The SCGM paper says natural landscapes are weaker; this turns that into a measurable diagnosis.

### B4. Lightweight baseline for remote-sensing-to-map translation

- Data: CSCMG.
- Question: how much can a simpler model achieve compared with diffusion?
- Method:
  - Train a small pix2pix/UNet/image-to-image baseline on a subset.
  - Compare against SCGM or ground-truth-only reference metrics.
- Metrics:
  - LPIPS/SSIM/PSNR.
  - Edge continuity.
  - Feature presence.
- Contribution angle:
  - Gives a low-compute baseline for future work and helps separate dataset difficulty from model novelty.

## C. Experiments That Could Become Novel Research

### C1. Geo-faithfulness evaluator for generated maps

- Data: MapGenerator, CSCMG, and choropleth outputs.
- Research question: can a unified evaluator detect whether generated maps are geographically and cartographically faithful?
- Method:
  - Combine low-level image metrics, VLM critique, GIS rule checks, and map-specific feature detectors.
  - Evaluate on three generation modes:
    - text-to-map images
    - remote-sensing-to-map images
    - code-generated choropleth maps
- Metrics:
  - Agreement with human/cartographer ratings.
  - Detection of hallucinated/missing features.
  - Detection of broken legends, labels, colors, topology, and joins.
- Why promising:
  - Evaluation is a clear gap across nearly all surveyed papers.

### C2. LLM repair loop for geospatial code maps

- Data: choropleth repository.
- Research question: can an LLM improve its generated map when given structured cartographic lint feedback?
- Method:
  - Generate initial map code.
  - Run code and linter.
  - Feed back exact errors/warnings.
  - Iterate until the output passes checks or hits a budget.
- Metrics:
  - Pass rate before/after repair.
  - Number of iterations.
  - Error classes fixed vs introduced.
  - Final human/cartographic quality score.
- Why promising:
  - Practical, low-compute, and directly addresses reliability rather than novelty for its own sake.

### C3. Prompt-to-map benchmark with constrained geodata

- Data: choropleth repository plus possibly fresh OSM extracts later.
- Research question: can natural-language map requests be translated into trustworthy GIS workflows?
- Method:
  - Build a benchmark of user intents over fixed geodata.
  - Require generated code to use authoritative data, not invent geography.
  - Evaluate data selection, transformation, styling, and rendering.
- Metrics:
  - Workflow success.
  - Data correctness.
  - Cartographic completeness.
  - Reproducibility.
- Why promising:
  - This connects LLM-agent mapping papers with more rigorous benchmark design.

### C4. Text-to-map dataset expansion and cleaning

- Data: MapGenerator.
- Research question: can we improve text-to-map datasets by detecting weak captions and generating controlled alternatives?
- Method:
  - Audit image-caption pairs.
  - Rewrite captions into controlled schemas:
    - objects
    - spatial relations
    - visual style
    - cartographic constraints
  - Compare generation/evaluation results with original vs structured prompts.
- Metrics:
  - Caption factuality.
  - Prompt controllability.
  - Generated-map feature accuracy.
- Why promising:
  - Many text-to-map datasets are caption-like, but not explicitly cartographic or constraint-aware.

### C5. Cross-paradigm comparison: image generation vs GIS-code generation

- Data: MapGenerator and choropleth data.
- Research question: when should maps be generated as images, and when should they be generated as GIS/code artifacts?
- Method:
  - Choose comparable tasks: roads/water sketch maps, thematic choropleths, style variations.
  - Compare pure text-to-image, image-to-image, and code-based generation.
  - Evaluate fidelity, editability, reproducibility, and cartographic correctness.
- Metrics:
  - Geographic faithfulness.
  - Editability.
  - Reproducibility.
  - Visual quality.
  - Human preference.
- Why promising:
  - A useful framing for the field: generative AI should not always mean pixel generation.

## Recommended First Track

The best first experimental track is:

1. Build a reproducibility/data audit for all downloaded datasets.
2. Build the choropleth LLM code-generation benchmark and cartographic linter.
3. In parallel, run a lightweight MapGenerator image-text audit.
4. Move to SCGM reproduction only after compute/environment is ready.

Reason:

- The choropleth and MapGenerator experiments are low-compute and can produce publishable observations quickly.
- SCGM is scientifically strong but heavier; it is better as a second phase after the evaluation framework is clear.
- The biggest research gap across the survey is evaluation and reliability, not merely producing prettier maps.

