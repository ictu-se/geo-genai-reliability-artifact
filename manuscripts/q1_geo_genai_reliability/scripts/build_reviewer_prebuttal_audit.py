#!/usr/bin/env python3
"""Build a reviewer-risk prebuttal audit for the Q1 manuscript track.

This artifact anticipates likely Q1-reviewer objections and maps them to
existing evidence, claim boundaries, and remaining gates. It is a control file
for tightening prose, cover letters, and eventual response-to-reviewer drafts.
"""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MS_DIR = ROOT / "manuscripts/q1_geo_genai_reliability"
OUT_DIR = MS_DIR / "submission/reviewer_prebuttal_audit"
CSV_OUT = OUT_DIR / "reviewer_prebuttal_audit.csv"
MD_OUT = OUT_DIR / "reviewer_prebuttal_audit.md"


def rows() -> list[dict[str, str]]:
    return [
        {
            "risk_id": "RISK-01",
            "likely_reviewer_objection": "The manuscript uses VLMs and CLIP-style scores; are these being treated as ground truth?",
            "affected_claim": "MapGenerator caption fidelity and choropleth visual-quality interpretation.",
            "current_evidence": "Tables 15, 15b, 15c, 18, 18b, 21, 22, 24; human validation panels and execution plan.",
            "prebuttal_response": "Frame VLM/CLIP layers as screening, evaluator-robustness, and prioritization evidence; preserve human-label gate as open.",
            "before_submission_action": "Collect human labels or keep all caption/visual-quality claims explicitly scoped to calibrated VLM/proxy evidence.",
            "overclaim_guard": "Never write that VLM labels are expert cartographic truth.",
        },
        {
            "risk_id": "RISK-02",
            "likely_reviewer_objection": "SCGM baselines do not reproduce the official diffusion/cascade model.",
            "affected_claim": "RQ3 remote-sensing-to-map reproduction and spatial-faithfulness diagnostics.",
            "current_evidence": "Tables 4, 5, 5b, 5c, 5d; SCGM official-reproduction readiness audit and run contract; generated-output baselines.",
            "prebuttal_response": "State that current outputs are leakage-guarded diagnostics and lower-bound stress tests, not official SCGM reproduction.",
            "before_submission_action": "Run the contracted official/cascade-conditioned inference if checkpoints and runtime become available; otherwise retain explicit blocker language.",
            "overclaim_guard": "Do not call retrieval, ridge, forest, patch, MLP, or tiny-CNN outputs official SCGM reproduction.",
        },
        {
            "risk_id": "RISK-03",
            "likely_reviewer_objection": "Local LLM/VLM models may not represent frontier systems.",
            "affected_claim": "Choropleth generation/repair and evaluator-robustness results.",
            "current_evidence": "Tables 10, 13, 18, 18b, 19, 20, 22, 25; run logs and safety scans.",
            "prebuttal_response": "Position the benchmark as a reproducible artifact-chain stress test, not a universal leaderboard of all model families.",
            "before_submission_action": "Keep model names, local environment, and non-universality caveat visible in methods and limitations.",
            "overclaim_guard": "Do not generalize local model failure rates to all proprietary/frontier models.",
        },
        {
            "risk_id": "RISK-04",
            "likely_reviewer_objection": "The cross-paradigm reliability matrix may look subjective.",
            "affected_claim": "RQ5 cross-paradigm synthesis and dimension-level scores.",
            "current_evidence": "Tables 11, 17, 23; RQ evidence map; claim-to-evidence crosswalk.",
            "prebuttal_response": "Define 0-3 scores as diagnostic evidence summaries, not universal quality scores; preserve dimension-level evidence.",
            "before_submission_action": "Add expert validation only if available; otherwise avoid ranking language and keep score construction transparent.",
            "overclaim_guard": "Do not present cross-paradigm means as a definitive model or paradigm ranking.",
        },
        {
            "risk_id": "RISK-05",
            "likely_reviewer_objection": "Validator/reference repair is an oracle; is the paper counting it as LLM success?",
            "affected_claim": "Choropleth repair success and positive controls.",
            "current_evidence": "Tables 12, 16, 19, 20, 25; validator/reference artifacts; screenshot QA.",
            "prebuttal_response": "Report validator/reference as a deterministic positive control and upper-bound artifact contract, separate from LLM repairs.",
            "before_submission_action": "Keep the oracle/positive-control wording in results, discussion, limitations, and claim crosswalk.",
            "overclaim_guard": "Never merge validator/reference completions into LLM completion counts.",
        },
        {
            "risk_id": "RISK-06",
            "likely_reviewer_objection": "The paper has many artifacts and tables; can reviewers see the logical spine?",
            "affected_claim": "Overall Q1 contribution and readability of the compact manuscript.",
            "current_evidence": "Compact manuscript, main/supplement split, page-budget audit, claim crosswalk, RQ evidence map.",
            "prebuttal_response": "Use the artifact-chain framework and five RQs as the spine; move exhaustive tables to supplement.",
            "before_submission_action": "Keep the compact manuscript focused and use crosswalk/prebuttal artifacts for cover-letter framing.",
            "overclaim_guard": "Do not let supplementary breadth obscure the main methodological contribution.",
        },
        {
            "risk_id": "RISK-07",
            "likely_reviewer_objection": "Are the data and code actually releasable?",
            "affected_claim": "Reproducibility, data availability, code availability, and DOI package.",
            "current_evidence": "Release preflight, release-license audit, DATA_SOURCES, reproducibility manifest, reproduction runbook.",
            "prebuttal_response": "Release project-created scripts and derived summaries; source-link or restrict raw third-party data and model weights.",
            "before_submission_action": "Choose final license, create repository/DOI, and update non-blinded metadata before portal upload.",
            "overclaim_guard": "Do not imply this project relicenses raw third-party datasets, upstream repositories, or model weights.",
        },
        {
            "risk_id": "RISK-08",
            "likely_reviewer_objection": "Is the selected venue/Q1 route actually current?",
            "affected_claim": "Submission positioning and submission route.",
            "current_evidence": "Journal target recheck dated 2026-06-24; journal style preflight; Q1 gate tracker.",
            "prebuttal_response": "Treat submission route and quartile status as live external checks, not static manuscript facts.",
            "before_submission_action": "Reopen official journal/special-issue pages and quartile database immediately before upload.",
            "overclaim_guard": "Do not call the package final submission-ready until live route/quartile checks are refreshed.",
        },
    ]


def write_csv(path: Path, data: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(data[0].keys()))
        writer.writeheader()
        writer.writerows(data)


def build_markdown(data: list[dict[str, str]]) -> str:
    lines = [
        "# Reviewer Prebuttal Audit",
        "",
        "This audit anticipates likely Q1-reviewer objections and maps each one to current evidence, a response posture, and a non-overclaim guard.",
        "",
        "## Summary",
        "",
        f"- Reviewer risks tracked: {len(data)}",
        "- Use: tighten discussion, limitations, cover letter, and response-to-reviewer drafts.",
        "",
        "## Risk Ledger",
        "",
        "| Risk | Likely objection | Current evidence | Prebuttal response | Before-submission action |",
        "|---|---|---|---|---|",
    ]
    for row in data:
        lines.append(
            "| {risk_id} | {likely_reviewer_objection} | {current_evidence} | {prebuttal_response} | {before_submission_action} |".format(
                risk_id=row["risk_id"],
                likely_reviewer_objection=row["likely_reviewer_objection"].replace("|", "/"),
                current_evidence=row["current_evidence"].replace("|", "/"),
                prebuttal_response=row["prebuttal_response"].replace("|", "/"),
                before_submission_action=row["before_submission_action"].replace("|", "/"),
            )
        )
    lines += [
        "",
        "## Use Rule",
        "",
        "The `overclaim_guard` column in the CSV should be checked before strengthening any abstract, discussion, limitation, cover-letter, or response-to-reviewer language.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    data = rows()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(CSV_OUT, data)
    MD_OUT.write_text(build_markdown(data), encoding="utf-8")
    print(f"Wrote {CSV_OUT.relative_to(ROOT)}")
    print(f"Wrote {MD_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
