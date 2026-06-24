# Manuscript Tables

## Table 1. Local Geo-GenAI artifact inventory

| Dataset | Artifact type | Size | Files | Code | Local path |
| --- | --- | --- | --- | --- | --- |
| SCGM / CSCMG | remote-sensing-to-map tile pairs | 9.4 GB | 522485 | True | data/raw/SCGM |
| MapGenerator MGTrain/MGEval | map image and natural-language description pairs | 40.4 MB | 852 | True | data/raw/MapGenerator |
| ChatGPT choropleth materials | prompt outputs, choropleth data, static/interactive maps | 473.9 MB | 113 | True | data/repos/Materials-for-Creating-maps-by-Artificial-Intelligence |
| Generative AI mapmaking code | ControlNet-style training/evaluation code | 246.1 KB | 37 | True | data/repos/generative-ai-mapmaking |
| GeoGuard local LA County benchmark | vector/raster GIS data and generated workflow outputs | 650.2 MB | 169 | True | data/raw/geoguard |

## Table 2. Reproducibility matrix

| Dataset | Data | Code | Reproducible | Main blocker |
| --- | --- | --- | --- | --- |
| SCGM / CSCMG | yes | True | partial | GPU/training environment and exact evaluation protocol need setup; cascade-reference coverage is not full one-to-one. |
| MapGenerator MGTrain/MGEval | yes | True | partial | Full paper PDF not local; released train image count differs from paper-note claim. |
| ChatGPT choropleth materials | yes | yes | mostly | Original ChatGPT version/prompt environment is not frozen; outputs are static artifacts. |
| Generative AI mapmaking code | no_original_training_data | yes | no | Original controlled vector/raster training data are not in workspace. |
| GeoGuard local LA County benchmark | yes | yes | yes_for_local_scripts | Local benchmark rather than external paper artifact. |

## Table 3. MapGenerator caption audit

| Split | Pairs | Missing images | Image size | Avg words | No relation | Generic no-feature | No named feature |
| --- | --- | --- | --- | --- | --- | --- | --- |
| MapTrain | 750 | 0 | 1024x1024 | 50.67 | 315 | 79 | 29 |
| MGEval | 100 | 0 | 1024x1024 | 54.11 | 38 | 13 | 2 |

## Table 4. SCGM split and cascade-reference coverage

| Split | RS | Map | Matched | Ref 2x | Ref 4x | Zooms |
| --- | --- | --- | --- | --- | --- | --- |
| train | 135572 | 135572 | 135572 | 130701 | 115595 | {"14": 4871, "15": 15106, "16": 30040, "17": 40555, "18": 45000} |
| val | 1473 | 1473 | 1473 | 1192 | 900 | {"14": 281, "15": 292, "16": 300, "17": 300, "18": 300} |

## Table 5. SCGM validation edge-continuity baseline

| Group | Pairs | Mean | Median | P90 | Max |
| --- | --- | --- | --- | --- | --- |
| val/map_256/down | 27 | 2.752893 | 2.083333 | 6.082031 | 9.467448 |
| val/map_256/right | 32 | 1.853434 | 1.104167 | 3.544401 | 9.363281 |
| val/rs_256/down | 27 | 13.467978 | 15.924479 | 19.422134 | 23.701822 |
| val/rs_256/right | 32 | 11.520061 | 10.635417 | 17.91901 | 21.700521 |

## Table 5b. SCGM lightweight retrieval generated-output baseline

| Metric | Mean | Median | P10 | P90 | Note |
| --- | --- | --- | --- | --- | --- |
| train candidates | 200 |  |  |  | exact tile candidates excluded=6 |
| validation outputs | 100 |  |  |  | same-zoom retrievals=100 |
| MAE RGB | 16.767246 | 16.875938 | 4.401522 | 30.814087 | retrieval baseline |
| PSNR RGB | 19.931509 | 18.702965 | 16.768648 | 24.497568 | retrieval baseline |
| Global SSIM luma | 0.245472 | 0.229878 | 0.068687 | 0.457476 | retrieval baseline |
| Generated edge continuity | 20.089735 | 22.808594 | 5.73802 | 35.796093 | retrieval baseline |

## Table 5c. SCGM generated-output baseline comparison

| Baseline | Validation outputs | Leakage guard | MAE RGB mean | PSNR mean | SSIM luma mean | Edge continuity mean |
| --- | --- | --- | --- | --- | --- | --- |
| color-stat retrieval | 100 | 6 | 16.767246 | 19.931509 | 0.245472 | 20.089735 |
| multi-feature retrieval | 100 | 6 | 21.684555 | 19.187075 | 0.290337 | 24.089735 |
| learned forest | 100 | 6 | 17.362703 | 21.608828 | 0.409008 | 4.611871 |
| neural MLP | 100 | 6 | 30.725883 | 17.955496 | 0.303307 | 12.132487 |
| local-context ridge | 100 | 6 | 17.542248 | 21.193199 | 0.361186 | 8.075412 |
| convolutional filter-bank ridge | 100 | 6 | 19.14752 | 20.752409 | 0.347422 | 6.235243 |
| patch-embedding retrieval | 100 | 6 | 16.335779 | 19.992807 | 0.273621 | 11.403972 |
| trained tiny CNN | 100 | 6 | 26.100397 | 18.466171 | 0.366129 | 9.221896 |

## Table 5d. SCGM mosaic neighbor-seam stress audit

| Baseline | Neighbor pairs | Missing pairs | Generated seam mean | Target seam mean | Stress ratio mean | Stress ratio p90 | Interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| color-stat retrieval | 12 | 12 | 20.089735 | 4.467556 | 10.695079 | 14.855922 | seam score; lower can also indicate over-smoothing |
| multi-feature retrieval | 12 | 12 | 24.089735 | 4.467556 | 11.765274 | 17.107949 | seam score; lower can also indicate over-smoothing |
| learned forest | 12 | 12 | 4.611871 | 4.467556 | 1.75489 | 2.921877 | seam score; lower can also indicate over-smoothing |
| neural MLP | 12 | 12 | 12.132487 | 4.467556 | 15.686329 | 10.629434 | seam score; lower can also indicate over-smoothing |
| local-context ridge | 12 | 12 | 8.075412 | 4.467556 | 2.876555 | 3.653725 | seam score; lower can also indicate over-smoothing |
| convolutional filter-bank ridge | 12 | 12 | 6.235243 | 4.467556 | 2.33258 | 2.808676 | seam score; lower can also indicate over-smoothing |
| patch-embedding retrieval | 12 | 12 | 11.403971 | 4.467556 | 5.200429 | 8.198448 | seam score; lower can also indicate over-smoothing |
| trained tiny CNN | 12 | 12 | 9.221897 | 4.467556 | 3.392778 | 6.487469 | seam score; lower can also indicate over-smoothing |

## Table 6. Choropleth data and artifact QA

| Component | Items | Errors | Warnings | Finding |
| --- | --- | --- | --- | --- |
| Input geodata lint |  | 2 | 0 | boundary.shp.valid_geometry: 1 geometries are invalid.; mainlandburn.shp.crs: Shapefile has no CRS. The coordinates look like lon/lat, but a renderer should explicitly set EPSG:4326. |
| Released map artifacts | 43 | 0 | 0 | {'png': 33, 'html': 10}; QA flags={} |

## Table 7. Seed LLM choropleth candidate benchmark

| Prompt | Candidate | Score | Passed | Failed checks |
| --- | --- | --- | --- | --- |
| P01_static_basic | p01_static_basic_naive.py | 1.0 | 2/2 |  |
| P02_static_with_crs_repair | p02_static_with_crs_repair.py | 1.0 | 3/3 |  |
| P03_interactive_basic | p03_interactive_basic.py | 1.0 | 2/2 |  |
| P04_csv_time_series | p04_csv_time_series.py | 1.0 | 3/3 |  |
| P05_robust_cartographic_output | reference_solution.py | 1.0 | 5/5 |  |
| P05_wrong_column | p05_wrong_column_failure.py | 0.0 | 0/5 | execution_success, static, interactive, crs_repair, diagnostic_report |

## Table 8. Literature claim vs local artifact availability

| Paper | Paradigm | Scale | Local data | Local code | Status |
| --- | --- | --- | --- | --- | --- |
| Affolter et al. 2025 | controlled diffusion mapmaking | 296495 training tiles reported in survey notes; 100 test tiles per style | no | partial | not_reproducible_locally |
| Sun et al. 2025 SCGM | remote-sensing-to-map diffusion | local train 135572 RS/map pairs; val 1473 RS/map pairs; cascade references incomplete | yes | yes | partially_reproducible |
| Zhang et al. 2025 MapGenerator | text-to-map diffusion | paper notes report 1000 train and 100 eval; local release has 750 train and 100 eval | yes | yes | partially_reproducible |
| Pannoon and Netek 2025 | LLM-generated choropleth code maps | local repo has 33 PNG maps, 10 HTML maps, 20 notebooks, choropleth data | yes | yes | mostly_reproducible_as_artifact_audit |
| Wang et al. 2025 CartoAgent | multimodal map style agent | human evaluation with 17 experts/students reported in survey notes | no | no | not_reproducible_locally |
| Song et al. 2025 LLM VGI mapping | LLM GIS/tool agent | qualitative case studies: Beijing/Wuhan and thematic examples | no | no | not_reproducible_locally |
| Li and Ning et al. 2025 Autonomous GIS | LLM GIS/cartography agent agenda | research agenda plus prototype cases | no | no | not_reproducible_locally |
| Yang et al. 2025 MapColorAI | LLM map design subtask | user study with 60 participants reported in survey notes | no | no | not_reproducible_locally |
| Shomer and Xu 2025 MAPLE | label-placement LLM benchmark | 883 train, 126 validation, 267 test landmarks reported in survey notes | no | no | not_reproducible_locally |
| Burghardt et al. 2025 | pictorial map generation | short abstract/prototype-level evidence | no | no | not_reproducible_locally |

## Table 9. MapGenerator proxy caption-fidelity review

| Split | Reviewed | Mean proxy score | Low | Medium | High | Top issues |
| --- | --- | --- | --- | --- | --- | --- |
| MGEval | 100 | 0.946 | 66 | 34 | 0 | road_caption_lacks_relation=15; generic_no_feature_claim_needs_visual_review=11; possible_water_omission=10 |
| MapTrain | 100 | 0.914 | 46 | 53 | 1 | generic_no_feature_claim_needs_visual_review=38; possible_water_omission=18; road_caption_lacks_relation=7 |

## Table 10. Expanded choropleth benchmark condition summary

| Model | Mode | Prompt | Condition | Attempts | Best score | Best passed | Execution |
| --- | --- | --- | --- | --- | --- | --- | --- |
| deepseek-coder_6.7b | basic | C001_static_burned_area | initial | 1 | 0.250 | 1/4 | False |
| deepseek-coder_6.7b | basic | C001_static_burned_area | repair_by_qwen2.5-coder_32b | 1 | 0.500 | 2/4 | False |
| deepseek-coder_6.7b | basic | C002_static_number_fires | initial | 1 | 0.250 | 1/4 | False |
| deepseek-coder_6.7b | basic | C002_static_number_fires | repair_by_qwen2.5-coder_32b | 1 | 0.500 | 2/4 | False |
| deepseek-coder_6.7b | basic | C003_static_full_layout | initial | 1 | 0.167 | 1/6 | False |
| deepseek-coder_6.7b | basic | C003_static_full_layout | repair_by_qwen2.5-coder_32b | 1 | 1.000 | 6/6 | True |
| deepseek-coder_6.7b | basic | C004_missing_crs_repair | initial | 1 | 0.286 | 2/7 | False |
| deepseek-coder_6.7b | basic | C004_missing_crs_repair | repair_by_qwen2.5-coder_32b | 1 | 0.571 | 4/7 | False |
| deepseek-coder_6.7b | basic | C005_geometry_repair | initial | 1 | 0.143 | 1/7 | False |
| deepseek-coder_6.7b | basic | C005_geometry_repair | repair_by_qwen2.5-coder_32b | 1 | 1.000 | 7/7 | True |
| deepseek-coder_6.7b | basic | C006_join_diagnostics | initial | 1 | 0.167 | 1/6 | False |
| deepseek-coder_6.7b | basic | C006_join_diagnostics | repair_by_qwen2.5-coder_32b | 1 | 0.500 | 3/6 | False |
| deepseek-coder_6.7b | basic | C007_wrong_column_guard | initial | 1 | 0.000 | 0/5 | False |
| deepseek-coder_6.7b | basic | C007_wrong_column_guard | repair_by_qwen2.5-coder_32b | 1 | 0.600 | 3/5 | False |
| deepseek-coder_6.7b | basic | C008_quantile_classes | initial | 1 | 0.000 | 0/5 | False |
| deepseek-coder_6.7b | basic | C008_quantile_classes | repair_by_qwen2.5-coder_32b | 1 | 0.400 | 2/5 | False |
| deepseek-coder_6.7b | basic | C009_colorblind_safe | initial | 1 | 0.000 | 0/6 | False |
| deepseek-coder_6.7b | basic | C009_colorblind_safe | repair_by_qwen2.5-coder_32b | 1 | 0.500 | 3/6 | False |
| deepseek-coder_6.7b | basic | C010_interactive_tooltips | initial | 1 | 0.500 | 2/4 | True |
| deepseek-coder_6.7b | basic | C010_interactive_tooltips | repair_by_qwen2.5-coder_32b | 1 | 0.500 | 2/4 | False |
| deepseek-coder_6.7b | rules | C001_static_burned_area | initial | 1 | 0.500 | 2/4 | False |
| deepseek-coder_6.7b | rules | C001_static_burned_area | repair_by_qwen2.5-coder_32b | 1 | 1.000 | 4/4 | True |
| deepseek-coder_6.7b | rules | C002_static_number_fires | initial | 1 | 0.500 | 2/4 | False |
| deepseek-coder_6.7b | rules | C002_static_number_fires | repair_by_qwen2.5-coder_32b | 1 | 0.500 | 2/4 | False |
| deepseek-coder_6.7b | rules | C003_static_full_layout | initial | 1 | 0.833 | 5/6 | True |
| deepseek-coder_6.7b | rules | C003_static_full_layout | repair_by_qwen2.5-coder_32b | 1 | 0.833 | 5/6 | True |
| deepseek-coder_6.7b | rules | C004_missing_crs_repair | initial | 1 | 0.571 | 4/7 | False |
| deepseek-coder_6.7b | rules | C004_missing_crs_repair | repair_by_qwen2.5-coder_32b | 1 | 0.571 | 4/7 | False |
| deepseek-coder_6.7b | rules | C005_geometry_repair | initial | 1 | 0.571 | 4/7 | False |
| deepseek-coder_6.7b | rules | C005_geometry_repair | repair_by_qwen2.5-coder_32b | 1 | 0.714 | 5/7 | False |
| deepseek-coder_6.7b | rules | C006_join_diagnostics | initial | 1 | 0.500 | 3/6 | False |
| deepseek-coder_6.7b | rules | C006_join_diagnostics | repair_by_qwen2.5-coder_32b | 1 | 0.500 | 3/6 | False |
| deepseek-coder_6.7b | rules | C007_wrong_column_guard | initial | 1 | 0.400 | 2/5 | False |
| deepseek-coder_6.7b | rules | C007_wrong_column_guard | repair_by_qwen2.5-coder_32b | 1 | 1.000 | 5/5 | True |
| deepseek-coder_6.7b | rules | C008_quantile_classes | initial | 1 | 0.400 | 2/5 | False |
| deepseek-coder_6.7b | rules | C008_quantile_classes | repair_by_qwen2.5-coder_32b | 1 | 0.400 | 2/5 | False |
| deepseek-coder_6.7b | rules | C009_colorblind_safe | initial | 1 | 0.500 | 3/6 | False |
| deepseek-coder_6.7b | rules | C009_colorblind_safe | repair_by_qwen2.5-coder_32b | 1 | 0.500 | 3/6 | False |
| deepseek-coder_6.7b | rules | C010_interactive_tooltips | initial | 1 | 0.500 | 2/4 | False |
| deepseek-coder_6.7b | rules | C010_interactive_tooltips | repair_by_qwen2.5-coder_32b | 1 | 0.500 | 2/4 | False |
| deepseek-coder_6.7b | rules | C011_static_and_interactive | initial | 1 | 0.333 | 2/6 | False |
| deepseek-coder_6.7b | rules | C011_static_and_interactive | repair_by_qwen2.5-coder_32b | 1 | 0.333 | 2/6 | False |
| deepseek-coder_6.7b | rules | C012_time_series_report | initial | 1 | 0.400 | 2/5 | False |
| deepseek-coder_6.7b | rules | C012_time_series_report | repair_by_qwen2.5-coder_32b | 1 | 0.400 | 2/5 | False |
| qwen2.5-coder_7b | basic | C001_static_burned_area | initial | 1 | 0.000 | 0/4 | False |
| qwen2.5-coder_7b | basic | C001_static_burned_area | repair_by_qwen2.5-coder_32b | 1 | 0.500 | 2/4 | False |
| qwen2.5-coder_7b | basic | C001_static_burned_area | repair_by_qwen2.5-coder_7b | 3 | 0.500 | 2/4 | False |
| qwen2.5-coder_7b | basic | C002_static_number_fires | initial | 1 | 0.250 | 1/4 | False |
| qwen2.5-coder_7b | basic | C002_static_number_fires | repair_by_qwen2.5-coder_32b | 1 | 1.000 | 4/4 | True |
| qwen2.5-coder_7b | basic | C002_static_number_fires | repair_by_qwen2.5-coder_7b | 3 | 0.500 | 2/4 | False |
| qwen2.5-coder_7b | basic | C003_static_full_layout | initial | 1 | 0.167 | 1/6 | False |
| qwen2.5-coder_7b | basic | C003_static_full_layout | repair_by_qwen2.5-coder_32b | 1 | 0.500 | 3/6 | False |
| qwen2.5-coder_7b | basic | C003_static_full_layout | repair_by_qwen2.5-coder_7b | 3 | 0.500 | 3/6 | False |
| qwen2.5-coder_7b | basic | C004_missing_crs_repair | initial | 1 | 0.143 | 1/7 | False |
| qwen2.5-coder_7b | basic | C004_missing_crs_repair | repair_by_qwen2.5-coder_32b | 1 | 0.571 | 4/7 | False |
| qwen2.5-coder_7b | basic | C005_geometry_repair | initial | 1 | 0.143 | 1/7 | False |
| qwen2.5-coder_7b | basic | C005_geometry_repair | repair_by_qwen2.5-coder_32b | 1 | 0.571 | 4/7 | False |
| qwen2.5-coder_7b | basic | C006_join_diagnostics | initial | 1 | 0.000 | 0/6 | False |
| qwen2.5-coder_7b | basic | C006_join_diagnostics | repair_by_qwen2.5-coder_32b | 1 | 0.500 | 3/6 | False |
| qwen2.5-coder_7b | basic | C007_wrong_column_guard | initial | 1 | 0.000 | 0/5 | False |
| qwen2.5-coder_7b | basic | C007_wrong_column_guard | repair_by_qwen2.5-coder_32b | 1 | 0.600 | 3/5 | False |
| qwen2.5-coder_7b | basic | C008_quantile_classes | initial | 1 | 0.000 | 0/5 | False |
| qwen2.5-coder_7b | basic | C008_quantile_classes | repair_by_qwen2.5-coder_32b | 1 | 0.400 | 2/5 | False |
| qwen2.5-coder_7b | basic | C009_colorblind_safe | initial | 1 | 0.000 | 0/6 | False |
| qwen2.5-coder_7b | basic | C009_colorblind_safe | repair_by_qwen2.5-coder_32b | 1 | 0.500 | 3/6 | False |
| qwen2.5-coder_7b | basic | C010_interactive_tooltips | initial | 1 | 0.000 | 0/4 | False |
| qwen2.5-coder_7b | basic | C010_interactive_tooltips | repair_by_qwen2.5-coder_32b | 1 | 0.500 | 2/4 | False |
| qwen2.5-coder_7b | basic | C011_static_and_interactive | initial | 1 | 0.000 | 0/6 | False |
| qwen2.5-coder_7b | basic | C011_static_and_interactive | repair_by_qwen2.5-coder_32b | 1 | 0.333 | 2/6 | False |
| qwen2.5-coder_7b | basic | C012_time_series_report | initial | 1 | 0.000 | 0/5 | False |
| qwen2.5-coder_7b | basic | C012_time_series_report | repair_by_qwen2.5-coder_32b | 1 | 0.400 | 2/5 | False |
| qwen2.5-coder_7b | rules | C001_static_burned_area | initial | 1 | 0.500 | 2/4 | False |
| qwen2.5-coder_7b | rules | C001_static_burned_area | repair_by_qwen2.5-coder_32b | 1 | 0.500 | 2/4 | False |
| qwen2.5-coder_7b | rules | C001_static_burned_area | repair_by_qwen2.5-coder_7b | 1 | 0.500 | 2/4 | False |
| qwen2.5-coder_7b | rules | C002_static_number_fires | initial | 1 | 0.500 | 2/4 | False |
| qwen2.5-coder_7b | rules | C002_static_number_fires | repair_by_qwen2.5-coder_32b | 1 | 0.500 | 2/4 | False |
| qwen2.5-coder_7b | rules | C002_static_number_fires | repair_by_qwen2.5-coder_7b | 1 | 0.500 | 2/4 | False |
| qwen2.5-coder_7b | rules | C003_static_full_layout | initial | 1 | 0.500 | 3/6 | False |
| qwen2.5-coder_7b | rules | C003_static_full_layout | repair_by_qwen2.5-coder_32b | 1 | 1.000 | 6/6 | True |
| qwen2.5-coder_7b | rules | C003_static_full_layout | repair_by_qwen2.5-coder_7b | 1 | 0.500 | 3/6 | False |
| qwen2.5-coder_7b | rules | C004_missing_crs_repair | initial | 1 | 0.571 | 4/7 | False |
| qwen2.5-coder_7b | rules | C004_missing_crs_repair | repair_by_qwen2.5-coder_32b | 1 | 0.571 | 4/7 | False |
| qwen2.5-coder_7b | rules | C005_geometry_repair | initial | 1 | 0.571 | 4/7 | False |
| qwen2.5-coder_7b | rules | C005_geometry_repair | repair_by_qwen2.5-coder_32b | 1 | 0.571 | 4/7 | False |
| qwen2.5-coder_7b | rules | C006_join_diagnostics | initial | 1 | 0.500 | 3/6 | False |
| qwen2.5-coder_7b | rules | C006_join_diagnostics | repair_by_qwen2.5-coder_32b | 1 | 0.500 | 3/6 | False |
| qwen2.5-coder_7b | rules | C007_wrong_column_guard | initial | 1 | 0.600 | 3/5 | False |
| qwen2.5-coder_7b | rules | C007_wrong_column_guard | repair_by_qwen2.5-coder_32b | 1 | 0.600 | 3/5 | False |
| qwen2.5-coder_7b | rules | C008_quantile_classes | initial | 1 | 0.400 | 2/5 | False |
| qwen2.5-coder_7b | rules | C008_quantile_classes | repair_by_qwen2.5-coder_32b | 1 | 0.400 | 2/5 | False |
| qwen2.5-coder_7b | rules | C009_colorblind_safe | initial | 1 | 0.500 | 3/6 | False |
| qwen2.5-coder_7b | rules | C009_colorblind_safe | repair_by_qwen2.5-coder_32b | 1 | 0.500 | 3/6 | False |
| qwen2.5-coder_7b | rules | C010_interactive_tooltips | initial | 1 | 0.500 | 2/4 | False |
| qwen2.5-coder_7b | rules | C010_interactive_tooltips | repair_by_qwen2.5-coder_32b | 1 | 0.500 | 2/4 | False |
| qwen2.5-coder_7b | rules | C011_static_and_interactive | initial | 1 | 0.333 | 2/6 | False |
| qwen2.5-coder_7b | rules | C011_static_and_interactive | repair_by_qwen2.5-coder_32b | 1 | 0.333 | 2/6 | False |
| qwen2.5-coder_7b | rules | C012_time_series_report | initial | 1 | 0.400 | 2/5 | False |
| qwen2.5-coder_7b | rules | C012_time_series_report | repair_by_qwen2.5-coder_32b | 1 | 0.400 | 2/5 | False |
| validator_repair_reference | validator | C001_static_burned_area | initial | 1 | 1.000 | 4/4 | True |
| validator_repair_reference | validator | C002_static_number_fires | initial | 1 | 1.000 | 4/4 | True |
| validator_repair_reference | validator | C003_static_full_layout | initial | 1 | 1.000 | 6/6 | True |
| validator_repair_reference | validator | C004_missing_crs_repair | initial | 1 | 1.000 | 7/7 | True |
| validator_repair_reference | validator | C005_geometry_repair | initial | 1 | 1.000 | 7/7 | True |
| validator_repair_reference | validator | C006_join_diagnostics | initial | 1 | 1.000 | 6/6 | True |
| validator_repair_reference | validator | C007_wrong_column_guard | initial | 1 | 1.000 | 5/5 | True |
| validator_repair_reference | validator | C008_quantile_classes | initial | 1 | 1.000 | 5/5 | True |
| validator_repair_reference | validator | C009_colorblind_safe | initial | 1 | 1.000 | 6/6 | True |
| validator_repair_reference | validator | C010_interactive_tooltips | initial | 1 | 1.000 | 4/4 | True |
| validator_repair_reference | validator | C011_static_and_interactive | initial | 1 | 1.000 | 6/6 | True |
| validator_repair_reference | validator | C012_time_series_report | initial | 1 | 1.000 | 5/5 | True |

## Table 11. Cross-paradigm metric taxonomy

| Paradigm | Artifact | Failure modes | Evaluation | Repairability |
| --- | --- | --- | --- | --- |
| Text-to-map image generation | raster map image | caption mismatch; fake geography; broken topology; unreadable labels; weak editability | image-text similarity; OCR; VLM entity/relation checks; human cartographic review | low_to_medium |
| Remote-sensing-to-map translation | paired raster map tile | tile-edge discontinuity; feature omission; scale inconsistency; weak natural-feature generalization | SSIM/PSNR/LPIPS; edge continuity; feature segmentation; zoom/content stratification | medium |
| LLM-generated GIS/code maps | Python/Folium/GeoPandas code plus rendered map | execution errors; wrong columns; CRS mistakes; invalid geometries; weak legends/classification | execution tests; GIS lint; screenshot QA; repair-loop scoring | high |
| Map style agents | stylesheet/config and rendered map | subjective style mismatch; semantic symbol errors; copyright/style leakage; weak legend semantics | style constraint checks; human/VLM preference; symbol consistency checks | medium |
| Cartographic design subtasks | color/label/symbol outputs | accessibility errors; label collisions; cultural mismatch; missing multimodal context | task-specific metrics; accessibility checks; collision metrics; user studies | medium_to_high |

## Table 12. Deterministic choropleth reference baseline

| Artifact | File | Exists | Bytes | Validation note |
| --- | --- | --- | --- | --- |
| static choropleth PNG | map_static.png | True | 307172 | mainland CRS None -> EPSG:4326 |
| interactive Folium HTML | map_interactive.html | True | 25051271 | 18 district features with tooltips |
| annual time-series PNG | time_series.png | True | 167977 | 2002-2022; max burned area year 2017 |
| diagnostic JSON | diagnostics.json | True | 1334 | boundary invalid geometries 1 -> 0 |

## Table 13. Choropleth benchmark model-mode aggregate

| Model | Mode | Generated | Safe | Unsafe | Executed | Complete | Mean score | Max score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| deepseek-coder_6.7b | basic | 12 | 10 | 2 | 1 | 0 | 0.176 | 0.500 |
| deepseek-coder_6.7b | rules | 12 | 12 | 0 | 1 | 0 | 0.501 | 0.833 |
| qwen2.5-coder_7b | basic | 12 | 12 | 0 | 0 | 0 | 0.059 | 0.250 |
| qwen2.5-coder_7b | rules | 12 | 12 | 0 | 0 | 0 | 0.490 | 0.600 |
| validator_repair_reference | validator | 12 | 12 | 0 | 12 | 12 | 1.000 | 1.000 |

## Table 14. Rendered artifact QA summary

| Source | Checked artifacts | Existing | Nonblank images | Valid HTML | Valid JSON |
| --- | --- | --- | --- | --- | --- |
| deepseek-coder_6.7b | 88 | 1 | 0 | 0 | 1 |
| qwen2.5-coder_7b | 96 | 0 | 0 | 0 | 0 |
| reference | 4 | 4 | 2 | 1 | 1 |
| repair_qwen2.5-coder_32b | 184 | 11 | 5 | 0 | 6 |
| repair_qwen2.5-coder_7b | 36 | 0 | 0 | 0 | 0 |
| validator_repair_reference | 48 | 48 | 24 | 12 | 12 |

## Table 15. MapGenerator VLM caption-fidelity pilot

| Model | Split | Reviewed | Mean VLM score | Mean proxy score | Verdicts | Errors | Unsupported rows | Omission rows |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| granite3.2-vision:latest | MGEval | 10 | 1.0 | 0.741 | supported=10 | 0 | 0 | 0 |
| granite3.2-vision:latest | MapTrain | 10 | 0.945 | 0.667 | supported=9; partly_supported=1 | 0 | 0 | 0 |
| llama3.2-vision:11b | MGEval | 10 | 0 | 0.741 | error=10 | 10 | 0 | 0 |
| llama3.2-vision:11b | MapTrain | 10 | 0 | 0.667 | error=10 | 10 | 0 | 0 |
| llava-llama3:8b | MGEval | 10 | 0.3 | 0.741 | =2; partly_supported=5; error=3 | 3 | 0 | 0 |
| llava-llama3:8b | MapTrain | 10 | 0.356 | 0.667 | =3; error=1; partly_supported=6 | 1 | 0 | 0 |
| minicpm-v:latest | MGEval | 10 | 0 | 0.741 | error=10 | 10 | 0 | 0 |
| minicpm-v:latest | MapTrain | 10 | 0.8 | 0.667 | partly_supported=1; error=9 | 9 | 0 | 1 |
| qwen2.5vl:3b | MGEval | 10 | 0.88 | 0.741 | partly_supported=10 | 0 | 10 | 4 |
| qwen2.5vl:3b | MapTrain | 10 | 0.89 | 0.667 | partly_supported=8; supported=2 | 0 | 8 | 5 |
| qwen3-vl:4b | MGEval | 5 | 0.7 | 0.69 | partly_supported=1; error=4 | 4 | 1 | 0 |
| qwen3-vl:4b | MapTrain | 5 | 0 | 0.644 | error=5 | 5 | 0 | 0 |

## Table 15b. MapGenerator two-VLM caption agreement pilot

| Scope | Paired items | Exact verdict agreement | Supported/below agreement | Both supported | Mean score Granite | Mean score Qwen | Score Pearson r | Qwen lower score | Feature agreement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| overall | 20 | 3/20 | 3/20 | 2 | 0.972 | 0.885 | 0.420 | 15/20 | 73/79 |
| MGEval | 10 | 0/10 | 0/10 | 0 | 1.000 | 0.880 |  | 9/10 | 35/39 |
| MapTrain | 10 | 3/10 | 3/10 | 2 | 0.945 | 0.890 | 0.754 | 6/10 | 38/40 |

## Table 15c. MapGenerator CLIP caption-embedding scoring

| Group | Items | Mean CLIP score | Min CLIP score | Max CLIP score | Proxy-score Pearson r | Note |
| --- | --- | --- | --- | --- | --- | --- |
| overall | 200 | 0.342781 | 0.260293 | 0.441454 |  | model=openai/clip-vit-base-patch32; errors=0 |
| proxy severity: high | 1 | 0.316893 | 0.316893 | 0.316893 |  | CLIP is a screening metric, not human ground truth |
| proxy severity: low | 112 | 0.340465 | 0.260293 | 0.441454 | 0.000000 | CLIP is a screening metric, not human ground truth |
| proxy severity: medium | 87 | 0.346061 | 0.290746 | 0.418686 | 0.026007 | CLIP is a screening metric, not human ground truth |
| split: MGEval | 100 | 0.339040 | 0.260293 | 0.438895 | 0.059427 | CLIP is a screening metric, not human ground truth |
| split: MapTrain | 100 | 0.346522 | 0.275674 | 0.441454 | -0.085032 | CLIP is a screening metric, not human ground truth |

## Table 16. Screenshot-level choropleth artifact QA

| Source | Artifact kind | Checked | Existing | HTML rendered | Screenshot QA pass | Pass rate existing |
| --- | --- | --- | --- | --- | --- | --- |
| deepseek-coder_6.7b | interactive_html | 22 | 0 | 0 | 0 | 0.000 |
| deepseek-coder_6.7b | static_png | 22 | 0 |  | 0 | 0.000 |
| deepseek-coder_6.7b | time_series_png | 22 | 0 |  | 0 | 0.000 |
| qwen2.5-coder_7b | interactive_html | 24 | 0 | 0 | 0 | 0.000 |
| qwen2.5-coder_7b | static_png | 24 | 0 |  | 0 | 0.000 |
| qwen2.5-coder_7b | time_series_png | 24 | 0 |  | 0 | 0.000 |
| reference | interactive_html | 1 | 1 | 1 | 1 | 1.000 |
| reference | static_png | 1 | 1 |  | 1 | 1.000 |
| reference | time_series_png | 1 | 1 |  | 1 | 1.000 |
| repair_qwen2.5-coder_32b | interactive_html | 46 | 0 | 0 | 0 | 0.000 |
| repair_qwen2.5-coder_32b | static_png | 46 | 5 |  | 5 | 1.000 |
| repair_qwen2.5-coder_32b | time_series_png | 46 | 0 |  | 0 | 0.000 |
| repair_qwen2.5-coder_7b | interactive_html | 9 | 0 | 0 | 0 | 0.000 |
| repair_qwen2.5-coder_7b | static_png | 9 | 0 |  | 0 | 0.000 |
| repair_qwen2.5-coder_7b | time_series_png | 9 | 0 |  | 0 | 0.000 |
| validator_repair_reference | interactive_html | 12 | 12 | 12 | 12 | 1.000 |
| validator_repair_reference | static_png | 12 | 12 |  | 12 | 1.000 |
| validator_repair_reference | time_series_png | 12 | 12 |  | 12 | 1.000 |

## Table 17. Geo-GenAI map-generation literature taxonomy

| Work | Paradigm | Generated artifact | Control signal | Evaluation style | Reliability gap |
| --- | --- | --- | --- | --- | --- |
| Affolter et al. 2025 | controlled diffusion map tiles | raster map tile | rasterized vector semantics + text style prompt | visual inspection + cartographer user study | topology, labels, tile seams, GIS integration |
| Sun et al. 2025 SCGM | remote-sensing-to-map diffusion | multi-scale map tile | remote sensing image + scale encoding + cascade references | quantitative image metrics + ablations | natural landscapes, long-range continuity, missing public reproduction details |
| Zhang et al. 2025 MapGenerator | text-to-map diffusion | map-like raster image | natural-language map caption | text-map dataset and generation examples | caption fidelity, spatial relations, dataset-count reproducibility |
| Wang et al. 2025 CartoAgent | MLLM cartographic style agent | stylesheet and styled map | inspiration image + vector/style ecosystem | expert/student human evaluation + MLLM reviewer | formal constraints beyond style, reviewer calibration |
| Song et al. 2025 VGI mapping agent | LLM GIS workflow agent | thematic map workflow/output | natural-language request + OSM/VGI tools | qualitative case studies | benchmarking, VGI quality, automated cartographic completeness |
| Li & Ning et al. 2025 | autonomous GIS agenda | GIS workflows and result-aware agents | LLM/tool orchestration + visual review | agenda + proof-of-concept systems | result-aware validation and explicit map-design rubrics |
| Pannoon & Netek 2025 | LLM-generated choropleth code | static and interactive choropleth maps | prompted ChatGPT-4 code generation | case-study outputs | execution logs, data linting, repair, artifact completeness |
| Yang et al. 2025 MapColorAI | LLM map-design subtask | choropleth color scheme | theme/data semantics + color theory | user study | accessibility, cultural context, multimodal style grounding |
| Shomer & Xu 2025 MAPLE | LLM map-label placement | label coordinates | guideline RAG + map context | RMSE against benchmark labels | rendered-layout reasoning, occlusion, scale/context generalization |
| Kang & Wang 2026 | GenAI cartography perspective | research agenda | cartographic workflow analysis | conceptual synthesis | operational benchmarks and ethical governance |

## Table 18. Choropleth VLM cartographic-quality pilot

| Model | Source | Reviewed | Mean VLM quality | Verdicts | Title | Legend/colorbar | Readable | Choropleth |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| granite3.2-vision:latest | reference | 3 | 0.567 | usable_with_minor_issues=3 | 0 | 0 | 3 | 3 |
| granite3.2-vision:latest | repair_qwen2.5-coder_32b | 5 | 0.478 | usable_with_minor_issues=3; failed=1; weak=1 | 0 | 0 | 4 | 5 |
| granite3.2-vision:latest | validator_repair_reference | 10 | 0.7 | usable_with_minor_issues=10 | 0 | 0 | 10 | 10 |
| llava-llama3:8b | reference | 3 | 0.5 | error=2; usable_with_minor_issues=1 | 0 | 0 | 1 | 1 |
| llava-llama3:8b | repair_qwen2.5-coder_32b | 5 | 0.165 | error=1; weak=2; publication_ready=1; usable_with_minor_issues=1 | 4 | 3 | 3 | 4 |
| llava-llama3:8b | validator_repair_reference | 10 | 0 | error=10 | 0 | 0 | 0 | 0 |
| qwen2.5vl:3b | reference | 3 | 0.4 | usable_with_minor_issues=2; failed=1 | 2 | 2 | 2 | 3 |
| qwen2.5vl:3b | repair_qwen2.5-coder_32b | 5 | 0.22 | failed=5 | 4 | 4 | 1 | 5 |
| qwen2.5vl:3b | validator_repair_reference | 10 | 0.3 | usable_with_minor_issues=10 | 0 | 10 | 10 | 10 |

## Table 18b. Choropleth two-VLM cartographic-quality agreement pilot

| Scope | Paired artifacts | Exact verdict agreement | Usable/below agreement | Both usable | Mean score Granite | Mean score Qwen | Score Pearson r | Qwen lower score | Component agreement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| overall | 18 | 13/18 | 14/18 | 12 | 0.616 | 0.294 | -0.058 | 15/18 | 80/108 |
| reference | 3 | 2/3 | 2/3 | 2 | 0.567 | 0.400 | -0.327 | 2/3 | 13/18 |
| repair_qwen2.5-coder_32b | 5 | 1/5 | 2/5 | 0 | 0.478 | 0.220 | -0.572 | 3/5 | 17/30 |
| validator_repair_reference | 10 | 10/10 | 10/10 | 10 | 0.700 | 0.300 | -1.000 | 10/10 | 50/60 |

## Table 19. Iterative validator-gated choropleth repair pilot

| Source model | Mode | Prompt | One-pass score | Final iteration | Final score | Passed | Complete | Failed checks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| deepseek-coder_6.7b | basic | C001_static_burned_area | 0.500 | 3 | 0.750 | 3/4 | False | execution_success |
| deepseek-coder_6.7b | basic | C002_static_number_fires | 0.500 | 2 | 1.000 | 4/4 | True |  |
| deepseek-coder_6.7b | basic | C004_missing_crs_repair | 0.571 | 3 | 0.857 | 6/7 | False | execution_success |
| deepseek-coder_6.7b | basic | C006_join_diagnostics | 0.500 | 3 | 0.833 | 5/6 | False | static_png |
| deepseek-coder_6.7b | basic | C007_wrong_column_guard | 0.600 | 2 | 1.000 | 5/5 | True |  |
| deepseek-coder_6.7b | basic | C008_quantile_classes | 0.400 | 3 | 0.600 | 3/5 | False | execution_success, diagnostic_json |
| deepseek-coder_6.7b | basic | C009_colorblind_safe | 0.500 | 2 | 1.000 | 6/6 | True |  |
| deepseek-coder_6.7b | basic | C010_interactive_tooltips | 0.500 | 3 | 0.500 | 2/4 | False | execution_success, interactive_html |
| deepseek-coder_6.7b | rules | C002_static_number_fires | 0.500 | 2 | 1.000 | 4/4 | True |  |
| deepseek-coder_6.7b | rules | C003_static_full_layout | 0.833 | 3 | 0.833 | 5/6 | False | static_png |
| deepseek-coder_6.7b | rules | C004_missing_crs_repair | 0.571 | 1 | 1.000 | 7/7 | True |  |
| deepseek-coder_6.7b | rules | C005_geometry_repair | 0.714 | 1 | 1.000 | 7/7 | True |  |
| deepseek-coder_6.7b | rules | C006_join_diagnostics | 0.500 | 3 | 0.667 | 4/6 | False | execution_success, static_png |
| deepseek-coder_6.7b | rules | C008_quantile_classes | 0.400 | 3 | 0.400 | 2/5 | False | execution_success, static_png, diagnostic_json |
| deepseek-coder_6.7b | rules | C009_colorblind_safe | 0.500 | 1 | 1.000 | 6/6 | True |  |
| deepseek-coder_6.7b | rules | C010_interactive_tooltips | 0.500 | 2 | 1.000 | 4/4 | True |  |
| deepseek-coder_6.7b | rules | C011_static_and_interactive | 0.333 | 3 | 1.000 | 6/6 | True |  |
| deepseek-coder_6.7b | rules | C012_time_series_report | 0.400 | 3 | 1.000 | 5/5 | True |  |
| qwen2.5-coder_7b | basic | C001_static_burned_area | 0.500 | 2 | 1.000 | 4/4 | True |  |
| qwen2.5-coder_7b | basic | C003_static_full_layout | 0.500 | 3 | 0.500 | 3/6 | False | execution_success, static_png, diagnostic_json |
| qwen2.5-coder_7b | basic | C004_missing_crs_repair | 0.571 | 1 | 1.000 | 7/7 | True |  |
| qwen2.5-coder_7b | basic | C005_geometry_repair | 0.571 | 1 | 1.000 | 7/7 | True |  |
| qwen2.5-coder_7b | basic | C006_join_diagnostics | 0.500 | 3 | 0.500 | 3/6 | False | execution_success, static_png, diagnostic_json |
| qwen2.5-coder_7b | basic | C007_wrong_column_guard | 0.600 | 2 | 1.000 | 5/5 | True |  |
| qwen2.5-coder_7b | basic | C008_quantile_classes | 0.400 | 1 | 1.000 | 5/5 | True |  |
| qwen2.5-coder_7b | basic | C009_colorblind_safe | 0.500 | 2 | 1.000 | 6/6 | True |  |
| qwen2.5-coder_7b | basic | C010_interactive_tooltips | 0.500 | 1 | 1.000 | 4/4 | True |  |
| qwen2.5-coder_7b | basic | C011_static_and_interactive | 0.333 | 3 | 0.500 | 3/6 | False | execution_success, static_png, interactive_html |
| qwen2.5-coder_7b | basic | C012_time_series_report | 0.400 | 1 | 1.000 | 5/5 | True |  |
| qwen2.5-coder_7b | rules | C001_static_burned_area | 0.500 | 1 | 1.000 | 4/4 | True |  |
| qwen2.5-coder_7b | rules | C002_static_number_fires | 0.500 | 3 | 0.500 | 2/4 | False | execution_success, static_png |
| qwen2.5-coder_7b | rules | C004_missing_crs_repair | 0.571 | 3 | 1.000 | 7/7 | True |  |
| qwen2.5-coder_7b | rules | C005_geometry_repair | 0.571 | 2 | 1.000 | 7/7 | True |  |
| qwen2.5-coder_7b | rules | C006_join_diagnostics | 0.500 | 3 | 0.667 | 4/6 | False | execution_success, static_png |
| qwen2.5-coder_7b | rules | C007_wrong_column_guard | 0.600 | 3 | 0.800 | 4/5 | False | execution_success |
| qwen2.5-coder_7b | rules | C008_quantile_classes | 0.400 | 1 | 1.000 | 5/5 | True |  |
| qwen2.5-coder_7b | rules | C009_colorblind_safe | 0.500 | 2 | 1.000 | 6/6 | True |  |
| qwen2.5-coder_7b | rules | C010_interactive_tooltips | 0.500 | 3 | 1.000 | 4/4 | True |  |
| qwen2.5-coder_7b | rules | C011_static_and_interactive | 0.333 | 3 | 0.333 | 2/6 | False | execution_success, static_png, interactive_html, diagnostic_json |
| qwen2.5-coder_7b | rules | C012_time_series_report | 0.400 | 2 | 1.000 | 5/5 | True |  |

## Table 20. Iterative repair model comparison

| Repair model | Scope | Cases | Max iters | Attempt rows | Safe attempts | Completed | Completion rate | Mean final score | Completed by iter |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:32b | full incomplete one-pass set | 40 | 3 | 89 | 89 | 25 | 25/40 | 0.856 | iter 1: 10; iter 2: 11; iter 3: 4 |
| qwen2.5-coder:14b | near-miss pilot subset | 8 | 2 | 14 | 14 | 3 | 3/8 | 0.829 | iter 1: 2; iter 2: 1 |
| qwen2.5-coder:7b | near-miss pilot subset | 8 | 2 | 14 | 14 | 3 | 3/8 | 0.808 | iter 1: 2; iter 2: 1 |
| deepseek-coder:6.7b | near-miss pilot subset | 8 | 2 | 10 | 4 | 0 | 0/8 | 0.204 | none |

## Table 21. Evaluator adjudication and human-priority queue

| Task | Items | Exact agreement | Coarse agreement | Urgent human adjudication | High priority | Stable/low priority | Mean score gap |
| --- | --- | --- | --- | --- | --- | --- | --- |
| MapGenerator caption fidelity | 20 | 3/20 | 3/20 | 17 | 0 | 3 | 0.093 |
| Choropleth cartographic quality | 18 | 13/18 | 14/18 | 4 | 2 | 10 | 0.399 |

## Table 22. VLM judge robustness and schema-adherence audit

| Task | Model | Reviewed | Usable | Errors | Usable rate pct | Panel role |
| --- | --- | --- | --- | --- | --- | --- |
| Choropleth cartographic quality | granite3.2-vision:latest | 18 | 18 | 0 | 100.0 | agreement_panel |
| Choropleth cartographic quality | qwen2.5vl:3b | 18 | 18 | 0 | 100.0 | agreement_panel |
| Choropleth cartographic quality | llava-llama3:8b | 18 | 5 | 13 | 27.8 | failed_candidate |
| MapGenerator caption fidelity | granite3.2-vision:latest | 20 | 20 | 0 | 100.0 | agreement_panel |
| MapGenerator caption fidelity | qwen2.5vl:3b | 20 | 20 | 0 | 100.0 | agreement_panel |
| MapGenerator caption fidelity | llava-llama3:8b | 20 | 16 | 4 | 80.0 | candidate_partial |
| MapGenerator caption fidelity | llama3.2-vision:11b | 20 | 0 | 20 | 0.0 | failed_candidate |
| MapGenerator caption fidelity | minicpm-v:latest | 20 | 1 | 19 | 5.0 | failed_candidate |
| MapGenerator caption fidelity | qwen3-vl:4b | 10 | 1 | 9 | 10.0 | failed_candidate |

## Table 23. Cross-paradigm reliability summary

| Paradigm | Dimensions | Total score | Mean score | Lowest score | Highest score |
| --- | --- | --- | --- | --- | --- |
| LLM-generated choropleth maps | 7 | 15 | 2.14 | 2 | 3 |
| Remote-sensing-to-map tiles | 7 | 14 | 2.00 | 1 | 3 |
| Text-to-map image data | 7 | 9 | 1.29 | 0 | 3 |

## Table 25. Matched repair-model suite

| Repair model | Matched cases | Attempt rows | Safe attempts | Unsafe attempts | Completed cases | Completion rate | Mean final score | Top remaining failed checks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:14b | 8 | 14 | 14 | 0 | 3 | 3/8 | 0.829 | execution_success: 9; static_png: 6; diagnostic_json: 5 |
| qwen2.5-coder:7b | 8 | 14 | 14 | 0 | 3 | 3/8 | 0.808 | execution_success: 9; diagnostic_json: 7; static_png: 5 |
| deepseek-coder:6.7b | 8 | 10 | 4 | 6 | 0 | 0/8 | 0.204 | unsafe:syntax_error:invalid syntax: 5; static_png: 2; execution_success: 2; diagnostic_json: 1 |
