#!/usr/bin/env python3
"""Artifact and screenshot QA for iterative validator-repair runs."""

from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter, ImageStat
from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[3]
EXP_DIR = ROOT / "experiments/05_choropleth_reliability_benchmark"
RUN_ROOT = EXP_DIR / "outputs/runs_iterative_repair"
SCORES_DIR = EXP_DIR / "outputs/scores"
SHOT_DIR = SCORES_DIR / "iterative_repair_screenshot_qa"


def safe_name(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", text)[:180]


def repair_model_from_script(script: str) -> str:
    parts = Path(script).parts
    if "generated_code_iterative_repair" not in parts:
        return ""
    idx = parts.index("generated_code_iterative_repair")
    return parts[idx + 1] if idx + 1 < len(parts) else ""


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def image_metrics(path: Path) -> dict[str, str]:
    if not path.exists() or path.stat().st_size == 0:
        return {
            "exists": str(path.exists()),
            "bytes": str(path.stat().st_size if path.exists() else 0),
            "qa_pass": "False",
            "qa_fail_reasons": "missing_or_empty",
        }
    with Image.open(path) as image:
        rgb = image.convert("RGB")
    arr = np.asarray(rgb)
    width, height = rgb.size
    stat = ImageStat.Stat(rgb)
    extrema = rgb.getextrema()
    dynamic_range = max(high - low for low, high in extrema)
    mean_rgb = sum(stat.mean) / 3
    nonwhite = float(np.mean(np.any(arr < 245, axis=2)))
    nondark = float(np.mean(np.any(arr > 30, axis=2)))
    max_channel = arr.max(axis=2).astype(float)
    min_channel = arr.min(axis=2).astype(float)
    saturation_proxy = (max_channel - min_channel) / np.maximum(max_channel, 1.0)
    saturated_ratio = float(np.mean((saturation_proxy > 0.18) & (max_channel > 50) & (max_channel < 250)))
    dark_line_ratio = float(np.mean(np.max(arr, axis=2) < 110))
    quant = (arr // 32).reshape(-1, 3)
    unique_colors = len({tuple(x) for x in quant[:: max(1, len(quant) // 20000)]})
    edge_mean = float(ImageStat.Stat(rgb.convert("L").filter(ImageFilter.FIND_EDGES)).mean[0])
    reasons: list[str] = []
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
    return {
        "exists": "True",
        "bytes": str(path.stat().st_size),
        "width": str(width),
        "height": str(height),
        "dynamic_range": str(dynamic_range),
        "mean_rgb": f"{mean_rgb:.3f}",
        "nonwhite_ratio": f"{nonwhite:.4f}",
        "nondark_ratio": f"{nondark:.4f}",
        "saturated_ratio": f"{saturated_ratio:.4f}",
        "dark_line_ratio": f"{dark_line_ratio:.4f}",
        "unique_color_bins": str(unique_colors),
        "edge_mean": f"{edge_mean:.3f}",
        "qa_pass": str(not reasons),
        "qa_fail_reasons": ";".join(reasons),
    }


def content_qa(kind: str, metrics: dict[str, str], html_render_ok: str = "") -> tuple[bool, str]:
    nonwhite = float(metrics.get("nonwhite_ratio", "0") or 0)
    saturated = float(metrics.get("saturated_ratio", "0") or 0)
    dark_line = float(metrics.get("dark_line_ratio", "0") or 0)
    edge = float(metrics.get("edge_mean", "0") or 0)
    reasons: list[str] = []
    if metrics.get("exists") != "True":
        reasons.append("missing_or_empty")
    if kind == "static_png":
        if saturated < 0.010:
            reasons.append("low_thematic_color")
        if nonwhite < 0.030:
            reasons.append("low_map_ink")
        if edge < 2.000:
            reasons.append("low_edge_detail")
    elif kind == "time_series_png":
        if nonwhite < 0.010:
            reasons.append("low_plot_ink")
        if dark_line < 0.011 and saturated < 0.001:
            reasons.append("no_visible_line")
        if edge < 1.500:
            reasons.append("low_edge_detail")
    elif kind == "interactive_html":
        if html_render_ok != "True":
            reasons.append("html_not_rendered")
        if nonwhite < 0.050:
            reasons.append("low_rendered_map_ink")
        if edge < 2.000:
            reasons.append("low_edge_detail")
    return not reasons, ";".join(reasons)


def html_metrics(path: Path) -> dict[str, str]:
    if not path.exists() or path.stat().st_size == 0:
        return {
            "exists": str(path.exists()),
            "bytes": str(path.stat().st_size if path.exists() else 0),
            "valid_html_proxy": "False",
        }
    text = path.read_text(encoding="utf-8", errors="replace").lower()
    return {
        "exists": "True",
        "bytes": str(path.stat().st_size),
        "has_leaflet": str("leaflet" in text),
        "has_geojson": str("geojson" in text),
        "has_tooltip": str("tooltip" in text),
        "valid_html_proxy": str(len(text.strip()) > 5000 and ("leaflet" in text or "geojson" in text)),
    }


def json_metrics(path: Path) -> dict[str, str]:
    if not path.exists() or path.stat().st_size == 0:
        return {
            "exists": str(path.exists()),
            "bytes": str(path.stat().st_size if path.exists() else 0),
            "valid_json": "False",
        }
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return {
            "exists": "True",
            "bytes": str(path.stat().st_size),
            "valid_json": "True",
            "top_level_keys": str(len(data) if isinstance(data, dict) else 0),
        }
    except Exception as exc:
        return {
            "exists": "True",
            "bytes": str(path.stat().st_size),
            "valid_json": "False",
            "json_error": type(exc).__name__,
        }


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


def metadata_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for meta_path in sorted(RUN_ROOT.glob("*/*/*/metadata.json")):
        meta = read_json(meta_path)
        repair_model = repair_model_from_script(str(meta.get("script", "")))
        rows.append(
            {
                "repair_model": repair_model,
                "source_model": str(meta.get("model", "")),
                "mode": str(meta.get("mode", "")),
                "prompt_id": str(meta.get("prompt_id", "")),
                "iteration": str(meta.get("repair_iteration", "")),
                "run_dir": str(meta_path.parent.relative_to(ROOT)),
                "script": str(meta.get("script", "")),
                "returncode": str(meta.get("returncode", "")),
                "timed_out": str(meta.get("timed_out", "")),
            }
        )
    return rows


def audit_artifacts(meta_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    specs = [
        ("map_static.png", "static_png"),
        ("time_series.png", "time_series_png"),
        ("map_interactive.html", "interactive_html"),
        ("diagnostics.json", "diagnostic_json"),
    ]
    for meta in meta_rows:
        run_dir = ROOT / meta["run_dir"]
        for artifact, kind in specs:
            artifact_path = run_dir / artifact
            if kind in {"static_png", "time_series_png"}:
                metrics = image_metrics(artifact_path)
                valid = metrics.get("qa_pass") == "True"
            elif kind == "interactive_html":
                metrics = html_metrics(artifact_path)
                valid = metrics.get("valid_html_proxy") == "True"
            else:
                metrics = json_metrics(artifact_path)
                valid = metrics.get("valid_json") == "True"
            rows.append(
                {
                    **meta,
                    "artifact": artifact,
                    "kind": kind,
                    "artifact_path": str(artifact_path.relative_to(ROOT)),
                    "artifact_valid_proxy": str(valid),
                    **metrics,
                }
            )
    return rows


def screenshot_rows(artifact_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    SHOT_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []
    for row in artifact_rows:
        if row["kind"] not in {"static_png", "time_series_png", "interactive_html"}:
            continue
        artifact_path = ROOT / row["artifact_path"]
        qa_target = artifact_path
        screenshot_path = ""
        render_ok = ""
        render_error = ""
        if row["kind"] == "interactive_html":
            shot = SHOT_DIR / f"{safe_name(row['repair_model'])}_{safe_name(row['source_model'])}_{safe_name(row['mode'])}_{safe_name(row['prompt_id'])}_iter{row['iteration']}_interactive.png"
            ok, error = render_html(artifact_path, shot)
            render_ok = str(ok)
            render_error = error
            if ok:
                qa_target = shot
                screenshot_path = str(shot.relative_to(ROOT))
        metrics = image_metrics(qa_target)
        content_pass, content_reasons = content_qa(row["kind"], metrics, render_ok)
        rows.append(
            {
                **row,
                "screenshot_path": screenshot_path,
                "html_render_ok": render_ok,
                "html_render_error": render_error,
                "content_qa_pass": str(content_pass),
                "content_qa_fail_reasons": content_reasons,
                **{f"screenshot_{key}": value for key, value in metrics.items()},
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fields = sorted({key for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def summarize_artifacts(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[(row["repair_model"], row["kind"])].append(row)
    out = []
    for (repair_model, kind), group in sorted(grouped.items()):
        out.append(
            {
                "repair_model": repair_model,
                "kind": kind,
                "checked": str(len(group)),
                "exists": str(sum(row.get("exists") == "True" for row in group)),
                "valid_proxy": str(sum(row.get("artifact_valid_proxy") == "True" for row in group)),
            }
        )
    return out


def summarize_screenshots(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[(row["repair_model"], row["kind"])].append(row)
    out = []
    for (repair_model, kind), group in sorted(grouped.items()):
        existing = sum(row.get("screenshot_exists") == "True" for row in group)
        passed = sum(row.get("screenshot_qa_pass") == "True" for row in group)
        content_passed = sum(row.get("content_qa_pass") == "True" for row in group)
        html_rendered = sum(row.get("html_render_ok") == "True" for row in group)
        out.append(
            {
                "repair_model": repair_model,
                "kind": kind,
                "checked": str(len(group)),
                "existing_or_rendered": str(existing),
                "html_rendered": str(html_rendered) if kind == "interactive_html" else "",
                "screenshot_qa_pass": str(passed),
                "content_qa_pass": str(content_passed),
                "pass_rate_existing": f"{passed / existing:.3f}" if existing else "0.000",
                "content_pass_rate_existing": f"{content_passed / existing:.3f}" if existing else "0.000",
            }
        )
    return out


def main() -> None:
    SCORES_DIR.mkdir(parents=True, exist_ok=True)
    meta = metadata_rows()
    artifact = audit_artifacts(meta)
    screenshots = screenshot_rows(artifact)
    write_csv(SCORES_DIR / "iterative_repair_metadata_ledger.csv", meta)
    write_csv(SCORES_DIR / "iterative_repair_artifact_qa_detail.csv", artifact)
    write_csv(SCORES_DIR / "iterative_repair_artifact_qa_summary.csv", summarize_artifacts(artifact))
    write_csv(SCORES_DIR / "iterative_repair_screenshot_qa_detail.csv", screenshots)
    write_csv(SCORES_DIR / "iterative_repair_screenshot_qa_summary.csv", summarize_screenshots(screenshots))
    print(f"Wrote {len(meta)} metadata rows")
    print(f"Wrote {len(artifact)} artifact QA rows")
    print(f"Wrote {len(screenshots)} screenshot QA rows")


if __name__ == "__main__":
    main()
