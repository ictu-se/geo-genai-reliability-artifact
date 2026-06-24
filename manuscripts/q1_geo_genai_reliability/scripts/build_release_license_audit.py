#!/usr/bin/env python3
"""Build a release-license and redistribution audit for the submission package.

This is not legal advice and it does not choose the final license for the
author. It makes the release decision explicit: project-created code and
derived summaries can be licensed by the author, while raw third-party
datasets, upstream repositories, and model weights should be source-linked or
kept restricted unless the upstream terms are confirmed.
"""

from __future__ import annotations

import csv
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MS_DIR = ROOT / "manuscripts/q1_geo_genai_reliability"
OUT_DIR = MS_DIR / "submission/release_license_audit"
CSV_OUT = OUT_DIR / "release_license_matrix.csv"
MD_OUT = OUT_DIR / "release_license_audit.md"


REPOS = {
    "SCGM": ROOT / "data/repos/SCGM",
    "MapGenerator": ROOT / "data/repos/MapGenerator",
    "Materials-for-Creating-maps-by-Artificial-Intelligence": ROOT
    / "data/repos/Materials-for-Creating-maps-by-Artificial-Intelligence",
    "generative-ai-mapmaking": ROOT / "data/repos/generative-ai-mapmaking",
}


def git_text(repo: Path, args: list[str]) -> str:
    try:
        return subprocess.check_output(["git", "-C", str(repo), *args], text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def detect_license(repo: Path) -> tuple[str, str]:
    license_files = sorted(
        [path for path in repo.glob("LICENSE*") if path.is_file()]
        + [path for path in repo.glob("COPYING*") if path.is_file()]
    )
    if license_files:
        text = read(license_files[0]).lower()
        if "cc0 1.0 universal" in text:
            return "CC0-1.0", str(license_files[0].relative_to(ROOT))
        if "attribution 4.0 international" in text or "creative commons attribution 4.0" in text:
            return "CC-BY-4.0", str(license_files[0].relative_to(ROOT))
        if "mit license" in text:
            return "MIT", str(license_files[0].relative_to(ROOT))
        if "apache license" in text:
            return "Apache-2.0", str(license_files[0].relative_to(ROOT))
        return "license_file_present_unclassified", str(license_files[0].relative_to(ROOT))

    readme = read(repo / "README.md")
    lower = readme.lower()
    if "non-commercial use only" in lower or "research preview" in lower:
        return "research-preview-noncommercial-readme", str((repo / "README.md").relative_to(ROOT))
    if readme:
        return "no-license-file-readme-only", str((repo / "README.md").relative_to(ROOT))
    return "not_found", ""


def repo_row(name: str, repo: Path) -> dict[str, str]:
    license_id, evidence = detect_license(repo)
    remote = git_text(repo, ["remote", "get-url", "origin"]) if repo.exists() else ""
    commit = git_text(repo, ["rev-parse", "HEAD"]) if repo.exists() else ""
    if license_id == "CC0-1.0":
        posture = "source-link or include only if third-party embedded data rights remain compatible"
        release_action = "Do not assume all nested data are rights-cleared; include attribution/source note even when CC0 applies."
    elif license_id == "CC-BY-4.0":
        posture = "source-link raw data; derived metrics may be released with attribution notes"
        release_action = "Retain upstream attribution; do not redistribute bulky raw tiles unless final license review confirms scope."
    elif license_id == "research-preview-noncommercial-readme":
        posture = "source-link only for raw data and upstream content"
        release_action = "Exclude raw images/captions from open DOI package; release only derived audit summaries and reconstruction instructions."
    else:
        posture = "source-link only until license terms are confirmed"
        release_action = "Exclude raw upstream content from public package; retain URL/commit/access notes."
    return {
        "artifact_family": name,
        "artifact_scope": "upstream repository and raw/source artifacts",
        "detected_license_or_terms": license_id,
        "evidence": evidence,
        "upstream_remote": remote,
        "upstream_commit": commit,
        "release_posture": posture,
        "public_release_action": release_action,
    }


def release_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = [
        {
            "artifact_family": "project_created_code",
            "artifact_scope": "manuscript scripts, experiment scripts, prompt builders, audit builders",
            "detected_license_or_terms": "author-controlled",
            "evidence": "manuscripts/q1_geo_genai_reliability/scripts; experiments/*/scripts",
            "upstream_remote": "",
            "upstream_commit": "",
            "release_posture": "choose an OSI-compatible code license for project-created code",
            "public_release_action": "Recommended action: add a top-level LICENSE for project-created code and note that third-party data are excluded/source-linked.",
        },
        {
            "artifact_family": "project_created_manuscript_evidence",
            "artifact_scope": "derived CSV/JSON summaries, tables, figures, contact sheets, QA ledgers, manifests",
            "detected_license_or_terms": "author-controlled-with-third-party-context",
            "evidence": "submission/reproducibility_manifest.csv; tables; figures; derived outputs",
            "upstream_remote": "",
            "upstream_commit": "",
            "release_posture": "release derived summaries openly when they do not embed restricted upstream data",
            "public_release_action": "Recommended action: license derived metadata/tables separately from raw third-party data; use source links for reconstructing restricted inputs.",
        },
    ]
    rows.extend(repo_row(name, repo) for name, repo in REPOS.items())
    rows.extend(
        [
            {
                "artifact_family": "local_llm_vlm_outputs",
                "artifact_scope": "generated code, repair attempts, VLM reviews, local model names, logs",
                "detected_license_or_terms": "model-output-policy-dependent",
                "evidence": "experiments/05_choropleth_reliability_benchmark/outputs; submission/evaluator_reliability",
                "upstream_remote": "",
                "upstream_commit": "",
                "release_posture": "release as study evidence if model/output terms permit",
                "public_release_action": "Preserve prompts, model names, timestamps, and safety scans; recheck local model licenses before public upload.",
            },
            {
                "artifact_family": "model_weights_and_checkpoints",
                "artifact_scope": "Stable Diffusion, CLIP/SigLIP, Ollama/VLM models, SCGM checkpoints",
                "detected_license_or_terms": "not_redistributed",
                "evidence": "release plan excludes local model caches and weights",
                "upstream_remote": "",
                "upstream_commit": "",
                "release_posture": "source-link or documented acquisition only",
                "public_release_action": "Do not upload weights/checkpoints unless the license explicitly permits redistribution.",
            },
            {
                "artifact_family": "double_anonymous_review_package",
                "artifact_scope": "blinded manuscript, supplement manifests, reviewer-facing summaries",
                "detected_license_or_terms": "review-only",
                "evidence": "submission/blinded_main_manuscript.md; submission/blinded_compact_main_manuscript.md",
                "upstream_remote": "",
                "upstream_commit": "",
                "release_posture": "keep blinded artifacts separate from non-blinded DOI metadata",
                "public_release_action": "Upload blinded files to review portal; add non-blinded authors/DOI/license only after review-route policy is confirmed.",
            },
        ]
    )
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def build_markdown(rows: list[dict[str, str]]) -> str:
    source_link = [row for row in rows if "source-link" in row["release_posture"]]
    open_candidate = [row for row in rows if row["detected_license_or_terms"].startswith("author-controlled")]
    lines = [
        "# Release License and Redistribution Audit",
        "",
        "This audit converts the remaining license gate into a concrete release matrix. It is not legal advice and does not replace the final author/license decision before DOI deposit.",
        "",
        "## Summary",
        "",
        f"- Release rows: {len(rows)}",
        f"- Author-controlled rows: {len(open_candidate)}",
        f"- Source-link/restricted rows: {len(source_link)}",
        "- Final license decision remains manual until the public repository and DOI metadata are created.",
        "",
        "## Release Matrix",
        "",
        "| Artifact family | Terms | Release posture | Public release action | Evidence |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| {artifact_family} | {detected_license_or_terms} | {release_posture} | {public_release_action} | {evidence} |".format(
                artifact_family=row["artifact_family"].replace("|", "/"),
                detected_license_or_terms=row["detected_license_or_terms"].replace("|", "/"),
                release_posture=row["release_posture"].replace("|", "/"),
                public_release_action=row["public_release_action"].replace("|", "/"),
                evidence=row["evidence"].replace("|", "/"),
            )
        )
    lines += [
        "",
        "## Recommended Release Posture",
        "",
        "1. Add a top-level license for project-created code only after the author chooses the final license.",
        "2. Release derived CSV/JSON summaries, tables, scripts, prompts, QA ledgers, and manifests as the public reproducibility core.",
        "3. Exclude or source-link raw SCGM, MapGenerator, choropleth, map-sheet, and model-weight artifacts unless the final license review confirms redistribution rights.",
        "4. Keep blinded review files separate from non-blinded repository DOI, author metadata, and license metadata.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    rows = release_rows()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(CSV_OUT, rows)
    MD_OUT.write_text(build_markdown(rows), encoding="utf-8")
    print(f"Wrote {CSV_OUT.relative_to(ROOT)}")
    print(f"Wrote {MD_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
