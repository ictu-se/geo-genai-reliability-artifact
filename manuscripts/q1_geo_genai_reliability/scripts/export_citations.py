#!/usr/bin/env python3
"""Export citation metadata from the curated manuscript BibTeX file."""

from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MS_DIR = ROOT / "manuscripts/q1_geo_genai_reliability"
REFERENCE_DIR = MS_DIR / "references"
BIB_SOURCE = REFERENCE_DIR / "peer_reviewed.bib"
SUBMISSION_DIR = MS_DIR / "submission"
NOTES_DIR = MS_DIR / "notes"


CSV_FIELDS = [
    "key",
    "entry_type",
    "authors",
    "year",
    "title",
    "journal",
    "booktitle",
    "volume",
    "issue",
    "pages_or_article",
    "doi",
    "url",
    "status",
]


def split_bib_entries(text: str) -> list[tuple[str, str, str]]:
    entries: list[tuple[str, str, str]] = []
    pos = 0
    while True:
        start = text.find("@", pos)
        if start == -1:
            break
        brace = text.find("{", start)
        if brace == -1:
            break
        entry_type = text[start + 1 : brace].strip().lower()
        depth = 0
        end = brace
        for idx in range(brace, len(text)):
            if text[idx] == "{":
                depth += 1
            elif text[idx] == "}":
                depth -= 1
                if depth == 0:
                    end = idx
                    break
        body = text[brace + 1 : end]
        key, _, fields = body.partition(",")
        entries.append((entry_type, key.strip(), fields))
        pos = end + 1
    return entries


def parse_fields(fields: str) -> dict[str, str]:
    out: dict[str, str] = {}
    pattern = re.compile(r"(\w+)\s*=\s*[{]((?:[^{}]|[{][^{}]*[}])*)[}]\s*,?", re.S)
    for match in pattern.finditer(fields):
        key = match.group(1).lower()
        value = re.sub(r"\s+", " ", match.group(2).replace("{", "").replace("}", "")).strip()
        out[key] = value
    return out


def load_citations() -> list[dict[str, str]]:
    text = BIB_SOURCE.read_text(encoding="utf-8")
    rows: list[dict[str, str]] = []
    for entry_type, key, fields in split_bib_entries(text):
        item = parse_fields(fields)
        rows.append(
            {
                "key": key,
                "entry_type": entry_type,
                "authors": item.get("author", ""),
                "year": item.get("year", ""),
                "title": item.get("title", ""),
                "journal": item.get("journal", ""),
                "booktitle": item.get("booktitle", ""),
                "volume": item.get("volume", ""),
                "issue": item.get("number", ""),
                "pages_or_article": item.get("pages", item.get("eid", "")),
                "doi": item.get("doi", ""),
                "url": item.get("url", ""),
                "status": "curated manuscript bibliography source",
            }
        )
    return rows


def reference_line(item: dict[str, str]) -> str:
    authors = item["authors"].replace(" and ", ", ")
    title = item["title"].rstrip(".")
    venue = item["journal"] or item["booktitle"]
    line = f"{authors} ({item['year']}). {title}."
    if venue:
        line += f" {venue}"
    if item["volume"]:
        line += f", {item['volume']}"
    if item["issue"]:
        line += f"({item['issue']})"
    if item["pages_or_article"]:
        line += f", {item['pages_or_article'].replace('--', '-')}"
    if item["doi"]:
        line += f". https://doi.org/{item['doi']}"
    elif item["url"]:
        line += f". {item['url']}"
    return line


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def write_bib(path: Path) -> None:
    path.write_text(BIB_SOURCE.read_text(encoding="utf-8"), encoding="utf-8")


def write_ledger(path: Path, rows: list[dict[str, str]]) -> None:
    lines = [
        "# Citation Metadata Ledger",
        "",
        "Generated from `references/peer_reviewed.bib`. The BibTeX file is the source of truth for submission references and includes peer-reviewed works plus cited preprints that the manuscript directly discusses.",
        "",
        "## Coverage",
        "",
        f"- References exported: {len(rows)}",
        f"- DOI-backed entries: {sum(1 for item in rows if item['doi'])}",
        f"- Proceedings/booktitle entries: {sum(1 for item in rows if item['booktitle'])}",
        "",
        "## Metadata Table",
        "",
        "| Key | Type | Year | Venue | DOI/URL |",
        "|---|---|---:|---|---|",
    ]
    for item in rows:
        venue = item["journal"] or item["booktitle"]
        identifier = item["doi"] or item["url"]
        lines.append(f"| {item['key']} | {item['entry_type']} | {item['year']} | {venue} | {identifier} |")
    lines += ["", "## Reference Draft", ""]
    lines.extend(f"- {reference_line(item)}" for item in rows)
    lines += [
        "",
        "## Remaining Citation Tasks",
        "",
        "- Recheck publisher pages/Crossref for assigned volume, issue, pages, article numbers, capitalization, and online-first status.",
        "- Keep uncited dataset/provenance artifacts in methods or data provenance notes rather than expanding the formal bibliography unnecessarily.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    SUBMISSION_DIR.mkdir(parents=True, exist_ok=True)
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    rows = load_citations()
    write_csv(SUBMISSION_DIR / "citation_metadata.csv", rows)
    write_bib(SUBMISSION_DIR / "references.bib")
    write_ledger(NOTES_DIR / "citation_metadata_ledger.md", rows)
    print(f"Wrote {SUBMISSION_DIR.relative_to(ROOT)}/citation_metadata.csv")
    print(f"Wrote {SUBMISSION_DIR.relative_to(ROOT)}/references.bib")
    print(f"Wrote {NOTES_DIR.relative_to(ROOT)}/citation_metadata_ledger.md")


if __name__ == "__main__":
    main()
