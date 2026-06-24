# SCGM Patch-Embedding Retrieval Baseline

This baseline builds validation map tiles by retrieving local remote-sensing patches from the train split and copying their paired map patches.
It is a dependency-light image-to-image diagnostic: local and mosaic-like, but not a trained CNN, GAN, or diffusion model.

## Model

- estimator: 64x64 RS patch nearest-neighbor retrieval, patch=8
- input feature dimension: 264
- patch bank size: 12416
- patches per output: 64
- train/validation tile overlap excluded before retrieval: 6
- unique source tiles used: 193

## Summary

- train tiles: 194
- validation outputs: 100
- MAE RGB: {'mean': 16.335779, 'median': 15.684595, 'p10': 11.090369, 'p90': 22.503487}
- PSNR RGB: {'mean': 19.992807, 'median': 20.029947, 'p10': 18.019836, 'p90': 22.007727}
- global SSIM luma: {'mean': 0.273621, 'median': 0.247993, 'p10': 0.16329, 'p90': 0.439767}
- generated edge continuity: {'mean': 11.403972, 'median': 11.383463, 'p10': 6.737109, 'p90': 16.962629}

## Interpretation

- Patch retrieval tests local image-to-image transfer more directly than whole-tile retrieval.
- The mosaic construction can preserve local color/texture cues, but it has no learned global cartographic structure and can create patch seams.
- The result is a reproducible lower-bound bridge toward trained pix2pix/CNN or diffusion SCGM reproduction.
