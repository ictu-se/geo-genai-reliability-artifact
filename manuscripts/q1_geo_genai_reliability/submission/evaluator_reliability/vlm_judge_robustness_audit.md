# VLM Judge Robustness Audit

This audit checks whether local vision-language models obeyed the JSON review schema well enough to serve as evaluators. It is an evaluator-validity artifact, not a substitute for human labels.

## Summary

### Choropleth cartographic quality

- agreement-panel models: granite3.2-vision:latest, qwen2.5vl:3b
- partial candidate models: none
- failed candidate models: llava-llama3:8b

### MapGenerator caption fidelity

- agreement-panel models: granite3.2-vision:latest, qwen2.5vl:3b
- partial candidate models: llava-llama3:8b
- failed candidate models: llama3.2-vision:11b, minicpm-v:latest, qwen3-vl:4b

## Model-Level Results

| Task | Model | Reviewed | Usable | Errors | Usable rate pct | Role |
|---|---|---:|---:|---:|---:|---|
| Choropleth cartographic quality | `granite3.2-vision:latest` | 18 | 18 | 0 | 100.0 | agreement_panel |
| Choropleth cartographic quality | `qwen2.5vl:3b` | 18 | 18 | 0 | 100.0 | agreement_panel |
| Choropleth cartographic quality | `llava-llama3:8b` | 18 | 5 | 13 | 27.8 | failed_candidate |
| MapGenerator caption fidelity | `granite3.2-vision:latest` | 20 | 20 | 0 | 100.0 | agreement_panel |
| MapGenerator caption fidelity | `qwen2.5vl:3b` | 20 | 20 | 0 | 100.0 | agreement_panel |
| MapGenerator caption fidelity | `llava-llama3:8b` | 20 | 16 | 4 | 80.0 | candidate_partial |
| MapGenerator caption fidelity | `llama3.2-vision:11b` | 20 | 0 | 20 | 0.0 | failed_candidate |
| MapGenerator caption fidelity | `minicpm-v:latest` | 20 | 1 | 19 | 5.0 | failed_candidate |
| MapGenerator caption fidelity | `qwen3-vl:4b` | 10 | 1 | 9 | 10.0 | failed_candidate |

## Interpretation

- The current agreement tables should remain based on Granite and Qwen because both produced complete schema-conformant reviews for the paired panels.
- Additional local VLMs are useful as stress tests, but schema adherence is itself a reliability variable: weak JSON compliance can create evaluator failure even when an image model can describe maps conversationally.
- This supports the manuscript's conservative use of VLMs as pilot evaluators and adjudication queues rather than ground-truth cartographic labels.
