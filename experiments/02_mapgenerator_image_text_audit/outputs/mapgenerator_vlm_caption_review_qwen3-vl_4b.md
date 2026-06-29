# MapGenerator VLM Caption-Fidelity Review

- model: `qwen3-vl:4b`
- reviewed pairs: 10

## Summary

### MGEval

- reviewed pairs: 5
- mean VLM alignment score: 0.7
- mean proxy fidelity score: 0.69
- verdict counts: {'partly_supported': 1, 'error': 4}
- rows with unsupported claims: 1
- rows with omissions: 0

### MapTrain

- reviewed pairs: 5
- mean VLM alignment score: 0
- mean proxy fidelity score: 0.644
- verdict counts: {'error': 5}
- rows with unsupported claims: 0
- rows with omissions: 0

## Lowest VLM Alignment Cases

| Split | Image | Proxy | VLM | Verdict | Unsupported | Omissions |
|---|---|---:|---:|---|---|---|
| MGEval | `16_1783.jpg` | 0.690 |  | error |  |  |
| MGEval | `16_2568.jpg` | 0.690 |  | error |  |  |
| MGEval | `16_2764.jpg` | 0.690 |  | error |  |  |
| MGEval | `16_2977.jpg` | 0.690 |  | error |  |  |
| MapTrain | `16_202.jpg` | 0.690 |  | error |  |  |
| MapTrain | `16_23.jpg` | 0.690 |  | error |  |  |
| MapTrain | `16_348.jpg` | 0.690 |  | error |  |  |
| MapTrain | `16_373.jpg` | 0.510 |  | error |  |  |
| MapTrain | `16_601.jpg` | 0.640 |  | error |  |  |
| MGEval | `16_1253.jpg` | 0.690 | 0.700 | partly_supported | There are no additional geographic entities or landmarks visible on this map section |  |
