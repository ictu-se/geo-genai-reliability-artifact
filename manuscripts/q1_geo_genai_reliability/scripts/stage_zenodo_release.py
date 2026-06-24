#!/usr/bin/env python3
"""Stage a conservative Zenodo-ready release bundle.

The staged bundle is intentionally source-linked: it includes project-created
code, manuscript artifacts, derived tabular/JSON evidence, release metadata, and
runbooks, while excluding raw third-party data, cloned upstream repositories,
model weights, bulky run folders, and local machine paths.
"""

from __future__ import annotations

import csv
import hashlib
import shutil
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MS_DIR = ROOT / "manuscripts/q1_geo_genai_reliability"
SUBMISSION_DIR = MS_DIR / "submission"
STAGE_ROOT = SUBMISSION_DIR / "zenodo_release_staging"
PACKAGE_NAME = "geo_genai_reliability_zenodo"
PACKAGE_DIR = STAGE_ROOT / PACKAGE_NAME
ZIP_OUT = STAGE_ROOT / f"{PACKAGE_NAME}.zip"
MANIFEST_OUT = PACKAGE_DIR / "ZENODO_FILE_MANIFEST.csv"
README_OUT = PACKAGE_DIR / "README_ZENODO.md"


INCLUDE_PATTERNS = [
    "experiments/README.md",
    "experiments/*/README.md",
    "experiments/*/scripts/*.py",
    "experiments/05_choropleth_reliability_benchmark/inputs/*.json",
    "experiments/*/outputs/*.csv",
    "experiments/*/outputs/*.json",
    "experiments/*/outputs/*.md",
    "experiments/03_scgm_subset_reproduction/outputs/scgm_*_report.md",
    "experiments/05_choropleth_reliability_benchmark/outputs/scores/**/*.csv",
    "experiments/05_choropleth_reliability_benchmark/outputs/scores/**/*.json",
    "experiments/05_choropleth_reliability_benchmark/outputs/scores/**/*.md",
    "manuscripts/q1_geo_genai_reliability/README.md",
    "manuscripts/q1_geo_genai_reliability/draft/*.md",
    "manuscripts/q1_geo_genai_reliability/figures/*.mmd",
    "manuscripts/q1_geo_genai_reliability/figures/*.md",
    "manuscripts/q1_geo_genai_reliability/figures/*.png",
    "manuscripts/q1_geo_genai_reliability/protocols/*.md",
    "manuscripts/q1_geo_genai_reliability/scripts/*.py",
    "manuscripts/q1_geo_genai_reliability/tables/*.csv",
    "manuscripts/q1_geo_genai_reliability/tables/*.md",
    "manuscripts/q1_geo_genai_reliability/notes/manuscript_readiness_audit.md",
    "manuscripts/q1_geo_genai_reliability/notes/manuscript_consistency_audit.md",
    "manuscripts/q1_geo_genai_reliability/notes/status_dashboard.md",
    "manuscripts/q1_geo_genai_reliability/notes/page_budget_audit.md",
    "manuscripts/q1_geo_genai_reliability/notes/main_text_compression_plan.md",
    "manuscripts/q1_geo_genai_reliability/submission/*.md",
    "manuscripts/q1_geo_genai_reliability/submission/*.csv",
    "manuscripts/q1_geo_genai_reliability/submission/*.bib",
    "manuscripts/q1_geo_genai_reliability/submission/*.yml",
    "manuscripts/q1_geo_genai_reliability/submission/claim_evidence_crosswalk/*",
    "manuscripts/q1_geo_genai_reliability/submission/cross_paradigm/*",
    "manuscripts/q1_geo_genai_reliability/submission/evaluator_reliability/*",
    "manuscripts/q1_geo_genai_reliability/submission/evidence_map/*",
    "manuscripts/q1_geo_genai_reliability/submission/human_validation_panels/*.csv",
    "manuscripts/q1_geo_genai_reliability/submission/human_validation_panels/*.json",
    "manuscripts/q1_geo_genai_reliability/submission/human_validation_panels/*.md",
    "manuscripts/q1_geo_genai_reliability/submission/journal_style_preflight/*",
    "manuscripts/q1_geo_genai_reliability/submission/latex/README_latex.md",
    "manuscripts/q1_geo_genai_reliability/submission/latex/main.tex",
    "manuscripts/q1_geo_genai_reliability/submission/latex/main.pdf",
    "manuscripts/q1_geo_genai_reliability/submission/latex/main.bbl",
    "manuscripts/q1_geo_genai_reliability/submission/latex/references.bib",
    "manuscripts/q1_geo_genai_reliability/submission/public_release_skeleton/*",
    "manuscripts/q1_geo_genai_reliability/submission/q1_submission_gate_tracker/*",
    "manuscripts/q1_geo_genai_reliability/submission/release_license_audit/*",
    "manuscripts/q1_geo_genai_reliability/submission/release_preflight/*",
    "manuscripts/q1_geo_genai_reliability/submission/repair_model_suite/*",
    "manuscripts/q1_geo_genai_reliability/submission/reviewer_prebuttal_audit/*",
    "manuscripts/q1_geo_genai_reliability/submission/scgm_official_reproduction_audit/*",
    "manuscripts/q1_geo_genai_reliability/submission/scgm_official_reproduction_contract/*.csv",
    "manuscripts/q1_geo_genai_reliability/submission/scgm_official_reproduction_contract/*.md",
    "manuscripts/q1_geo_genai_reliability/submission/scgm_official_reproduction_contract/*.yml",
]

EXCLUDE_PARTS = {
    "__pycache__",
    ".DS_Store",
    ".git",
    "data",
    "runs",
    "repair_runs",
    "rendered",
    "generated_maps",
    "validator_reference_runs",
    "generated_code",
    "generated_code_repaired",
    "interact_template",
    "zenodo_release_staging",
}

EXCLUDE_SUFFIXES = {".zip", ".tar", ".gz", ".7z", ".pth", ".pt", ".ckpt", ".safetensors"}
EXCLUDE_NAMES = {"zenodo_release_preflight.csv", "zenodo_release_preflight.md"}
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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def include(path: Path) -> bool:
    if not path.is_file():
        return False
    rel_parts = path.relative_to(ROOT).parts
    if any(part in EXCLUDE_PARTS for part in rel_parts):
        return False
    if path.suffix.lower() in EXCLUDE_SUFFIXES:
        return False
    if path.name in EXCLUDE_NAMES:
        return False
    return True


def collect_files() -> list[Path]:
    seen: set[Path] = set()
    files: list[Path] = []
    for pattern in INCLUDE_PATTERNS:
        for path in sorted(ROOT.glob(pattern)):
            if not include(path):
                continue
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            files.append(path)
    return files


def copy_files(files: list[Path]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for src in files:
        rel = src.relative_to(ROOT)
        dst = PACKAGE_DIR / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.suffix.lower() in TEXT_SUFFIXES:
            text = src.read_text(encoding="utf-8", errors="replace")
            text = text.replace(str(ROOT), "[REPOSITORY ROOT]")
            text = text.replace(str(Path.home()), "[HOME]")
            dst.write_text(text, encoding="utf-8")
            shutil.copystat(src, dst)
        else:
            shutil.copy2(src, dst)
        rows.append(
            {
                "relative_path": rel.as_posix(),
                "bytes": str(dst.stat().st_size),
                "sha256": sha256(dst),
            }
        )
    return rows


def write_manifest(rows: list[dict[str, str]]) -> None:
    with MANIFEST_OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["relative_path", "bytes", "sha256"])
        writer.writeheader()
        writer.writerows(rows)


def build_readme(rows: list[dict[str, str]]) -> str:
    return "\n".join(
        [
            "# Geo-GenAI Reliability Zenodo Release Staging",
            "",
            "This staged package contains project-created code, manuscript artifacts, derived evidence tables, release metadata, and reproducibility documentation for the Geo-GenAI reliability manuscript.",
            "",
            "## Included",
            "",
            "- Experiment and manuscript-building scripts.",
            "- Derived CSV, JSON, Markdown, BibTeX, LaTeX, and PDF artifacts.",
            "- Manuscript tables, figures, protocols, evidence ledgers, release metadata drafts, and runbooks.",
            "- Human-validation packet templates and evaluator-reliability ledgers.",
            "",
            "## Excluded",
            "",
            "- Raw third-party datasets and cloned upstream repositories.",
            "- Model checkpoints, local model caches, and generated map/run folders.",
            "- Local machine-specific config files and bulky render directories.",
            "- Contact sheets or derived images that may embed third-party raw imagery unless separately cleared.",
            "",
            "## Rebuild",
            "",
            "Use `manuscripts/q1_geo_genai_reliability/submission/reproduction_runbook.md` for the deterministic rebuild path. Source third-party datasets via `DATA_SOURCES.md`; they are not redistributed in this package.",
            "",
            "## Manifest",
            "",
            f"- Files staged: {len(rows)}",
            "- File manifest: `ZENODO_FILE_MANIFEST.csv`",
            "- Checksum: SHA-256",
            "",
            "Run `python3 manuscripts/q1_geo_genai_reliability/scripts/preflight_zenodo_release.py` before uploading.",
            "",
        ]
    )


def zip_package() -> None:
    if ZIP_OUT.exists():
        ZIP_OUT.unlink()
    with zipfile.ZipFile(ZIP_OUT, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(PACKAGE_DIR.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(STAGE_ROOT))


def main() -> None:
    if PACKAGE_DIR.exists():
        shutil.rmtree(PACKAGE_DIR)
    PACKAGE_DIR.mkdir(parents=True, exist_ok=True)
    files = collect_files()
    rows = copy_files(files)
    README_OUT.write_text(build_readme(rows), encoding="utf-8")
    rows.append(
        {
            "relative_path": "README_ZENODO.md",
            "bytes": str(README_OUT.stat().st_size),
            "sha256": sha256(README_OUT),
        }
    )
    write_manifest(rows)
    zip_package()
    print(f"Staged {len(rows)} files in {PACKAGE_DIR.relative_to(ROOT)}")
    print(f"Wrote {MANIFEST_OUT.relative_to(ROOT)}")
    print(f"Wrote {ZIP_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
