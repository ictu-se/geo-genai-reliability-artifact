#!/usr/bin/env python3
"""Proxy caption-fidelity review for MapGenerator image-description pairs.

This is a deterministic pre-VLM review. It compares caption mentions with
simple image-derived signals for water, green areas, and visual detail.
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageStat


ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT / "data/raw/MapGenerator"
OUT_DIR = ROOT / "experiments/02_mapgenerator_image_text_audit/outputs"
AUDIT_CSV = OUT_DIR / "mapgenerator_pairs_audit.csv"


def read_rows() -> list[dict[str, str]]:
    with AUDIT_CSV.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def select_review_sample(rows: list[dict[str, str]], per_split: int = 100) -> list[dict[str, str]]:
    sample = []
    for split in sorted({row["split"] for row in rows}):
        split_rows = [row for row in rows if row["split"] == split]
        flagged = [row for row in split_rows if row["heuristic_quality_flags"]]
        unflagged = [row for row in split_rows if not row["heuristic_quality_flags"]]
        flagged.sort(key=lambda row: (-len(row["heuristic_quality_flags"].split(";")), row["image"]))
        unflagged.sort(key=lambda row: row["image"])
        flagged_n = min(len(flagged), per_split // 2)
        unflagged_n = min(len(unflagged), per_split - flagged_n)
        sample.extend(flagged[:flagged_n])
        sample.extend(unflagged[:unflagged_n])
    return sample


def image_proxy_metrics(path: Path) -> dict[str, float | int]:
    with Image.open(path) as image:
        rgb = image.convert("RGB").resize((256, 256))
    pixels = list(rgb.getdata())
    total = len(pixels)
    blue = 0
    green = 0
    dark = 0
    bright_low_sat = 0
    for r, g, b in pixels:
        max_c = max(r, g, b)
        min_c = min(r, g, b)
        if b > 145 and b > r + 18 and b > g + 8:
            blue += 1
        if g > 120 and g > r + 8 and g > b + 8:
            green += 1
        if max_c < 95:
            dark += 1
        if max_c > 180 and max_c - min_c < 28:
            bright_low_sat += 1

    gray = rgb.convert("L")
    edges = gray.filter(ImageFilter.FIND_EDGES)
    edge_stat = ImageStat.Stat(edges)
    edge_mean = float(edge_stat.mean[0])
    return {
        "blue_ratio": round(blue / total, 4),
        "green_ratio": round(green / total, 4),
        "dark_ratio": round(dark / total, 4),
        "bright_low_sat_ratio": round(bright_low_sat / total, 4),
        "edge_mean": round(edge_mean, 3),
    }


def bool_value(row: dict[str, str], key: str) -> bool:
    return row.get(key) == "True"


def review_one(row: dict[str, str]) -> dict[str, str]:
    img_path = DATA_DIR / row["split"] / "Images" / row["image"]
    metrics = image_proxy_metrics(img_path)
    issues = []
    strengths = []

    mentions_water = bool_value(row, "mentions_water")
    mentions_green = bool_value(row, "mentions_green_area")
    mentions_road = bool_value(row, "mentions_road")
    mentions_direction = bool_value(row, "mentions_direction")
    mentions_intersection = bool_value(row, "mentions_intersection")
    named_count = int(row["named_feature_count"])
    word_count = int(row["word_count"])

    if mentions_water and metrics["blue_ratio"] < 0.003:
        issues.append("water_mention_low_blue_signal")
    if not mentions_water and metrics["blue_ratio"] >= 0.025:
        issues.append("possible_water_omission")
    if mentions_green and metrics["green_ratio"] < 0.035:
        issues.append("green_mention_low_green_signal")
    if not mentions_green and metrics["green_ratio"] >= 0.22:
        issues.append("possible_green_omission")
    if row["generic_no_feature_claim"] == "True" and (metrics["blue_ratio"] >= 0.012 or metrics["green_ratio"] >= 0.18 or metrics["dark_ratio"] >= 0.015):
        issues.append("generic_no_feature_claim_needs_visual_review")
    if named_count == 0 and metrics["dark_ratio"] >= 0.012:
        issues.append("no_named_feature_but_textlike_detail")
    if not mentions_direction and not mentions_intersection and mentions_road and metrics["edge_mean"] >= 8.0:
        issues.append("road_caption_lacks_relation")
    if word_count < 30:
        issues.append("short_caption")

    if named_count > 0:
        strengths.append("named_feature_present")
    if mentions_direction or mentions_intersection:
        strengths.append("spatial_relation_present")
    if mentions_water == (metrics["blue_ratio"] >= 0.006):
        strengths.append("water_signal_consistent")
    if mentions_green == (metrics["green_ratio"] >= 0.08):
        strengths.append("green_signal_consistent")

    severity = "low"
    if len(issues) >= 3:
        severity = "high"
    elif len(issues) >= 1:
        severity = "medium"

    score = max(0.0, 1.0 - 0.18 * len(issues))
    if "named_feature_present" in strengths:
        score += 0.05
    if "spatial_relation_present" in strengths:
        score += 0.05
    score = min(1.0, round(score, 3))

    return {
        "split": row["split"],
        "image": row["image"],
        "word_count": row["word_count"],
        "named_feature_count": row["named_feature_count"],
        "heuristic_quality_flags": row["heuristic_quality_flags"],
        "caption_mentions_water": str(mentions_water),
        "caption_mentions_green": str(mentions_green),
        "caption_mentions_road": str(mentions_road),
        "caption_has_relation": str(mentions_direction or mentions_intersection),
        **{key: str(value) for key, value in metrics.items()},
        "proxy_issues": ";".join(issues),
        "proxy_strengths": ";".join(strengths),
        "review_severity": severity,
        "proxy_fidelity_score": f"{score:.3f}",
        "description": row["description"],
    }


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def summarize(rows: list[dict[str, str]]) -> dict[str, object]:
    by_split = defaultdict(list)
    for row in rows:
        by_split[row["split"]].append(row)
    summary: dict[str, object] = {}
    for split, split_rows in sorted(by_split.items()):
        severity = Counter(row["review_severity"] for row in split_rows)
        issues = Counter()
        for row in split_rows:
            for issue in row["proxy_issues"].split(";"):
                if issue:
                    issues[issue] += 1
        scores = [float(row["proxy_fidelity_score"]) for row in split_rows]
        summary[split] = {
            "reviewed_pairs": len(split_rows),
            "mean_proxy_fidelity_score": round(sum(scores) / len(scores), 3) if scores else 0,
            "severity_counts": dict(severity),
            "top_proxy_issues": dict(issues.most_common(10)),
        }
    return summary


def wrap_text(text: str, max_chars: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        candidate = " ".join(current + [word])
        if len(candidate) > max_chars and current:
            lines.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        lines.append(" ".join(current))
    return lines


def write_proxy_contact_sheet(rows: list[dict[str, str]]) -> None:
    selected = sorted(rows, key=lambda row: (row["review_severity"] != "high", float(row["proxy_fidelity_score"]), row["image"]))[:16]
    if not selected:
        return

    thumb = 210
    caption_h = 230
    pad = 18
    cols = 3
    cell_w = thumb + pad * 2
    cell_h = thumb + caption_h + pad * 2
    sheet = Image.new("RGB", (cols * cell_w, ((len(selected) + cols - 1) // cols) * cell_h), "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for i, row in enumerate(selected):
        x = (i % cols) * cell_w + pad
        y = (i // cols) * cell_h + pad
        img_path = DATA_DIR / row["split"] / "Images" / row["image"]
        with Image.open(img_path) as image:
            image = image.convert("RGB")
            image.thumbnail((thumb, thumb))
            sheet.paste(image, (x, y))
        text_y = y + thumb + 8
        draw.text((x, text_y), f"{row['split']} / {row['image']}", fill=(0, 0, 0), font=font)
        draw.text((x, text_y + 14), f"score {row['proxy_fidelity_score']} / {row['review_severity']}", fill=(140, 0, 0), font=font)
        issue_text = row["proxy_issues"] or "no proxy issue"
        for j, line in enumerate(wrap_text(issue_text.replace(";", ", "), 50)[:4]):
            draw.text((x, text_y + 32 + j * 13), line, fill=(40, 40, 40), font=font)
        for j, line in enumerate(wrap_text(row["description"], 50)[:8]):
            draw.text((x, text_y + 92 + j * 14), line, fill=(70, 70, 70), font=font)
    sheet.save(OUT_DIR / "mapgenerator_proxy_review_contact_sheet.jpg", quality=90)


def write_report(rows: list[dict[str, str]], summary: dict[str, object]) -> None:
    lines = [
        "# MapGenerator Proxy Caption-Fidelity Review",
        "",
        "This review uses deterministic image proxies rather than a VLM or human labels. It is designed to prioritize cases for deeper review and to provide a reproducible pre-screening layer.",
        "",
        "## Summary",
        "",
    ]
    for split, info in summary.items():
        assert isinstance(info, dict)
        lines += [
            f"### {split}",
            "",
            f"- reviewed pairs: {info['reviewed_pairs']}",
            f"- mean proxy fidelity score: {info['mean_proxy_fidelity_score']}",
            f"- severity counts: {info['severity_counts']}",
            f"- top proxy issues: {info['top_proxy_issues']}",
            "",
        ]
    lines += [
        "## Highest-Severity Proxy Mismatches",
        "",
        "| Split | Image | Score | Severity | Proxy issues | Caption |",
        "|---|---|---:|---|---|---|",
    ]
    selected = sorted(rows, key=lambda row: (row["review_severity"] != "high", float(row["proxy_fidelity_score"]), row["image"]))[:30]
    for row in selected:
        desc = row["description"].replace("|", "\\|")
        if len(desc) > 160:
            desc = desc[:157] + "..."
        lines.append(
            f"| {row['split']} | `{row['image']}` | {row['proxy_fidelity_score']} | {row['review_severity']} | {row['proxy_issues']} | {desc} |"
        )
    lines += [
        "",
        "## Interpretation",
        "",
        "- Proxy issues are candidate mismatches, not ground-truth errors.",
        "- The most useful signals are omissions or unsupported claims for water/green areas and generic no-feature statements on visually rich maps.",
        "- A Q1 submission should replace or validate this layer with VLM/human labels on the same sampled pairs.",
        "",
    ]
    (OUT_DIR / "mapgenerator_proxy_caption_review.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = select_review_sample(read_rows())
    reviewed = [review_one(row) for row in rows]
    summary = summarize(reviewed)
    write_csv(OUT_DIR / "mapgenerator_proxy_caption_review.csv", reviewed)
    (OUT_DIR / "mapgenerator_proxy_caption_review_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_proxy_contact_sheet(reviewed)
    write_report(reviewed, summary)
    print(f"Wrote {(OUT_DIR / 'mapgenerator_proxy_caption_review.csv').relative_to(ROOT)}")
    print(f"Wrote {(OUT_DIR / 'mapgenerator_proxy_caption_review_summary.json').relative_to(ROOT)}")
    print(f"Wrote {(OUT_DIR / 'mapgenerator_proxy_caption_review.md').relative_to(ROOT)}")


if __name__ == "__main__":
    main()
