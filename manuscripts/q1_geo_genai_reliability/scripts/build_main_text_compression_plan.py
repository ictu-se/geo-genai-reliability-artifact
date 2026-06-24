#!/usr/bin/env python3
"""Build a concrete main-text compression plan for the Q1 manuscript."""

from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MS_DIR = ROOT / "manuscripts/q1_geo_genai_reliability"
DRAFT = MS_DIR / "draft/manuscript_draft.md"
OUT_DIR = MS_DIR / "submission"
NOTES_DIR = MS_DIR / "notes"

TARGET_WORDS = 9500
TARGET_MAIN_TABLES = 6
TARGET_MAIN_FIGURES = 4

COMPACT_MAIN_TABLES = {
    "table_01_dataset_inventory": "merge with Table 2 or keep as compact artifact inventory",
    "table_05c_scgm_retrieval_comparison": "SCGM generated-output baseline comparison",
    "table_13_choropleth_model_mode_summary": "Choropleth benchmark model-mode aggregate",
    "table_16_screenshot_level_choropleth_qa": "Screenshot-level choropleth artifact QA",
    "table_19_iterative_validator_repair": "Iterative validator-gated repair sweep",
    "table_23_cross_paradigm_reliability_summary": "Cross-paradigm reliability summary",
}

COMPACT_MAIN_FIGURES = {
    "Figure 1": "Cross-paradigm artifact chain",
    "Figure 5": "Choropleth benchmark score bars",
    "Figure 7": "Screenshot-level QA bar chart",
    "Figure 9": "SCGM generated-output baseline comparison",
}

SECTION_TARGETS = {
    "Abstract": 240,
    "1. Introduction": 500,
    "2. Background and Related Work": 1000,
    "3. Conceptual Framework: Generated Maps as Artifact Chains": 700,
    "4. Data and Artifacts": 500,
    "5. Methods": 1550,
    "6. Results": 2400,
    "7. Discussion": 1200,
    "8. Limitations": 450,
    "9. Additional Strengthening Experiments": 80,
    "10. Conclusion": 100,
    "Acknowledgments": 30,
    "Declaration of Interest Statement": 40,
    "Data Availability Statement": 90,
    "Software Availability Statement": 80,
    "References": 470,
}


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


def section_word_counts() -> list[dict[str, str]]:
    text = DRAFT.read_text(encoding="utf-8")
    chunks = re.split(r"\n(?=## )", text)
    rows = []
    for chunk in chunks:
        if not chunk.strip():
            continue
        heading = chunk.splitlines()[0].strip("# ")
        current = len(chunk.split())
        target = SECTION_TARGETS.get(heading, current)
        rows.append(
            {
                "Section": heading,
                "Current words": str(current),
                "Target words": str(target),
                "Cut words": str(max(0, current - target)),
                "Action": action_for_section(heading, current, target),
            }
        )
    return rows


def action_for_section(heading: str, current: int, target: int) -> str:
    if current <= target:
        return "keep"
    if heading == "5. Methods":
        return "move procedural detail and prompt mechanics to supplement; keep contracts and scoring logic"
    if heading == "6. Results":
        return "retain headline metrics and cross-paradigm contrasts; move per-model/per-case narration to supplement"
    if heading == "2. Background and Related Work":
        return "compress literature examples into paradigm paragraphs and Table 17 supplement"
    if heading == "7. Discussion":
        return "merge repeated implications and keep reliability-matrix interpretation"
    if heading == "3. Conceptual Framework: Generated Maps as Artifact Chains":
        return "shorten definitions after first use; rely on Figure 1"
    return "tighten prose"


def display_rows() -> list[dict[str, str]]:
    split = read_csv(OUT_DIR / "main_supplement_split.csv")
    rows = []
    for row in split:
        artifact_id = row["artifact_id"]
        keep = (
            row["artifact_type"] == "table"
            and artifact_id in COMPACT_MAIN_TABLES
            or row["artifact_type"] == "figure"
            and artifact_id in COMPACT_MAIN_FIGURES
        )
        if row["artifact_type"] == "table":
            role = COMPACT_MAIN_TABLES.get(artifact_id, "supplement in compact plan")
        else:
            role = COMPACT_MAIN_FIGURES.get(artifact_id, "supplement in compact plan")
        rows.append(
            {
                "artifact_type": row["artifact_type"],
                "artifact_id": artifact_id,
                "file": row["file"],
                "compact_placement": "main_text" if keep else "supplement",
                "role": role,
            }
        )
    return rows


def estimate_pages(words: int, tables: int, figures: int) -> dict[str, float]:
    text_low = words / 550.0
    text_mid = words / 500.0
    text_high = words / 450.0
    display_low = tables * 0.45 + figures * 0.55
    display_mid = tables * 0.60 + figures * 0.70
    display_high = tables * 0.80 + figures * 0.95
    return {
        "text_low": round(text_low, 1),
        "text_mid": round(text_mid, 1),
        "text_high": round(text_high, 1),
        "display_low": round(display_low, 1),
        "display_mid": round(display_mid, 1),
        "display_high": round(display_high, 1),
        "total_low": round(text_low + display_low + 1.5, 1),
        "total_mid": round(text_mid + display_mid + 2.0, 1),
        "total_high": round(text_high + display_high + 2.5, 1),
    }


def build_report(section_rows: list[dict[str, str]], displays: list[dict[str, str]]) -> str:
    current_words = sum(int(row["Current words"]) for row in section_rows)
    target_words = sum(int(row["Target words"]) for row in section_rows)
    main_tables = sum(row["artifact_type"] == "table" and row["compact_placement"] == "main_text" for row in displays)
    main_figures = sum(row["artifact_type"] == "figure" and row["compact_placement"] == "main_text" for row in displays)
    pages = estimate_pages(min(target_words, TARGET_WORDS), main_tables, main_figures)
    lines = [
        "# Main-Manuscript Compression Plan",
        "",
        "This plan preserves the full evidence archive while defining a compact main-text target for Q1 submission formatting.",
        "",
        "## Target",
        "",
        f"- Current draft words: {current_words}",
        f"- Target main-text words: {min(target_words, TARGET_WORDS)}",
        f"- Word reduction target: {max(0, current_words - min(target_words, TARGET_WORDS))}",
        f"- Compact main-text tables: {main_tables}",
        f"- Compact main-text figures: {main_figures}",
        f"- Estimated pages low/mid/high: {pages['total_low']}/{pages['total_mid']}/{pages['total_high']}",
        "- Status: within the compact main-text budget at low and mid density; high-density risk remains template-dependent.",
        "",
        "## Section Word Budget",
        "",
        "| Section | Current | Target | Cut | Action |",
        "|---|---:|---:|---:|---|",
    ]
    for row in section_rows:
        lines.append(
            f"| {row['Section']} | {row['Current words']} | {row['Target words']} | {row['Cut words']} | {row['Action']} |"
        )
    lines += [
        "",
        "## Compact Main Displays",
        "",
        "| Type | Artifact | Placement | Role |",
        "|---|---|---|---|",
    ]
    for row in displays:
        if row["compact_placement"] != "main_text":
            continue
        lines.append(f"| {row['artifact_type']} | {row['artifact_id']} | {row['compact_placement']} | {row['role']} |")
    lines += [
        "",
        "## Required Moves",
        "",
        "- Merge the dataset inventory and reproducibility matrix in prose or as one compact main table.",
        "- Keep Table 23 in the main text because it carries the cross-paradigm synthesis; move the detailed taxonomy table to supplement.",
        "- Move Figure 2 to supplement unless the final template has room after figure sizing.",
        "- Keep Table 19 in the main text only if repair is a core reviewer-facing contribution; otherwise cite it from supplement and keep the repair-model summary in prose.",
        "- Remove repeated methodological mechanics once scripts and supplementary manifests are cited.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    section_rows = section_word_counts()
    displays = display_rows()
    write_csv(OUT_DIR / "main_text_word_budget.csv", section_rows)
    write_csv(OUT_DIR / "compact_main_display_plan.csv", displays)
    report = build_report(section_rows, displays)
    (OUT_DIR / "main_text_compression_plan.md").write_text(report, encoding="utf-8")
    (NOTES_DIR / "main_text_compression_plan.md").write_text(report, encoding="utf-8")
    print(f"Wrote {(OUT_DIR / 'main_text_word_budget.csv').relative_to(ROOT)}")
    print(f"Wrote {(OUT_DIR / 'compact_main_display_plan.csv').relative_to(ROOT)}")
    print(f"Wrote {(OUT_DIR / 'main_text_compression_plan.md').relative_to(ROOT)}")


if __name__ == "__main__":
    main()
