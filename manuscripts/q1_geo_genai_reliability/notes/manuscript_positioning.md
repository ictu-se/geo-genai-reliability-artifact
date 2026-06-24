# Manuscript Positioning

## Working Title

From Map-Like Images to Trustworthy Cartographic Artifacts: A Cross-Paradigm Reliability Audit of Geo-Generative AI

## Target Contribution

This is not a paper about proposing one more map generator. It is a reliability and evaluation paper for Geo-GenAI map generation.

The central argument:

> Geo-generative AI should be evaluated as a chain of cartographic artifacts, not only as plausible images. Across public text-to-map, remote-sensing-to-map, and LLM-code mapmaking artifacts, the most important failures occur in reproducibility, geospatial grounding, caption semantics, metadata integrity, topology/continuity, and cartographic QA.

## Why Q1-Relevant

The paper can aim higher than a simple replication because it spans three currently disconnected paradigms:

1. text-to-map image generation;
2. remote-sensing-to-map image translation;
3. LLM-generated GIS/code map production.

The novelty is a cross-paradigm evaluation frame:

- dataset reproducibility audit;
- semantic caption fidelity audit;
- geospatial metadata and CRS linting;
- tile-edge continuity metric;
- code-execution and cartographic QA checks;
- repair-loop design for generated GIS maps.

## Best-Fit Journal Families

Candidate journal families to check later against current aims/scope and Q ranking:

- cartography/GIScience journals;
- geoinformatics and geographic information science journals;
- remote sensing / GeoAI journals if SCGM reproduction is expanded;
- applied AI + geospatial data quality journals.

Do not lock the journal until the final experiment set is clear. The current strongest positioning is evaluation/reliability in cartography and GIScience.

## Risk Assessment

Current evidence has moved beyond a simple systems/audit paper. The workspace now has the main experimental spine needed for a Q1-style reliability manuscript:

1. a 12-task choropleth LLM benchmark across two local coding models and two prompt modes;
2. screenshot-level cartographic QA for generated, repaired, validator/reference, and reference artifacts;
3. MapGenerator proxy caption-fidelity review plus two complete local VLM review passes and one failed evaluator-stress pass;
4. SCGM generated-output baselines including color-stat retrieval, multi-feature retrieval, a leakage-guarded lightweight learned forest, and a compact neural MLP;
5. one-pass and iterative validator-gated repair experiments, with the iterative sweep completing 25 of 40 previously incomplete one-pass repair cases, Qwen 7B/14B repair-model pilots each completing 3 of 8 near-miss cases, and a DeepSeek 6.7B pilot completing 0 of 8.

The remaining Q1 risk is no longer absence of an empirical spine. It is calibration and journal polish:

- MapGenerator caption fidelity still needs human labels, CLIP/SigLIP evidence, or agreement-scored multi-VLM adjudication.
- Choropleth visual-quality review still needs human labels or agreement-scored multi-VLM adjudication.
- The SCGM learned forest, compact MLP, patch-transfer, and trained tiny-CNN baselines reduce the risk that reviewers see the RS-to-map component as dataset-only; an official or cascade-conditioned diffusion-style reproduction would still be stronger.
- The draft needs selected journal/Taylor & Francis formatting, final repository/DOI metadata, and final citation metadata. Double-anonymized packaging and public/restricted data-code release planning are now in place.

The near-term submission path is to prepare an selected journal `Critical Challenges in GeoAI` abstract before 01 August 2026 while keeping the full manuscript track aimed at 01 December 2026.
