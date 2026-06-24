# Data Sources and Redistribution Notes

This file is the review-facing data-source manifest for the Geo-GenAI reliability manuscript. It summarizes the datasets and repositories used locally and states how they should be handled in a public reproducibility release.

## SCGM / CSCMG

- Role in manuscript: remote-sensing-to-map generation, split reproducibility, cascade-reference coverage, edge continuity, retrieval, forest, and MLP generated-output baselines.
- Upstream repository: `https://github.com/Magician-MO/SCGM`
- Local audit source: upstream repository plus CSCMG archive linked from the upstream README.
- Local evidence produced by this study: split manifests, complete-reference subset manifests, edge-continuity metrics, retrieval metrics, forest metrics, MLP metrics, contact sheets, and summary JSON files.
- Redistribution status: raw archive and extracted tiles should be source-linked, not redistributed, unless upstream terms explicitly permit redistribution in the final deposit.
- Rebuild instruction: obtain the upstream data, place it in the expected local layout, then run `experiments/03_scgm_subset_reproduction/scripts/build_scgm_manifest.py` followed by the SCGM metric/baseline scripts.

## MapGenerator / MGTrain and MGEval

- Role in manuscript: text-to-map image-caption reproducibility, caption audit, proxy image-text review, and local VLM caption-fidelity pilot.
- Upstream repository: `https://github.com/AGI-GIS/MapGenerator`
- Local audit source: upstream repository `data.zip`.
- Local evidence produced by this study: pair inventory, missing-file audit, caption heuristic flags, proxy review, VLM review CSVs, paired VLM agreement table, and contact sheets.
- Redistribution status: raw images/captions should be source-linked, not redistributed, unless upstream license terms explicitly permit redistribution in the final deposit.
- Rebuild instruction: obtain the upstream `data.zip`, extract it into the expected local layout, then run the scripts in `experiments/02_mapgenerator_image_text_audit/scripts/`.

## Materials for Creating Maps by Artificial Intelligence

- Role in manuscript: choropleth geodata linting, released artifact QA, deterministic reference baseline, LLM code-generation benchmark, validator-gated repair, screenshot QA, and local VLM cartographic-quality pilot.
- Upstream repository: `https://github.com/GeoAI-Map/Materials-for-Creating-maps-by-Artificial-Intelligence`
- Local audit source: upstream repository, including `data_choropleth`.
- Local evidence produced by this study: geodata lint outputs, released artifact audit, generated scripts, safety scans, execution logs, repair manifests, screenshot QA, VLM reviews, and summary tables.
- Redistribution status: raw upstream repository contents should be source-linked or mirrored only if final license review permits it. Generated scripts and derived QA outputs from this study can be released unless they embed restricted upstream content.
- Rebuild instruction: clone the upstream repository into the expected local layout, then run the linter and choropleth benchmark scripts in `experiments/01_choropleth_llm_linter/scripts/` and `experiments/05_choropleth_reliability_benchmark/scripts/`.

## Generative AI Mapmaking / Cartographic ControlNet

- Role in manuscript: reproducibility comparison for a ControlNet-style cartographic generation project with code and model references but without a packaged local training/evaluation dataset.
- Upstream repository: `https://github.com/claudaff/generative-ai-mapmaking`
- Local audit source: upstream code repository.
- Local evidence produced by this study: dataset/repository inventory and reproducibility matrix entries.
- Redistribution status: source-link the upstream repository; do not include external map-sheet or model-weight artifacts unless license review permits them.
- Rebuild instruction: use the dataset reproducibility audit scripts to regenerate the inventory row from a local clone.

## Unavailable or Dynamic Sources

The audit also records papers or projects whose claimed repositories were unavailable, dynamic, API-derived, or not packaged as reusable datasets at the time of local inspection. These items should remain in the reproducibility matrix as negative or partial evidence rather than being replaced by newly scraped data that would not reproduce the original artifact.

## Public Release Rule

The public package should contain this manifest, all project-created scripts, derived tables, JSON summaries, safety scans, prompts, logs, contact sheets, and manuscript figures. Raw third-party data should be replaced by source links and reconstruction instructions whenever redistribution rights are unclear.

