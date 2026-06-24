#!/usr/bin/env python3
"""Build submission-facing abstract, significance, and portal fields."""

from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MS_DIR = ROOT / "manuscripts/q1_geo_genai_reliability"
OUT_DIR = MS_DIR / "submission"


TITLE = "From Map-Like Images to Trustworthy Cartographic Artifacts: A Cross-Paradigm Reliability Audit of Geo-Generative AI"

KEYWORDS = [
    "GeoAI",
    "generative AI",
    "cartography",
    "map generation",
    "evaluation",
    "reproducibility",
    "cartographic quality",
    "LLM agents",
    "remote sensing",
    "choropleth maps",
]

SHORT_ABSTRACT = """
Generative AI is entering cartography through text-to-map image synthesis,
remote-sensing-to-map translation, LLM-generated GIS code, multimodal design
agents, and specialized map-design assistants. Yet current evaluations often
ask whether outputs look map-like, while practical map production requires
artifacts that remain geographically grounded, spatially coherent,
reproducible, editable, and auditable. This paper proposes an artifact-aware
reliability framework for GeoAI map generation and stress-tests it across three
public artifact families: paired text-map image data, remote-sensing-to-map
tiles, and LLM/code-generated choropleth maps. The framework treats generated
maps as chains linking source data, prompts or captions, conditioning inputs,
generated intermediate objects, rendered outputs, validation traces, and repair
histories. We operationalize this view through dataset reproducibility audits,
caption-fidelity heuristics and local VLM review, geospatial linting,
tile-edge continuity metrics, leakage-guarded generated-output baselines,
code-execution checks, screenshot-level cartographic QA, evaluator
adjudication queues, and validator-gated repair loops. Results show that
reliability failures emerge at different links in the chain: caption grounding
is uneven, cascade-reference coverage is incomplete, lightweight learned
remote-sensing-to-map baselines improve some image metrics while smoothing
cartographic detail, and plausible generated GIS code can fail to produce
complete map artifacts. A validator-gated repair sweep completes 25 of 40
previously incomplete choropleth cases, but also shows why repair must be
audited as evidence rather than assumed as success. The study offers a
reproducible scaffold for comparing, diagnosing, and improving GeoAI
map-generation workflows.
"""

EXTENDED_ABSTRACT = """
Generative AI is rapidly changing how maps can be produced, from text-to-map
image synthesis and remote-sensing-to-map translation to LLM-generated GIS code
and multimodal cartographic agents. Yet current evaluation practices often
remain fragmented: image-generation studies emphasize visual plausibility,
agent studies emphasize case demonstrations, and code-generation workflows
emphasize execution. These views are individually useful but insufficient for
map production, where a trustworthy artifact must remain geographically
grounded, reproducible, spatially coherent, cartographically complete, and
auditable after generation.

This paper proposes an artifact-aware reliability framework for GeoAI map
generation and evaluates it across three public artifact families: paired
text-map image data, remote-sensing-to-map tile data, and LLM/code-generated
choropleth maps. The framework treats generated maps as artifact chains linking
source data, prompts or captions, conditioning inputs, generated intermediate
objects, rendered outputs, validation traces, and repair histories. We
operationalize this view through dataset reproducibility audits,
caption-fidelity heuristics and local VLM review, geospatial linting,
tile-edge continuity metrics, leakage-guarded generated-output baselines,
code-execution checks, screenshot-level cartographic QA, evaluator
adjudication queues, and validator-gated repair loops.

The empirical results show that reliability failures arise at different points
in the map-generation chain. Public artifacts are valuable but uneven:
text-map image pairs require caption-grounding validation, remote-sensing-to-map
releases can provide complete base pairs while lacking full cascade-reference
coverage, and LLM-code choropleth generation can fail to produce complete map
artifacts even when generated code appears plausible. Repair and validation
help, but do not remove the need for artifact-specific evaluation: an iterative
validator-gated repair sweep completes 25 of 40 previously incomplete
choropleth cases, while lightweight learned remote-sensing-to-map baselines
expose trade-offs between image similarity, edge continuity, and cartographic
detail. We argue that critical GeoAI research should move from asking whether
models make map-like outputs to asking which cartographic obligations each
generated artifact satisfies.
"""

SIGNIFICANCE = """
This manuscript reframes GeoAI map generation as an artifact-reliability
problem rather than a single-model performance problem. Its value is the
combination of an evaluation framework and a reproducible empirical stress test
across text-map images, remote-sensing-to-map tiles, and LLM-generated
choropleth workflows. The study identifies where public artifacts already
support rigorous evaluation, where validation remains under-specified, and how
repair loops should be measured before generated maps are trusted.
"""

SPECIAL_ISSUE_FIT = """
The paper fits the Critical Challenges in GeoAI theme by addressing evaluation
paradigms, robustness, uncertainty, reproducibility, and constructive pathways
for responsible GeoAI map generation. Rather than centering a new generator, it
develops a cross-paradigm reliability scaffold that can help researchers,
reviewers, and system builders diagnose whether generated maps satisfy the
cartographic obligations implied by their artifact type.
"""

CONTRIBUTIONS = [
    "Defines generated maps as artifact chains that link data, prompts, conditioning inputs, generated objects, rendered outputs, validation traces, and repair histories.",
    "Implements a cross-paradigm reliability audit spanning text-to-map images, remote-sensing-to-map tiles, and LLM/code-generated choropleth maps.",
    "Shows empirically that reliability requires artifact-specific checks: caption grounding, cascade coverage, tile continuity, geospatial linting, screenshot-level QA, adjudication queues, and validator-gated repair.",
]

NOVELTY_CLAIMS = [
    "The paper evaluates GeoAI map generation across artifact families rather than ranking one model family.",
    "The evidence package separates data reproducibility, generated-output validity, visual/cartographic QA, and repair success.",
    "The repair experiments report validator-gated completion and safety scans, making repair itself an auditable artifact.",
]

REVIEWER_NOTES = [
    "Frame the contribution as GIScience evaluation methodology, not as a new generative model.",
    "Do not overclaim VLM outputs as ground truth; use them as pilots and adjudication queues unless human labels are collected.",
    "Keep SCGM retrieval/forest/MLP/local-context/convolutional-filter/patch/tiny-CNN baselines as diagnostic evidence unless an official or cascade-conditioned diffusion-style reproduction is added.",
]


def compact(text: str) -> str:
    paragraphs = []
    for paragraph in text.strip().split("\n\n"):
        paragraphs.append(re.sub(r"\s+", " ", paragraph.strip()))
    return "\n\n".join(paragraphs)


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w-]+\b", text))


def bullet_list(items: list[str]) -> list[str]:
    return [f"- {item}" for item in items]


def build_markdown() -> str:
    short = compact(SHORT_ABSTRACT)
    extended = compact(EXTENDED_ABSTRACT)
    significance = compact(SIGNIFICANCE)
    fit = compact(SPECIAL_ISSUE_FIT)
    lines = [
        "# Submission Abstract Pack",
        "",
        "Prepared for the selected submission path.",
        "",
        "## Portal Fields",
        "",
        f"**Title:** {TITLE}",
        "",
        f"**Keywords:** {', '.join(KEYWORDS)}",
        "",
        f"**Short abstract ({word_count(short)} words):**",
        "",
        short,
        "",
        f"**Significance statement ({word_count(significance)} words):**",
        "",
        significance,
        "",
        f"**Special-issue fit statement ({word_count(fit)} words):**",
        "",
        fit,
        "",
        "## Contribution Bullets",
        "",
        *bullet_list(CONTRIBUTIONS),
        "",
        "## Reviewer-Facing Novelty Claims",
        "",
        *bullet_list(NOVELTY_CLAIMS),
        "",
        "## Guardrails Before Submission",
        "",
        *bullet_list(REVIEWER_NOTES),
        "",
        f"## Extended Abstract ({word_count(extended)} words)",
        "",
        extended,
        "",
        "## Current Deadline Context",
        "",
        "- Special-issue abstract deadline recorded in the target pack: 01 August 2026.",
        "- Full manuscript deadline recorded in the target pack: 01 December 2026.",
        "- Recheck the publisher call page immediately before upload.",
        "",
    ]
    return "\n".join(lines)


def build_fields() -> list[dict[str, str]]:
    short = compact(SHORT_ABSTRACT)
    extended = compact(EXTENDED_ABSTRACT)
    significance = compact(SIGNIFICANCE)
    fit = compact(SPECIAL_ISSUE_FIT)
    return [
        {"field": "title", "value": TITLE, "word_count": str(word_count(TITLE))},
        {"field": "keywords", "value": "; ".join(KEYWORDS), "word_count": str(len(KEYWORDS))},
        {"field": "short_abstract", "value": short, "word_count": str(word_count(short))},
        {"field": "extended_abstract", "value": extended, "word_count": str(word_count(extended))},
        {"field": "significance_statement", "value": significance, "word_count": str(word_count(significance))},
        {"field": "special_issue_fit", "value": fit, "word_count": str(word_count(fit))},
        {"field": "contribution_bullets", "value": " | ".join(CONTRIBUTIONS), "word_count": str(len(CONTRIBUTIONS))},
        {"field": "novelty_claims", "value": " | ".join(NOVELTY_CLAIMS), "word_count": str(len(NOVELTY_CLAIMS))},
    ]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "submission_abstract_pack.md").write_text(build_markdown(), encoding="utf-8")
    with (OUT_DIR / "submission_abstract_fields.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["field", "value", "word_count"])
        writer.writeheader()
        writer.writerows(build_fields())
    print(f"Wrote {OUT_DIR.relative_to(ROOT)}/submission_abstract_pack.md")
    print(f"Wrote {OUT_DIR.relative_to(ROOT)}/submission_abstract_fields.csv")


if __name__ == "__main__":
    main()
