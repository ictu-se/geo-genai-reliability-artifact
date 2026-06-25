# Evidence Map

This file records the current evidence available for the LLM cartographic repair benchmark. It should be updated whenever the experiment suite is expanded.

## Existing Evidence

| Claim | Current evidence | Source artifact | Status |
|---|---|---|---|
| First-pass local code LLMs often fail to produce complete cartographic artifacts. | qwen2.5-coder:7b and deepseek-coder:6.7b produced no complete valid artifacts in the expanded choropleth benchmark. | `experiments/05_choropleth_reliability_benchmark/outputs/scores/expanded_choropleth_condition_summary.csv` | usable |
| Execution success alone is insufficient. | Rendered artifact and screenshot QA distinguish existing files from nonblank/renderable/usable outputs. | `rendered_artifact_qa_summary.csv`, `screenshot_level_qa_summary.csv` | usable |
| Validator-gated repair can recover many failures. | qwen2.5-coder:32b iterative repair completed 25/40 incomplete cases. | `iterative_validator_repair_summary_qwen2.5-coder_32b.json` | usable |
| Repair capacity differs strongly across models under the same matched case set. | Full 40-case matched suite: deepseek-coder:6.7b completed 2/40, qwen2.5-coder:7b completed 6/40, qwen2.5-coder:14b completed 9/40, and qwen2.5-coder:32b completed 25/40. | `iterative_validator_repair_summary_*.json`; `tables/full_matched_repair_summary.md` | usable |
| GIS/cartographic failures are domain-specific. | Dominant error classes include missing imports, geometry/CRS, schema hallucination, hardcoded paths, wrong file names, deprecated APIs, and other runtime errors. | `expanded_choropleth_error_taxonomy_summary.csv` | usable |
| Visual QA is needed after code repair. | Screenshot QA currently shows repair outputs can exist while only a subset pass visual QA. | `screenshot_level_qa_summary.csv` | usable |
| Content-level visual QA changes the interpretation of completion. | In the full matched suite, qwen2.5-coder:32b completes 25/40 cases, 23 of which pass content QA; qwen2.5-coder:14b completes 9/40 but only 5 completed cases pass content QA; qwen2.5-coder:7b completes 6/40 but only 4 completed cases pass content QA. | `iterative_repair_screenshot_qa_summary.csv`; `tables/full_matched_repair_summary_auto.md`; `figures/iterative_artifact_qa_ladder.png` | usable |
| Residual failures differ by model family. | deepseek-coder:6.7b is dominated by unsafe syntax errors, while qwen models mostly leave execution, static PNG, diagnostic JSON, and interactive HTML contract failures. | `tables/residual_failed_checks_summary.md`; `figures/residual_failed_checks_heatmap.png` | usable |
| Repairability is task-family dependent. | qwen2.5-coder:32b performs best on time-series, CRS/geometry, interactive, static-basic, and cartographic-design families, while classification and multi-output cases remain harder. | `tables/repair_completion_by_family.md`; `figures/repair_completion_by_family_heatmap.png` | usable |
| VLM visual review adds a cartographic-completeness stress test. | A 24-artifact two-judge VLM pilot shows strong evaluator sensitivity: granite3.2-vision reports mostly usable-with-minor-issues verdicts, while qwen2.5vl:3b labels most artifacts weak or failed. Both repeatedly flag missing titles, legends/colorbars, or weak thematic completeness. | `tables/iterative_repair_vlm_judge_comparison.md` | pilot |

## Current Headline Numbers

| Metric | Value | Notes |
|---|---:|---|
| First-pass complete artifacts | 0 | Across qwen2.5-coder:7b and deepseek-coder:6.7b expanded benchmark conditions currently summarized for manuscript track. |
| qwen2.5-coder:32b repair completed cases | 25/40 | Full matched iterative validator-gated sweep. |
| qwen2.5-coder:14b repair completed cases | 9/40 | Full matched iterative validator-gated sweep. |
| qwen2.5-coder:7b repair completed cases | 6/40 | Full matched iterative validator-gated sweep. |
| deepseek-coder:6.7b repair completed cases | 2/40 | Full matched iterative validator-gated sweep; many attempts were unsafe under the static scanner. |
| Error taxonomy rows | 7 classes | Missing import, geometry/CRS, schema hallucination, hardcoded path, wrong file name, deprecated API, other. |

## Evidence Gaps

| Gap | Why it matters | Proposed fix |
|---|---|---|
| Human cartographic labels are limited. | Content QA is deterministic and useful, but not a substitute for expert cartographic judgment. | Build a small blind panel over content-passing and content-failing repaired outputs. |
| Human cartographic labels are limited. | Screenshot QA checks rendering, but not all design-quality claims. | Use existing human validation packet or create a smaller final blind panel for repaired outputs. |
| Attempt-cost analysis is not summarized. | Repairability includes how many iterations are needed. | Build table of completion by attempt number and residual failures by final attempt. |
| Error transitions are not yet summarized. | The paper can be stronger if it shows which error classes repair well or persist. | Compare failed checks before and after repair for each case. |
| Figure assets are not yet isolated. | The second paper needs its own visual identity and figures. | Create `figures/` outputs from benchmark ledgers rather than borrowing final figures from paper 1. |
