#!/usr/bin/env python3
"""Build a cross-paradigm reliability matrix from generated evidence."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MS_DIR = ROOT / "manuscripts/q1_geo_genai_reliability"
OUT_DIR = MS_DIR / "submission/cross_paradigm"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def score_label(score: int) -> str:
    return {
        0: "not_demonstrated",
        1: "weak_or_proxy",
        2: "partial_with_validation",
        3: "strong_in_current_scope",
    }[score]


def add(rows: list[dict[str, str]], paradigm: str, dimension: str, score: int, evidence: str, caveat: str) -> None:
    rows.append(
        {
            "Paradigm": paradigm,
            "Reliability dimension": dimension,
            "Score": str(score),
            "Score label": score_label(score),
            "Evidence": evidence,
            "Caveat": caveat,
        }
    )


def build_rows() -> list[dict[str, str]]:
    mapgen_summary = json.loads((ROOT / "experiments/02_mapgenerator_image_text_audit/outputs/mapgenerator_audit_summary.json").read_text())
    proxy_summary = json.loads((ROOT / "experiments/02_mapgenerator_image_text_audit/outputs/mapgenerator_proxy_caption_review_summary.json").read_text())
    scgm_split = json.loads((ROOT / "experiments/03_scgm_subset_reproduction/outputs/scgm_split_summary.json").read_text())
    scgm_table = read_csv(MS_DIR / "tables/table_05c_scgm_retrieval_comparison.csv")
    choro_model = read_csv(MS_DIR / "tables/table_13_choropleth_model_mode_summary.csv")
    repair_models = read_csv(MS_DIR / "tables/table_20_iterative_repair_model_comparison.csv")
    screenshot = read_csv(MS_DIR / "tables/table_16_screenshot_level_choropleth_qa.csv")
    adjudication = read_csv(MS_DIR / "tables/table_21_evaluator_adjudication_summary.csv")
    judge = read_csv(MS_DIR / "tables/table_22_vlm_judge_robustness.csv")

    mapgen_pairs = sum(int(item["pairs"]) for item in mapgen_summary.values())
    mapgen_mean_proxy = sum(float(item["mean_proxy_fidelity_score"]) for item in proxy_summary.values()) / len(proxy_summary)
    mapgen_adj = next(row for row in adjudication if row["Task"] == "MapGenerator caption fidelity")
    choro_adj = next(row for row in adjudication if row["Task"] == "Choropleth cartographic quality")
    scgm_train = next(item for item in scgm_split if item["split"] == "train")
    scgm_val = next(item for item in scgm_split if item["split"] == "val")
    scgm_best = max(scgm_table, key=lambda row: float(row["SSIM luma mean"]))
    scgm_edge_best = min(scgm_table, key=lambda row: float(row["Edge continuity mean"]))
    choro_generated_complete = sum(int(row["Complete"]) for row in choro_model if row["Model"] != "validator_repair_reference")
    validator_complete = sum(int(row["Complete"]) for row in choro_model if row["Model"] == "validator_repair_reference")
    qwen32_repair = next(row for row in repair_models if row["Repair model"] == "qwen2.5-coder:32b")
    screenshot_pass = sum(int(row["Screenshot QA pass"]) for row in screenshot)
    agreement_rows = [row for row in judge if row["Panel role"] == "agreement_panel"]

    rows: list[dict[str, str]] = []

    add(
        rows,
        "Text-to-map image data",
        "release_reproducibility",
        2,
        f"{mapgen_pairs} local image-caption pairs with no missing images; local train count differs from survey-note claim.",
        "Dataset is usable locally, but paper-level count reconciliation remains a reproducibility caveat.",
    )
    add(
        rows,
        "Text-to-map image data",
        "data_grounding",
        1,
        f"Proxy review mean score about {mapgen_mean_proxy:.3f}; paired VLM exact verdict agreement {mapgen_adj['Exact agreement']}.",
        "Caption fidelity is measurable but not yet human-ground-truth validated.",
    )
    add(
        rows,
        "Text-to-map image data",
        "spatial_faithfulness",
        1,
        "Caption heuristics include relation/feature checks, but no generated topology or georeferenced geometry is available.",
        "Raster images are map-like artifacts, not geospatially executable map data.",
    )
    add(
        rows,
        "Text-to-map image data",
        "artifact_validity",
        3,
        "All local images exist and parse; contact sheets and review CSVs are generated.",
        "Validity here is file/image validity, not correctness of generated geography.",
    )
    add(
        rows,
        "Text-to-map image data",
        "cartographic_completeness",
        1,
        "Proxy/VLM layers inspect visible features and labels on sampled images.",
        "No expert cartographic rubric has been applied to the full dataset.",
    )
    add(
        rows,
        "Text-to-map image data",
        "evaluator_robustness",
        1,
        f"{mapgen_adj['Urgent human adjudication']} of {mapgen_adj['Items']} paired cases are urgent human-adjudication cases.",
        "VLM feature agreement is high, but semantic support thresholds differ sharply.",
    )
    add(
        rows,
        "Text-to-map image data",
        "repairability",
        0,
        "No edit/repair loop is available for raster image-caption pairs in the local artifact chain.",
        "Repairability would require caption revision, image regeneration, or vectorized outputs.",
    )

    add(
        rows,
        "Remote-sensing-to-map tiles",
        "release_reproducibility",
        2,
        f"Base RS-map pairs are complete for train ({scgm_train['rs_map_intersection']}) and validation ({scgm_val['rs_map_intersection']}); cascade references are incomplete.",
        "Original diffusion reproduction remains blocked by model/compute details.",
    )
    add(
        rows,
        "Remote-sensing-to-map tiles",
        "data_grounding",
        3,
        "RS and target map tiles match one-to-one by tile id in the local base pairs.",
        "Cascade-reference conditioning coverage is weaker than base-pair coverage.",
    )
    add(
        rows,
        "Remote-sensing-to-map tiles",
        "spatial_faithfulness",
        2,
        f"Edge continuity is measured for targets and generated outputs; best generated edge mean is {float(scgm_edge_best['Edge continuity mean']):.3f} ({scgm_edge_best['Baseline']}).",
        "Low edge discontinuity can reflect smoothing rather than correct cartographic topology.",
    )
    add(
        rows,
        "Remote-sensing-to-map tiles",
        "artifact_validity",
        3,
        "Six leakage-guarded generated-output baselines each produce 100 validation maps and metric CSVs.",
        "Generated outputs are diagnostics, not full SCGM diffusion reproductions.",
    )
    add(
        rows,
        "Remote-sensing-to-map tiles",
        "cartographic_completeness",
        1,
        f"Best SSIM baseline is {scgm_best['Baseline']} at {float(scgm_best['SSIM luma mean']):.3f}, but contact sheets show smoothing and missing fine map detail.",
        "Image metrics do not verify roads, labels, symbols, or topology.",
    )
    add(
        rows,
        "Remote-sensing-to-map tiles",
        "evaluator_robustness",
        2,
        "Metrics are deterministic and regenerated from CSV/JSON outputs.",
        "No human/VLM cartographic quality labels are attached to SCGM generated tiles.",
    )
    add(
        rows,
        "Remote-sensing-to-map tiles",
        "repairability",
        1,
        "The generated-output harness can score replacement outputs from future CNN/pix2pix/diffusion models.",
        "No automatic repair loop exists for failed tile generations.",
    )

    add(
        rows,
        "LLM-generated choropleth maps",
        "release_reproducibility",
        2,
        "Local data, prompts, generated code, safety scans, run logs, artifacts, and validator outputs are preserved.",
        "Original historical ChatGPT environment/model version is not frozen.",
    )
    add(
        rows,
        "LLM-generated choropleth maps",
        "data_grounding",
        2,
        "Rules prompts, geodata linting, known columns, CRS repair, and validator feedback are explicit in the benchmark.",
        "Initial local model generations still fail to produce complete artifacts.",
    )
    add(
        rows,
        "LLM-generated choropleth maps",
        "spatial_faithfulness",
        2,
        "CRS, geometry validity, join diagnostics, and screenshot-level checks are part of scoring.",
        "The benchmark covers one wildfire choropleth domain, not all thematic map types.",
    )
    add(
        rows,
        "LLM-generated choropleth maps",
        "artifact_validity",
        2,
        f"Initial local model conditions complete {choro_generated_complete} artifacts; iterative 32B repair completes {qwen32_repair['Completed']}/{qwen32_repair['Cases']}; validator/reference completes {validator_complete}; screenshot QA pass artifacts total {screenshot_pass}.",
        "Positive controls prove feasibility, but local LLM completion remains uneven.",
    )
    add(
        rows,
        "LLM-generated choropleth maps",
        "cartographic_completeness",
        2,
        f"Two-VLM visual review has exact agreement {choro_adj['Exact agreement']} and coarse agreement {choro_adj['Coarse agreement']}.",
        "Visual review is still VLM-pilot evidence rather than expert human scoring.",
    )
    add(
        rows,
        "LLM-generated choropleth maps",
        "evaluator_robustness",
        2,
        f"{len(agreement_rows)} task-model rows are agreement-panel VLM runs; failed candidate judges are also recorded.",
        "Human labels are still the strongest missing evaluator-validity upgrade.",
    )
    add(
        rows,
        "LLM-generated choropleth maps",
        "repairability",
        3,
        "Iterative validator-gated repair completes 25 of 40 previously incomplete one-pass repairs, with safety scans on every attempt.",
        "Repair success is model- and task-dependent; deterministic validator/reference is an oracle-style upper bound.",
    )
    return rows


def build_summary(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    grouped: dict[str, list[int]] = {}
    for row in rows:
        grouped.setdefault(row["Paradigm"], []).append(int(row["Score"]))
    out = []
    for paradigm, scores in sorted(grouped.items()):
        out.append(
            {
                "Paradigm": paradigm,
                "Dimensions": str(len(scores)),
                "Total score": str(sum(scores)),
                "Mean score": f"{sum(scores) / len(scores):.2f}",
                "Lowest score": str(min(scores)),
                "Highest score": str(max(scores)),
            }
        )
    return out


def build_report(rows: list[dict[str, str]], summary: list[dict[str, str]]) -> str:
    lines = [
        "# Cross-Paradigm Reliability Matrix",
        "",
        "Scores are 0-3 diagnostic ratings derived from local evidence. They are not universal quality scores; they make the evidence balance comparable across artifact types.",
        "",
        "## Summary",
        "",
        "| Paradigm | Dimensions | Total | Mean | Lowest | Highest |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in summary:
        lines.append(
            f"| {row['Paradigm']} | {row['Dimensions']} | {row['Total score']} | {row['Mean score']} | {row['Lowest score']} | {row['Highest score']} |"
        )
    lines += [
        "",
        "## Matrix",
        "",
        "| Paradigm | Dimension | Score | Label | Evidence | Caveat |",
        "|---|---|---:|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['Paradigm']} | {row['Reliability dimension']} | {row['Score']} | {row['Score label']} | {row['Evidence'].replace('|', '/')} | {row['Caveat'].replace('|', '/')} |"
        )
    lines += [
        "",
        "## Interpretation",
        "",
        "- Text-to-map image data are file-complete but weakest on evaluator agreement and repairability.",
        "- Remote-sensing-to-map tiles have strong base-pair grounding and generated-output diagnostics, but image metrics and continuity scores do not prove cartographic completeness.",
        "- LLM-generated choropleth maps are initially brittle, yet their editable artifact chain makes validation and repair more operational than in raster-only workflows.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    rows = build_rows()
    summary = build_summary(rows)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(OUT_DIR / "cross_paradigm_reliability_matrix.csv", rows)
    write_csv(OUT_DIR / "cross_paradigm_reliability_summary.csv", summary)
    (OUT_DIR / "cross_paradigm_reliability_matrix.md").write_text(build_report(rows, summary), encoding="utf-8")
    print(f"Wrote {(OUT_DIR / 'cross_paradigm_reliability_matrix.csv').relative_to(ROOT)}")
    print(f"Wrote {(OUT_DIR / 'cross_paradigm_reliability_summary.csv').relative_to(ROOT)}")
    print(f"Wrote {(OUT_DIR / 'cross_paradigm_reliability_matrix.md').relative_to(ROOT)}")


if __name__ == "__main__":
    main()
