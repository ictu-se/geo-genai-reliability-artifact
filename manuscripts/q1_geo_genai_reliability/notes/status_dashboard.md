# Manuscript Status Dashboard

- Draft word count: 12267
- Tables generated: 33
- Figures indexed: 9
- Blinded submission manuscript: present.
- Blinded compact submission manuscript: present.
- Supplementary material manifest: present.
- selected journal compliance checklist: present.
- Dated journal-target source recheck: present.
- Journal style preflight: present; automated passed=14/14.
- Reproducibility release plan: present.
- Reproduction runbook: present; commands=26; required=20.
- DOI/public repository release preflight: present; automated passed=9/9.
- Release-license audit: present; rows=9.
- Public release skeleton: present; file-map rows=6; summary rows=12.
- Reproducibility checksum manifest: present; tracked artifacts=1014.
- Data-source manifest: present.
- Minimal environment manifest: present.
- Optional embedding environment manifest: present.
- Citation metadata/BibTeX export: present.
- Citation DOI/arXiv verification report: present.
- Human validation panels and rubric: present.
- Human validation packet: present; priority rows=38; assignments=76.
- Human validation annotator packets: present; packet files=6.
- Human validation packet preflight: present; passed=4/4.
- Human validation visual galleries: present; gallery rows=38; missing artifacts=0.
- Human validation execution plan: present; criteria=7; file contracts=3.
- Human validation label summary: present.
- Human validation metric summary: present; rows=2; urgent closure=mapgenerator_caption_fidelity=0/17, choropleth_cartographic_quality=0/5.
- Human validation adjudication queue: present; tasks=2; urgent final ready=mapgenerator_caption_fidelity=0/17, choropleth_cartographic_quality=0/5.
- Human validation final label summary: present; tasks=2; final labels=choropleth_cartographic_quality=0/18, mapgenerator_caption_fidelity=0/20.
- Evaluator adjudication summary: present.
- VLM judge robustness audit: present.
- Calibrated multi-judge VLM consensus: present.
- Cross-paradigm reliability matrix: present.
- RQ-to-evidence map and objective audit: present.
- Goal completion audit: present; requirements=9; open/manual=6.
- Claim-to-evidence crosswalk: present; claims=7.
- Q1 submission gate tracker: present; gates=9; open=9.
- Reviewer prebuttal audit: present; risks=8.
- SCGM official reproduction contract: present; mapped runs=2; ready subsets=2.
- SCGM official local overrides: present; artifacts=5; ready=5.
- SCGM official-reproduction readiness audit: present; components=10; blocking=2.
- SCGM official feasibility probe: present; checks=15; blocking=5; warnings=0.
- Manuscript numerical consistency audit: pass.
- Main/supplement split and page-budget audit: present.
- 30-page compression plan: present.
- Compact main manuscript draft: present.
- LaTeX submission package: present; compile=pass; figures=11; tables=5.
- Submission abstract/significance/keyword pack: present.

## Current Submission Track

- Primary submission venue: selected venue.
- Special issue opportunity: `Critical Challenges in GeoAI`.
- Abstract deadline: 01 August 2026.
- Full manuscript deadline: 01 December 2026.
- Target pack: `notes/ijgis_submission_target_pack.md`.
- Dated source recheck: `submission/journal_target_recheck_2026-06-24.md`.
- Draft special-issue abstract: `notes/ijgis_special_issue_abstract.md`.
- Submission abstract pack: `submission/submission_abstract_pack.md`.

## Current Evidence

- MapGenerator proxy review: 200 sampled pairs.
- Citation verification: 12 metadata verified; 2 DOI-resolver verified; 0 publisher-URL verified.
- MapGenerator VLM pilot review: 110 review attempts across 6 local VLMs; non-error reviews=58.
- MapGenerator two-VLM paired agreement: 3/20 exact verdict agreement; 73/79 feature agreement.
- MapGenerator evaluator adjudication queue: 17 urgent human-adjudication cases.
- MapGenerator CLIP/SigLIP-style embedding scoring: status=completed; scored pairs=200; mean score=0.342781; errors=0.
- SCGM retrieval baseline: 100 generated validation outputs; exact tile candidates excluded=6.
- SCGM multi-feature retrieval baseline: 100 generated validation outputs; mean SSIM=0.290337.
- SCGM learned forest baseline: 100 generated validation outputs; train/val overlap excluded=6; mean SSIM=0.409008.
- SCGM compact neural MLP baseline: 100 generated validation outputs; train/val overlap excluded=6; mean SSIM=0.303307.
- SCGM local-context ridge baseline: 100 generated validation outputs; train/val overlap excluded=6; mean SSIM=0.361186.
- SCGM convolutional filter-bank ridge baseline: 100 generated validation outputs; train/val overlap excluded=6; mean SSIM=0.347422; edge continuity=6.235243.
- SCGM patch-embedding retrieval baseline: 100 generated validation outputs; patch bank=12416; train/val overlap excluded=6; mean MAE=16.335779; mean SSIM=0.273621; edge continuity=11.403972.
- SCGM trained tiny-CNN baseline: 100 generated validation outputs; train/val overlap excluded=6; final training loss=0.063394; mean MAE=26.100397; mean SSIM=0.366129; edge continuity=9.221896.
- SCGM mosaic neighbor-seam stress audit: 8 baselines; generated neighbor pairs=96; best seam mean=4.611871.
- SCGM official-reproduction audit: 10 components checked; contract runs=2; feasibility blockers=5; checkpoint/official-output gaps remain explicit.
- Choropleth benchmark initial LLM conditions: 46 prompt-model-mode rows.
- Choropleth complete LLM-generated artifacts: 0.
- Choropleth complete LLM-repaired artifacts: 6.
- Validator/reference repair complete artifacts: 12.
- Deterministic choropleth reference artifacts: 4/4.
- Rendered artifact QA initial LLM-generated existing artifacts: 1.
- Rendered artifact QA LLM-repaired existing artifacts: 11.
- Rendered artifact QA validator/reference existing artifacts: 48.
- Screenshot-level QA pass artifacts: initial LLM=0, LLM repair=5, validator/reference=36, reference=3.
- Choropleth VLM cartographic-quality pilot: 54 review attempts across 3 local VLMs on 18 screenshot-passing artifacts.
- Choropleth two-VLM paired agreement: 13/18 exact verdict agreement; 14/18 usable/below agreement.
- Choropleth evaluator adjudication queue: 4 urgent human-adjudication cases; stable/low priority=10.
- VLM judge robustness: 4 agreement-panel task-model rows; 1 partial candidates; 4 failed candidates.
- Calibrated multi-judge VLM consensus: MapGenerator caption fidelity high=1/20, medium=15, Choropleth cartographic quality high=13/18, medium=4.
- Cross-paradigm reliability summary: LLM-generated choropleth maps=2.14, Remote-sensing-to-map tiles=2.00, Text-to-map image data=1.29.
- Iterative validator-gated repair sweep: 25/40 incomplete one-pass repair cases completed after up to three additional iterations.
- Repair-model comparison pilot: qwen2.5-coder:7b completed 3/8; qwen2.5-coder:14b completed 3/8; deepseek-coder:6.7b completed 0/8; full qwen2.5-coder:32b sweep remains 25/40.
- Matched repair-model suite: qwen2.5-coder:14b=3/8 mean=0.829, qwen2.5-coder:7b=3/8 mean=0.808, deepseek-coder:6.7b=0/8 mean=0.204.

## Remaining Q1-Strengthening Work

- Expand MapGenerator calibrated VLM consensus and completed CLIP screening into human labels or an additional schema-stable VLM judge.
- Expand the matched 7B/14B/DeepSeek repair-model suite to a broader full-case design if more local model time is available.
- Expand the choropleth calibrated VLM consensus into human labels or an additional schema-stable VLM judge.
- Strengthen SCGM beyond the current retrieval/forest/MLP/local-context/convolutional-filter/patch/tiny-CNN diagnostics with an official or cascade-conditioned diffusion-style reproduction when compute and model details permit.
- Final publisher/Crossref citation recheck and journal-format pass.
- Final journal-target/quartile recheck before portal upload; current dated source-confidence ledger is in `submission/journal_target_recheck_2026-06-24.md`.

## Model-Mode Choropleth Summary

| Model | Mode | Generated | Safe | Executed | Complete | Mean score |
|---|---|---:|---:|---:|---:|---:|
| deepseek-coder_6.7b | basic | 12 | 10 | 1 | 0 | 0.176 |
| deepseek-coder_6.7b | rules | 12 | 12 | 1 | 0 | 0.501 |
| qwen2.5-coder_7b | basic | 12 | 12 | 0 | 0 | 0.059 |
| qwen2.5-coder_7b | rules | 12 | 12 | 0 | 0 | 0.490 |
| validator_repair_reference | validator | 12 | 12 | 12 | 12 | 1.000 |
