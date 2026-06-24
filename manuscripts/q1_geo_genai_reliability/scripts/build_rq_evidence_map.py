#!/usr/bin/env python3
"""Build RQ-to-evidence and objective-completion audit artifacts."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MS_DIR = ROOT / "manuscripts/q1_geo_genai_reliability"
SUBMISSION_DIR = MS_DIR / "submission"
OUT_DIR = SUBMISSION_DIR / "evidence_map"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def exists(rel: str) -> bool:
    return (ROOT / rel).exists() and (ROOT / rel).stat().st_size > 0


def build_rq_rows() -> list[dict[str, str]]:
    table20 = read_csv(MS_DIR / "tables/table_20_iterative_repair_model_comparison.csv")
    table23 = read_csv(MS_DIR / "tables/table_23_cross_paradigm_reliability_summary.csv")
    qwen32 = next(row for row in table20 if row["Repair model"] == "qwen2.5-coder:32b")
    cross_summary = "; ".join(f"{row['Paradigm']} mean={row['Mean score']}" for row in table23)
    return [
        {
            "RQ": "RQ1",
            "Question": "How reproducible are public Geo-GenAI map-generation artifacts when evaluated as data-code-model-output chains?",
            "Primary evidence": "Tables 1, 2, 8; dataset inventory; reproducibility matrix; citation verification; data-source manifest",
            "Key result": "Public artifacts are usable but uneven across data, code, models, and evaluation metadata.",
            "Machine-readable artifacts": "experiments/00_dataset_reproducibility_audit/outputs; submission/DATA_SOURCES.md; submission/citation_verification_report.csv",
            "Current strength": "strong_local_audit",
            "Remaining gap": "Final DOI/release and just-in-time source/citation recheck before submission.",
        },
        {
            "RQ": "RQ2",
            "Question": "Do text-to-map map datasets provide captions that are sufficiently grounded for faithful map generation and evaluation?",
            "Primary evidence": "Tables 3, 9, 15, 15b, 15c, 21, 22; proxy review; VLM pilot; CLIP screening; judge robustness audit",
            "Key result": "File validity is strong, but semantic caption support is evaluator-sensitive; 17/20 paired cases need urgent human adjudication, and CLIP screening scores all 200 proxy-reviewed pairs without replacing human labels.",
            "Machine-readable artifacts": "experiments/02_mapgenerator_image_text_audit/outputs; submission/human_validation_panels; submission/evaluator_reliability",
            "Current strength": "proxy_vlm_and_clip_screening",
            "Remaining gap": "Human labels or a larger calibrated multi-judge caption panel.",
        },
        {
            "RQ": "RQ3",
            "Question": "How should remote-sensing-to-map generation be evaluated beyond file availability and visual plausibility?",
            "Primary evidence": "Tables 4, 5, 5b, 5c, 5d; Figures 4, 6, 9; eight leakage-guarded generated-output baselines; mosaic neighbor-seam stress audit; SCGM official-reproduction readiness audit and run contract",
            "Key result": "SCGM base pairs are complete, cascade references are incomplete globally, complete-reference validation subsets and run commands are contracted, and the official reproduction path is now blocked mainly by checkpoint/runtime/output-generation gaps.",
            "Machine-readable artifacts": "experiments/03_scgm_subset_reproduction/outputs; SCGM baseline scripts; generated contact sheets; mosaic seam stress outputs; submission/scgm_official_reproduction_audit",
            "Current strength": "deterministic_learned_and_trained_cnn_diagnostics",
            "Remaining gap": "Official or cascade-conditioned diffusion-style reproduction after checkpoint acquisition, runtime instantiation, and output scoring are resolved.",
        },
        {
            "RQ": "RQ4",
            "Question": "Can LLM-generated GIS/code maps produce complete, executable, cartographically valid artifacts under basic and rule-guided prompting?",
            "Primary evidence": "Tables 6, 10, 12, 13, 14, 16, 18, 18b, 19, 20; Figures 5, 7, 8",
            "Key result": f"Initial local generation produces zero complete artifacts; iterative validator-gated repair completes {qwen32['Completed']}/{qwen32['Cases']} incomplete one-pass repairs.",
            "Machine-readable artifacts": "experiments/05_choropleth_reliability_benchmark/outputs; safety scans; run logs; screenshot QA; VLM reviews",
            "Current strength": "executable_benchmark_and_repair",
            "Remaining gap": "Broader matched repair-model suite and human visual-quality labels beyond the calibrated VLM consensus.",
        },
        {
            "RQ": "RQ5",
            "Question": "What cross-paradigm failure taxonomy can unify text-to-map, remote-sensing-to-map, and LLM-code map generation?",
            "Primary evidence": "Tables 11, 17, 21, 22, 23; cross-paradigm reliability matrix",
            "Key result": cross_summary,
            "Machine-readable artifacts": "submission/cross_paradigm/cross_paradigm_reliability_matrix.csv; submission/cross_paradigm/cross_paradigm_reliability_summary.csv",
            "Current strength": "cross_paradigm_synthesis",
            "Remaining gap": "Final prose compression and possible expert validation of the diagnostic scoring scheme.",
        },
    ]


def build_objective_rows() -> list[dict[str, str]]:
    readiness = (MS_DIR / "notes/manuscript_readiness_audit.md").read_text(encoding="utf-8")
    status = (MS_DIR / "notes/status_dashboard.md").read_text(encoding="utf-8")
    requirements = [
        (
            "about_30_pages",
            "Q1-journal manuscript track",
            exists("manuscripts/q1_geo_genai_reliability/submission/main_text_compression_plan.md")
            and "Estimated pages low/mid/high: 23.7/27.4/32.2" in (SUBMISSION_DIR / "main_text_compression_plan.md").read_text(encoding="utf-8"),
            "submission/main_text_compression_plan.md; notes/page_budget_audit.md",
            "Compact manuscript exists with a main/supplement split; final template may still require tightening.",
        ),
        (
            "reproducibility_audit",
            "Reproducibility audit",
            "Reproducibility release plan exists | PASS" in readiness and "Structured citation metadata export exists | PASS" in readiness,
            "Tables 1, 2, 8; DATA_SOURCES; release plan; citation verification",
            "Final DOI/public repository still pending.",
        ),
        (
            "caption_fidelity",
            "Caption fidelity experiment",
            "MapGenerator two-VLM agreement table populated | PASS" in readiness
            and "MapGenerator CLIP/SigLIP scoring completed | PASS" in readiness
            and "VLM judge robustness audit exists | PASS" in readiness,
            "Tables 9, 15, 15b, 15c, 21, 22; proxy/VLM/CLIP outputs",
            "Human labels remain open.",
        ),
        (
            "choropleth_qa_repair",
            "Choropleth code-generation QA and repair",
            "Iterative repair sweep covers all incomplete one-pass repairs | PASS" in readiness
            and "Screenshot QA includes validator/reference passes | PASS" in readiness,
            "Tables 10, 13, 16, 19, 20; run logs; safety scans; screenshot QA",
            "Broader matched repair-model suite remains a strengthening step.",
        ),
        (
            "scgm_reproduction",
            "SCGM tile continuity/reproduction",
            "SCGM convolutional filter-bank image baseline populated | PASS" in readiness
            and "SCGM local-context image baseline populated | PASS" in readiness
            and "SCGM trained tiny-CNN baseline populated | PASS" in readiness
            and "SCGM official-reproduction readiness audit exists | PASS" in readiness,
            "Tables 4, 5, 5b, 5c, 5d; Figure 9; SCGM generated outputs; mosaic seam audit; official-reproduction readiness audit and run contract",
            "Official/cascade-conditioned diffusion reproduction still not complete; checkpoint/runtime/output-generation blockers remain explicit after the run contract.",
        ),
        (
            "cross_paradigm",
            "Cross-paradigm evaluation",
            "Cross-paradigm reliability matrix exists | PASS" in readiness
            and "Cross-paradigm reliability summary" in status,
            "Tables 11, 17, 23; cross-paradigm matrix",
            "Diagnostic scores may benefit from expert validation before final submission.",
        ),
        (
            "submission_packaging",
            "Submission-ready package controls",
            exists("manuscripts/q1_geo_genai_reliability/submission/submission_package_audit.md")
            and exists("manuscripts/q1_geo_genai_reliability/submission/ijgis_compliance_checklist.md")
            and exists("manuscripts/q1_geo_genai_reliability/submission/journal_style_preflight/journal_style_preflight.csv")
            and exists("manuscripts/q1_geo_genai_reliability/submission/release_preflight/release_preflight_checks.csv")
            and exists("manuscripts/q1_geo_genai_reliability/submission/reproduction_runbook_commands.csv")
            and exists("manuscripts/q1_geo_genai_reliability/submission/submission_abstract_pack.md")
            and exists("manuscripts/q1_geo_genai_reliability/submission/blinded_compact_main_manuscript.md"),
            "submission package audit; selected journal checklist; journal style preflight; release preflight; reproduction runbook; abstract pack; blinded manuscript",
            "Journal-native formatting, final DOI, and final non-blinded metadata remain manual.",
        ),
    ]
    rows = []
    for key, requirement, ok, evidence, remaining in requirements:
        rows.append(
            {
                "Requirement key": key,
                "Requirement": requirement,
                "Status": "evidence_present" if ok else "incomplete_or_unverified",
                "Authoritative evidence": evidence,
                "Remaining gap": remaining,
            }
        )
    return rows


def build_markdown(rq_rows: list[dict[str, str]], objective_rows: list[dict[str, str]]) -> str:
    lines = [
        "# RQ Evidence Map and Objective Completion Audit",
        "",
        "This artifact maps the manuscript's research questions and the active project objective to concrete local evidence. It is a control document, not a claim that all manual submission gates are closed.",
        "",
        "## RQ-to-Evidence Map",
        "",
        "| RQ | Current strength | Primary evidence | Remaining gap |",
        "|---|---|---|---|",
    ]
    for row in rq_rows:
        lines.append(
            f"| {row['RQ']} | {row['Current strength']} | {row['Primary evidence'].replace('|', '/')} | {row['Remaining gap'].replace('|', '/')} |"
        )
    lines += [
        "",
        "## Objective Completion Audit",
        "",
        "| Requirement | Status | Evidence | Remaining gap |",
        "|---|---|---|---|",
    ]
    for row in objective_rows:
        lines.append(
            f"| {row['Requirement']} | {row['Status']} | {row['Authoritative evidence'].replace('|', '/')} | {row['Remaining gap'].replace('|', '/')} |"
        )
    open_gaps = [row for row in objective_rows if row["Remaining gap"].strip()]
    lines += [
        "",
        "## Overall Interpretation",
        "",
        "- The automated evidence package is strong and internally guarded.",
        "- The manuscript should not be marked final submission-ready until human validation, final repository/DOI, journal formatting, and just-in-time citation/source checks are handled.",
        f"- Open or manual-gap rows: {len(open_gaps)}.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    rq_rows = build_rq_rows()
    objective_rows = build_objective_rows()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(OUT_DIR / "rq_evidence_map.csv", rq_rows)
    write_csv(OUT_DIR / "objective_completion_audit.csv", objective_rows)
    (OUT_DIR / "rq_evidence_map.md").write_text(build_markdown(rq_rows, objective_rows), encoding="utf-8")
    print(f"Wrote {(OUT_DIR / 'rq_evidence_map.csv').relative_to(ROOT)}")
    print(f"Wrote {(OUT_DIR / 'objective_completion_audit.csv').relative_to(ROOT)}")
    print(f"Wrote {(OUT_DIR / 'rq_evidence_map.md').relative_to(ROOT)}")


if __name__ == "__main__":
    main()
