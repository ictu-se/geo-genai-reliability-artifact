# Morning Handoff for Q1 Geo-GenAI Reliability Manuscript

Prepared: 2026-06-24

## Active Track

The active workspace track is a Q1 manuscript package on Geo-GenAI map-generation reliability:

- working manuscript directory: `manuscripts/q1_geo_genai_reliability`
- working title: "From Map-Like Images to Trustworthy Cartographic Artifacts: A Cross-Paradigm Reliability Audit of Geo-Generative AI"
- target form: compact blinded main manuscript plus supplement, now using LaTeX/PDF as the primary submission route
- current LaTeX package: `submission/latex/main.tex` compiles to `submission/latex/main.pdf`

Legacy conference-template and local absolute-path residue have been removed from the current manuscript/submission package scope.

## Large Local Data

The large downloaded dataset is SCGM/CSCMG:

- local family: `data/raw/SCGM`
- archive: `data/raw/SCGM/CSCMG.tar.gz`
- total local footprint: about 10 GB
- extracted data: `data/raw/SCGM/extracted/TMGN_1814`
- extracted footprint recorded in the data manifest: about 6.2 GB
- role in manuscript: remote-sensing-to-map tile generation and continuity/reproduction diagnostics

Other local data families:

- MapGenerator/MGTrain/MGEval: about 42 MB extracted, 750 train image-caption pairs and 100 eval pairs locally present.
- GeoGuard: about 650 MB, useful as a local evaluator testbed rather than a main external public dataset claim.
- ChatGPT choropleth materials: about 474 MB in the source repo clone, used for LLM generated-code/cartographic QA experiments.

## Experiments Now Represented

- Dataset reproducibility inventory across downloaded Geo-GenAI artifact families.
- MapGenerator caption-image audit, CLIP/SigLIP scoring, VLM review, paired VLM agreement, and human-validation packet workflow.
- SCGM manifest, complete-reference filtering, edge-continuity baselines, retrieval/forest/MLP/local-context/convolutional-filter/patch-embedding/tiny-CNN baselines, and official reproduction contract/audit.
- Choropleth geodata linting, generated-code benchmark, screenshot QA, VLM cartographic review, validator repair loops, and matched repair-model comparison.
- Cross-paradigm reliability matrix tying text-to-map images, remote-sensing-to-map tiles, and LLM-generated choropleth maps to common failure dimensions.
- Release, citation, journal-style, reviewer-prebuttal, claim-evidence, and Q1 gate ledgers.

## Current Automated Status

- Automated readiness audit: 76/76 passing.
- Reproducibility manifest: 1005 tracked artifact rows.
- Reproduction runbook: 26 command rows, including 20 required and 6 optional/model-dependent steps.
- LaTeX submission package: present and compiling; `submission/latex/main.pdf` is the current manuscript-format artifact.
- SCGM official local overrides: present with bridge dataroot, 200-row complete-reference datalist, cascade seed directory, and 2c/4c local data-config overrides.
- SCGM official feasibility probe: present with 15 checks, including 5 blocking gaps and 0 warnings; dataroot/datalist/cascade prep is closed, while runtime/imports, checkpoints, and official output generation remain open.
- Human validation metric summary: present with two task rows; urgent closure remains 0/17 for MapGenerator and 0/5 for choropleth because real human labels have not been collected yet.
- Human validation adjudication queue: present with 38 rows, final-label template, and task summary; urgent final-ready remains 0/17 for MapGenerator and 0/5 for choropleth because labels are still blank.
- Human validation final-label reducer: present with 38-row ledger and two task summaries; final human labels remain 0/20 for MapGenerator and 0/18 for choropleth, preserving the open claim gate.

## Remaining Manual Q1 Gates

- Collect and adjudicate two-annotator human labels for MapGenerator caption fidelity.
- Collect and adjudicate two-annotator human labels for choropleth cartographic quality.
- Run or explicitly close the official/cascade-conditioned SCGM reproduction gate beyond the current low-compute diagnostics.
- Create final DOI/public repository record immediately before submission.
- Perform final journal/quartile/route and publisher-style checks immediately before portal upload.
- Apply journal-native reference style and any final portal metadata requirements.

## Best Next Work Block

1. Fill the human-validation annotator packets or replace the blank packet placeholders with completed labels.
2. Run `validate_human_validation_packets.py --require-completed`.
3. Run `summarize_human_validation.py` to populate kappa, agreement, score-difference, and urgent-closure metrics.
4. Update manuscript claims from "VLM/calibrated screening plus pending human labels" to the measured human-label outcomes only after labels exist.
5. Decide whether the SCGM official reproduction gate will be executed, deferred as a limitation, or moved to a separate reproduction paper.
