# Human Validation Packet Preflight

This preflight validates annotator packet schemas, panel coverage, local artifact links, and optional completed-label values against the rubric. Blank prepared packets may pass in `blank_or_partial` mode; completed packets must have required labels.

## Summary

- files checked: 4
- passed: 4/4

## Checks

| File | Task | Mode | Rows | Expected | Missing artifacts | Invalid values | Incomplete rows | Score errors | Status |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| `manuscripts/q1_geo_genai_reliability/submission/human_validation_panels/annotator_packets/mapgenerator_caption_fidelity_A_completed.csv` | mapgenerator_caption_fidelity | blank_or_partial | 20 | 20 | 0 | 0 | 0 | 0 | pass |
| `manuscripts/q1_geo_genai_reliability/submission/human_validation_panels/annotator_packets/mapgenerator_caption_fidelity_B_completed.csv` | mapgenerator_caption_fidelity | blank_or_partial | 20 | 20 | 0 | 0 | 0 | 0 | pass |
| `manuscripts/q1_geo_genai_reliability/submission/human_validation_panels/annotator_packets/choropleth_cartographic_quality_A_completed.csv` | choropleth_cartographic_quality | blank_or_partial | 18 | 18 | 0 | 0 | 0 | 0 | pass |
| `manuscripts/q1_geo_genai_reliability/submission/human_validation_panels/annotator_packets/choropleth_cartographic_quality_B_completed.csv` | choropleth_cartographic_quality | blank_or_partial | 18 | 18 | 0 | 0 | 0 | 0 | pass |
