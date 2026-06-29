# MapGenerator Image-Text Audit

This audit checks released image-description pairs with file-level and text heuristics. It does not use CLIP/VLM scoring yet.

## Summary

### MapTrain

- pairs: 750
- unique images: 750
- missing images: 0
- average caption length: 50.67 words
- image dimensions: {'1024x1024': 750}
- feature mentions: {'road': 550, 'green_area': 616, 'building_poi': 72, 'direction': 415, 'intersection': 90, 'label': 390, 'water': 363}
- heuristic quality flags: {'generic_no_feature_claim': 79, 'no_direction_or_relation': 315, 'no_named_feature': 29}

### MGEval

- pairs: 100
- unique images: 100
- missing images: 0
- average caption length: 54.11 words
- image dimensions: {'1024x1024': 100}
- feature mentions: {'road': 84, 'water': 60, 'green_area': 89, 'direction': 58, 'label': 62, 'intersection': 15, 'building_poi': 9}
- heuristic quality flags: {'no_direction_or_relation': 38, 'generic_no_feature_claim': 13, 'no_named_feature': 2}

## Highest-Priority Manual Review Candidates

| Split | Image | Flags | Words | Caption |
|---|---|---|---:|---|
| MapTrain | `16_257.jpg` | no_named_feature;no_direction_or_relation | 64 | The google map shows a section of a road network with a major highway running vertically through the center. The Mercer County Bar Association is marked along this highway. To t... |
| MapTrain | `16_54.jpg` | no_direction_or_relation;generic_no_feature_claim | 64 | The google map shows a section of land featuring Neshaminy Creek, which flows in a generally southeast direction. Above the creek, there is a road labeled "Rte 202" running hori... |
| MapTrain | `16_56.jpg` | no_named_feature;no_direction_or_relation | 64 | The google map shows a section of the Philadelphia Cricket Club - Militia Hill Course. It features a light green area representing the golf course, with a blue line indicating a... |
| MapTrain | `16_587.jpg` | no_direction_or_relation;generic_no_feature_claim | 61 | The google map shows a section of Del Puerto Canyon Road, which runs horizontally across the image. The road is depicted in blue, indicating its path through a light green area,... |
| MapTrain | `16_574.jpg` | no_direction_or_relation;generic_no_feature_claim | 60 | The google map shows a section of Del Puerto Creek, which flows in a generally curved path from the northwest to the southeast. The creek is depicted in blue, indicating a water... |
| MapTrain | `16_784.jpg` | no_direction_or_relation;generic_no_feature_claim | 58 | The google map shows a section of Los Gatos Creek, which flows in a generally southwest to northeast direction. The creek is depicted in light blue, indicating a waterway, and i... |
| MapTrain | `16_97.jpg` | no_direction_or_relation;generic_no_feature_claim | 58 | The google map shows a section where Herman Black Road intersects with Sykesville Road. The roads are depicted in light gray against a light green background, indicating a rural... |
| MapTrain | `16_647.jpg` | no_direction_or_relation;generic_no_feature_claim | 56 | The google map shows a location labeled "Silver Creek Self Storage." There are several roads depicted, with one road curving around the area near the label. The map background i... |
| MapTrain | `16_168.jpg` | no_named_feature;generic_no_feature_claim | 55 | The google map shows a section of Manalapan Brook, which flows vertically from the top to the bottom of the image. The brook is depicted in blue, indicating a waterway. The surr... |
| MapTrain | `16_166.jpg` | no_named_feature;no_direction_or_relation | 54 | The google map shows a section of a road with two notable locations. The Marblehead Chowder House NJ is situated near the road, marked with a dining icon. Nearby, the Bryan Anim... |
| MapTrain | `16_216.jpg` | no_direction_or_relation;generic_no_feature_claim | 54 | The google map shows a section of land featuring Cranbury Brook, which flows diagonally from the northwest to the southeast. Dugans Grove Road runs parallel to the brook on the ... |
| MapTrain | `16_159.jpg` | no_direction_or_relation;generic_no_feature_claim | 53 | The google map shows a location marked as "Silva Guard Inc." It is situated near a linear feature, possibly a road or a boundary, which runs diagonally across the map. The backg... |
| MapTrain | `16_714.jpg` | no_named_feature;no_direction_or_relation | 52 | The google map shows the Brushy Peak Regional Preserve, which is highlighted in green. There are two small blue areas within the preserve, indicating bodies of water. A light pu... |
| MapTrain | `16_930.jpg` | no_direction_or_relation;generic_no_feature_claim | 52 | The google map shows an area labeled "Durham Ferry Outdoor Education Center." The map features a network of roads or paths surrounding the center. The background is shaded in gr... |
| MapTrain | `16_385.jpg` | no_direction_or_relation;generic_no_feature_claim | 51 | The google map shows two roads: Hawks Nest Ln and Hollow Rd. Hawks Nest Ln runs horizontally, while Hollow Rd runs vertically and intersects with Hawks Nest Ln. The surrounding ... |
| MapTrain | `16_745.jpg` | no_direction_or_relation;generic_no_feature_claim | 51 | The google map shows a section of a road labeled "The Cross Rd." The road appears to have a winding path, with several curves. The surrounding area is shaded in green, indicatin... |
| MapTrain | `16_764.jpg` | no_direction_or_relation;generic_no_feature_claim | 50 | The google map shows a section of Willow Springs Road, which curves through the area. The road is the primary feature visible, with no additional geographic entities or landmark... |
| MapTrain | `16_634.jpg` | no_named_feature;no_direction_or_relation | 49 | The google map shows a network of roads in a residential area. Key roads include Via Valverde, Via Belmonte, Via Portada, Via Granja, and Via Laguna. The roads are arranged in a... |
| MapTrain | `16_788.jpg` | no_direction_or_relation;generic_no_feature_claim | 49 | The google map shows a body of water labeled "Cottonwood Bay." The bay is depicted in blue, with irregular, jagged edges indicating the shoreline. Surrounding the bay is a beige... |
| MapTrain | `16_58.jpg` | no_named_feature;no_direction_or_relation | 48 | The google map shows a section of land featuring Haystack Brook, which flows horizontally across the upper part of the map. Below the brook, there is a location marked as Utopia... |
| MapTrain | `16_136.jpg` | no_direction_or_relation;generic_no_feature_claim | 47 | The google map shows a section of Thompson Mill Road, which runs diagonally from the northeast to the southwest. The surrounding area is shaded in light green, indicating a like... |
| MapTrain | `16_36.jpg` | no_named_feature;no_direction_or_relation | 47 | The google map shows a section of a water body with a dashed line indicating a boundary between Pennsylvania and New Jersey. The land area is shaded in light green, while the wa... |
| MapTrain | `16_761.jpg` | no_direction_or_relation;generic_no_feature_claim | 47 | The google map shows a section of Herbert Creek, depicted as a blue line running diagonally from the northwest to the southeast. The surrounding area is shaded in light green, i... |
| MapTrain | `16_373.jpg` | no_direction_or_relation;generic_no_feature_claim | 46 | The google map shows a section of Adelphia-Farmingdale Road, which runs horizontally across the image. There is a marked location for "Our House Restaurant and Banquet Facility"... |
| MapTrain | `16_652.jpg` | no_direction_or_relation;generic_no_feature_claim | 46 | The google map shows a section of San Antonio Valley Road, which runs vertically through the center of the image. The surrounding area is shaded in green, indicating a natural o... |
| MapTrain | `16_683.jpg` | no_direction_or_relation;generic_no_feature_claim | 46 | The google map shows a location labeled "WM - Guadalupe Rubbish Disposal Facility." It is situated among several intersecting roads. The surrounding area is shaded in green, ind... |
| MapTrain | `16_701.jpg` | no_direction_or_relation;generic_no_feature_claim | 46 | The google map shows an area labeled "Middle Ridge." It features a dashed line indicating a boundary or path running through the region. The map background is shaded in light gr... |
| MapTrain | `16_840.jpg` | no_direction_or_relation;generic_no_feature_claim | 46 | The google map shows a location labeled "Tuscan House Vineyards" with an icon indicating a wine-related establishment. It is situated near a road named "Soma Way." The surroundi... |
| MapTrain | `16_970.jpg` | no_direction_or_relation;generic_no_feature_claim | 46 | The google map shows a section of Corral Hollow Road, which runs in a generally northeast-southwest direction. Adjacent to the road is a small blue area, indicating a body of wa... |
| MapTrain | `16_601.jpg` | no_named_feature;no_direction_or_relation | 45 | The google map shows a section of the Robert T. Monagan Freeway, which runs horizontally across the image. There is a thin, light blue line intersecting the freeway, possibly in... |

## Interpretation

- The local release has 750 MapTrain descriptions and 100 MGEval descriptions.
- The current audit is a reproducibility/data-quality layer; model-based alignment scoring should be added next.
- Captions are generally descriptive, but generic claims such as no additional geographic features need visual verification.
- Named-feature and relation heuristics identify candidates for VLM/manual review, not definitive errors.
