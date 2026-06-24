#!/usr/bin/env python3
"""Optional CLIP/SigLIP image-text scoring for MapGenerator captions.

This script is intentionally optional. If PyTorch/Transformers or the requested
model are unavailable, it writes a clear status file instead of failing the
manuscript pipeline.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from statistics import mean

from PIL import Image


ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT / "data/raw/MapGenerator"
INPUT = ROOT / "experiments/02_mapgenerator_image_text_audit/outputs/mapgenerator_proxy_caption_review.csv"
OUT_DIR = ROOT / "experiments/02_mapgenerator_image_text_audit/outputs"

DEFAULT_MODEL = "openai/clip-vit-base-patch32"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, data: dict[str, object]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def image_path(row: dict[str, str]) -> Path:
    return DATA_DIR / row["split"] / "Images" / row["image"]


def empty_outputs(prefix: str, status: dict[str, object]) -> None:
    write_csv(
        OUT_DIR / f"{prefix}_caption_embedding_scores.csv",
        [],
        [
            "split",
            "image",
            "model",
            "embedding_score",
            "proxy_fidelity_score",
            "review_severity",
            "description",
        ],
    )
    write_json(OUT_DIR / f"{prefix}_caption_embedding_summary.json", status)
    lines = [
        "# MapGenerator Caption Embedding Scoring",
        "",
        f"- status: {status['status']}",
        f"- model: {status.get('model', '')}",
        f"- reason: {status.get('reason', '')}",
        "",
        "This optional CLIP/SigLIP-style scoring layer was not executed successfully in the current environment. The manuscript should continue to treat embedding-based validation as a remaining Q1-strengthening gate until a real score table is produced.",
        "",
    ]
    (OUT_DIR / f"{prefix}_caption_embedding_report.md").write_text("\n".join(lines), encoding="utf-8")


def load_clip(model_name: str, local_files_only: bool):
    import torch  # type: ignore
    from transformers import CLIPModel, CLIPProcessor  # type: ignore

    model = CLIPModel.from_pretrained(model_name, local_files_only=local_files_only)
    processor = CLIPProcessor.from_pretrained(model_name, local_files_only=local_files_only)
    model.eval()
    return torch, model, processor


def score_clip(torch, model, processor, image: Image.Image, text: str) -> float:
    inputs = processor(text=[text], images=[image], return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        image_features = model.get_image_features(pixel_values=inputs["pixel_values"])
        text_features = model.get_text_features(input_ids=inputs["input_ids"], attention_mask=inputs["attention_mask"])
        image_features = image_features / image_features.norm(dim=-1, keepdim=True)
        text_features = text_features / text_features.norm(dim=-1, keepdim=True)
        score = (image_features @ text_features.T).item()
    return float(score)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--prefix", default="mapgenerator_clip")
    parser.add_argument("--limit", type=int, default=200)
    parser.add_argument("--local-files-only", action="store_true")
    args = parser.parse_args()

    try:
        torch, model, processor = load_clip(args.model, args.local_files_only)
    except Exception as exc:
        empty_outputs(
            args.prefix,
            {
                "status": "dependency_or_model_missing",
                "model": args.model,
                "scored_pairs": 0,
                "reason": f"{type(exc).__name__}: {str(exc)[:500]}",
                "requires": ["torch", "transformers", "CLIPModel/CLIPProcessor-compatible model"],
            },
        )
        print(f"Wrote missing-model status for {args.model}")
        return

    rows = read_csv(INPUT)[: args.limit]
    scored: list[dict[str, str]] = []
    errors: list[str] = []
    for row in rows:
        path = image_path(row)
        try:
            with Image.open(path) as img:
                score = score_clip(torch, model, processor, img.convert("RGB"), row["description"])
            scored.append(
                {
                    "split": row["split"],
                    "image": row["image"],
                    "model": args.model,
                    "embedding_score": f"{score:.6f}",
                    "proxy_fidelity_score": row["proxy_fidelity_score"],
                    "review_severity": row["review_severity"],
                    "description": row["description"],
                }
            )
        except Exception as exc:
            errors.append(f"{row['split']}/{row['image']}: {type(exc).__name__}: {str(exc)[:160]}")

    fieldnames = [
        "split",
        "image",
        "model",
        "embedding_score",
        "proxy_fidelity_score",
        "review_severity",
        "description",
    ]
    write_csv(OUT_DIR / f"{args.prefix}_caption_embedding_scores.csv", scored, fieldnames)
    scores = [float(row["embedding_score"]) for row in scored]
    summary = {
        "status": "completed",
        "model": args.model,
        "requested_pairs": len(rows),
        "scored_pairs": len(scored),
        "errors": len(errors),
        "mean_embedding_score": round(mean(scores), 6) if scores else None,
        "min_embedding_score": round(min(scores), 6) if scores else None,
        "max_embedding_score": round(max(scores), 6) if scores else None,
        "local_files_only": args.local_files_only,
        "error_examples": errors[:10],
    }
    write_json(OUT_DIR / f"{args.prefix}_caption_embedding_summary.json", summary)
    report = [
        "# MapGenerator Caption Embedding Scoring",
        "",
        f"- status: {summary['status']}",
        f"- model: {summary['model']}",
        f"- scored pairs: {summary['scored_pairs']}/{summary['requested_pairs']}",
        f"- mean embedding score: {summary['mean_embedding_score']}",
        f"- errors: {summary['errors']}",
        "",
    ]
    (OUT_DIR / f"{args.prefix}_caption_embedding_report.md").write_text("\n".join(report), encoding="utf-8")
    print(f"Wrote embedding scores for {len(scored)} pairs")


if __name__ == "__main__":
    main()
