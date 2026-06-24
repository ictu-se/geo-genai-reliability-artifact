#!/usr/bin/env python3
"""Build an selected journal/Taylor & Francis style preflight ledger."""

from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MS_DIR = ROOT / "manuscripts/q1_geo_genai_reliability"
SUBMISSION_DIR = MS_DIR / "submission"
OUT_DIR = SUBMISSION_DIR / "journal_style_preflight"
CSV_OUT = OUT_DIR / "journal_style_preflight.csv"
MD_OUT = OUT_DIR / "journal_style_preflight.md"

OFFICIAL_SOURCES = {
    "manuscript_layout": "https://authorservices.taylorandfrancis.com/publishing-your-research/writing-your-paper/journal-manuscript-layout-guide/",
    "data_availability": "https://authorservices.taylorandfrancis.com/data-sharing/share-your-data/data-availability-statements/",
    "open_data_policy": "https://authorservices.taylorandfrancis.com/data-sharing-policies/open-data/",
    "ijgis": "https://www.tandfonline.com/journals/tgis20",
    "special_issue": "https://think.taylorandfrancis.com/special_issues/critical-challenges-in-geoai/",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w-]+\b", text))


def header_line(text: str, header: str) -> int | None:
    needle = f"## {header}"
    for index, line in enumerate(text.splitlines(), start=1):
        if line.strip() == needle:
            return index
    return None


def contains_any(text: str, needles: list[str]) -> list[str]:
    low = text.lower()
    return [needle for needle in needles if needle.lower() in low]


def add_row(
    rows: list[dict[str, str]],
    category: str,
    check: str,
    mode: str,
    status: str,
    evidence: str,
    source: str,
) -> None:
    rows.append(
        {
            "category": category,
            "check": check,
            "mode": mode,
            "status": status,
            "evidence": evidence,
            "source": source,
        }
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    draft_text = read_text(MS_DIR / "draft/manuscript_draft.md")
    blinded_text = read_text(SUBMISSION_DIR / "blinded_main_manuscript.md")
    blinded_compact_text = read_text(SUBMISSION_DIR / "blinded_compact_main_manuscript.md")
    abstract_rows = read_csv(SUBMISSION_DIR / "submission_abstract_fields.csv")
    citation_rows = read_csv(SUBMISSION_DIR / "citation_metadata.csv")
    citation_verification_rows = read_csv(SUBMISSION_DIR / "citation_verification_report.csv")
    latex_main = SUBMISSION_DIR / "latex/main.tex"
    latex_pdf = SUBMISSION_DIR / "latex/main.pdf"
    latex_log = read_text(SUBMISSION_DIR / "latex/latex_build.log")
    abstract_by_field = {row.get("field", ""): row for row in abstract_rows}
    keywords = abstract_by_field.get("keywords", {})
    short_abstract = abstract_by_field.get("short_abstract", {})
    keyword_count = int(keywords.get("word_count", "0") or 0)
    short_abstract_words = word_count(short_abstract.get("value", ""))

    rows: list[dict[str, str]] = []
    add_row(
        rows,
        "review_file",
        "Blinded compact manuscript exists",
        "automated",
        "pass" if blinded_compact_text else "fail",
        f"{word_count(blinded_compact_text)} words",
        "local package",
    )
    add_row(
        rows,
        "review_file",
        "LaTeX submission package compiles to PDF",
        "automated",
        "pass"
        if latex_main.exists()
        and latex_pdf.exists()
        and ("Output written on main.pdf" in latex_log or "All targets (main.pdf) are up-to-date" in latex_log)
        else "fail",
        f"pdf_bytes={latex_pdf.stat().st_size if latex_pdf.exists() else 0}",
        "local LaTeX compile",
    )
    review_leaks = contains_any(
        blinded_text + "\n" + blinded_compact_text,
        ["/" + "Users/", "nguyen" + "thevinh", "Geo" + "-LLM", "OR" + "CID", "Acknowledg" + "ements", "Fund" + "ing"],
    )
    add_row(
        rows,
        "review_file",
        "Double-anonymous review files have no obvious identity/path leaks",
        "automated",
        "pass" if not review_leaks and blinded_text and blinded_compact_text else "fail",
        "; ".join(review_leaks) if review_leaks else "none detected",
        "local anonymization scan",
    )
    add_row(
        rows,
        "front_matter",
        "Short abstract is in a journal-ready length band",
        "automated",
        "pass" if 150 <= short_abstract_words <= 250 else "fail",
        f"{short_abstract_words} words",
        OFFICIAL_SOURCES["manuscript_layout"],
    )
    add_row(
        rows,
        "front_matter",
        "Keyword field is populated",
        "automated",
        "pass" if keyword_count >= 5 else "fail",
        f"{keyword_count} keywords",
        OFFICIAL_SOURCES["manuscript_layout"],
    )

    compact_positions = {
        name: header_line(blinded_compact_text, name)
        for name in [
            "Acknowledgments",
            "Declaration of Interest Statement",
            "Data Availability Statement",
            "Software Availability Statement",
            "References",
        ]
    }
    refs_line = compact_positions.get("References") or 10**9
    for header in [
        "Acknowledgments",
        "Declaration of Interest Statement",
        "Data Availability Statement",
        "Software Availability Statement",
    ]:
        line_no = compact_positions.get(header)
        add_row(
            rows,
            "statements",
            f"{header} section appears before References",
            "automated",
            "pass" if line_no is not None and line_no < refs_line else "fail",
            f"{header} line={line_no}; References line={compact_positions.get('References')}",
            OFFICIAL_SOURCES["data_availability"] if header in {"Data Availability Statement", "Software Availability Statement"} else OFFICIAL_SOURCES["manuscript_layout"],
        )

    final_sections = [
        "Acknowledgments",
        "Declaration of Interest Statement",
        "Data Availability Statement",
        "Software Availability Statement",
        "References",
    ]
    draft_missing = [section for section in final_sections if header_line(draft_text, section) is None]
    add_row(
        rows,
        "statements",
        "Full draft includes required end-matter sections",
        "automated",
        "pass" if not draft_missing else "fail",
        "missing: " + ", ".join(draft_missing) if draft_missing else "all present",
        OFFICIAL_SOURCES["manuscript_layout"],
    )
    verified_statuses = {"verified", "resolver_verified", "publisher_url_verified"}
    unresolved = [
        row.get("key", "unknown")
        for row in citation_verification_rows
        if row.get("verification_status") not in verified_statuses
    ]
    add_row(
        rows,
        "references",
        "Structured citations and resolver verification are current",
        "automated",
        "pass" if len(citation_rows) >= 14 and len(citation_rows) == len(citation_verification_rows) and not unresolved else "fail",
        f"metadata={len(citation_rows)}; verification={len(citation_verification_rows)}; unresolved={len(unresolved)}",
        "Crossref/arXiv/DOI resolver local audit",
    )
    add_row(
        rows,
        "references",
        "BibTeX export exists for final native reference-style conversion",
        "automated",
        "pass" if (SUBMISSION_DIR / "references.bib").exists() else "fail",
        "submission/references.bib",
        OFFICIAL_SOURCES["manuscript_layout"],
    )
    target_recheck_text = read_text(SUBMISSION_DIR / "journal_target_recheck_2026-06-24.md")
    add_row(
        rows,
        "target_route",
        "Dated journal/special-issue source-confidence ledger exists",
        "automated",
        "pass"
        if "Checked date: 2026-06-24" in target_recheck_text
        and "official-opened" in target_recheck_text
        and "third-party/supporting evidence" in target_recheck_text
        else "fail",
        "2026-06-24 ledger with official and supporting-source confidence labels",
        OFFICIAL_SOURCES["special_issue"],
    )
    add_row(
        rows,
        "data_code",
        "Data/code release plan and data-source manifest exist",
        "automated",
        "pass"
        if (SUBMISSION_DIR / "reproducibility_release_plan.md").exists()
        and (SUBMISSION_DIR / "DATA_SOURCES.md").exists()
        and (SUBMISSION_DIR / "reproducibility_manifest.csv").exists()
        else "fail",
        "release plan, data sources, and checksum manifest",
        OFFICIAL_SOURCES["open_data_policy"],
    )
    add_row(
        rows,
        "manual_gate",
        "Final native Taylor & Francis/selected journal reference style conversion",
        "manual",
        "manual",
        "Defer until final portal route and reference manager export are fixed.",
        OFFICIAL_SOURCES["manuscript_layout"],
    )
    add_row(
        rows,
        "manual_gate",
        "Final DOI/public repository and double-anonymous link treatment",
        "manual",
        "manual",
        "Defer until public release DOI/URL exists and review-route policy is reconfirmed.",
        OFFICIAL_SOURCES["data_availability"],
    )
    add_row(
        rows,
        "manual_gate",
        "Final Q1/quartile and route recheck",
        "manual",
        "manual",
        "Quartile evidence is database/category/year dependent and must be reconfirmed immediately before portal upload.",
        OFFICIAL_SOURCES["ijgis"],
    )

    with CSV_OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["category", "check", "mode", "status", "evidence", "source"])
        writer.writeheader()
        writer.writerows(rows)

    automated = [row for row in rows if row["mode"] == "automated"]
    manual = [row for row in rows if row["mode"] == "manual"]
    passed = sum(row["status"] == "pass" for row in automated)
    lines = [
        "# Journal Style Preflight",
        "",
        "This ledger converts the current selected journal/Taylor & Francis submission route into local, reproducible checks. It is a preflight artifact, not a claim that the manuscript is final submission-ready.",
        "",
        f"- Automated checks passed: {passed}/{len(automated)}",
        f"- Manual gates retained: {len(manual)}",
        "- Checked route date: 2026-06-24",
        "",
        "## Automated and Manual Checks",
        "",
        "| Category | Check | Mode | Status | Evidence | Source |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['category']} | {row['check']} | {row['mode']} | {row['status']} | {row['evidence']} | {row['source']} |"
        )
    lines += [
        "",
        "## Official Sources to Reopen Before Submission",
        "",
    ]
    for label, source in OFFICIAL_SOURCES.items():
        lines.append(f"- {label}: {source}")
    lines += [
        "",
        "## Interpretation",
        "",
        "- `pass` means the local artifact satisfies the current automated preflight rule.",
        "- `manual` means the item intentionally remains a final submission gate because it depends on the live portal, journal route, public DOI, or external database state.",
        "",
    ]
    MD_OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {CSV_OUT.relative_to(ROOT)}")
    print(f"Wrote {MD_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
