#!/usr/bin/env python3
"""Build a reviewer-facing manuscript claim-to-evidence crosswalk."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MS_DIR = ROOT / "manuscripts/q1_geo_genai_reliability"
OUT_DIR = MS_DIR / "submission/claim_evidence_crosswalk"
CSV_OUT = OUT_DIR / "claim_evidence_crosswalk.csv"
MD_OUT = OUT_DIR / "claim_evidence_crosswalk.md"


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def rows() -> list[dict[str, str]]:
    return [
        {
            "claim_id": "C01",
            "manuscript_claim": "Public Geo-GenAI artifacts are available but unevenly reproducible across data, code, model, and evaluation layers.",
            "rq": "RQ1",
            "primary_evidence": "Tables 1, 2, 8; dataset inventory; reproducibility matrix; DATA_SOURCES; citation verification",
            "machine_artifacts": "experiments/00_dataset_reproducibility_audit/outputs; submission/DATA_SOURCES.md; submission/reproducibility_manifest.csv",
            "claim_strength": "strong_local_audit",
            "reviewer_caveat": "Final public DOI/repository and just-in-time publisher/source checks remain manual.",
            "do_not_overclaim": "Do not imply that missing model weights, API versions, or private datasets were fully reproduced.",
        },
        {
            "claim_id": "C02",
            "manuscript_claim": "MapGenerator captions require fidelity auditing beyond file existence and caption fluency.",
            "rq": "RQ2",
            "primary_evidence": "Tables 3, 9, 15, 15b, 15c, 21, 22; proxy review; VLM reviews; CLIP screening; judge robustness audit",
            "machine_artifacts": "experiments/02_mapgenerator_image_text_audit/outputs; submission/human_validation_panels; submission/evaluator_reliability",
            "claim_strength": "proxy_vlm_clip_screening",
            "reviewer_caveat": "Caption truth still needs human labels or a larger calibrated judge panel.",
            "do_not_overclaim": "Do not treat VLM verdicts, CLIP scores, or color/edge proxies as expert ground truth.",
        },
        {
            "claim_id": "C03",
            "manuscript_claim": "SCGM/CSCMG supports local spatial-faithfulness diagnostics, but generated-output baselines expose metric trade-offs and incomplete cartographic detail.",
            "rq": "RQ3",
            "primary_evidence": "Tables 4, 5, 5b, 5c, 5d; Figures 4, 6, 9; generated-output metrics; mosaic neighbor-seam stress audit; official-reproduction readiness audit and run contract",
            "machine_artifacts": "experiments/03_scgm_subset_reproduction/outputs; SCGM baseline scripts; generated-output summaries; submission/scgm_official_reproduction_audit; submission/scgm_official_reproduction_contract",
            "claim_strength": "deterministic_learned_cnn_mosaic_diagnostics",
            "reviewer_caveat": "Official/cascade-conditioned diffusion reproduction remains unresolved because checkpoint, instantiated-runtime, and generated-output blockers are explicit.",
            "do_not_overclaim": "Do not present retrieval, ridge, forest, patch, or tiny-CNN baselines as reproduction of the original SCGM model.",
        },
        {
            "claim_id": "C04",
            "manuscript_claim": "LLM-generated choropleth code fails at artifact-chain validity, not merely at syntax or process exit status.",
            "rq": "RQ4",
            "primary_evidence": "Tables 6, 10, 12, 13, 14, 16, 18, 18b, 19, 20, 25; Figures 5, 7, 8; run logs; safety scans; screenshot QA",
            "machine_artifacts": "experiments/05_choropleth_reliability_benchmark/outputs; repair_model_suite; human_validation_panels",
            "claim_strength": "strong_local_executable_benchmark",
            "reviewer_caveat": "Human visual-quality labels remain open beyond calibrated VLM consensus.",
            "do_not_overclaim": "Do not call validator/reference repair an LLM success; it is an oracle-style positive control.",
        },
        {
            "claim_id": "C05",
            "manuscript_claim": "Validator-gated repair can recover some choropleth artifact contracts, but repair success is model-, case-, and contract-dependent.",
            "rq": "RQ4",
            "primary_evidence": "Tables 19, 20, 25; iterative 32B repair sweep; matched Qwen 7B/14B and DeepSeek repair suite",
            "machine_artifacts": "experiments/05_choropleth_reliability_benchmark/outputs/scores; submission/repair_model_suite",
            "claim_strength": "strong_repair_diagnostics",
            "reviewer_caveat": "Matched repair suite is still smaller than the full 40-case 32B iterative sweep.",
            "do_not_overclaim": "Do not rank repair models universally from a near-miss subset.",
        },
        {
            "claim_id": "C06",
            "manuscript_claim": "Cross-paradigm reliability should be reported by artifact-specific dimensions rather than a single universal score.",
            "rq": "RQ5",
            "primary_evidence": "Tables 11, 17, 21, 22, 23; cross-paradigm reliability matrix; RQ evidence map",
            "machine_artifacts": "submission/cross_paradigm; submission/evidence_map",
            "claim_strength": "strong_conceptual_synthesis",
            "reviewer_caveat": "Diagnostic 0-3 scores would benefit from expert validation before final article submission.",
            "do_not_overclaim": "Do not treat cross-paradigm scores as universal quality rankings.",
        },
        {
            "claim_id": "C07",
            "manuscript_claim": "The submission package is auditable and rebuildable as a compact manuscript plus supplement.",
            "rq": "Packaging",
            "primary_evidence": "Blinded compact manuscript; compiled LaTeX/PDF package; reproduction runbook; release preflight; reproducibility manifest; readiness audit",
            "machine_artifacts": "submission/blinded_compact_main_manuscript.md; submission/latex; submission/reproduction_runbook.md; submission/release_preflight; notes/manuscript_readiness_audit.md",
            "claim_strength": "strong_package_controls",
            "reviewer_caveat": "Journal-native formatting, final repository DOI/URL, license decision, and non-blinded metadata remain manual.",
            "do_not_overclaim": "Do not call the package final submission-ready until manual gates are closed.",
        },
    ]


def build_markdown(items: list[dict[str, str]]) -> str:
    lines = [
        "# Claim-to-Evidence Crosswalk",
        "",
        "This crosswalk is a reviewer-facing control artifact. It links the manuscript's major claims to local evidence, caveats, and explicit non-overclaim boundaries.",
        "",
        "| Claim | RQ | Strength | Primary evidence | Reviewer caveat | Do not overclaim |",
        "|---|---|---|---|---|---|",
    ]
    for row in items:
        lines.append(
            f"| {row['claim_id']}: {row['manuscript_claim']} | {row['rq']} | {row['claim_strength']} | {row['primary_evidence']} | {row['reviewer_caveat']} | {row['do_not_overclaim']} |"
        )
    lines += [
        "",
        "## Use",
        "",
        "- Use this file when tightening the discussion, limitations, cover letter, and response-to-reviewer materials.",
        "- Preserve the `do_not_overclaim` column until the corresponding manual evidence is actually collected.",
        "- Treat this crosswalk as a supplement-control artifact, not as a replacement for manuscript prose.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    items = rows()
    write_csv(CSV_OUT, items)
    MD_OUT.write_text(build_markdown(items), encoding="utf-8")
    print(f"Wrote {CSV_OUT.relative_to(ROOT)}")
    print(f"Wrote {MD_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
