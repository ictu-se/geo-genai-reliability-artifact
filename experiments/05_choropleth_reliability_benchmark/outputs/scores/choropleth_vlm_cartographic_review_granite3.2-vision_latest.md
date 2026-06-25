# Choropleth VLM Cartographic Screenshot Review

- model: `granite3.2-vision:latest`
- reviewed artifacts: 18
- scope: VLM pilot over screenshot-level QA-pass artifacts; this is a visual sanity check, not human ground truth.

## Summary

| Source group | Reviewed | Mean VLM quality | Verdict counts | Title | Legend/colorbar | Readable | Choropleth |
|---|---:|---:|---|---:|---:|---:|---:|
| reference | 3 | 0.567 | {'usable_with_minor_issues': 3} | 0 | 0 | 3 | 3 |
| repair_qwen2.5-coder_32b | 5 | 0.478 | {'usable_with_minor_issues': 3, 'failed': 1, 'weak': 1} | 0 | 0 | 4 | 5 |
| validator_repair_reference | 10 | 0.7 | {'usable_with_minor_issues': 10} | 0 | 0 | 10 | 10 |

## Reviewed Artifacts

| Source group | Kind | Score | Verdict | Main issue | Image |
|---|---|---:|---|---|---|
| reference | interactive_html | 0.700 | usable_with_minor_issues | The map is not fully visible due to the cropped area and lack of a title. | `experiments/05_choropleth_reliability_benchmark/outputs/scores/screenshot_qa/reference_reference_baseline_interactive.png` |
| reference | static_png | 0.500 | usable_with_minor_issues | The map is not properly labeled with a title and legend or color bar. | `experiments/05_choropleth_reliability_benchmark/outputs/reference_baseline/map_static.png` |
| reference | time_series_png | 0.500 | usable_with_minor_issues | The map lacks a clear title and legend, which are essential for understanding the data presented. | `experiments/05_choropleth_reliability_benchmark/outputs/reference_baseline/time_series.png` |
| repair_qwen2.5-coder_32b | static_png | 0.000 | failed | The map is not visible or readable due to the small size and lack of detail. | `experiments/05_choropleth_reliability_benchmark/outputs/runs/deepseek-coder_6.7b/rules/deepseek-coder_6.7b_rules_C001_static_burned_area_20260624_032612/map_static.png` |
| repair_qwen2.5-coder_32b | static_png | 0.000 | weak | The map is not properly oriented and the scale bar is not visible. | `experiments/05_choropleth_reliability_benchmark/outputs/runs/qwen2.5-coder_7b/rules/qwen2.5-coder_7b_rules_C003_static_full_layout_20260624_032635/map_static.png` |
| repair_qwen2.5-coder_32b | static_png | 0.540 | usable_with_minor_issues | The map is too small to discern details | `experiments/05_choropleth_reliability_benchmark/outputs/runs/qwen2.5-coder_7b/basic/qwen2.5-coder_7b_basic_C002_static_number_fires_20260624_032629/map_static.png` |
| repair_qwen2.5-coder_32b | static_png | 0.850 | usable_with_minor_issues | The map is too small to read the details clearly. | `experiments/05_choropleth_reliability_benchmark/outputs/runs/deepseek-coder_6.7b/basic/deepseek-coder_6.7b_basic_C005_geometry_repair_20260624_032606/map_static.png` |
| repair_qwen2.5-coder_32b | static_png | 1.000 | usable_with_minor_issues | The map is not fully visible due to the cropped area and lack of a title. | `experiments/05_choropleth_reliability_benchmark/outputs/runs/deepseek-coder_6.7b/basic/deepseek-coder_6.7b_basic_C003_static_full_layout_20260624_032603/map_static.png` |
| validator_repair_reference | interactive_html | 0.700 | usable_with_minor_issues | The map is not fully visible due to the cropped area and lack of a title. | `experiments/05_choropleth_reliability_benchmark/outputs/scores/screenshot_qa/validator_repair_reference_validator_C001_static_burned_area_validator_repair_reference_validator_C001_static_burned_area_20260624_022520_interactive.png` |
| validator_repair_reference | interactive_html | 0.700 | usable_with_minor_issues | The map is not fully visible due to the cropped area and lack of a title. | `experiments/05_choropleth_reliability_benchmark/outputs/scores/screenshot_qa/validator_repair_reference_validator_C002_static_number_fires_validator_repair_reference_validator_C002_static_number_fires_20260624_022526_interactive.png` |
| validator_repair_reference | interactive_html | 0.700 | usable_with_minor_issues | The map is not fully visible due to the cropped area and lack of a title. | `experiments/05_choropleth_reliability_benchmark/outputs/scores/screenshot_qa/validator_repair_reference_validator_C003_static_full_layout_validator_repair_reference_validator_C003_static_full_layout_20260624_022532_interactive.png` |
| validator_repair_reference | interactive_html | 0.700 | usable_with_minor_issues | The map is not fully visible due to the cropped area and lack of a title. | `experiments/05_choropleth_reliability_benchmark/outputs/scores/screenshot_qa/validator_repair_reference_validator_C004_missing_crs_repair_validator_repair_reference_validator_C004_missing_crs_repair_20260624_022538_interactive.png` |
| validator_repair_reference | interactive_html | 0.700 | usable_with_minor_issues | The map is not fully visible due to the cropped area and lack of a title. | `experiments/05_choropleth_reliability_benchmark/outputs/scores/screenshot_qa/validator_repair_reference_validator_C005_geometry_repair_validator_repair_reference_validator_C005_geometry_repair_20260624_022544_interactive.png` |
| validator_repair_reference | interactive_html | 0.700 | usable_with_minor_issues | The map is not fully visible due to the cropped area and lack of a title. | `experiments/05_choropleth_reliability_benchmark/outputs/scores/screenshot_qa/validator_repair_reference_validator_C006_join_diagnostics_validator_repair_reference_validator_C006_join_diagnostics_20260624_022550_interactive.png` |
| validator_repair_reference | interactive_html | 0.700 | usable_with_minor_issues | The map is not fully visible due to the cropped area and lack of a title. | `experiments/05_choropleth_reliability_benchmark/outputs/scores/screenshot_qa/validator_repair_reference_validator_C007_wrong_column_guard_validator_repair_reference_validator_C007_wrong_column_guard_20260624_022555_interactive.png` |
| validator_repair_reference | interactive_html | 0.700 | usable_with_minor_issues | The map is not fully visible due to the cropped area and lack of a title. | `experiments/05_choropleth_reliability_benchmark/outputs/scores/screenshot_qa/validator_repair_reference_validator_C008_quantile_classes_validator_repair_reference_validator_C008_quantile_classes_20260624_022601_interactive.png` |
| validator_repair_reference | interactive_html | 0.700 | usable_with_minor_issues | The map is not fully visible due to the cropped area and lack of a title. | `experiments/05_choropleth_reliability_benchmark/outputs/scores/screenshot_qa/validator_repair_reference_validator_C009_colorblind_safe_validator_repair_reference_validator_C009_colorblind_safe_20260624_022607_interactive.png` |
| validator_repair_reference | interactive_html | 0.700 | usable_with_minor_issues | The map is not fully visible due to the cropped area and lack of a title. | `experiments/05_choropleth_reliability_benchmark/outputs/scores/screenshot_qa/validator_repair_reference_validator_C010_interactive_tooltips_validator_repair_reference_validator_C010_interactive_tooltips_20260624_022613_interactive.png` |
