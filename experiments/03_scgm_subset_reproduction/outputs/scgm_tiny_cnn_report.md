# SCGM Tiny Trained CNN Baseline

This baseline trains a small fully convolutional RS-to-map model on the leakage-filtered SCGM subset.
It is a lower-bound trained CNN condition, not an official SCGM diffusion reproduction.

## Model

- estimator: TinyCNN(3->24->32->32->16->3 conv stack, sigmoid output)
- output target: 64x64x3
- train tiles after overlap filtering: 194
- validation outputs: 100
- train/validation tile overlap excluded before fitting: 6
- epochs: 14
- device: mps
- training loss first/final: 0.199439 / 0.063394

## Summary

- MAE RGB: {'mean': 26.100397, 'median': 26.492479, 'p10': 22.626059, 'p90': 29.342575}
- PSNR RGB: {'mean': 18.466171, 'median': 18.23185, 'p10': 17.551096, 'p90': 19.283501}
- global SSIM luma: {'mean': 0.366129, 'median': 0.33037, 'p10': 0.191427, 'p90': 0.579186}
- generated edge continuity: {'mean': 9.221896, 'median': 8.02474, 'p10': 4.771744, 'p90': 14.25039}

## Interpretation

- This closes the gap between fixed-filter diagnostics and a genuinely trained convolutional image-to-image baseline.
- The model is intentionally small so that the experiment is reproducible on local CPU/MPS hardware.
- The output should still be interpreted as a lower-bound diagnostic: it lacks cascade references, scale conditioning, adversarial/perceptual losses, and diffusion sampling.
