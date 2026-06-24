#!/usr/bin/env python3
"""Create a local citation audit for the manuscript draft.

The audit is intentionally conservative: it records only metadata supported by
local notes/extracted text, and leaves publication metadata that requires web
verification as a remaining pre-submission task.
"""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MS_DIR = ROOT / "manuscripts/q1_geo_genai_reliability"
DRAFT = MS_DIR / "draft/manuscript_draft.md"
OUT = MS_DIR / "notes/citation_audit.md"


LOCAL_EVIDENCE: dict[str, dict[str, str]] = {
    "Affolter et al., 2025": {
        "source": "notes/paper_manifest.md; notes/extracted_text/2025_affolter_genai_map_making.txt",
        "identifier": "arXiv:2508.18959",
        "status": "Local arXiv identifier recorded; final venue/DOI not verified locally.",
    },
    "Burghardt et al., 2025": {
        "source": "notes/extracted_text/2025_burghardt_generative_methods_pictorial_maps.txt",
        "identifier": "Abstracts of the International Cartographic Association 10, 27; DOI:10.5194/ica-abs-10-27-2025",
        "status": "Conference abstract metadata locally supported.",
    },
    "Kang and Wang, 2026": {
        "source": "publisher page/Crossref lookup; notes/extracted_text/2026_kang_envisioning_genai_cartography.txt",
        "identifier": "International Journal of Cartography 12(2), 334-360; DOI:10.1080/23729333.2025.2582231",
        "status": "Publisher metadata verified externally; keep arXiv note only as local provenance if needed.",
    },
    "Kausika and van Altena, 2025": {
        "source": "notes/extracted_text/2025_kausika_geoai_topographic_mapping.txt",
        "identifier": "ISPRS Int. J. Geo-Inf. 2025, 14, 313; DOI:10.3390/ijgi14080313",
        "status": "Journal volume/article/DOI locally supported.",
    },
    "Li et al., 2025a": {
        "source": "notes/paper_manifest.md; notes/extracted_text/2025_li_autonomous_gis_research_agenda.txt",
        "identifier": "arXiv:2503.23633",
        "status": "Local arXiv identifier recorded; final venue/DOI not verified locally.",
    },
    "Li et al., 2025b": {
        "source": "notes/extracted_text/2025_li_cartodirector.txt",
        "identifier": "Abstracts of the International Cartographic Association 10, 168; DOI:10.5194/ica-abs-10-168-2025",
        "status": "Conference abstract metadata locally supported.",
    },
    "Pannoon and Netek, 2025": {
        "source": "notes/extracted_text/2025_pannoon_choropleth_maps_chatgpt4.txt",
        "identifier": "ISPRS Int. J. Geo-Inf. 2025, 14, 486; DOI:10.3390/ijgi14120486",
        "status": "Journal volume/article/DOI locally supported.",
    },
    "Shomer and Xu, 2025": {
        "source": "notes/extracted_text/2025_shomer_maple_label_placement_llm.txt",
        "identifier": "arXiv:2507.22952",
        "status": "Local arXiv identifier recorded; placeholder DOI appears in extracted text, so DOI must not be used.",
    },
    "Song et al., 2025": {
        "source": "notes/extracted_text/2025_song_llm_agent_vgi_mapping.txt",
        "identifier": "Journal of Geodesy and Geoinformation Science 8(2), 57-73; DOI:10.11947/j.JGGS.2025.0204",
        "status": "SciOpen metadata verified externally.",
    },
    "Sun et al., 2025a": {
        "source": "notes/paper_manifest.md; notes/extracted_text/2025_sun_scgm_bridging_scales_map_generation.txt",
        "identifier": "arXiv:2502.04991",
        "status": "Local arXiv identifier recorded; final venue/DOI not verified locally.",
    },
    "Sun et al., 2025b": {
        "source": "notes/extracted_text/2025_sun_genai_applications_cartography_gis_review.txt",
        "identifier": "Journal of Geodesy and Geoinformation Science 8(2), 74-89; DOI:10.11947/j.JGGS.2025.0205",
        "status": "SciOpen metadata verified externally.",
    },
    "Wang et al., 2025": {
        "source": "publisher page/Crossref lookup; notes/extracted_text/2025_wang_cartoagent.txt",
        "identifier": "International Journal of Geographical Information Science 39(9), 1904-1937; DOI:10.1080/13658816.2025.2507844",
        "status": "Publisher metadata verified externally.",
    },
    "Yang et al., 2025": {
        "source": "publisher page/Crossref lookup; notes/extracted_text/2025_yang_mapcolorai.txt",
        "identifier": "Cartography and Geographic Information Science 53(4), 479-497; DOI:10.1080/15230406.2025.2531055",
        "status": "Crossref metadata verified externally.",
    },
    "Zhang et al., 2025": {
        "source": "publisher page/Crossref lookup; MapGenerator local data release",
        "identifier": "Cartography and Geographic Information Science, 1-23; DOI:10.1080/15230406.2025.2587273",
        "status": "Crossref metadata verified externally; online-first article has pages but no assigned volume/issue in Crossref as of 2026-06-24.",
    },
}


EXTERNAL_VERIFICATION_URLS = {
    "Kang and Wang, 2026": "https://doi.org/10.1080/23729333.2025.2582231",
    "Song et al., 2025": "https://www.sciopen.com/article/10.11947/j.JGGS.2025.0204",
    "Sun et al., 2025b": "https://www.sciopen.com/article/10.11947/j.JGGS.2025.0205",
    "Wang et al., 2025": "https://doi.org/10.1080/13658816.2025.2507844",
    "Yang et al., 2025": "https://doi.org/10.1080/15230406.2025.2531055",
    "Zhang et al., 2025": "https://doi.org/10.1080/15230406.2025.2587273",
}


def extract_citations(text: str) -> list[str]:
    parenthetical = re.compile(r"\(([^()]*20\d{2}[a-z]?[^()]*)\)")
    key_pattern = re.compile(r"([A-Z][A-Za-z]+(?: and [A-Z][A-Za-z]+| et al\.), 20\d{2}[a-z]?)")
    keys: set[str] = set()
    for match in parenthetical.findall(text):
        keys.update(key_pattern.findall(match))
    return sorted(keys)


def extract_references(text: str) -> list[str]:
    if "## References" not in text:
        return []
    refs = text.split("## References", 1)[1].strip().split("\n\n")
    return [ref.replace("\n", " ").strip() for ref in refs if ref.strip()]


def main() -> None:
    text = DRAFT.read_text(encoding="utf-8")
    citations = extract_citations(text)
    references = extract_references(text)
    reference_text = "\n".join(references)

    rows: list[tuple[str, str, str, str, str]] = []
    for key in sorted(LOCAL_EVIDENCE):
        cited = "yes" if key in citations else "no"
        lead_author = key.split()[0]
        has_reference = "yes" if reference_text.startswith(lead_author) or f"\n{lead_author}" in reference_text else "check"
        evidence = LOCAL_EVIDENCE[key]
        rows.append((key, cited, has_reference, evidence["identifier"], evidence["status"]))

    uncatalogued = [citation for citation in citations if citation not in LOCAL_EVIDENCE]

    lines = [
        "# Citation Audit",
        "",
        "This audit is generated from the current manuscript draft, local paper notes, and structured citation exports. DOI/arXiv endpoint verification is reported separately in `notes/citation_verification_report.md`.",
        "",
        "## Coverage",
        "",
        f"- In-text citation keys found: {len(citations)}",
        f"- Reference paragraphs found: {len(references)}",
        f"- Locally catalogued citation keys: {len(LOCAL_EVIDENCE)}",
        f"- Uncatalogued in-text citation keys: {len(uncatalogued)}",
        "- Structured exports: `submission/citation_metadata.csv`, `submission/references.bib`, and `notes/citation_metadata_ledger.md` are generated by `scripts/export_citations.py`.",
        "- Endpoint verification: `submission/citation_verification_report.csv` and `notes/citation_verification_report.md` are generated by `scripts/verify_citation_metadata.py`.",
        "",
        "## Local Metadata Checks",
        "",
        "| Citation key | Cited in text | Reference present | Locally supported identifier | Status |",
        "|---|---:|---:|---|---|",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    lines += [
        "",
        "## Evidence Sources",
        "",
        "| Citation key | Local source |",
        "|---|---|",
    ]
    for key, evidence in sorted(LOCAL_EVIDENCE.items()):
        lines.append(f"| {key} | {evidence['source']} |")
    lines += [
        "",
        "## External Verification URLs",
        "",
        "| Citation key | URL |",
        "|---|---|",
    ]
    for key, url in sorted(EXTERNAL_VERIFICATION_URLS.items()):
        lines.append(f"| {key} | {url} |")
    lines += [
        "",
        "## Remaining Citation Tasks",
        "",
        "- Rerun endpoint verification immediately before submission because online-first metadata can change.",
        "- Convert all references to the selected journal's native style after selected venue selection.",
        "",
    ]
    if uncatalogued:
        lines += ["## Uncatalogued In-Text Citations", ""]
        lines.extend(f"- {citation}" for citation in uncatalogued)
        lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
