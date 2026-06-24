# Manuscript Readiness Audit

This report is generated from local manuscript and experiment artifacts.

## Automated Checks

| Gate | Status | Evidence |
|---|---|---|
| Draft exists and is substantial | PASS | 11813 words |
| References section exists | PASS |  |
| Acknowledgments section exists | PASS |  |
| Declaration of interest statement exists | PASS |  |
| Data availability statement exists | PASS |  |
| Software availability statement exists | PASS |  |
| Submission packaging plan exists | PASS |  |
| Submission readiness checklist exists | PASS |  |
| Blinded submission manuscript exists | PASS |  |
| Blinded submission manuscript has no obvious identity/path leaks | PASS |  |
| Blinded compact submission manuscript exists | PASS | 7345 words |
| Blinded compact submission manuscript has no obvious identity/path leaks | PASS |  |
| Supplementary material manifest exists | PASS |  |
| selected journal compliance checklist exists | PASS |  |
| Dated journal-target source recheck exists | PASS | 2026-06-24 source-confidence ledger |
| Journal style preflight exists | TODO | automated passed=13/14; manual gates=3 |
| Structured citation metadata export exists | PASS | 39 exported references |
| Citation DOI/arXiv verification report is current | TODO | resolver_verified; verified |
| Reproducibility release plan exists | PASS |  |
| Reproduction runbook exists | PASS | commands=26; required=20; optional=6 |
| DOI/public repository release preflight exists | PASS | automated passed=9/9; manual gates=3 |
| Release-license audit exists | PASS | release rows=9 |
| Public release skeleton exists | PASS | file-map rows=6; summary rows=12 |
| Reproducibility checksum manifest exists | PASS | 1014 tracked artifacts |
| Review-facing data-source manifest exists | PASS |  |
| Minimal environment manifest exists | PASS |  |
| Optional embedding environment manifest exists | PASS |  |
| Human/adjudication validation panels exist | PASS | MapGenerator=20; choropleth=18 |
| Blind validation exports and rubric exist | PASS | blind MapGenerator=20; blind choropleth=18 |
| Human validation packet is reviewer-ready | PASS | priority rows=38; assignments=76; agreement rows=38 |
| Human validation annotator packets exist | PASS | packet rows=6 |
| Human validation packet preflight passes | PASS | preflight rows=4; passed=4 |
| Human validation visual galleries exist | PASS | gallery rows=38; missing artifacts=0 |
| Human validation execution plan exists | PASS | acceptance criteria=7; file contracts=3 |
| Evaluator adjudication ledgers exist | PASS | summary=2; MapGenerator=20; choropleth=18 |
| VLM judge robustness audit exists | PASS | models=9; agreement=4 |
| Calibrated multi-judge VLM consensus exists | PASS | summary=2; MapGenerator=20; choropleth=18 |
| Cross-paradigm reliability matrix exists | PASS | matrix rows=21; summary rows=3 |
| RQ-to-evidence map and objective audit exist | TODO | RQs=5; objective rows=7 |
| Goal completion audit distinguishes track evidence from open gates | PASS | goal rows=9; open=6 |
| Claim-to-evidence crosswalk exists | PASS | claims=7 |
| Q1 submission gate tracker exists | PASS | gates=9 |
| Reviewer prebuttal audit exists | PASS | risks=8 |
| Human validation label summarizer status exists | PASS |  |
| Human validation metric summarizer is acceptance-criteria ready | PASS | metric rows=2 |
| Human validation adjudication queue is final-label ready | PASS | queue rows=38; summary rows=2; final rows=38 |
| Human validation final-label reducer preserves open claim gate | PASS | final ledger rows=38; summary rows=2 |
| Submission package audit exists | PASS |  |
| Manuscript numerical consistency audit passes | PASS |  |
| Main/supplement split and page-budget audit exist | PASS | split rows=42 |
| Main-text compression plan exists | TODO | word budget rows=17; compact display rows=42 |
| Compact main manuscript draft exists | TODO | 7340 words |
| LaTeX submission package compiles to PDF | PASS | pdf_bytes=2004562; figures=10; tables=5 |
| Submission abstract/significance/keyword pack exists | PASS | short abstract words=220; keywords=10 |
| Manuscript tables generated | PASS | 33 table CSV files |
| Figure index populated | PASS | 9 indexed figures |
| MapGenerator VLM pilot table populated | PASS | 110 reviewed pairs |
| MapGenerator two-VLM agreement table populated | PASS | 20 paired caption reviews |
| MapGenerator CLIP/SigLIP scoring completed | PASS | status=completed; scored=200; errors=0 |
| Choropleth VLM visual pilot populated | PASS | 54 reviewed artifacts |
| Choropleth two-VLM agreement table populated | PASS | 18 paired visual reviews |
| Screenshot QA includes validator/reference passes | PASS |  |
| SCGM compact neural MLP baseline populated | PASS | 100 validation outputs |
| SCGM local-context image baseline populated | PASS | 100 validation outputs |
| SCGM convolutional filter-bank image baseline populated | PASS | 100 validation outputs; features=52 |
| SCGM patch-embedding retrieval baseline populated | PASS | 100 validation outputs; patch bank=12416 |
| SCGM trained tiny-CNN baseline populated | PASS | 100 validation outputs; final loss=0.063394 |
| SCGM mosaic neighbor-seam stress audit populated | PASS | baselines=8; pairs=96 |
| SCGM official reproduction contract exists | PASS | runtime rows=7; config rows=2; commands=3 |
| SCGM official local overrides close dataroot and datalist prep | PASS | override rows=5; ready=5 |
| SCGM official-reproduction readiness audit exists | PASS | components=10; blocking=2 |
| SCGM official feasibility probe localizes runtime and config blockers | PASS | probe rows=15; blocking=5; warnings=0 |
| Iterative repair sweep covers all incomplete one-pass repairs | PASS | 25/40 complete; table rows=40 |
| Repair-model comparison pilot table populated | PASS | 4 model rows |
| Matched repair-model suite populated | PASS | models=3; ledger rows=24 |
| Iterative repair attempts are safety-scanned | PASS | 89/89 safe |

## Remaining Manual/Q1 Gates

- Just-in-time publisher/Crossref citation recheck immediately before submission.
- Journal-specific formatting and native reference style.
- Human labels for MapGenerator caption fidelity beyond the current calibrated VLM consensus and CLIP screening layer.
- Human labels for choropleth visual quality beyond the current calibrated VLM consensus.
- Official or cascade-conditioned SCGM diffusion-style reproduction beyond the current retrieval/forest/MLP/local-context/convolutional-filter/patch/tiny-CNN diagnostics.
- Create final DOI/public repository immediately before submission.
- Final journal-target recheck immediately before portal upload; dated 2026-06-24 source-confidence ledger is present, but quartile/route status remains category- and database-dependent.

## Overall

- Automated gates passed: 71/76
- Status: strong manuscript track, not final submission-ready until the manual/Q1 gates above are closed.
