# RQ Evidence Map and Objective Completion Audit

This artifact maps the manuscript's research questions and the active project objective to concrete local evidence. It is a control document, not a claim that all manual submission gates are closed.

## RQ-to-Evidence Map

| RQ | Current strength | Primary evidence | Remaining gap |
|---|---|---|---|
| RQ1 | strong_local_audit | Tables 1, 2, 8; dataset inventory; reproducibility matrix; citation verification; data-source manifest | Final DOI/release and just-in-time source/citation recheck before submission. |
| RQ2 | proxy_vlm_and_clip_screening | Tables 3, 9, 15, 15b, 15c, 21, 22; proxy review; VLM pilot; CLIP screening; judge robustness audit | Human labels or a larger calibrated multi-judge caption panel. |
| RQ3 | deterministic_learned_and_trained_cnn_diagnostics | Tables 4, 5, 5b, 5c, 5d; Figures 4, 6, 9; eight leakage-guarded generated-output baselines; mosaic neighbor-seam stress audit; SCGM official-reproduction readiness audit and run contract | Official or cascade-conditioned diffusion-style reproduction after checkpoint acquisition, runtime instantiation, and output scoring are resolved. |
| RQ4 | executable_benchmark_and_repair | Tables 6, 10, 12, 13, 14, 16, 18, 18b, 19, 20; Figures 5, 7, 8 | Broader matched repair-model suite and human visual-quality labels beyond the calibrated VLM consensus. |
| RQ5 | cross_paradigm_synthesis | Tables 11, 17, 21, 22, 23; cross-paradigm reliability matrix | Final prose compression and possible expert validation of the diagnostic scoring scheme. |

## Objective Completion Audit

| Requirement | Status | Evidence | Remaining gap |
|---|---|---|---|
| Q1-journal manuscript track | incomplete_or_unverified | submission/main_text_compression_plan.md; notes/page_budget_audit.md | Compact manuscript exists with a main/supplement split; final template may still require tightening. |
| Reproducibility audit | evidence_present | Tables 1, 2, 8; DATA_SOURCES; release plan; citation verification | Final DOI/public repository still pending. |
| Caption fidelity experiment | evidence_present | Tables 9, 15, 15b, 15c, 21, 22; proxy/VLM/CLIP outputs | Human labels remain open. |
| Choropleth code-generation QA and repair | evidence_present | Tables 10, 13, 16, 19, 20; run logs; safety scans; screenshot QA | Broader matched repair-model suite remains a strengthening step. |
| SCGM tile continuity/reproduction | evidence_present | Tables 4, 5, 5b, 5c, 5d; Figure 9; SCGM generated outputs; mosaic seam audit; official-reproduction readiness audit and run contract | Official/cascade-conditioned diffusion reproduction still not complete; checkpoint/runtime/output-generation blockers remain explicit after the run contract. |
| Cross-paradigm evaluation | evidence_present | Tables 11, 17, 23; cross-paradigm matrix | Diagnostic scores may benefit from expert validation before final submission. |
| Submission-ready package controls | evidence_present | submission package audit; selected journal checklist; journal style preflight; release preflight; reproduction runbook; abstract pack; blinded manuscript | Journal-native formatting, final DOI, and final non-blinded metadata remain manual. |

## Overall Interpretation

- The automated evidence package is strong and internally guarded.
- The manuscript should not be marked final submission-ready until human validation, final repository/DOI, journal formatting, and just-in-time citation/source checks are handled.
- Open or manual-gap rows: 7.
