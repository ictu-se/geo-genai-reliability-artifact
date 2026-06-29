# Q1 Manuscript Track: Grounded GIS Workflow Benchmark

Working title:

**Grounded Workflow Specifications for Reliable LLM-GIS Copilots: A GeoGuard Benchmark Across Planning, Validation, and Reflection**

This manuscript track is backed by `experiments/07_grounded_gis_workflow_benchmark`.

## Core Claim

LLM-GIS systems should be evaluated at the workflow-contract level, not only as free-form code generators. Metadata grounding, tool constraints, and validation rules can reduce dataset hallucination, field/schema errors, CRS mistakes, and weak cartographic planning.

## Initial Experimental Design

- At least 10 local Ollama models.
- Three planning modes: `basic`, `grounded`, and `geoguard`.
- Thirty GIS workflow tasks across buffer, overlay, spatial join, raster, zonal statistics, and choropleth-map export categories.
- Metrics: JSON validity, tool validity, data validity, field validity, CRS plan, schema plan, map plan, output naming, plan hallucination risk, and plan reliability score.

