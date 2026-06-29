# SCGM Multi-Feature Retrieval Baseline

This baseline retrieves train map tiles using a stronger remote-sensing feature vector than the simple color-statistics baseline.
The feature vector concatenates downsampled RGB grids, edge grids, RGB summary statistics, and color histograms.
It is still not a trained generator; it is a deterministic embedding-style retrieval lower bound.

## Summary

- train candidates: 200
- validation outputs: 100
- exact tile candidates excluded: 6
- same-zoom retrievals: 100
- MAE RGB: {'mean': 21.684555, 'median': 24.289112, 'p10': 6.048589, 'p90': 32.387108}
- PSNR RGB: {'mean': 19.187075, 'median': 17.986187, 'p10': 16.611565, 'p90': 23.65383}
- global SSIM luma: {'mean': 0.290337, 'median': 0.252883, 'p10': 0.131242, 'p90': 0.53899}
- generated edge continuity: {'mean': 24.089735, 'median': 31.539062, 'p10': 5.213672, 'p90': 35.861069}
