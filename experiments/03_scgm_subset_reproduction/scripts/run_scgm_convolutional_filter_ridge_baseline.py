#!/usr/bin/env python3
"""Run a convolutional filter-bank ridge baseline for SCGM/CSCMG tiles.

This dependency-light baseline approximates the front end of a small CNN with
fixed Sobel, Laplacian, Gaussian, and local-context filters, then learns a
shared ridge regressor from per-pixel convolutional features to map RGB. It is
not a trained CNN or diffusion model, but it tests whether multiscale
convolutional image features improve the local-context RS-to-map diagnostic.
"""

from __future__ import annotations

import csv
import json
import warnings
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = ROOT / "experiments/03_scgm_subset_reproduction/outputs"
GEN_DIR = OUT_DIR / "scgm_convolutional_filter_ridge_generated_maps"
TRAIN_MANIFEST = OUT_DIR / "scgm_subset_manifest_train_first200.csv"
VAL_MANIFEST = OUT_DIR / "scgm_subset_manifest_val_first200.csv"
LOW_RES = 64

warnings.filterwarnings("ignore", category=RuntimeWarning)
np.seterr(all="ignore")


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


def conv_features(path: Path) -> np.ndarray:
    rgb = lowres_rgb(path)
    gray = 0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]

    features = [rgb]
    for sigma in (0.7, 1.5, 3.0):
        blurred = ndimage.gaussian_filter(rgb, sigma=(sigma, sigma, 0))
        features.append(blurred)
        features.append(rgb - blurred)

    sobel_x = ndimage.sobel(gray, axis=1)
    sobel_y = ndimage.sobel(gray, axis=0)
    grad_mag = np.sqrt(sobel_x**2 + sobel_y**2)
    laplace = ndimage.laplace(gray)
    gray_blur = ndimage.gaussian_filter(gray, sigma=2.0)
    features.extend([sobel_x[:, :, None], sobel_y[:, :, None], grad_mag[:, :, None], laplace[:, :, None], gray_blur[:, :, None]])

    padded = np.pad(rgb, ((2, 2), (2, 2), (0, 0)), mode="edge")
    for dy, dx in ((0, 0), (0, 2), (0, 4), (2, 0), (2, 4), (4, 0), (4, 2), (4, 4)):
        features.append(padded[dy : dy + LOW_RES, dx : dx + LOW_RES, :])

    yy, xx = np.mgrid[0:LOW_RES, 0:LOW_RES].astype(np.float32)
    coords = np.stack([xx / (LOW_RES - 1), yy / (LOW_RES - 1)], axis=2)
    features.append(coords)
    return np.concatenate(features, axis=2).reshape(-1, sum(item.shape[2] for item in features)).astype(np.float32)


def target_pixels(path: Path) -> np.ndarray:
    return lowres_rgb(path).reshape(-1, 3).astype(np.float32)


def prediction_image(pixels: np.ndarray) -> Image.Image:
    arr = np.clip(pixels.reshape(LOW_RES, LOW_RES, 3) * 255.0, 0, 255).astype(np.uint8)
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

    val_tiles = {row["tile"] for row in val}
    overlap = sorted({row["tile"] for row in train} & val_tiles)
    train = [row for row in train if row["tile"] not in val_tiles]

    x_train = np.vstack([conv_features(ROOT / row["rs_path"]) for row in train]).astype(np.float64)
    y_train = np.vstack([target_pixels(ROOT / row["map_path"]) for row in train]).astype(np.float64)
    model = make_pipeline(StandardScaler(), Ridge(alpha=2.5, random_state=31))
    model.fit(x_train, y_train)

    rows: list[dict[str, str]] = []
    generated_index: dict[tuple[int, int, int], Path] = {}
    for row in val:
        pred_pixels = model.predict(conv_features(ROOT / row["rs_path"]))
        generated_path = GEN_DIR / f"{row['tile']}_conv_filter_ridge.png"
        prediction_image(pred_pixels).save(generated_path)
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
    for key in sorted(val_by_key):
        z, x, y = key
        for direction, nkey in [("right", (z, x + 1, y)), ("down", (z, x, y + 1))]:
            if nkey not in generated_index:
                continue
            edge_rows.append(
                {
                    "split": "val",
                    "folder": "convolutional_filter_ridge_generated",
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
        "model": "StandardScaler + Ridge(alpha=2.5) over fixed convolutional RS filter bank",
        "input_feature_dimension": int(x_train.shape[1]),
        "training_pixel_samples": int(x_train.shape[0]),
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
        labels = ["val RS", "conv ridge", "target"]
        for j, path in enumerate(paths):
            with Image.open(path) as image:
                image = image.convert("RGB")
                image.thumbnail((thumb, thumb))
                sheet.paste(image, (x0 + j * thumb, y0))
            draw.text((x0 + j * thumb, y0 + thumb + 2), labels[j], fill=(0, 0, 0), font=font)
        draw.text((x0, y0 + thumb + 18), row["tile"], fill=(0, 0, 0), font=font)
        draw.text((x0, y0 + thumb + 32), f"MAE {row['mae_rgb']} PSNR {row['psnr_rgb']} SSIM {row['global_ssim_luma']}", fill=(120, 0, 0), font=font)
    sheet.save(OUT_DIR / "scgm_convolutional_filter_ridge_contact_sheet.jpg", quality=90)


def write_report(summary: dict[str, object]) -> None:
    lines = [
        "# SCGM Convolutional Filter-Bank Ridge Baseline",
        "",
        "This baseline uses fixed multiscale convolutional features over remote-sensing tiles and a shared per-pixel ridge regressor to generate map RGB values.",
        "It is a CPU-friendly CNN-style diagnostic, not a trained CNN or diffusion reproduction.",
        "",
        "## Model",
        "",
        f"- estimator: {summary['model']}",
        f"- input feature dimension: {summary['input_feature_dimension']}",
        f"- training pixel samples: {summary['training_pixel_samples']}",
        f"- output target: {summary['low_resolution_output']}",
        f"- train/validation tile overlap excluded before fitting: {summary['train_val_tile_overlap_excluded']}",
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
        "- The model tests whether fixed convolutional texture and edge features add value beyond a simple 3x3 local RGB context.",
        "- Because the filters are fixed and the regressor is per-pixel, it still cannot synthesize labels, road topology, or long-range cartographic structure.",
        "- The result is best reported as a dependency-light CNN-style diagnostic and a bridge toward a trained pix2pix/CNN or diffusion reproduction.",
        "",
    ]
    (OUT_DIR / "scgm_convolutional_filter_ridge_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    rows, edge_rows, metadata = run_baseline()
    write_csv(OUT_DIR / "scgm_convolutional_filter_ridge_metrics.csv", rows)
    write_csv(OUT_DIR / "scgm_convolutional_filter_ridge_edge_continuity.csv", edge_rows)
    summary = {
        **metadata,
        "train_samples": metadata["train_samples_after_overlap_filter"],
        "validation_outputs": len(rows),
        "mae_rgb": summarize_numeric(rows, "mae_rgb"),
        "psnr_rgb": summarize_numeric(rows, "psnr_rgb"),
        "global_ssim_luma": summarize_numeric(rows, "global_ssim_luma"),
        "generated_edge_continuity": summarize_numeric(edge_rows, "edge_absdiff_rgb") if edge_rows else {},
    }
    (OUT_DIR / "scgm_convolutional_filter_ridge_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_contact_sheet(rows)
    write_report(summary)
    print(f"Wrote {len(rows)} generated SCGM convolutional-filter ridge outputs")


if __name__ == "__main__":
    main()
