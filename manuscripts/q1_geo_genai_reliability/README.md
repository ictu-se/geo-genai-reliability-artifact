# Q1 Manuscript Track: Geo-GenAI Reliability

Working title:

**From Map-Like Images to Trustworthy Cartographic Artifacts: A Cross-Paradigm Reliability Audit of Geo-Generative AI**

This folder contains the manuscript plan, draft, experiment protocols, and manuscript-ready tables for a Q1-journal submission target.

Key files:

- `draft/manuscript_draft.md`
- `protocols/full_experimental_program.md`
- `protocols/completion_roadmap.md`
- `protocols/expanded_choropleth_prompt_set.md`
- `tables/manuscript_tables.md`
- `figures/figure_index.md`
- `submission/blinded_main_manuscript.md`
- `submission/supplementary_material_manifest.md`
- `submission/ijgis_compliance_checklist.md`
- `submission/reproducibility_release_plan.md`
- `submission/DATA_SOURCES.md`
- `submission/environment_minimal.yml`
- `submission/environment_optional_embedding.yml`
- `submission/human_validation_panels/human_validation_protocol.md`
- `submission/human_validation_panels/human_validation_rubric.json`
- `submission/submission_package_audit.md`
- `notes/manuscript_positioning.md`
- `notes/evidence_map.md`
- `notes/vlm_agreement_calibration.md`
- `notes/journal_targeting.md`
- `notes/ijgis_submission_target_pack.md`
- `notes/ijgis_special_issue_abstract.md`
- `notes/manuscript_readiness_audit.md`
- `notes/citation_audit.md`
- `notes/submission_packaging_plan.md`
- `notes/submission_readiness_checklist.md`
- `notes/status_dashboard.md`

Regenerate tables:

```bash
python3 manuscripts/q1_geo_genai_reliability/scripts/synthesize_tables.py
```

Regenerate draft figures:

```bash
python3 manuscripts/q1_geo_genai_reliability/scripts/make_figures.py
```

Run manuscript readiness audit:

```bash
python3 manuscripts/q1_geo_genai_reliability/scripts/build_submission_package.py
python3 manuscripts/q1_geo_genai_reliability/scripts/audit_manuscript_readiness.py
```

Build human/adjudication validation panels:

```bash
python3 manuscripts/q1_geo_genai_reliability/scripts/build_human_validation_panels.py
```

Summarize completed human validation labels:

```bash
python3 manuscripts/q1_geo_genai_reliability/scripts/summarize_human_validation.py
```

Release/reproducibility packaging:

- `submission/reproducibility_release_plan.md` defines what can be public, what should remain source-linked or restricted, and the minimum environment/manifest expectations for review and DOI deposit.
- `submission/DATA_SOURCES.md` records source-linked datasets and redistribution notes.
- `submission/environment_minimal.yml` provides a minimal Conda environment for the audit scripts.

Current experiment spine:

- `experiments/00_dataset_reproducibility_audit`
- `experiments/01_choropleth_llm_linter`
- `experiments/02_mapgenerator_image_text_audit`
- `experiments/03_scgm_subset_reproduction`
- `experiments/05_choropleth_reliability_benchmark`

Current choropleth benchmark status:

- 12 prompts x 2 prompting modes for `qwen2.5-coder:7b` and `deepseek-coder:6.7b`.
- qwen: 24/24 generated scripts passed static safety scan; 0/24 executed successfully.
- deepseek: 22/24 generated scripts passed static safety scan; 2/22 safe scripts executed successfully.
- Neither model produced a complete valid benchmark artifact under current checks.
- Rules prompting improved partial rubric score relative to basic prompting, but did not guarantee valid map artifacts.
- A deterministic reference baseline successfully produces static PNG, interactive HTML, time-series PNG, and diagnostics from the same local data.
- One-pass 32B repair completes 6 failed/incomplete LLM-generated tasks.
- Iterative validator-gated repair completes 25/40 remaining incomplete one-pass repair cases after up to three additional iterations.
