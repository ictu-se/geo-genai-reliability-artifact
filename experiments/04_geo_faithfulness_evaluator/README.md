# 04 Geo-Faithfulness Evaluator

This track builds a shared evaluator for generated maps across text-to-map, remote-sensing-to-map, and code-generated map workflows.

Data source:

- outputs from `../01_choropleth_llm_linter`
- outputs from `../02_mapgenerator_image_text_audit`
- outputs from `../03_scgm_subset_reproduction`

Initial tasks:

1. Define a common cartographic quality rubric.
2. Implement rule-based checks where GIS structure is available.
3. Implement image-based checks where only rendered maps are available.
4. Compare metric scores with human or VLM review.
5. Summarize which generation paradigm is reliable for which kind of map task.

