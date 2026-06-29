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
- `manuscripts/q1_geo_genai_reliability/` contains manuscript source, tables, figures, references, submission checks, and LaTeX build outputs.
- `notes/` contains project-level survey and research-track notes.

Raw datasets, cloned third-party repositories, copyrighted papers, generated HTML maps, large rendered outputs, and Zenodo staging bundles are intentionally excluded from Git. They are documented in the manifest and can be regenerated or obtained from the upstream sources where licensing permits.

## Main Build Commands

Build manuscript tables, figures, submission package, LaTeX, and release checks:

```bash
python3 manuscripts/q1_geo_genai_reliability/scripts/build_submission_package.py
```

Run the manuscript readiness audit:

```bash
python3 manuscripts/q1_geo_genai_reliability/scripts/audit_manuscript_readiness.py
```

The generated PDF is:

```text
manuscripts/q1_geo_genai_reliability/submission/latex/main.pdf
```

## Current Manuscript Snapshot

- Word count: approximately 7,300 words before references.
- PDF length: 24 pages in the Taylor & Francis `interact` LaTeX template.
- Displays: 10 figures and 5 tables.
- References: 39 peer-reviewed entries.

## Data and Software Availability

The repository contains code and summarized result artifacts. Raw third-party datasets are not redistributed here; see `data/data_manifest.md` and `manuscripts/q1_geo_genai_reliability/submission/DATA_SOURCES.md` for source links, local path expectations, and redistribution notes.

