#!/usr/bin/env python3
"""Audit rendered artifacts from reference and generated choropleth runs."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from PIL import Image, ImageStat


ROOT = Path(__file__).resolve().parents[3]
EXP_DIR = ROOT / "experiments/05_choropleth_reliability_benchmark"
RUN_ROOT = EXP_DIR / "outputs/runs"
REFERENCE_DIR = EXP_DIR / "outputs/reference_baseline"
OUT_DIR = EXP_DIR / "outputs/scores"


def image_metrics(path: Path) -> dict[str, str]:
    if not path.exists() or path.stat().st_size == 0:
        return {"exists": str(path.exists()), "bytes": str(path.stat().st_size if path.exists() else 0)}
    with Image.open(path) as image:
        rgb = image.convert("RGB")
        stat = ImageStat.Stat(rgb)
        extrema = rgb.getextrema()
        dynamic_range = max(high - low for low, high in extrema)
        mean_rgb = sum(stat.mean) / len(stat.mean)
    return {
        "exists": "True",
        "bytes": str(path.stat().st_size),
        "width": str(rgb.width),
        "height": str(rgb.height),
        "mean_rgb": f"{mean_rgb:.3f}",
        "dynamic_range": str(dynamic_range),
        "nonblank": str(dynamic_range > 10),
    }


def html_metrics(path: Path) -> dict[str, str]:
    if not path.exists() or path.stat().st_size == 0:
        return {"exists": str(path.exists()), "bytes": str(path.stat().st_size if path.exists() else 0)}
    text = path.read_text(encoding="utf-8", errors="replace").lower()
    return {
        "exists": "True",
        "bytes": str(path.stat().st_size),
        "has_leaflet": str("leaflet" in text),
        "has_geojson": str("geojson" in text),
        "has_tooltip": str("tooltip" in text),
        "nonblank": str(len(text.strip()) > 5000),
    }


def json_metrics(path: Path) -> dict[str, str]:
    if not path.exists() or path.stat().st_size == 0:
        return {"exists": str(path.exists()), "bytes": str(path.stat().st_size if path.exists() else 0)}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return {"exists": "True", "bytes": str(path.stat().st_size), "valid_json": "True", "top_level_keys": str(len(data))}
    except Exception as exc:
        return {"exists": "True", "bytes": str(path.stat().st_size), "valid_json": "False", "json_error": type(exc).__name__}


def audit_dir(label: str, path: Path) -> list[dict[str, str]]:
    specs = [
        ("map_static.png", "image"),
        ("time_series.png", "image"),
        ("map_interactive.html", "html"),
        ("diagnostics.json", "json"),
    ]
    rows = []
    for filename, kind in specs:
        artifact_path = path / filename
        if kind == "image":
            metrics = image_metrics(artifact_path)
        elif kind == "html":
            metrics = html_metrics(artifact_path)
        else:
            metrics = json_metrics(artifact_path)
        rows.append({"source": label, "artifact": filename, "kind": kind, **metrics})
    return rows


def run_sources() -> list[tuple[str, Path]]:
    sources = [("reference", REFERENCE_DIR)]
    for manifest_path in sorted(list(RUN_ROOT.glob("*/run_manifest.json")) + list(RUN_ROOT.glob("*/repair_run_manifest.json"))):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        repair_model = manifest_path.parent.name if manifest_path.name == "repair_run_manifest.json" else ""
        for meta in manifest:
            run_dir = ROOT / meta["run_dir"]
            if repair_model:
                label = f"repair_{repair_model}:{meta['model']}:{meta['mode']}:{meta['prompt_id']}:{run_dir.name}"
            else:
                label = f"{meta['model']}:{meta['mode']}:{meta['prompt_id']}:{run_dir.name}"
            sources.append((label, run_dir))
    return sources


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fields = sorted({key for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def summarize(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault((row["source"], row["kind"]), []).append(row)
    summary = []
    for (source, kind), group in sorted(grouped.items()):
        summary.append(
            {
                "source": source,
                "kind": kind,
                "artifacts": str(len(group)),
                "exists": str(sum(row.get("exists") == "True" for row in group)),
                "nonblank_or_valid": str(
                    sum(row.get("nonblank") == "True" or row.get("valid_json") == "True" for row in group)
                ),
            }
        )
    return summary


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for label, path in run_sources():
        rows.extend(audit_dir(label, path))
    detail_path = OUT_DIR / "rendered_artifact_qa_detail.csv"
    summary_path = OUT_DIR / "rendered_artifact_qa_summary.csv"
    write_csv(detail_path, rows)
    write_csv(summary_path, summarize(rows))
    print(f"Wrote {detail_path.relative_to(ROOT)}")
    print(f"Wrote {summary_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
