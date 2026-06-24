# Human Validation Execution Plan

This plan converts the remaining human-label gate into an executable validation workflow. It does not claim that labels have been collected; it specifies how completed labels will be accepted, summarized, and allowed to change manuscript claims.

## Scope

- MapGenerator caption-fidelity cases: 20.
- Choropleth cartographic-quality cases: 18.
- Total two-annotator assignments: 76.
- Batch IDs: B01, B02, B03, B04.
- Urgent MapGenerator VLM-disagreement cases: 17.
- Urgent choropleth VLM-disagreement cases: 5.

## Execution Steps

1. Freeze the blind panel CSV files and keep the full panel files hidden from annotators.
2. Assign every `panel_id` to annotator slots A and B using `human_validation_assignment_sheet.csv`.
3. Ask annotators to edit only the `human_*` columns listed in `human_validation_file_contract.csv`.
4. Run `summarize_human_validation.py --mapgenerator-labels ... --choropleth-labels ...` on completed annotator files.
5. Merge disagreements into `human_validation_agreement_template.csv` and record expert adjudication only where needed.
6. Revise the manuscript claim strength only for items satisfying `human_validation_acceptance_criteria.csv`.

## Reporting Rules

- Report human labels as a separate evidence layer from VLM verdicts, CLIP/SigLIP-style scores, and deterministic proxies.
- Preserve the original VLM disagreement counts even after human adjudication, because evaluator instability is part of the finding.
- Use human labels to strengthen RQ2 and choropleth visual-quality claims only when the corresponding acceptance criteria are met.
- If completed labels remain sparse, report them as a pilot validation layer and keep the current limitations language.

## Manuscript Update Trigger

The manuscript can replace `human-label gate pending` caveats with human-supported claims only after the label summary reports nonzero completed annotations for both tasks and the agreement/adjudication template records final labels for all urgent disagreement cases.
