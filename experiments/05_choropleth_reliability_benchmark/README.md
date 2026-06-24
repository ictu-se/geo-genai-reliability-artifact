# 05 Choropleth Reliability Benchmark

This track expands the seed choropleth linter experiment into a Q1-manuscript benchmark for LLM-generated GIS/code maps.

Goals:

1. Generate Python mapping scripts from a broader prompt set.
2. Compare basic, data-grounded, and cartographic-rule prompting.
3. Run safety checks before executing generated code.
4. Score execution success, geospatial validity, and cartographic completeness.
5. Add lint-feedback repair in a later phase.

Current benchmark:

```bash
python3 experiments/05_choropleth_reliability_benchmark/scripts/generate_ollama_choropleth_code.py --model qwen2.5-coder:7b --modes basic rules
python3 experiments/05_choropleth_reliability_benchmark/scripts/safety_scan_generated_code.py --model qwen2.5-coder:7b
python3 experiments/05_choropleth_reliability_benchmark/scripts/run_generated_code.py --model qwen2.5-coder:7b --timeout 45
python3 experiments/05_choropleth_reliability_benchmark/scripts/score_generated_runs.py
```

The same workflow has also been run for `deepseek-coder:6.7b`.

Current status:

- qwen2.5-coder:7b: 24/24 safe scripts, 0/24 execution success, 0 complete artifacts.
- deepseek-coder:6.7b: 22/24 safe scripts, 2/22 execution success among safe scripts, 0 complete artifacts.
- deterministic reference baseline: successfully creates `map_static.png`, `map_interactive.html`, `time_series.png`, and `diagnostics.json`.

Reference baseline:

```bash
python3 experiments/05_choropleth_reliability_benchmark/scripts/run_reference_choropleth_baseline.py
```
