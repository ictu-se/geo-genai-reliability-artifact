# Iterative Repair Artifact QA Summary

| repair_model | artifact_kind | checked | exists | valid_proxy | screenshot_or_rendered | screenshot_qa_pass | content_qa_pass | pass_rate_existing | content_pass_rate_existing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| deepseek-coder_6.7b | diagnostic_json | 23 | 6 | 6 |  |  |  |  |  |
| deepseek-coder_6.7b | interactive_html | 23 | 0 | 0 | 0 | 0 | 0 | 0.000 | 0.000 |
| deepseek-coder_6.7b | static_png | 23 | 2 | 2 | 2 | 2 | 1 | 1.000 | 0.500 |
| deepseek-coder_6.7b | time_series_png | 23 | 1 | 1 | 1 | 1 | 1 | 1.000 | 1.000 |
| qwen2.5-coder_14b | diagnostic_json | 110 | 28 | 21 |  |  |  |  |  |
| qwen2.5-coder_14b | interactive_html | 110 | 1 | 1 | 1 | 1 | 1 | 1.000 | 1.000 |
| qwen2.5-coder_14b | static_png | 110 | 6 | 6 | 6 | 6 | 5 | 1.000 | 0.833 |
| qwen2.5-coder_14b | time_series_png | 110 | 6 | 6 | 6 | 6 | 3 | 1.000 | 0.500 |
| qwen2.5-coder_32b | diagnostic_json | 89 | 44 | 37 |  |  |  |  |  |
| qwen2.5-coder_32b | interactive_html | 89 | 8 | 5 | 8 | 5 | 5 | 0.625 | 0.625 |
| qwen2.5-coder_32b | static_png | 89 | 23 | 23 | 23 | 23 | 22 | 1.000 | 0.957 |
| qwen2.5-coder_32b | time_series_png | 89 | 4 | 4 | 4 | 4 | 4 | 1.000 | 1.000 |
| qwen2.5-coder_7b | diagnostic_json | 113 | 15 | 14 |  |  |  |  |  |
| qwen2.5-coder_7b | interactive_html | 113 | 4 | 1 | 4 | 1 | 1 | 0.250 | 0.250 |
| qwen2.5-coder_7b | static_png | 113 | 6 | 6 | 6 | 6 | 3 | 1.000 | 0.500 |
| qwen2.5-coder_7b | time_series_png | 113 | 2 | 2 | 2 | 2 | 2 | 1.000 | 1.000 |
