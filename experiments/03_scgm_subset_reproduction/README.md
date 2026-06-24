# 03 SCGM Subset Reproduction

This track reproduces or approximates SCGM experiments on a smaller local subset.

Data source:

- `../../data/raw/SCGM/extracted/TMGN_1814`
- `../../data/repos/SCGM`

Implemented tasks:

1. Build a small train/val subset manifest.
2. Inspect scale and tile-neighbor metadata.
3. Compute validation edge-continuity baselines for RS and target map tiles.
4. Run a lightweight retrieval generated-output baseline.
5. Run multi-feature retrieval, learned forest, compact neural MLP, local-context ridge, convolutional filter-bank ridge, patch-embedding retrieval, and tiny trained CNN generated-output baselines.
6. Evaluate image similarity and generated tile-edge continuity.
7. Stress-test generated validation outputs as partial mosaics by measuring neighbor-seam discontinuity between adjacent generated tiles.

Regenerate:

```bash
python3 experiments/03_scgm_subset_reproduction/scripts/build_scgm_manifest.py
python3 experiments/03_scgm_subset_reproduction/scripts/compute_edge_continuity.py
python3 experiments/03_scgm_subset_reproduction/scripts/run_scgm_retrieval_baseline.py
python3 experiments/03_scgm_subset_reproduction/scripts/run_scgm_multifeature_retrieval_baseline.py
python3 experiments/03_scgm_subset_reproduction/scripts/run_scgm_learned_forest_baseline.py
python3 experiments/03_scgm_subset_reproduction/scripts/run_scgm_mlp_baseline.py
python3 experiments/03_scgm_subset_reproduction/scripts/run_scgm_local_context_ridge_baseline.py
python3 experiments/03_scgm_subset_reproduction/scripts/run_scgm_convolutional_filter_ridge_baseline.py
python3 experiments/03_scgm_subset_reproduction/scripts/run_scgm_patch_embedding_retrieval_baseline.py
python3 experiments/03_scgm_subset_reproduction/scripts/run_scgm_tiny_cnn_baseline.py
python3 experiments/03_scgm_subset_reproduction/scripts/compute_scgm_mosaic_continuity_stress.py
```

Current outputs:

- `outputs/scgm_split_summary.json`
- `outputs/scgm_edge_continuity_summary.json`
- `outputs/scgm_retrieval_baseline_metrics.csv`
- `outputs/scgm_retrieval_baseline_edge_continuity.csv`
- `outputs/scgm_retrieval_baseline_summary.json`
- `outputs/scgm_retrieval_baseline_contact_sheet.jpg`
- `outputs/scgm_multifeature_retrieval_summary.json`
- `outputs/scgm_learned_forest_summary.json`
- `outputs/scgm_mlp_summary.json`
- `outputs/scgm_local_context_ridge_summary.json`
- `outputs/scgm_convolutional_filter_ridge_summary.json`
- `outputs/scgm_patch_embedding_retrieval_summary.json`
- `outputs/scgm_tiny_cnn_summary.json`
- `outputs/scgm_mosaic_neighbor_stress_pairs.csv`
- `outputs/scgm_mosaic_neighbor_stress_summary.json`
- `outputs/scgm_mosaic_neighbor_stress_report.md`
- generated map folders and contact sheets for each baseline

Current baselines:

- 200 train candidates, 100 validation outputs.
- 6 exact tile-id candidates excluded to avoid leakage.
- Color-stat retrieval: mean RGB MAE 16.77, mean RGB PSNR 19.93, mean global luma SSIM 0.245.
- Multi-feature retrieval: mean RGB MAE 21.68, mean RGB PSNR 19.19, mean global luma SSIM 0.290.
- Learned forest: mean RGB MAE 17.36, mean RGB PSNR 21.61, mean global luma SSIM 0.409.
- Compact neural MLP: mean RGB MAE 30.73, mean RGB PSNR 17.96, mean global luma SSIM 0.303.
- Local-context ridge: mean RGB MAE 17.54, mean RGB PSNR 21.19, mean global luma SSIM 0.361.
- Convolutional filter-bank ridge: mean RGB MAE 19.15, mean RGB PSNR 20.75, mean global luma SSIM 0.347, mean generated edge continuity 6.24.
- Patch-embedding retrieval: mean RGB MAE 16.34, mean RGB PSNR 19.99, mean global luma SSIM 0.274, mean generated edge continuity 11.40.
- Trained tiny CNN: mean RGB MAE 26.10, mean RGB PSNR 18.47, mean global luma SSIM 0.366, mean generated edge continuity 9.22.
- Mosaic neighbor-seam audit: 8 baselines, 96 generated neighbor-pair rows, with 12 available adjacent validation pairs per baseline. Learned forest has the lowest generated seam mean among current baselines, but this is interpreted together with contact sheets because low seam discontinuity can also reflect over-smoothing.

Remaining Q1-strengthening task:

- add a trained CNN/pix2pix, diffusion-style, or embedding-supervised SCGM reproduction when compute and dependencies permit.
