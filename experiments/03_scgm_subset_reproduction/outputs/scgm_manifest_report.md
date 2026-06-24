# SCGM / CSCMG Local Manifest

This report checks local file consistency and creates small subset manifests for lightweight reproduction work.

## Split Summary

| Split | RS | Map | RS-map matched | Ref 2x | Ref 4x | RS with ref 2x | RS with ref 4x | Zoom distribution |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| train | 135572 | 135572 | 135572 | 130701 | 115595 | 130701 | 115595 | {'15': 15106, '17': 40555, '16': 30040, '18': 45000, '14': 4871} |
| val | 1473 | 1473 | 1473 | 1192 | 900 | 1192 | 900 | {'16': 300, '14': 281, '15': 292, '17': 300, '18': 300} |

## Immediate Findings

- Base remote-sensing and target map tiles match one-to-one by filename for the checked splits.
- Cascade reference folders contain fewer files than the base RS/map folders, so reproduction code must handle missing references or filter to complete-reference subsets.
- The generated `scgm_subset_manifest_*.csv` files provide small deterministic subsets for environment smoke tests.
- The generated `scgm_complete_reference_subset_*.csv` files provide deterministic subsets where both cascade references are present.

## Next Checks

1. Add tile-neighbor discovery from z/x/y names for edge-continuity metrics.
2. Run image statistics on complete-reference subsets.
3. Run a tiny baseline only after confirming GPU/runtime setup.
