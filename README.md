# Geo-GenAI Reliability Artifact

This repository contains the code, summarized results, manuscript sources, and LaTeX submission package for:

**From Map-Like Images to Trustworthy Cartographic Artifacts: A Cross-Paradigm Reliability Audit of Geo-Generative AI**

The study evaluates generated maps as artifact chains spanning source data, prompts/captions, conditioning inputs, generated objects, rendered outputs, validation traces, and repair histories. It covers three public artifact families:

- text-to-map image-caption data,
- remote-sensing-to-map tile generation,
- LLM/code-generated choropleth workflows.

## Repository Layout

- `data/data_manifest.md` records third-party data sources, local acquisition notes, and redistribution constraints.
- `experiments/` contains reproducibility, caption-fidelity, SCGM, GeoGuard, and choropleth benchmark scripts plus lightweight summary outputs.
- `experiments/07_grounded_gis_workflow_benchmark/` contains the local-model workflow-contract planning benchmark.
- `experiments/08_workflow_contract_execution/` contains the deterministic execution, bounded repair, synthetic-profile, and negative-control audits for workflow contracts.
- `manuscripts/01_q1_geo_genai_reliability/` contains manuscript source, tables, figures, references, submission checks, and LaTeX build outputs.
- `manuscripts/02_q1_llm_cartographic_repair_benchmark/` contains the second manuscript track on validator-gated repair of LLM-generated GIS/cartographic code.
- `manuscripts/03_q1_cartographic_evaluator_calibration/` contains the third manuscript track on visual-language/proxy evaluator calibration.
- `manuscripts/04_q1_grounded_gis_workflow_benchmark/` contains the newest manuscript track on grounded GIS workflow-spec planning with local Ollama models.
- `notes/` contains project-level survey and research-track notes.

Raw datasets, cloned third-party repositories, copyrighted papers, generated HTML maps, large rendered outputs, and Zenodo staging bundles are intentionally excluded from Git. They are documented in the manifest and can be regenerated or obtained from the upstream sources where licensing permits.

## Main Build Commands

Build manuscript tables, figures, submission package, LaTeX, and release checks:

```bash
python3 manuscripts/01_q1_geo_genai_reliability/working_archive/scripts/build_submission_package.py
```

Run the manuscript readiness audit:

```bash
python3 manuscripts/01_q1_geo_genai_reliability/working_archive/scripts/audit_manuscript_readiness.py
```

The generated PDF is:

```text
manuscripts/01_q1_geo_genai_reliability/submission_ready/Manuscript_with_author_details.pdf
```

## Current Manuscript Snapshot

- Word count: approximately 7,300 words before references.
- PDF length: 24 pages in the Taylor & Francis `interact` LaTeX template.
- Displays: 10 figures and 5 tables.
- References: 39 peer-reviewed entries.

## Data and Software Availability

The repository contains code and summarized result artifacts. Raw third-party datasets are not redistributed here; see `data/data_manifest.md` and `manuscripts/01_q1_geo_genai_reliability/working_archive/submission/DATA_SOURCES.md` for source links, local path expectations, and redistribution notes.

## Workflow-Contract Benchmark

The GeoInformatica submission uses the reproducibility path below:

```bash
python3 -m pip install -r requirements.txt
python3 experiments/07_grounded_gis_workflow_benchmark/scripts/build_gsis_extension_analysis.py
python3 experiments/08_workflow_contract_execution/scripts/build_synthetic_data_profile.py
python3 experiments/08_workflow_contract_execution/scripts/run_contract_execution.py --only-ready
python3 experiments/08_workflow_contract_execution/scripts/run_contract_negative_control_audit.py
```

Large generated GIS artifacts are excluded from Git and can be regenerated from the scripts. Summary ledgers, model outputs, manuscript tables, and the synthetic profile are versioned for review.
