# Iterative Repair VLM Judge Comparison

Scope: 24 content-QA-pass iterative repair artifacts reviewed by two local VLM judges. Treat this as evaluator-stress evidence, not human ground truth.

| VLM model | Repair model | Reviewed | Mean score | Verdict counts |
|---|---|---:|---:|---|
| granite3.2-vision:latest | deepseek-coder_6.7b | 2 | 0.750 | {'usable_with_minor_issues': 2} |
| granite3.2-vision:latest | qwen2.5-coder_14b | 9 | 0.667 | {'usable_with_minor_issues': 7, 'weak': 1, 'publication_ready': 1} |
| granite3.2-vision:latest | qwen2.5-coder_32b | 7 | 0.750 | {'usable_with_minor_issues': 7} |
| granite3.2-vision:latest | qwen2.5-coder_7b | 6 | 0.783 | {'usable_with_minor_issues': 6} |
| qwen2.5vl:3b | deepseek-coder_6.7b | 2 | 0.200 | {'weak': 1, 'failed': 1} |
| qwen2.5vl:3b | qwen2.5-coder_14b | 9 | 0.222 | {'failed': 5, 'weak': 4} |
| qwen2.5vl:3b | qwen2.5-coder_32b | 7 | 0.229 | {'failed': 5, 'weak': 2} |
| qwen2.5vl:3b | qwen2.5-coder_7b | 6 | 0.217 | {'failed': 6} |

Interpretation: deterministic content QA is more stable than VLM-only assessment. Granite3.2-vision tends to read content-QA-pass artifacts as usable with minor issues, whereas qwen2.5vl:3b is much stricter and often labels the same class of artifacts weak or failed. This supports using VLMs as stress tests rather than as final cartographic ground truth.
