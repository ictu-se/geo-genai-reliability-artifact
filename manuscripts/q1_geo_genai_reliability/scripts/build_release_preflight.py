#!/usr/bin/env python3
"""Build public repository/DOI release metadata and preflight checks."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MS_DIR = ROOT / "manuscripts/q1_geo_genai_reliability"
SUBMISSION_DIR = MS_DIR / "submission"
OUT_DIR = SUBMISSION_DIR / "release_preflight"
CSV_OUT = OUT_DIR / "release_preflight_checks.csv"
MD_OUT = OUT_DIR / "release_preflight.md"
ZENODO_OUT = OUT_DIR / "zenodo_metadata_draft.json"
CITATION_OUT = OUT_DIR / "CITATION.cff"
CODEMETA_OUT = OUT_DIR / "codemeta_draft.json"
CHECKLIST_OUT = OUT_DIR / "doi_release_checklist.md"

TITLE = "From Map-Like Images to Trustworthy Cartographic Artifacts: A Cross-Paradigm Reliability Audit of Geo-Generative AI"
KEYWORDS = [
    "GeoAI",
    "generative AI",
    "cartography",
    "map generation",
    "reproducibility",
    "remote sensing",
    "choropleth maps",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def add_check(
    rows: list[dict[str, str]],
    category: str,
    check: str,
    mode: str,
    status: str,
    evidence: str,
    action: str,
) -> None:
    rows.append(
        {
            "category": category,
            "check": check,
            "mode": mode,
            "status": status,
            "evidence": evidence,
            "action": action,
        }
    )


def build_zenodo_metadata() -> dict[str, object]:
    return {
        "title": TITLE,
        "upload_type": "dataset",
        "description": (
            "Reproducibility package for a Geo-GenAI map-generation reliability manuscript. "
            "The deposit is intended to include project-created scripts, derived CSV/JSON summaries, "
            "manuscript tables, figures, prompts, safety scans, and QA ledgers. Raw third-party datasets "
            "should be source-linked unless redistribution rights are confirmed."
        ),
        "creators": [
            {
                "name": "TODO: Author Name",
                "affiliation": "TODO: Affiliation",
                "orcid": "TODO: ORCID or remove",
            }
        ],
        "keywords": KEYWORDS,
        "license": "TODO: choose a code/data license after checking third-party constraints",
        "access_right": "open",
        "related_identifiers": [
            {
                "identifier": "TODO: manuscript DOI or preprint URL",
                "relation": "isSupplementTo",
                "resource_type": "publication-article",
            }
        ],
        "notes": "Do not upload raw third-party data unless redistribution rights are explicitly confirmed.",
    }


def build_citation_cff() -> str:
    lines = [
        "cff-version: 1.2.0",
        "message: Please cite this reproducibility package and the associated manuscript.",
        f"title: {TITLE}",
        "type: dataset",
        "authors:",
        "  - family-names: TODO",
        "    given-names: TODO",
        "    affiliation: TODO",
        "    orcid: TODO",
        "doi: TODO",
        "repository-code: TODO",
        "date-released: TODO",
        "keywords:",
    ]
    lines.extend(f"  - {keyword}" for keyword in KEYWORDS)
    lines += [
        "abstract: >-",
        "  Reproducibility package containing project-created code, derived evidence tables,",
        "  prompts, manifests, and QA ledgers for a cross-paradigm Geo-GenAI map-generation",
        "  reliability audit. Raw third-party datasets are source-linked unless redistribution",
        "  permissions are confirmed.",
        "",
    ]
    return "\n".join(lines)


def build_codemeta() -> dict[str, object]:
    return {
        "@context": "https://doi.org/10.5063/schema/codemeta-2.0",
        "@type": "SoftwareSourceCode",
        "name": "geo-genai-reliability",
        "description": "Scripts and derived evidence for a cross-paradigm Geo-GenAI map-generation reliability audit.",
        "codeRepository": "TODO: public repository URL",
        "issueTracker": "TODO: repository issue tracker URL or remove",
        "license": "TODO: choose license",
        "programmingLanguage": ["Python"],
        "runtimePlatform": "Python 3.10+",
        "softwareRequirements": [
            "geopandas",
            "matplotlib",
            "numpy",
            "pandas",
            "pillow",
            "pyogrio",
            "pyproj",
            "rasterio",
            "scikit-image",
            "scikit-learn",
            "shapely",
            "folium",
            "playwright",
        ],
        "author": [
            {
                "@type": "Person",
                "givenName": "TODO",
                "familyName": "TODO",
                "affiliation": "TODO",
            }
        ],
        "dateCreated": "2026-06-24",
        "version": "TODO: release tag",
        "identifier": "TODO: DOI",
    }


def build_checklist() -> str:
    return "\n".join(
        [
            "# DOI/Public Repository Release Checklist",
            "",
            "Use this checklist immediately before creating the public repository release or DOI deposit.",
            "",
            "## Metadata",
            "",
            "- [ ] Replace every `TODO` in `zenodo_metadata_draft.json`, `CITATION.cff`, and `codemeta_draft.json`.",
            "- [ ] Choose a repository license after confirming third-party data constraints.",
            "- [ ] Add the final public repository URL and release tag.",
            "- [ ] Add the final DOI after the archive is minted.",
            "- [ ] Link the release to the submitted manuscript, preprint, or article DOI when available.",
            "",
            "## Contents",
            "",
            "- [ ] Include project-created scripts, prompts, safety scans, derived CSV/JSON summaries, tables, figures, manifests, and QA ledgers.",
            "- [ ] Exclude raw third-party datasets unless redistribution rights are confirmed.",
            "- [ ] Exclude local model caches, raw model weights, private keys, shell histories, and machine-specific paths.",
            "- [ ] Include `DATA_SOURCES.md`, `environment_minimal.yml`, `environment_optional_embedding.yml`, and `reproducibility_manifest.csv`.",
            "- [ ] Include a note that local LLM/VLM generations are preserved as evidence and reruns may not be bit-reproducible.",
            "",
            "## Final Checks",
            "",
            "- [ ] Run `python3 manuscripts/q1_geo_genai_reliability/scripts/build_submission_package.py`.",
            "- [ ] Run `python3 manuscripts/q1_geo_genai_reliability/scripts/audit_manuscript_readiness.py`.",
            "- [ ] Run the residue sweep for local paths and removed conference/template artifacts.",
            "- [ ] Recompute SHA-256 manifest after the final file set is frozen.",
            "- [ ] Confirm whether the review upload should use anonymized repository links or a private reviewer link.",
            "",
        ]
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest_rows = read_csv(SUBMISSION_DIR / "reproducibility_manifest.csv")
    manifest_paths = [row.get("relative_path", "") for row in manifest_rows]
    data_sources = read_text(SUBMISSION_DIR / "DATA_SOURCES.md")
    release_plan = read_text(SUBMISSION_DIR / "reproducibility_release_plan.md")
    minimal_env = SUBMISSION_DIR / "environment_minimal.yml"
    optional_env = SUBMISSION_DIR / "environment_optional_embedding.yml"
    license_matrix = SUBMISSION_DIR / "release_license_audit/release_license_matrix.csv"
    license_audit = SUBMISSION_DIR / "release_license_audit/release_license_audit.md"
    license_rows = read_csv(license_matrix)
    release_skeleton = SUBMISSION_DIR / "public_release_skeleton/README_release_skeleton.md"
    release_file_map = SUBMISSION_DIR / "public_release_skeleton/RELEASE_FILE_MAP.csv"
    release_exclusions = SUBMISSION_DIR / "public_release_skeleton/THIRD_PARTY_EXCLUSIONS.md"
    release_license_note = SUBMISSION_DIR / "public_release_skeleton/LICENSE_DECISION_REQUIRED.md"

    ZENODO_OUT.write_text(json.dumps(build_zenodo_metadata(), indent=2) + "\n", encoding="utf-8")
    CITATION_OUT.write_text(build_citation_cff(), encoding="utf-8")
    CODEMETA_OUT.write_text(json.dumps(build_codemeta(), indent=2) + "\n", encoding="utf-8")
    CHECKLIST_OUT.write_text(build_checklist(), encoding="utf-8")

    rows: list[dict[str, str]] = []
    add_check(
        rows,
        "manifest",
        "Checksum manifest exists and is substantial",
        "automated",
        "pass" if len(manifest_rows) >= 900 and all(len(row.get("sha256", "")) == 64 for row in manifest_rows[:50]) else "fail",
        f"rows={len(manifest_rows)}",
        "Regenerate reproducibility_manifest.csv after final file freeze.",
    )
    raw_paths = [path for path in manifest_paths if path.startswith("data/raw/") or "/data/raw/" in path]
    add_check(
        rows,
        "redistribution",
        "Manifest excludes raw third-party datasets",
        "automated",
        "pass" if not raw_paths else "fail",
        f"raw paths tracked={len(raw_paths)}",
        "Remove raw third-party data from public deposit unless redistribution rights are confirmed.",
    )
    generated_map_paths = [path for path in manifest_paths if "generated_maps" in path or "/runs/" in path or "/repair_runs/" in path]
    add_check(
        rows,
        "redistribution",
        "Manifest excludes bulky generated-map/run folders",
        "automated",
        "pass" if not generated_map_paths else "fail",
        f"bulky paths tracked={len(generated_map_paths)}",
        "Represent bulky outputs with metrics, summaries, contact sheets, or restricted reviewer material.",
    )
    source_sections = ["SCGM / CSCMG", "MapGenerator", "Materials for Creating Maps by Artificial Intelligence"]
    missing_sources = [section for section in source_sections if section not in data_sources]
    add_check(
        rows,
        "data_sources",
        "Data-source manifest covers the three empirical artifact families",
        "automated",
        "pass" if not missing_sources else "fail",
        "missing=" + ",".join(missing_sources) if missing_sources else "all core sources documented",
        "Update DATA_SOURCES.md before release.",
    )
    add_check(
        rows,
        "environment",
        "Minimal and optional environment manifests exist",
        "automated",
        "pass" if minimal_env.exists() and optional_env.exists() else "fail",
        f"minimal={minimal_env.exists()}; optional={optional_env.exists()}",
        "Keep dependency files in the public release.",
    )
    add_check(
        rows,
        "metadata",
        "Release metadata draft files exist",
        "automated",
        "pass" if ZENODO_OUT.exists() and CITATION_OUT.exists() and CODEMETA_OUT.exists() and CHECKLIST_OUT.exists() else "fail",
        "zenodo, citation, codemeta, checklist",
        "Replace TODO fields before public deposit.",
    )
    add_check(
        rows,
        "policy",
        "Release plan records source-linking rule for third-party data",
        "automated",
        "pass" if "Do not redistribute large third-party datasets" in release_plan and "source URLs" in release_plan else "fail",
        "third-party data rule present" if release_plan else "release plan missing",
        "Keep this rule visible in the public repository README or release notes.",
    )
    add_check(
        rows,
        "license",
        "Release-license matrix separates author-controlled and third-party artifacts",
        "automated",
        "pass"
        if license_audit.exists()
        and len(license_rows) >= 8
        and any(row.get("artifact_family") == "project_created_code" for row in license_rows)
        and any(row.get("artifact_family") == "MapGenerator" and "source-link" in row.get("release_posture", "") for row in license_rows)
        and any(row.get("artifact_family") == "model_weights_and_checkpoints" and "Do not upload" in row.get("public_release_action", "") for row in license_rows)
        else "fail",
        f"rows={len(license_rows)}",
        "Use release_license_audit before choosing the final top-level code/data license.",
    )
    skeleton_text = read_text(release_skeleton)
    license_note_text = read_text(release_license_note)
    add_check(
        rows,
        "release_skeleton",
        "Public release skeleton separates included artifacts from third-party exclusions",
        "automated",
        "pass"
        if release_skeleton.exists()
        and release_file_map.exists()
        and release_exclusions.exists()
        and release_license_note.exists()
        and "Raw third-party datasets and cloned upstream repositories are source-linked" in skeleton_text
        and "No final top-level license is selected" in license_note_text
        else "fail",
        "public_release_skeleton present" if release_skeleton.exists() else "public_release_skeleton missing",
        "Keep the skeleton in the public repository root or release notes and replace only final DOI/license metadata after the route is chosen.",
    )
    add_check(
        rows,
        "manual_gate",
        "Final public repository URL",
        "manual",
        "manual",
        "Repository URL is intentionally TODO until the public release exists.",
        "Create release repository and update metadata immediately before submission.",
    )
    add_check(
        rows,
        "manual_gate",
        "Final DOI",
        "manual",
        "manual",
        "DOI is intentionally TODO until archive deposit is minted.",
        "Mint DOI through the chosen archive and update manuscript metadata.",
    )
    add_check(
        rows,
        "manual_gate",
        "License decision",
        "manual",
        "manual",
        "Final author-selected license is intentionally TODO; release-license audit now records third-party redistribution constraints.",
        "Choose top-level code/evidence license, keep third-party data source-linked/restricted as documented, then update metadata.",
    )
    write_csv(CSV_OUT, rows)

    automated = [row for row in rows if row["mode"] == "automated"]
    manual = [row for row in rows if row["mode"] == "manual"]
    lines = [
        "# Release Preflight",
        "",
        "This artifact prepares the public repository/DOI route without pretending that a DOI has already been minted.",
        "",
        f"- Automated checks passed: {sum(row['status'] == 'pass' for row in automated)}/{len(automated)}",
        f"- Manual release gates retained: {len(manual)}",
        f"- Manifest rows inspected: {len(manifest_rows)}",
        "",
        "## Checks",
        "",
        "| Category | Check | Mode | Status | Evidence | Action |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['category']} | {row['check']} | {row['mode']} | {row['status']} | {row['evidence']} | {row['action']} |"
        )
    lines += [
        "",
        "## Draft Metadata Files",
        "",
        "- `zenodo_metadata_draft.json`",
        "- `CITATION.cff`",
        "- `codemeta_draft.json`",
        "- `doi_release_checklist.md`",
        "",
    ]
    MD_OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {CSV_OUT.relative_to(ROOT)}")
    print(f"Wrote {MD_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
