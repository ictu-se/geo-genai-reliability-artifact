# MapGenerator VLM Caption-Fidelity Review

- model: `qwen2.5vl:3b`
- reviewed pairs: 20

## Summary

### MGEval

- reviewed pairs: 10
- mean VLM alignment score: 0.88
- mean proxy fidelity score: 0.741
- verdict counts: {'partly_supported': 10}
- rows with unsupported claims: 10
- rows with omissions: 4

### MapTrain

- reviewed pairs: 10
- mean VLM alignment score: 0.89
- mean proxy fidelity score: 0.667
- verdict counts: {'partly_supported': 8, 'supported': 2}
- rows with unsupported claims: 8
- rows with omissions: 5

## Lowest VLM Alignment Cases

| Split | Image | Proxy | VLM | Verdict | Unsupported | Omissions |
|---|---|---:|---:|---|---|---|
| MGEval | `16_1783.jpg` | 0.690 | 0.800 | partly_supported | The map shows a section of Lapping Park Disc Golf Course | A blue water feature is visible to the southwest of the course, indicating a body of water or stream. |
| MGEval | `16_2568.jpg` | 0.690 | 0.800 | partly_supported | There are additional geographic entities or labels visible in this section of the map. |  |
| MGEval | `16_3150.jpg` | 0.740 | 0.800 | partly_supported | The road is labeled '335' horizontally | No additional geographic features or entities are labeled on this map segment. |
| MapTrain | `16_348.jpg` | 0.690 | 0.800 | partly_supported | There are no additional geographic features or landmarks visible. |  |
| MapTrain | `16_601.jpg` | 0.640 | 0.800 | partly_supported | The freeway runs vertically across the image. | There is a thin, light blue line intersecting the freeway, possibly indicating a waterway or road. The background is a light green, suggesting a general land area. |
| MGEval | `16_1008.jpg` | 0.870 | 0.900 | partly_supported | Kingdom Hall of Jehovah's Witnesses |  |
| MGEval | `16_1253.jpg` | 0.690 | 0.900 | partly_supported | The road runs horizontally across the map. |  |
| MGEval | `16_1284.jpg` | 0.870 | 0.900 | partly_supported | A linear feature is a road or boundary |  |
| MGEval | `16_2764.jpg` | 0.690 | 0.900 | partly_supported | There are two parallel lanes indicating the highway. | The hotel Fairfield Inn & Suites Louisville is marked to the northeast of the highway. |
| MGEval | `16_2977.jpg` | 0.690 | 0.900 | partly_supported | The map focuses on the course of the waterway without additional geographic features or labels. |  |
| MGEval | `16_3260.jpg` | 0.740 | 0.900 | partly_supported | The waterway runs horizontally through the map. | No additional geographic entities or labels are visible on this map section. |
| MapTrain | `16_202.jpg` | 0.690 | 0.900 | partly_supported | roads | additional geographic features |
| MapTrain | `16_23.jpg` | 0.690 | 0.900 | partly_supported | The map shows a section of 'Hill Rd' running vertically. | No additional geographic entities or labels are visible in the image. |
| MapTrain | `16_373.jpg` | 0.510 | 0.900 | partly_supported | There is a marked location for 'Our House Restaurant and Banquet Facility' near the road. |  |
| MapTrain | `16_587.jpg` | 0.690 | 0.900 | supported |  |  |
| MapTrain | `16_630.jpg` | 0.690 | 0.900 | partly_supported | open land |  |
| MapTrain | `16_683.jpg` | 0.690 | 0.900 | partly_supported | The caption mentions 'several intersecting roads,' but the image shows only one road segment with a label | No additional geographic entities or landmarks are visible in this section of the map. |
| MapTrain | `16_719.jpg` | 0.690 | 0.900 | partly_supported | The reservoir is surrounded by green areas | No additional geographic entities or labels are visible in this section of the map. |
| MGEval | `16_221.jpg` | 0.740 | 1.000 | partly_supported | The road labeled with the number 60 is horizontal |  |
| MapTrain | `16_54.jpg` | 0.690 | 1.000 | supported |  |  |
