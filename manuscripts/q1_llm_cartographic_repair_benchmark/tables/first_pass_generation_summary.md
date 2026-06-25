# First-Pass Generation Summary

| model | mode | cases | complete | execution_success_any | static_png_any | diagnostic_json_any | mean_best_score | dominant_failed_checks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| deepseek-coder:6.7b | basic | 10 | 0 | 1 | 0 | 0 | 0.176 | uses_known_files=10; execution_success=9; static_png=8; diagnostic_json=7 |
| deepseek-coder:6.7b | rules | 12 | 0 | 1 | 0 | 1 | 0.501 | execution_success=11; static_png=9; diagnostic_json=8; interactive_html=2 |
| qwen2.5-coder:7b | basic | 12 | 0 | 0 | 0 | 0 | 0.059 | execution_success=12; uses_known_files=12; uses_env_vars=11; static_png=9 |
| qwen2.5-coder:7b | rules | 12 | 0 | 0 | 0 | 0 | 0.490 | execution_success=12; static_png=9; diagnostic_json=9; interactive_html=2 |
| validator:repair:reference | validator | 12 | 12 | 12 | 12 | 12 | 1.000 |  |
