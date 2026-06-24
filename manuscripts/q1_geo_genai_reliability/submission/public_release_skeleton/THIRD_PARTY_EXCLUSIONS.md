# Third-Party Exclusions and Source-Linking Rules

This skeleton does not redistribute raw third-party data, upstream repositories, or model weights. It records the public-release action that should be taken for each artifact family before a DOI archive is created.

| Artifact family | Terms | Public-release action |
|---|---|---|
| project_created_code | author-controlled | Recommended action: add a top-level LICENSE for project-created code and note that third-party data are excluded/source-linked. |
| project_created_manuscript_evidence | author-controlled-with-third-party-context | Recommended action: license derived metadata/tables separately from raw third-party data; use source links for reconstructing restricted inputs. |
| SCGM | CC-BY-4.0 | Retain upstream attribution; do not redistribute bulky raw tiles unless final license review confirms scope. |
| MapGenerator | research-preview-noncommercial-readme | Exclude raw images/captions from open DOI package; release only derived audit summaries and reconstruction instructions. |
| Materials-for-Creating-maps-by-Artificial-Intelligence | CC0-1.0 | Do not assume all nested data are rights-cleared; include attribution/source note even when CC0 applies. |
| generative-ai-mapmaking | no-license-file-readme-only | Exclude raw upstream content from public package; retain URL/commit/access notes. |
| local_llm_vlm_outputs | model-output-policy-dependent | Preserve prompts, model names, timestamps, and safety scans; recheck local model licenses before public upload. |
| model_weights_and_checkpoints | not_redistributed | Do not upload weights/checkpoints unless the license explicitly permits redistribution. |
| double_anonymous_review_package | review-only | Upload blinded files to review portal; add non-blinded authors/DOI/license only after review-route policy is confirmed. |

## Non-Redistribution Rule

If a file is raw upstream content, a cloned upstream repository, a checkpoint, or a local model cache, leave it out of the public package unless redistribution rights are explicitly confirmed. Provide source URL, commit or version, access date, expected local layout, and rebuild scripts instead.
