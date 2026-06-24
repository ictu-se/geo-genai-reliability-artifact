# Reviewer Prebuttal Audit

This audit anticipates likely Q1-reviewer objections and maps each one to current evidence, a response posture, and a non-overclaim guard.

## Summary

- Reviewer risks tracked: 8
- Use: tighten discussion, limitations, cover letter, and response-to-reviewer drafts.

## Risk Ledger

| Risk | Likely objection | Current evidence | Prebuttal response | Before-submission action |
|---|---|---|---|---|
| RISK-01 | The manuscript uses VLMs and CLIP-style scores; are these being treated as ground truth? | Tables 15, 15b, 15c, 18, 18b, 21, 22, 24; human validation panels and execution plan. | Frame VLM/CLIP layers as screening, evaluator-robustness, and prioritization evidence; preserve human-label gate as open. | Collect human labels or keep all caption/visual-quality claims explicitly scoped to calibrated VLM/proxy evidence. |
| RISK-02 | SCGM baselines do not reproduce the official diffusion/cascade model. | Tables 4, 5, 5b, 5c, 5d; SCGM official-reproduction readiness audit and run contract; generated-output baselines. | State that current outputs are leakage-guarded diagnostics and lower-bound stress tests, not official SCGM reproduction. | Run the contracted official/cascade-conditioned inference if checkpoints and runtime become available; otherwise retain explicit blocker language. |
| RISK-03 | Local LLM/VLM models may not represent frontier systems. | Tables 10, 13, 18, 18b, 19, 20, 22, 25; run logs and safety scans. | Position the benchmark as a reproducible artifact-chain stress test, not a universal leaderboard of all model families. | Keep model names, local environment, and non-universality caveat visible in methods and limitations. |
| RISK-04 | The cross-paradigm reliability matrix may look subjective. | Tables 11, 17, 23; RQ evidence map; claim-to-evidence crosswalk. | Define 0-3 scores as diagnostic evidence summaries, not universal quality scores; preserve dimension-level evidence. | Add expert validation only if available; otherwise avoid ranking language and keep score construction transparent. |
| RISK-05 | Validator/reference repair is an oracle; is the paper counting it as LLM success? | Tables 12, 16, 19, 20, 25; validator/reference artifacts; screenshot QA. | Report validator/reference as a deterministic positive control and upper-bound artifact contract, separate from LLM repairs. | Keep the oracle/positive-control wording in results, discussion, limitations, and claim crosswalk. |
| RISK-06 | The paper has many artifacts and tables; can reviewers see the logical spine? | Compact manuscript, main/supplement split, page-budget audit, claim crosswalk, RQ evidence map. | Use the artifact-chain framework and five RQs as the spine; move exhaustive tables to supplement. | Keep the compact manuscript focused and use crosswalk/prebuttal artifacts for cover-letter framing. |
| RISK-07 | Are the data and code actually releasable? | Release preflight, release-license audit, DATA_SOURCES, reproducibility manifest, reproduction runbook. | Release project-created scripts and derived summaries; source-link or restrict raw third-party data and model weights. | Choose final license, create repository/DOI, and update non-blinded metadata before portal upload. |
| RISK-08 | Is the selected venue/Q1 route actually current? | Journal target recheck dated 2026-06-24; journal style preflight; Q1 gate tracker. | Treat submission route and quartile status as live external checks, not static manuscript facts. | Reopen official journal/special-issue pages and quartile database immediately before upload. |

## Use Rule

The `overclaim_guard` column in the CSV should be checked before strengthening any abstract, discussion, limitation, cover-letter, or response-to-reviewer language.
