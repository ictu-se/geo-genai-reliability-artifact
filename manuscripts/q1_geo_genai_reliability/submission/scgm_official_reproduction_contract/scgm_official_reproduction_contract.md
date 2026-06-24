# SCGM Official Reproduction Contract

This contract records the exact local bridge from the official SCGM repository to a future official/cascade-conditioned reproduction run. It is intentionally conservative: no official SCGM output claim is made until checkpoints, runtime, and scored outputs exist.

## Runtime Contract

| Item | Status | Evidence | Notes |
|---|---|---|---|
| official_repo_commit | pinned | https://github.com/Magician-MO/SCGM.git@a3ea795af8f095af46bb44a97ff652bb264d3639 | Use this exact commit for any official/cascade-conditioned claim. |
| python_runtime | contract_drafted | python>=3.10,<3.12 | Chosen to match modern PyTorch/Lightning while avoiding untested Python 3.12 API drift. |
| core_deep_learning_stack | contract_drafted | pytorch, torchvision, pytorch-lightning, torchmetrics, omegaconf, einops, numpy, pillow, tqdm | Derived from official entry-point imports and model utilities. |
| diffusion_dependency | contract_drafted | Stable Diffusion SD-2.1-base remains an upstream prerequisite in README. | Model weights are not redistributed by this manuscript package. |
| device_policy | contract_drafted | official configs assume GPU; inference script has cpu/cuda/mps switch but heavy diffusion inference should be treated as GPU-preferred. | CPU smoke tests may validate imports/configs, not final official metrics. |
| local_data_policy | ready | data/raw/SCGM/extracted/TMGN_1814 | Local CSCMG extract has base RS/map pairs and deterministic complete-reference subset manifests. |
| checkpoint_policy | external_blocker | official resume paths point to process/init weights that are not present locally. | Do not claim official reproduction until obtained checkpoints or a documented training path exists. |

## Config And Subset Mapping

| Run | Official config | Data config | Checkpoint reference | Local subset | Rows | Reference status | Planned output |
|---|---|---|---|---|---:|---|---|
| 2c_oz_val_complete_reference | `configs/test_refmap_level_2c_oz.yaml` | `configs/datasetcfg/reference_map_test_level_2c_oz.yaml` | `data/checkpoints/process_weight/g1-l1-2c+oz-1102-t165500-c30.771.ckpt` | `experiments/03_scgm_subset_reproduction/outputs/scgm_complete_reference_subset_val_first200.csv` | 200 | ready | `experiments/03_scgm_subset_reproduction/outputs/scgm_official_2c_oz_val` |
| 4c_oz_val_complete_reference | `configs/test_refmap_level_4c_oz.yaml` | `configs/datasetcfg/reference_map_test_level_4c_oz.yaml` | `data/checkpoints/process_weight/g1-l1-4c+oz-0922-t169500-c30.700.ckpt` | `experiments/03_scgm_subset_reproduction/outputs/scgm_complete_reference_subset_val_first200.csv` | 200 | ready | `experiments/03_scgm_subset_reproduction/outputs/scgm_official_4c_oz_val` |

## Planned Commands

| Order | Run | Command | Required before running | Expected artifacts |
|---:|---|---|---|---|
| 1 | 2c_oz_val_complete_reference | `cd data/repos/SCGM && python inference_refmap_batch_level.py --ckpt data/checkpoints/process_weight/g1-l1-2c+oz-1102-t165500-c30.771.ckpt --model_config configs/modelcfg/refmap_level_wc.yaml --data_config ../../../manuscripts/q1_geo_genai_reliability/submission/scgm_official_reproduction_contract/local_overrides/reference_map_test_level_2c_oz_local.yaml --output ../../../experiments/03_scgm_subset_reproduction/outputs/scgm_official_2c_oz_val --steps 50 --seed 231 --device cuda` | official checkpoint present; local override dataroot bridge generated; GPU runtime available | samples/; targets/; log_metrics.txt |
| 2 | 4c_oz_val_complete_reference | `cd data/repos/SCGM && python inference_refmap_batch_level.py --ckpt data/checkpoints/process_weight/g1-l1-4c+oz-0922-t169500-c30.700.ckpt --model_config configs/modelcfg/refmap_level_wc.yaml --data_config ../../../manuscripts/q1_geo_genai_reliability/submission/scgm_official_reproduction_contract/local_overrides/reference_map_test_level_4c_oz_local.yaml --output ../../../experiments/03_scgm_subset_reproduction/outputs/scgm_official_4c_oz_val --steps 50 --seed 231 --device cuda` | official checkpoint present; local override dataroot bridge generated; GPU runtime available | samples/; targets/; log_metrics.txt |
| 3 | metric_ingest | `Feed official samples/targets into the existing MAE/PSNR/SSIM, edge-continuity, and mosaic neighbor-seam scoring scripts after normalizing filenames.` | official samples and target tiles generated | official metrics CSV/JSON and report files under experiments/03_scgm_subset_reproduction/outputs |

## Claim Boundary

- Current manuscript evidence remains diagnostic, not an official SCGM reproduction.
- The complete-reference validation subset is ready for controlled official inference once checkpoint and runtime blockers are resolved.
- Any future upgrade must add generated official samples, target copies, metric CSV/JSON files, and a manuscript-table update before changing the claim language.
