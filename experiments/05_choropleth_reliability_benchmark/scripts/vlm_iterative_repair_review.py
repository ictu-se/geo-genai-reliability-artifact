#!/usr/bin/env python3
"""Local VLM review for iterative repair visual outputs."""

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
EXP_DIR = ROOT / "experiments/05_choropleth_reliability_benchmark"
OUT_DIR = EXP_DIR / "outputs/scores"
DETAIL_CSV = OUT_DIR / "iterative_repair_screenshot_qa_detail.csv"


PROMPT = """You are reviewing a rendered GIS/cartographic artifact produced by repairing LLM-generated Python code.

Return JSON only with this exact schema:
{
  "cartographic_quality_score": number from 0 to 1,
  "map_content_visible": boolean,
  "has_title": boolean,
  "has_legend_or_colorbar": boolean,
  "text_readable": boolean,
  "layout_not_occluded": boolean,
  "appears_thematic_map_or_valid_plot": boolean,
  "main_issue": "short phrase",
  "verdict": "publication_ready" or "usable_with_minor_issues" or "weak" or "failed"
}

Judge only what is visible. Be conservative: blank axes, weak thematic content, tiny unreadable labels, or non-map artifacts should receive a low score.
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


def safe_model_slug(model: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", model)


def review_image_path(row: dict[str, str]) -> Path | None:
    if row.get("screenshot_path"):
        return ROOT / row["screenshot_path"]
    path = ROOT / row.get("artifact_path", "")
    if path.suffix.lower() in {".png", ".jpg", ".jpeg"}:
        return path
    return None


def select_rows(rows: list[dict[str, str]], limit: int) -> list[dict[str, str]]:
    candidates = []
    for row in rows:
        if row.get("content_qa_pass") != "True":
            continue
        image_path = review_image_path(row)
        if not image_path or not image_path.exists() or image_path.stat().st_size == 0:
            continue
        candidates.append(row)
    candidates.sort(key=lambda r: (r["repair_model"], r["kind"], r["prompt_id"], r["source_model"], r["mode"], r["iteration"]))
    by_model: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in candidates:
        by_model[row["repair_model"]].append(row)
    selected: list[dict[str, str]] = []
    model_order = ["qwen2.5-coder_32b", "qwen2.5-coder_14b", "qwen2.5-coder_7b", "deepseek-coder_6.7b"]
    quota = max(1, limit // max(1, len([m for m in model_order if m in by_model])))
    for model in model_order:
        selected.extend(by_model.get(model, [])[:quota])
    for row in candidates:
        if len(selected) >= limit:
            break
        if row not in selected:
            selected.append(row)
    return selected[:limit]


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


def call_ollama(model: str, image_path: Path, timeout: int, num_predict: int) -> dict[str, object]:
    payload = {
        "model": model,
        "prompt": PROMPT,
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


def normalize(result: dict[str, object]) -> dict[str, str]:
    try:
        score = max(0.0, min(1.0, float(result.get("cartographic_quality_score", ""))))
        score_text = f"{score:.3f}"
    except Exception:
        score_text = ""
    return {
        "vlm_cartographic_quality_score": score_text,
        "vlm_map_content_visible": str(result.get("map_content_visible", "")),
        "vlm_has_title": str(result.get("has_title", "")),
        "vlm_has_legend_or_colorbar": str(result.get("has_legend_or_colorbar", "")),
        "vlm_text_readable": str(result.get("text_readable", "")),
        "vlm_layout_not_occluded": str(result.get("layout_not_occluded", "")),
        "vlm_appears_thematic_map_or_valid_plot": str(result.get("appears_thematic_map_or_valid_plot", "")),
        "vlm_main_issue": str(result.get("main_issue", "")),
        "vlm_verdict": str(result.get("verdict", "")),
        "vlm_raw_response": str(result.get("_raw_response", "")),
    }


def summarize(rows: list[dict[str, str]], model: str) -> dict[str, object]:
    by_repair: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_repair[row["repair_model"]].append(row)
    summary: dict[str, object] = {"vlm_model": model, "reviewed_artifacts": len(rows), "by_repair_model": {}}
    for repair_model, group in sorted(by_repair.items()):
        scores = [float(row["vlm_cartographic_quality_score"]) for row in group if row.get("vlm_cartographic_quality_score")]
        verdicts = Counter(row.get("vlm_verdict", "") for row in group)
        summary["by_repair_model"][repair_model] = {
            "reviewed_artifacts": len(group),
            "mean_score": round(sum(scores) / len(scores), 3) if scores else 0,
            "verdict_counts": dict(verdicts),
            "title_count": sum(row.get("vlm_has_title") == "True" for row in group),
            "legend_or_colorbar_count": sum(row.get("vlm_has_legend_or_colorbar") == "True" for row in group),
            "readable_count": sum(row.get("vlm_text_readable") == "True" for row in group),
            "thematic_or_valid_plot_count": sum(row.get("vlm_appears_thematic_map_or_valid_plot") == "True" for row in group),
        }
    return summary


def write_report(rows: list[dict[str, str]], summary: dict[str, object], path: Path) -> None:
    lines = [
        "# Iterative Repair VLM Visual Review",
        "",
        f"- VLM model: `{summary['vlm_model']}`",
        f"- reviewed artifacts: {summary['reviewed_artifacts']}",
        "- scope: content-QA-pass iterative repair outputs; VLM review is a visual sanity check, not human ground truth.",
        "",
        "| Repair model | Reviewed | Mean score | Verdict counts | Title | Legend/colorbar | Readable | Thematic/valid plot |",
        "|---|---:|---:|---|---:|---:|---:|---:|",
    ]
    for repair_model, item in summary["by_repair_model"].items():
        lines.append(
            f"| {repair_model} | {item['reviewed_artifacts']} | {item['mean_score']} | {item['verdict_counts']} | {item['title_count']} | {item['legend_or_colorbar_count']} | {item['readable_count']} | {item['thematic_or_valid_plot_count']} |"
        )
    lines += [
        "",
        "## Reviewed Artifacts",
        "",
        "| Repair model | Source | Kind | Prompt | Score | Verdict | Main issue | Image |",
        "|---|---|---|---|---:|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['repair_model']} | {row['source_model']} {row['mode']} | {row['kind']} | {row['prompt_id']} | {row['vlm_cartographic_quality_score']} | {row['vlm_verdict']} | {row['vlm_main_issue'].replace('|', '/')} | `{row['review_image_path']}` |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="granite3.2-vision:latest")
    parser.add_argument("--limit", type=int, default=24)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--num-predict", type=int, default=180)
    parser.add_argument("--sleep", type=float, default=0.0)
    args = parser.parse_args()

    model_slug = safe_model_slug(args.model)
    out_csv = OUT_DIR / f"iterative_repair_vlm_review_{model_slug}.csv"
    out_json = OUT_DIR / f"iterative_repair_vlm_review_summary_{model_slug}.json"
    out_md = OUT_DIR / f"iterative_repair_vlm_review_{model_slug}.md"

    selected = select_rows(read_csv(DETAIL_CSV), args.limit)
    existing: dict[str, dict[str, str]] = {}
    if out_csv.exists():
        for row in read_csv(out_csv):
            existing[row["review_image_path"]] = row

    rows: list[dict[str, str]] = []
    for row in selected:
        image_path = review_image_path(row)
        assert image_path is not None
        rel_image = str(image_path.relative_to(ROOT))
        if rel_image in existing:
            rows.append(existing[rel_image])
            print(f"cached: {rel_image}", flush=True)
            continue
        try:
            result = call_ollama(args.model, image_path, args.timeout, args.num_predict)
            merged = {**row, "review_image_path": rel_image, **normalize(result)}
            print(f"reviewed: {row['repair_model']} {row['kind']} {row['prompt_id']} score={merged['vlm_cartographic_quality_score']} verdict={merged['vlm_verdict']}", flush=True)
        except Exception as exc:
            merged = {
                **row,
                "review_image_path": rel_image,
                "vlm_cartographic_quality_score": "",
                "vlm_map_content_visible": "",
                "vlm_has_title": "",
                "vlm_has_legend_or_colorbar": "",
                "vlm_text_readable": "",
                "vlm_layout_not_occluded": "",
                "vlm_appears_thematic_map_or_valid_plot": "",
                "vlm_main_issue": f"review_error:{type(exc).__name__}",
                "vlm_verdict": "failed",
                "vlm_raw_response": str(exc)[:500],
            }
            print(f"review_error: {rel_image} {type(exc).__name__}: {exc}", flush=True)
        rows.append(merged)
        if args.sleep:
            time.sleep(args.sleep)

    summary = summarize(rows, args.model)
    write_csv(out_csv, rows)
    out_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_report(rows, summary, out_md)
    print(f"Wrote {out_csv.relative_to(ROOT)}")
    print(f"Wrote {out_json.relative_to(ROOT)}")
    print(f"Wrote {out_md.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
