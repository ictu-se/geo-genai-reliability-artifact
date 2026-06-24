# Evidence Map for Q1 Manuscript

This file maps the manuscript's claims to current local evidence. It is a writing and completion-control artifact, not a replacement for the manuscript text.

## Research Questions

RQ1. How reproducible are public Geo-GenAI map-generation artifacts when evaluated as data-code-model-output chains?

RQ2. Do text-to-map datasets provide captions that are sufficiently grounded for faithful map generation and evaluation?

RQ3. How should remote-sensing-to-map generation be evaluated beyond file availability and visual plausibility?

RQ4. Can LLM-generated GIS/code maps produce complete, executable, cartographically valid artifacts under basic and rule-guided prompting?

RQ5. What cross-paradigm failure taxonomy can unify text-to-map, RS-to-map, and LLM-code map generation?

## Claim-to-Evidence Matrix

| Claim | Evidence | Tables/Figures | Current Strength | Remaining Weakness |
|---|---|---|---|---|
| Public Geo-GenAI artifacts are available but unevenly reproducible. | Dataset inventory, reproducibility matrix, claim-vs-artifact table. | Tables 1, 2, 8; Figure 2. | Strong for local artifact audit. | Needs final citation-checked literature table before submission. |
| MapGenerator captions are mostly present and descriptive, but need fidelity auditing. | 850 image-caption pairs; no missing images; heuristic flags; proxy review on 200 sampled pairs; 50 local VLM review attempts across Granite, qwen2.5vl, and qwen3-vl, with 41 non-error labels including 40 labels from two complete 20-pair runs; paired Granite/qwen2.5vl agreement over 20 common pairs; optional CLIP/SigLIP-style scorer implemented with explicit no-model status. | Tables 3, 9, 15, 15b; `mapgenerator_clip_caption_embedding_summary.json`. | Moderate-plus. Deterministic proxy is reproducible; multi-model VLM pilot confirms feasibility; paired agreement shows high feature agreement (73/79) but low semantic verdict agreement (3/20). | Needs human labels, completed CLIP/SigLIP scoring, or a larger calibrated multi-judge panel to validate proxy findings. |
| SCGM base pairs are complete, but cascade references are incomplete. | Split manifest and complete-reference subset manifests. | Table 4. | Strong for local release. | Needs comparison with official reported split details if available. |
| Generated RS-to-map outputs should be evaluated for both pixel similarity and edge continuity. | Target edge-continuity baseline; retrieval, forest, MLP, local-context, convolutional-filter, patch-transfer, and trained tiny-CNN generated-output baselines; leakage guard excluding exact tile overlap. | Tables 5, 5b, 5c; Figures 4, 6, 9. | Moderate-plus. Now includes generated outputs, fitted lower-bound models, a trained CNN diagnostic, metric-sensitivity comparison, and explicit leakage filtering. | Lower-bound outputs are smooth or noisy and are not substitutes for official cascade-conditioned diffusion-style SCGM reproduction. |
| LLM-code map generation fails at artifact-chain validity, not only at code execution. | Two-model, 12-task choropleth benchmark; 7B repair pilot; 32B one-pass repair on 46 failed/incomplete runs; 40-case iterative validator-gated incomplete-case repair sweep; Qwen 7B/14B and DeepSeek 6.7B repair-model pilots over 8 near-miss cases; safety scan; run manifests; artifact QA; screenshot-level QA; two-VLM cartographic-quality pilot over 18 screenshot-passing artifacts; paired two-VLM agreement over the same 18 artifacts; deterministic validator/reference positive control. | Tables 10, 13, 14, 16, 18, 18b, 19, 20; Figures 5, 7, 8. | Strong for local models and benchmark design; 32B one-pass repair recovers 6 complete tasks and 5 screenshot-passing static maps; three-iteration repair recovers 25/40 remaining incomplete one-pass cases, including three interactive-tooltip tasks, three time-series reports, two quantile-classification tasks, one static-plus-interactive multi-output task, and all four colorblind-safe design cases; Qwen 7B and 14B repair-model pilots each recover 3/8 near-miss cases with 14/14 safe attempts, while DeepSeek 6.7B recovers 0/8 with 4/10 safe attempts; reference condition confirms 12/12 feasibility; VLM agreement is 13/18 exact verdicts and 14/18 usable/below decisions, with strongest agreement on validator/reference artifacts. | Needs a broader matched repair-model suite and human or larger calibrated cartographic-quality labels. |
| Deterministic reference baselines are necessary to distinguish missing data from model failure. | Choropleth reference baseline produces static PNG, interactive HTML, time-series PNG, diagnostics, and 3/3 screenshot-level QA passes. | Tables 12, 16. | Strong. | Add publication-ready screenshot examples if included in final paper. |
| Cross-paradigm reliability can be expressed as artifact validity, data grounding, spatial faithfulness, cartographic completeness, and reproducibility. | Integrated taxonomy across text-to-map, RS-to-map, LLM-code, style agents, design subtasks; literature taxonomy by artifact/control/evaluation/gap. | Tables 11, 17; Figure 1. | Strong as conceptual contribution. | Needs final citation formatting and source verification before submission. |

## Experiment Coverage

| Work Package | Current Status | Key Outputs |
|---|---|---|
| WP1 Reproducibility audit | Implemented. | `experiments/00_dataset_reproducibility_audit/outputs` |
| WP2 MapGenerator caption fidelity | Implemented as heuristics + proxy review + multi-model local VLM pilot + paired two-VLM agreement analysis. | `experiments/02_mapgenerator_image_text_audit/outputs`; `tables/table_15b_mapgenerator_vlm_agreement.csv` |
| WP3 SCGM continuity/reproduction | Implemented as manifest, edge baseline, color-stat retrieval baseline, multi-feature retrieval baseline, lightweight learned forest baseline, and compact neural MLP baseline. | `experiments/03_scgm_subset_reproduction/outputs` |
| WP4 Choropleth LLM-code QA | Implemented as two-model benchmark, one-pass and iterative repair pilots, Qwen 7B/14B and DeepSeek repair-model comparison pilots, reference baseline, artifact QA, screenshot-level QA, 18-artifact/two-VLM cartographic-quality pilot, and paired two-VLM agreement analysis. | `experiments/05_choropleth_reliability_benchmark/outputs`; `tables/table_18b_choropleth_vlm_agreement.csv`; `tables/table_20_iterative_repair_model_comparison.csv` |
| WP5 Repair loop | 7B repair pilot, 32B one-pass repair on 46 failed/incomplete runs, plus deterministic validator/reference positive control for all 12 tasks. | `outputs/generated_code_repaired`, `outputs/generated_code/validator_repair_reference`, `repair_manifest.json` |
| WP6 Cross-paradigm taxonomy | Implemented in draft/table plus literature taxonomy. | `tables/table_11_cross_paradigm_metric_taxonomy.csv`, `tables/table_17_literature_taxonomy.csv` |
| WP7 Reproducibility release | Implemented as a public/restricted artifact plan for review and DOI packaging. | `submission/reproducibility_release_plan.md` |
| WP8 Human validation preparation | Implemented as blind annotation exports, full adjudication panels, and a machine-readable rubric. | `submission/human_validation_panels/` |

## Submission-Readiness Gates

Gate A. Strong systems/audit paper:

- complete manuscript draft around 8,000-10,000 words;
- all tables cited and interpreted;
- all scripts regenerate current tables;
- evidence map complete;
- limitations explicit about proxy/VLM and weak retrieval baseline.

Gate B. Strong Q1 empirical paper:

- expand the current MapGenerator two-VLM agreement pilot into human labels, CLIP/SigLIP scoring, or a larger calibrated multi-judge panel;
- expand the Qwen 7B/14B and DeepSeek comparison pilots into a broader matched repair-model suite;
- expand the choropleth two-VLM cartographic-quality agreement pilot to human labels or a larger calibrated multi-judge panel;
- strengthen SCGM beyond lower-bound CNN diagnostics with an official or cascade-conditioned diffusion-style reproduction;
- citation audit with final journal target formatting.

Gate C. Release package:

- keep public scripts, derived tables, manifests, prompts, logs, contact sheets, and generated-code QA outputs together;
- source-link or restrict raw third-party datasets when redistribution is not clearly permitted;
- assign the final public repository URL or DOI immediately before submission.
