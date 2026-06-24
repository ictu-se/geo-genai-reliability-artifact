# MapGenerator VLM Caption-Fidelity Review

- model: `granite3.2-vision:latest`
- reviewed pairs: 20

## Summary

### MGEval

- reviewed pairs: 10
- mean VLM alignment score: 1.0
- mean proxy fidelity score: 0.741
- verdict counts: {'supported': 10}
- rows with unsupported claims: 0
- rows with omissions: 0

### MapTrain

- reviewed pairs: 10
- mean VLM alignment score: 0.945
- mean proxy fidelity score: 0.667
- verdict counts: {'supported': 9, 'partly_supported': 1}
- rows with unsupported claims: 0
- rows with omissions: 0

## Lowest VLM Alignment Cases

| Split | Image | Proxy | VLM | Verdict | Unsupported | Omissions |
|---|---|---:|---:|---|---|---|
| MapTrain | `16_348.jpg` | 0.690 | 0.800 | partly_supported |  |  |
| MapTrain | `16_601.jpg` | 0.640 | 0.800 | supported |  |  |
| MapTrain | `16_23.jpg` | 0.690 | 0.850 | supported |  |  |
| MGEval | `16_1008.jpg` | 0.870 | 1.000 | supported |  |  |
| MGEval | `16_1253.jpg` | 0.690 | 1.000 | supported |  |  |
| MGEval | `16_1284.jpg` | 0.870 | 1.000 | supported |  |  |
| MGEval | `16_1783.jpg` | 0.690 | 1.000 | supported |  |  |
| MGEval | `16_221.jpg` | 0.740 | 1.000 | supported |  |  |
| MGEval | `16_2568.jpg` | 0.690 | 1.000 | supported |  |  |
| MGEval | `16_2764.jpg` | 0.690 | 1.000 | supported |  |  |
| MGEval | `16_2977.jpg` | 0.690 | 1.000 | supported |  |  |
| MGEval | `16_3150.jpg` | 0.740 | 1.000 | supported |  |  |
| MGEval | `16_3260.jpg` | 0.740 | 1.000 | supported |  |  |
| MapTrain | `16_202.jpg` | 0.690 | 1.000 | supported |  |  |
| MapTrain | `16_373.jpg` | 0.510 | 1.000 | supported |  |  |
| MapTrain | `16_54.jpg` | 0.690 | 1.000 | supported |  |  |
| MapTrain | `16_587.jpg` | 0.690 | 1.000 | supported |  |  |
| MapTrain | `16_630.jpg` | 0.690 | 1.000 | supported |  |  |
| MapTrain | `16_683.jpg` | 0.690 | 1.000 | supported |  |  |
| MapTrain | `16_719.jpg` | 0.690 | 1.000 | supported |  |  |
