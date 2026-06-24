#!/usr/bin/env python3
"""Build a public-release skeleton without selecting the final DOI or license."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MS_DIR = ROOT / "manuscripts/q1_geo_genai_reliability"
SUBMISSION_DIR = MS_DIR / "submission"
OUT_DIR = SUBMISSION_DIR / "public_release_skeleton"
README_OUT = OUT_DIR / "README_release_skeleton.md"
FILE_MAP_OUT = OUT_DIR / "RELEASE_FILE_MAP.csv"
EXCLUSIONS_OUT = OUT_DIR / "THIRD_PARTY_EXCLUSIONS.md"
LICENSE_OUT = OUT_DIR / "LICENSE_DECISION_REQUIRED.md"
SUMMARY_OUT = OUT_DIR / "release_manifest_summary.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def manifest_group(relative_path: str) -> str:
    if relative_path.startswith("manuscripts/q1_geo_genai_reliability/scripts/"):
        return "project_scripts"
    if relative_path.startswith("experiments/") and "/scripts/" in relative_path:
        return "experiment_scripts"
    if "/submission/tables/" in relative_path or "/tables/" in relative_path:
        return "tables"
    if "/figures/" in relative_path:
        return "figures"
    if "/submission/human_validation_panels/" in relative_path:
        return "human_validation_packets"
    if "/submission/release_" in relative_path or "/submission/public_release_skeleton/" in relative_path:
        return "release_metadata"
    if "/submission/evidence_map/" in relative_path or "/submission/cross_paradigm/" in relative_path:
        return "evidence_ledgers"
    if relative_path.endswith(".tex") or relative_path.endswith(".pdf") or "/submission/latex/" in relative_path:
        return "latex_manuscript_package"
    if "/submission/" in relative_path:
        return "submission_artifacts"
    if relative_path.startswith("experiments/"):
        return "derived_experiment_outputs"
    if relative_path.startswith("manuscripts/q1_geo_genai_reliability/"):
        return "manuscript_artifacts"
    return "other"


def build_file_map(manifest_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    families = [
        {
            "release_family": "project_scripts",
            "include_in_public_release": "yes",
            "content_rule": "Include project-created manuscript and experiment scripts.",
            "exclude_or_restrict": "Exclude local caches, temporary notebooks, and machine-specific outputs.",
            "examples": "manuscripts/q1_geo_genai_reliability/scripts; experiments/*/scripts",
        },
        {
            "release_family": "derived_experiment_outputs",
            "include_in_public_release": "yes_with_review",
            "content_rule": "Include derived CSV, JSON, Markdown summaries, prompts, QA ledgers, and safety scans created by this study.",
            "exclude_or_restrict": "Do not include raw third-party images, captions, tiles, upstream repositories, model checkpoints, or bulky generated run directories unless terms permit.",
            "examples": "experiment outputs/scores; audit summaries; contact sheets when redistribution is permitted",
        },
        {
            "release_family": "manuscript_artifacts",
            "include_in_public_release": "yes",
            "content_rule": "Include manuscript draft, compact route, tables, figures, notes, protocols, and supplementary ledgers.",
            "exclude_or_restrict": "Keep double-anonymous review files separate from non-blinded DOI metadata when required by the review route.",
            "examples": "draft; tables; figures; protocols; submission ledgers",
        },
        {
            "release_family": "human_validation_packets",
            "include_in_public_release": "yes",
            "content_rule": "Include blank annotator packets, rubric, file contract, galleries, and final-label templates.",
            "exclude_or_restrict": "Do not invent labels; exclude any future private annotator identity metadata.",
            "examples": "human_validation_panels; adjudication queue; final-label template",
        },
        {
            "release_family": "release_metadata",
            "include_in_public_release": "yes",
            "content_rule": "Include data-source manifest, runbook, environment manifests, checksum manifest, license audit, and this skeleton.",
            "exclude_or_restrict": "Replace TODO repository, DOI, author, and license fields only after the final route is chosen.",
            "examples": "DATA_SOURCES.md; reproducibility_manifest.csv; release_preflight; public_release_skeleton",
        },
        {
            "release_family": "third_party_raw_data",
            "include_in_public_release": "no",
            "content_rule": "Source-link raw upstream data and document expected local layout.",
            "exclude_or_restrict": "Raw SCGM/CSCMG tiles, raw MapGenerator images/captions, raw map-sheet corpora, cloned upstream repositories, and model weights are not redistributed by this skeleton.",
            "examples": "data/raw; data/repos; checkpoints; local model caches",
        },
    ]
    counts = Counter(manifest_group(row.get("relative_path", "")) for row in manifest_rows)
    for row in families:
        row["tracked_manifest_rows_in_current_package"] = str(counts.get(row["release_family"], 0))
    return families


def build_summary(manifest_rows: list[dict[str, str]], license_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    counts = Counter(manifest_group(row.get("relative_path", "")) for row in manifest_rows)
    rows = [
        {
            "metric": "manifest_rows_available_to_release_audit",
            "value": str(len(manifest_rows)),
            "interpretation": "Rows are the current local evidence package, not a frozen DOI archive.",
        },
        {
            "metric": "license_matrix_rows",
            "value": str(len(license_rows)),
            "interpretation": "Rows separate author-controlled artifacts from source-linked or restricted upstream material.",
        },
    ]
    for group, count in sorted(counts.items()):
        rows.append(
            {
                "metric": f"group_{group}",
                "value": str(count),
                "interpretation": "Current manifest grouping used to draft the public release file map.",
            }
        )
    return rows


def build_readme(manifest_rows: list[dict[str, str]], license_rows: list[dict[str, str]]) -> str:
    return "\n".join(
        [
            "# Public Release Skeleton",
            "",
            "This folder is a repository-facing skeleton for the Geo-GenAI reliability manuscript package. It prepares the public release layout without selecting the final DOI, repository URL, author metadata, or top-level license.",
            "",
            "## Intended Public Contents",
            "",
            "- Project-created scripts for manuscript building, dataset audits, MapGenerator caption fidelity screening, SCGM diagnostics, choropleth code-generation QA, repair evaluation, and release checks.",
            "- Derived CSV, JSON, Markdown, figure, table, prompt, safety-scan, QA, and manifest artifacts created by this study.",
            "- Human-validation packet templates, rubrics, galleries, assignment files, adjudication queue, final-label template, and final-label reducer outputs.",
            "- Environment manifests, reproduction runbook, data-source manifest, checksum manifest, release-license audit, DOI metadata drafts, and reviewer-facing documentation.",
            "",
            "## Explicit Exclusions",
            "",
            "- Raw third-party datasets and cloned upstream repositories are source-linked, not redistributed.",
            "- Raw SCGM/CSCMG archives or extracted tile trees are not part of the public package unless final license review permits them.",
            "- Raw MapGenerator images/captions are not part of the public package when their terms require source-linking or restricted use.",
            "- Model checkpoints, local model caches, pretrained weights, private keys, shell histories, and machine-specific absolute paths are excluded.",
            "- Bulky generated run folders should be represented by derived metrics, QA ledgers, selected permissible figures, or restricted reviewer material.",
            "",
            "## Current Evidence Counts",
            "",
            f"- Current checksum manifest rows inspected: {len(manifest_rows)}",
            f"- Release-license matrix rows inspected: {len(license_rows)}",
            "",
            "## Files In This Skeleton",
            "",
            "- `README_release_skeleton.md`: this public-facing release overview.",
            "- `RELEASE_FILE_MAP.csv`: include/exclude rules by artifact family.",
            "- `THIRD_PARTY_EXCLUSIONS.md`: source-link and exclusion rules for upstream data, repositories, and weights.",
            "- `LICENSE_DECISION_REQUIRED.md`: final license decision checklist, intentionally unresolved here.",
            "- `release_manifest_summary.csv`: manifest group counts for the current local evidence package.",
            "",
            "## Manual Steps Before DOI Deposit",
            "",
            "1. Choose the public repository route and update repository metadata.",
            "2. Choose final top-level code/evidence license terms after checking third-party constraints.",
            "3. Mint the DOI and replace TODO metadata in the release preflight files.",
            "4. Rebuild the checksum manifest after the public file set is frozen.",
            "5. Re-run the readiness audit and local-path residue sweep.",
            "",
        ]
    )


def build_exclusions(license_rows: list[dict[str, str]]) -> str:
    lines = [
        "# Third-Party Exclusions and Source-Linking Rules",
        "",
        "This skeleton does not redistribute raw third-party data, upstream repositories, or model weights. It records the public-release action that should be taken for each artifact family before a DOI archive is created.",
        "",
        "| Artifact family | Terms | Public-release action |",
        "|---|---|---|",
    ]
    for row in license_rows:
        family = row.get("artifact_family", "").replace("|", "/")
        terms = row.get("detected_license_or_terms", "").replace("|", "/")
        action = row.get("public_release_action", "").replace("|", "/")
        lines.append(f"| {family} | {terms} | {action} |")
    lines += [
        "",
        "## Non-Redistribution Rule",
        "",
        "If a file is raw upstream content, a cloned upstream repository, a checkpoint, or a local model cache, leave it out of the public package unless redistribution rights are explicitly confirmed. Provide source URL, commit or version, access date, expected local layout, and rebuild scripts instead.",
        "",
    ]
    return "\n".join(lines)


def build_license_note() -> str:
    return "\n".join(
        [
            "# License Decision Required",
            "",
            "No final top-level license is selected by this skeleton.",
            "",
            "## Required Author Decisions",
            "",
            "- Choose a license for project-created code.",
            "- Choose compatible terms for derived tables, figures, prompts, QA ledgers, and manuscript evidence.",
            "- Confirm whether any third-party-derived thumbnails or contact sheets may be redistributed.",
            "- Keep raw third-party datasets, upstream repositories, and model weights source-linked or restricted unless the relevant terms explicitly allow redistribution.",
            "- Update `release_preflight/zenodo_metadata_draft.json`, `release_preflight/CITATION.cff`, and `release_preflight/codemeta_draft.json` after the repository URL, DOI, release tag, author metadata, and license are final.",
            "",
            "## Review Guard",
            "",
            "Do not treat this file as legal advice or as a final license grant. It is a checklist that prevents the manuscript package from silently implying a license choice before the author makes one.",
            "",
        ]
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest_rows = read_csv(SUBMISSION_DIR / "reproducibility_manifest.csv")
    license_rows = read_csv(SUBMISSION_DIR / "release_license_audit/release_license_matrix.csv")
    write_csv(FILE_MAP_OUT, build_file_map(manifest_rows))
    write_csv(SUMMARY_OUT, build_summary(manifest_rows, license_rows))
    README_OUT.write_text(build_readme(manifest_rows, license_rows), encoding="utf-8")
    EXCLUSIONS_OUT.write_text(build_exclusions(license_rows), encoding="utf-8")
    LICENSE_OUT.write_text(build_license_note(), encoding="utf-8")
    print(f"Wrote {README_OUT.relative_to(ROOT)}")
    print(f"Wrote {FILE_MAP_OUT.relative_to(ROOT)}")
    print(f"Wrote {EXCLUSIONS_OUT.relative_to(ROOT)}")
    print(f"Wrote {LICENSE_OUT.relative_to(ROOT)}")
    print(f"Wrote {SUMMARY_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
