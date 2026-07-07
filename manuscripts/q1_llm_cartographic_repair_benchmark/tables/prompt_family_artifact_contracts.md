# Prompt Families and Artifact Contracts

| Prompt family | Main stressor | Required artifact contract | Typical failure signal |
|---|---|---|---|
| static_basic | Single thematic choropleth rendering | Static PNG, diagnostics JSON, known input files | Missing static PNG, blank map, wrong thematic field |
| attribute_join | District geometry joined to wildfire attributes | Static PNG, diagnostics JSON, correct join field use | Schema hallucination, wrong merge key, empty layer |
| classification | Thematic classification or color encoding | Static PNG, diagnostics JSON, class/color implementation | Unclassified map, weak legend, misleading color scale |
| crs_geometry | Missing CRS metadata and invalid geometry repair | Static PNG, diagnostics JSON, CRS and geometry repair evidence | CRS assumption omitted, invalid geometry not repaired |
| interactive | Web map with tooltips or popups | Interactive HTML, diagnostics JSON, renderable browser screenshot | HTML not written, no map layer, missing tooltips |
| multi_output | Multiple requested outputs in one run | Static PNG, interactive HTML, diagnostics JSON and/or time-series PNG | One artifact written while others are omitted |
| cartographic_design | Title, legend/colorbar, layout, readability, source/design cues | Static PNG plus design-completeness evidence | Missing title, no legend, unreadable map layout |
| time_series | Non-map analytical figure tied to wildfire records | Time-series PNG, diagnostics JSON, expected temporal field use | Figure missing, wrong year field, weak temporal plot |
