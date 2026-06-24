# Submission Readiness Checklist

This checklist tracks the remaining gates before treating the manuscript as submission-ready.

## Manuscript Gates

- [x] Working title and abstract.
- [x] Research questions and contribution list.
- [x] Related-work taxonomy with initial references.
- [x] Conceptual framework and reliability dimensions.
- [x] Methods for reproducibility, caption fidelity, SCGM continuity, choropleth QA, repair, and VLM review.
- [x] Results for current experiment spine.
- [x] Limitations and threats to validity.
- [x] Data availability, code availability, supplementary material, and AI-use statements.
- [x] Automated readiness audit passes local artifact checks.
- [x] Local citation audit from available PDFs/text notes.
- [x] selected journal target pack and current special-issue/guideline audit.
- [ ] Final journal-specific formatting.
- [ ] Final citation audit with DOI, venue, volume, issue, and page metadata where available.
- [ ] Native citation style conversion for selected journal.
- [x] selected journal/Taylor & Francis compliance checklist prepared.
- [x] Double-anonymized main manuscript package for selected journal review.
- [x] Public repository, DOI, or explicit restricted-access plan for data/code artifacts.
- [x] Review-facing data-source manifest.
- [x] Minimal environment manifest for reproduction.
- [x] Optional embedding-scoring environment manifest.

## Empirical Gates

- [x] Reproducibility audit across local artifacts.
- [x] MapGenerator file/count/caption audit.
- [x] MapGenerator 200-pair proxy caption-fidelity review.
- [x] MapGenerator 20-pair Granite VLM pilot.
- [x] MapGenerator second complete 20-pair VLM pilot with qwen2.5vl:3b and failed qwen3-vl evaluator-stress attempt recorded.
- [x] MapGenerator paired two-VLM agreement analysis over 20 common reviewed pairs.
- [x] Optional CLIP/SigLIP-style embedding scorer implemented with explicit no-model status.
- [x] SCGM split/cascade coverage audit.
- [x] SCGM edge-continuity baseline.
- [x] SCGM color-stat and multi-feature retrieval generated-output baselines.
- [x] SCGM lightweight learned forest generated-output baseline with overlap filtering.
- [x] SCGM compact neural MLP generated-output baseline with overlap filtering.
- [x] Choropleth geodata lint and released artifact QA.
- [x] Choropleth 12-prompt benchmark over two local coding models and two prompt modes.
- [x] One-pass 32B repair over 46 failed/incomplete LLM-generated runs.
- [x] Iterative validator-gated repair over all 40 incomplete one-pass repair cases.
- [x] Matched near-miss repair-model comparison pilots with qwen2.5-coder:7b, qwen2.5-coder:14b, and deepseek-coder:6.7b over 8 cases.
- [x] Screenshot-level QA over static PNG, time-series PNG, and rendered HTML artifacts.
- [x] 18-artifact VLM cartographic-quality pilot.
- [x] Second 18-artifact choropleth VLM cartographic-quality pilot with qwen2.5vl:3b.
- [x] Choropleth paired two-VLM agreement analysis over 18 common reviewed artifacts.
- [ ] Human labels, CLIP/SigLIP scoring, or a larger calibrated multi-judge panel for MapGenerator captions.
- [ ] Human labels or a larger calibrated multi-judge panel for choropleth visual quality.
- [x] Human/adjudication annotation panels, blind exports, and rubric prepared for MapGenerator captions and choropleth cartographic quality.
- [x] Trained tiny-CNN SCGM/RS-to-map baseline beyond the lightweight forest/MLP diagnostics.
- [ ] Official or cascade-conditioned diffusion-style SCGM/RS-to-map reproduction if model details and compute permit.

## Main-Text Caption and Callout Plan

### Table 1
Use in Section 4 to establish artifact scope and local evidence base.

### Table 2
Use in Section 6.1 to support the claim that reproducibility fails at different points in the artifact chain.

### Table 5c
Use in Section 6.3 to compare color-stat retrieval, multi-feature retrieval, the leakage-guarded learned forest baseline, and the compact neural MLP baseline. The caption should state that the learned forest improves SSIM but remains smooth and low-detail, while the MLP remains visually noisy, so image metrics must be read alongside visual/cartographic validity.

### Table 11
Use in Section 3 or Section 7.2 to define the cross-paradigm evaluation vocabulary.

### Table 13
Use in Section 6.5 to show that initial LLM-code generation has zero complete artifacts despite partial grounding.

### Table 16
Use in Section 6.5 to show the gap between file existence, execution success, and visually inspectable rendered artifacts.

### Table 19
Use in Section 6.5/7.4 as the repair-loop anchor: one-pass repair completes 6 tasks, while iterative validator-gated repair completes 25 of 40 remaining incomplete one-pass cases after up to three additional iterations.

### Table 20
Use in Section 7.4 or supplement as repair-model sensitivity evidence. State that qwen2.5-coder:7b and qwen2.5-coder:14b each completed 3/8 near-miss cases with 14/14 safe attempts, while deepseek-coder:6.7b completed 0/8 with 4/10 safe attempts and frequent syntax failures. qwen2.5-coder:32b completed 25/40 in the full three-iteration sweep; because the 32B scope differs, this is a pilot sensitivity comparison rather than a full ranking.

### Figure 1
Use in Section 3 as the conceptual spine of the paper.

### Figure 5
Use in Section 6.5 to visualize prompt/model/repair condition score differences.

### Figure 7
Use in Section 6.5 to summarize screenshot-level QA pass counts by source group.

### Figure 9
Use in Section 6.3 to demonstrate why SCGM evaluation needs multiple generated-output metrics.

## selected journal Special Issue Timing

- [x] Draft 250-400 word abstract for `Critical Challenges in GeoAI`.
- [ ] Submit abstract to a guest editor before 01 August 2026 if the special-issue path remains preferred.
- [ ] Prepare full manuscript and supporting materials before 01 December 2026 if invited.
- [ ] In the cover letter, identify the `Critical Challenges in GeoAI` special issue and explain why the paper is an evaluation-paradigm contribution rather than only a reproducibility audit.

## Final Pre-Submission Commands

```bash
python3 manuscripts/q1_geo_genai_reliability/scripts/synthesize_tables.py
python3 manuscripts/q1_geo_genai_reliability/scripts/make_figures.py
python3 manuscripts/q1_geo_genai_reliability/scripts/write_status_dashboard.py
python3 manuscripts/q1_geo_genai_reliability/scripts/audit_manuscript_readiness.py
python3 manuscripts/q1_geo_genai_reliability/scripts/build_submission_package.py
python3 -m py_compile manuscripts/q1_geo_genai_reliability/scripts/*.py experiments/02_mapgenerator_image_text_audit/scripts/*.py experiments/03_scgm_subset_reproduction/scripts/*.py experiments/05_choropleth_reliability_benchmark/scripts/*.py
```
