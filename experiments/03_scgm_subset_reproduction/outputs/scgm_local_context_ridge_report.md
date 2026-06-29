# SCGM Local-Context Ridge Baseline

This baseline trains a shared per-pixel ridge regressor from low-resolution remote-sensing local neighborhoods to low-resolution map RGB values.
It is not a CNN or diffusion model, but it introduces local image context and pixel-coordinate conditioning without requiring GPU libraries.

## Model

- estimator: StandardScaler + Ridge(alpha=1.0) over per-pixel 3x3 RS context
- input feature dimension: 30
- training pixel samples: 198656
- output target: 32x32x3
- train/validation tile overlap excluded before fitting: 6

## Summary

- train tiles: 194
- validation outputs: 100
- MAE RGB: {'mean': 17.542248, 'median': 17.479759, 'p10': 13.428826, 'p90': 21.63093}
- PSNR RGB: {'mean': 21.193199, 'median': 21.059921, 'p10': 19.23237, 'p90': 23.123503}
- global SSIM luma: {'mean': 0.361186, 'median': 0.366493, 'p10': 0.103821, 'p90': 0.59028}
- generated edge continuity: {'mean': 8.075412, 'median': 7.283204, 'p10': 5.32487, 'p90': 11.268359}

## Interpretation

- The model tests whether local RS texture and position improve low-resolution RS-to-map prediction beyond whole-tile feature regressors.
- Because it predicts pixels independently after a small local context window, it cannot generate labels, roads, or long-range cartographic topology.
- The result should be read as an image-structured lower bound and a dependency-light bridge toward future pix2pix/CNN or diffusion reproduction.
