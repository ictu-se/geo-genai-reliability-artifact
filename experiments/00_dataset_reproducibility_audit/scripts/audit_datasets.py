#!/usr/bin/env python3
"""Create a reproducibility inventory for local Geo-GenAI datasets."""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = ROOT / "experiments/00_dataset_reproducibility_audit/outputs"


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def human_size(num_bytes: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(num_bytes)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    return f"{num_bytes} B"


def dir_size(path: Path) -> int:
    total = 0
    if not path.exists():
        return total
    for root, _, files in os.walk(path):
        for name in files:
            try:
                total += (Path(root) / name).stat().st_size
            except OSError:
                pass
    return total


def count_files(path: Path, suffixes: tuple[str, ...] | None = None) -> int:
    if not path.exists():
        return 0
    count = 0
    for p in path.rglob("*"):
        if not p.is_file():
            continue
        if suffixes and p.suffix.lower() not in suffixes:
            continue
        count += 1
    return count


def readme_exists(path: Path) -> bool:
    return any((path / name).exists() for name in ("README.md", "README.txt", "readme.md", "Readme.md"))


def license_exists(path: Path) -> bool:
    return any((path / name).exists() for name in ("LICENSE", "LICENSE.md", "license.txt"))


def scgm_counts() -> dict[str, int | str | bool]:
    base = ROOT / "data/raw/SCGM/extracted/TMGN_1814"
    counts: dict[str, int | str | bool] = {}
    for split in ("train", "val"):
        for folder in ("rs_256", "map_256", "ref_scale_2_256", "ref_scale_4_256"):
            files = sorted((base / split / folder).glob("*.png"))
            counts[f"{split}_{folder}_png"] = len(files)
    for split in ("train", "val"):
        rs = {p.name for p in (base / split / "rs_256").glob("*.png")}
        mp = {p.name for p in (base / split / "map_256").glob("*.png")}
        r2 = {p.name for p in (base / split / "ref_scale_2_256").glob("*.png")}
        r4 = {p.name for p in (base / split / "ref_scale_4_256").glob("*.png")}
        counts[f"{split}_rs_map_name_intersection"] = len(rs & mp)
        counts[f"{split}_rs_missing_map"] = len(rs - mp)
        counts[f"{split}_map_missing_rs"] = len(mp - rs)
        counts[f"{split}_rs_with_ref_scale_2"] = len(rs & r2)
        counts[f"{split}_rs_with_ref_scale_4"] = len(rs & r4)
    return counts


def mapgenerator_counts() -> dict[str, int | str | bool]:
    base = ROOT / "data/raw/MapGenerator"
    counts: dict[str, int | str | bool] = {}
    for split in ("MapTrain", "MGEval"):
        img_dir = base / split / "Images"
        counts[f"{split}_images"] = count_files(img_dir, (".jpg", ".jpeg", ".png"))
        counts[f"{split}_has_descriptions_xlsx"] = (base / split / "descriptions.xlsx").exists()
    return counts


def choropleth_counts() -> dict[str, int | str | bool]:
    base = ROOT / "data/repos/Materials-for-Creating-maps-by-Artificial-Intelligence"
    return {
        "static_png": count_files(base / "StaticMaps", (".png",)),
        "interactive_html": count_files(base / "InteractiveMaps", (".html",)),
        "code_notebooks": count_files(base / "codesnippet", (".ipynb",)),
        "choropleth_shp": count_files(base / "data_choropleth", (".shp",)),
        "choropleth_csv": count_files(base / "data_choropleth", (".csv",)),
    }


def build_inventory() -> list[dict[str, str]]:
    datasets = [
        {
            "dataset": "SCGM / CSCMG",
            "local_path": ROOT / "data/raw/SCGM",
            "paper_or_source": "Sun et al. 2025 SCGM",
            "artifact_type": "remote-sensing-to-map tile pairs",
            "claimed_scale": "multi-scale levels 14-18",
            "counts": scgm_counts(),
            "code_path": ROOT / "data/repos/SCGM",
        },
        {
            "dataset": "MapGenerator MGTrain/MGEval",
            "local_path": ROOT / "data/raw/MapGenerator",
            "paper_or_source": "Zhang et al. 2025 MapGenerator",
            "artifact_type": "map image and natural-language description pairs",
            "claimed_scale": "1000 train pairs, 100 eval pairs in paper notes",
            "counts": mapgenerator_counts(),
            "code_path": ROOT / "data/repos/MapGenerator",
        },
        {
            "dataset": "ChatGPT choropleth materials",
            "local_path": ROOT / "data/repos/Materials-for-Creating-maps-by-Artificial-Intelligence",
            "paper_or_source": "Pannoon & Netek 2025",
            "artifact_type": "prompt outputs, choropleth data, static/interactive maps",
            "claimed_scale": "static and interactive prompt trials",
            "counts": choropleth_counts(),
            "code_path": ROOT / "data/repos/Materials-for-Creating-maps-by-Artificial-Intelligence",
        },
        {
            "dataset": "Generative AI mapmaking code",
            "local_path": ROOT / "data/repos/generative-ai-mapmaking",
            "paper_or_source": "Affolter et al. 2025 related code",
            "artifact_type": "ControlNet-style training/evaluation code",
            "claimed_scale": "code template; original controlled dataset not local",
            "counts": {
                "python_files": count_files(ROOT / "data/repos/generative-ai-mapmaking", (".py",)),
                "notebooks": count_files(ROOT / "data/repos/generative-ai-mapmaking", (".ipynb",)),
            },
            "code_path": ROOT / "data/repos/generative-ai-mapmaking",
        },
        {
            "dataset": "GeoGuard local LA County benchmark",
            "local_path": ROOT / "data/raw/geoguard",
            "paper_or_source": "local benchmark artifact",
            "artifact_type": "vector/raster GIS data and generated workflow outputs",
            "claimed_scale": "local benchmark; not a public Geo-GenAI source dataset",
            "counts": {
                "gpkg": count_files(ROOT / "data/raw/geoguard", (".gpkg",)),
                "tif": count_files(ROOT / "data/raw/geoguard", (".tif", ".tiff")),
                "csv": count_files(ROOT / "data/raw/geoguard", (".csv",)),
            },
            "code_path": ROOT / "data/raw/geoguard/geoguard",
        },
    ]

    rows: list[dict[str, str]] = []
    for item in datasets:
        path = item["local_path"]
        code_path = item["code_path"]
        size = dir_size(path)
        counts = item["counts"]
        rows.append(
            {
                "dataset": item["dataset"],
                "local_path": rel(path),
                "size_bytes": str(size),
                "size_human": human_size(size),
                "paper_or_source": item["paper_or_source"],
                "artifact_type": item["artifact_type"],
                "claimed_scale": item["claimed_scale"],
                "file_count": str(count_files(path)),
                "readme_available": str(readme_exists(path)),
                "license_available": str(license_exists(path)),
                "code_available": str(code_path.exists()),
                "code_path": rel(code_path),
                "counts_json": json.dumps(counts, sort_keys=True),
            }
        )
    return rows


def build_reproducibility(inventory: list[dict[str, str]]) -> list[dict[str, str]]:
    by_name = {row["dataset"]: row for row in inventory}
    rows = [
        {
            "dataset": "SCGM / CSCMG",
            "data_available": "yes",
            "code_available": by_name["SCGM / CSCMG"]["code_available"],
            "model_weights_available_local": "partial_or_unknown",
            "evaluation_reproducible_now": "partial",
            "main_blocker": "GPU/training environment and exact evaluation protocol need setup; cascade-reference coverage is not full one-to-one.",
            "recommended_first_check": "Build subset manifest and edge-continuity metric before attempting training.",
        },
        {
            "dataset": "MapGenerator MGTrain/MGEval",
            "data_available": "yes",
            "code_available": by_name["MapGenerator MGTrain/MGEval"]["code_available"],
            "model_weights_available_local": "unknown",
            "evaluation_reproducible_now": "partial",
            "main_blocker": "Full paper PDF not local; released train image count differs from paper-note claim.",
            "recommended_first_check": "Audit image-caption consistency and released-count discrepancy.",
        },
        {
            "dataset": "ChatGPT choropleth materials",
            "data_available": "yes",
            "code_available": "yes",
            "model_weights_available_local": "not_applicable_api_case_study",
            "evaluation_reproducible_now": "mostly",
            "main_blocker": "Original ChatGPT version/prompt environment is not frozen; outputs are static artifacts.",
            "recommended_first_check": "Use released outputs as benchmark cases for cartographic linting.",
        },
        {
            "dataset": "Generative AI mapmaking code",
            "data_available": "no_original_training_data",
            "code_available": "yes",
            "model_weights_available_local": "no",
            "evaluation_reproducible_now": "no",
            "main_blocker": "Original controlled vector/raster training data are not in workspace.",
            "recommended_first_check": "Treat as method template, not a directly reproducible dataset.",
        },
        {
            "dataset": "GeoGuard local LA County benchmark",
            "data_available": "yes",
            "code_available": "yes",
            "model_weights_available_local": "not_applicable",
            "evaluation_reproducible_now": "yes_for_local_scripts",
            "main_blocker": "Local benchmark rather than external paper artifact.",
            "recommended_first_check": "Use as controlled testbed for evaluator ideas, not as public dataset audit evidence.",
        },
    ]
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_report(inventory: list[dict[str, str]], matrix: list[dict[str, str]]) -> None:
    lines = [
        "# Dataset Reproducibility Audit",
        "",
        "Generated from local workspace artifacts.",
        "",
        "## Dataset Inventory",
        "",
        "| Dataset | Size | Files | Data path | Code | Key counts |",
        "|---|---:|---:|---|---|---|",
    ]
    for row in inventory:
        counts = json.loads(row["counts_json"])
        compact = ", ".join(f"{k}={v}" for k, v in list(counts.items())[:8])
        if len(counts) > 8:
            compact += ", ..."
        lines.append(
            f"| {row['dataset']} | {row['size_human']} | {row['file_count']} | `{row['local_path']}` | {row['code_available']} | {compact} |"
        )

    lines += [
        "",
        "## Reproducibility Matrix",
        "",
        "| Dataset | Data | Code | Reproducible now | Main blocker | First check |",
        "|---|---|---|---|---|---|",
    ]
    for row in matrix:
        lines.append(
            f"| {row['dataset']} | {row['data_available']} | {row['code_available']} | {row['evaluation_reproducible_now']} | {row['main_blocker']} | {row['recommended_first_check']} |"
        )

    lines += [
        "",
        "## Immediate Findings",
        "",
        "- SCGM/CSCMG is the dominant local dataset by size and sample count.",
        "- SCGM train has complete `rs_256`/`map_256` name matching, but cascade references are fewer than base pairs.",
        "- MapGenerator release has 750 train descriptions and 100 eval descriptions locally; this should be reported against the paper-note claim of 1000 train pairs.",
        "- The choropleth materials are best suited for low-compute reliability experiments because data, outputs, and code snippets are local.",
        "- The Affolter-style mapmaking repo is useful as a method template, but the original training data are not local.",
        "",
        "## Recommended First Track",
        "",
        "1. Use this inventory as the reproducibility table.",
        "2. Run the MapGenerator image-caption audit for caption/data quality evidence.",
        "3. Treat choropleth outputs as a cartographic linting benchmark.",
        "4. Move SCGM to GPU reproduction only after a subset manifest and edge-continuity metric are stable.",
        "",
    ]
    (OUT_DIR / "dataset_audit_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    inventory = build_inventory()
    matrix = build_reproducibility(inventory)
    write_csv(OUT_DIR / "dataset_inventory.csv", inventory)
    write_csv(OUT_DIR / "reproducibility_matrix.csv", matrix)
    write_report(inventory, matrix)
    print(f"Wrote {rel(OUT_DIR / 'dataset_inventory.csv')}")
    print(f"Wrote {rel(OUT_DIR / 'reproducibility_matrix.csv')}")
    print(f"Wrote {rel(OUT_DIR / 'dataset_audit_report.md')}")


if __name__ == "__main__":
    main()

