# Release License and Redistribution Audit

This audit converts the remaining license gate into a concrete release matrix. It is not legal advice and does not replace the final author/license decision before DOI deposit.

## Summary

- Release rows: 9
- Author-controlled rows: 2
- Source-link/restricted rows: 5
- Final license decision remains manual until the public repository and DOI metadata are created.

## Release Matrix

| Artifact family | Terms | Release posture | Public release action | Evidence |
|---|---|---|---|---|
| project_created_code | author-controlled | choose an OSI-compatible code license for project-created code | Recommended action: add a top-level LICENSE for project-created code and note that third-party data are excluded/source-linked. | manuscripts/q1_geo_genai_reliability/scripts; experiments/*/scripts |
| project_created_manuscript_evidence | author-controlled-with-third-party-context | release derived summaries openly when they do not embed restricted upstream data | Recommended action: license derived metadata/tables separately from raw third-party data; use source links for reconstructing restricted inputs. | submission/reproducibility_manifest.csv; tables; figures; derived outputs |
| SCGM | CC-BY-4.0 | source-link raw data; derived metrics may be released with attribution notes | Retain upstream attribution; do not redistribute bulky raw tiles unless final license review confirms scope. | data/repos/SCGM/LICENSE |
| MapGenerator | research-preview-noncommercial-readme | source-link only for raw data and upstream content | Exclude raw images/captions from open DOI package; release only derived audit summaries and reconstruction instructions. | data/repos/MapGenerator/README.md |
| Materials-for-Creating-maps-by-Artificial-Intelligence | CC0-1.0 | source-link or include only if third-party embedded data rights remain compatible | Do not assume all nested data are rights-cleared; include attribution/source note even when CC0 applies. | data/repos/Materials-for-Creating-maps-by-Artificial-Intelligence/LICENSE |
| generative-ai-mapmaking | no-license-file-readme-only | source-link only until license terms are confirmed | Exclude raw upstream content from public package; retain URL/commit/access notes. | data/repos/generative-ai-mapmaking/README.md |
| local_llm_vlm_outputs | model-output-policy-dependent | release as study evidence if model/output terms permit | Preserve prompts, model names, timestamps, and safety scans; recheck local model licenses before public upload. | experiments/05_choropleth_reliability_benchmark/outputs; submission/evaluator_reliability |
| model_weights_and_checkpoints | not_redistributed | source-link or documented acquisition only | Do not upload weights/checkpoints unless the license explicitly permits redistribution. | release plan excludes local model caches and weights |
| double_anonymous_review_package | review-only | keep blinded artifacts separate from non-blinded DOI metadata | Upload blinded files to review portal; add non-blinded authors/DOI/license only after review-route policy is confirmed. | submission/blinded_main_manuscript.md; submission/blinded_compact_main_manuscript.md |

## Recommended Release Posture

1. Add a top-level license for project-created code only after the author chooses the final license.
2. Release derived CSV/JSON summaries, tables, scripts, prompts, QA ledgers, and manifests as the public reproducibility core.
3. Exclude or source-link raw SCGM, MapGenerator, choropleth, map-sheet, and model-weight artifacts unless the final license review confirms redistribution rights.
4. Keep blinded review files separate from non-blinded repository DOI, author metadata, and license metadata.
