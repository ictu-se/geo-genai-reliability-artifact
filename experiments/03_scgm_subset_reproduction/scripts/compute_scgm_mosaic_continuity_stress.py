#!/usr/bin/env python3
"""Measure neighbor-seam stress for generated SCGM validation mosaics."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from statistics import mean, median

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = ROOT / "experiments/03_scgm_subset_reproduction/outputs"
VAL_MANIFEST = OUT_DIR / "scgm_subset_manifest_val_first200.csv"
PAIR_OUT = OUT_DIR / "scgm_mosaic_neighbor_stress_pairs.csv"
SUMMARY_OUT = OUT_DIR / "scgm_mosaic_neighbor_stress_summary.json"
REPORT_OUT = OUT_DIR / "scgm_mosaic_neighbor_stress_report.md"

BASELINES = [
    ("color-stat retrieval", OUT_DIR / "scgm_retrieval_baseline_generated_maps"),
    ("multi-feature retrieval", OUT_DIR / "scgm_multifeature_retrieval_generated_maps"),
    ("learned forest", OUT_DIR / "scgm_learned_forest_generated_maps"),
    ("neural MLP", OUT_DIR / "scgm_mlp_generated_maps"),
    ("local-context ridge", OUT_DIR / "scgm_local_context_ridge_generated_maps"),
    ("convolutional filter-bank ridge", OUT_DIR / "scgm_convolutional_filter_ridge_generated_maps"),
    ("patch-embedding retrieval", OUT_DIR / "scgm_patch_embedding_retrieval_generated_maps"),
    ("trained tiny CNN", OUT_DIR / "scgm_tiny_cnn_generated_maps"),
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def image_array(path: Path) -> np.ndarray:
    with Image.open(path) as image:
        return np.asarray(image.convert("RGB"), dtype=np.float32)


def edge_absdiff(a_path: Path, b_path: Path, direction: str) -> float:
    a = image_array(a_path)
    b = image_array(b_path)
    if direction == "right":
        edge_a = a[:, -1, :]
        edge_b = b[:, 0, :]
    elif direction == "down":
        edge_a = a[-1, :, :]
        edge_b = b[0, :, :]
    else:
        raise ValueError(direction)
    return float(np.mean(np.abs(edge_a - edge_b)))


def tile_key(row: dict[str, str]) -> tuple[int, int, int]:
    return int(row["z"]), int(row["x"]), int(row["y"])


def generated_index(folder: Path) -> dict[str, Path]:
    index: dict[str, Path] = {}
    for path in sorted(folder.glob("*.png")):
        parts = path.stem.split("_")
        if len(parts) < 3:
            continue
        tile = "_".join(parts[:3])
        index[tile] = path
    return index


def neighbor_pairs(rows: list[dict[str, str]]) -> list[tuple[dict[str, str], dict[str, str], str]]:
    by_key = {tile_key(row): row for row in rows}
    pairs: list[tuple[dict[str, str], dict[str, str], str]] = []
    for key, row in sorted(by_key.items()):
        z, x, y = key
        right = by_key.get((z, x + 1, y))
        down = by_key.get((z, x, y + 1))
        if right:
            pairs.append((row, right, "right"))
        if down:
            pairs.append((row, down, "down"))
    return pairs


def summarize(values: list[float]) -> dict[str, float]:
    if not values:
        return {"mean": 0.0, "median": 0.0, "p90": 0.0, "max": 0.0}
    arr = np.asarray(values, dtype=np.float32)
    return {
        "mean": round(float(mean(values)), 6),
        "median": round(float(median(values)), 6),
        "p90": round(float(np.quantile(arr, 0.9)), 6),
        "max": round(float(np.max(arr)), 6),
    }


def main() -> None:
    val_rows = [row for row in read_csv(VAL_MANIFEST) if row.get("has_map") == "True"]
    pairs = neighbor_pairs(val_rows)
    pair_rows: list[dict[str, str]] = []
    summary_rows: list[dict[str, object]] = []

    for baseline, folder in BASELINES:
        gen = generated_index(folder)
        generated_values: list[float] = []
        target_values: list[float] = []
        stress_ratios: list[float] = []
        missing = 0
        for a, b, direction in pairs:
            gen_a = gen.get(a["tile"])
            gen_b = gen.get(b["tile"])
            if not gen_a or not gen_b:
                missing += 1
                continue
            target_diff = edge_absdiff(ROOT / a["map_path"], ROOT / b["map_path"], direction)
            generated_diff = edge_absdiff(gen_a, gen_b, direction)
            ratio = generated_diff / target_diff if target_diff else 0.0
            generated_values.append(generated_diff)
            target_values.append(target_diff)
            stress_ratios.append(ratio)
            pair_rows.append(
                {
                    "baseline": baseline,
                    "tile_a": a["tile"],
                    "tile_b": b["tile"],
                    "direction": direction,
                    "generated_seam_absdiff": f"{generated_diff:.6f}",
                    "target_seam_absdiff": f"{target_diff:.6f}",
                    "generated_minus_target": f"{generated_diff - target_diff:.6f}",
                    "stress_ratio": f"{ratio:.6f}",
                    "generated_a_path": str(gen_a.relative_to(ROOT)),
                    "generated_b_path": str(gen_b.relative_to(ROOT)),
                }
            )
        gen_stats = summarize(generated_values)
        target_stats = summarize(target_values)
        ratio_stats = summarize(stress_ratios)
        summary_rows.append(
            {
                "baseline": baseline,
                "neighbor_pairs_available": len(generated_values),
                "neighbor_pairs_missing": missing,
                "generated_seam_absdiff": gen_stats,
                "target_seam_absdiff": target_stats,
                "stress_ratio": ratio_stats,
                "interpretation": "lower generated seam absdiff is smoother, but values below target can also indicate over-smoothing",
            }
        )

    write_csv(PAIR_OUT, pair_rows)
    SUMMARY_OUT.write_text(json.dumps(summary_rows, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# SCGM Mosaic Neighbor-Seam Stress Audit",
        "",
        "This audit measures seam discontinuity between adjacent validation tiles when generated outputs are treated as a small mosaic. It complements per-tile image metrics by testing whether neighboring generated tiles agree at shared borders.",
        "",
        f"- validation neighbor pairs found: {len(pairs)}",
        f"- pair-level rows: {len(pair_rows)}",
        "",
        "| Baseline | Pairs | Missing | Generated seam mean | Target seam mean | Stress-ratio mean | Note |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in summary_rows:
        gen_stats = row["generated_seam_absdiff"]
        target_stats = row["target_seam_absdiff"]
        ratio_stats = row["stress_ratio"]
        assert isinstance(gen_stats, dict)
        assert isinstance(target_stats, dict)
        assert isinstance(ratio_stats, dict)
        lines.append(
            f"| {row['baseline']} | {row['neighbor_pairs_available']} | {row['neighbor_pairs_missing']} | {gen_stats['mean']:.6f} | {target_stats['mean']:.6f} | {ratio_stats['mean']:.6f} | lower-than-target can mean smooth seams, not necessarily cartographic detail |"
        )
    lines += [
        "",
        "Interpretation: the best mosaic seam score is not automatically the best map. A model can reduce seam differences by washing out roads, labels, and symbol texture. The audit is therefore reported beside MAE, PSNR, SSIM, contact sheets, and qualitative cartographic-detail cautions.",
        "",
    ]
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {PAIR_OUT.relative_to(ROOT)}")
    print(f"Wrote {SUMMARY_OUT.relative_to(ROOT)}")
    print(f"Wrote {REPORT_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
