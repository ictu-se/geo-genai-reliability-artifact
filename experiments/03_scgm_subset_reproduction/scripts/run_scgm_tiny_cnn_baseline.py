#!/usr/bin/env python3
"""Run a tiny trained CNN RS-to-map baseline for SCGM/CSCMG tiles.

This is a CPU/MPS-friendly pix2pix-style lower-bound baseline. It trains a
small fully convolutional network directly from remote-sensing RGB tiles to map
RGB tiles at 64x64 resolution, then upsamples generated outputs to 256x256 for
the same metric harness used by the other SCGM generated-output baselines.
"""

from __future__ import annotations

import csv
import json
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = ROOT / "experiments/03_scgm_subset_reproduction/outputs"
GEN_DIR = OUT_DIR / "scgm_tiny_cnn_generated_maps"
TRAIN_MANIFEST = OUT_DIR / "scgm_subset_manifest_train_first200.csv"
VAL_MANIFEST = OUT_DIR / "scgm_subset_manifest_val_first200.csv"
LOW_RES = 64


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


def lowres_tensor(path: Path) -> np.ndarray:
    with Image.open(path) as image:
        arr = np.asarray(image.convert("RGB").resize((LOW_RES, LOW_RES), Image.Resampling.BILINEAR), dtype=np.float32)
    return (arr.transpose(2, 0, 1) / 255.0).astype(np.float32)


def prediction_image(array: np.ndarray) -> Image.Image:
    arr = np.clip(array.transpose(1, 2, 0) * 255.0, 0, 255).astype(np.uint8)
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


def torch_status(prefix: str, status: dict[str, object]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / f"{prefix}_summary.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (OUT_DIR / f"{prefix}_report.md").write_text(
        "\n".join(
            [
                "# SCGM Tiny CNN Baseline",
                "",
                f"- status: {status.get('status', '')}",
                f"- reason: {status.get('reason', '')}",
                "",
            ]
        ),
        encoding="utf-8",
    )


def train_model(train: list[dict[str, str]], epochs: int, batch_size: int, seed: int):
    import torch  # type: ignore
    from torch import nn  # type: ignore
    from torch.utils.data import DataLoader, TensorDataset  # type: ignore

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

    class TinyCNN(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.net = nn.Sequential(
                nn.Conv2d(3, 24, kernel_size=3, padding=1),
                nn.ReLU(inplace=True),
                nn.Conv2d(24, 32, kernel_size=3, padding=1),
                nn.ReLU(inplace=True),
                nn.Conv2d(32, 32, kernel_size=3, padding=1),
                nn.ReLU(inplace=True),
                nn.Conv2d(32, 16, kernel_size=3, padding=1),
                nn.ReLU(inplace=True),
                nn.Conv2d(16, 3, kernel_size=1),
                nn.Sigmoid(),
            )

        def forward(self, x):
            return self.net(x)

    x = np.stack([lowres_tensor(ROOT / row["rs_path"]) for row in train])
    y = np.stack([lowres_tensor(ROOT / row["map_path"]) for row in train])
    dataset = TensorDataset(torch.from_numpy(x), torch.from_numpy(y))

    if torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")
    model = TinyCNN().to(device)
    loss_fn = nn.L1Loss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.003, weight_decay=0.0005)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True, generator=torch.Generator().manual_seed(seed))

    losses: list[float] = []
    for _ in range(epochs):
        epoch_losses: list[float] = []
        model.train()
        for xb, yb in loader:
            xb = xb.to(device)
            yb = yb.to(device)
            optimizer.zero_grad(set_to_none=True)
            pred = model(xb)
            loss = loss_fn(pred, yb)
            loss.backward()
            optimizer.step()
            epoch_losses.append(float(loss.detach().cpu()))
        losses.append(float(np.mean(epoch_losses)))
    return torch, model, device, losses


def run_baseline(train_limit: int = 200, val_limit: int = 100, epochs: int = 14, batch_size: int = 12, seed: int = 47) -> tuple[list[dict[str, str]], list[dict[str, str]], dict[str, object]]:
    GEN_DIR.mkdir(parents=True, exist_ok=True)
    train = [row for row in read_csv(TRAIN_MANIFEST) if row["has_map"] == "True"][:train_limit]
    val = [row for row in read_csv(VAL_MANIFEST) if row["has_map"] == "True"][:val_limit]

    val_tiles = {row["tile"] for row in val}
    overlap = sorted({row["tile"] for row in train} & val_tiles)
    train = [row for row in train if row["tile"] not in val_tiles]

    torch, model, device, losses = train_model(train, epochs=epochs, batch_size=batch_size, seed=seed)

    rows: list[dict[str, str]] = []
    generated_index: dict[tuple[int, int, int], Path] = {}
    model.eval()
    for row in val:
        source = torch.from_numpy(lowres_tensor(ROOT / row["rs_path"])[None, :, :, :]).to(device)
        with torch.no_grad():
            pred = model(source).detach().cpu().numpy()[0]
        generated_path = GEN_DIR / f"{row['tile']}_tiny_cnn.png"
        prediction_image(pred).save(generated_path)
        generated_index[tile_key(row)] = generated_path

        generated = image_array(generated_path)
        target = image_array(ROOT / row["map_path"])
        rows.append(
            {
                "split": "val",
                "tile": row["tile"],
                "z": row["z"],
                "x": row["x"],
                "y": row["y"],
                "mae_rgb": f"{float(np.mean(np.abs(generated - target))):.6f}",
                "psnr_rgb": f"{psnr(generated, target):.6f}",
                "global_ssim_luma": f"{global_ssim_luma(generated, target):.6f}",
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
                    "folder": "tiny_cnn_generated",
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
        "status": "completed",
        "model": "TinyCNN(3->24->32->32->16->3 conv stack, sigmoid output)",
        "model_family": "trained_cnn",
        "low_resolution_output": f"{LOW_RES}x{LOW_RES}x3",
        "epochs": epochs,
        "batch_size": batch_size,
        "seed": seed,
        "device": str(device),
        "train_candidates_before_overlap_filter": train_limit,
        "train_samples_after_overlap_filter": len(train),
        "train_val_tile_overlap_excluded": len(overlap),
        "train_val_tile_overlap_excluded_examples": overlap[:10],
        "training_loss_first": round(losses[0], 6) if losses else None,
        "training_loss_final": round(losses[-1], 6) if losses else None,
        "training_losses": [round(item, 6) for item in losses],
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
        labels = ["val RS", "tiny CNN", "target"]
        for j, path in enumerate(paths):
            with Image.open(path) as image:
                image = image.convert("RGB")
                image.thumbnail((thumb, thumb))
                sheet.paste(image, (x0 + j * thumb, y0))
            draw.text((x0 + j * thumb, y0 + thumb + 2), labels[j], fill=(0, 0, 0), font=font)
        draw.text((x0, y0 + thumb + 18), row["tile"], fill=(0, 0, 0), font=font)
        draw.text((x0, y0 + thumb + 32), f"MAE {row['mae_rgb']} PSNR {row['psnr_rgb']} SSIM {row['global_ssim_luma']}", fill=(120, 0, 0), font=font)
    sheet.save(OUT_DIR / "scgm_tiny_cnn_contact_sheet.jpg", quality=90)


def write_report(summary: dict[str, object]) -> None:
    lines = [
        "# SCGM Tiny Trained CNN Baseline",
        "",
        "This baseline trains a small fully convolutional RS-to-map model on the leakage-filtered SCGM subset.",
        "It is a lower-bound trained CNN condition, not an official SCGM diffusion reproduction.",
        "",
        "## Model",
        "",
        f"- estimator: {summary['model']}",
        f"- output target: {summary['low_resolution_output']}",
        f"- train tiles after overlap filtering: {summary['train_samples_after_overlap_filter']}",
        f"- validation outputs: {summary['validation_outputs']}",
        f"- train/validation tile overlap excluded before fitting: {summary['train_val_tile_overlap_excluded']}",
        f"- epochs: {summary['epochs']}",
        f"- device: {summary['device']}",
        f"- training loss first/final: {summary['training_loss_first']} / {summary['training_loss_final']}",
        "",
        "## Summary",
        "",
        f"- MAE RGB: {summary['mae_rgb']}",
        f"- PSNR RGB: {summary['psnr_rgb']}",
        f"- global SSIM luma: {summary['global_ssim_luma']}",
        f"- generated edge continuity: {summary['generated_edge_continuity']}",
        "",
        "## Interpretation",
        "",
        "- This closes the gap between fixed-filter diagnostics and a genuinely trained convolutional image-to-image baseline.",
        "- The model is intentionally small so that the experiment is reproducible on local CPU/MPS hardware.",
        "- The output should still be interpreted as a lower-bound diagnostic: it lacks cascade references, scale conditioning, adversarial/perceptual losses, and diffusion sampling.",
        "",
    ]
    (OUT_DIR / "scgm_tiny_cnn_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    try:
        rows, edge_rows, metadata = run_baseline()
    except Exception as exc:
        torch_status(
            "scgm_tiny_cnn",
            {
                "status": "dependency_or_runtime_failure",
                "reason": f"{type(exc).__name__}: {str(exc)[:500]}",
                "requires": ["torch", "numpy", "pillow"],
            },
        )
        raise

    summary = {
        **metadata,
        "train_samples": metadata["train_samples_after_overlap_filter"],
        "validation_outputs": len(rows),
        "mae_rgb": summarize_numeric(rows, "mae_rgb"),
        "psnr_rgb": summarize_numeric(rows, "psnr_rgb"),
        "global_ssim_luma": summarize_numeric(rows, "global_ssim_luma"),
        "generated_edge_pairs": len(edge_rows),
        "generated_edge_continuity": summarize_numeric(edge_rows, "edge_absdiff_rgb") if edge_rows else {},
    }
    write_csv(OUT_DIR / "scgm_tiny_cnn_metrics.csv", rows)
    write_csv(OUT_DIR / "scgm_tiny_cnn_edge_continuity.csv", edge_rows)
    (OUT_DIR / "scgm_tiny_cnn_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    write_contact_sheet(rows)
    write_report(summary)
    print(f"Wrote tiny CNN baseline for {len(rows)} validation outputs")


if __name__ == "__main__":
    main()
