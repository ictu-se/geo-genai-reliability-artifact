#!/usr/bin/env python3
"""Preflight checks for the staged Zenodo release package."""

from __future__ import annotations

import csv
import re
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MS_DIR = ROOT / "manuscripts/q1_geo_genai_reliability"
SUBMISSION_DIR = MS_DIR / "submission"
STAGE_ROOT = SUBMISSION_DIR / "zenodo_release_staging"
PACKAGE_NAME = "geo_genai_reliability_zenodo"
PACKAGE_DIR = STAGE_ROOT / PACKAGE_NAME
ZIP_OUT = STAGE_ROOT / f"{PACKAGE_NAME}.zip"
OUT_DIR = SUBMISSION_DIR / "release_preflight"
CSV_OUT = OUT_DIR / "zenodo_release_preflight.csv"
MD_OUT = OUT_DIR / "zenodo_release_preflight.md"


TEXT_SUFFIXES = {
    ".bib",
    ".cff",
    ".csv",
    ".json",
    ".md",
    ".mmd",
    ".py",
    ".tex",
    ".txt",
    ".yml",
    ".yaml",
}

FORBIDDEN_REL_PATTERNS = [
    re.compile(r"(^|/)data/"),
    re.compile(r"(^|/)runs/"),
    re.compile(r"(^|/)repair_runs/"),
    re.compile(r"(^|/)generated_maps/"),
    re.compile(r"(^|/)generated_code/"),
    re.compile(r"(^|/)generated_code_repaired/"),
    re.compile(r"(^|/)__pycache__/"),
    re.compile(r"(^|/)interact_template/"),
]

FORBIDDEN_TEXT_PATTERNS = [
    "/" + "Users/",
    "nguyen" + "thevinh",
    "IC" + "TA",
    "Over" + "leaf",
    "LN" + "CS",
    "ll" + "ncs",
    "sp" + "lncs",
]

ARCHIVE_OR_WEIGHT_SUFFIXES = {".zip", ".tar", ".gz", ".7z", ".pth", ".pt", ".ckpt", ".safetensors"}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def add(rows: list[dict[str, str]], check: str, status: str, evidence: str, action: str) -> None:
    rows.append({"check": check, "status": status, "evidence": evidence, "action": action})


def staged_files() -> list[Path]:
    if not PACKAGE_DIR.exists():
        return []
    return sorted(path for path in PACKAGE_DIR.rglob("*") if path.is_file())


def relative(path: Path) -> str:
    return path.relative_to(PACKAGE_DIR).as_posix()


def text_files(files: list[Path]) -> list[Path]:
    return [path for path in files if path.suffix.lower() in TEXT_SUFFIXES]


def build_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    files = staged_files()
    add(
        rows,
        "staged directory exists",
        "pass" if PACKAGE_DIR.exists() and files else "fail",
        f"files={len(files)}; path={PACKAGE_DIR.relative_to(ROOT) if PACKAGE_DIR.exists() else PACKAGE_DIR}",
        "Run stage_zenodo_release.py before preflight.",
    )

    manifest = PACKAGE_DIR / "ZENODO_FILE_MANIFEST.csv"
    add(
        rows,
        "staged manifest exists",
        "pass" if manifest.exists() and manifest.stat().st_size > 0 else "fail",
        f"bytes={manifest.stat().st_size if manifest.exists() else 0}",
        "Regenerate staging so every file has a checksum row.",
    )

    rel_paths = [relative(path) for path in files]
    forbidden_paths = [rel for rel in rel_paths if any(pattern.search(rel) for pattern in FORBIDDEN_REL_PATTERNS)]
    add(
        rows,
        "raw data and bulky run folders excluded",
        "pass" if not forbidden_paths else "fail",
        "; ".join(forbidden_paths[:12]) or "no forbidden release paths",
        "Remove raw data, generated maps, generated code folders, run folders, and caches from Zenodo staging.",
    )

    archive_or_weights = [rel for rel in rel_paths if Path(rel).suffix.lower() in ARCHIVE_OR_WEIGHT_SUFFIXES]
    add(
        rows,
        "archives and model weights excluded",
        "pass" if not archive_or_weights else "fail",
        "; ".join(archive_or_weights[:12]) or "no archives/checkpoints in staged package",
        "Do not upload nested archives or model weights unless explicitly cleared.",
    )

    text_hits: list[str] = []
    todo_hits: list[str] = []
    for path in text_files(files):
        text = read_text(path)
        rel = relative(path)
        for pattern in FORBIDDEN_TEXT_PATTERNS:
            if pattern in text:
                text_hits.append(f"{rel}: {pattern}")
                break
        if "TODO" in text and rel.startswith("manuscripts/q1_geo_genai_reliability/submission/release_preflight/"):
            todo_hits.append(rel)
    add(
        rows,
        "no local path or removed-template residue",
        "pass" if not text_hits else "fail",
        "; ".join(text_hits[:12]) or "no forbidden text residue",
        "Sanitize local paths and removed-template residue before upload.",
    )
    add(
        rows,
        "final Zenodo metadata has no TODO placeholders",
        "warning" if todo_hits else "pass",
        "; ".join(todo_hits[:12]) or "no TODO placeholders in release metadata",
        "Replace author, license, DOI, repository, and ORCID placeholders before final deposit.",
    )

    if ZIP_OUT.exists():
        try:
            with zipfile.ZipFile(ZIP_OUT) as zf:
                bad_zip = zf.testzip()
                zip_count = len(zf.infolist())
            status = "pass" if bad_zip is None else "fail"
            evidence = f"entries={zip_count}; bad={bad_zip}"
        except zipfile.BadZipFile:
            status = "fail"
            evidence = "bad zip file"
    else:
        status = "fail"
        evidence = "zip missing"
    add(
        rows,
        "zip archive readable",
        status,
        evidence,
        "Regenerate stage zip if unreadable.",
    )

    return rows


def write_csv(rows: list[dict[str, str]]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with CSV_OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["check", "status", "evidence", "action"])
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(rows: list[dict[str, str]]) -> None:
    failures = [row for row in rows if row["status"] == "fail"]
    warnings = [row for row in rows if row["status"] == "warning"]
    lines = [
        "# Zenodo Release Preflight",
        "",
        f"- staged package: `{PACKAGE_DIR.relative_to(ROOT)}`",
        f"- zip archive: `{ZIP_OUT.relative_to(ROOT)}`",
        f"- failures: {len(failures)}",
        f"- warnings: {len(warnings)}",
        "",
        "| Check | Status | Evidence | Action |",
        "|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| {check} | {status} | {evidence} | {action} |".format(
                check=row["check"].replace("|", "/"),
                status=row["status"],
                evidence=row["evidence"].replace("|", "/"),
                action=row["action"].replace("|", "/"),
            )
        )
    lines += [
        "",
        "## Interpretation",
        "",
        "A warning on TODO metadata is acceptable for a draft staging package, but it must be resolved before a final Zenodo deposit.",
        "",
    ]
    MD_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    rows = build_rows()
    write_csv(rows)
    write_markdown(rows)
    print(f"Wrote {CSV_OUT.relative_to(ROOT)}")
    print(f"Wrote {MD_OUT.relative_to(ROOT)}")
    failures = [row for row in rows if row["status"] == "fail"]
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
