# SCGM Compact Neural MLP Baseline

This baseline trains a CPU-friendly neural MLP from remote-sensing tile features to low-resolution map pixels.
It is not a diffusion reproduction, but it is a fitted neural RS-to-map generated-output condition with the same leakage guard and metrics as the retrieval and forest baselines.

## Model

- estimator: StandardScaler + MLPRegressor(hidden_layer_sizes=(64,), solver='lbfgs', alpha=0.1)
- input feature dimension: 1039
- output target: 16x16x3
- train/validation tile overlap excluded before fitting: 6
- training iterations: 350
- training loss: 0.066365
- best validation score: None

## Summary

- train samples: 194
- validation outputs: 100
- MAE RGB: {'mean': 30.725883, 'median': 23.033997, 'p10': 18.114159, 'p90': 58.801395}
- PSNR RGB: {'mean': 17.955496, 'median': 18.74062, 'p10': 12.043325, 'p90': 21.487251}
- global SSIM luma: {'mean': 0.303307, 'median': 0.25767, 'p10': 0.158878, 'p90': 0.540507}
- generated edge continuity: {'mean': 12.132487, 'median': 0.011719, 'p10': 0.0, 'p90': 29.630207}

## Interpretation

This baseline is a neural diagnostic rather than a production map generator. It tests whether a compact fitted nonlinear model can improve the generated-output layer without copying validation tiles. Visual contact sheets should be read alongside metrics because smooth low-resolution predictions can improve some image scores while losing roads, labels, and cartographic symbols.
