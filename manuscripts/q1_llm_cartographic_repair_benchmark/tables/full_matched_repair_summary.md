# Full Matched Repair Summary

Generated from:

`experiments/05_choropleth_reliability_benchmark/outputs/scores/iterative_validator_repair_*.csv`

Run scope:

- 40 matched incomplete cases selected from the one-pass qwen2.5-coder:32b repair condition.
- Maximum repair attempts per case: 3.
- Repair models: deepseek-coder:6.7b, qwen2.5-coder:7b, qwen2.5-coder:14b, qwen2.5-coder:32b.

## Model-Level Results

| Repair model | Cases | Attempt rows | Safe attempts | Unsafe attempts | Completed cases | Completion rate | Mean final score |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-coder:6.7b | 40 | 66 | 23 | 43 | 2 | 0.050 | 0.062 |
| qwen2.5-coder:7b | 40 | 113 | 113 | 0 | 6 | 0.150 | 0.572 |
| qwen2.5-coder:14b | 40 | 110 | 110 | 0 | 9 | 0.225 | 0.636 |
| qwen2.5-coder:32b | 40 | 89 | 89 | 0 | 25 | 0.625 | 0.856 |

## Completion by First Successful Iteration

| Repair model | Iteration 1 | Iteration 2 | Iteration 3 | Total completed |
|---|---:|---:|---:|---:|
| deepseek-coder:6.7b | 0 | 2 | 0 | 2 |
| qwen2.5-coder:7b | 2 | 3 | 1 | 6 |
| qwen2.5-coder:14b | 3 | 4 | 2 | 9 |
| qwen2.5-coder:32b | 10 | 11 | 4 | 25 |

## Final-Score Thresholds

| Repair model | Score >= 1.0 | Score >= 0.8 | Score >= 0.6 | Score >= 0.5 | Score >= 0.4 |
|---|---:|---:|---:|---:|---:|
| deepseek-coder:6.7b | 2 | 2 | 2 | 3 | 3 |
| qwen2.5-coder:7b | 6 | 7 | 9 | 32 | 38 |
| qwen2.5-coder:14b | 9 | 12 | 14 | 34 | 38 |
| qwen2.5-coder:32b | 25 | 29 | 33 | 38 | 39 |

## Immediate Interpretation

The full matched suite shows a strong repair-capacity gradient. qwen2.5-coder:32b completes 25/40 cases and reaches high final scores for most remaining cases, while qwen2.5-coder:7b and qwen2.5-coder:14b remain mostly partial despite safe code generation. deepseek-coder:6.7b completes only 2/40 cases and produces many unsafe attempts under the benchmark scanner. This supports the paper's central claim that repairability should be measured separately from first-pass generation and that validator-gated repair exposes differences in safety, completion, and residual artifact-contract failures.
