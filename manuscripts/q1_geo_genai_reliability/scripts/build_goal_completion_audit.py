#!/usr/bin/env python3
"""Build a requirement-level audit for the active Q1 manuscript goal."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MS_DIR = ROOT / "manuscripts/q1_geo_genai_reliability"
SUBMISSION_DIR = MS_DIR / "submission"
OUT_DIR = SUBMISSION_DIR / "evidence_map"
AUDIT_CSV = OUT_DIR / "goal_completion_audit.csv"
AUDIT_MD = OUT_DIR / "goal_completion_audit.md"


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def exists(path: Path) -> bool:
    return path.exists() and path.stat().st_size > 0


def status_from(ok: bool, blocker: str = "") -> str:
    if ok and not blocker:
        return "proven_for_manuscript_track"
    if ok and blocker == "manual":
        return "track_evidence_present_manual_gate_open"
    if ok and blocker == "external":
        return "track_evidence_present_external_gate_open"
    if ok:
        return "track_evidence_present_limitations_explicit"
    return "incomplete_or_unverified"


def build_rows() -> list[dict[str, str]]:
    readiness = text(MS_DIR / "notes/manuscript_readiness_audit.md")
    dashboard = text(MS_DIR / "notes/status_dashboard.md")
    manuscript = text(SUBMISSION_DIR / "compact_main_manuscript.md")
    goal_handoff = text(MS_DIR / "notes/morning_handoff_2026_06_25.md")
    q1_gates = read_csv(SUBMISSION_DIR / "q1_submission_gate_tracker/q1_submission_gate_tracker.csv")
    human_metrics = read_csv(SUBMISSION_DIR / "human_validation_panels/summaries/human_validation_metric_summary.csv")
    scgm_probe = read_csv(SUBMISSION_DIR / "scgm_official_reproduction_audit/scgm_official_feasibility_probe.csv")
    manifest_rows = read_csv(SUBMISSION_DIR / "reproducibility_manifest.csv")
    runbook_rows = read_csv(SUBMISSION_DIR / "reproduction_runbook_commands.csv")
    latex_log = text(SUBMISSION_DIR / "latex/latex_build.log")
    open_gates = [row for row in q1_gates if row.get("status", "").startswith("open")]
    human_labels_open = any(row.get("status") == "no_labels_collected" for row in human_metrics)
    scgm_open = any(row.get("gate_id") == "G05" and row.get("status", "").startswith("open") for row in q1_gates)
    release_open = any(row.get("gate_id") in {"G06", "G07", "G08"} and row.get("status", "").startswith("open") for row in q1_gates)
    journal_open = any(row.get("gate_id") in {"G01", "G02", "G09"} and row.get("status", "").startswith("open") for row in q1_gates)

    requirements = [
        {
            "requirement_id": "R01",
            "requirement": "Q1-journal manuscript track",
            "evidence_test": (
                "Automated gates passed:" in readiness
                and "LaTeX submission package compiles to PDF | PASS" in readiness
                and exists(SUBMISSION_DIR / "blinded_compact_main_manuscript.md")
                and exists(SUBMISSION_DIR / "latex/main.tex")
                and exists(SUBMISSION_DIR / "latex/main.pdf")
                and ("Output written on main.pdf" in latex_log or "All targets (main.pdf) are up-to-date" in latex_log)
            ),
            "blocker": "manual" if journal_open else "",
            "authoritative_evidence": "notes/manuscript_readiness_audit.md; submission/blinded_compact_main_manuscript.md; submission/latex/main.tex; submission/latex/main.pdf; submission/journal_style_preflight",
            "proven_now": "Compact manuscript and compiled LaTeX/PDF submission package are present.",
            "not_yet_proven": "Final journal-native reference style, portal route, and Q1/deadline recheck remain manual near submission.",
        },
        {
            "requirement_id": "R02",
            "requirement": "Full reproducibility audit",
            "evidence_test": (
                "Review-facing data-source manifest exists | PASS" in readiness
                and "Reproducibility release plan exists | PASS" in readiness
                and "Reproducibility checksum manifest exists | PASS" in readiness
                and len(manifest_rows) >= 900
                and exists(SUBMISSION_DIR / "DATA_SOURCES.md")
                and exists(SUBMISSION_DIR / "reproducibility_release_plan.md")
                and exists(SUBMISSION_DIR / "release_preflight/release_preflight_checks.csv")
                and exists(SUBMISSION_DIR / "public_release_skeleton/README_release_skeleton.md")
            ),
            "blocker": "manual" if release_open else "",
            "authoritative_evidence": "experiments/00_dataset_reproducibility_audit/outputs; submission/DATA_SOURCES.md; submission/reproducibility_manifest.csv; submission/release_preflight; submission/public_release_skeleton",
            "proven_now": f"Dataset and release evidence are present; checksum manifest tracks {len(manifest_rows)} artifacts.",
            "not_yet_proven": "Final public repository URL, DOI, and top-level license decision are not yet closed.",
        },
        {
            "requirement_id": "R03",
            "requirement": "Caption fidelity experiment",
            "evidence_test": (
                "MapGenerator two-VLM agreement table populated | PASS" in readiness
                and "MapGenerator CLIP/SigLIP scoring completed | PASS" in readiness
                and "Human validation metric summarizer is acceptance-criteria ready | PASS" in readiness
                and len(human_metrics) == 2
            ),
            "blocker": "manual" if human_labels_open else "",
            "authoritative_evidence": "experiments/02_mapgenerator_image_text_audit/outputs; tables/table_15c_mapgenerator_clip_caption_embedding.csv; submission/human_validation_panels; submission/evaluator_reliability",
            "proven_now": "Proxy, VLM, CLIP/SigLIP, agreement, and packetized human-label workflow are in place.",
            "not_yet_proven": "Two-annotator human labels are still blank; urgent caption-disagreement closure is 0/17.",
        },
        {
            "requirement_id": "R04",
            "requirement": "Choropleth code-generation QA and repair",
            "evidence_test": (
                "Iterative repair sweep covers all incomplete one-pass repairs | PASS" in readiness
                and "Matched repair-model suite populated | PASS" in readiness
                and "Choropleth two-VLM agreement table populated | PASS" in readiness
                and exists(SUBMISSION_DIR / "repair_model_suite/matched_repair_model_summary.csv")
            ),
            "blocker": "manual" if human_labels_open else "",
            "authoritative_evidence": "experiments/05_choropleth_reliability_benchmark/outputs; submission/repair_model_suite; tables/table_18b_choropleth_vlm_agreement.csv; submission/human_validation_panels",
            "proven_now": "Generated-code scoring, artifact QA, screenshot QA, iterative repair, matched repair-model suite, and VLM review are present.",
            "not_yet_proven": "Two-annotator cartographic-quality labels are still blank; urgent cartographic-disagreement closure is 0/5.",
        },
        {
            "requirement_id": "R05",
            "requirement": "SCGM tile continuity and reproduction program",
            "evidence_test": (
                "SCGM mosaic neighbor-seam stress audit populated | PASS" in readiness
                and "SCGM official reproduction contract exists | PASS" in readiness
                and "SCGM official-reproduction readiness audit exists | PASS" in readiness
                and "SCGM official feasibility probe localizes runtime and config blockers | PASS" in readiness
                and "SCGM trained tiny-CNN baseline populated | PASS" in readiness
                and len(scgm_probe) == 15
            ),
            "blocker": "external" if scgm_open else "",
            "authoritative_evidence": "experiments/03_scgm_subset_reproduction/outputs; submission/scgm_official_reproduction_contract; submission/scgm_official_reproduction_audit; submission/scgm_official_feasibility_probe",
            "proven_now": "Continuity metrics, low-compute baselines, generated-output diagnostics, official run contract, local override bridge, and local feasibility probe are present.",
            "not_yet_proven": "Official or cascade-conditioned diffusion-style SCGM reproduction remains open because runtime/import, checkpoint, and output-generation dependencies are not closed.",
        },
        {
            "requirement_id": "R06",
            "requirement": "Cross-paradigm evaluation",
            "evidence_test": (
                "Cross-paradigm reliability matrix exists | PASS" in readiness
                and exists(SUBMISSION_DIR / "cross_paradigm/cross_paradigm_reliability_matrix.csv")
                and "cross-paradigm" in manuscript.lower()
            ),
            "blocker": "",
            "authoritative_evidence": "submission/cross_paradigm/cross_paradigm_reliability_matrix.csv; tables/table_23_cross_paradigm_reliability_summary.csv; submission/compact_main_manuscript.md",
            "proven_now": "Unified taxonomy and summary scores connect text-to-map, remote-sensing-to-map, and LLM-code map artifacts.",
            "not_yet_proven": "Expert validation of diagnostic scoring remains a possible strengthening step, not an automated completion gate.",
        },
        {
            "requirement_id": "R07",
            "requirement": "Reproducible rebuild path and full experimental program",
            "evidence_test": (
                len(runbook_rows) == 26
                and sum(row.get("required") == "yes" for row in runbook_rows) == 20
                and sum(row.get("required") == "optional" for row in runbook_rows) == 6
                and "Reproduction runbook exists | PASS | commands=26; required=20; optional=6" in readiness
                and exists(SUBMISSION_DIR / "supplementary_material_manifest.md")
            ),
            "blocker": "",
            "authoritative_evidence": "submission/reproduction_runbook_commands.csv; submission/supplementary_material_manifest.md; submission/reproducibility_manifest.csv",
            "proven_now": "Runbook covers deterministic rebuild steps and optional model-dependent reruns across the experimental program.",
            "not_yet_proven": "Optional model-dependent reruns are intentionally preserved as evidence rather than required bit-reproducible reruns.",
        },
        {
            "requirement_id": "R08",
            "requirement": "Goal completion can be claimed",
            "evidence_test": (
                "Automated gates passed:" in readiness
                and not open_gates
                and "Remaining Manual/Q1 Gates" not in readiness
            ),
            "blocker": "manual" if open_gates else "",
            "authoritative_evidence": "notes/manuscript_readiness_audit.md; submission/q1_submission_gate_tracker/q1_submission_gate_tracker.csv; notes/status_dashboard.md",
            "proven_now": "Automated manuscript-track package is strong and all automated gates pass.",
            "not_yet_proven": f"{len(open_gates)} Q1 submission gates remain open, so the persistent goal should remain active.",
        },
    ]

    rows: list[dict[str, str]] = []
    for item in requirements:
        status = status_from(bool(item["evidence_test"]), item["blocker"])
        rows.append(
            {
                "requirement_id": item["requirement_id"],
                "requirement": item["requirement"],
                "verification_status": status,
                "authoritative_evidence": item["authoritative_evidence"],
                "proven_now": item["proven_now"],
                "not_yet_proven": item["not_yet_proven"],
            }
        )

    # Keep this file useful as a quick handoff even when generated before the
    # morning handoff note exists.
    if goal_handoff:
        rows.append(
            {
                "requirement_id": "R09",
                "requirement": "Human-readable handoff for continued work",
                "verification_status": "proven_for_manuscript_track",
                "authoritative_evidence": "notes/morning_handoff_2026_06_25.md",
                "proven_now": "A concise continuation note identifies the active track, large data, experiments, automated status, and next work block.",
                "not_yet_proven": "The handoff is informational; it does not close manual Q1 gates.",
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    open_rows = [row for row in rows if row["verification_status"] != "proven_for_manuscript_track"]
    lines = [
        "# Goal Completion Audit",
        "",
        "This audit verifies the active Q1 manuscript objective requirement by requirement. It deliberately separates a strong manuscript-track evidence package from final submission readiness.",
        "",
        "## Summary",
        "",
        f"- Requirements checked: {len(rows)}",
        f"- Fully proven for current manuscript track: {sum(row['verification_status'] == 'proven_for_manuscript_track' for row in rows)}",
        f"- Requirements with manual or external gates still open: {len(open_rows)}",
        "- Goal status: keep active until all manual/external Q1 gates are closed.",
        "",
        "## Requirement Ledger",
        "",
        "| ID | Requirement | Verification status | Proven now | Not yet proven |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| {requirement_id} | {requirement} | {verification_status} | {proven_now} | {not_yet_proven} |".format(
                **{k: v.replace("|", "/") for k, v in row.items()}
            )
        )
    lines += [
        "",
        "## Interpretation",
        "",
        "- The current package is suitable as a strong, auditable manuscript track.",
        "- It is not yet a final submission package because human labels, official SCGM reproduction disposition, DOI/repository metadata, license, and final journal/citation checks remain open.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    rows = build_rows()
    write_csv(AUDIT_CSV, rows)
    write_markdown(AUDIT_MD, rows)
    print(f"Wrote {AUDIT_CSV.relative_to(ROOT)}")
    print(f"Wrote {AUDIT_MD.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
