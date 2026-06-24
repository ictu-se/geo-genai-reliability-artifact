# SCGM Convolutional Filter-Bank Ridge Baseline

This baseline uses fixed multiscale convolutional features over remote-sensing tiles and a shared per-pixel ridge regressor to generate map RGB values.
It is a CPU-friendly CNN-style diagnostic, not a trained CNN or diffusion reproduction.

## Model

- estimator: StandardScaler + Ridge(alpha=2.5) over fixed convolutional RS filter bank
- input feature dimension: 52
- training pixel samples: 794624
- output target: 64x64x3
- train/validation tile overlap excluded before fitting: 6

## Summary

- train tiles: 194
- validation outputs: 100
- MAE RGB: {'mean': 19.14752, 'median': 19.991188, 'p10': 14.010356, 'p90': 22.424826}
- PSNR RGB: {'mean': 20.752409, 'median': 20.326809, 'p10': 18.893551, 'p90': 23.348072}
- global SSIM luma: {'mean': 0.347422, 'median': 0.34729, 'p10': 0.069325, 'p90': 0.599801}
- generated edge continuity: {'mean': 6.235243, 'median': 5.794922, 'p10': 4.133593, 'p90': 9.264193}

## Interpretation

- The model tests whether fixed convolutional texture and edge features add value beyond a simple 3x3 local RGB context.
- Because the filters are fixed and the regressor is per-pixel, it still cannot synthesize labels, road topology, or long-range cartographic structure.
- The result is best reported as a dependency-light CNN-style diagnostic and a bridge toward a trained pix2pix/CNN or diffusion reproduction.
