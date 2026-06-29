#!/usr/bin/env python3
"""Run a patch-embedding retrieval RS-to-map baseline for SCGM/CSCMG tiles.

This baseline retrieves local train patches in remote-sensing feature space and
copies the corresponding train map patches into each validation output. It is a
CPU-friendly image-to-image diagnostic: more local than whole-tile retrieval,
but still not a trained CNN or diffusion model.
"""

from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = ROOT / "experiments/03_scgm_subset_reproduction/outputs"
GEN_DIR = OUT_DIR / "scgm_patch_embedding_retrieval_generated_maps"
TRAIN_MANIFEST = OUT_DIR / "scgm_subset_manifest_train_first200.csv"
VAL_MANIFEST = OUT_DIR / "scgm_subset_manifest_val_first200.csv"
LOW_RES = 64
PATCH = 8


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


def lowres_rgb(path: Path) -> np.ndarray:
    with Image.open(path) as image:
        return np.asarray(image.convert("RGB").resize((LOW_RES, LOW_RES), Image.Resampling.BILINEAR), dtype=np.float32) / 255.0


def lowres_edge(path: Path) -> np.ndarray:
    with Image.open(path) as image:
        edge = image.convert("L").filter(ImageFilter.FIND_EDGES)
        return np.asarray(edge.resize((LOW_RES, LOW_RES), Image.Resampling.BILINEAR), dtype=np.float32)[:, :, None] / 255.0


def patch_features(rs_path: Path) -> tuple[np.ndarray, list[tuple[int, int]]]:
    rgb = lowres_rgb(rs_path)
    edge = lowres_edge(rs_path)
    feats: list[np.ndarray] = []
    coords: list[tuple[int, int]] = []
    for y in range(0, LOW_RES, PATCH):
        for x in range(0, LOW_RES, PATCH):
            rgb_patch = rgb[y : y + PATCH, x : x + PATCH, :].reshape(-1)
            edge_patch = edge[y : y + PATCH, x : x + PATCH, :].reshape(-1)
            mean = rgb_patch.reshape(-1, 3).mean(axis=0)
            std = rgb_patch.reshape(-1, 3).std(axis=0)
            position = np.asarray([x / (LOW_RES - PATCH), y / (LOW_RES - PATCH)], dtype=np.float32)
            feat = np.concatenate([rgb_patch, edge_patch, mean, std, position]).astype(np.float32)
            norm = np.linalg.norm(feat)
            feats.append(feat / norm if norm else feat)
            coords.append((x, y))
    return np.vstack(feats), coords


def lowres_map_patches(map_path: Path) -> list[np.ndarray]:
    rgb = lowres_rgb(map_path)
    patches: list[np.ndarray] = []
    for y in range(0, LOW_RES, PATCH):
        for x in range(0, LOW_RES, PATCH):
            patches.append(rgb[y : y + PATCH, x : x + PATCH, :])
    return patches


def output_image(lowres: np.ndarray) -> Image.Image:
    arr = np.clip(lowres * 255.0, 0, 255).astype(np.uint8)
    return Image.fromarray(arr).resize((256, 256), Image.Resampling.BICUBIC)


def psnr(a: np.ndarray, b: np.ndarray) -> float:
    mse = float(np.mean((a - b) ** 2))
    if mse == 0:
        return 99.0
    return 20.0 * np.log10(255.0 / np.sqrt(mse))


def global_ssim_luma(a: np.ndarray, b: np.ndarray) -> float:
    wa = 0.299 * a[:, :, 0] + 0.587 * a[:, :, 1] + 0.114 * a[:, :, 2]
    wb = 0.299 * b[:, :, 0] + 0.587 * b[:, :, 1] + 0.114 * b[:, :, 2]
    c1 = (0.01 * 255) ** 2
    c2 = (0.03 * 255) ** 2
    mu_a = float(wa.mean())
    mu_b = float(wb.mean())
    var_a = float(wa.var())
    var_b = float(wb.var())
    cov = float(((wa - mu_a) * (wb - mu_b)).mean())
    return ((2 * mu_a * mu_b + c1) * (2 * cov + c2)) / ((mu_a**2 + mu_b**2 + c1) * (var_a + var_b + c2))


def edge_diff(a_path: Path, b_path: Path, direction: str) -> float:
    a = image_array(a_path)
    b = image_array(b_path)
    if direction == "right":
        return float(np.mean(np.abs(a[:, -1, :] - b[:, 0, :])))
    if direction == "down":
        return float(np.mean(np.abs(a[-1, :, :] - b[0, :, :])))
    raise ValueError(direction)


def tile_key(row: dict[str, str]) -> tuple[int, int, int]:
    return int(row["z"]), int(row["x"]), int(row["y"])


def summarize_numeric(rows: list[dict[str, str]], key: str) -> dict[str, float]:
    values = np.asarray([float(row[key]) for row in rows], dtype=np.float32)
    return {
        "mean": round(float(values.mean()), 6),
        "median": round(float(np.median(values)), 6),
        "p10": round(float(np.quantile(values, 0.1)), 6),
        "p90": round(float(np.quantile(values, 0.9)), 6),
    }


def build_patch_bank(train: list[dict[str, str]]) -> tuple[np.ndarray, list[np.ndarray], list[str]]:
    features: list[np.ndarray] = []
    map_patches: list[np.ndarray] = []
    patch_ids: list[str] = []
    for row in train:
        feats, coords = patch_features(ROOT / row["rs_path"])
        patches = lowres_map_patches(ROOT / row["map_path"])
        features.append(feats)
        map_patches.extend(patches)
        patch_ids.extend(f"{row['tile']}:{x}:{y}" for x, y in coords)
    return np.vstack(features).astype(np.float32), map_patches, patch_ids


def retrieve_patch_indices(query: np.ndarray, bank: np.ndarray, chunk: int = 512) -> np.ndarray:
    query = np.nan_to_num(query.astype(np.float64), nan=0.0, posinf=0.0, neginf=0.0)
    bank = np.nan_to_num(bank.astype(np.float64), nan=0.0, posinf=0.0, neginf=0.0)
    best_dist = np.full(query.shape[0], np.inf, dtype=np.float64)
    best_idx = np.zeros(query.shape[0], dtype=np.int32)
    for start in range(0, bank.shape[0], chunk):
        part = bank[start : start + chunk]
        dists = np.sum((query[:, None, :] - part[None, :, :]) ** 2, axis=2)
        local = np.argmin(dists, axis=1)
        local_dist = dists[np.arange(query.shape[0]), local]
        update = local_dist < best_dist
        best_dist[update] = local_dist[update]
        best_idx[update] = start + local[update]
    return best_idx


def run_baseline(train_limit: int = 200, val_limit: int = 100) -> tuple[list[dict[str, str]], list[dict[str, str]], dict[str, object]]:
    if GEN_DIR.exists():
        shutil.rmtree(GEN_DIR)
    GEN_DIR.mkdir(parents=True, exist_ok=True)
    train = [row for row in read_csv(TRAIN_MANIFEST) if row["has_map"] == "True"][:train_limit]
    val = [row for row in read_csv(VAL_MANIFEST) if row["has_map"] == "True"][:val_limit]

    val_tiles = {row["tile"] for row in val}
    overlap = sorted({row["tile"] for row in train} & val_tiles)
    train = [row for row in train if row["tile"] not in val_tiles]
    bank, map_patches, patch_ids = build_patch_bank(train)

    rows: list[dict[str, str]] = []
    generated_index: dict[tuple[int, int, int], Path] = {}
    patch_usage: dict[str, int] = {}
    for row in val:
        q, coords = patch_features(ROOT / row["rs_path"])
        indices = retrieve_patch_indices(q, bank)
        canvas = np.zeros((LOW_RES, LOW_RES, 3), dtype=np.float32)
        for idx, (x, y) in zip(indices, coords):
            canvas[y : y + PATCH, x : x + PATCH, :] = map_patches[int(idx)]
            patch_tile = patch_ids[int(idx)].split(":", 1)[0]
            patch_usage[patch_tile] = patch_usage.get(patch_tile, 0) + 1
        generated_path = GEN_DIR / f"{row['tile']}_patch_embedding_retrieval.png"
        output_image(canvas).save(generated_path)
        generated_index[tile_key(row)] = generated_path

        pred = image_array(generated_path)
        target = image_array(ROOT / row["map_path"])
        rows.append(
            {
                "split": "val",
                "tile": row["tile"],
                "z": row["z"],
                "x": row["x"],
                "y": row["y"],
                "patches": str(len(indices)),
                "unique_source_tiles": str(len({patch_ids[int(idx)].split(':', 1)[0] for idx in indices})),
                "mae_rgb": f"{float(np.mean(np.abs(pred - target))):.6f}",
                "psnr_rgb": f"{psnr(pred, target):.6f}",
                "global_ssim_luma": f"{global_ssim_luma(pred, target):.6f}",
                "val_rs_path": row["rs_path"],
                "generated_map_path": str(generated_path.relative_to(ROOT)),
                "target_map_path": row["map_path"],
            }
        )

    edge_rows: list[dict[str, str]] = []
    val_by_key = {tile_key(row): row for row in val}
    for key in sorted(val_by_key):
        z, x, y = key
        for direction, nkey in [("right", (z, x + 1, y)), ("down", (z, x, y + 1))]:
            if nkey not in generated_index:
                continue
            edge_rows.append(
                {
                    "split": "val",
                    "folder": "patch_embedding_retrieval_generated",
                    "z": str(z),
                    "x": str(x),
                    "y": str(y),
                    "neighbor_x": str(nkey[1]),
                    "neighbor_y": str(nkey[2]),
                    "direction": direction,
                    "edge_absdiff_rgb": f"{edge_diff(generated_index[key], generated_index[nkey], direction):.6f}",
                    "tile": Path(generated_index[key]).name,
                    "neighbor": Path(generated_index[nkey]).name,
                }
            )

    metadata = {
        "model": f"{LOW_RES}x{LOW_RES} RS patch nearest-neighbor retrieval, patch={PATCH}",
        "input_feature_dimension": int(bank.shape[1]),
        "patch_bank_size": int(bank.shape[0]),
        "patches_per_output": int((LOW_RES // PATCH) ** 2),
        "train_candidates_before_overlap_filter": train_limit,
        "train_samples_after_overlap_filter": len(train),
        "train_val_tile_overlap_excluded": len(overlap),
        "train_val_tile_overlap_excluded_examples": overlap[:10],
        "unique_source_tiles_used": len(patch_usage),
    }
    return rows, edge_rows, metadata


def write_contact_sheet(rows: list[dict[str, str]], limit: int = 12) -> None:
    selected = sorted(rows, key=lambda row: float(row["mae_rgb"]))[: limit // 2]
    selected += sorted(rows, key=lambda row: float(row["mae_rgb"]), reverse=True)[: limit - len(selected)]
    if not selected:
        return
    thumb = 128
    pad = 14
    label_h = 76
    cols = 3
    cell_w = thumb * 3 + pad * 2
    cell_h = thumb + label_h + pad * 2
    sheet = Image.new("RGB", (cols * cell_w, ((len(selected) + cols - 1) // cols) * cell_h), "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for i, row in enumerate(selected):
        x0 = (i % cols) * cell_w + pad
        y0 = (i // cols) * cell_h + pad
        paths = [ROOT / row["val_rs_path"], ROOT / row["generated_map_path"], ROOT / row["target_map_path"]]
        labels = ["val RS", "patch retrieval", "target"]
        for j, path in enumerate(paths):
            with Image.open(path) as image:
                image = image.convert("RGB")
                image.thumbnail((thumb, thumb))
                sheet.paste(image, (x0 + j * thumb, y0))
            draw.text((x0 + j * thumb, y0 + thumb + 2), labels[j], fill=(0, 0, 0), font=font)
        draw.text((x0, y0 + thumb + 18), row["tile"], fill=(0, 0, 0), font=font)
        draw.text((x0, y0 + thumb + 32), f"src tiles {row['unique_source_tiles']} patches {row['patches']}", fill=(0, 0, 0), font=font)
        draw.text((x0, y0 + thumb + 46), f"MAE {row['mae_rgb']} SSIM {row['global_ssim_luma']}", fill=(120, 0, 0), font=font)
    sheet.save(OUT_DIR / "scgm_patch_embedding_retrieval_contact_sheet.jpg", quality=90)


def write_report(summary: dict[str, object]) -> None:
    lines = [
        "# SCGM Patch-Embedding Retrieval Baseline",
        "",
        "This baseline builds validation map tiles by retrieving local remote-sensing patches from the train split and copying their paired map patches.",
        "It is a dependency-light image-to-image diagnostic: local and mosaic-like, but not a trained CNN, GAN, or diffusion model.",
        "",
        "## Model",
        "",
        f"- estimator: {summary['model']}",
        f"- input feature dimension: {summary['input_feature_dimension']}",
        f"- patch bank size: {summary['patch_bank_size']}",
        f"- patches per output: {summary['patches_per_output']}",
        f"- train/validation tile overlap excluded before retrieval: {summary['train_val_tile_overlap_excluded']}",
        f"- unique source tiles used: {summary['unique_source_tiles_used']}",
        "",
        "## Summary",
        "",
        f"- train tiles: {summary['train_samples']}",
        f"- validation outputs: {summary['validation_outputs']}",
        f"- MAE RGB: {summary['mae_rgb']}",
        f"- PSNR RGB: {summary['psnr_rgb']}",
        f"- global SSIM luma: {summary['global_ssim_luma']}",
        f"- generated edge continuity: {summary['generated_edge_continuity']}",
        "",
        "## Interpretation",
        "",
        "- Patch retrieval tests local image-to-image transfer more directly than whole-tile retrieval.",
        "- The mosaic construction can preserve local color/texture cues, but it has no learned global cartographic structure and can create patch seams.",
        "- The result is a reproducible lower-bound bridge toward trained pix2pix/CNN or diffusion SCGM reproduction.",
        "",
    ]
    (OUT_DIR / "scgm_patch_embedding_retrieval_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    rows, edge_rows, metadata = run_baseline()
    write_csv(OUT_DIR / "scgm_patch_embedding_retrieval_metrics.csv", rows)
    write_csv(OUT_DIR / "scgm_patch_embedding_retrieval_edge_continuity.csv", edge_rows)
    summary: dict[str, object] = {
        **metadata,
        "train_samples": metadata["train_samples_after_overlap_filter"],
        "validation_outputs": len(rows),
        "mae_rgb": summarize_numeric(rows, "mae_rgb"),
        "psnr_rgb": summarize_numeric(rows, "psnr_rgb"),
        "global_ssim_luma": summarize_numeric(rows, "global_ssim_luma"),
        "generated_edge_continuity": summarize_numeric(edge_rows, "edge_absdiff_rgb") if edge_rows else {},
    }
    (OUT_DIR / "scgm_patch_embedding_retrieval_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_contact_sheet(rows)
    write_report(summary)
    print(f"Wrote {OUT_DIR.relative_to(ROOT)}/scgm_patch_embedding_retrieval_metrics.csv")
    print(f"Wrote {OUT_DIR.relative_to(ROOT)}/scgm_patch_embedding_retrieval_summary.json")
    print(f"Wrote {OUT_DIR.relative_to(ROOT)}/scgm_patch_embedding_retrieval_report.md")


if __name__ == "__main__":
    main()
