# Qwen 32B Realistic Experimental Design

Updated: 2026-06-19

## Problem With Previous Design

The previous live-code benchmark asked `qwen2.5-coder:32b` to generate full GIS Python scripts from scratch. That design is too harsh and not aligned with the GeoGuard-Copilot claim.

GeoGuard-Copilot is not supposed to be a raw code generator only. The proposed architecture includes:

- Data Profiler
- Tool Retriever
- Planner
- Code Generator/Executor
- GeoGuard Validator
- Map Quality Critic
- Reflector

Therefore, a fair experiment should evaluate whether LLM reasoning improves when it is constrained by tool schemas, data profiles, validation feedback, and deterministic GIS execution.

## Better Experimental Unit

The LLM should generate a structured workflow specification, not arbitrary code.

The deterministic executor should then run the workflow using known GIS tools. This separates:

- LLM planning/parameter selection errors
- GIS execution errors
- validation/repair effectiveness
- cartographic output quality

This is closer to a real copilot architecture and more realistic for `qwen2.5-coder:32b`.

## Systems to Compare

### S1 Basic LLM Planner

Input:

- natural language task only

Output:

- JSON workflow spec

Expected weakness:

- wrong layer names
- wrong field names
- missing CRS strategy
- incomplete output schema
- weak map elements

### S2 Metadata-Grounded Planner

Input:

- natural language task
- data profile
- allowed tool schema

Expected improvement:

- fewer field/layer hallucinations
- better CRS and output choices

### S3 GeoGuard Planner

Input:

- natural language task
- data profile
- allowed tool schema
- validation rules
- map quality requirements

Expected improvement:

- explicit CRS checks
- schema preservation
- geometry repair
- map quality elements

### S4 GeoGuard + Reflector

Input:

- failed/weak workflow spec
- structured validator feedback

Expected improvement:

- fixes missing CRS strategy
- fixes field names
- adds validation/map checks

## Metrics

Use metrics that evaluate workflow specs and generated artifacts:

- `JSON_VALID`: valid parseable JSON
- `TOOL_VALID`: operation belongs to allowed tool list
- `DATA_VALID`: referenced layers exist
- `FIELD_VALID`: referenced fields exist
- `CRS_PLAN`: metric operations specify projected CRS or raster/vector CRS alignment
- `SCHEMA_PLAN`: required output fields are preserved/generated
- `MAP_PLAN`: title, legend, classification, color ramp, and source note for visualization tasks
- `EXECUTION_SUCCESS`: deterministic executor succeeds
- `ARTIFACT_VALID`: output file exists and is readable
- `SC`, `PHR`, `CRSC`, `TV`, `SCH`, `MCS`: mapped from artifact and plan checks

## Why This Is Better

This design directly tests the paper's actual claim:

> GeoGuard improves LLM GIS reliability through metadata grounding, validation, and reflection.

It no longer depends on whether a local 32B model can write perfect GeoPandas/Rasterio code from scratch.

## Next Implementation

Implement:

1. `generate_ollama_workflow_specs.py`
2. `score_workflow_specs.py`
3. deterministic executor for accepted specs
4. validator feedback loop
5. manuscript update to describe workflow-spec generation rather than raw script generation

## Full 30-Task Qwen32 Workflow-Spec Run

Model: `qwen2.5-coder:32b`

Run date: 2026-06-19

Generated specs:

- `experiments/04_geo_faithfulness_evaluator/outputs/workflow_spec_benchmark/generated_specs/qwen2.5-coder_32b`

Scores:

- `experiments/04_geo_faithfulness_evaluator/outputs/workflow_spec_benchmark/scores/qwen2.5-coder_32b/workflow_summary.csv`
- `experiments/04_geo_faithfulness_evaluator/outputs/workflow_spec_benchmark/scores/qwen2.5-coder_32b/workflow_task_scores.csv`
- `experiments/04_geo_faithfulness_evaluator/outputs/workflow_spec_benchmark/scores/qwen2.5-coder_32b/workflow_category_scores.csv`
- `experiments/04_geo_faithfulness_evaluator/outputs/workflow_spec_benchmark/scores/qwen2.5-coder_32b/workflow_failure_taxonomy.csv`
- `experiments/04_geo_faithfulness_evaluator/outputs/workflow_spec_benchmark/scores/qwen2.5-coder_32b/workflow_task_composition.csv`

| Mode | JSON_VALID | TOOL_VALID | DATA_VALID | FIELD_VALID | CRS_PLAN | SCHEMA_PLAN | MAP_PLAN | OUTPUT_NAME | PHR | Tasks |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Basic | 0.9000 | 0.9000 | 0.0667 | 0.3540 | 0.6833 | 0.9000 | 0.8400 | 0.9000 | 0.4533 | 30 |
| Metadata-grounded | 1.0000 | 0.9333 | 0.9333 | 0.8100 | 0.8333 | 0.9722 | 0.9267 | 0.9333 | 0.1533 | 30 |
| GeoGuard | 1.0000 | 0.9000 | 1.0000 | 0.8421 | 0.9667 | 0.9722 | 0.9000 | 0.9000 | 0.1200 | 30 |

Main observations:

- The original direct-code benchmark was not a fair primary experiment for this paper because it measured whether Qwen32 could write full GeoPandas/Rasterio programs from scratch.
- The workflow-spec benchmark is better aligned with GeoGuard-Copilot because it tests planning under data profiles, tool constraints, and geospatial validation rules.
- The task suite is balanced across six workflow categories: buffer service areas, overlay intersections, point-count joins, raster clipping, zonal statistics, and choropleth export.
- Metadata grounding almost eliminates dataset hallucination relative to the basic planner.
- GeoGuard validation rules further improve CRS planning, especially for metric buffers and projected area workflows.
- Remaining GeoGuard errors are not uniform: most are complex visualization tasks where the model emits an intermediate analysis operation instead of the required final `choropleth_export`, or references a derived field such as `combined_risk_score` that is not present in the available layer.
- This is a more defensible result shape for the manuscript: GeoGuard improves reliability substantially, but does not claim perfect planning.

Category-level PHR:

| Task category | Basic | Metadata-grounded | GeoGuard |
|---|---:|---:|---:|
| Buffer service area | 0.6400 | 0.1200 | 0.0000 |
| Overlay intersection | 0.6000 | 0.2800 | 0.2000 |
| Point-count join | 0.4000 | 0.0800 | 0.0800 |
| Raster clip | 0.1200 | 0.0000 | 0.0000 |
| Zonal statistics | 0.5200 | 0.0800 | 0.0800 |
| Choropleth export | 0.4400 | 0.3600 | 0.3600 |

Failure counts over 30 tasks:

| Failure type | Basic | Metadata-grounded | GeoGuard |
|---|---:|---:|---:|
| JSON/tool/output failure | 3 | 2 | 3 |
| Dataset hallucination | 28 | 2 | 0 |
| Field or schema error | 22 | 10 | 10 |
| CRS planning error | 12 | 7 | 2 |
| Map-planning weakness | 7 | 3 | 3 |

Recommended manuscript use:

- Replace claims based on repeated identical synthetic values with this 30-task Qwen32 workflow-spec evaluation.
- Present the original artifact-level stress benchmark as controlled executor-side validation.
- Present this Qwen32 run as the model-facing planning benchmark.
- Add a limitation that complex multi-step map requests still need a reflector or multi-step planner to convert intermediate analysis specs into final visualization specs.
