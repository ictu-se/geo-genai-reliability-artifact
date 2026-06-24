# SCGM Retrieval Baseline

This lightweight generated-output baseline retrieves the nearest train remote-sensing tile by color statistics and uses its paired train map tile as the validation output.

It is not intended to be a strong model. It provides a reproducible lower bound for applying generated-output metrics without training a diffusion model.

## Summary

- train candidates: 200
- validation outputs: 100
- exact tile candidates excluded: 6
- same-zoom retrievals: 100
- MAE RGB: {'mean': 16.767246, 'median': 16.875938, 'p10': 4.401522, 'p90': 30.814087}
- PSNR RGB: {'mean': 19.931509, 'median': 18.702965, 'p10': 16.768648, 'p90': 24.497568}
- global SSIM luma: {'mean': 0.245472, 'median': 0.229878, 'p10': 0.068687, 'p90': 0.457476}
- generated edge continuity: {'mean': 20.089735, 'median': 22.808594, 'p10': 5.73802, 'p90': 35.796093}

## Interpretation

- Retrieval gives the manuscript a generated-output baseline for the SCGM track.
- The baseline is intentionally weak and should be replaced or complemented by a learned model when runtime/GPU resources allow.
- The same metric code can be reused for future pix2pix, ControlNet, or SCGM reproduction outputs.
