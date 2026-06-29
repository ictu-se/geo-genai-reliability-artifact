#!/usr/bin/env python3
"""Audit MapGenerator image-caption pairs without external model calls."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT / "data/raw/MapGenerator"
OUT_DIR = ROOT / "experiments/02_mapgenerator_image_text_audit/outputs"


FEATURE_KEYWORDS = {
    "road": ["road", "rd", "street", "st", "avenue", "ave", "lane", "ln", "drive", "dr", "highway", "route"],
    "intersection": ["intersect", "junction", "crossroad", "corner"],
    "water": ["water", "river", "creek", "lake", "pond", "stream", "canal"],
    "green_area": ["green", "park", "vegetation", "wood", "forest", "rural", "undeveloped"],
    "building_poi": ["building", "school", "church", "facility", "landmark", "icon", "business"],
    "label": ["labeled", "label", "named"],
    "direction": ["north", "south", "east", "west", "top", "bottom", "left", "right", "diagonal", "vertical", "horizontal"],
}


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    mapping = {}
    for col in df.columns:
        low = col.strip().lower()
        if low == "images":
            mapping[col] = "image"
        elif low in {"descriptions", "description"}:
            mapping[col] = "description"
    return df.rename(columns=mapping)


def feature_flags(text: str) -> dict[str, bool]:
    low = text.lower()
    flags = {}
    for name, words in FEATURE_KEYWORDS.items():
        flags[name] = any(re.search(rf"\b{re.escape(word)}\b", low) for word in words)
    return flags


def inspect_image(path: Path) -> dict[str, str | int | bool]:
    if not path.exists():
        return {"image_exists": False, "width": "", "height": "", "mode": "", "bytes": ""}
    with Image.open(path) as img:
        width, height = img.size
        mode = img.mode
    return {
        "image_exists": True,
        "width": width,
        "height": height,
        "mode": mode,
        "bytes": path.stat().st_size,
    }


def audit_split(split: str) -> list[dict[str, str]]:
    xlsx = DATA_DIR / split / "descriptions.xlsx"
    df = normalize_columns(pd.read_excel(xlsx))
    rows: list[dict[str, str]] = []
    for idx, rec in df.iterrows():
        image_name = str(rec["image"]).strip()
        desc = str(rec["description"]).strip()
        img_path = DATA_DIR / split / "Images" / image_name
        img = inspect_image(img_path)
        flags = feature_flags(desc)
        word_count = len(re.findall(r"\w+", desc))
        named_suffix_count = len(
            re.findall(
                r"\b[A-Z][A-Za-z0-9'.-]*(?:\s+[A-Z][A-Za-z0-9'.-]*)*\s+"
                r"(?:Road|Rd|Street|St|Avenue|Ave|Lane|Ln|Drive|Dr|Highway|Route|Way|Court|Ct|"
                r"Creek|River|Lake|Bay|Reservoir|Canyon|Valley|Branch|Gulch)\b",
                desc,
            )
        )
        quoted_label_count = len(re.findall(r'"[^"]{3,80}"', desc))
        named_feature_count = named_suffix_count + quoted_label_count
        generic_no_feature = "no additional geographic" in desc.lower() or "without additional geographic" in desc.lower()
        row = {
            "split": split,
            "row_index": str(idx),
            "image": image_name,
            "description": desc,
            "word_count": str(word_count),
            "named_feature_count": str(named_feature_count),
            "generic_no_feature_claim": str(generic_no_feature),
        }
        row.update({k: str(v) for k, v in img.items()})
        row.update({f"mentions_{k}": str(v) for k, v in flags.items()})
        row["heuristic_quality_flags"] = ";".join(
            flag
            for flag, cond in [
                ("missing_image", not img["image_exists"]),
                ("short_caption", word_count < 25),
                ("no_named_feature", named_feature_count == 0),
                ("no_direction_or_relation", not flags["direction"] and not flags["intersection"]),
                ("generic_no_feature_claim", generic_no_feature),
            ]
            if cond
        )
        rows.append(row)
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def build_summary(rows: list[dict[str, str]]) -> dict[str, object]:
    by_split: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        by_split.setdefault(row["split"], []).append(row)
    summary: dict[str, object] = {}
    for split, split_rows in by_split.items():
        flag_counter = Counter()
        feature_counter = Counter()
        dimensions = Counter()
        for row in split_rows:
            for flag in row["heuristic_quality_flags"].split(";"):
                if flag:
                    flag_counter[flag] += 1
            for key in row:
                if key.startswith("mentions_") and row[key] == "True":
                    feature_counter[key.removeprefix("mentions_")] += 1
            dimensions[f"{row['width']}x{row['height']}"] += 1
        word_counts = [int(row["word_count"]) for row in split_rows]
        summary[split] = {
            "pairs": len(split_rows),
            "missing_images": sum(row["image_exists"] != "True" for row in split_rows),
            "unique_images": len({row["image"] for row in split_rows}),
            "avg_word_count": round(sum(word_counts) / len(word_counts), 2) if word_counts else 0,
            "min_word_count": min(word_counts) if word_counts else 0,
            "max_word_count": max(word_counts) if word_counts else 0,
            "feature_mentions": dict(feature_counter),
            "quality_flags": dict(flag_counter),
            "image_dimensions": dict(dimensions),
        }
    return summary


def write_report(rows: list[dict[str, str]], summary: dict[str, object]) -> None:
    lines = [
        "# MapGenerator Image-Text Audit",
        "",
        "This audit checks released image-description pairs with file-level and text heuristics. It does not use CLIP/VLM scoring yet.",
        "",
        "## Summary",
        "",
    ]
    for split, info in summary.items():
        assert isinstance(info, dict)
        lines += [
            f"### {split}",
            "",
            f"- pairs: {info['pairs']}",
            f"- unique images: {info['unique_images']}",
            f"- missing images: {info['missing_images']}",
            f"- average caption length: {info['avg_word_count']} words",
            f"- image dimensions: {info['image_dimensions']}",
            f"- feature mentions: {info['feature_mentions']}",
            f"- heuristic quality flags: {info['quality_flags']}",
            "",
        ]

    flagged = [row for row in rows if row["heuristic_quality_flags"]]
    flagged.sort(key=lambda r: (r["split"], len(r["heuristic_quality_flags"].split(";")), int(r["word_count"])), reverse=True)
    lines += [
        "## Highest-Priority Manual Review Candidates",
        "",
        "| Split | Image | Flags | Words | Caption |",
        "|---|---|---|---:|---|",
    ]
    for row in flagged[:30]:
        desc = row["description"].replace("|", "\\|")
        if len(desc) > 180:
            desc = desc[:177] + "..."
        lines.append(f"| {row['split']} | `{row['image']}` | {row['heuristic_quality_flags']} | {row['word_count']} | {desc} |")

    lines += [
        "",
        "## Interpretation",
        "",
        "- The local release has 750 MapTrain descriptions and 100 MGEval descriptions.",
        "- The current audit is a reproducibility/data-quality layer; model-based alignment scoring should be added next.",
        "- Captions are generally descriptive, but generic claims such as no additional geographic features need visual verification.",
        "- Named-feature and relation heuristics identify candidates for VLM/manual review, not definitive errors.",
        "",
    ]
    (OUT_DIR / "mapgenerator_audit_report.md").write_text("\n".join(lines), encoding="utf-8")


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


def write_contact_sheet(rows: list[dict[str, str]]) -> None:
    flagged = [row for row in rows if row["heuristic_quality_flags"]]
    flagged.sort(key=lambda r: (len(r["heuristic_quality_flags"].split(";")), int(r["word_count"])), reverse=True)
    selected = flagged[:16]
    if not selected:
        return

    thumb = 180
    caption_h = 150
    pad = 16
    cols = 4
    rows_n = (len(selected) + cols - 1) // cols
    cell_w = thumb + pad * 2
    cell_h = thumb + caption_h + pad * 2
    sheet = Image.new("RGB", (cols * cell_w, rows_n * cell_h), "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()

    for i, row in enumerate(selected):
        x = (i % cols) * cell_w + pad
        y = (i // cols) * cell_h + pad
        img_path = DATA_DIR / row["split"] / "Images" / row["image"]
        with Image.open(img_path) as img:
            img = img.convert("RGB")
            img.thumbnail((thumb, thumb))
            sheet.paste(img, (x, y))
        text_y = y + thumb + 8
        draw.text((x, text_y), f"{row['split']} / {row['image']}", fill=(0, 0, 0), font=font)
        draw.text((x, text_y + 14), row["heuristic_quality_flags"][:42], fill=(150, 0, 0), font=font)
        desc_lines = wrap_text(row["description"], 42)[:7]
        for j, line in enumerate(desc_lines):
            draw.text((x, text_y + 32 + j * 13), line, fill=(40, 40, 40), font=font)

    sheet.save(OUT_DIR / "mapgenerator_flagged_contact_sheet.jpg", quality=90)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = audit_split("MapTrain") + audit_split("MGEval")
    summary = build_summary(rows)
    write_csv(OUT_DIR / "mapgenerator_pairs_audit.csv", rows)
    (OUT_DIR / "mapgenerator_audit_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_report(rows, summary)
    write_contact_sheet(rows)
    print(f"Wrote {OUT_DIR.relative_to(ROOT)}/mapgenerator_pairs_audit.csv")
    print(f"Wrote {OUT_DIR.relative_to(ROOT)}/mapgenerator_audit_summary.json")
    print(f"Wrote {OUT_DIR.relative_to(ROOT)}/mapgenerator_audit_report.md")
    print(f"Wrote {OUT_DIR.relative_to(ROOT)}/mapgenerator_flagged_contact_sheet.jpg")


if __name__ == "__main__":
    main()
