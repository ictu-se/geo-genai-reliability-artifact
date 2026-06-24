# Cross-Paradigm Reliability Matrix

Scores are 0-3 diagnostic ratings derived from local evidence. They are not universal quality scores; they make the evidence balance comparable across artifact types.

## Summary

| Paradigm | Dimensions | Total | Mean | Lowest | Highest |
|---|---:|---:|---:|---:|---:|
| LLM-generated choropleth maps | 7 | 15 | 2.14 | 2 | 3 |
| Remote-sensing-to-map tiles | 7 | 14 | 2.00 | 1 | 3 |
| Text-to-map image data | 7 | 9 | 1.29 | 0 | 3 |

## Matrix

| Paradigm | Dimension | Score | Label | Evidence | Caveat |
|---|---|---:|---|---|---|
| Text-to-map image data | release_reproducibility | 2 | partial_with_validation | 850 local image-caption pairs with no missing images; local train count differs from survey-note claim. | Dataset is usable locally, but paper-level count reconciliation remains a reproducibility caveat. |
| Text-to-map image data | data_grounding | 1 | weak_or_proxy | Proxy review mean score about 0.930; paired VLM exact verdict agreement 3/20. | Caption fidelity is measurable but not yet human-ground-truth validated. |
| Text-to-map image data | spatial_faithfulness | 1 | weak_or_proxy | Caption heuristics include relation/feature checks, but no generated topology or georeferenced geometry is available. | Raster images are map-like artifacts, not geospatially executable map data. |
| Text-to-map image data | artifact_validity | 3 | strong_in_current_scope | All local images exist and parse; contact sheets and review CSVs are generated. | Validity here is file/image validity, not correctness of generated geography. |
| Text-to-map image data | cartographic_completeness | 1 | weak_or_proxy | Proxy/VLM layers inspect visible features and labels on sampled images. | No expert cartographic rubric has been applied to the full dataset. |
| Text-to-map image data | evaluator_robustness | 1 | weak_or_proxy | 17 of 20 paired cases are urgent human-adjudication cases. | VLM feature agreement is high, but semantic support thresholds differ sharply. |
| Text-to-map image data | repairability | 0 | not_demonstrated | No edit/repair loop is available for raster image-caption pairs in the local artifact chain. | Repairability would require caption revision, image regeneration, or vectorized outputs. |
| Remote-sensing-to-map tiles | release_reproducibility | 2 | partial_with_validation | Base RS-map pairs are complete for train (135572) and validation (1473); cascade references are incomplete. | Original diffusion reproduction remains blocked by model/compute details. |
| Remote-sensing-to-map tiles | data_grounding | 3 | strong_in_current_scope | RS and target map tiles match one-to-one by tile id in the local base pairs. | Cascade-reference conditioning coverage is weaker than base-pair coverage. |
| Remote-sensing-to-map tiles | spatial_faithfulness | 2 | partial_with_validation | Edge continuity is measured for targets and generated outputs; best generated edge mean is 4.612 (learned forest). | Low edge discontinuity can reflect smoothing rather than correct cartographic topology. |
| Remote-sensing-to-map tiles | artifact_validity | 3 | strong_in_current_scope | Six leakage-guarded generated-output baselines each produce 100 validation maps and metric CSVs. | Generated outputs are diagnostics, not full SCGM diffusion reproductions. |
| Remote-sensing-to-map tiles | cartographic_completeness | 1 | weak_or_proxy | Best SSIM baseline is learned forest at 0.409, but contact sheets show smoothing and missing fine map detail. | Image metrics do not verify roads, labels, symbols, or topology. |
| Remote-sensing-to-map tiles | evaluator_robustness | 2 | partial_with_validation | Metrics are deterministic and regenerated from CSV/JSON outputs. | No human/VLM cartographic quality labels are attached to SCGM generated tiles. |
| Remote-sensing-to-map tiles | repairability | 1 | weak_or_proxy | The generated-output harness can score replacement outputs from future CNN/pix2pix/diffusion models. | No automatic repair loop exists for failed tile generations. |
| LLM-generated choropleth maps | release_reproducibility | 2 | partial_with_validation | Local data, prompts, generated code, safety scans, run logs, artifacts, and validator outputs are preserved. | Original historical ChatGPT environment/model version is not frozen. |
| LLM-generated choropleth maps | data_grounding | 2 | partial_with_validation | Rules prompts, geodata linting, known columns, CRS repair, and validator feedback are explicit in the benchmark. | Initial local model generations still fail to produce complete artifacts. |
| LLM-generated choropleth maps | spatial_faithfulness | 2 | partial_with_validation | CRS, geometry validity, join diagnostics, and screenshot-level checks are part of scoring. | The benchmark covers one wildfire choropleth domain, not all thematic map types. |
| LLM-generated choropleth maps | artifact_validity | 2 | partial_with_validation | Initial local model conditions complete 0 artifacts; iterative 32B repair completes 25/40; validator/reference completes 12; screenshot QA pass artifacts total 44. | Positive controls prove feasibility, but local LLM completion remains uneven. |
| LLM-generated choropleth maps | cartographic_completeness | 2 | partial_with_validation | Two-VLM visual review has exact agreement 13/18 and coarse agreement 14/18. | Visual review is still VLM-pilot evidence rather than expert human scoring. |
| LLM-generated choropleth maps | evaluator_robustness | 2 | partial_with_validation | 4 task-model rows are agreement-panel VLM runs; failed candidate judges are also recorded. | Human labels are still the strongest missing evaluator-validity upgrade. |
| LLM-generated choropleth maps | repairability | 3 | strong_in_current_scope | Iterative validator-gated repair completes 25 of 40 previously incomplete one-pass repairs, with safety scans on every attempt. | Repair success is model- and task-dependent; deterministic validator/reference is an oracle-style upper bound. |

## Interpretation

- Text-to-map image data are file-complete but weakest on evaluator agreement and repairability.
- Remote-sensing-to-map tiles have strong base-pair grounding and generated-output diagnostics, but image metrics and continuity scores do not prove cartographic completeness.
- LLM-generated choropleth maps are initially brittle, yet their editable artifact chain makes validation and repair more operational than in raster-only workflows.
