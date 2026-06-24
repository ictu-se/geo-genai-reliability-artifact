#!/usr/bin/env python3
"""Run local VLM caption-alignment review for MapGenerator samples."""

from __future__ import annotations

import argparse
import base64
import csv
import json
import re
import time
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT / "data/raw/MapGenerator"
OUT_DIR = ROOT / "experiments/02_mapgenerator_image_text_audit/outputs"
PROXY_CSV = OUT_DIR / "mapgenerator_proxy_caption_review.csv"


PROMPT_TEMPLATE = """You are auditing whether a map-image caption is visually supported.

Return JSON only with this exact schema:
{{
  "alignment_score": number from 0 to 1,
  "visible_water": boolean,
  "visible_roads": boolean,
  "visible_green_area": boolean,
  "visible_named_label": boolean,
  "caption_unsupported_claims": [short strings],
  "caption_omissions": [short strings],
  "verdict": "supported" or "partly_supported" or "weak"
}}

Judge the caption against the image. Be conservative: mark claims unsupported when the map image does not visibly support them.

Caption:
{caption}
"""


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


def select_rows(rows: list[dict[str, str]], limit: int | None) -> list[dict[str, str]]:
    severity_rank = {"high": 0, "medium": 1, "low": 2}
    selected: list[dict[str, str]] = []
    by_split: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_split[row["split"]].append(row)
    per_split = None if limit is None else max(1, limit // max(1, len(by_split)))
    for split, split_rows in sorted(by_split.items()):
        split_rows.sort(key=lambda row: (severity_rank.get(row["review_severity"], 9), float(row["proxy_fidelity_score"]), row["image"]))
        selected.extend(split_rows[:per_split] if per_split else split_rows)
    return selected[:limit] if limit else selected


def extract_json(text: str) -> dict[str, object]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.S)
        if match:
            return json.loads(match.group(0))
        raise


def call_ollama(model: str, image_path: Path, caption: str, timeout: int, num_predict: int) -> dict[str, object]:
    payload = {
        "model": model,
        "prompt": PROMPT_TEMPLATE.format(caption=caption),
        "images": [base64.b64encode(image_path.read_bytes()).decode("ascii")],
        "stream": False,
        "options": {"temperature": 0.0, "num_predict": num_predict},
    }
    req = urllib.request.Request(
        "http://127.0.0.1:11434/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    parsed = extract_json(data.get("response", ""))
    parsed["_raw_response"] = data.get("response", "").replace("\n", " ")[:500]
    return parsed


def normalize_result(result: dict[str, object]) -> dict[str, str]:
    score = result.get("alignment_score", "")
    try:
        score_text = f"{float(score):.3f}"
    except Exception:
        score_text = ""
    return {
        "vlm_alignment_score": score_text,
        "vlm_visible_water": str(result.get("visible_water", "")),
        "vlm_visible_roads": str(result.get("visible_roads", "")),
        "vlm_visible_green_area": str(result.get("visible_green_area", "")),
        "vlm_visible_named_label": str(result.get("visible_named_label", "")),
        "vlm_unsupported_claims": ";".join(result.get("caption_unsupported_claims", []) if isinstance(result.get("caption_unsupported_claims"), list) else []),
        "vlm_omissions": ";".join(result.get("caption_omissions", []) if isinstance(result.get("caption_omissions"), list) else []),
        "vlm_verdict": str(result.get("verdict", "")),
        "vlm_raw_response": str(result.get("_raw_response", "")),
    }


def summarize(rows: list[dict[str, str]], model: str) -> dict[str, object]:
    by_split: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_split[row["split"]].append(row)
    summary: dict[str, object] = {"model": model, "reviewed_pairs": len(rows), "by_split": {}}
    for split, split_rows in sorted(by_split.items()):
        verdicts = Counter(row["vlm_verdict"] for row in split_rows)
        scores = [float(row["vlm_alignment_score"]) for row in split_rows if row["vlm_alignment_score"]]
        proxy_scores = [float(row["proxy_fidelity_score"]) for row in split_rows if row["proxy_fidelity_score"]]
        summary["by_split"][split] = {
            "reviewed_pairs": len(split_rows),
            "mean_vlm_alignment_score": round(sum(scores) / len(scores), 3) if scores else 0,
            "mean_proxy_fidelity_score": round(sum(proxy_scores) / len(proxy_scores), 3) if proxy_scores else 0,
            "verdict_counts": dict(verdicts),
            "unsupported_claim_rows": sum(bool(row["vlm_unsupported_claims"]) for row in split_rows),
            "omission_rows": sum(bool(row["vlm_omissions"]) for row in split_rows),
        }
    return summary


def write_report(rows: list[dict[str, str]], summary: dict[str, object], path: Path) -> None:
    lines = [
        "# MapGenerator VLM Caption-Fidelity Review",
        "",
        f"- model: `{summary['model']}`",
        f"- reviewed pairs: {summary['reviewed_pairs']}",
        "",
        "## Summary",
        "",
    ]
    for split, item in summary["by_split"].items():
        lines += [
            f"### {split}",
            "",
            f"- reviewed pairs: {item['reviewed_pairs']}",
            f"- mean VLM alignment score: {item['mean_vlm_alignment_score']}",
            f"- mean proxy fidelity score: {item['mean_proxy_fidelity_score']}",
            f"- verdict counts: {item['verdict_counts']}",
            f"- rows with unsupported claims: {item['unsupported_claim_rows']}",
            f"- rows with omissions: {item['omission_rows']}",
            "",
        ]
    lines += [
        "## Lowest VLM Alignment Cases",
        "",
        "| Split | Image | Proxy | VLM | Verdict | Unsupported | Omissions |",
        "|---|---|---:|---:|---|---|---|",
    ]
    selected = sorted(rows, key=lambda row: (float(row["vlm_alignment_score"] or 0), row["split"], row["image"]))[:30]
    for row in selected:
        lines.append(
            f"| {row['split']} | `{row['image']}` | {row['proxy_fidelity_score']} | {row['vlm_alignment_score']} | {row['vlm_verdict']} | {row['vlm_unsupported_claims'].replace('|', '/')} | {row['vlm_omissions'].replace('|', '/')} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="qwen3-vl:4b")
    parser.add_argument("--limit", type=int, default=60)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--num-predict", type=int, default=180)
    parser.add_argument("--sleep", type=float, default=0.0)
    args = parser.parse_args()

    model_slug = args.model.replace(":", "_")
    out_csv = OUT_DIR / f"mapgenerator_vlm_caption_review_{model_slug}.csv"
    out_json = OUT_DIR / f"mapgenerator_vlm_caption_review_summary_{model_slug}.json"
    out_md = OUT_DIR / f"mapgenerator_vlm_caption_review_{model_slug}.md"

    proxy_rows = read_csv(PROXY_CSV)
    selected = select_rows(proxy_rows, args.limit)
    existing: dict[tuple[str, str], dict[str, str]] = {}
    if out_csv.exists():
        for row in read_csv(out_csv):
            existing[(row["split"], row["image"])] = row

    rows: list[dict[str, str]] = []
    for row in selected:
        key = (row["split"], row["image"])
        if key in existing:
            rows.append(existing[key])
            print(f"cached: {row['split']} {row['image']}")
            continue
        image_path = DATA_DIR / row["split"] / "Images" / row["image"]
        try:
            result = call_ollama(args.model, image_path, row["description"], args.timeout, args.num_predict)
            merged = {**row, **normalize_result(result)}
            print(f"reviewed: {row['split']} {row['image']} score={merged['vlm_alignment_score']} verdict={merged['vlm_verdict']}", flush=True)
        except Exception as exc:
            merged = {
                **row,
                "vlm_alignment_score": "",
                "vlm_visible_water": "",
                "vlm_visible_roads": "",
                "vlm_visible_green_area": "",
                "vlm_visible_named_label": "",
                "vlm_unsupported_claims": "",
                "vlm_omissions": "",
                "vlm_verdict": "error",
                "vlm_raw_response": f"{type(exc).__name__}: {exc}",
            }
            print(f"error: {row['split']} {row['image']} {type(exc).__name__}: {exc}", flush=True)
        rows.append(merged)
        write_csv(out_csv, rows)
        if args.sleep:
            time.sleep(args.sleep)

    summary = summarize(rows, args.model)
    out_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_report(rows, summary, out_md)
    print(f"Wrote {out_csv.relative_to(ROOT)}", flush=True)
    print(f"Wrote {out_json.relative_to(ROOT)}", flush=True)
    print(f"Wrote {out_md.relative_to(ROOT)}", flush=True)


if __name__ == "__main__":
    main()
