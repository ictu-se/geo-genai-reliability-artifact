# Human Validation Panel Protocol

These panels are designed to close the remaining evaluator-validity gate without changing the main experimental pipeline.

## Files

- `mapgenerator_caption_human_panel.csv`: 20 paired image-caption cases.
- `choropleth_cartographic_human_panel.csv`: 18 screenshot-passing choropleth artifacts.
- `mapgenerator_caption_blind_panel.csv`: blind annotator-facing caption panel.
- `choropleth_cartographic_blind_panel.csv`: blind annotator-facing cartographic panel.
- `human_validation_rubric.json`: machine-readable labels and adjudication rules.

## MapGenerator Caption Panel

Annotators should open `image_path`, read `caption`, and fill the `human_*` columns only. Use `mapgenerator_caption_blind_panel.csv` for blind annotation; use the full panel only for later adjudication.

Recommended labels:

- `human_visible_water`, `human_visible_roads`, `human_visible_green_area`, `human_visible_named_label`: `yes`, `no`, or `unclear`.
- `human_caption_support`: `supported`, `partly_supported`, `unsupported`, or `unclear`.
- `human_unsupported_claims` and `human_omissions`: short free text.

## Choropleth Cartographic Panel

Annotators should open `review_image_path` and fill the `human_*` columns only. Use `choropleth_cartographic_blind_panel.csv` for blind annotation; use the full panel only for later adjudication.

Recommended labels:

- Binary visual components: `yes`, `no`, or `unclear`.
- `human_cartographic_quality`: numeric score from 0.0 to 1.0.
- `human_verdict`: `usable`, `usable_with_minor_issues`, `weak`, `failed`, or `unclear`.
- `human_main_issue`: one concise reason for the verdict.

## Adjudication Rule

For Q1-strengthened claims, report human agreement separately from VLM agreement. Treat a case as supported only when at least two independent human annotations agree or a designated expert adjudicates the disagreement.
