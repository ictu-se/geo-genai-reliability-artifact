# Dataset Reproducibility Audit

Generated from local workspace artifacts.

## Dataset Inventory

| Dataset | Size | Files | Data path | Code | Key counts |
|---|---:|---:|---|---|---|
| SCGM / CSCMG | 9.4 GB | 522485 | `data/raw/SCGM` | True | train_map_256_png=135572, train_map_missing_rs=0, train_ref_scale_2_256_png=130701, train_ref_scale_4_256_png=115595, train_rs_256_png=135572, train_rs_map_name_intersection=135572, train_rs_missing_map=0, train_rs_with_ref_scale_2=130701, ... |
| MapGenerator MGTrain/MGEval | 40.4 MB | 852 | `data/raw/MapGenerator` | True | MGEval_has_descriptions_xlsx=True, MGEval_images=100, MapTrain_has_descriptions_xlsx=True, MapTrain_images=750 |
| ChatGPT choropleth materials | 473.9 MB | 113 | `data/repos/Materials-for-Creating-maps-by-Artificial-Intelligence` | True | choropleth_csv=1, choropleth_shp=2, code_notebooks=20, interactive_html=10, static_png=33 |
| Generative AI mapmaking code | 246.1 KB | 37 | `data/repos/generative-ai-mapmaking` | True | notebooks=0, python_files=6 |
| GeoGuard local LA County benchmark | 650.2 MB | 169 | `data/raw/geoguard` | True | csv=5, gpkg=90, tif=35 |

## Reproducibility Matrix

| Dataset | Data | Code | Reproducible now | Main blocker | First check |
|---|---|---|---|---|---|
| SCGM / CSCMG | yes | True | partial | GPU/training environment and exact evaluation protocol need setup; cascade-reference coverage is not full one-to-one. | Build subset manifest and edge-continuity metric before attempting training. |
| MapGenerator MGTrain/MGEval | yes | True | partial | Full paper PDF not local; released train image count differs from paper-note claim. | Audit image-caption consistency and released-count discrepancy. |
| ChatGPT choropleth materials | yes | yes | mostly | Original ChatGPT version/prompt environment is not frozen; outputs are static artifacts. | Use released outputs as benchmark cases for cartographic linting. |
| Generative AI mapmaking code | no_original_training_data | yes | no | Original controlled vector/raster training data are not in workspace. | Treat as method template, not a directly reproducible dataset. |
| GeoGuard local LA County benchmark | yes | yes | yes_for_local_scripts | Local benchmark rather than external paper artifact. | Use as controlled testbed for evaluator ideas, not as public dataset audit evidence. |

## Immediate Findings

- SCGM/CSCMG is the dominant local dataset by size and sample count.
- SCGM train has complete `rs_256`/`map_256` name matching, but cascade references are fewer than base pairs.
- MapGenerator release has 750 train descriptions and 100 eval descriptions locally; this should be reported against the paper-note claim of 1000 train pairs.
- The choropleth materials are best suited for low-compute reliability experiments because data, outputs, and code snippets are local.
- The Affolter-style mapmaking repo is useful as a method template, but the original training data are not local.

## Recommended First Track

1. Use this inventory as the reproducibility table.
2. Run the MapGenerator image-caption audit for caption/data quality evidence.
3. Treat choropleth outputs as a cartographic linting benchmark.
4. Move SCGM to GPU reproduction only after a subset manifest and edge-continuity metric are stable.
