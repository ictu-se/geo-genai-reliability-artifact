# 07 Grounded GIS Workflow Benchmark

This directory contains a reproducible artifact for evaluating local Ollama
models as GIS workflow planners. The benchmark asks each model to generate a
structured JSON workflow specification for GIS tasks, then scores the
specification before any GIS code is executed.

The public artifact intentionally contains code, prompts, model definitions,
generated specifications, and tabular results only. Manuscript files are not
part of this release.

## Repository Layout

```text
experiments/07_grounded_gis_workflow_benchmark/
  inputs/
    model_panel.json              # model list used in the full run
    workflow_tasks_30.json        # 30 GIS planning tasks and expected contracts
  outputs/
    generated_specs/              # raw and parsed model outputs
    scores/                       # task-level and aggregate CSV/Markdown scores
  scripts/
    common.py                     # shared paths and model slug helper
    generate_ollama_workflow_specs.py
    score_workflow_specs.py
    run_model_panel.py
    aggregate_scores.py
    summarize_full_results.py
  requirements.txt
```

## Requirements

- Python 3.10 or newer.
- Ollama installed and running locally at `http://127.0.0.1:11434`.
- The model tags listed in `inputs/model_panel.json` pulled into local Ollama.
- No third-party Python package is required by the benchmark scripts; they use
  the Python standard library.

Create an isolated environment:

```bash
cd /path/to/geo-genai-reliability-artifact
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r experiments/07_grounded_gis_workflow_benchmark/requirements.txt
```

Install the default Ollama model panel:

```bash
ollama pull qwen2.5-coder:1.5b
ollama pull qwen2.5-coder:3b
ollama pull qwen2.5-coder:7b
ollama pull qwen2.5-coder:14b
ollama pull qwen2.5-coder:32b
ollama pull deepseek-coder:6.7b
ollama pull qwen2.5:3b
ollama pull qwen3:4b
ollama pull llama3.2:3b
ollama pull phi3:mini
ollama pull mistral:7b
ollama pull gemma3:4b
```

Check that Ollama is reachable:

```bash
curl http://127.0.0.1:11434/api/tags
```

## Run A Smoke Test

The smoke test runs all 12 models, all 3 prompting modes, and the first 3 tasks.
It is useful for checking that the environment and model names are correct.

```bash
python experiments/07_grounded_gis_workflow_benchmark/scripts/run_model_panel.py \
  --task-limit 3 \
  --timeout 240

python experiments/07_grounded_gis_workflow_benchmark/scripts/aggregate_scores.py
python experiments/07_grounded_gis_workflow_benchmark/scripts/summarize_full_results.py
```

To run a smaller smoke test while debugging:

```bash
python experiments/07_grounded_gis_workflow_benchmark/scripts/run_model_panel.py \
  --models qwen2.5-coder:3b gemma3:4b \
  --modes geoguard \
  --task-limit 3 \
  --timeout 240
```

## Reproduce The Full Benchmark

The full run evaluates 12 models, 3 modes, and 30 tasks, for 1080 attempted
workflow specifications.

```bash
python experiments/07_grounded_gis_workflow_benchmark/scripts/run_model_panel.py \
  --timeout 300

python experiments/07_grounded_gis_workflow_benchmark/scripts/aggregate_scores.py
python experiments/07_grounded_gis_workflow_benchmark/scripts/summarize_full_results.py
```

The runner caches parsed JSON files. If a task output already exists, generation
is skipped and the scorer is rerun. To rescore existing outputs without calling
Ollama:

```bash
python experiments/07_grounded_gis_workflow_benchmark/scripts/run_model_panel.py \
  --skip-generation

python experiments/07_grounded_gis_workflow_benchmark/scripts/aggregate_scores.py
python experiments/07_grounded_gis_workflow_benchmark/scripts/summarize_full_results.py
```

## Modes

- `basic`: natural-language task only.
- `grounded`: task plus data profile and allowed operation schema.
- `geoguard`: grounded context plus CRS, schema, geometry, raster, and map
  validation rules.

## Main Outputs

- `outputs/generated_specs/<model>/<mode>/*.raw.txt`: raw model responses.
- `outputs/generated_specs/<model>/<mode>/*.json`: parsed JSON specifications.
- `outputs/generated_specs/<model>/workflow_generation_manifest.json`: run status.
- `outputs/scores/<model>/workflow_task_scores.csv`: task-level metrics.
- `outputs/scores/<model>/workflow_summary.csv`: per-model, per-mode summary.
- `outputs/scores/model_comparison_summary.csv`: compact model comparison.
- `outputs/scores/full_*`: aggregate summaries by mode, model, task family, and
  failure type.

## Metrics

- `JSON_VALID`: the response was parsed as one JSON object.
- `TOOL_VALID`: the operation matched the expected GIS task type.
- `DATA_VALID`: referenced layers match the provided data profile.
- `FIELD_VALID`: referenced and required fields are known or created.
- `CRS_PLAN`: CRS handling is appropriate for the task family.
- `SCHEMA_PLAN`: required output fields are declared.
- `MAP_PLAN`: choropleth export contains map quality controls.
- `OUTPUT_NAME`: output filename matches the task contract.
- `PHR`: unweighted planning-hallucination rate.
- `WPHR`: weighted planning-hallucination risk.
- `PRS`: aggregate plan reliability score.

## Notes For Reuse

- The benchmark uses synthetic task contracts and metadata profiles. It does not
  redistribute third-party geospatial datasets.
- Full generation time depends heavily on local hardware and selected Ollama
  models. Large models such as `qwen2.5-coder:32b` may require substantially
  longer timeouts.
- To change the model panel, edit `inputs/model_panel.json` or pass `--models`
  to `run_model_panel.py`.
- To add tasks, append records to `inputs/workflow_tasks_30.json` and rerun the
  panel plus aggregation scripts.
