#!/usr/bin/env python3
"""Build a checksum/provenance manifest for the manuscript evidence package."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MS_DIR = ROOT / "manuscripts/q1_geo_genai_reliability"
OUT_DIR = MS_DIR / "submission"
CSV_OUT = OUT_DIR / "reproducibility_manifest.csv"
MD_OUT = OUT_DIR / "reproducibility_manifest.md"


GROUPS = [
    ("manuscript", MS_DIR / "draft", ["*.md"]),
    ("tables", MS_DIR / "tables", ["table_*.csv", "manuscript_tables.md"]),
    ("figures", MS_DIR / "figures", ["*.png", "*.jpg", "*.md", "*.mmd"]),
    ("notes", MS_DIR / "notes", ["*.md"]),
    ("protocols", MS_DIR / "protocols", ["*.md", "*.json"]),
    ("scripts", MS_DIR / "scripts", ["*.py"]),
    ("submission", OUT_DIR, ["*.md", "*.csv", "*.bib", "*.yml", "*.yaml", "*.tex", "*.pdf", "*.html"]),
    ("submission_nested", OUT_DIR, ["**/*.md", "**/*.csv", "**/*.json", "**/*.yml", "**/*.yaml", "**/*.tex", "**/*.bib", "**/*.pdf", "**/*.html", "**/Makefile"]),
    ("dataset_audit", ROOT / "experiments/00_dataset_reproducibility_audit", ["README.md", "outputs/*.csv", "outputs/*.json", "outputs/*.md"]),
    ("choropleth_linter", ROOT / "experiments/01_choropleth_llm_linter", ["README.md", "inputs/*.json", "outputs/*.csv", "outputs/*.json", "outputs/*.md"]),
    ("mapgenerator_audit", ROOT / "experiments/02_mapgenerator_image_text_audit", ["README.md", "outputs/*.csv", "outputs/*.json", "outputs/*.md"]),
    ("scgm_reproduction", ROOT / "experiments/03_scgm_subset_reproduction", ["README.md", "outputs/*.csv", "outputs/*.json", "outputs/*.md"]),
    ("geo_faithfulness", ROOT / "experiments/04_geo_faithfulness_evaluator", ["README.md", "inputs/*.json", "outputs/**/*.csv", "outputs/**/*.json", "notes/*.md"]),
    ("choropleth_benchmark", ROOT / "experiments/05_choropleth_reliability_benchmark", ["README.md", "inputs/*.json", "outputs/**/*.csv", "outputs/**/*.json", "outputs/**/*.md"]),
]

EXCLUDE_PARTS = {
    "__pycache__",
    ".DS_Store",
    "rendered",
    "generated_maps",
    "runs",
    "repair_runs",
    "validator_reference_runs",
    "zenodo_release_staging",
}

EXCLUDE_NAMES = {
    "submission_package_audit.md",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def csv_rows(path: Path) -> str:
    if path.suffix.lower() != ".csv":
        return ""
    try:
        with path.open(newline="", encoding="utf-8") as f:
            return str(max(0, sum(1 for _ in csv.reader(f)) - 1))
    except UnicodeDecodeError:
        return ""


def artifact_role(path: Path, group: str) -> str:
    rel = path.relative_to(ROOT).as_posix()
    name = path.name
    if name.startswith("table_"):
        return "manuscript evidence table"
    if "summary" in name and path.suffix in {".csv", ".json"}:
        return "machine-readable summary"
    if "metrics" in name or "scores" in name:
        return "metric-level evidence"
    if "manifest" in name:
        return "reproducibility manifest"
    if "audit" in name:
        return "audit report or ledger"
    if "review" in name:
        return "review/evaluator evidence"
    if rel.endswith(".py"):
        return "rebuild script"
    if rel.endswith(".tex") or rel.endswith(".pdf"):
        return "LaTeX manuscript artifact"
    if group == "figures":
        return "manuscript figure or figure index"
    return "supporting artifact"


def include(path: Path) -> bool:
    if not path.is_file():
        return False
    if any(part in EXCLUDE_PARTS for part in path.parts):
        return False
    if path.name in EXCLUDE_NAMES:
        return False
    if path == CSV_OUT or path == MD_OUT:
        return False
    return True


def collect_paths() -> list[tuple[str, Path]]:
    seen: set[Path] = set()
    paths: list[tuple[str, Path]] = []
    for group, base, patterns in GROUPS:
        if not base.exists():
            continue
        for pattern in patterns:
            for path in sorted(base.glob(pattern)):
                resolved = path.resolve()
                if resolved in seen or not include(path):
                    continue
                seen.add(resolved)
                paths.append((group, path))
    return paths


def build_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for group, path in collect_paths():
        rel = path.relative_to(ROOT).as_posix()
        rows.append(
            {
                "artifact_group": group,
                "relative_path": rel,
                "suffix": path.suffix.lower(),
                "bytes": str(path.stat().st_size),
                "sha256": sha256(path),
                "csv_rows": csv_rows(path),
                "role": artifact_role(path, group),
            }
        )
    rows.sort(key=lambda row: (row["artifact_group"], row["relative_path"]))
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def build_report(rows: list[dict[str, str]]) -> str:
    group_counts: dict[str, int] = {}
    total_bytes = 0
    for row in rows:
        group_counts[row["artifact_group"]] = group_counts.get(row["artifact_group"], 0) + 1
        total_bytes += int(row["bytes"])
    lines = [
        "# Reproducibility Manifest",
        "",
        "This manifest records review-package and experiment-derived artifacts with file sizes and SHA-256 checksums. It excludes raw third-party datasets, generated map directories, and bulky render folders unless represented by derived summaries.",
        "",
        "## Summary",
        "",
        f"- manifest rows: {len(rows)}",
        f"- total manifest-tracked bytes: {total_bytes}",
        f"- checksum algorithm: SHA-256",
        "",
        "## Artifact Groups",
        "",
        "| Group | Files |",
        "|---|---:|",
    ]
    for group, count in sorted(group_counts.items()):
        lines.append(f"| {group} | {count} |")
    lines += [
        "",
        "## Rebuild Note",
        "",
        "Run `python3 manuscripts/q1_geo_genai_reliability/scripts/build_submission_package.py` before regenerating this manifest so derived tables, manuscript variants, and submission ledgers are current.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    rows = build_rows()
    write_csv(CSV_OUT, rows)
    MD_OUT.write_text(build_report(rows), encoding="utf-8")
    print(f"Wrote {CSV_OUT.relative_to(ROOT)}")
    print(f"Wrote {MD_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
