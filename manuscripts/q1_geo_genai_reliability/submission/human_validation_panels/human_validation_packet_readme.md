# Human Validation Packet

This packet is prepared for collecting real human labels. It deliberately contains blank annotation fields and should not be cited as completed human evidence until completed annotator files are summarized.

## Packet Contents

- `mapgenerator_caption_blind_panel.csv`: blind caption-fidelity form.
- `choropleth_cartographic_blind_panel.csv`: blind cartographic-quality form.
- `human_validation_priority_queue.csv`: merged priority queue across both tasks.
- `human_validation_assignment_sheet.csv`: two-annotator assignment sheet with batch IDs.
- `annotator_packets/`: ready-to-fill per-annotator CSV packets using the exact return filenames expected by the summarizer.
- `human_validation_agreement_template.csv`: blank merge/adjudication template for completed labels.
- `human_validation_acceptance_criteria.csv`: thresholds for when human labels may strengthen manuscript claims.
- `human_validation_file_contract.csv`: annotator-facing editable/locked column contract.
- `human_validation_execution_plan.md`: step-by-step label collection, summary, and manuscript-update plan.
- `human_validation_rubric.json`: label definitions and adjudication rules.
- `mapgenerator_caption_gallery.html`: blind visual gallery for caption annotators.
- `choropleth_cartographic_gallery.html`: blind visual gallery for cartographic-quality annotators.
- `human_validation_gallery_index.csv`: machine-readable gallery/artifact index.

## Coverage

- MapGenerator caption cases: 20.
- Choropleth cartographic cases: 18.
- Total annotation assignments at two independent annotators per item: 76.
- Batches: B01, B02, B03, B04.
- Urgent VLM-disagreement cases: 22.

## Recommended Workflow

1. Give annotator A and annotator B separate copies of the relevant blind panel CSVs.
2. Prefer the files in `annotator_packets/`, which are already split by annotator slot and task without exposing VLM/proxy labels.
3. After both annotators return completed files, run `summarize_human_validation.py` with the completed CSV paths.
4. Use `human_validation_agreement_template.csv` to record disagreements and expert adjudication.
5. Only then revise manuscript claims from `human-label gate pending` to human-supported evidence.

## Guardrails

- Do not show annotators the full panel files, VLM verdicts, proxy scores, or priority labels.
- Do not treat agreement between local VLMs as a substitute for human labels.
- Keep the raw completed annotator files outside the blinded review manuscript unless the journal explicitly asks for them.
