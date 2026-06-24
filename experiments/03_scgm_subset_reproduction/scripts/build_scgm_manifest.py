#!/usr/bin/env python3
"""Build SCGM/CSCMG consistency summaries and small subset manifests."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT / "data/raw/SCGM/extracted/TMGN_1814"
OUT_DIR = ROOT / "experiments/03_scgm_subset_reproduction/outputs"


def tile_key(path: Path) -> str:
    return path.stem


def parse_tile_name(name: str) -> dict[str, str]:
    parts = name.split("_")
    if len(parts) >= 3:
        return {"z": parts[0], "x": parts[1], "y": parts[2]}
    return {"z": "", "x": "", "y": ""}


def files(split: str, folder: str) -> dict[str, Path]:
    return {tile_key(p): p for p in (DATA_DIR / split / folder).glob("*.png")}


def inspect_one(path: Path) -> tuple[int, int, str]:
    with Image.open(path) as img:
        return img.width, img.height, img.mode


def build_rows(split: str, limit: int | None = None, complete_refs_only: bool = False) -> list[dict[str, str]]:
    rs = files(split, "rs_256")
    mp = files(split, "map_256")
    r2 = files(split, "ref_scale_2_256")
    r4 = files(split, "ref_scale_4_256")
    keys = sorted(rs)
    if complete_refs_only:
        keys = [key for key in keys if key in mp and key in r2 and key in r4]
    if limit:
        keys = keys[:limit]
    rows: list[dict[str, str]] = []
    for key in keys:
        tile = parse_tile_name(key)
        rs_path = rs[key]
        width, height, mode = inspect_one(rs_path)
        rows.append(
            {
                "split": split,
                "tile": key,
                "z": tile["z"],
                "x": tile["x"],
                "y": tile["y"],
                "rs_path": str(rs_path.relative_to(ROOT)),
                "map_path": str(mp[key].relative_to(ROOT)) if key in mp else "",
                "ref_scale_2_path": str(r2[key].relative_to(ROOT)) if key in r2 else "",
                "ref_scale_4_path": str(r4[key].relative_to(ROOT)) if key in r4 else "",
                "has_map": str(key in mp),
                "has_ref_scale_2": str(key in r2),
                "has_ref_scale_4": str(key in r4),
                "width": str(width),
                "height": str(height),
                "mode": mode,
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def summarize_split(split: str) -> dict[str, object]:
    rs = files(split, "rs_256")
    mp = files(split, "map_256")
    r2 = files(split, "ref_scale_2_256")
    r4 = files(split, "ref_scale_4_256")
    z_counts: dict[str, int] = {}
    for key in rs:
        z = parse_tile_name(key)["z"]
        z_counts[z] = z_counts.get(z, 0) + 1
    return {
        "split": split,
        "rs_256": len(rs),
        "map_256": len(mp),
        "ref_scale_2_256": len(r2),
        "ref_scale_4_256": len(r4),
        "rs_map_intersection": len(set(rs) & set(mp)),
        "rs_missing_map": len(set(rs) - set(mp)),
        "map_missing_rs": len(set(mp) - set(rs)),
        "rs_with_ref_scale_2": len(set(rs) & set(r2)),
        "rs_with_ref_scale_4": len(set(rs) & set(r4)),
        "zoom_distribution_rs": z_counts,
    }


def write_report(summary: list[dict[str, object]]) -> None:
    lines = [
        "# SCGM / CSCMG Local Manifest",
        "",
        "This report checks local file consistency and creates small subset manifests for lightweight reproduction work.",
        "",
        "## Split Summary",
        "",
        "| Split | RS | Map | RS-map matched | Ref 2x | Ref 4x | RS with ref 2x | RS with ref 4x | Zoom distribution |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for item in summary:
        lines.append(
            f"| {item['split']} | {item['rs_256']} | {item['map_256']} | {item['rs_map_intersection']} | {item['ref_scale_2_256']} | {item['ref_scale_4_256']} | {item['rs_with_ref_scale_2']} | {item['rs_with_ref_scale_4']} | {item['zoom_distribution_rs']} |"
        )
    lines += [
        "",
        "## Immediate Findings",
        "",
        "- Base remote-sensing and target map tiles match one-to-one by filename for the checked splits.",
        "- Cascade reference folders contain fewer files than the base RS/map folders, so reproduction code must handle missing references or filter to complete-reference subsets.",
        "- The generated `scgm_subset_manifest_*.csv` files provide small deterministic subsets for environment smoke tests.",
        "- The generated `scgm_complete_reference_subset_*.csv` files provide deterministic subsets where both cascade references are present.",
        "",
        "## Next Checks",
        "",
        "1. Add tile-neighbor discovery from z/x/y names for edge-continuity metrics.",
        "2. Run image statistics on complete-reference subsets.",
        "3. Run a tiny baseline only after confirming GPU/runtime setup.",
        "",
    ]
    (OUT_DIR / "scgm_manifest_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary = [summarize_split("train"), summarize_split("val")]
    (OUT_DIR / "scgm_split_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    for split in ("train", "val"):
        write_csv(OUT_DIR / f"scgm_subset_manifest_{split}_first200.csv", build_rows(split, limit=200))
        write_csv(
            OUT_DIR / f"scgm_complete_reference_subset_{split}_first200.csv",
            build_rows(split, limit=200, complete_refs_only=True),
        )
    write_report(summary)
    print(f"Wrote {OUT_DIR.relative_to(ROOT)}/scgm_split_summary.json")
    print(f"Wrote {OUT_DIR.relative_to(ROOT)}/scgm_subset_manifest_train_first200.csv")
    print(f"Wrote {OUT_DIR.relative_to(ROOT)}/scgm_subset_manifest_val_first200.csv")
    print(f"Wrote {OUT_DIR.relative_to(ROOT)}/scgm_manifest_report.md")


if __name__ == "__main__":
    main()
