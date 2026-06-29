# LLM Code Benchmark Pilot

Updated: 2026-06-19

## Purpose

This pilot starts the larger Q1-oriented benchmark: natural-language GIS tasks -> LLM-generated Python code -> execution -> artifact scoring with GeoGuard metrics.

## Benchmark Assets

- Task set: `experiments/04_geo_faithfulness_evaluator/inputs/llm_tasks_30.json`
- Ollama generator: `experiments/04_geo_faithfulness_evaluator/scripts/generate_ollama_task_code.py`
- Script runner: `experiments/04_geo_faithfulness_evaluator/scripts/run_llm_task_scripts.py`
- Script scorer: `experiments/04_geo_faithfulness_evaluator/scripts/score_llm_task_runs.py`
- Repair loop: `experiments/04_geo_faithfulness_evaluator/scripts/repair_failed_llm_task_scripts.py`

## Current Local Model

- Model used: `qwen2.5-coder:7b`
- Pilot tasks: `T001`, `T006`, `T011`, `T016`, `T021`, `T026`
- Modes: `basic`, `planner`, `geoguard`

## Important Pipeline Fix

Initial generation used `ollama run`, which inserted terminal control characters into generated code and caused invalid Python syntax. The generator was changed to Ollama HTTP API `/api/generate` with `stream=false`, which produces clean code.

## First-Pass Results

The first clean qwen2.5-coder:7b pilot produced low execution rates:

| Mode | ES | Artifact Rate | SC | PHR | CRSC | TV | SCH | MCS | Tasks |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| basic | 0.3333 | 0.3333 | 0.3333 | 0.1667 | 0.5000 | 0.5000 | 0.5000 | 0.0 | 6 |
| planner | 0.3333 | 0.3333 | 0.3333 | 0.2000 | 0.4083 | 0.5000 | 0.5000 | 0.0 | 6 |
| geoguard | 0.1667 | 0.1667 | 0.1667 | 0.2083 | 0.3333 | 0.3333 | 0.3333 | 0.0 | 6 |

Observed failure types:

- missing imports
- wrong or deprecated GeoPandas spatial join parameters
- wrong assumptions about available files/fields
- missing output files
- CRS handling omitted or incorrect
- map scripts failing before PNG export

## Repair Loop Result

A one-step repair loop was implemented using generated code plus stderr as feedback. On the qwen2.5-coder:7b pilot, the repair loop fixed some individual scripts but did not yet produce a reliable system-level improvement. This suggests that the local 7B model is too weak for robust GIS code repair on this benchmark.

## Interpretation

This is useful evidence, but it should not be used as the main positive result of the manuscript yet. It shows that the benchmark is capable of exposing real generated-code failures, which is exactly what the earlier deterministic benchmark could not do.

For a Q1-level experiment, the next required step is to run the same 30-task benchmark on stronger models:

- qwen2.5-coder:32b local, if runtime allows
- GPT-4.1 / GPT-4o or equivalent cloud model
- Claude Sonnet or equivalent
- Gemini Pro or equivalent
- at least one open-weight model

Then report:

- execution success
- artifact rate
- semantic correctness
- CRS correctness
- topology validity
- schema consistency
- map communication score
- error taxonomy
- repair-loop improvement

