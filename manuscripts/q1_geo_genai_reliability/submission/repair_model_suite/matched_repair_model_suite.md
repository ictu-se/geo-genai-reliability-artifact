# Matched Repair-Model Suite

This suite compares three smaller repair models on the same eight near-miss iterative-repair cases. It complements the qwen2.5-coder:32b full 40-case sweep by isolating model-size/model-family sensitivity on a matched subset.

## Summary

| Repair model | Matched cases | Attempt rows | Safe attempts | Completed cases | Completion rate | Mean final score | Mean best score | Completed by iteration |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| qwen2.5-coder:14b | 8 | 14 | 14 | 3 | 3/8 | 0.829 | 0.829 | iter 1: 2; iter 2: 1 |
| qwen2.5-coder:7b | 8 | 14 | 14 | 3 | 3/8 | 0.808 | 0.808 | iter 1: 2; iter 2: 1 |
| deepseek-coder:6.7b | 8 | 10 | 4 | 0 | 0/8 | 0.204 | 0.204 | none |

## Case-Level Pattern

- `deepseek-coder_6.7b__basic__C004_missing_crs_repair`: completed by none; final scores qwen2.5-coder:14b=0.857, qwen2.5-coder:7b=0.571, deepseek-coder:6.7b=0.000.
- `deepseek-coder_6.7b__basic__C007_wrong_column_guard`: completed by qwen2.5-coder:14b; final scores qwen2.5-coder:14b=1.000, qwen2.5-coder:7b=0.600, deepseek-coder:6.7b=0.000.
- `deepseek-coder_6.7b__rules__C003_static_full_layout`: completed by none; final scores qwen2.5-coder:14b=0.833, qwen2.5-coder:7b=0.833, deepseek-coder:6.7b=0.833.
- `deepseek-coder_6.7b__rules__C004_missing_crs_repair`: completed by qwen2.5-coder:7b; final scores qwen2.5-coder:14b=0.571, qwen2.5-coder:7b=1.000, deepseek-coder:6.7b=0.000.
- `deepseek-coder_6.7b__rules__C005_geometry_repair`: completed by qwen2.5-coder:14b; final scores qwen2.5-coder:14b=1.000, qwen2.5-coder:7b=0.857, deepseek-coder:6.7b=0.000.
- `qwen2.5-coder_7b__basic__C004_missing_crs_repair`: completed by qwen2.5-coder:7b; final scores qwen2.5-coder:14b=0.571, qwen2.5-coder:7b=1.000, deepseek-coder:6.7b=0.000.
- `qwen2.5-coder_7b__basic__C007_wrong_column_guard`: completed by qwen2.5-coder:14b, qwen2.5-coder:7b; final scores qwen2.5-coder:14b=1.000, qwen2.5-coder:7b=1.000, deepseek-coder:6.7b=0.000.
- `qwen2.5-coder_7b__rules__C007_wrong_column_guard`: completed by none; final scores qwen2.5-coder:14b=0.800, qwen2.5-coder:7b=0.600, deepseek-coder:6.7b=0.800.

## Interpretation

- qwen2.5-coder:7b and qwen2.5-coder:14b complete the same number of matched near-miss cases, but their final scores and completion iteration expose case-specific repair sensitivity.
- deepseek-coder:6.7b produces unsafe syntax-failing attempts on several cases and completes no matched cases in this suite.
- The matched subset is deliberately smaller than the 40-case qwen2.5-coder:32b sweep; it should be reported as model-sensitivity evidence, not as a full benchmark ranking.
