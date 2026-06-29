# SCGM Learned Forest Baseline

This baseline trains a CPU-friendly random-forest regressor from remote-sensing tile features to low-resolution map pixels.
It is not a diffusion model and should be interpreted as a weak learned lower bound, but it is a genuine fitted RS-to-map mapping rather than nearest-neighbor retrieval.

## Model

- estimator: RandomForestRegressor(n_estimators=40, max_depth=12, min_samples_leaf=2)
- input feature dimension: 1039
- output target: 16x16x3
- train/validation tile overlap excluded before fitting: 6

## Summary

- train samples: 194
- validation outputs: 100
- MAE RGB: {'mean': 17.362703, 'median': 17.028126, 'p10': 12.440184, 'p90': 23.228569}
- PSNR RGB: {'mean': 21.608828, 'median': 21.320431, 'p10': 19.174232, 'p90': 23.855383}
- global SSIM luma: {'mean': 0.409008, 'median': 0.369864, 'p10': 0.193912, 'p90': 0.67811}
- generated edge continuity: {'mean': 4.611871, 'median': 4.508463, 'p10': 3.679818, 'p90': 5.991928}

## Interpretation

- The model is intentionally small enough to rerun without GPU resources.
- Low-resolution regression tends to smooth cartographic detail, so it should be compared against retrieval baselines as a lower bound rather than a competitive generator.
- The baseline is useful because it makes the SCGM track include a learned generated-output condition with the same metric and leakage-audit scaffold as the retrieval baselines.
