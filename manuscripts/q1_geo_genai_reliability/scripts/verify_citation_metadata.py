#!/usr/bin/env python3
"""Verify citation metadata against Crossref and arXiv endpoints.

This is a pre-submission verification aid. It records endpoint availability and
basic metadata agreement, but it does not replace the final journal-style
reference formatting pass.
"""

from __future__ import annotations

import csv
import json
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MS_DIR = ROOT / "manuscripts/q1_geo_genai_reliability"
SUBMISSION_DIR = MS_DIR / "submission"
NOTES_DIR = MS_DIR / "notes"
METADATA_CSV = SUBMISSION_DIR / "citation_metadata.csv"
OUT_CSV = SUBMISSION_DIR / "citation_verification_report.csv"
OUT_MD = NOTES_DIR / "citation_verification_report.md"


USER_AGENT = "GeoGenAIReliabilityCitationAudit/0.1 (mailto:metadata-audit@example.invalid)"
ARXIV_NS = {"atom": "http://www.w3.org/2005/Atom"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def fetch_json(url: str) -> tuple[int, dict[str, object] | None, str]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.status, json.loads(response.read().decode("utf-8")), ""
    except urllib.error.HTTPError as exc:
        return exc.code, None, str(exc)
    except Exception as exc:  # noqa: BLE001 - network verification should report every failure.
        return 0, None, f"{type(exc).__name__}: {exc}"


def fetch_text(url: str) -> tuple[int, str, str]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.status, response.read().decode("utf-8", errors="replace"), ""
    except urllib.error.HTTPError as exc:
        return exc.code, "", str(exc)
    except Exception as exc:  # noqa: BLE001
        return 0, "", f"{type(exc).__name__}: {exc}"


def resolve_url(url: str) -> tuple[int, str, str]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.status, response.geturl(), ""
    except urllib.error.HTTPError as exc:
        return exc.code, exc.geturl(), str(exc)
    except Exception as exc:  # noqa: BLE001
        return 0, "", f"{type(exc).__name__}: {exc}"


def normalize(value: str) -> str:
    text = value.lower().replace("–", "-").replace("—", "-")
    for old, new in [(":", " "), ("-", " "), ("&", "and")]:
        text = text.replace(old, new)
    return " ".join(text.split())


def title_match(local: str, remote: str) -> str:
    local_norm = normalize(local).rstrip(".")
    remote_norm = normalize(remote).rstrip(".")
    if not remote_norm:
        return "missing_remote_title"
    if local_norm == remote_norm:
        return "match"
    if local_norm in remote_norm or remote_norm in local_norm:
        return "partial_match"
    return "mismatch"


def container_match(local: str, remote: str) -> str:
    if not local:
        return "not_applicable"
    local_norm = normalize(local)
    remote_norm = normalize(remote)
    aliases = {
        "abstracts of the international cartographic association": {"abstracts of the ica"},
    }
    if local_norm == remote_norm:
        return "match"
    if remote_norm in aliases.get(local_norm, set()):
        return "match_abbreviation"
    if local_norm in remote_norm or remote_norm in local_norm:
        return "partial_match"
    return "mismatch"


def year_from_crossref(message: dict[str, object]) -> str:
    for key in ["published", "issued", "published-online", "published-print"]:
        part = message.get(key)
        if isinstance(part, dict):
            date_parts = part.get("date-parts")
            if isinstance(date_parts, list) and date_parts and isinstance(date_parts[0], list) and date_parts[0]:
                return str(date_parts[0][0])
    return ""


def crossref_verify(item: dict[str, str]) -> dict[str, str]:
    doi = item["doi"]
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="")
    status, data, error = fetch_json(url)
    row = {
        "endpoint": url,
        "endpoint_status": str(status),
        "remote_title": "",
        "remote_container": "",
        "remote_year": "",
        "remote_volume": "",
        "remote_issue": "",
        "remote_pages": "",
        "title_check": "not_checked",
        "year_check": "not_checked",
        "container_check": "not_checked",
        "volume_issue_pages_check": "not_checked",
        "verification_status": "endpoint_error",
        "verification_note": error,
    }
    if status != 200 or not data:
        resolver_status, resolved_url, resolver_error = resolve_url("https://doi.org/" + urllib.parse.quote(doi, safe="/."))
        if resolver_status in {200, 301, 302} or resolved_url:
            row["endpoint_status"] = f"crossref:{status};doi_resolver:{resolver_status}"
            row["verification_status"] = "resolver_verified"
            row["verification_note"] = f"Crossref metadata unavailable; DOI resolver reached {resolved_url or 'target URL'}. {resolver_error}".strip()
            return row
        if item.get("url"):
            publisher_status, _, publisher_error = fetch_text(item["url"])
            if publisher_status == 200:
                row["endpoint_status"] = f"crossref:{status};publisher_url:{publisher_status}"
                row["endpoint"] = item["url"]
                row["verification_status"] = "publisher_url_verified"
                row["verification_note"] = "Crossref metadata unavailable; publisher URL reached directly."
                return row
            row["verification_note"] = f"{error}; DOI resolver: {resolver_error}; publisher URL: {publisher_status} {publisher_error}"
        return row
    message = data.get("message", {})
    if not isinstance(message, dict):
        row["verification_note"] = "Crossref response did not contain a message object."
        return row

    titles = message.get("title") or []
    containers = message.get("container-title") or []
    row["remote_title"] = str(titles[0]) if isinstance(titles, list) and titles else ""
    row["remote_container"] = str(containers[0]) if isinstance(containers, list) and containers else ""
    row["remote_year"] = year_from_crossref(message)
    row["remote_volume"] = str(message.get("volume", ""))
    row["remote_issue"] = str(message.get("issue", ""))
    row["remote_pages"] = str(message.get("page", message.get("article-number", "")))
    row["title_check"] = title_match(item["title"], row["remote_title"])
    row["year_check"] = "match" if item["year"] == row["remote_year"] else f"local={item['year']};remote={row['remote_year']}"
    row["container_check"] = container_match(item["journal"], row["remote_container"])

    details: list[str] = []
    for local_key, remote_key, label in [
        ("volume", "remote_volume", "volume"),
        ("issue", "remote_issue", "issue"),
        ("pages_or_article", "remote_pages", "pages"),
    ]:
        local = item.get(local_key, "").replace("--", "-")
        remote = row.get(remote_key, "").replace("--", "-")
        if local and remote and local == remote:
            details.append(f"{label}:match")
        elif local and remote:
            details.append(f"{label}:local={local};remote={remote}")
        elif local and not remote:
            details.append(f"{label}:local_only={local}")
        elif remote and not local:
            details.append(f"{label}:remote_only={remote}")
    row["volume_issue_pages_check"] = "; ".join(details) if details else "no_volume_issue_pages"

    core_ok = row["title_check"] in {"match", "partial_match"} and row["container_check"] in {"match", "match_abbreviation", "partial_match", "not_applicable"}
    if row["year_check"] != "match":
        row["verification_status"] = "metadata_warning"
    elif core_ok:
        row["verification_status"] = "verified"
    else:
        row["verification_status"] = "metadata_warning"
    row["verification_note"] = "Crossref metadata endpoint reached."
    return row


def arxiv_verify(item: dict[str, str]) -> dict[str, str]:
    arxiv = item["arxiv"]
    url = "https://export.arxiv.org/api/query?id_list=" + urllib.parse.quote(arxiv)
    status, text, error = fetch_text(url)
    row = {
        "endpoint": url,
        "endpoint_status": str(status),
        "remote_title": "",
        "remote_container": "arXiv",
        "remote_year": "",
        "remote_volume": "",
        "remote_issue": "",
        "remote_pages": "",
        "title_check": "not_checked",
        "year_check": "not_checked",
        "container_check": "not_applicable",
        "volume_issue_pages_check": "not_applicable",
        "verification_status": "endpoint_error",
        "verification_note": error,
    }
    if status != 200 or not text:
        return row
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        row["verification_note"] = f"arXiv XML parse error: {exc}"
        return row
    entries = root.findall("atom:entry", ARXIV_NS)
    if not entries:
        row["verification_note"] = "No arXiv entry returned."
        return row
    entry = entries[0]
    title = entry.findtext("atom:title", default="", namespaces=ARXIV_NS)
    published = entry.findtext("atom:published", default="", namespaces=ARXIV_NS)
    row["remote_title"] = " ".join(title.split())
    row["remote_year"] = published[:4]
    row["title_check"] = title_match(item["title"], row["remote_title"])
    row["year_check"] = "match" if item["year"] == row["remote_year"] else f"local={item['year']};remote={row['remote_year']}"
    if row["title_check"] in {"match", "partial_match"} and row["year_check"] == "match":
        row["verification_status"] = "verified"
    else:
        row["verification_status"] = "metadata_warning"
    row["verification_note"] = "arXiv API endpoint reached."
    return row


def verify_all() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    checked_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for item in read_csv(METADATA_CSV):
        if item["doi"]:
            remote = crossref_verify(item)
            identifier_type = "doi"
            identifier = item["doi"]
        elif item["arxiv"]:
            remote = arxiv_verify(item)
            identifier_type = "arxiv"
            identifier = item["arxiv"]
        else:
            remote = {
                "endpoint": "",
                "endpoint_status": "",
                "remote_title": "",
                "remote_container": "",
                "remote_year": "",
                "remote_volume": "",
                "remote_issue": "",
                "remote_pages": "",
                "title_check": "not_checked",
                "year_check": "not_checked",
                "container_check": "not_checked",
                "volume_issue_pages_check": "not_checked",
                "verification_status": "no_identifier",
                "verification_note": "No DOI or arXiv identifier in local metadata.",
            }
            identifier_type = "none"
            identifier = ""
        rows.append(
            {
                "checked_at_utc": checked_at,
                "key": item["key"],
                "citation_key": item["citation_key"],
                "identifier_type": identifier_type,
                "identifier": identifier,
                "local_title": item["title"],
                "local_container": item["journal"],
                "local_year": item["year"],
                "local_volume": item["volume"],
                "local_issue": item["issue"],
                "local_pages": item["pages_or_article"],
                **remote,
            }
        )
        time.sleep(0.2)
    return rows


def write_markdown(rows: list[dict[str, str]]) -> None:
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["verification_status"]] = counts.get(row["verification_status"], 0) + 1
    checked_at = rows[0]["checked_at_utc"] if rows else ""
    lines = [
        "# Citation Verification Report",
        "",
        f"Checked at UTC: `{checked_at}`.",
        "",
        "This report verifies DOI-backed references through the Crossref works endpoint, DOI resolver or publisher URLs when Crossref metadata is unavailable, and arXiv-only references through the arXiv API. It is a reproducible pre-submission metadata check, not the final journal reference-style conversion.",
        "",
        "## Summary",
        "",
    ]
    lines.extend(f"- {status}: {count}" for status, count in sorted(counts.items()))
    lines += [
        "",
        "## Per-Reference Checks",
        "",
        "| Citation key | Identifier | Status | Title | Year | Container | Volume/issue/pages |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    row["citation_key"],
                    f"{row['identifier_type']}:{row['identifier']}",
                    row["verification_status"],
                    row["title_check"],
                    row["year_check"],
                    row["container_check"],
                    row["volume_issue_pages_check"],
                ]
            )
            + " |"
        )
    lines += [
        "",
        "## Remaining Citation Tasks",
        "",
        "- Recheck this report immediately before submission because online-first metadata can change.",
        "- Convert references to the selected venue's exact native style.",
        "- Inspect any `resolver_verified` or `publisher_url_verified` rows manually if the submission portal requires publisher-page metadata beyond DOI resolution.",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    rows = verify_all()
    write_csv(OUT_CSV, rows)
    write_markdown(rows)
    print(f"Wrote {OUT_CSV.relative_to(ROOT)}")
    print(f"Wrote {OUT_MD.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
