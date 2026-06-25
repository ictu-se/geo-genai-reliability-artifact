# Residual Failed Checks After Final Repair

| repair_model | incomplete_cases | failed_check | cases | share_of_incomplete |
| --- | --- | --- | --- | --- |
| deepseek-coder:6.7b | 38 | unsafe:syntax_error:invalid syntax | 33 | 0.868 |
| deepseek-coder:6.7b | 38 | unsafe:syntax_error:unexpected EOF while parsing | 3 | 0.079 |
| deepseek-coder:6.7b | 38 | execution_success | 1 | 0.026 |
| deepseek-coder:6.7b | 38 | static_png | 1 | 0.026 |
| deepseek-coder:6.7b | 38 | unsafe:syntax_error:EOL while scanning string literal | 1 | 0.026 |
| qwen2.5-coder:7b | 34 | execution_success | 33 | 0.971 |
| qwen2.5-coder:7b | 34 | static_png | 26 | 0.765 |
| qwen2.5-coder:7b | 34 | diagnostic_json | 22 | 0.647 |
| qwen2.5-coder:7b | 34 | interactive_html | 7 | 0.206 |
| qwen2.5-coder:7b | 34 | time_series_png | 2 | 0.059 |
| qwen2.5-coder:14b | 31 | execution_success | 30 | 0.968 |
| qwen2.5-coder:14b | 31 | static_png | 26 | 0.839 |
| qwen2.5-coder:14b | 31 | diagnostic_json | 16 | 0.516 |
| qwen2.5-coder:14b | 31 | interactive_html | 6 | 0.194 |
| qwen2.5-coder:32b | 15 | execution_success | 13 | 0.867 |
| qwen2.5-coder:32b | 15 | static_png | 10 | 0.667 |
| qwen2.5-coder:32b | 15 | diagnostic_json | 5 | 0.333 |
| qwen2.5-coder:32b | 15 | interactive_html | 3 | 0.200 |
