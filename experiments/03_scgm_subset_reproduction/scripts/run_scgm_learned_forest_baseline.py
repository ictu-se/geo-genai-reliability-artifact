#!/usr/bin/env python3
"""Run a small learned RS-to-map baseline for SCGM/CSCMG tiles.

This baseline trains a random-forest regressor from remote-sensing tile
features to low-resolution map pixels, then upsamples predictions to 256x256.
It is intentionally lightweight and CPU-friendly, but unlike retrieval it learns
a mapping from RS appearance to cartographic output.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from sklearn.ensemble import RandomForestRegressor


ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = ROOT / "experiments/03_scgm_subset_reproduction/outputs"
GEN_DIR = OUT_DIR / "scgm_learned_forest_generated_maps"
TRAIN_MANIFEST = OUT_DIR / "scgm_subset_manifest_train_first200.csv"
VAL_MANIFEST = OUT_DIR / "scgm_subset_manifest_val_first200.csv"
LOW_RES = 16


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


def rs_feature(path: Path) -> np.ndarray:
    with Image.open(path) as image:
        rgb = image.convert("RGB")
        small = np.asarray(rgb.resize((16, 16), Image.Resampling.BILINEAR), dtype=np.float32).reshape(-1) / 255.0
        gray = rgb.convert("L")
        edges = gray.filter(ImageFilter.FIND_EDGES)
        edge_small = np.asarray(edges.resize((16, 16), Image.Resampling.BILINEAR), dtype=np.float32).reshape(-1) / 255.0
        arr = np.asarray(rgb, dtype=np.float32)

    flat = arr.reshape(-1, 3)
    mean = flat.mean(axis=0) / 255.0
    std = flat.std(axis=0) / 255.0
    q10 = np.quantile(flat, 0.10, axis=0) / 255.0
    q50 = np.quantile(flat, 0.50, axis=0) / 255.0
    q90 = np.quantile(flat, 0.90, axis=0) / 255.0
    return np.concatenate([small, edge_small, mean, std, q10, q50, q90]).astype(np.float32)


def target_lowres(path: Path) -> np.ndarray:
    with Image.open(path) as image:
        arr = np.asarray(image.convert("RGB").resize((LOW_RES, LOW_RES), Image.Resampling.BILINEAR), dtype=np.float32)
    return (arr.reshape(-1) / 255.0).astype(np.float32)


def prediction_image(vector: np.ndarray) -> Image.Image:
    arr = np.clip(vector.reshape(LOW_RES, LOW_RES, 3) * 255.0, 0, 255).astype(np.uint8)
    image = Image.fromarray(arr)
    return image.resize((256, 256), Image.Resampling.BICUBIC)


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


def summarize_numeric(rows: list[dict[str, str]], key: str) -> dict[str, float]:
    values = np.asarray([float(row[key]) for row in rows], dtype=np.float32)
    return {
        "mean": round(float(values.mean()), 6),
        "median": round(float(np.median(values)), 6),
        "p10": round(float(np.quantile(values, 0.1)), 6),
        "p90": round(float(np.quantile(values, 0.9)), 6),
    }


def run_baseline(train_limit: int = 200, val_limit: int = 100) -> tuple[list[dict[str, str]], list[dict[str, str]], dict[str, object]]:
    GEN_DIR.mkdir(parents=True, exist_ok=True)
    train = [row for row in read_csv(TRAIN_MANIFEST) if row["has_map"] == "True"][:train_limit]
    val = [row for row in read_csv(VAL_MANIFEST) if row["has_map"] == "True"][:val_limit]

    train_tiles = {row["tile"] for row in train}
    val_tiles = {row["tile"] for row in val}
    overlap = sorted(train_tiles & val_tiles)
    train = [row for row in train if row["tile"] not in val_tiles]

    x_train = np.vstack([rs_feature(ROOT / row["rs_path"]) for row in train]).astype(np.float64)
    y_train = np.vstack([target_lowres(ROOT / row["map_path"]) for row in train]).astype(np.float64)
    model = RandomForestRegressor(
        n_estimators=40,
        max_depth=12,
        min_samples_leaf=2,
        random_state=0,
        n_jobs=-1,
    )
    model.fit(x_train, y_train)

    rows: list[dict[str, str]] = []
    generated_index: dict[tuple[int, int, int], Path] = {}
    for row in val:
        pred_vec = model.predict(rs_feature(ROOT / row["rs_path"])[None, :])[0]
        generated_path = GEN_DIR / f"{row['tile']}_learned_forest.png"
        prediction_image(pred_vec).save(generated_path)
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
    for key, row in sorted(val_by_key.items()):
        z, x, y = key
        for direction, nkey in [("right", (z, x + 1, y)), ("down", (z, x, y + 1))]:
            if nkey not in generated_index:
                continue
            edge_rows.append(
                {
                    "split": "val",
                    "folder": "learned_forest_generated",
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
        "model": "RandomForestRegressor(n_estimators=40, max_depth=12, min_samples_leaf=2)",
        "input_feature_dimension": int(x_train.shape[1]),
        "output_dimension": int(y_train.shape[1]),
        "low_resolution_output": f"{LOW_RES}x{LOW_RES}x3",
        "train_candidates_before_overlap_filter": train_limit,
        "train_samples_after_overlap_filter": len(train),
        "train_val_tile_overlap_excluded": len(overlap),
        "train_val_tile_overlap_excluded_examples": overlap[:10],
    }
    return rows, edge_rows, metadata


def write_contact_sheet(rows: list[dict[str, str]], limit: int = 12) -> None:
    selected = sorted(rows, key=lambda row: float(row["mae_rgb"]))[: limit // 2]
    selected += sorted(rows, key=lambda row: float(row["mae_rgb"]), reverse=True)[: limit - len(selected)]
    if not selected:
        return
    thumb = 128
    pad = 14
    label_h = 70
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
        labels = ["val RS", "forest", "target"]
        for j, path in enumerate(paths):
            with Image.open(path) as image:
                image = image.convert("RGB")
                image.thumbnail((thumb, thumb))
                sheet.paste(image, (x0 + j * thumb, y0))
            draw.text((x0 + j * thumb, y0 + thumb + 2), labels[j], fill=(0, 0, 0), font=font)
        draw.text((x0, y0 + thumb + 18), row["tile"], fill=(0, 0, 0), font=font)
        draw.text((x0, y0 + thumb + 32), f"MAE {row['mae_rgb']} PSNR {row['psnr_rgb']} SSIM {row['global_ssim_luma']}", fill=(120, 0, 0), font=font)
    sheet.save(OUT_DIR / "scgm_learned_forest_contact_sheet.jpg", quality=90)


def write_report(summary: dict[str, object]) -> None:
    lines = [
        "# SCGM Learned Forest Baseline",
        "",
        "This baseline trains a CPU-friendly random-forest regressor from remote-sensing tile features to low-resolution map pixels.",
        "It is not a diffusion model and should be interpreted as a weak learned lower bound, but it is a genuine fitted RS-to-map mapping rather than nearest-neighbor retrieval.",
        "",
        "## Model",
        "",
        f"- estimator: {summary['model']}",
        f"- input feature dimension: {summary['input_feature_dimension']}",
        f"- output target: {summary['low_resolution_output']}",
        f"- train/validation tile overlap excluded before fitting: {summary['train_val_tile_overlap_excluded']}",
        "",
        "## Summary",
        "",
        f"- train samples: {summary['train_samples']}",
        f"- validation outputs: {summary['validation_outputs']}",
        f"- MAE RGB: {summary['mae_rgb']}",
        f"- PSNR RGB: {summary['psnr_rgb']}",
        f"- global SSIM luma: {summary['global_ssim_luma']}",
        f"- generated edge continuity: {summary['generated_edge_continuity']}",
        "",
        "## Interpretation",
        "",
        "- The model is intentionally small enough to rerun without GPU resources.",
        "- Low-resolution regression tends to smooth cartographic detail, so it should be compared against retrieval baselines as a lower bound rather than a competitive generator.",
        "- The baseline is useful because it makes the SCGM track include a learned generated-output condition with the same metric and leakage-audit scaffold as the retrieval baselines.",
        "",
    ]
    (OUT_DIR / "scgm_learned_forest_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    rows, edge_rows, metadata = run_baseline()
    write_csv(OUT_DIR / "scgm_learned_forest_metrics.csv", rows)
    write_csv(OUT_DIR / "scgm_learned_forest_edge_continuity.csv", edge_rows)
    summary: dict[str, object] = {
        **metadata,
        "train_samples": metadata["train_samples_after_overlap_filter"],
        "validation_outputs": len(rows),
        "mae_rgb": summarize_numeric(rows, "mae_rgb"),
        "psnr_rgb": summarize_numeric(rows, "psnr_rgb"),
        "global_ssim_luma": summarize_numeric(rows, "global_ssim_luma"),
        "generated_edge_continuity": summarize_numeric(edge_rows, "edge_absdiff_rgb") if edge_rows else {},
    }
    (OUT_DIR / "scgm_learned_forest_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_contact_sheet(rows)
    write_report(summary)
    print(f"Wrote {OUT_DIR.relative_to(ROOT)}/scgm_learned_forest_metrics.csv")
    print(f"Wrote {OUT_DIR.relative_to(ROOT)}/scgm_learned_forest_summary.json")
    print(f"Wrote {OUT_DIR.relative_to(ROOT)}/scgm_learned_forest_report.md")


if __name__ == "__main__":
    main()
