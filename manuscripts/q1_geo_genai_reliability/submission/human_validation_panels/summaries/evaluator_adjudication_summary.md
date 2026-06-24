# Evaluator Adjudication Summary

Generated from paired local VLM reviews and human-validation panels. These outputs prioritize human adjudication; they do not convert VLM agreement into ground truth.

| Task | Items | Exact VLM agreement | Coarse VLM agreement | Urgent human adjudication | High human priority | Low priority/stable | Mean score gap |
|---|---:|---:|---:|---:|---:|---:|---:|
| MapGenerator caption fidelity | 20 | 3/20 | 3/20 | 17 | 0 | 3 | 0.093 |
| Choropleth cartographic quality | 18 | 13/18 | 14/18 | 4 | 2 | 10 | 0.399 |

## Interpretation

- MapGenerator caption cases show high low-level feature agreement but weak semantic-support agreement, so they remain high priority for human adjudication.
- Choropleth rendered artifacts show stronger coarse agreement, especially for the validator/reference positive-control group, but score scales differ substantially.
- Final Q1 claims should report these ledgers as evaluator-sensitivity evidence and keep human labels as a remaining validation gate until collected.
