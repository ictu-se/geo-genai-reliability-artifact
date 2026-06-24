# Live Generated-Code Evaluation

Updated: 2026-06-19

## Purpose

This experiment supplements the V3 stress benchmark with actual generated-code candidate scripts. It is still controlled and small, but it runs real Python/GeoPandas/Rasterio code over the GeoGuard Los Angeles County datasets and then scores the generated artifacts.

## Files

- Runner: `experiments/04_geo_faithfulness_evaluator/scripts/run_live_candidate.py`
- Scorer: `experiments/04_geo_faithfulness_evaluator/scripts/score_live_candidate_runs.py`
- Candidates:
  - `experiments/04_geo_faithfulness_evaluator/inputs/live_candidates/basic_gis_copilot_generated.py`
  - `experiments/04_geo_faithfulness_evaluator/inputs/live_candidates/planner_reflector_generated.py`
  - `experiments/04_geo_faithfulness_evaluator/inputs/live_candidates/geoguard_copilot_generated.py`
- Output:
  - `experiments/04_geo_faithfulness_evaluator/outputs/live_llm_eval/live_summary.csv`
  - `experiments/04_geo_faithfulness_evaluator/outputs/live_llm_eval/live_task_scores.csv`

## Commands

```bash
python3 experiments/04_geo_faithfulness_evaluator/scripts/run_live_candidate.py \
  experiments/04_geo_faithfulness_evaluator/inputs/live_candidates/basic_gis_copilot_generated.py \
  --system basic_gis_copilot

python3 experiments/04_geo_faithfulness_evaluator/scripts/run_live_candidate.py \
  experiments/04_geo_faithfulness_evaluator/inputs/live_candidates/planner_reflector_generated.py \
  --system planner_reflector

python3 experiments/04_geo_faithfulness_evaluator/scripts/run_live_candidate.py \
  experiments/04_geo_faithfulness_evaluator/inputs/live_candidates/geoguard_copilot_generated.py \
  --system geoguard_copilot

python3 experiments/04_geo_faithfulness_evaluator/scripts/score_live_candidate_runs.py
```

## Summary

| System | ES | SC | PHR | CRSC | TV | SCH | MCS |
|---|---:|---:|---:|---:|---:|---:|---:|
| Basic GIS Copilot | 1.0000 | 0.9583 | 0.1750 | 0.6333 | 1.0000 | 0.8333 | 2.4 |
| Planner-Reflector | 1.0000 | 0.9583 | 0.0417 | 1.0000 | 1.0000 | 0.8333 | 3.0 |
| GeoGuard-Copilot | 1.0000 | 1.0000 | 0.0000 | 1.0000 | 1.0000 | 1.0000 | 4.4 |

## Interpretation

- All candidates executed and produced six artifacts.
- Basic GIS Copilot produced runnable outputs but used geographic CRS for several analytical vector outputs, reducing `CRSC` and increasing `PHR`.
- Basic GIS Copilot also lost the required `name` field in R001 after overlay, reducing `SCH`.
- Planner-Reflector fixed CRS handling but still lost the required R001 field, so `SCH` stayed below GeoGuard.
- GeoGuard-Copilot added CRS checks, schema restoration, geometry repair, and map-quality features, producing the best scores.

## Caveat

These candidates were generated in this workspace as representative generated-code candidates. A stronger paper version should repeat this with multiple external LLMs and multiple prompt seeds.

