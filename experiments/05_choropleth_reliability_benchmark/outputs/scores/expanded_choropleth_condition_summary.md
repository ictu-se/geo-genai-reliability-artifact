# Expanded Choropleth Benchmark Condition Summary

| Model | Mode | Prompt | Condition | Attempts | Best score | Best passed | Execution any | Failed checks |
|---|---|---|---|---:|---:|---:|---|---|
| deepseek-coder_6.7b | basic | C001_static_burned_area | initial | 1 | 0.250 | 1/4 | False | execution_success, uses_known_files, static_png |
| deepseek-coder_6.7b | basic | C001_static_burned_area | repair_by_qwen2.5-coder_32b | 1 | 0.500 | 2/4 | False | execution_success, static_png |
| deepseek-coder_6.7b | basic | C002_static_number_fires | initial | 1 | 0.250 | 1/4 | False | execution_success, uses_known_files, static_png |
| deepseek-coder_6.7b | basic | C002_static_number_fires | repair_by_qwen2.5-coder_32b | 1 | 0.500 | 2/4 | False | execution_success, static_png |
| deepseek-coder_6.7b | basic | C003_static_full_layout | initial | 1 | 0.167 | 1/6 | False | execution_success, uses_env_vars, uses_known_files, static_png, diagnostic_json |
| deepseek-coder_6.7b | basic | C003_static_full_layout | repair_by_qwen2.5-coder_32b | 1 | 1.000 | 6/6 | True |  |
| deepseek-coder_6.7b | basic | C004_missing_crs_repair | initial | 1 | 0.286 | 2/7 | False | execution_success, uses_known_files, static_png, diagnostic_json, mentions_geometry_repair |
| deepseek-coder_6.7b | basic | C004_missing_crs_repair | repair_by_qwen2.5-coder_32b | 1 | 0.571 | 4/7 | False | execution_success, static_png, diagnostic_json |
| deepseek-coder_6.7b | basic | C005_geometry_repair | initial | 1 | 0.143 | 1/7 | False | execution_success, uses_known_files, static_png, diagnostic_json, mentions_crs, mentions_geometry_repair |
| deepseek-coder_6.7b | basic | C005_geometry_repair | repair_by_qwen2.5-coder_32b | 1 | 1.000 | 7/7 | True |  |
| deepseek-coder_6.7b | basic | C006_join_diagnostics | initial | 1 | 0.167 | 1/6 | False | execution_success, uses_known_files, static_png, diagnostic_json, mentions_crs |
| deepseek-coder_6.7b | basic | C006_join_diagnostics | repair_by_qwen2.5-coder_32b | 1 | 0.500 | 3/6 | False | execution_success, static_png, diagnostic_json |
| deepseek-coder_6.7b | basic | C007_wrong_column_guard | initial | 1 | 0.000 | 0/5 | False | execution_success, uses_env_vars, uses_known_files, diagnostic_json, mentions_crs |
| deepseek-coder_6.7b | basic | C007_wrong_column_guard | repair_by_qwen2.5-coder_32b | 1 | 0.600 | 3/5 | False | execution_success, diagnostic_json |
| deepseek-coder_6.7b | basic | C008_quantile_classes | initial | 1 | 0.000 | 0/5 | False | execution_success, uses_env_vars, uses_known_files, static_png, diagnostic_json |
| deepseek-coder_6.7b | basic | C008_quantile_classes | repair_by_qwen2.5-coder_32b | 1 | 0.400 | 2/5 | False | execution_success, static_png, diagnostic_json |
| deepseek-coder_6.7b | basic | C009_colorblind_safe | initial | 1 | 0.000 | 0/6 | False | execution_success, uses_env_vars, uses_known_files, static_png, diagnostic_json, mentions_crs |
| deepseek-coder_6.7b | basic | C009_colorblind_safe | repair_by_qwen2.5-coder_32b | 1 | 0.500 | 3/6 | False | execution_success, static_png, diagnostic_json |
| deepseek-coder_6.7b | basic | C010_interactive_tooltips | initial | 1 | 0.500 | 2/4 | True | uses_known_files, interactive_html |
| deepseek-coder_6.7b | basic | C010_interactive_tooltips | repair_by_qwen2.5-coder_32b | 1 | 0.500 | 2/4 | False | execution_success, interactive_html |
| deepseek-coder_6.7b | rules | C001_static_burned_area | initial | 1 | 0.500 | 2/4 | False | execution_success, static_png |
| deepseek-coder_6.7b | rules | C001_static_burned_area | repair_by_qwen2.5-coder_32b | 1 | 1.000 | 4/4 | True |  |
| deepseek-coder_6.7b | rules | C002_static_number_fires | initial | 1 | 0.500 | 2/4 | False | execution_success, static_png |
| deepseek-coder_6.7b | rules | C002_static_number_fires | repair_by_qwen2.5-coder_32b | 1 | 0.500 | 2/4 | False | execution_success, static_png |
| deepseek-coder_6.7b | rules | C003_static_full_layout | initial | 1 | 0.833 | 5/6 | True | static_png |
| deepseek-coder_6.7b | rules | C003_static_full_layout | repair_by_qwen2.5-coder_32b | 1 | 0.833 | 5/6 | True | static_png |
| deepseek-coder_6.7b | rules | C004_missing_crs_repair | initial | 1 | 0.571 | 4/7 | False | execution_success, static_png, diagnostic_json |
| deepseek-coder_6.7b | rules | C004_missing_crs_repair | repair_by_qwen2.5-coder_32b | 1 | 0.571 | 4/7 | False | execution_success, static_png, diagnostic_json |
| deepseek-coder_6.7b | rules | C005_geometry_repair | initial | 1 | 0.571 | 4/7 | False | execution_success, static_png, diagnostic_json |
| deepseek-coder_6.7b | rules | C005_geometry_repair | repair_by_qwen2.5-coder_32b | 1 | 0.714 | 5/7 | False | execution_success, static_png |
| deepseek-coder_6.7b | rules | C006_join_diagnostics | initial | 1 | 0.500 | 3/6 | False | execution_success, static_png, diagnostic_json |
| deepseek-coder_6.7b | rules | C006_join_diagnostics | repair_by_qwen2.5-coder_32b | 1 | 0.500 | 3/6 | False | execution_success, static_png, diagnostic_json |
| deepseek-coder_6.7b | rules | C007_wrong_column_guard | initial | 1 | 0.400 | 2/5 | False | execution_success, diagnostic_json, mentions_crs |
| deepseek-coder_6.7b | rules | C007_wrong_column_guard | repair_by_qwen2.5-coder_32b | 1 | 1.000 | 5/5 | True |  |
| deepseek-coder_6.7b | rules | C008_quantile_classes | initial | 1 | 0.400 | 2/5 | False | execution_success, static_png, diagnostic_json |
| deepseek-coder_6.7b | rules | C008_quantile_classes | repair_by_qwen2.5-coder_32b | 1 | 0.400 | 2/5 | False | execution_success, static_png, diagnostic_json |
| deepseek-coder_6.7b | rules | C009_colorblind_safe | initial | 1 | 0.500 | 3/6 | False | execution_success, static_png, diagnostic_json |
| deepseek-coder_6.7b | rules | C009_colorblind_safe | repair_by_qwen2.5-coder_32b | 1 | 0.500 | 3/6 | False | execution_success, static_png, diagnostic_json |
| deepseek-coder_6.7b | rules | C010_interactive_tooltips | initial | 1 | 0.500 | 2/4 | False | execution_success, interactive_html |
| deepseek-coder_6.7b | rules | C010_interactive_tooltips | repair_by_qwen2.5-coder_32b | 1 | 0.500 | 2/4 | False | execution_success, interactive_html |
| deepseek-coder_6.7b | rules | C011_static_and_interactive | initial | 1 | 0.333 | 2/6 | False | execution_success, static_png, interactive_html, diagnostic_json |
| deepseek-coder_6.7b | rules | C011_static_and_interactive | repair_by_qwen2.5-coder_32b | 1 | 0.333 | 2/6 | False | execution_success, static_png, interactive_html, diagnostic_json |
| deepseek-coder_6.7b | rules | C012_time_series_report | initial | 1 | 0.400 | 2/5 | False | execution_success, time_series_png, diagnostic_json |
| deepseek-coder_6.7b | rules | C012_time_series_report | repair_by_qwen2.5-coder_32b | 1 | 0.400 | 2/5 | False | execution_success, time_series_png, diagnostic_json |
| qwen2.5-coder_7b | basic | C001_static_burned_area | initial | 1 | 0.000 | 0/4 | False | execution_success, uses_env_vars, uses_known_files, static_png |
| qwen2.5-coder_7b | basic | C001_static_burned_area | repair_by_qwen2.5-coder_32b | 1 | 0.500 | 2/4 | False | execution_success, static_png |
| qwen2.5-coder_7b | basic | C001_static_burned_area | repair_by_qwen2.5-coder_7b | 3 | 0.500 | 2/4 | False | execution_success, static_png |
| qwen2.5-coder_7b | basic | C002_static_number_fires | initial | 1 | 0.250 | 1/4 | False | execution_success, uses_known_files, static_png |
| qwen2.5-coder_7b | basic | C002_static_number_fires | repair_by_qwen2.5-coder_32b | 1 | 1.000 | 4/4 | True |  |
| qwen2.5-coder_7b | basic | C002_static_number_fires | repair_by_qwen2.5-coder_7b | 3 | 0.500 | 2/4 | False | execution_success, static_png |
| qwen2.5-coder_7b | basic | C003_static_full_layout | initial | 1 | 0.167 | 1/6 | False | execution_success, uses_env_vars, uses_known_files, static_png, diagnostic_json |
| qwen2.5-coder_7b | basic | C003_static_full_layout | repair_by_qwen2.5-coder_32b | 1 | 0.500 | 3/6 | False | execution_success, static_png, diagnostic_json |
| qwen2.5-coder_7b | basic | C003_static_full_layout | repair_by_qwen2.5-coder_7b | 3 | 0.500 | 3/6 | False | execution_success, static_png, diagnostic_json |
| qwen2.5-coder_7b | basic | C004_missing_crs_repair | initial | 1 | 0.143 | 1/7 | False | execution_success, uses_env_vars, uses_known_files, static_png, diagnostic_json, mentions_geometry_repair |
| qwen2.5-coder_7b | basic | C004_missing_crs_repair | repair_by_qwen2.5-coder_32b | 1 | 0.571 | 4/7 | False | execution_success, static_png, diagnostic_json |
| qwen2.5-coder_7b | basic | C005_geometry_repair | initial | 1 | 0.143 | 1/7 | False | execution_success, uses_env_vars, uses_known_files, static_png, diagnostic_json, mentions_crs |
| qwen2.5-coder_7b | basic | C005_geometry_repair | repair_by_qwen2.5-coder_32b | 1 | 0.571 | 4/7 | False | execution_success, static_png, diagnostic_json |
| qwen2.5-coder_7b | basic | C006_join_diagnostics | initial | 1 | 0.000 | 0/6 | False | execution_success, uses_env_vars, uses_known_files, static_png, diagnostic_json, mentions_crs |
| qwen2.5-coder_7b | basic | C006_join_diagnostics | repair_by_qwen2.5-coder_32b | 1 | 0.500 | 3/6 | False | execution_success, static_png, diagnostic_json |
| qwen2.5-coder_7b | basic | C007_wrong_column_guard | initial | 1 | 0.000 | 0/5 | False | execution_success, uses_env_vars, uses_known_files, diagnostic_json, mentions_crs |
| qwen2.5-coder_7b | basic | C007_wrong_column_guard | repair_by_qwen2.5-coder_32b | 1 | 0.600 | 3/5 | False | execution_success, diagnostic_json |
| qwen2.5-coder_7b | basic | C008_quantile_classes | initial | 1 | 0.000 | 0/5 | False | execution_success, uses_env_vars, uses_known_files, static_png, diagnostic_json |
| qwen2.5-coder_7b | basic | C008_quantile_classes | repair_by_qwen2.5-coder_32b | 1 | 0.400 | 2/5 | False | execution_success, static_png, diagnostic_json |
| qwen2.5-coder_7b | basic | C009_colorblind_safe | initial | 1 | 0.000 | 0/6 | False | execution_success, uses_env_vars, uses_known_files, static_png, diagnostic_json, mentions_crs |
| qwen2.5-coder_7b | basic | C009_colorblind_safe | repair_by_qwen2.5-coder_32b | 1 | 0.500 | 3/6 | False | execution_success, static_png, diagnostic_json |
| qwen2.5-coder_7b | basic | C010_interactive_tooltips | initial | 1 | 0.000 | 0/4 | False | execution_success, uses_env_vars, uses_known_files, interactive_html |
| qwen2.5-coder_7b | basic | C010_interactive_tooltips | repair_by_qwen2.5-coder_32b | 1 | 0.500 | 2/4 | False | execution_success, interactive_html |
| qwen2.5-coder_7b | basic | C011_static_and_interactive | initial | 1 | 0.000 | 0/6 | False | execution_success, uses_env_vars, uses_known_files, static_png, interactive_html, diagnostic_json |
| qwen2.5-coder_7b | basic | C011_static_and_interactive | repair_by_qwen2.5-coder_32b | 1 | 0.333 | 2/6 | False | execution_success, static_png, interactive_html, diagnostic_json |
| qwen2.5-coder_7b | basic | C012_time_series_report | initial | 1 | 0.000 | 0/5 | False | execution_success, uses_env_vars, uses_known_files, time_series_png, diagnostic_json |
| qwen2.5-coder_7b | basic | C012_time_series_report | repair_by_qwen2.5-coder_32b | 1 | 0.400 | 2/5 | False | execution_success, time_series_png, diagnostic_json |
| qwen2.5-coder_7b | rules | C001_static_burned_area | initial | 1 | 0.500 | 2/4 | False | execution_success, static_png |
| qwen2.5-coder_7b | rules | C001_static_burned_area | repair_by_qwen2.5-coder_32b | 1 | 0.500 | 2/4 | False | execution_success, static_png |
| qwen2.5-coder_7b | rules | C001_static_burned_area | repair_by_qwen2.5-coder_7b | 1 | 0.500 | 2/4 | False | execution_success, static_png |
| qwen2.5-coder_7b | rules | C002_static_number_fires | initial | 1 | 0.500 | 2/4 | False | execution_success, static_png |
| qwen2.5-coder_7b | rules | C002_static_number_fires | repair_by_qwen2.5-coder_32b | 1 | 0.500 | 2/4 | False | execution_success, static_png |
| qwen2.5-coder_7b | rules | C002_static_number_fires | repair_by_qwen2.5-coder_7b | 1 | 0.500 | 2/4 | False | execution_success, static_png |
| qwen2.5-coder_7b | rules | C003_static_full_layout | initial | 1 | 0.500 | 3/6 | False | execution_success, static_png, diagnostic_json |
| qwen2.5-coder_7b | rules | C003_static_full_layout | repair_by_qwen2.5-coder_32b | 1 | 1.000 | 6/6 | True |  |
| qwen2.5-coder_7b | rules | C003_static_full_layout | repair_by_qwen2.5-coder_7b | 1 | 0.500 | 3/6 | False | execution_success, static_png, diagnostic_json |
| qwen2.5-coder_7b | rules | C004_missing_crs_repair | initial | 1 | 0.571 | 4/7 | False | execution_success, static_png, diagnostic_json |
| qwen2.5-coder_7b | rules | C004_missing_crs_repair | repair_by_qwen2.5-coder_32b | 1 | 0.571 | 4/7 | False | execution_success, static_png, diagnostic_json |
| qwen2.5-coder_7b | rules | C005_geometry_repair | initial | 1 | 0.571 | 4/7 | False | execution_success, static_png, diagnostic_json |
| qwen2.5-coder_7b | rules | C005_geometry_repair | repair_by_qwen2.5-coder_32b | 1 | 0.571 | 4/7 | False | execution_success, static_png, diagnostic_json |
| qwen2.5-coder_7b | rules | C006_join_diagnostics | initial | 1 | 0.500 | 3/6 | False | execution_success, static_png, diagnostic_json |
| qwen2.5-coder_7b | rules | C006_join_diagnostics | repair_by_qwen2.5-coder_32b | 1 | 0.500 | 3/6 | False | execution_success, static_png, diagnostic_json |
| qwen2.5-coder_7b | rules | C007_wrong_column_guard | initial | 1 | 0.600 | 3/5 | False | execution_success, diagnostic_json |
| qwen2.5-coder_7b | rules | C007_wrong_column_guard | repair_by_qwen2.5-coder_32b | 1 | 0.600 | 3/5 | False | execution_success, diagnostic_json |
| qwen2.5-coder_7b | rules | C008_quantile_classes | initial | 1 | 0.400 | 2/5 | False | execution_success, static_png, diagnostic_json |
| qwen2.5-coder_7b | rules | C008_quantile_classes | repair_by_qwen2.5-coder_32b | 1 | 0.400 | 2/5 | False | execution_success, static_png, diagnostic_json |
| qwen2.5-coder_7b | rules | C009_colorblind_safe | initial | 1 | 0.500 | 3/6 | False | execution_success, static_png, diagnostic_json |
| qwen2.5-coder_7b | rules | C009_colorblind_safe | repair_by_qwen2.5-coder_32b | 1 | 0.500 | 3/6 | False | execution_success, static_png, diagnostic_json |
| qwen2.5-coder_7b | rules | C010_interactive_tooltips | initial | 1 | 0.500 | 2/4 | False | execution_success, interactive_html |
| qwen2.5-coder_7b | rules | C010_interactive_tooltips | repair_by_qwen2.5-coder_32b | 1 | 0.500 | 2/4 | False | execution_success, interactive_html |
| qwen2.5-coder_7b | rules | C011_static_and_interactive | initial | 1 | 0.333 | 2/6 | False | execution_success, static_png, interactive_html, diagnostic_json |
| qwen2.5-coder_7b | rules | C011_static_and_interactive | repair_by_qwen2.5-coder_32b | 1 | 0.333 | 2/6 | False | execution_success, static_png, interactive_html, diagnostic_json |
| qwen2.5-coder_7b | rules | C012_time_series_report | initial | 1 | 0.400 | 2/5 | False | execution_success, time_series_png, diagnostic_json |
| qwen2.5-coder_7b | rules | C012_time_series_report | repair_by_qwen2.5-coder_32b | 1 | 0.400 | 2/5 | False | execution_success, time_series_png, diagnostic_json |
| validator_repair_reference | validator | C001_static_burned_area | initial | 1 | 1.000 | 4/4 | True |  |
| validator_repair_reference | validator | C002_static_number_fires | initial | 1 | 1.000 | 4/4 | True |  |
| validator_repair_reference | validator | C003_static_full_layout | initial | 1 | 1.000 | 6/6 | True |  |
| validator_repair_reference | validator | C004_missing_crs_repair | initial | 1 | 1.000 | 7/7 | True |  |
| validator_repair_reference | validator | C005_geometry_repair | initial | 1 | 1.000 | 7/7 | True |  |
| validator_repair_reference | validator | C006_join_diagnostics | initial | 1 | 1.000 | 6/6 | True |  |
| validator_repair_reference | validator | C007_wrong_column_guard | initial | 1 | 1.000 | 5/5 | True |  |
| validator_repair_reference | validator | C008_quantile_classes | initial | 1 | 1.000 | 5/5 | True |  |
| validator_repair_reference | validator | C009_colorblind_safe | initial | 1 | 1.000 | 6/6 | True |  |
| validator_repair_reference | validator | C010_interactive_tooltips | initial | 1 | 1.000 | 4/4 | True |  |
| validator_repair_reference | validator | C011_static_and_interactive | initial | 1 | 1.000 | 6/6 | True |  |
| validator_repair_reference | validator | C012_time_series_report | initial | 1 | 1.000 | 5/5 | True |  |
