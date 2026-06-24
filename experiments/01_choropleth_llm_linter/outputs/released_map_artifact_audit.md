# Released Choropleth Artifact Audit

This audit checks the static and interactive map artifacts released with the ChatGPT choropleth materials.

## Summary

- total artifacts: 43
- artifact types: {'png': 33, 'html': 10}
- prompt patterns: {'advanced': 20, 'arcgis_reference': 3, 'basic': 20}
- map types: {'choropleth': 10, 'dot_density': 10, 'graduated_symbol': 10, 'reference_layout': 3, 'interactive_choropleth': 10}
- QA flags: {}

## Flagged Artifacts

| Artifact | Prompt | Type | Flags |
|---|---|---|---|
| _none_ | | | |

## Interpretation

- Static PNGs and interactive HTML files are present for both basic and advanced prompt patterns.
- This file-level audit is intentionally conservative: it detects missing/empty/blank artifacts and coarse HTML structure only.
- The next useful step is screenshot-based cartographic QA: title, legend, color ramp, classification, readable labels, and source note.
