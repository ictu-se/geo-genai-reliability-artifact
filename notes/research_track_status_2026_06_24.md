# Geo-GenAI Research Track Status

Date: 2026-06-24

## What Is Now Set Up

The workspace now has a concrete low-compute research track for the downloaded Geo-GenAI map datasets.

New audit track:

- `experiments/00_dataset_reproducibility_audit`
- outputs:
  - `outputs/dataset_inventory.csv`
  - `outputs/reproducibility_matrix.csv`
  - `outputs/dataset_audit_report.md`

MapGenerator audit:

- `experiments/02_mapgenerator_image_text_audit/scripts/audit_mapgenerator_pairs.py`
- outputs:
  - `outputs/mapgenerator_pairs_audit.csv`
  - `outputs/mapgenerator_audit_summary.json`
  - `outputs/mapgenerator_audit_report.md`
  - `outputs/mapgenerator_flagged_contact_sheet.jpg`

SCGM manifest:

- `experiments/03_scgm_subset_reproduction/scripts/build_scgm_manifest.py`
- `experiments/03_scgm_subset_reproduction/scripts/compute_edge_continuity.py`
- outputs:
  - `outputs/scgm_split_summary.json`
  - `outputs/scgm_subset_manifest_train_first200.csv`
  - `outputs/scgm_subset_manifest_val_first200.csv`
  - `outputs/scgm_complete_reference_subset_train_first200.csv`
  - `outputs/scgm_complete_reference_subset_val_first200.csv`
  - `outputs/scgm_manifest_report.md`
  - `outputs/scgm_edge_continuity_val.csv`
  - `outputs/scgm_edge_continuity_summary.json`
  - `outputs/scgm_edge_continuity_report.md`

Choropleth artifact audit:

- `experiments/01_choropleth_llm_linter/scripts/audit_released_map_artifacts.py`
- outputs:
  - `outputs/released_map_artifact_audit.csv`
  - `outputs/released_map_artifact_audit_summary.json`
  - `outputs/released_map_artifact_audit.md`

## Key Findings So Far

### Dataset inventory

- SCGM/CSCMG is the main large dataset: 9.4 GB local, 522,485 files.
- MapGenerator is lightweight: 40.4 MB, 750 train image-caption pairs and 100 eval pairs.
- ChatGPT choropleth materials are 473.9 MB and include 43 released map artifacts.
- Generative AI mapmaking code is local, but the original controlled training data are not.
- GeoGuard LA County data are useful as a local evaluator testbed, but should not be treated as an external public dataset in the survey.

### SCGM / CSCMG

- Train split:
  - `rs_256`: 135,572
  - `map_256`: 135,572
  - matched RS-map filenames: 135,572
  - `ref_scale_2_256`: 130,701
  - `ref_scale_4_256`: 115,595
- Val split:
  - `rs_256`: 1,473
  - `map_256`: 1,473
  - matched RS-map filenames: 1,473
  - `ref_scale_2_256`: 1,192
  - `ref_scale_4_256`: 900
- Base image-to-map pairs are complete, but cascade references are not one-to-one. Any SCGM reproduction must either filter to complete-reference subsets or handle missing references.
- Validation edge-continuity baseline:
  - `map_256/right`: mean RGB border difference 1.8534
  - `map_256/down`: mean RGB border difference 2.7529
  - `rs_256/right`: mean RGB border difference 11.5201
  - `rs_256/down`: mean RGB border difference 13.4680
- This gives a simple reference metric for future generated tile continuity.

### MapGenerator

- MapTrain:
  - 750 pairs
  - 0 missing images
  - all images 1024x1024
  - average caption length: 50.67 words
  - heuristic flags: 79 generic no-feature claims, 315 no direction/relation, 29 no named feature
- MGEval:
  - 100 pairs
  - 0 missing images
  - all images 1024x1024
  - average caption length: 54.11 words
  - heuristic flags: 13 generic no-feature claims, 38 no direction/relation, 2 no named feature
- Important reproducibility observation: local release has 750 train pairs, while the survey note records the paper claim as 1000 train pairs.

### Choropleth materials

- Raw data linter finds two important data issues:
  - `boundary.shp` has 1 invalid geometry.
  - `mainlandburn.shp` has no CRS.
- Released map artifact audit finds:
  - 33 PNG files
  - 10 interactive HTML files
  - no empty or blank artifacts by file-level checks
- Existing candidate benchmark already has 6 candidate runs, including one intentional wrong-column failure. This is a useful seed but too small for a full benchmark claim.

## Visual Review Artifact

`experiments/02_mapgenerator_image_text_audit/outputs/mapgenerator_flagged_contact_sheet.jpg` is a contact sheet for the top flagged MapGenerator image-caption pairs. It is intended for fast human review before adding CLIP/VLM scoring.

## Best Next Experiment

The most publishable next step is a reliability/evaluation paper track:

1. Expand the choropleth LLM code benchmark from 6 seed candidates to a larger prompt set.
2. Add screenshot-level cartographic QA checks:
   - title
   - legend
   - color ramp suitability
   - source note
   - class count
   - missing/unjoined regions
   - CRS repair
3. Add a repair loop where lint feedback is fed back to the LLM.
4. Use MapGenerator as a second dataset-quality case study: caption fidelity and text-map alignment.
5. Keep SCGM for phase 2, after GPU/runtime setup, starting with complete-reference subset manifests.
6. Use SCGM edge-continuity baselines as a ready metric once generated tiles exist.

## Update: Q1 Manuscript Track Started

New manuscript workspace:

- `manuscripts/q1_geo_genai_reliability`

New expanded choropleth benchmark:

- `experiments/05_choropleth_reliability_benchmark`

Pilot result:

- `qwen2.5-coder:7b` generated 6 initial scripts for 3 prompts x 2 conditions.
- Static safety scan passed all 6 scripts.
- Execution success was 0/6.
- Basic prompts hallucinated paths/files/schema.
- Rules prompts improved grounding but failed on imports/API/schema.
- One-pass repair improved partial scores for basic prompts but still produced 0 successful executions.

## Paper Angle

Working title:

> Auditing Geo-GenAI Map Generation Artifacts: Reproducibility, Caption Fidelity, and Cartographic QA

Core claim:

> Public Geo-GenAI map-generation artifacts are increasingly available, but their reproducibility and cartographic reliability are uneven. A lightweight audit layer can expose dataset-release mismatches, missing geospatial metadata, weak caption constraints, and output QA gaps before expensive model training or subjective evaluation.

Evidence already available locally:

- dataset inventory/reproducibility matrix across five artifact groups;
- MapGenerator release-count and caption-quality audit;
- SCGM cascade-reference coverage analysis;
- choropleth geodata linting and artifact presence audit;
- seed LLM choropleth candidate benchmark with one controlled failure.

## Concrete Next Commands

```bash
python3 experiments/00_dataset_reproducibility_audit/scripts/audit_datasets.py
python3 experiments/02_mapgenerator_image_text_audit/scripts/audit_mapgenerator_pairs.py
python3 experiments/03_scgm_subset_reproduction/scripts/build_scgm_manifest.py
python3 experiments/03_scgm_subset_reproduction/scripts/compute_edge_continuity.py
python3 experiments/01_choropleth_llm_linter/scripts/inspect_data.py
python3 experiments/01_choropleth_llm_linter/scripts/lint_choropleth_data.py
python3 experiments/01_choropleth_llm_linter/scripts/audit_released_map_artifacts.py
```
