# SCGM Mosaic Neighbor-Seam Stress Audit

This audit measures seam discontinuity between adjacent validation tiles when generated outputs are treated as a small mosaic. It complements per-tile image metrics by testing whether neighboring generated tiles agree at shared borders.

- validation neighbor pairs found: 24
- pair-level rows: 96

| Baseline | Pairs | Missing | Generated seam mean | Target seam mean | Stress-ratio mean | Note |
|---|---:|---:|---:|---:|---:|---|
| color-stat retrieval | 12 | 12 | 20.089735 | 4.467556 | 10.695079 | lower-than-target can mean smooth seams, not necessarily cartographic detail |
| multi-feature retrieval | 12 | 12 | 24.089735 | 4.467556 | 11.765274 | lower-than-target can mean smooth seams, not necessarily cartographic detail |
| learned forest | 12 | 12 | 4.611871 | 4.467556 | 1.754890 | lower-than-target can mean smooth seams, not necessarily cartographic detail |
| neural MLP | 12 | 12 | 12.132487 | 4.467556 | 15.686329 | lower-than-target can mean smooth seams, not necessarily cartographic detail |
| local-context ridge | 12 | 12 | 8.075412 | 4.467556 | 2.876555 | lower-than-target can mean smooth seams, not necessarily cartographic detail |
| convolutional filter-bank ridge | 12 | 12 | 6.235243 | 4.467556 | 2.332580 | lower-than-target can mean smooth seams, not necessarily cartographic detail |
| patch-embedding retrieval | 12 | 12 | 11.403971 | 4.467556 | 5.200429 | lower-than-target can mean smooth seams, not necessarily cartographic detail |
| trained tiny CNN | 12 | 12 | 9.221897 | 4.467556 | 3.392778 | lower-than-target can mean smooth seams, not necessarily cartographic detail |

Interpretation: the best mosaic seam score is not automatically the best map. A model can reduce seam differences by washing out roads, labels, and symbol texture. The audit is therefore reported beside MAE, PSNR, SSIM, contact sheets, and qualitative cartographic-detail cautions.
