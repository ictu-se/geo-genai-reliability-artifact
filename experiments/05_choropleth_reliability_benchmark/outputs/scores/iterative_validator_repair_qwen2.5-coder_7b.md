# Iterative Validator-Gated Choropleth Repair Pilot

- repair model: `qwen2.5-coder:7b`
- cases: 40
- completed after iterative repair: 6

| Source model | Mode | Prompt | Iteration | Score | Passed | Complete | Failed checks |
|---|---|---|---:|---:|---:|---|---|
| deepseek-coder_6.7b | basic | C001_static_burned_area | 3 | 0.500 | 2/4 | False | execution_success, static_png |
| deepseek-coder_6.7b | basic | C002_static_number_fires | 3 | 0.500 | 2/4 | False | execution_success, static_png |
| deepseek-coder_6.7b | basic | C004_missing_crs_repair | 3 | 0.571 | 4/7 | False | execution_success, static_png, diagnostic_json |
| deepseek-coder_6.7b | basic | C006_join_diagnostics | 3 | 0.500 | 3/6 | False | execution_success, static_png, diagnostic_json |
| deepseek-coder_6.7b | basic | C007_wrong_column_guard | 3 | 0.600 | 3/5 | False | execution_success, diagnostic_json |
| deepseek-coder_6.7b | basic | C008_quantile_classes | 3 | 0.400 | 2/5 | False | execution_success, static_png, diagnostic_json |
| deepseek-coder_6.7b | basic | C009_colorblind_safe | 3 | 0.500 | 3/6 | False | execution_success, static_png, diagnostic_json |
| deepseek-coder_6.7b | basic | C010_interactive_tooltips | 3 | 0.500 | 2/4 | False | execution_success, interactive_html |
| deepseek-coder_6.7b | rules | C002_static_number_fires | 3 | 0.500 | 2/4 | False | execution_success, static_png |
| deepseek-coder_6.7b | rules | C003_static_full_layout | 3 | 0.833 | 5/6 | False | static_png |
| deepseek-coder_6.7b | rules | C004_missing_crs_repair | 1 | 1.000 | 7/7 | True |  |
| deepseek-coder_6.7b | rules | C005_geometry_repair | 3 | 1.000 | 7/7 | True |  |
| deepseek-coder_6.7b | rules | C006_join_diagnostics | 3 | 0.500 | 3/6 | False | execution_success, static_png, diagnostic_json |
| deepseek-coder_6.7b | rules | C008_quantile_classes | 3 | 0.400 | 2/5 | False | execution_success, static_png, diagnostic_json |
| deepseek-coder_6.7b | rules | C009_colorblind_safe | 3 | 0.500 | 3/6 | False | execution_success, static_png, diagnostic_json |
| deepseek-coder_6.7b | rules | C010_interactive_tooltips | 3 | 0.500 | 2/4 | False | execution_success, interactive_html |
| deepseek-coder_6.7b | rules | C011_static_and_interactive | 3 | 0.333 | 2/6 | False | execution_success, static_png, interactive_html, diagnostic_json |
| deepseek-coder_6.7b | rules | C012_time_series_report | 3 | 0.400 | 2/5 | False | execution_success, time_series_png, diagnostic_json |
| qwen2.5-coder_7b | basic | C001_static_burned_area | 3 | 0.500 | 2/4 | False | execution_success, static_png |
| qwen2.5-coder_7b | basic | C003_static_full_layout | 3 | 0.500 | 3/6 | False | execution_success, static_png, diagnostic_json |
| qwen2.5-coder_7b | basic | C004_missing_crs_repair | 2 | 1.000 | 7/7 | True |  |
| qwen2.5-coder_7b | basic | C005_geometry_repair | 3 | 0.571 | 4/7 | False | execution_success, static_png, diagnostic_json |
| qwen2.5-coder_7b | basic | C006_join_diagnostics | 3 | 0.500 | 3/6 | False | execution_success, static_png, diagnostic_json |
| qwen2.5-coder_7b | basic | C007_wrong_column_guard | 1 | 1.000 | 5/5 | True |  |
| qwen2.5-coder_7b | basic | C008_quantile_classes | 3 | 0.400 | 2/5 | False | execution_success, static_png, diagnostic_json |
| qwen2.5-coder_7b | basic | C009_colorblind_safe | 2 | 1.000 | 6/6 | True |  |
| qwen2.5-coder_7b | basic | C010_interactive_tooltips | 3 | 0.500 | 2/4 | False | execution_success, interactive_html |
| qwen2.5-coder_7b | basic | C011_static_and_interactive | 3 | 0.500 | 3/6 | False | execution_success, static_png, interactive_html |
| qwen2.5-coder_7b | basic | C012_time_series_report | 3 | 0.400 | 2/5 | False | execution_success, time_series_png, diagnostic_json |
| qwen2.5-coder_7b | rules | C001_static_burned_area | 3 | 0.500 | 2/4 | False | execution_success, static_png |
| qwen2.5-coder_7b | rules | C002_static_number_fires | 3 | 0.500 | 2/4 | False | execution_success, static_png |
| qwen2.5-coder_7b | rules | C004_missing_crs_repair | 3 | 0.571 | 4/7 | False | execution_success, static_png, diagnostic_json |
| qwen2.5-coder_7b | rules | C005_geometry_repair | 3 | 0.571 | 4/7 | False | execution_success, static_png, diagnostic_json |
| qwen2.5-coder_7b | rules | C006_join_diagnostics | 3 | 0.500 | 3/6 | False | execution_success, static_png, diagnostic_json |
| qwen2.5-coder_7b | rules | C007_wrong_column_guard | 3 | 0.600 | 3/5 | False | execution_success, diagnostic_json |
| qwen2.5-coder_7b | rules | C008_quantile_classes | 3 | 0.400 | 2/5 | False | execution_success, static_png, diagnostic_json |
| qwen2.5-coder_7b | rules | C009_colorblind_safe | 3 | 0.500 | 3/6 | False | execution_success, static_png, diagnostic_json |
| qwen2.5-coder_7b | rules | C010_interactive_tooltips | 3 | 0.500 | 2/4 | False | execution_success, interactive_html |
| qwen2.5-coder_7b | rules | C011_static_and_interactive | 3 | 0.333 | 2/6 | False | execution_success, static_png, interactive_html, diagnostic_json |
| qwen2.5-coder_7b | rules | C012_time_series_report | 2 | 1.000 | 5/5 | True |  |
