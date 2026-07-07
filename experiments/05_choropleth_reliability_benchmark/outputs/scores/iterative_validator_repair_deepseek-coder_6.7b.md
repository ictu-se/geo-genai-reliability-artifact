# Iterative Validator-Gated Choropleth Repair Pilot

- repair model: `deepseek-coder:6.7b`
- cases: 40
- completed after iterative repair: 2

| Source model | Mode | Prompt | Iteration | Score | Passed | Complete | Failed checks |
|---|---|---|---:|---:|---:|---|---|
| deepseek-coder_6.7b | basic | C001_static_burned_area | 3 | 0.000 | 0/0 | False | unsafe:syntax_error:invalid syntax |
| deepseek-coder_6.7b | basic | C002_static_number_fires | 1 | 0.000 | 0/0 | False | unsafe:syntax_error:invalid syntax |
| deepseek-coder_6.7b | basic | C004_missing_crs_repair | 3 | 0.000 | 0/0 | False | unsafe:syntax_error:unexpected EOF while parsing |
| deepseek-coder_6.7b | basic | C006_join_diagnostics | 1 | 0.000 | 0/0 | False | unsafe:syntax_error:invalid syntax |
| deepseek-coder_6.7b | basic | C007_wrong_column_guard | 3 | 0.000 | 0/0 | False | unsafe:syntax_error:invalid syntax |
| deepseek-coder_6.7b | basic | C008_quantile_classes | 1 | 0.000 | 0/0 | False | unsafe:syntax_error:invalid syntax |
| deepseek-coder_6.7b | basic | C009_colorblind_safe | 1 | 0.000 | 0/0 | False | unsafe:syntax_error:invalid syntax |
| deepseek-coder_6.7b | basic | C010_interactive_tooltips | 2 | 0.000 | 0/0 | False | unsafe:syntax_error:invalid syntax |
| deepseek-coder_6.7b | rules | C002_static_number_fires | 3 | 0.500 | 2/4 | False | execution_success, static_png |
| deepseek-coder_6.7b | rules | C003_static_full_layout | 3 | 0.000 | 0/0 | False | unsafe:syntax_error:invalid syntax |
| deepseek-coder_6.7b | rules | C004_missing_crs_repair | 2 | 0.000 | 0/0 | False | unsafe:syntax_error:invalid syntax |
| deepseek-coder_6.7b | rules | C005_geometry_repair | 3 | 0.000 | 0/0 | False | unsafe:syntax_error:invalid syntax |
| deepseek-coder_6.7b | rules | C006_join_diagnostics | 1 | 0.000 | 0/0 | False | unsafe:syntax_error:invalid syntax |
| deepseek-coder_6.7b | rules | C008_quantile_classes | 2 | 0.000 | 0/0 | False | unsafe:syntax_error:invalid syntax |
| deepseek-coder_6.7b | rules | C009_colorblind_safe | 1 | 0.000 | 0/0 | False | unsafe:syntax_error:invalid syntax |
| deepseek-coder_6.7b | rules | C010_interactive_tooltips | 1 | 0.000 | 0/0 | False | unsafe:syntax_error:invalid syntax |
| deepseek-coder_6.7b | rules | C011_static_and_interactive | 2 | 0.000 | 0/0 | False | unsafe:syntax_error:invalid syntax |
| deepseek-coder_6.7b | rules | C012_time_series_report | 1 | 0.000 | 0/0 | False | unsafe:syntax_error:invalid syntax |
| qwen2.5-coder_7b | basic | C001_static_burned_area | 2 | 0.000 | 0/0 | False | unsafe:syntax_error:invalid syntax |
| qwen2.5-coder_7b | basic | C003_static_full_layout | 1 | 0.000 | 0/0 | False | unsafe:syntax_error:EOL while scanning string literal |
| qwen2.5-coder_7b | basic | C004_missing_crs_repair | 2 | 1.000 | 7/7 | True |  |
| qwen2.5-coder_7b | basic | C005_geometry_repair | 1 | 0.000 | 0/0 | False | unsafe:syntax_error:invalid syntax |
| qwen2.5-coder_7b | basic | C006_join_diagnostics | 1 | 0.000 | 0/0 | False | unsafe:syntax_error:invalid syntax |
| qwen2.5-coder_7b | basic | C007_wrong_column_guard | 3 | 0.000 | 0/0 | False | unsafe:syntax_error:invalid syntax |
| qwen2.5-coder_7b | basic | C008_quantile_classes | 1 | 0.000 | 0/0 | False | unsafe:syntax_error:invalid syntax |
| qwen2.5-coder_7b | basic | C009_colorblind_safe | 1 | 0.000 | 0/0 | False | unsafe:syntax_error:invalid syntax |
| qwen2.5-coder_7b | basic | C010_interactive_tooltips | 1 | 0.000 | 0/0 | False | unsafe:syntax_error:invalid syntax |
| qwen2.5-coder_7b | basic | C011_static_and_interactive | 1 | 0.000 | 0/0 | False | unsafe:syntax_error:invalid syntax |
| qwen2.5-coder_7b | basic | C012_time_series_report | 2 | 1.000 | 5/5 | True |  |
| qwen2.5-coder_7b | rules | C001_static_burned_area | 1 | 0.000 | 0/0 | False | unsafe:syntax_error:invalid syntax |
| qwen2.5-coder_7b | rules | C002_static_number_fires | 1 | 0.000 | 0/0 | False | unsafe:syntax_error:invalid syntax |
| qwen2.5-coder_7b | rules | C004_missing_crs_repair | 1 | 0.000 | 0/0 | False | unsafe:syntax_error:invalid syntax |
| qwen2.5-coder_7b | rules | C005_geometry_repair | 1 | 0.000 | 0/0 | False | unsafe:syntax_error:unexpected EOF while parsing |
| qwen2.5-coder_7b | rules | C006_join_diagnostics | 3 | 0.000 | 0/0 | False | unsafe:syntax_error:invalid syntax |
| qwen2.5-coder_7b | rules | C007_wrong_column_guard | 3 | 0.000 | 0/0 | False | unsafe:syntax_error:unexpected EOF while parsing |
| qwen2.5-coder_7b | rules | C008_quantile_classes | 1 | 0.000 | 0/0 | False | unsafe:syntax_error:invalid syntax |
| qwen2.5-coder_7b | rules | C009_colorblind_safe | 1 | 0.000 | 0/0 | False | unsafe:syntax_error:invalid syntax |
| qwen2.5-coder_7b | rules | C010_interactive_tooltips | 1 | 0.000 | 0/0 | False | unsafe:syntax_error:invalid syntax |
| qwen2.5-coder_7b | rules | C011_static_and_interactive | 2 | 0.000 | 0/0 | False | unsafe:syntax_error:invalid syntax |
| qwen2.5-coder_7b | rules | C012_time_series_report | 1 | 0.000 | 0/0 | False | unsafe:syntax_error:invalid syntax |
