# MapGenerator VLM Caption-Fidelity Review

- model: `llava-llama3:8b`
- reviewed pairs: 20

## Summary

### MGEval

- reviewed pairs: 10
- mean VLM alignment score: 0.3
- mean proxy fidelity score: 0.741
- verdict counts: {'': 2, 'partly_supported': 5, 'error': 3}
- rows with unsupported claims: 0
- rows with omissions: 0

### MapTrain

- reviewed pairs: 10
- mean VLM alignment score: 0.356
- mean proxy fidelity score: 0.667
- verdict counts: {'': 3, 'error': 1, 'partly_supported': 6}
- rows with unsupported claims: 0
- rows with omissions: 0

## Lowest VLM Alignment Cases

| Split | Image | Proxy | VLM | Verdict | Unsupported | Omissions |
|---|---|---:|---:|---|---|---|
| MGEval | `16_1008.jpg` | 0.870 |  | error |  |  |
| MGEval | `16_1253.jpg` | 0.690 | 0.000 |  |  |  |
| MGEval | `16_1284.jpg` | 0.870 |  | error |  |  |
| MGEval | `16_221.jpg` | 0.740 | 0.000 | partly_supported |  |  |
| MGEval | `16_2568.jpg` | 0.690 | 0.000 |  |  |  |
| MGEval | `16_2764.jpg` | 0.690 |  | error |  |  |
| MGEval | `16_3150.jpg` | 0.740 | 0.000 | partly_supported |  |  |
| MapTrain | `16_202.jpg` | 0.690 | 0.000 |  |  |  |
| MapTrain | `16_348.jpg` | 0.690 | 0.000 |  |  |  |
| MapTrain | `16_373.jpg` | 0.510 | 0.000 |  |  |  |
| MapTrain | `16_601.jpg` | 0.640 |  | error |  |  |
| MapTrain | `16_630.jpg` | 0.690 | 0.000 | partly_supported |  |  |
| MapTrain | `16_719.jpg` | 0.690 | 0.000 | partly_supported |  |  |
| MGEval | `16_2977.jpg` | 0.690 | 0.500 | partly_supported |  |  |
| MGEval | `16_1783.jpg` | 0.690 | 0.800 | partly_supported |  |  |
| MGEval | `16_3260.jpg` | 0.740 | 0.800 | partly_supported |  |  |
| MapTrain | `16_23.jpg` | 0.690 | 0.800 | partly_supported |  |  |
| MapTrain | `16_54.jpg` | 0.690 | 0.800 | partly_supported |  |  |
| MapTrain | `16_587.jpg` | 0.690 | 0.800 | partly_supported |  |  |
| MapTrain | `16_683.jpg` | 0.690 | 0.800 | partly_supported |  |  |
