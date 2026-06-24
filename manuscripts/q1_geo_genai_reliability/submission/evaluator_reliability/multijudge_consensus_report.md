# Calibrated Multi-Judge VLM Consensus

This report aggregates parseable local VLM reviews into coarse consensus tiers. It is an evaluator-calibration layer and should not be cited as human ground truth.

| Task | Consensus items | >=2 usable judges | High | Medium | Low/insufficient | Positive | Below-threshold | Discordant/tied | Max judges |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| MapGenerator caption fidelity | 20 | 20 | 1 | 15 | 4 | 2 | 14 | 4 | 4 |
| Choropleth cartographic quality | 18 | 18 | 13 | 4 | 1 | 13 | 4 | 1 | 3 |

## Interpretation

- The consensus layer uses only schema-conformant VLM outputs; failed JSON or missing scores reduce coverage rather than being imputed.
- High-confidence rows indicate unanimous coarse agreement among usable judges, but they remain automated labels.
- Medium and low-confidence rows identify where expert human validation should be prioritized before making semantic caption-fidelity or cartographic-quality claims.
