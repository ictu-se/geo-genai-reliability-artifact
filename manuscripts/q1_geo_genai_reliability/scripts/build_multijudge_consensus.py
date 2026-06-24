#!/usr/bin/env python3
"""Build calibrated multi-judge consensus summaries from usable VLM reviews.

The outputs are evaluator-calibration artifacts. They aggregate local VLM
reviews only where a model produced parseable schema-conformant rows, and they
do not replace human labels.
"""

from __future__ import annotations

import csv
import statistics
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MS_DIR = ROOT / "manuscripts/q1_geo_genai_reliability"
TABLE_DIR = MS_DIR / "tables"
OUT_DIR = MS_DIR / "submission/evaluator_reliability"

MAPGEN_DIR = ROOT / "experiments/02_mapgenerator_image_text_audit/outputs"
CHORO_DIR = ROOT / "experiments/05_choropleth_reliability_benchmark/outputs/scores"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def model_name_from_path(path: Path, prefix: str) -> str:
    return path.stem.replace(prefix, "").replace("_", ":")


def as_float(value: str) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def boolish(value: str) -> bool:
    return value.strip().lower() == "true"


def mapgen_coarse(verdict: str) -> str:
    return "supported" if verdict == "supported" else "below_supported"


def choro_coarse(verdict: str) -> str:
    return "usable_or_minor" if verdict in {"usable", "usable_with_minor_issues"} else "below_usable"


def consensus_label(votes: list[str], positive_label: str) -> tuple[str, str, str]:
    if len(votes) < 2:
        return "insufficient_usable_reviews", "low", "0/0"
    positive = sum(vote == positive_label for vote in votes)
    negative = len(votes) - positive
    majority = positive_label if positive > negative else ("below_" + positive_label if negative > positive else "tied")
    agreement = max(positive, negative)
    agreement_fraction = f"{agreement}/{len(votes)}"
    if positive == len(votes):
        return positive_label, "high", agreement_fraction
    if negative == len(votes):
        return "below_" + positive_label, "high", agreement_fraction
    if agreement >= 2:
        return majority, "medium", agreement_fraction
    return "discordant", "low", agreement_fraction


def score_summary(scores: list[float]) -> tuple[str, str, str]:
    if not scores:
        return "", "", ""
    mean = sum(scores) / len(scores)
    spread = statistics.pstdev(scores) if len(scores) > 1 else 0.0
    return f"{mean:.3f}", f"{min(scores):.3f}-{max(scores):.3f}", f"{spread:.3f}"


def mapgen_feature_agreement(rows: list[dict[str, str]]) -> str:
    fields = [
        "vlm_visible_water",
        "vlm_visible_roads",
        "vlm_visible_green_area",
        "vlm_visible_named_label",
    ]
    comparable = 0
    agreed = 0
    for field in fields:
        values = [row.get(field, "") for row in rows if row.get(field, "") not in {"", "None"}]
        if len(values) < 2:
            continue
        comparable += 1
        agreed += int(len(set(values)) == 1)
    return f"{agreed}/{comparable}" if comparable else "0/0"


def choro_component_agreement(rows: list[dict[str, str]]) -> str:
    fields = [
        "vlm_map_content_visible",
        "vlm_has_title",
        "vlm_has_legend_or_colorbar",
        "vlm_text_readable",
        "vlm_layout_not_occluded",
        "vlm_appears_choropleth",
    ]
    comparable = 0
    agreed = 0
    for field in fields:
        values = [row.get(field, "") for row in rows if row.get(field, "") not in {"", "None"}]
        if len(values) < 2:
            continue
        comparable += 1
        agreed += int(len(set(values)) == 1)
    return f"{agreed}/{comparable}" if comparable else "0/0"


def build_mapgen_consensus() -> list[dict[str, str]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = {}
    metadata: dict[tuple[str, str], dict[str, str]] = {}
    for path in sorted(MAPGEN_DIR.glob("mapgenerator_vlm_caption_review_*.csv")):
        model = model_name_from_path(path, "mapgenerator_vlm_caption_review_")
        for row in read_csv(path):
            if row.get("vlm_verdict") == "error" or as_float(row.get("vlm_alignment_score", "")) is None:
                continue
            key = (row["split"], row["image"])
            item = dict(row)
            item["model"] = model
            grouped.setdefault(key, []).append(item)
            metadata.setdefault(key, row)

    rows: list[dict[str, str]] = []
    for key, reviews in sorted(grouped.items()):
        votes = [mapgen_coarse(row["vlm_verdict"]) for row in reviews]
        label, confidence, vote_fraction = consensus_label(votes, "supported")
        scores = [as_float(row.get("vlm_alignment_score", "")) for row in reviews]
        score_values = [score for score in scores if score is not None]
        mean_score, score_range, score_spread = score_summary(score_values)
        meta = metadata[key]
        rows.append(
            {
                "task": "MapGenerator caption fidelity",
                "split": key[0],
                "item_id": key[1],
                "usable_judges": str(len(reviews)),
                "judge_models": ";".join(row["model"] for row in reviews),
                "coarse_votes": ";".join(votes),
                "consensus_label": label,
                "confidence_tier": confidence,
                "vote_fraction": vote_fraction,
                "mean_score": mean_score,
                "score_range": score_range,
                "score_spread": score_spread,
                "component_agreement": mapgen_feature_agreement(reviews),
                "proxy_severity": meta.get("review_severity", ""),
                "proxy_score": meta.get("proxy_fidelity_score", ""),
                "interpretation": "calibrated VLM triage; not a human label",
            }
        )
    return rows


def build_choro_consensus() -> list[dict[str, str]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    metadata: dict[str, dict[str, str]] = {}
    for path in sorted(CHORO_DIR.glob("choropleth_vlm_cartographic_review_*.csv")):
        model = model_name_from_path(path, "choropleth_vlm_cartographic_review_")
        for row in read_csv(path):
            if row.get("vlm_verdict") == "error" or as_float(row.get("vlm_cartographic_quality_score", "")) is None:
                continue
            key = row["artifact_path"]
            item = dict(row)
            item["model"] = model
            grouped.setdefault(key, []).append(item)
            metadata.setdefault(key, row)

    rows: list[dict[str, str]] = []
    for key, reviews in sorted(grouped.items()):
        votes = [choro_coarse(row["vlm_verdict"]) for row in reviews]
        label, confidence, vote_fraction = consensus_label(votes, "usable_or_minor")
        scores = [as_float(row.get("vlm_cartographic_quality_score", "")) for row in reviews]
        score_values = [score for score in scores if score is not None]
        mean_score, score_range, score_spread = score_summary(score_values)
        meta = metadata[key]
        rows.append(
            {
                "task": "Choropleth cartographic quality",
                "source_group": meta.get("source_group", ""),
                "source": meta.get("source", ""),
                "kind": meta.get("kind", ""),
                "item_id": meta.get("artifact", ""),
                "artifact_path": key,
                "usable_judges": str(len(reviews)),
                "judge_models": ";".join(row["model"] for row in reviews),
                "coarse_votes": ";".join(votes),
                "consensus_label": label,
                "confidence_tier": confidence,
                "vote_fraction": vote_fraction,
                "mean_score": mean_score,
                "score_range": score_range,
                "score_spread": score_spread,
                "component_agreement": choro_component_agreement(reviews),
                "screenshot_qa_pass": meta.get("qa_pass", ""),
                "interpretation": "calibrated VLM triage; not a human label",
            }
        )
    return rows


def summarize(task: str, rows: list[dict[str, str]]) -> dict[str, str]:
    high = [row for row in rows if row["confidence_tier"] == "high"]
    medium = [row for row in rows if row["confidence_tier"] == "medium"]
    low = [row for row in rows if row["confidence_tier"] == "low"]
    usable_counts = [int(row["usable_judges"]) for row in rows]
    positive = sum(row["consensus_label"] in {"supported", "usable_or_minor"} for row in rows)
    below = sum(row["consensus_label"].startswith("below_") for row in rows)
    discordant = sum(row["consensus_label"] in {"discordant", "tied"} for row in rows)
    insufficient = sum(row["consensus_label"] == "insufficient_usable_reviews" for row in rows)
    return {
        "Task": task,
        "Consensus items": str(len(rows)),
        "Items with at least two usable judges": str(sum(count >= 2 for count in usable_counts)),
        "High-confidence consensus": str(len(high)),
        "Medium-confidence consensus": str(len(medium)),
        "Low/insufficient consensus": str(len(low)),
        "Positive consensus": str(positive),
        "Below-threshold consensus": str(below),
        "Discordant/tied": str(discordant),
        "Insufficient usable reviews": str(insufficient),
        "Max usable judges": str(max(usable_counts) if usable_counts else 0),
        "Interpretation": "calibrated VLM triage, not human ground truth",
    }


def build_report(summary_rows: list[dict[str, str]]) -> str:
    lines = [
        "# Calibrated Multi-Judge VLM Consensus",
        "",
        "This report aggregates parseable local VLM reviews into coarse consensus tiers. It is an evaluator-calibration layer and should not be cited as human ground truth.",
        "",
        "| Task | Consensus items | >=2 usable judges | High | Medium | Low/insufficient | Positive | Below-threshold | Discordant/tied | Max judges |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary_rows:
        lines.append(
            f"| {row['Task']} | {row['Consensus items']} | {row['Items with at least two usable judges']} | {row['High-confidence consensus']} | {row['Medium-confidence consensus']} | {row['Low/insufficient consensus']} | {row['Positive consensus']} | {row['Below-threshold consensus']} | {row['Discordant/tied']} | {row['Max usable judges']} |"
        )
    lines += [
        "",
        "## Interpretation",
        "",
        "- The consensus layer uses only schema-conformant VLM outputs; failed JSON or missing scores reduce coverage rather than being imputed.",
        "- High-confidence rows indicate unanimous coarse agreement among usable judges, but they remain automated labels.",
        "- Medium and low-confidence rows identify where expert human validation should be prioritized before making semantic caption-fidelity or cartographic-quality claims.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    mapgen_rows = build_mapgen_consensus()
    choro_rows = build_choro_consensus()
    summary_rows = [
        summarize("MapGenerator caption fidelity", mapgen_rows),
        summarize("Choropleth cartographic quality", choro_rows),
    ]

    write_csv(OUT_DIR / "mapgenerator_multijudge_consensus.csv", mapgen_rows)
    write_csv(OUT_DIR / "choropleth_multijudge_consensus.csv", choro_rows)
    write_csv(OUT_DIR / "multijudge_consensus_summary.csv", summary_rows)
    write_csv(TABLE_DIR / "table_24_multijudge_vlm_consensus.csv", summary_rows)
    (OUT_DIR / "multijudge_consensus_report.md").write_text(build_report(summary_rows), encoding="utf-8")
    print(f"Wrote {(TABLE_DIR / 'table_24_multijudge_vlm_consensus.csv').relative_to(ROOT)}")
    print(f"Wrote {(OUT_DIR / 'multijudge_consensus_report.md').relative_to(ROOT)}")


if __name__ == "__main__":
    main()
