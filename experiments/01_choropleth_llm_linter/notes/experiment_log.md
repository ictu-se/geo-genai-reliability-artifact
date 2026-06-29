# Experiment Log

## Run 001 - Data Inspection, Baseline Render, and Initial Lint

Date: 2026-06-19

Scripts run:

- `scripts/inspect_data.py`
- `scripts/render_baseline_choropleth.py`
- `scripts/lint_choropleth_data.py`

Outputs:

- `outputs/data_inspection.json`
- `outputs/baseline_maps/portugal_burned_area_static.png`
- `outputs/baseline_maps/portugal_burned_area_interactive.html`
- `outputs/lint_report.json`

Findings:

- The CSV has 21 annual records from 2002 to 2022 with no missing values in `Year`, `Burned Area [ha]`, or `Number of Fires`.
- `boundary.shp` declares `EPSG:4326`, but its single geometry is invalid.
- `mainlandburn.shp` has 18 district features and thematic columns `Burned_Are` and `of_Fires`, but it does not declare a CRS.
- The baseline renderer repairs `mainlandburn.shp` by setting `EPSG:4326` after checking the coordinate bounds.
- Initial linter result: 2 errors, 0 warnings.

Interpretation:

- This is already a useful benchmark case because raw geospatial data contains realistic issues that a robust LLM-generated mapping workflow should detect or repair.
- The first linter checks are intentionally simple: CRS, geometry validity, missing values, thematic numeric columns, unique region labels, and expected output files.

Next:

- Add visual-output lint checks for title, legend, source note, and map/legend overlap where possible.
- Add a script to run generated candidate code in a controlled folder and capture execution logs.
- Turn `prompt_set_v0.md` into machine-readable prompts for repeatable LLM comparisons.

## Run 002 - Candidate Runner Smoke Test

Date: 2026-06-19

Added:

- `inputs/prompts_v0.json`
- `inputs/candidates/reference_solution.py`
- `scripts/run_candidate.py`

Command:

```bash
python3 experiments/01_choropleth_llm_linter/scripts/run_candidate.py \
  experiments/01_choropleth_llm_linter/inputs/candidates/reference_solution.py \
  --prompt-id P05_robust_cartographic_output
```

Result:

- Return code: 0
- Elapsed time: about 4 seconds
- Candidate outputs:
  - `map_static.png`
  - `map_interactive.html`
  - `stdout.txt`
  - `stderr.txt`
  - `metadata.json`

Interpretation:

- The experiment can now run candidate scripts in isolated output folders.
- Candidate scripts receive the fixed dataset path through `CHOROPLETH_DATA_DIR` and the run output folder through `CHOROPLETH_OUTPUT_DIR`.
- This is ready for comparing code generated from different LLMs or prompt variants.

## Run 003 - MVP Candidate Batch and Scoring

Date: 2026-06-19

Added:

- `inputs/candidates/p01_static_basic_naive.py`
- `inputs/candidates/p02_static_with_crs_repair.py`
- `inputs/candidates/p03_interactive_basic.py`
- `inputs/candidates/p04_csv_time_series.py`
- `inputs/candidates/p05_wrong_column_failure.py`
- `scripts/summarize_candidate_runs.py`
- `scripts/score_candidate_runs.py`

Outputs:

- `outputs/candidate_run_summary.csv`
- `outputs/candidate_run_summary.md`
- `outputs/candidate_scores.csv`
- `outputs/candidate_scores.md`

Batch result:

| Prompt | Candidate | Return | Score | Notes |
|---|---|---:|---:|---|
| P01_static_basic | `p01_static_basic_naive.py` | 0 | 1.000 | Static PNG created. |
| P02_static_with_crs_repair | `p02_static_with_crs_repair.py` | 0 | 1.000 | Static PNG created; CRS repair present. |
| P03_interactive_basic | `p03_interactive_basic.py` | 0 | 1.000 | Interactive HTML created. |
| P04_csv_time_series | `p04_csv_time_series.py` | 0 | 1.000 | Time-series PNG created; max burned-area year reported as 2017. |
| P05_robust_cartographic_output | `reference_solution.py` | 0 | 1.000 | Static PNG and interactive HTML created; diagnostic report printed. |
| P05_wrong_column | `p05_wrong_column_failure.py` | 1 | 0.000 | Failed because it used the plausible but wrong column name `Burned Area [ha]` instead of `Burned_Are`. |

Interpretation:

- The runner can now capture both successful map-generation outputs and realistic code-generation failures.
- The wrong-column failure is a strong benchmark case because it mirrors a common LLM/GIS issue: confusing human-readable CSV column names with truncated shapefile field names.
- The current scorer is intentionally lightweight; it verifies execution and task-specific artifact presence, not full visual/cartographic quality yet.

Next:

- Add candidate-output linting beyond file existence.
- Add checks for legend/title/source note and map/legend overlap.
- Add a small report that compares prompt strictness against candidate robustness.
