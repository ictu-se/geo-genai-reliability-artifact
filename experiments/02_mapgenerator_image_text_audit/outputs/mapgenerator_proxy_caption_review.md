# MapGenerator Proxy Caption-Fidelity Review

This review uses deterministic image proxies rather than a VLM or human labels. It is designed to prioritize cases for deeper review and to provide a reproducible pre-screening layer.

## Summary

### MGEval

- reviewed pairs: 100
- mean proxy fidelity score: 0.946
- severity counts: {'medium': 34, 'low': 66}
- top proxy issues: {'road_caption_lacks_relation': 15, 'generic_no_feature_claim_needs_visual_review': 11, 'possible_water_omission': 10, 'green_mention_low_green_signal': 2, 'water_mention_low_blue_signal': 2, 'possible_green_omission': 2}

### MapTrain

- reviewed pairs: 100
- mean proxy fidelity score: 0.914
- severity counts: {'medium': 53, 'low': 46, 'high': 1}
- top proxy issues: {'generic_no_feature_claim_needs_visual_review': 38, 'possible_water_omission': 18, 'road_caption_lacks_relation': 7, 'possible_green_omission': 1, 'green_mention_low_green_signal': 1}

## Highest-Severity Proxy Mismatches

| Split | Image | Score | Severity | Proxy issues | Caption |
|---|---|---:|---|---|---|
| MapTrain | `16_373.jpg` | 0.510 | high | possible_green_omission;generic_no_feature_claim_needs_visual_review;road_caption_lacks_relation | The google map shows a section of Adelphia-Farmingdale Road, which runs horizontally across the image. There is a marked location for "Our House Restaurant a... |
| MapTrain | `16_601.jpg` | 0.640 | medium | possible_water_omission;road_caption_lacks_relation | The google map shows a section of the Robert T. Monagan Freeway, which runs horizontally across the image. There is a thin, light blue line intersecting the ... |
| MGEval | `16_1253.jpg` | 0.690 | medium | generic_no_feature_claim_needs_visual_review;road_caption_lacks_relation | The google map shows a location marked as "Caldwell Sash Company" situated along Scottsville Road. The road appears to run diagonally across the map. The sur... |
| MGEval | `16_1783.jpg` | 0.690 | medium | green_mention_low_green_signal;road_caption_lacks_relation | The google map shows a section of Lapping Park Disc Golf Course, located near Milner Way. A blue water feature is visible to the southwest of the course, ind... |
| MapTrain | `16_202.jpg` | 0.690 | medium | possible_water_omission;generic_no_feature_claim_needs_visual_review | The google map shows a light green area with a blue line labeled "Sunken Branch," indicating a waterway. The waterway has a few curves and branches off into ... |
| MapTrain | `16_23.jpg` | 0.690 | medium | possible_water_omission;generic_no_feature_claim_needs_visual_review | The google map shows a section of "Hill Rd" running horizontally. A blue line, likely representing a waterway, runs parallel and slightly above the road. The... |
| MGEval | `16_2568.jpg` | 0.690 | medium | possible_water_omission;generic_no_feature_claim_needs_visual_review | The google map shows a section of a waterway labeled "Curry Fork." The waterway curves through the area, surrounded by a light green background, which typica... |
| MGEval | `16_2764.jpg` | 0.690 | medium | possible_water_omission;possible_green_omission | The google map shows a section of Interstate 265, which runs vertically through the center. There are two parallel lanes indicating the highway. A hotel, Fai... |
| MGEval | `16_2977.jpg` | 0.690 | medium | possible_water_omission;generic_no_feature_claim_needs_visual_review | The google map shows a section of a waterway labeled "Floyds Fork." The waterway is depicted in blue, winding through a light green area, which likely repres... |
| MapTrain | `16_348.jpg` | 0.690 | medium | possible_water_omission;generic_no_feature_claim_needs_visual_review | The google map shows a location labeled "Corkum Tree Farm." There are light blue lines indicating roads or pathways surrounding the area. The map is minimali... |
| MapTrain | `16_54.jpg` | 0.690 | medium | generic_no_feature_claim_needs_visual_review;road_caption_lacks_relation | The google map shows a section of land featuring Neshaminy Creek, which flows in a generally southeast direction. Above the creek, there is a road labeled "R... |
| MapTrain | `16_587.jpg` | 0.690 | medium | possible_water_omission;generic_no_feature_claim_needs_visual_review | The google map shows a section of Del Puerto Canyon Road, which runs horizontally across the image. The road is depicted in blue, indicating its path through... |
| MapTrain | `16_630.jpg` | 0.690 | medium | green_mention_low_green_signal;generic_no_feature_claim_needs_visual_review | The google map shows a section of a river running vertically through the center. A road labeled "Shiells Rd" crosses the river horizontally. The surrounding ... |
| MapTrain | `16_683.jpg` | 0.690 | medium | possible_water_omission;generic_no_feature_claim_needs_visual_review | The google map shows a location labeled "WM - Guadalupe Rubbish Disposal Facility." It is situated among several intersecting roads. The surrounding area is ... |
| MapTrain | `16_719.jpg` | 0.690 | medium | possible_water_omission;generic_no_feature_claim_needs_visual_review | The google map shows the Calero Reservoir, depicted in blue, surrounded by beige land areas. The reservoir has an irregular shape with several inlets and ext... |
| MGEval | `16_221.jpg` | 0.740 | medium | possible_water_omission;generic_no_feature_claim_needs_visual_review | The google map shows a section of a road labeled with the number 60 running vertically. To the right, there is another road labeled Bennettsville Rd, which i... |
| MGEval | `16_3150.jpg` | 0.740 | medium | possible_water_omission;generic_no_feature_claim_needs_visual_review | The google map shows a section of a road labeled "335" running vertically. To the left of the road, there is a marker for "Albertsons Mobile Mechanic." The s... |
| MGEval | `16_3260.jpg` | 0.740 | medium | possible_water_omission;generic_no_feature_claim_needs_visual_review | The google map shows a section of a waterway labeled "Floyds Fork." The waterway runs vertically through the map, with a slight bend and branching towards th... |
| MapTrain | `16_166.jpg` | 0.820 | medium | road_caption_lacks_relation | The google map shows a section of a road with two notable locations. The Marblehead Chowder House NJ is situated near the road, marked with a dining icon. Ne... |
| MapTrain | `16_257.jpg` | 0.820 | medium | road_caption_lacks_relation | The google map shows a section of a road network with a major highway running vertically through the center. The Mercer County Bar Association is marked alon... |
| MapTrain | `16_362.jpg` | 0.820 | medium | road_caption_lacks_relation | The google map shows the location of the Commonwealth National Golf Club. It features a road network with a roundabout near the golf club. The area is predom... |
| MGEval | `16_1008.jpg` | 0.870 | medium | road_caption_lacks_relation | The google map shows a small area with several roads and a labeled location. "Pleasantview Ct" is a curved road connecting to "Chapel Creek Trail," which run... |
| MapTrain | `16_12.jpg` | 0.870 | medium | generic_no_feature_claim_needs_visual_review | The google map shows a water body labeled "Scotts Creek" in blue. Surrounding the creek are areas of light green, indicating land. The creek appears to flow ... |
| MGEval | `16_1284.jpg` | 0.870 | medium | road_caption_lacks_relation | The google map shows a location labeled "Cooper Lane Quarry" with a nearby body of water to the northeast. Another location, "Ernst Concrete," is situated to... |
| MapTrain | `16_136.jpg` | 0.870 | medium | generic_no_feature_claim_needs_visual_review | The google map shows a section of Thompson Mill Road, which runs diagonally from the northeast to the southwest. The surrounding area is shaded in light gree... |
| MapTrain | `16_159.jpg` | 0.870 | medium | generic_no_feature_claim_needs_visual_review | The google map shows a location marked as "Silva Guard Inc." It is situated near a linear feature, possibly a road or a boundary, which runs diagonally acros... |
| MapTrain | `16_168.jpg` | 0.870 | medium | generic_no_feature_claim_needs_visual_review | The google map shows a section of Manalapan Brook, which flows vertically from the top to the bottom of the image. The brook is depicted in blue, indicating ... |
| MGEval | `16_1874.jpg` | 0.870 | medium | water_mention_low_blue_signal | The google map shows a network of roads labeled Doe Creek Dr and Doe Ridge Dr. Doe Creek Dr runs vertically and intersects with Doe Ridge Dr, which runs hori... |
| MGEval | `16_2057.jpg` | 0.870 | medium | road_caption_lacks_relation | The google map shows a small residential area with several roads. Perrin Place and Perrin Circle are connected to Perrin, which curves through the area. Bree... |
| MapTrain | `16_212.jpg` | 0.870 | medium | generic_no_feature_claim_needs_visual_review | The google map shows a section of Penns Park Road, which runs horizontally across the image. The surrounding area is shaded in green, indicating a likely rur... |

## Interpretation

- Proxy issues are candidate mismatches, not ground-truth errors.
- The most useful signals are omissions or unsupported claims for water/green areas and generic no-feature statements on visually rich maps.
- A Q1 submission should replace or validate this layer with VLM/human labels on the same sampled pairs.
