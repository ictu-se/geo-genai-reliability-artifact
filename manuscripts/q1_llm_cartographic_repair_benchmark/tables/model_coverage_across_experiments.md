# Model and Evaluator Coverage Across Experiments

| Role | Count | Models or systems | Manuscript use |
|---|---:|---|---|
| First-pass code generators | 2 | deepseek-coder:6.7b; qwen2.5-coder:7b | Source failures for the repair benchmark |
| Matched repair models | 4 | deepseek-coder:6.7b; qwen2.5-coder:7b; qwen2.5-coder:14b; qwen2.5-coder:32b | Main 40-case matched repair comparison |
| Workflow-spec LLMs | 4 | qwen2.5-coder:3b; qwen2.5-coder:7b; qwen2.5-coder:32b; deepseek-coder:6.7b | Supporting evidence on geospatial planning and model scale |
| VLM judges | 6 | granite3.2-vision:latest; qwen2.5vl:3b; llava-llama3:8b; llama3.2-vision:11b; minicpm-v:latest; qwen3-vl:4b | Visual-review sensitivity and evaluator instability |
| Embedding baseline | 1 | openai/clip-vit-base-patch32 | Supporting visual-text alignment baseline |
| Live systems | 3 | basic_gis_copilot; geoguard_copilot; planner_reflector | Context for deployed workflow behavior |
