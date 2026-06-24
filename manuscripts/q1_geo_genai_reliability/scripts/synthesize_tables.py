#!/usr/bin/env python3
"""Synthesize manuscript-ready tables from experiment outputs."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from collections import defaultdict
from statistics import mean


ROOT = Path(__file__).resolve().parents[3]
MS_DIR = ROOT / "manuscripts/q1_geo_genai_reliability"
TABLE_DIR = MS_DIR / "tables"


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


def markdown_table(rows: list[dict[str, str]], columns: list[str]) -> str:
    out = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows:
        out.append("| " + " | ".join(str(row.get(col, "")).replace("|", "\\|") for col in columns) + " |")
    return "\n".join(out)


def dataset_inventory_table() -> tuple[list[dict[str, str]], str]:
    rows = read_csv(ROOT / "experiments/00_dataset_reproducibility_audit/outputs/dataset_inventory.csv")
    slim = []
    for row in rows:
        slim.append(
            {
                "Dataset": row["dataset"],
                "Artifact type": row["artifact_type"],
                "Size": row["size_human"],
                "Files": row["file_count"],
                "Code": row["code_available"],
                "Local path": row["local_path"],
            }
        )
    return slim, markdown_table(slim, ["Dataset", "Artifact type", "Size", "Files", "Code", "Local path"])


def reproducibility_table() -> tuple[list[dict[str, str]], str]:
    rows = read_csv(ROOT / "experiments/00_dataset_reproducibility_audit/outputs/reproducibility_matrix.csv")
    slim = []
    for row in rows:
        slim.append(
            {
                "Dataset": row["dataset"],
                "Data": row["data_available"],
                "Code": row["code_available"],
                "Reproducible": row["evaluation_reproducible_now"],
                "Main blocker": row["main_blocker"],
            }
        )
    return slim, markdown_table(slim, ["Dataset", "Data", "Code", "Reproducible", "Main blocker"])


def mapgenerator_table() -> tuple[list[dict[str, str]], str]:
    summary = json.loads((ROOT / "experiments/02_mapgenerator_image_text_audit/outputs/mapgenerator_audit_summary.json").read_text())
    rows = []
    for split, item in summary.items():
        rows.append(
            {
                "Split": split,
                "Pairs": str(item["pairs"]),
                "Missing images": str(item["missing_images"]),
                "Image size": ", ".join(item["image_dimensions"].keys()),
                "Avg words": str(item["avg_word_count"]),
                "No relation": str(item["quality_flags"].get("no_direction_or_relation", 0)),
                "Generic no-feature": str(item["quality_flags"].get("generic_no_feature_claim", 0)),
                "No named feature": str(item["quality_flags"].get("no_named_feature", 0)),
            }
        )
    return rows, markdown_table(rows, ["Split", "Pairs", "Missing images", "Image size", "Avg words", "No relation", "Generic no-feature", "No named feature"])


def scgm_table() -> tuple[list[dict[str, str]], str]:
    summary = json.loads((ROOT / "experiments/03_scgm_subset_reproduction/outputs/scgm_split_summary.json").read_text())
    rows = []
    for item in summary:
        rows.append(
            {
                "Split": item["split"],
                "RS": str(item["rs_256"]),
                "Map": str(item["map_256"]),
                "Matched": str(item["rs_map_intersection"]),
                "Ref 2x": str(item["ref_scale_2_256"]),
                "Ref 4x": str(item["ref_scale_4_256"]),
                "Zooms": json.dumps(item["zoom_distribution_rs"], sort_keys=True),
            }
        )
    return rows, markdown_table(rows, ["Split", "RS", "Map", "Matched", "Ref 2x", "Ref 4x", "Zooms"])


def edge_table() -> tuple[list[dict[str, str]], str]:
    summary = json.loads((ROOT / "experiments/03_scgm_subset_reproduction/outputs/scgm_edge_continuity_summary.json").read_text())
    rows = []
    for group, item in sorted(summary.items()):
        rows.append(
            {
                "Group": group,
                "Pairs": str(item["pairs"]),
                "Mean": str(item["mean_absdiff_rgb"]),
                "Median": str(item["median_absdiff_rgb"]),
                "P90": str(item["p90_absdiff_rgb"]),
                "Max": str(item["max_absdiff_rgb"]),
            }
        )
    return rows, markdown_table(rows, ["Group", "Pairs", "Mean", "Median", "P90", "Max"])


def scgm_retrieval_baseline_table() -> tuple[list[dict[str, str]], str]:
    summary = json.loads((ROOT / "experiments/03_scgm_subset_reproduction/outputs/scgm_retrieval_baseline_summary.json").read_text())
    rows = [
        {
            "Metric": "train candidates",
            "Mean": str(summary["train_candidates"]),
            "Median": "",
            "P10": "",
            "P90": "",
            "Note": f"exact tile candidates excluded={summary['exact_tile_candidates_excluded']}",
        },
        {
            "Metric": "validation outputs",
            "Mean": str(summary["validation_outputs"]),
            "Median": "",
            "P10": "",
            "P90": "",
            "Note": f"same-zoom retrievals={summary['same_zoom_retrievals']}",
        },
    ]
    for key, label in [
        ("mae_rgb", "MAE RGB"),
        ("psnr_rgb", "PSNR RGB"),
        ("global_ssim_luma", "Global SSIM luma"),
        ("generated_edge_continuity", "Generated edge continuity"),
    ]:
        item = summary[key]
        rows.append(
            {
                "Metric": label,
                "Mean": str(item.get("mean", "")),
                "Median": str(item.get("median", "")),
                "P10": str(item.get("p10", "")),
                "P90": str(item.get("p90", "")),
                "Note": "retrieval baseline",
            }
        )
    return rows, markdown_table(rows, ["Metric", "Mean", "Median", "P10", "P90", "Note"])


def scgm_retrieval_comparison_table() -> tuple[list[dict[str, str]], str]:
    baselines = [
        ("color-stat retrieval", ROOT / "experiments/03_scgm_subset_reproduction/outputs/scgm_retrieval_baseline_summary.json"),
        ("multi-feature retrieval", ROOT / "experiments/03_scgm_subset_reproduction/outputs/scgm_multifeature_retrieval_summary.json"),
        ("learned forest", ROOT / "experiments/03_scgm_subset_reproduction/outputs/scgm_learned_forest_summary.json"),
        ("neural MLP", ROOT / "experiments/03_scgm_subset_reproduction/outputs/scgm_mlp_summary.json"),
        ("local-context ridge", ROOT / "experiments/03_scgm_subset_reproduction/outputs/scgm_local_context_ridge_summary.json"),
        ("convolutional filter-bank ridge", ROOT / "experiments/03_scgm_subset_reproduction/outputs/scgm_convolutional_filter_ridge_summary.json"),
        ("patch-embedding retrieval", ROOT / "experiments/03_scgm_subset_reproduction/outputs/scgm_patch_embedding_retrieval_summary.json"),
        ("trained tiny CNN", ROOT / "experiments/03_scgm_subset_reproduction/outputs/scgm_tiny_cnn_summary.json"),
    ]
    rows = []
    for name, path in baselines:
        summary = json.loads(path.read_text(encoding="utf-8"))
        rows.append(
            {
                "Baseline": name,
                "Validation outputs": str(summary["validation_outputs"]),
                "Leakage guard": str(
                    summary.get(
                        "exact_tile_candidates_excluded",
                        summary.get("train_val_tile_overlap_excluded", ""),
                    )
                ),
                "MAE RGB mean": str(summary["mae_rgb"]["mean"]),
                "PSNR mean": str(summary["psnr_rgb"]["mean"]),
                "SSIM luma mean": str(summary["global_ssim_luma"]["mean"]),
                "Edge continuity mean": str(summary["generated_edge_continuity"]["mean"]),
            }
        )
    return rows, markdown_table(rows, ["Baseline", "Validation outputs", "Leakage guard", "MAE RGB mean", "PSNR mean", "SSIM luma mean", "Edge continuity mean"])


def scgm_mosaic_neighbor_stress_table() -> tuple[list[dict[str, str]], str]:
    summary = json.loads((ROOT / "experiments/03_scgm_subset_reproduction/outputs/scgm_mosaic_neighbor_stress_summary.json").read_text(encoding="utf-8"))
    rows = []
    for item in summary:
        generated = item["generated_seam_absdiff"]
        target = item["target_seam_absdiff"]
        ratio = item["stress_ratio"]
        rows.append(
            {
                "Baseline": item["baseline"],
                "Neighbor pairs": str(item["neighbor_pairs_available"]),
                "Missing pairs": str(item["neighbor_pairs_missing"]),
                "Generated seam mean": str(generated["mean"]),
                "Target seam mean": str(target["mean"]),
                "Stress ratio mean": str(ratio["mean"]),
                "Stress ratio p90": str(ratio["p90"]),
                "Interpretation": "seam score; lower can also indicate over-smoothing",
            }
        )
    return rows, markdown_table(rows, ["Baseline", "Neighbor pairs", "Missing pairs", "Generated seam mean", "Target seam mean", "Stress ratio mean", "Stress ratio p90", "Interpretation"])


def mapgenerator_embedding_scoring_table() -> tuple[list[dict[str, str]], str]:
    scores_path = ROOT / "experiments/02_mapgenerator_image_text_audit/outputs/mapgenerator_clip_caption_embedding_scores.csv"
    summary_path = ROOT / "experiments/02_mapgenerator_image_text_audit/outputs/mapgenerator_clip_caption_embedding_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    score_rows = read_csv(scores_path)
    rows: list[dict[str, str]] = [
        {
            "Group": "overall",
            "Items": str(summary.get("scored_pairs", 0)),
            "Mean CLIP score": str(summary.get("mean_embedding_score", "")),
            "Min CLIP score": str(summary.get("min_embedding_score", "")),
            "Max CLIP score": str(summary.get("max_embedding_score", "")),
            "Proxy-score Pearson r": "",
            "Note": f"model={summary.get('model', '')}; errors={summary.get('errors', '')}",
        }
    ]

    by_group: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in score_rows:
        by_group[("split", row["split"])].append(row)
        by_group[("proxy severity", row["review_severity"])].append(row)

    for (group_type, group_name), items in sorted(by_group.items()):
        clip_scores = [float(row["embedding_score"]) for row in items]
        proxy_scores = [float(row["proxy_fidelity_score"]) for row in items]
        clip_mean = mean(clip_scores)
        proxy_mean = mean(proxy_scores)
        numerator = sum((c - clip_mean) * (p - proxy_mean) for c, p in zip(clip_scores, proxy_scores))
        denominator = math.sqrt(
            sum((c - clip_mean) ** 2 for c in clip_scores)
            * sum((p - proxy_mean) ** 2 for p in proxy_scores)
        )
        pearson = numerator / denominator if denominator else 0.0
        rows.append(
            {
                "Group": f"{group_type}: {group_name}",
                "Items": str(len(items)),
                "Mean CLIP score": f"{clip_mean:.6f}",
                "Min CLIP score": f"{min(clip_scores):.6f}",
                "Max CLIP score": f"{max(clip_scores):.6f}",
                "Proxy-score Pearson r": f"{pearson:.6f}" if len(items) > 1 else "",
                "Note": "CLIP is a screening metric, not human ground truth",
            }
        )
    return rows, markdown_table(rows, ["Group", "Items", "Mean CLIP score", "Min CLIP score", "Max CLIP score", "Proxy-score Pearson r", "Note"])


def choropleth_table() -> tuple[list[dict[str, str]], str]:
    lint = json.loads((ROOT / "experiments/01_choropleth_llm_linter/outputs/lint_report.json").read_text())
    artifact = json.loads((ROOT / "experiments/01_choropleth_llm_linter/outputs/released_map_artifact_audit_summary.json").read_text())
    rows = [
        {
            "Component": "Input geodata lint",
            "Items": "",
            "Errors": str(lint["error_count"]),
            "Warnings": str(lint["warning_count"]),
            "Finding": "; ".join(f"{f['check']}: {f['message']}" for f in lint["findings"]),
        },
        {
            "Component": "Released map artifacts",
            "Items": str(artifact["total_artifacts"]),
            "Errors": "0",
            "Warnings": "0",
            "Finding": f"{artifact['artifact_type']}; QA flags={artifact['qa_flags']}",
        },
    ]
    return rows, markdown_table(rows, ["Component", "Items", "Errors", "Warnings", "Finding"])


def candidate_table() -> tuple[list[dict[str, str]], str]:
    rows = read_csv(ROOT / "experiments/01_choropleth_llm_linter/outputs/candidate_scores.csv")
    slim = []
    for row in rows:
        slim.append(
            {
                "Prompt": row["prompt_id"],
                "Candidate": row["candidate"],
                "Score": row["score"],
                "Passed": f"{row['passed']}/{row['required']}",
                "Failed checks": row["failed_checks"],
            }
        )
    return slim, markdown_table(slim, ["Prompt", "Candidate", "Score", "Passed", "Failed checks"])


def claims_table() -> tuple[list[dict[str, str]], str]:
    rows = read_csv(TABLE_DIR / "table_08_claims_vs_artifacts.csv")
    slim = []
    for row in rows:
        slim.append(
            {
                "Paper": row["paper"],
                "Paradigm": row["paradigm"],
                "Scale": row["claimed_or_reported_scale"],
                "Local data": row["local_data_available"],
                "Local code": row["local_code_available"],
                "Status": row["reproducibility_status"],
            }
        )
    return slim, markdown_table(slim, ["Paper", "Paradigm", "Scale", "Local data", "Local code", "Status"])


def mapgenerator_proxy_review_table() -> tuple[list[dict[str, str]], str]:
    summary = json.loads((ROOT / "experiments/02_mapgenerator_image_text_audit/outputs/mapgenerator_proxy_caption_review_summary.json").read_text())
    rows = []
    for split, item in summary.items():
        severity = item["severity_counts"]
        top_issues = item["top_proxy_issues"]
        rows.append(
            {
                "Split": split,
                "Reviewed": str(item["reviewed_pairs"]),
                "Mean proxy score": str(item["mean_proxy_fidelity_score"]),
                "Low": str(severity.get("low", 0)),
                "Medium": str(severity.get("medium", 0)),
                "High": str(severity.get("high", 0)),
                "Top issues": "; ".join(f"{name}={count}" for name, count in list(top_issues.items())[:3]),
            }
        )
    return rows, markdown_table(rows, ["Split", "Reviewed", "Mean proxy score", "Low", "Medium", "High", "Top issues"])


def mapgenerator_vlm_review_table() -> tuple[list[dict[str, str]], str]:
    summary_paths = sorted(
        (ROOT / "experiments/02_mapgenerator_image_text_audit/outputs").glob("mapgenerator_vlm_caption_review_summary_*.json")
    )
    if not summary_paths:
        return [], ""
    rows = []
    for summary_path in summary_paths:
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        for split, item in summary["by_split"].items():
            verdict_counts = item["verdict_counts"]
            rows.append(
                {
                    "Model": summary["model"],
                    "Split": split,
                    "Reviewed": str(item["reviewed_pairs"]),
                    "Mean VLM score": str(item["mean_vlm_alignment_score"]),
                    "Mean proxy score": str(item["mean_proxy_fidelity_score"]),
                    "Verdicts": "; ".join(f"{name}={count}" for name, count in verdict_counts.items()),
                    "Errors": str(verdict_counts.get("error", 0)),
                    "Unsupported rows": str(item["unsupported_claim_rows"]),
                    "Omission rows": str(item["omission_rows"]),
                }
            )
    rows.sort(key=lambda row: (row["Model"], row["Split"]))
    return rows, markdown_table(rows, ["Model", "Split", "Reviewed", "Mean VLM score", "Mean proxy score", "Verdicts", "Errors", "Unsupported rows", "Omission rows"])


def _pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 2 or len(xs) != len(ys):
        return None
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    den_x = sum((x - mean_x) ** 2 for x in xs)
    den_y = sum((y - mean_y) ** 2 for y in ys)
    if den_x == 0 or den_y == 0:
        return None
    return num / ((den_x * den_y) ** 0.5)


def _fmt_float(value: float | None, digits: int = 3) -> str:
    return "" if value is None else f"{value:.{digits}f}"


def mapgenerator_vlm_agreement_table() -> tuple[list[dict[str, str]], str]:
    out_dir = ROOT / "experiments/02_mapgenerator_image_text_audit/outputs"
    granite_path = out_dir / "mapgenerator_vlm_caption_review_granite3.2-vision_latest.csv"
    qwen_path = out_dir / "mapgenerator_vlm_caption_review_qwen2.5vl_3b.csv"
    if not granite_path.exists() or not qwen_path.exists():
        return [], ""

    granite = {(row["split"], row["image"]): row for row in read_csv(granite_path) if row.get("vlm_verdict") != "error"}
    qwen = {(row["split"], row["image"]): row for row in read_csv(qwen_path) if row.get("vlm_verdict") != "error"}
    paired_keys = sorted(set(granite) & set(qwen))

    groups: dict[str, list[tuple[dict[str, str], dict[str, str]]]] = defaultdict(list)
    for key in paired_keys:
        groups["overall"].append((granite[key], qwen[key]))
        groups[key[0]].append((granite[key], qwen[key]))

    rows = []
    for group_name in ["overall", *sorted(name for name in groups if name != "overall")]:
        pairs = groups[group_name]
        if not pairs:
            continue
        score_g = [float(g["vlm_alignment_score"]) for g, _ in pairs if g.get("vlm_alignment_score")]
        score_q = [float(q["vlm_alignment_score"]) for _, q in pairs if q.get("vlm_alignment_score")]
        exact = sum(g["vlm_verdict"] == q["vlm_verdict"] for g, q in pairs)
        binary = sum((g["vlm_verdict"] == "supported") == (q["vlm_verdict"] == "supported") for g, q in pairs)
        qwen_more_critical = sum(float(q["vlm_alignment_score"]) < float(g["vlm_alignment_score"]) for g, q in pairs)
        both_supported = sum(g["vlm_verdict"] == "supported" and q["vlm_verdict"] == "supported" for g, q in pairs)
        feature_fields = ["vlm_visible_water", "vlm_visible_roads", "vlm_visible_green_area", "vlm_visible_named_label"]
        feature_checks = 0
        feature_agree = 0
        for g, q in pairs:
            for field in feature_fields:
                if g.get(field) in {"True", "False"} and q.get(field) in {"True", "False"}:
                    feature_checks += 1
                    feature_agree += g[field] == q[field]
        rows.append(
            {
                "Scope": group_name,
                "Paired items": str(len(pairs)),
                "Exact verdict agreement": f"{exact}/{len(pairs)}",
                "Supported/below agreement": f"{binary}/{len(pairs)}",
                "Both supported": str(both_supported),
                "Mean score Granite": _fmt_float(sum(score_g) / len(score_g) if score_g else None),
                "Mean score Qwen": _fmt_float(sum(score_q) / len(score_q) if score_q else None),
                "Score Pearson r": _fmt_float(_pearson(score_g, score_q)),
                "Qwen lower score": f"{qwen_more_critical}/{len(pairs)}",
                "Feature agreement": f"{feature_agree}/{feature_checks}",
            }
        )
    return rows, markdown_table(rows, ["Scope", "Paired items", "Exact verdict agreement", "Supported/below agreement", "Both supported", "Mean score Granite", "Mean score Qwen", "Score Pearson r", "Qwen lower score", "Feature agreement"])


def taxonomy_table() -> tuple[list[dict[str, str]], str]:
    rows = read_csv(TABLE_DIR / "table_11_cross_paradigm_metric_taxonomy.csv")
    slim = []
    for row in rows:
        slim.append(
            {
                "Paradigm": row["paradigm"],
                "Artifact": row["generated_artifact"],
                "Failure modes": row["dominant_failure_modes"],
                "Evaluation": row["best_evaluation_methods"],
                "Repairability": row["repairability"],
            }
        )
    return slim, markdown_table(slim, ["Paradigm", "Artifact", "Failure modes", "Evaluation", "Repairability"])


def expanded_choropleth_summary_table() -> tuple[list[dict[str, str]], str]:
    path = ROOT / "experiments/05_choropleth_reliability_benchmark/outputs/scores/expanded_choropleth_condition_summary.csv"
    rows = read_csv(path)
    slim = []
    for row in rows:
        slim.append(
            {
                "Model": row["model"],
                "Mode": row["mode"],
                "Prompt": row["prompt_id"],
                "Condition": row["condition"],
                "Attempts": row["attempts"],
                "Best score": row["best_score"],
                "Best passed": f"{row['best_passed']}/{row['best_required']}",
                "Execution": row["execution_success_any"],
            }
        )
    return slim, markdown_table(slim, ["Model", "Mode", "Prompt", "Condition", "Attempts", "Best score", "Best passed", "Execution"])


def reference_choropleth_table() -> tuple[list[dict[str, str]], str]:
    diagnostics_path = ROOT / "experiments/05_choropleth_reliability_benchmark/outputs/reference_baseline/diagnostics.json"
    diagnostics = json.loads(diagnostics_path.read_text(encoding="utf-8"))
    outputs = diagnostics["outputs"]
    rows = [
        {
            "Artifact": "static choropleth PNG",
            "File": "map_static.png",
            "Exists": str(outputs["map_static.png"]["exists"]),
            "Bytes": str(outputs["map_static.png"]["bytes"]),
            "Validation note": f"mainland CRS {diagnostics['mainland_crs_before']} -> {diagnostics['mainland_crs_after']}",
        },
        {
            "Artifact": "interactive Folium HTML",
            "File": "map_interactive.html",
            "Exists": str(outputs["map_interactive.html"]["exists"]),
            "Bytes": str(outputs["map_interactive.html"]["bytes"]),
            "Validation note": f"{diagnostics['mainland_rows_after_geometry_filter']} district features with tooltips",
        },
        {
            "Artifact": "annual time-series PNG",
            "File": "time_series.png",
            "Exists": str(outputs["time_series.png"]["exists"]),
            "Bytes": str(outputs["time_series.png"]["bytes"]),
            "Validation note": f"{diagnostics['year_min']}-{diagnostics['year_max']}; max burned area year {diagnostics['max_burned_area_year']}",
        },
        {
            "Artifact": "diagnostic JSON",
            "File": "diagnostics.json",
            "Exists": str(outputs["diagnostics.json"]["exists"]),
            "Bytes": str(outputs["diagnostics.json"]["bytes"]),
            "Validation note": f"boundary invalid geometries {diagnostics['boundary_invalid_before']} -> {diagnostics['boundary_invalid_after']}",
        },
    ]
    return rows, markdown_table(rows, ["Artifact", "File", "Exists", "Bytes", "Validation note"])


def choropleth_model_summary_table() -> tuple[list[dict[str, str]], str]:
    condition_rows = [
        row
        for row in read_csv(ROOT / "experiments/05_choropleth_reliability_benchmark/outputs/scores/expanded_choropleth_condition_summary.csv")
        if row["condition"] == "initial"
    ]
    safety_counts: dict[tuple[str, str], dict[str, int]] = defaultdict(lambda: {"generated": 0, "safe": 0, "unsafe": 0})
    for scan_path in sorted((ROOT / "experiments/05_choropleth_reliability_benchmark/outputs/scores").glob("generated_code_safety_scan_*.csv")):
        for row in read_csv(scan_path):
            path = Path(row["script"])
            model = path.parts[-3]
            mode = path.parts[-2]
            key = (model, mode)
            safety_counts[key]["generated"] += 1
            if row["safe_to_run"] == "True":
                safety_counts[key]["safe"] += 1
            else:
                safety_counts[key]["unsafe"] += 1

    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in condition_rows:
        grouped[(row["model"], row["mode"])].append(row)

    out = []
    for key in sorted(safety_counts):
        model, mode = key
        group = grouped.get(key, [])
        scores = [float(row["best_score"]) for row in group]
        executed = sum(row["execution_success_any"] == "True" for row in group)
        complete = sum(float(row["best_score"]) >= 0.999 and row["execution_success_any"] == "True" for row in group)
        out.append(
            {
                "Model": model,
                "Mode": mode,
                "Generated": str(safety_counts[key]["generated"]),
                "Safe": str(safety_counts[key]["safe"]),
                "Unsafe": str(safety_counts[key]["unsafe"]),
                "Executed": str(executed),
                "Complete": str(complete),
                "Mean score": f"{sum(scores) / len(scores):.3f}" if scores else "0.000",
                "Max score": f"{max(scores):.3f}" if scores else "0.000",
            }
        )
    return out, markdown_table(out, ["Model", "Mode", "Generated", "Safe", "Unsafe", "Executed", "Complete", "Mean score", "Max score"])


def rendered_artifact_qa_table() -> tuple[list[dict[str, str]], str]:
    rows = read_csv(ROOT / "experiments/05_choropleth_reliability_benchmark/outputs/scores/rendered_artifact_qa_detail.csv")
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        if row["source"] == "reference":
            key = "reference"
        else:
            key = row["source"].split(":", 1)[0]
        grouped[key].append(row)

    out = []
    for source, group in sorted(grouped.items()):
        out.append(
            {
                "Source": source,
                "Checked artifacts": str(len(group)),
                "Existing": str(sum(row.get("exists") == "True" for row in group)),
                "Nonblank images": str(sum(row.get("kind") == "image" and row.get("nonblank") == "True" for row in group)),
                "Valid HTML": str(sum(row.get("kind") == "html" and row.get("has_leaflet") == "True" and row.get("has_geojson") == "True" for row in group)),
                "Valid JSON": str(sum(row.get("kind") == "json" and row.get("valid_json") == "True" for row in group)),
            }
        )
    return out, markdown_table(out, ["Source", "Checked artifacts", "Existing", "Nonblank images", "Valid HTML", "Valid JSON"])


def screenshot_level_qa_table() -> tuple[list[dict[str, str]], str]:
    rows = read_csv(ROOT / "experiments/05_choropleth_reliability_benchmark/outputs/scores/screenshot_level_qa_summary.csv")
    out = []
    for row in rows:
        out.append(
            {
                "Source": row["source_group"],
                "Artifact kind": row["kind"],
                "Checked": row["checked"],
                "Existing": row["existing"],
                "HTML rendered": row["html_rendered"],
                "Screenshot QA pass": row["screenshot_qa_pass"],
                "Pass rate existing": row["pass_rate_existing"],
            }
        )
    return out, markdown_table(out, ["Source", "Artifact kind", "Checked", "Existing", "HTML rendered", "Screenshot QA pass", "Pass rate existing"])


def choropleth_vlm_cartographic_review_table() -> tuple[list[dict[str, str]], str]:
    summary_paths = sorted(
        (ROOT / "experiments/05_choropleth_reliability_benchmark/outputs/scores").glob("choropleth_vlm_cartographic_review_summary_*.json")
    )
    if not summary_paths:
        return [], ""
    rows = []
    for summary_path in summary_paths:
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        for source_group, item in summary["by_source_group"].items():
            rows.append(
                {
                    "Model": summary["model"],
                    "Source": source_group,
                    "Reviewed": str(item["reviewed_artifacts"]),
                    "Mean VLM quality": str(item["mean_vlm_cartographic_quality_score"]),
                    "Verdicts": "; ".join(f"{name}={count}" for name, count in item["verdict_counts"].items()),
                    "Title": str(item["title_count"]),
                    "Legend/colorbar": str(item["legend_or_colorbar_count"]),
                    "Readable": str(item["readable_count"]),
                    "Choropleth": str(item["appears_choropleth_count"]),
                }
            )
    rows.sort(key=lambda row: (row["Model"], row["Source"]))
    return rows, markdown_table(rows, ["Model", "Source", "Reviewed", "Mean VLM quality", "Verdicts", "Title", "Legend/colorbar", "Readable", "Choropleth"])


def choropleth_vlm_agreement_table() -> tuple[list[dict[str, str]], str]:
    out_dir = ROOT / "experiments/05_choropleth_reliability_benchmark/outputs/scores"
    granite_path = out_dir / "choropleth_vlm_cartographic_review_granite3.2-vision_latest.csv"
    qwen_path = out_dir / "choropleth_vlm_cartographic_review_qwen2.5vl_3b.csv"
    if not granite_path.exists() or not qwen_path.exists():
        return [], ""

    key_fields = ["source_group", "source", "kind", "artifact_path"]
    granite = {tuple(row[field] for field in key_fields): row for row in read_csv(granite_path)}
    qwen = {tuple(row[field] for field in key_fields): row for row in read_csv(qwen_path)}
    paired_keys = sorted(set(granite) & set(qwen))

    groups: dict[str, list[tuple[dict[str, str], dict[str, str]]]] = defaultdict(list)
    for key in paired_keys:
        g = granite[key]
        q = qwen[key]
        groups["overall"].append((g, q))
        groups[g["source_group"]].append((g, q))

    usable_verdicts = {"publication_ready", "usable_with_minor_issues"}
    rows = []
    for group_name in ["overall", *sorted(name for name in groups if name != "overall")]:
        pairs = groups[group_name]
        if not pairs:
            continue
        score_g = [float(g["vlm_cartographic_quality_score"]) for g, _ in pairs if g.get("vlm_cartographic_quality_score")]
        score_q = [float(q["vlm_cartographic_quality_score"]) for _, q in pairs if q.get("vlm_cartographic_quality_score")]
        exact = sum(g["vlm_verdict"] == q["vlm_verdict"] for g, q in pairs)
        usable_binary = sum((g["vlm_verdict"] in usable_verdicts) == (q["vlm_verdict"] in usable_verdicts) for g, q in pairs)
        qwen_more_critical = sum(float(q["vlm_cartographic_quality_score"]) < float(g["vlm_cartographic_quality_score"]) for g, q in pairs)
        both_usable = sum(g["vlm_verdict"] in usable_verdicts and q["vlm_verdict"] in usable_verdicts for g, q in pairs)
        component_fields = [
            "vlm_map_content_visible",
            "vlm_has_title",
            "vlm_has_legend_or_colorbar",
            "vlm_text_readable",
            "vlm_layout_not_occluded",
            "vlm_appears_choropleth",
        ]
        component_checks = 0
        component_agree = 0
        for g, q in pairs:
            for field in component_fields:
                if g.get(field) in {"True", "False"} and q.get(field) in {"True", "False"}:
                    component_checks += 1
                    component_agree += g[field] == q[field]
        rows.append(
            {
                "Scope": group_name,
                "Paired artifacts": str(len(pairs)),
                "Exact verdict agreement": f"{exact}/{len(pairs)}",
                "Usable/below agreement": f"{usable_binary}/{len(pairs)}",
                "Both usable": str(both_usable),
                "Mean score Granite": _fmt_float(sum(score_g) / len(score_g) if score_g else None),
                "Mean score Qwen": _fmt_float(sum(score_q) / len(score_q) if score_q else None),
                "Score Pearson r": _fmt_float(_pearson(score_g, score_q)),
                "Qwen lower score": f"{qwen_more_critical}/{len(pairs)}",
                "Component agreement": f"{component_agree}/{component_checks}",
            }
        )
    return rows, markdown_table(rows, ["Scope", "Paired artifacts", "Exact verdict agreement", "Usable/below agreement", "Both usable", "Mean score Granite", "Mean score Qwen", "Score Pearson r", "Qwen lower score", "Component agreement"])


def iterative_validator_repair_table() -> tuple[list[dict[str, str]], str]:
    path = ROOT / "experiments/05_choropleth_reliability_benchmark/outputs/scores/iterative_validator_repair_qwen2.5-coder_32b.csv"
    if not path.exists():
        return [], ""
    rows = read_csv(path)
    final: dict[tuple[str, str, str], dict[str, str]] = {}
    for row in rows:
        key = (row["source_model"], row["mode"], row["prompt_id"])
        current = final.get(key)
        if current is None or int(row["iteration"]) > int(current["iteration"]):
            final[key] = row
    out = []
    for row in sorted(final.values(), key=lambda r: (r["source_model"], r["mode"], r["prompt_id"])):
        out.append(
            {
                "Source model": row["source_model"],
                "Mode": row["mode"],
                "Prompt": row["prompt_id"],
                "One-pass score": row["one_pass_score"],
                "Final iteration": row["iteration"],
                "Final score": row["score"],
                "Passed": f"{row['passed']}/{row['required']}",
                "Complete": row["complete"],
                "Failed checks": row["failed_checks"],
            }
        )
    return out, markdown_table(out, ["Source model", "Mode", "Prompt", "One-pass score", "Final iteration", "Final score", "Passed", "Complete", "Failed checks"])


def repair_model_comparison_table() -> tuple[list[dict[str, str]], str]:
    configs = [
        {
            "label": "qwen2.5-coder:32b",
            "scope": "full incomplete one-pass set",
            "max_iters": "3",
            "summary": ROOT / "experiments/05_choropleth_reliability_benchmark/outputs/scores/iterative_validator_repair_summary_qwen2.5-coder_32b.json",
            "csv": ROOT / "experiments/05_choropleth_reliability_benchmark/outputs/scores/iterative_validator_repair_qwen2.5-coder_32b.csv",
        },
        {
            "label": "qwen2.5-coder:14b",
            "scope": "near-miss pilot subset",
            "max_iters": "2",
            "summary": ROOT / "experiments/05_choropleth_reliability_benchmark/outputs/scores/iterative_validator_repair_summary_qwen2.5-coder_14b.json",
            "csv": ROOT / "experiments/05_choropleth_reliability_benchmark/outputs/scores/iterative_validator_repair_qwen2.5-coder_14b.csv",
        },
        {
            "label": "qwen2.5-coder:7b",
            "scope": "near-miss pilot subset",
            "max_iters": "2",
            "summary": ROOT / "experiments/05_choropleth_reliability_benchmark/outputs/scores/iterative_validator_repair_summary_qwen2.5-coder_7b.json",
            "csv": ROOT / "experiments/05_choropleth_reliability_benchmark/outputs/scores/iterative_validator_repair_qwen2.5-coder_7b.csv",
        },
        {
            "label": "deepseek-coder:6.7b",
            "scope": "near-miss pilot subset",
            "max_iters": "2",
            "summary": ROOT / "experiments/05_choropleth_reliability_benchmark/outputs/scores/iterative_validator_repair_summary_deepseek-coder_6.7b.json",
            "csv": ROOT / "experiments/05_choropleth_reliability_benchmark/outputs/scores/iterative_validator_repair_deepseek-coder_6.7b.csv",
        },
    ]
    out = []
    for cfg in configs:
        if not cfg["summary"].exists() or not cfg["csv"].exists():
            continue
        summary = json.loads(cfg["summary"].read_text(encoding="utf-8"))
        rows = read_csv(cfg["csv"])
        final: dict[tuple[str, str, str], dict[str, str]] = {}
        for row in rows:
            key = (row["source_model"], row["mode"], row["prompt_id"])
            current = final.get(key)
            if current is None or int(row["iteration"]) > int(current["iteration"]):
                final[key] = row
        final_scores = [float(row["score"]) for row in final.values()]
        complete_by_iter = defaultdict(int)
        for row in final.values():
            if row["complete"] == "True":
                complete_by_iter[row["iteration"]] += 1
        out.append(
            {
                "Repair model": cfg["label"],
                "Scope": cfg["scope"],
                "Cases": str(summary["cases"]),
                "Max iters": cfg["max_iters"],
                "Attempt rows": str(summary["attempt_rows"]),
                "Safe attempts": str(summary["safe_attempts"]),
                "Completed": str(summary["completed_cases"]),
                "Completion rate": f"{summary['completed_cases']}/{summary['cases']}",
                "Mean final score": _fmt_float(sum(final_scores) / len(final_scores) if final_scores else None),
                "Completed by iter": "; ".join(f"iter {k}: {v}" for k, v in sorted(complete_by_iter.items())) or "none",
            }
        )
    return out, markdown_table(out, ["Repair model", "Scope", "Cases", "Max iters", "Attempt rows", "Safe attempts", "Completed", "Completion rate", "Mean final score", "Completed by iter"])


def matched_repair_model_suite_table() -> tuple[list[dict[str, str]], str]:
    path = MS_DIR / "submission/repair_model_suite/matched_repair_model_summary.csv"
    if not path.exists():
        return [], ""
    rows = read_csv(path)
    slim = []
    for row in rows:
        slim.append(
            {
                "Repair model": row["Repair model"],
                "Matched cases": row["Matched cases"],
                "Attempt rows": row["Attempt rows"],
                "Safe attempts": row["Safe attempts"],
                "Unsafe attempts": row["Unsafe attempts"],
                "Completed cases": row["Completed cases"],
                "Completion rate": row["Completion rate"],
                "Mean final score": row["Mean final score"],
                "Top remaining failed checks": row["Top remaining failed checks"],
            }
        )
    return slim, markdown_table(slim, ["Repair model", "Matched cases", "Attempt rows", "Safe attempts", "Unsafe attempts", "Completed cases", "Completion rate", "Mean final score", "Top remaining failed checks"])


def evaluator_adjudication_table() -> tuple[list[dict[str, str]], str]:
    rows = read_csv(MS_DIR / "submission/human_validation_panels/summaries/evaluator_adjudication_summary.csv")
    slim = []
    for row in rows:
        slim.append(
            {
                "Task": row["Task"],
                "Items": row["Items"],
                "Exact agreement": row["Exact VLM agreement"],
                "Coarse agreement": row["Coarse VLM agreement"],
                "Urgent human adjudication": row["Urgent human adjudication"],
                "High priority": row["High human priority"],
                "Stable/low priority": row["Low priority/stable"],
                "Mean score gap": row["Mean score gap"],
            }
        )
    return slim, markdown_table(slim, ["Task", "Items", "Exact agreement", "Coarse agreement", "Urgent human adjudication", "High priority", "Stable/low priority", "Mean score gap"])


def vlm_judge_robustness_table() -> tuple[list[dict[str, str]], str]:
    rows = read_csv(MS_DIR / "submission/evaluator_reliability/vlm_judge_robustness_audit.csv")
    slim = []
    for row in rows:
        slim.append(
            {
                "Task": row["Task"],
                "Model": row["Model"],
                "Reviewed": row["Reviewed"],
                "Usable": row["Usable reviews"],
                "Errors": row["Errors"],
                "Usable rate pct": row["Usable rate pct"],
                "Panel role": row["Panel role"],
            }
        )
    return slim, markdown_table(slim, ["Task", "Model", "Reviewed", "Usable", "Errors", "Usable rate pct", "Panel role"])


def cross_paradigm_reliability_summary_table() -> tuple[list[dict[str, str]], str]:
    rows = read_csv(MS_DIR / "submission/cross_paradigm/cross_paradigm_reliability_summary.csv")
    slim = []
    for row in rows:
        slim.append(
            {
                "Paradigm": row["Paradigm"],
                "Dimensions": row["Dimensions"],
                "Total score": row["Total score"],
                "Mean score": row["Mean score"],
                "Lowest score": row["Lowest score"],
                "Highest score": row["Highest score"],
            }
        )
    return slim, markdown_table(slim, ["Paradigm", "Dimensions", "Total score", "Mean score", "Lowest score", "Highest score"])


def literature_taxonomy_table() -> tuple[list[dict[str, str]], str]:
    rows = [
        {
            "Work": "Affolter et al. 2025",
            "Paradigm": "controlled diffusion map tiles",
            "Generated artifact": "raster map tile",
            "Control signal": "rasterized vector semantics + text style prompt",
            "Evaluation style": "visual inspection + cartographer user study",
            "Reliability gap": "topology, labels, tile seams, GIS integration",
        },
        {
            "Work": "Sun et al. 2025 SCGM",
            "Paradigm": "remote-sensing-to-map diffusion",
            "Generated artifact": "multi-scale map tile",
            "Control signal": "remote sensing image + scale encoding + cascade references",
            "Evaluation style": "quantitative image metrics + ablations",
            "Reliability gap": "natural landscapes, long-range continuity, missing public reproduction details",
        },
        {
            "Work": "Zhang et al. 2025 MapGenerator",
            "Paradigm": "text-to-map diffusion",
            "Generated artifact": "map-like raster image",
            "Control signal": "natural-language map caption",
            "Evaluation style": "text-map dataset and generation examples",
            "Reliability gap": "caption fidelity, spatial relations, dataset-count reproducibility",
        },
        {
            "Work": "Wang et al. 2025 CartoAgent",
            "Paradigm": "MLLM cartographic style agent",
            "Generated artifact": "stylesheet and styled map",
            "Control signal": "inspiration image + vector/style ecosystem",
            "Evaluation style": "expert/student human evaluation + MLLM reviewer",
            "Reliability gap": "formal constraints beyond style, reviewer calibration",
        },
        {
            "Work": "Song et al. 2025 VGI mapping agent",
            "Paradigm": "LLM GIS workflow agent",
            "Generated artifact": "thematic map workflow/output",
            "Control signal": "natural-language request + OSM/VGI tools",
            "Evaluation style": "qualitative case studies",
            "Reliability gap": "benchmarking, VGI quality, automated cartographic completeness",
        },
        {
            "Work": "Li & Ning et al. 2025",
            "Paradigm": "autonomous GIS agenda",
            "Generated artifact": "GIS workflows and result-aware agents",
            "Control signal": "LLM/tool orchestration + visual review",
            "Evaluation style": "agenda + proof-of-concept systems",
            "Reliability gap": "result-aware validation and explicit map-design rubrics",
        },
        {
            "Work": "Pannoon & Netek 2025",
            "Paradigm": "LLM-generated choropleth code",
            "Generated artifact": "static and interactive choropleth maps",
            "Control signal": "prompted ChatGPT-4 code generation",
            "Evaluation style": "case-study outputs",
            "Reliability gap": "execution logs, data linting, repair, artifact completeness",
        },
        {
            "Work": "Yang et al. 2025 MapColorAI",
            "Paradigm": "LLM map-design subtask",
            "Generated artifact": "choropleth color scheme",
            "Control signal": "theme/data semantics + color theory",
            "Evaluation style": "user study",
            "Reliability gap": "accessibility, cultural context, multimodal style grounding",
        },
        {
            "Work": "Shomer & Xu 2025 MAPLE",
            "Paradigm": "LLM map-label placement",
            "Generated artifact": "label coordinates",
            "Control signal": "guideline RAG + map context",
            "Evaluation style": "RMSE against benchmark labels",
            "Reliability gap": "rendered-layout reasoning, occlusion, scale/context generalization",
        },
        {
            "Work": "Kang & Wang 2026",
            "Paradigm": "GenAI cartography perspective",
            "Generated artifact": "research agenda",
            "Control signal": "cartographic workflow analysis",
            "Evaluation style": "conceptual synthesis",
            "Reliability gap": "operational benchmarks and ethical governance",
        },
    ]
    return rows, markdown_table(rows, ["Work", "Paradigm", "Generated artifact", "Control signal", "Evaluation style", "Reliability gap"])


def write_all_markdown(tables: list[tuple[str, str]]) -> None:
    lines = ["# Manuscript Tables", ""]
    for title, table in tables:
        lines.extend([f"## {title}", "", table, ""])
    (TABLE_DIR / "manuscript_tables.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    specs = [
        ("Table 1. Local Geo-GenAI artifact inventory", "table_01_dataset_inventory.csv", dataset_inventory_table),
        ("Table 2. Reproducibility matrix", "table_02_reproducibility_matrix.csv", reproducibility_table),
        ("Table 3. MapGenerator caption audit", "table_03_mapgenerator_caption_audit.csv", mapgenerator_table),
        ("Table 4. SCGM split and cascade-reference coverage", "table_04_scgm_coverage.csv", scgm_table),
        ("Table 5. SCGM validation edge-continuity baseline", "table_05_scgm_edge_continuity.csv", edge_table),
        ("Table 5b. SCGM lightweight retrieval generated-output baseline", "table_05b_scgm_retrieval_baseline.csv", scgm_retrieval_baseline_table),
        ("Table 5c. SCGM generated-output baseline comparison", "table_05c_scgm_retrieval_comparison.csv", scgm_retrieval_comparison_table),
        ("Table 5d. SCGM mosaic neighbor-seam stress audit", "table_05d_scgm_mosaic_neighbor_stress.csv", scgm_mosaic_neighbor_stress_table),
        ("Table 6. Choropleth data and artifact QA", "table_06_choropleth_qa.csv", choropleth_table),
        ("Table 7. Seed LLM choropleth candidate benchmark", "table_07_seed_choropleth_candidates.csv", candidate_table),
        ("Table 8. Literature claim vs local artifact availability", "table_08_claims_vs_artifacts_slim.csv", claims_table),
        ("Table 9. MapGenerator proxy caption-fidelity review", "table_09_mapgenerator_proxy_caption_review.csv", mapgenerator_proxy_review_table),
        ("Table 10. Expanded choropleth benchmark condition summary", "table_10_expanded_choropleth_condition_summary.csv", expanded_choropleth_summary_table),
        ("Table 11. Cross-paradigm metric taxonomy", "table_11_cross_paradigm_metric_taxonomy_slim.csv", taxonomy_table),
        ("Table 12. Deterministic choropleth reference baseline", "table_12_reference_choropleth_baseline.csv", reference_choropleth_table),
        ("Table 13. Choropleth benchmark model-mode aggregate", "table_13_choropleth_model_mode_summary.csv", choropleth_model_summary_table),
        ("Table 14. Rendered artifact QA summary", "table_14_rendered_artifact_qa_summary.csv", rendered_artifact_qa_table),
        ("Table 15. MapGenerator VLM caption-fidelity pilot", "table_15_mapgenerator_vlm_caption_review.csv", mapgenerator_vlm_review_table),
        ("Table 15b. MapGenerator two-VLM caption agreement pilot", "table_15b_mapgenerator_vlm_agreement.csv", mapgenerator_vlm_agreement_table),
        ("Table 15c. MapGenerator CLIP caption-embedding scoring", "table_15c_mapgenerator_clip_caption_embedding.csv", mapgenerator_embedding_scoring_table),
        ("Table 16. Screenshot-level choropleth artifact QA", "table_16_screenshot_level_choropleth_qa.csv", screenshot_level_qa_table),
        ("Table 17. Geo-GenAI map-generation literature taxonomy", "table_17_literature_taxonomy.csv", literature_taxonomy_table),
        ("Table 18. Choropleth VLM cartographic-quality pilot", "table_18_choropleth_vlm_cartographic_review.csv", choropleth_vlm_cartographic_review_table),
        ("Table 18b. Choropleth two-VLM cartographic-quality agreement pilot", "table_18b_choropleth_vlm_agreement.csv", choropleth_vlm_agreement_table),
        ("Table 19. Iterative validator-gated choropleth repair pilot", "table_19_iterative_validator_repair.csv", iterative_validator_repair_table),
        ("Table 20. Iterative repair model comparison", "table_20_iterative_repair_model_comparison.csv", repair_model_comparison_table),
        ("Table 21. Evaluator adjudication and human-priority queue", "table_21_evaluator_adjudication_summary.csv", evaluator_adjudication_table),
        ("Table 22. VLM judge robustness and schema-adherence audit", "table_22_vlm_judge_robustness.csv", vlm_judge_robustness_table),
        ("Table 23. Cross-paradigm reliability summary", "table_23_cross_paradigm_reliability_summary.csv", cross_paradigm_reliability_summary_table),
        ("Table 25. Matched repair-model suite", "table_25_matched_repair_model_suite.csv", matched_repair_model_suite_table),
    ]
    md_tables: list[tuple[str, str]] = []
    for title, filename, builder in specs:
        rows, md = builder()
        write_csv(TABLE_DIR / filename, rows)
        md_tables.append((title, md))
    write_all_markdown(md_tables)
    print(f"Wrote tables to {TABLE_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
