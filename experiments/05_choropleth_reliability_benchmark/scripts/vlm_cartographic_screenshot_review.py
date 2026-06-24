#!/usr/bin/env python3
"""Run local VLM cartographic-quality review for choropleth screenshots."""

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
DETAIL_CSV = OUT_DIR / "screenshot_level_qa_detail.csv"


PROMPT = """You are reviewing a rendered choropleth-map artifact for cartographic quality.

Return JSON only with this exact schema:
{
  "cartographic_quality_score": number from 0 to 1,
  "map_content_visible": boolean,
  "has_title": boolean,
  "has_legend_or_colorbar": boolean,
  "text_readable": boolean,
  "layout_not_occluded": boolean,
  "appears_choropleth": boolean,
  "main_issue": "short phrase",
  "verdict": "publication_ready" or "usable_with_minor_issues" or "weak" or "failed"
}

Judge only what is visible in the image. Be conservative: a blank, tiny, cropped, unreadable, or non-map artifact should receive a low score.
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


def select_rows(rows: list[dict[str, str]], limit: int | None) -> list[dict[str, str]]:
    candidates = []
    for row in rows:
        if row.get("qa_pass") != "True":
            continue
        image_path = review_image_path(row)
        if not image_path or not image_path.exists() or image_path.stat().st_size == 0:
            continue
        candidates.append(row)

    priority = {
        "reference": 0,
        "repair_qwen2.5-coder_32b": 1,
        "validator_repair_reference": 2,
    }
    candidates.sort(key=lambda row: (priority.get(row["source_group"], 9), row["kind"], row["source"], row["artifact_path"]))

    if limit is None or limit >= len(candidates):
        return candidates

    selected: list[dict[str, str]] = []
    by_group: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in candidates:
        by_group[row["source_group"]].append(row)
    preferred = ["reference", "repair_qwen2.5-coder_32b", "validator_repair_reference"]
    quota = max(1, limit // max(1, len([g for g in preferred if g in by_group])))
    for group in preferred:
        selected.extend(by_group.get(group, [])[:quota])
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


def normalize_result(result: dict[str, object]) -> dict[str, str]:
    score = result.get("cartographic_quality_score", "")
    try:
        numeric_score = max(0.0, min(1.0, float(score)))
        score_text = f"{numeric_score:.3f}"
    except Exception:
        score_text = ""
    return {
        "vlm_cartographic_quality_score": score_text,
        "vlm_map_content_visible": str(result.get("map_content_visible", "")),
        "vlm_has_title": str(result.get("has_title", "")),
        "vlm_has_legend_or_colorbar": str(result.get("has_legend_or_colorbar", "")),
        "vlm_text_readable": str(result.get("text_readable", "")),
        "vlm_layout_not_occluded": str(result.get("layout_not_occluded", "")),
        "vlm_appears_choropleth": str(result.get("appears_choropleth", "")),
        "vlm_main_issue": str(result.get("main_issue", "")),
        "vlm_verdict": str(result.get("verdict", "")),
        "vlm_raw_response": str(result.get("_raw_response", "")),
    }


def summarize(rows: list[dict[str, str]], model: str) -> dict[str, object]:
    by_group: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_group[row["source_group"]].append(row)
    summary: dict[str, object] = {"model": model, "reviewed_artifacts": len(rows), "by_source_group": {}}
    for group, group_rows in sorted(by_group.items()):
        scores = [float(row["vlm_cartographic_quality_score"]) for row in group_rows if row.get("vlm_cartographic_quality_score")]
        verdicts = Counter(row.get("vlm_verdict", "") for row in group_rows)
        summary["by_source_group"][group] = {
            "reviewed_artifacts": len(group_rows),
            "mean_vlm_cartographic_quality_score": round(sum(scores) / len(scores), 3) if scores else 0,
            "verdict_counts": dict(verdicts),
            "title_count": sum(row.get("vlm_has_title") == "True" for row in group_rows),
            "legend_or_colorbar_count": sum(row.get("vlm_has_legend_or_colorbar") == "True" for row in group_rows),
            "readable_count": sum(row.get("vlm_text_readable") == "True" for row in group_rows),
            "appears_choropleth_count": sum(row.get("vlm_appears_choropleth") == "True" for row in group_rows),
        }
    return summary


def write_report(rows: list[dict[str, str]], summary: dict[str, object], path: Path) -> None:
    lines = [
        "# Choropleth VLM Cartographic Screenshot Review",
        "",
        f"- model: `{summary['model']}`",
        f"- reviewed artifacts: {summary['reviewed_artifacts']}",
        "- scope: VLM pilot over screenshot-level QA-pass artifacts; this is a visual sanity check, not human ground truth.",
        "",
        "## Summary",
        "",
        "| Source group | Reviewed | Mean VLM quality | Verdict counts | Title | Legend/colorbar | Readable | Choropleth |",
        "|---|---:|---:|---|---:|---:|---:|---:|",
    ]
    for group, item in summary["by_source_group"].items():
        lines.append(
            f"| {group} | {item['reviewed_artifacts']} | {item['mean_vlm_cartographic_quality_score']} | {item['verdict_counts']} | {item['title_count']} | {item['legend_or_colorbar_count']} | {item['readable_count']} | {item['appears_choropleth_count']} |"
        )
    lines += [
        "",
        "## Reviewed Artifacts",
        "",
        "| Source group | Kind | Score | Verdict | Main issue | Image |",
        "|---|---|---:|---|---|---|",
    ]
    for row in sorted(rows, key=lambda r: (r["source_group"], r["kind"], r["vlm_cartographic_quality_score"])):
        image_path = row.get("review_image_path", row.get("artifact_path", ""))
        lines.append(
            f"| {row['source_group']} | {row['kind']} | {row['vlm_cartographic_quality_score']} | {row['vlm_verdict']} | {row['vlm_main_issue'].replace('|', '/')} | `{image_path}` |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="granite3.2-vision:latest")
    parser.add_argument("--limit", type=int, default=18)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--num-predict", type=int, default=180)
    parser.add_argument("--sleep", type=float, default=0.0)
    args = parser.parse_args()

    model_slug = safe_model_slug(args.model)
    out_csv = OUT_DIR / f"choropleth_vlm_cartographic_review_{model_slug}.csv"
    out_json = OUT_DIR / f"choropleth_vlm_cartographic_review_summary_{model_slug}.json"
    out_md = OUT_DIR / f"choropleth_vlm_cartographic_review_{model_slug}.md"

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
            merged = {
                **row,
                "review_image_path": rel_image,
                **normalize_result(result),
            }
            print(
                f"reviewed: {row['source_group']} {row['kind']} score={merged['vlm_cartographic_quality_score']} verdict={merged['vlm_verdict']}",
                flush=True,
            )
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
                "vlm_appears_choropleth": "",
                "vlm_main_issue": f"{type(exc).__name__}: {exc}",
                "vlm_verdict": "error",
                "vlm_raw_response": "",
            }
            print(f"error: {rel_image} {type(exc).__name__}: {exc}", flush=True)
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
