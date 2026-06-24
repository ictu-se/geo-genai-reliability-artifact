# VLM Agreement and Calibration Notes

Generated on 2026-06-24 from existing local VLM review outputs. This is a pilot agreement analysis, not a substitute for expert cartographic or human caption labels.

## MapGenerator Caption Fidelity

Source tables:

- `tables/table_15_mapgenerator_vlm_caption_review.csv`
- `tables/table_15b_mapgenerator_vlm_agreement.csv`

Two complete local VLM runs, `granite3.2-vision:latest` and `qwen2.5vl:3b`, reviewed the same 20 proxy-selected MapGenerator image-caption pairs.

Key results:

- Paired reviewed items: 20.
- Exact verdict agreement: 3/20.
- Supported-versus-below agreement: 3/20.
- Both models marked the caption as fully supported in 2 cases.
- Mean alignment score: Granite 0.972; qwen2.5vl 0.885.
- Qwen gave a lower alignment score in 15/20 cases.
- Feature-level agreement across water, roads, green area, and named-label visibility: 73/79.

Interpretation:

The two VLMs often agree about low-level visible features but disagree sharply on semantic caption support. Granite is permissive, while qwen2.5vl is more critical and frequently marks captions as partly supported. This supports the manuscript's claim that single-VLM caption review is feasible as a screening layer but not reliable enough to serve as ground truth without calibration, adjudication, or human labels.

## Choropleth Cartographic Quality

Source tables:

- `tables/table_18_choropleth_vlm_cartographic_review.csv`
- `tables/table_18b_choropleth_vlm_agreement.csv`

Two complete local VLM runs reviewed the same 18 screenshot-passing choropleth artifacts: 3 deterministic reference artifacts, 5 LLM-repair artifacts, and 10 validator/reference artifacts.

Key results:

- Paired reviewed artifacts: 18.
- Exact verdict agreement: 13/18.
- Usable-versus-below agreement: 14/18.
- Both models marked 12 artifacts usable.
- Mean quality score: Granite 0.616; qwen2.5vl 0.294.
- Qwen gave a lower quality score in 15/18 artifacts.
- Component agreement across content visibility, title, legend/colorbar, readability, layout, and choropleth appearance: 80/108.

Interpretation:

The two VLMs agree more strongly on coarse usable/failed verdicts than on numeric quality scores or component flags. The agreement is strongest for validator/reference artifacts: 10/10 exact verdict agreement and 10/10 usable-versus-below agreement. The repair artifacts remain the most contested group, with only 1/5 exact verdict agreement and 0 artifacts judged usable by both models. This supports using the VLM layer as evaluator-sensitivity evidence: it strengthens the conclusion that validator/reference outputs are consistently more usable than LLM-repair outputs, while also showing that numeric VLM quality scores should not be treated as calibrated expert scores.

## Manuscript Implication

The agreement pilot closes part of the evaluator-validity gap by measuring how two independent local VLMs behave on identical samples. It does not close the final Q1 validation gate. Before submission, the strongest next move is one of:

- add a small human adjudication set for the same paired items;
- add a third stable VLM with a successfully parsed complete run;
- add CLIP/SigLIP or another image-text embedding score for MapGenerator captions;
- convert VLM verdicts into an explicit adjudication rule, such as both-model agreement, majority vote, or expert override.

The local package now includes prepared annotation panels and blind exports under `submission/human_validation_panels/`. These files make the human-label path operational, but they do not close the validation gate until independent labels are actually collected and summarized.

An optional CLIP/SigLIP-style embedding scorer now exists at `experiments/02_mapgenerator_image_text_audit/scripts/run_clip_siglip_caption_scoring.py`. In the current environment it records `dependency_or_model_missing` because PyTorch/Transformers are not installed, so embedding scores remain a pending validation layer rather than evidence.
