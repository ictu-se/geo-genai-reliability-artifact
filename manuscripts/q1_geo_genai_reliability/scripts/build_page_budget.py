#!/usr/bin/env python3
"""Build a main-text/supplement split and page-budget audit."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MS_DIR = ROOT / "manuscripts/q1_geo_genai_reliability"
DRAFT = MS_DIR / "draft/manuscript_draft.md"
TABLE_DIR = MS_DIR / "tables"
FIG_DIR = MS_DIR / "figures"
NOTES_DIR = MS_DIR / "notes"
SUBMISSION_DIR = MS_DIR / "submission"


MAIN_TABLES = {
    "table_01_dataset_inventory.csv": "Local Geo-GenAI artifact inventory",
    "table_02_reproducibility_matrix.csv": "Reproducibility matrix",
    "table_05c_scgm_retrieval_comparison.csv": "SCGM generated-output baseline comparison",
    "table_11_cross_paradigm_metric_taxonomy_slim.csv": "Cross-paradigm metric taxonomy",
    "table_13_choropleth_model_mode_summary.csv": "Choropleth benchmark model-mode aggregate",
    "table_16_screenshot_level_choropleth_qa.csv": "Screenshot-level choropleth artifact QA",
    "table_19_iterative_validator_repair.csv": "Iterative validator-gated repair sweep",
}

MAIN_FIGURES = {
    "Figure 1": "Cross-paradigm artifact chain",
    "Figure 2": "Dataset inventory",
    "Figure 5": "Choropleth benchmark score bars",
    "Figure 7": "Screenshot-level QA bar chart",
    "Figure 9": "SCGM generated-output baseline comparison",
}


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def word_count() -> int:
    return len(DRAFT.read_text(encoding="utf-8").split())


def figure_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line in (FIG_DIR / "figure_index.md").read_text(encoding="utf-8").splitlines():
        if not line.startswith("| Figure ") or line.startswith("| Figure |"):
            continue
        parts = [part.strip() for part in line.strip("|").split("|")]
        rows.append({"id": parts[0], "file": parts[1].strip("`"), "status": parts[2] if len(parts) > 2 else ""})
    return rows


def split_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in sorted(TABLE_DIR.glob("table_*.csv")):
        placement = "main_text" if path.name in MAIN_TABLES else "supplement"
        rows.append(
            {
                "artifact_type": "table",
                "artifact_id": path.stem,
                "file": str(path.relative_to(MS_DIR)),
                "placement": placement,
                "role": MAIN_TABLES.get(path.name, "supporting detail/evidence table"),
            }
        )
    for figure in figure_rows():
        placement = "main_text" if figure["id"] in MAIN_FIGURES else "supplement"
        rows.append(
            {
                "artifact_type": "figure",
                "artifact_id": figure["id"],
                "file": figure["file"],
                "placement": placement,
                "role": MAIN_FIGURES.get(figure["id"], "supporting visual evidence/contact sheet"),
            }
        )
    return rows


def estimate_pages(words: int, main_table_count: int, main_figure_count: int) -> dict[str, float]:
    # Coarse manuscript estimates; final pagination depends on journal template.
    text_low = words / 550.0
    text_mid = words / 500.0
    text_high = words / 450.0
    display_low = main_table_count * 0.45 + main_figure_count * 0.55
    display_mid = main_table_count * 0.60 + main_figure_count * 0.70
    display_high = main_table_count * 0.80 + main_figure_count * 0.95
    back_matter_low = 1.5
    back_matter_mid = 2.0
    back_matter_high = 2.5
    return {
        "text_low": round(text_low, 1),
        "text_mid": round(text_mid, 1),
        "text_high": round(text_high, 1),
        "display_low": round(display_low, 1),
        "display_mid": round(display_mid, 1),
        "display_high": round(display_high, 1),
        "total_low": round(text_low + display_low + back_matter_low, 1),
        "total_mid": round(text_mid + display_mid + back_matter_mid, 1),
        "total_high": round(text_high + display_high + back_matter_high, 1),
    }


def write_report(rows: list[dict[str, str]]) -> None:
    words = word_count()
    main_tables = [row for row in rows if row["artifact_type"] == "table" and row["placement"] == "main_text"]
    main_figures = [row for row in rows if row["artifact_type"] == "figure" and row["placement"] == "main_text"]
    supplement_tables = [row for row in rows if row["artifact_type"] == "table" and row["placement"] == "supplement"]
    supplement_figures = [row for row in rows if row["artifact_type"] == "figure" and row["placement"] == "supplement"]
    pages = estimate_pages(words, len(main_tables), len(main_figures))
    if pages["total_mid"] <= 30.0:
        status = "within_30_page_target"
    elif pages["total_mid"] <= 32.0:
        status = "borderline_with_compression_plan"
    else:
        status = "needs_compression"

    lines = [
        "# Main/Supplement Split and Page-Budget Audit",
        "",
        "This generated audit keeps the main-text submission budget separate from the larger evidence archive.",
        "",
        "## Summary",
        "",
        f"- Draft word count: {words}",
        f"- Total evidence tables: {len(list(TABLE_DIR.glob('table_*.csv')))}",
        f"- Indexed figures/contact sheets: {len(figure_rows())}",
        f"- Main-text tables: {len(main_tables)}",
        f"- Main-text figures: {len(main_figures)}",
        f"- Supplementary tables: {len(supplement_tables)}",
        f"- Supplementary figures/contact sheets: {len(supplement_figures)}",
        f"- Page-budget status: `{status}`",
        "",
        "## Page Estimate",
        "",
        "| Component | Low | Mid | High |",
        "|---|---:|---:|---:|",
        f"| Text body | {pages['text_low']} | {pages['text_mid']} | {pages['text_high']} |",
        f"| Main tables/figures | {pages['display_low']} | {pages['display_mid']} | {pages['display_high']} |",
        "| References/statements | 1.5 | 2.0 | 2.5 |",
        f"| Estimated total | {pages['total_low']} | {pages['total_mid']} | {pages['total_high']} |",
        "",
        "## Main-Text Displays",
        "",
    ]
    lines.extend(f"- {row['artifact_id']}: {row['role']}" for row in main_tables)
    lines.extend(f"- {row['artifact_id']}: {row['role']}" for row in main_figures)
    lines += [
        "",
        "## Compression Actions Before Submission",
        "",
        "- Use `submission/main_text_compression_plan.md` for the generated 9,500-word, 6-table, 4-figure compact submission route.",
        "- Keep the main-text display set at 7 tables and 5 figures unless the journal template proves roomier than expected.",
        "- Move prompt lists, exhaustive run manifests, adjudication ledgers, VLM raw outputs, and contact sheets to supplement.",
        "- Tighten methods/results prose before adding any new main-text table.",
        "- If the high estimate is binding in the final template, merge Tables 1-2 or move Table 19 to supplement and cite it from the repair-loop discussion.",
        "",
    ]
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    (NOTES_DIR / "page_budget_audit.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    rows = split_rows()
    write_csv(SUBMISSION_DIR / "main_supplement_split.csv", rows)
    write_report(rows)
    print(f"Wrote {(SUBMISSION_DIR / 'main_supplement_split.csv').relative_to(ROOT)}")
    print(f"Wrote {(NOTES_DIR / 'page_budget_audit.md').relative_to(ROOT)}")


if __name__ == "__main__":
    main()
