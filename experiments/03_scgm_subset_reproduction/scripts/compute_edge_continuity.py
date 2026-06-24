#!/usr/bin/env python3
"""Compute tile-edge continuity baselines for SCGM/CSCMG tiles."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT / "data/raw/SCGM/extracted/TMGN_1814"
OUT_DIR = ROOT / "experiments/03_scgm_subset_reproduction/outputs"


def parse_key(path: Path) -> tuple[int, int, int]:
    parts = path.stem.split("_")
    if len(parts) < 3:
        raise ValueError(f"Unexpected tile filename: {path.name}")
    return int(parts[0]), int(parts[1]), int(parts[2])


def tile_index(split: str, folder: str) -> dict[tuple[int, int, int], Path]:
    return {parse_key(p): p for p in (DATA_DIR / split / folder).glob("*.png")}


def edge_diff(a_path: Path, b_path: Path, direction: str) -> float:
    with Image.open(a_path) as a_img, Image.open(b_path) as b_img:
        a = np.asarray(a_img.convert("RGB"), dtype=np.float32)
        b = np.asarray(b_img.convert("RGB"), dtype=np.float32)
    if direction == "right":
        edge_a = a[:, -1, :]
        edge_b = b[:, 0, :]
    elif direction == "down":
        edge_a = a[-1, :, :]
        edge_b = b[0, :, :]
    else:
        raise ValueError(direction)
    return float(np.mean(np.abs(edge_a - edge_b)))


def compute(split: str, folder: str, max_pairs: int | None = None) -> list[dict[str, str]]:
    idx = tile_index(split, folder)
    rows: list[dict[str, str]] = []
    for z, x, y in sorted(idx):
        neighbors = [
            ("right", (z, x + 1, y)),
            ("down", (z, x, y + 1)),
        ]
        for direction, nkey in neighbors:
            if nkey not in idx:
                continue
            rows.append(
                {
                    "split": split,
                    "folder": folder,
                    "z": str(z),
                    "x": str(x),
                    "y": str(y),
                    "neighbor_x": str(nkey[1]),
                    "neighbor_y": str(nkey[2]),
                    "direction": direction,
                    "edge_absdiff_rgb": f"{edge_diff(idx[(z, x, y)], idx[nkey], direction):.6f}",
                    "tile": idx[(z, x, y)].name,
                    "neighbor": idx[nkey].name,
                }
            )
            if max_pairs and len(rows) >= max_pairs:
                return rows
    return rows


def summarize(rows: list[dict[str, str]]) -> dict[str, object]:
    groups: dict[tuple[str, str, str], list[float]] = {}
    for row in rows:
        key = (row["split"], row["folder"], row["direction"])
        groups.setdefault(key, []).append(float(row["edge_absdiff_rgb"]))
    out: dict[str, object] = {}
    for key, values in groups.items():
        arr = np.asarray(values, dtype=np.float32)
        out["/".join(key)] = {
            "pairs": int(arr.size),
            "mean_absdiff_rgb": round(float(arr.mean()), 6),
            "median_absdiff_rgb": round(float(np.median(arr)), 6),
            "p90_absdiff_rgb": round(float(np.quantile(arr, 0.9)), 6),
            "max_absdiff_rgb": round(float(arr.max()), 6),
        }
    return out


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_report(summary: dict[str, object]) -> None:
    lines = [
        "# SCGM Edge-Continuity Baseline",
        "",
        "This computes mean absolute RGB differences between adjacent tile borders. Lower values mean adjacent tiles are more visually continuous at the shared edge.",
        "",
        "## Validation Split",
        "",
        "| Group | Pairs | Mean | Median | P90 | Max |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for group, stats in sorted(summary.items()):
        assert isinstance(stats, dict)
        lines.append(
            f"| `{group}` | {stats['pairs']} | {stats['mean_absdiff_rgb']} | {stats['median_absdiff_rgb']} | {stats['p90_absdiff_rgb']} | {stats['max_absdiff_rgb']} |"
        )
    lines += [
        "",
        "## Use",
        "",
        "- Treat these as data/reference baselines before evaluating generated tiles.",
        "- Future generated outputs can be scored with the same border metric and compared against `map_256` ground truth.",
        "- The metric is intentionally simple and should be paired with road/line-continuity checks later.",
        "",
    ]
    (OUT_DIR / "scgm_edge_continuity_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []
    for folder in ("rs_256", "map_256"):
        rows.extend(compute("val", folder))
    summary = summarize(rows)
    write_csv(OUT_DIR / "scgm_edge_continuity_val.csv", rows)
    (OUT_DIR / "scgm_edge_continuity_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_report(summary)
    print(f"Wrote {OUT_DIR.relative_to(ROOT)}/scgm_edge_continuity_val.csv")
    print(f"Wrote {OUT_DIR.relative_to(ROOT)}/scgm_edge_continuity_summary.json")
    print(f"Wrote {OUT_DIR.relative_to(ROOT)}/scgm_edge_continuity_report.md")


if __name__ == "__main__":
    main()

