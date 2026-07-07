# Status

Created: 2026-06-29.

## Current Stage

Full manuscript draft started from the Taylor & Francis `interact` LaTeX template copied from paper 3. The draft now reports the complete local-Ollama workflow-specification benchmark and includes extended appendix ledgers.

## Draft Build

Current LaTeX source:

- `submission/latex/main.tex`

Current PDF:

- `submission/latex/main.pdf`

The draft is based on the full experiment:

- 12 local Ollama models.
- 3 prompting modes: `basic`, `grounded`, `geoguard`.
- All 30 tasks from the workflow-spec benchmark.
- 1080 attempted workflow specifications.
- Current compiled PDF length: 22 pages after replacing dense end-of-paper ledgers with compact summary tables.
- Seven synthetic geospatial figures are included across the benchmark-design and results sections: task artifact examples, operation-family gallery, task-family coverage, validation-contract examples, workflow-contract anatomy, failure-case maps, and cartographic export variants.
- Dense full-run ledgers are retained as generated CSV/TeX artifacts, but the PDF includes only compact task, model-family, and hard-case summaries.
- All figures and manuscript-included tables are explicitly referenced and analyzed near their insertion point; floats use `[htbp]` placement where applicable.
- Tables now include interpretation paragraphs that discuss patterns, exceptions, and methodological implications rather than only restating values.

## Main Full-Run Result

Mean plan reliability score improves from 0.547 in basic mode to 0.751 in grounded mode and 0.774 in GeoGuard mode. Data-invalid failures fall from 249 in basic mode to 31 in grounded mode and 25 in GeoGuard mode. GeoGuard produces the strongest CRS-planning gain, reducing CRS-weak cases from 89 in grounded mode to 39.

## Completed Commands

The full run and manuscript refresh used:

```bash
python3 experiments/07_grounded_gis_workflow_benchmark/scripts/run_model_panel.py --timeout 300
python3 experiments/07_grounded_gis_workflow_benchmark/scripts/aggregate_scores.py
python3 experiments/07_grounded_gis_workflow_benchmark/scripts/summarize_full_results.py
python3 manuscripts/04_q1_grounded_gis_workflow_benchmark/scripts/build_full_result_figures.py
python3 manuscripts/04_q1_grounded_gis_workflow_benchmark/scripts/build_geo_map_figures.py
python3 manuscripts/04_q1_grounded_gis_workflow_benchmark/scripts/build_latex_appendix_tables.py
```

## Next Needed Work

Add deterministic execution of accepted workflow specifications, then compare plan-level validity with execution success and rendered artifact quality. This would support a stronger second experimental layer beyond the current planning benchmark.
