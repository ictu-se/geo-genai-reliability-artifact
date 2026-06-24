#!/usr/bin/env python3
"""Audit released choropleth/static/interactive map artifacts."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

from PIL import Image, ImageStat


ROOT = Path(__file__).resolve().parents[3]
REPO_DIR = ROOT / "data/repos/Materials-for-Creating-maps-by-Artificial-Intelligence"
OUT_DIR = ROOT / "experiments/01_choropleth_llm_linter/outputs"


def classify_static(path: Path) -> tuple[str, str]:
    parts = path.parts
    prompt = "unknown"
    map_type = "unknown"
    if "Basic_Promptpattern" in parts:
        prompt = "basic"
    elif "Advanced_Promptpattern" in parts:
        prompt = "advanced"
    elif "ArcGISmaps" in parts:
        prompt = "arcgis_reference"
    name = path.name.lower()
    if "choro" in name:
        map_type = "choropleth"
    elif "dotden" in name:
        map_type = "dot_density"
    elif "graduated" in name:
        map_type = "graduated_symbol"
    elif "layout" in name:
        map_type = "reference_layout"
    return prompt, map_type


def classify_html(path: Path) -> tuple[str, str]:
    parts = path.parts
    prompt = "advanced" if "Advanced_Promptpattern" in parts else "basic" if "Basic_Promptpattern" in parts else "unknown"
    return prompt, "interactive_choropleth"


def image_nonblank_score(path: Path) -> float:
    with Image.open(path) as img:
        rgb = img.convert("RGB")
        stat = ImageStat.Stat(rgb)
        return float(sum(stat.stddev))


def audit_png(path: Path) -> dict[str, str]:
    prompt, map_type = classify_static(path)
    with Image.open(path) as img:
        width, height = img.size
        mode = img.mode
    nonblank = image_nonblank_score(path)
    return {
        "artifact_type": "png",
        "prompt_pattern": prompt,
        "map_type": map_type,
        "path": str(path.relative_to(ROOT)),
        "bytes": str(path.stat().st_size),
        "width": str(width),
        "height": str(height),
        "mode": mode,
        "nonblank_score": f"{nonblank:.3f}",
        "has_title_hint": str(any(word in path.name.lower() for word in ("choro", "dotden", "graduated", "layout"))),
        "qa_flags": ";".join(
            flag
            for flag, cond in [
                ("empty_file", path.stat().st_size == 0),
                ("small_image", width < 500 or height < 400),
                ("possibly_blank", nonblank < 5),
            ]
            if cond
        ),
    }


def audit_html(path: Path) -> dict[str, str]:
    prompt, map_type = classify_html(path)
    text = path.read_text(encoding="utf-8", errors="ignore")
    low = text.lower()
    script_count = len(re.findall(r"<script\b", low))
    style_count = len(re.findall(r"<style\b", low))
    return {
        "artifact_type": "html",
        "prompt_pattern": prompt,
        "map_type": map_type,
        "path": str(path.relative_to(ROOT)),
        "bytes": str(path.stat().st_size),
        "width": "",
        "height": "",
        "mode": "",
        "nonblank_score": "",
        "has_leaflet": str("leaflet" in low),
        "has_geojson": str("geojson" in low),
        "has_legend_hint": str("legend" in low or "burned" in low or "fires" in low),
        "script_count": str(script_count),
        "style_count": str(style_count),
        "qa_flags": ";".join(
            flag
            for flag, cond in [
                ("empty_file", path.stat().st_size == 0),
                ("missing_leaflet_hint", "leaflet" not in low),
                ("missing_geojson_hint", "geojson" not in low),
                ("missing_legend_hint", not ("legend" in low or "burned" in low or "fires" in low)),
            ]
            if cond
        ),
    }


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        return
    fields = sorted({key for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def summarize(rows: list[dict[str, str]]) -> dict[str, object]:
    summary: dict[str, object] = {"total_artifacts": len(rows)}
    for key in ("artifact_type", "prompt_pattern", "map_type"):
        counts: dict[str, int] = {}
        for row in rows:
            counts[row.get(key, "")] = counts.get(row.get(key, ""), 0) + 1
        summary[key] = counts
    flag_counts: dict[str, int] = {}
    for row in rows:
        for flag in row.get("qa_flags", "").split(";"):
            if flag:
                flag_counts[flag] = flag_counts.get(flag, 0) + 1
    summary["qa_flags"] = flag_counts
    return summary


def write_report(rows: list[dict[str, str]], summary: dict[str, object]) -> None:
    flagged = [row for row in rows if row.get("qa_flags")]
    lines = [
        "# Released Choropleth Artifact Audit",
        "",
        "This audit checks the static and interactive map artifacts released with the ChatGPT choropleth materials.",
        "",
        "## Summary",
        "",
        f"- total artifacts: {summary['total_artifacts']}",
        f"- artifact types: {summary['artifact_type']}",
        f"- prompt patterns: {summary['prompt_pattern']}",
        f"- map types: {summary['map_type']}",
        f"- QA flags: {summary['qa_flags']}",
        "",
        "## Flagged Artifacts",
        "",
        "| Artifact | Prompt | Type | Flags |",
        "|---|---|---|---|",
    ]
    if flagged:
        for row in flagged:
            lines.append(f"| `{row['path']}` | {row['prompt_pattern']} | {row['map_type']} | {row['qa_flags']} |")
    else:
        lines.append("| _none_ | | | |")
    lines += [
        "",
        "## Interpretation",
        "",
        "- Static PNGs and interactive HTML files are present for both basic and advanced prompt patterns.",
        "- This file-level audit is intentionally conservative: it detects missing/empty/blank artifacts and coarse HTML structure only.",
        "- The next useful step is screenshot-based cartographic QA: title, legend, color ramp, classification, readable labels, and source note.",
        "",
    ]
    (OUT_DIR / "released_map_artifact_audit.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []
    for path in sorted((REPO_DIR / "StaticMaps").rglob("*.png")):
        rows.append(audit_png(path))
    for path in sorted((REPO_DIR / "InteractiveMaps").rglob("*.html")):
        rows.append(audit_html(path))
    summary = summarize(rows)
    write_csv(OUT_DIR / "released_map_artifact_audit.csv", rows)
    (OUT_DIR / "released_map_artifact_audit_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_report(rows, summary)
    print(f"Wrote {OUT_DIR.relative_to(ROOT)}/released_map_artifact_audit.csv")
    print(f"Wrote {OUT_DIR.relative_to(ROOT)}/released_map_artifact_audit_summary.json")
    print(f"Wrote {OUT_DIR.relative_to(ROOT)}/released_map_artifact_audit.md")


if __name__ == "__main__":
    main()

