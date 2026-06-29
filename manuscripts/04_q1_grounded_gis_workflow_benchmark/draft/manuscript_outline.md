# Manuscript Outline

Working title:

**Grounded Workflow Specifications for Reliable LLM-GIS Copilots: A GeoGuard Benchmark Across Planning, Validation, and Reflection**

## 1. Introduction

- LLM-GIS copilots are often evaluated as code generators, but practical GIS systems need reliable workflow contracts before execution.
- Free-form code generation confounds planning errors, library syntax errors, data hallucination, and artifact-rendering failures.
- This paper evaluates local LLMs as structured GIS workflow planners under increasing levels of grounding.

## 2. Research Questions

1. How reliably do local LLMs produce valid GIS workflow specifications from natural-language tasks?
2. Does metadata and tool-schema grounding reduce dataset and field hallucination?
3. Do GeoGuard-style validation rules improve CRS, schema, and cartographic planning?
4. Which local model families are suitable for workflow-contract generation?

## 3. Benchmark Design

- Models: at least 10 local Ollama models; initial panel has 12.
- Tasks: 30 GIS workflow tasks across buffer, overlay, point-count joins, raster clipping, zonal statistics, and choropleth export.
- Modes:
  - `basic`: task only.
  - `grounded`: data profile plus allowed operation schema.
  - `geoguard`: grounded context plus validation and map-quality rules.
- Output: a single JSON workflow specification.

## 4. Metrics

- JSON validity.
- Tool validity.
- Data validity.
- Field validity.
- CRS plan.
- Schema plan.
- Map plan.
- Output filename match.
- Plan hallucination risk.
- Plan reliability score.

## 5. Preliminary Smoke Result

The initial smoke run covers 12 local Ollama models, 3 modes, and the first 3 workflow tasks. The result is stored in:

- `tables/model_comparison_summary_smoke.csv`
- `tables/model_comparison_summary_smoke.md`

Early pattern:

- Basic mode often fails through malformed JSON, missing known layers, or weak CRS planning.
- Grounding improves data validity for most models.
- GeoGuard-style rules produce the strongest reliability scores for several coder models.
- Some compact/general models fail the strict JSON-spec contract and should be reported as compliance failures rather than silently excluded.

## 6. Planned Full Experiment

- Run the full 30-task suite for the 12-model panel.
- Add category-level summaries.
- Add model-family comparison: coder vs general compact models.
- Add failure taxonomy for malformed JSON, wrong operation, unknown data, invalid field, CRS weakness, missing output name, and weak map plan.

