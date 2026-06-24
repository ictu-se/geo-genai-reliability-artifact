# MapGenerator VLM Caption-Fidelity Review

- model: `minicpm-v:latest`
- reviewed pairs: 20

## Summary

### MGEval

- reviewed pairs: 10
- mean VLM alignment score: 0
- mean proxy fidelity score: 0.741
- verdict counts: {'error': 10}
- rows with unsupported claims: 0
- rows with omissions: 0

### MapTrain

- reviewed pairs: 10
- mean VLM alignment score: 0.8
- mean proxy fidelity score: 0.667
- verdict counts: {'partly_supported': 1, 'error': 9}
- rows with unsupported claims: 0
- rows with omissions: 1

## Lowest VLM Alignment Cases

| Split | Image | Proxy | VLM | Verdict | Unsupported | Omissions |
|---|---|---:|---:|---|---|---|
| MGEval | `16_1008.jpg` | 0.870 |  | error |  |  |
| MGEval | `16_1253.jpg` | 0.690 |  | error |  |  |
| MGEval | `16_1284.jpg` | 0.870 |  | error |  |  |
| MGEval | `16_1783.jpg` | 0.690 |  | error |  |  |
| MGEval | `16_221.jpg` | 0.740 |  | error |  |  |
| MGEval | `16_2568.jpg` | 0.690 |  | error |  |  |
| MGEval | `16_2764.jpg` | 0.690 |  | error |  |  |
| MGEval | `16_2977.jpg` | 0.690 |  | error |  |  |
| MGEval | `16_3150.jpg` | 0.740 |  | error |  |  |
| MGEval | `16_3260.jpg` | 0.740 |  | error |  |  |
| MapTrain | `16_202.jpg` | 0.690 |  | error |  |  |
| MapTrain | `16_23.jpg` | 0.690 |  | error |  |  |
| MapTrain | `16_348.jpg` | 0.690 |  | error |  |  |
| MapTrain | `16_54.jpg` | 0.690 |  | error |  |  |
| MapTrain | `16_587.jpg` | 0.690 |  | error |  |  |
| MapTrain | `16_601.jpg` | 0.640 |  | error |  |  |
| MapTrain | `16_630.jpg` | 0.690 |  | error |  |  |
| MapTrain | `16_683.jpg` | 0.690 |  | error |  |  |
| MapTrain | `16_719.jpg` | 0.690 |  | error |  |  |
| MapTrain | `16_373.jpg` | 0.510 | 0.800 | partly_supported |  | The map shows a section of Adelphia-Farmingdale Road, which runs horizontally across the image. |
