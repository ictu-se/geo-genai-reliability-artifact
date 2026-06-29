# SCGM Edge-Continuity Baseline

This computes mean absolute RGB differences between adjacent tile borders. Lower values mean adjacent tiles are more visually continuous at the shared edge.

## Validation Split

| Group | Pairs | Mean | Median | P90 | Max |
|---|---:|---:|---:|---:|---:|
| `val/map_256/down` | 27 | 2.752893 | 2.083333 | 6.082031 | 9.467448 |
| `val/map_256/right` | 32 | 1.853434 | 1.104167 | 3.544401 | 9.363281 |
| `val/rs_256/down` | 27 | 13.467978 | 15.924479 | 19.422134 | 23.701822 |
| `val/rs_256/right` | 32 | 11.520061 | 10.635417 | 17.91901 | 21.700521 |

## Use

- Treat these as data/reference baselines before evaluating generated tiles.
- Future generated outputs can be scored with the same border metric and compared against `map_256` ground truth.
- The metric is intentionally simple and should be paired with road/line-continuity checks later.
