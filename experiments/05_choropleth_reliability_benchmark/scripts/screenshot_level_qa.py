#!/usr/bin/env python3
"""Screenshot-level QA for choropleth rendered artifacts."""

from __future__ import annotations

import csv
import json
import math
import re
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageStat
from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[3]
EXP_DIR = ROOT / "experiments/05_choropleth_reliability_benchmark"
RUN_ROOT = EXP_DIR / "outputs/runs"
REFERENCE_DIR = EXP_DIR / "outputs/reference_baseline"
OUT_DIR = EXP_DIR / "outputs/scores"
SHOT_DIR = OUT_DIR / "screenshot_qa"


def source_label(meta: dict[str, object], manifest_path: Path) -> str:
    repair_model = manifest_path.parent.name if manifest_path.name == "repair_run_manifest.json" else ""
    if repair_model:
        return f"repair_{repair_model}:{meta['model']}:{meta['mode']}:{meta['prompt_id']}"
    return f"{meta['model']}:{meta['mode']}:{meta['prompt_id']}"


def artifact_sources() -> list[dict[str, str]]:
    sources = [
        {"source": "reference", "run_dir": str(REFERENCE_DIR.relative_to(ROOT)), "artifact_origin": "reference"},
    ]
    manifests = sorted(list(RUN_ROOT.glob("*/run_manifest.json")) + list(RUN_ROOT.glob("*/repair_run_manifest.json")))
    for manifest_path in manifests:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for meta in manifest:
            sources.append(
                {
                    "source": source_label(meta, manifest_path),
                    "run_dir": meta["run_dir"],
                    "artifact_origin": "repair" if manifest_path.name == "repair_run_manifest.json" else "initial",
                }
            )
    return sources


def safe_name(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", text)[:180]


def render_html(path: Path, out_path: Path) -> tuple[bool, str]:
    if not path.exists() or path.stat().st_size == 0:
        return False, "missing"
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1200, "height": 850}, device_scale_factor=1)
            page.goto(path.resolve().as_uri(), wait_until="networkidle", timeout=15000)
            page.screenshot(path=str(out_path), full_page=True)
            browser.close()
        return True, ""
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


def image_qa(path: Path) -> dict[str, str]:
    if not path.exists() or path.stat().st_size == 0:
        return {
            "exists": str(path.exists()),
            "bytes": str(path.stat().st_size if path.exists() else 0),
            "qa_pass": "False",
            "qa_fail_reasons": "missing_or_empty",
        }
    with Image.open(path) as img:
        rgb = img.convert("RGB")
    arr = np.asarray(rgb)
    width, height = rgb.size
    stat = ImageStat.Stat(rgb)
    extrema = rgb.getextrema()
    dynamic_range = max(high - low for low, high in extrema)
    mean_rgb = sum(stat.mean) / 3
    nonwhite = np.mean(np.any(arr < 245, axis=2))
    nondark = np.mean(np.any(arr > 30, axis=2))
    quant = (arr // 32).reshape(-1, 3)
    unique_colors = len({tuple(x) for x in quant[:: max(1, len(quant) // 20000)]})
    gray = rgb.convert("L")
    edges = gray.filter(ImageFilter.FIND_EDGES)
    edge_mean = float(ImageStat.Stat(edges).mean[0])
    dark_textlike = np.mean(np.max(arr, axis=2) < 90)

    reasons = []
    if width < 300 or height < 250:
        reasons.append("too_small")
    if dynamic_range <= 20:
        reasons.append("low_dynamic_range")
    if nonwhite <= 0.015:
        reasons.append("mostly_white")
    if nondark <= 0.2:
        reasons.append("mostly_dark_or_blank")
    if unique_colors < 8:
        reasons.append("low_color_diversity")
    if edge_mean < 1.5:
        reasons.append("low_edge_detail")
    qa_pass = not reasons
    return {
        "exists": "True",
        "bytes": str(path.stat().st_size),
        "width": str(width),
        "height": str(height),
        "dynamic_range": str(dynamic_range),
        "mean_rgb": f"{mean_rgb:.3f}",
        "nonwhite_ratio": f"{nonwhite:.4f}",
        "nondark_ratio": f"{nondark:.4f}",
        "unique_color_bins": str(unique_colors),
        "edge_mean": f"{edge_mean:.3f}",
        "dark_textlike_ratio": f"{dark_textlike:.4f}",
        "qa_pass": str(qa_pass),
        "qa_fail_reasons": ";".join(reasons),
    }


def audit() -> list[dict[str, str]]:
    SHOT_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []
    for src in artifact_sources():
        run_dir = ROOT / src["run_dir"]
        for artifact, kind in [
            ("map_static.png", "static_png"),
            ("time_series.png", "time_series_png"),
            ("map_interactive.html", "interactive_html"),
        ]:
            artifact_path = run_dir / artifact
            screenshot_path = ""
            render_ok = ""
            render_error = ""
            qa_target = artifact_path
            if kind == "interactive_html":
                shot = SHOT_DIR / f"{safe_name(src['source'])}_{safe_name(Path(src['run_dir']).name)}_interactive.png"
                ok, error = render_html(artifact_path, shot)
                render_ok = str(ok)
                render_error = error
                if ok:
                    screenshot_path = str(shot.relative_to(ROOT))
                    qa_target = shot
            metrics = image_qa(qa_target) if kind != "interactive_html" or render_ok == "True" else image_qa(artifact_path)
            rows.append(
                {
                    "source": src["source"],
                    "source_group": src["source"].split(":", 1)[0],
                    "artifact_origin": src["artifact_origin"],
                    "run_dir": src["run_dir"],
                    "artifact": artifact,
                    "kind": kind,
                    "artifact_path": str(artifact_path.relative_to(ROOT)),
                    "screenshot_path": screenshot_path,
                    "html_render_ok": render_ok,
                    "html_render_error": render_error,
                    **metrics,
                }
            )
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fields = sorted({key for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def summarize(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[(row["source_group"], row["kind"])].append(row)
    out = []
    for (source_group, kind), group in sorted(grouped.items()):
        existing = sum(row.get("exists") == "True" for row in group)
        qa_pass = sum(row.get("qa_pass") == "True" for row in group)
        rendered = sum(row.get("html_render_ok") == "True" for row in group)
        out.append(
            {
                "source_group": source_group,
                "kind": kind,
                "checked": str(len(group)),
                "existing": str(existing),
                "html_rendered": str(rendered) if kind == "interactive_html" else "",
                "screenshot_qa_pass": str(qa_pass),
                "pass_rate_existing": f"{qa_pass / existing:.3f}" if existing else "0.000",
            }
        )
    return out


def contact_sheet(rows: list[dict[str, str]]) -> None:
    candidates = [
        row
        for row in rows
        if row["kind"] in {"static_png", "time_series_png", "interactive_html"}
        and row.get("qa_pass") == "True"
        and (row.get("screenshot_path") or Path(row["artifact_path"]).suffix == ".png")
    ]
    candidates.sort(key=lambda row: (row["source_group"] != "reference", row["source_group"], row["kind"], row["source"]))
    selected = candidates[:24]
    if not selected:
        return
    thumb_w, thumb_h = 240, 170
    label_h = 68
    pad = 14
    cols = 3
    rows_n = math.ceil(len(selected) / cols)
    sheet = Image.new("RGB", (cols * (thumb_w + 2 * pad), rows_n * (thumb_h + label_h + 2 * pad)), "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for idx, row in enumerate(selected):
        x = (idx % cols) * (thumb_w + 2 * pad) + pad
        y = (idx // cols) * (thumb_h + label_h + 2 * pad) + pad
        img_path = ROOT / (row["screenshot_path"] or row["artifact_path"])
        with Image.open(img_path) as img:
            img = img.convert("RGB")
            img.thumbnail((thumb_w, thumb_h))
            sheet.paste(img, (x, y))
        lines = [
            row["source_group"],
            row["kind"],
            f"edge={row.get('edge_mean', '')} colors={row.get('unique_color_bins', '')}",
        ]
        for j, line in enumerate(lines):
            draw.text((x, y + thumb_h + 6 + j * 15), line[:42], fill=(20, 20, 20), font=font)
    sheet.save(SHOT_DIR / "screenshot_qa_contact_sheet.jpg", quality=90)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = audit()
    detail_path = OUT_DIR / "screenshot_level_qa_detail.csv"
    summary_path = OUT_DIR / "screenshot_level_qa_summary.csv"
    write_csv(detail_path, rows)
    write_csv(summary_path, summarize(rows))
    contact_sheet(rows)
    print(f"Wrote {detail_path.relative_to(ROOT)}")
    print(f"Wrote {summary_path.relative_to(ROOT)}")
    print(f"Wrote {(SHOT_DIR / 'screenshot_qa_contact_sheet.jpg').relative_to(ROOT)}")


if __name__ == "__main__":
    main()
