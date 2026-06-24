#!/usr/bin/env python3
"""Audit consistency between manuscript prose and generated evidence tables."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MS_DIR = ROOT / "manuscripts/q1_geo_genai_reliability"
DRAFT = MS_DIR / "draft/manuscript_draft.md"
TABLE_DIR = MS_DIR / "tables"
OUT = MS_DIR / "notes/manuscript_consistency_audit.md"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def word_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").split())


def status(ok: bool) -> str:
    return "PASS" if ok else "TODO"


def contains(text: str, needle: str) -> bool:
    return needle in text


def table_count() -> int:
    return len(list(TABLE_DIR.glob("table_*.csv")))


def figure_count() -> int:
    figure_index = MS_DIR / "figures/figure_index.md"
    return sum(
        line.startswith("| Figure ") and not line.startswith("| Figure |")
        for line in figure_index.read_text(encoding="utf-8").splitlines()
    )


def main() -> None:
    text = DRAFT.read_text(encoding="utf-8")
    table15b = read_csv(TABLE_DIR / "table_15b_mapgenerator_vlm_agreement.csv")
    table15c = read_csv(TABLE_DIR / "table_15c_mapgenerator_clip_caption_embedding.csv")
    table18b = read_csv(TABLE_DIR / "table_18b_choropleth_vlm_agreement.csv")
    table19 = read_csv(TABLE_DIR / "table_19_iterative_validator_repair.csv")
    table20 = read_csv(TABLE_DIR / "table_20_iterative_repair_model_comparison.csv")
    table21 = read_csv(TABLE_DIR / "table_21_evaluator_adjudication_summary.csv")
    table22 = read_csv(TABLE_DIR / "table_22_vlm_judge_robustness.csv")
    table23 = read_csv(TABLE_DIR / "table_23_cross_paradigm_reliability_summary.csv")
    table25 = read_csv(TABLE_DIR / "table_25_matched_repair_model_suite.csv")
    table05c = read_csv(TABLE_DIR / "table_05c_scgm_retrieval_comparison.csv")
    citation_rows = read_csv(MS_DIR / "submission/citation_verification_report.csv")
    split_rows = read_csv(MS_DIR / "submission/main_supplement_split.csv")
    scgm_local = json.loads(
        (ROOT / "experiments/03_scgm_subset_reproduction/outputs/scgm_local_context_ridge_summary.json").read_text()
    )
    scgm_conv = json.loads(
        (ROOT / "experiments/03_scgm_subset_reproduction/outputs/scgm_convolutional_filter_ridge_summary.json").read_text()
    )
    scgm_patch = json.loads(
        (ROOT / "experiments/03_scgm_subset_reproduction/outputs/scgm_patch_embedding_retrieval_summary.json").read_text()
    )
    scgm_tiny_cnn = json.loads(
        (ROOT / "experiments/03_scgm_subset_reproduction/outputs/scgm_tiny_cnn_summary.json").read_text()
    )
    mapgen_embedding = json.loads(
        (ROOT / "experiments/02_mapgenerator_image_text_audit/outputs/mapgenerator_clip_caption_embedding_summary.json").read_text()
    )

    mapgen_overall = next(row for row in table15b if row["Scope"] == "overall")
    choro_overall = next(row for row in table18b if row["Scope"] == "overall")
    mapgen_queue = next(row for row in table21 if row["Task"] == "MapGenerator caption fidelity")
    choro_queue = next(row for row in table21 if row["Task"] == "Choropleth cartographic quality")
    agreement_panel_rows = [row for row in table22 if row["Panel role"] == "agreement_panel"]
    failed_candidate_rows = [row for row in table22 if row["Panel role"] == "failed_candidate"]
    cross_means = {row["Paradigm"]: row["Mean score"] for row in table23}
    qwen32 = next(row for row in table20 if row["Repair model"] == "qwen2.5-coder:32b")
    qwen14 = next(row for row in table20 if row["Repair model"] == "qwen2.5-coder:14b")
    qwen7 = next(row for row in table20 if row["Repair model"] == "qwen2.5-coder:7b")
    deepseek = next(row for row in table20 if row["Repair model"] == "deepseek-coder:6.7b")
    matched_suite = {row["Repair model"]: row for row in table25}
    local_ridge = next(row for row in table05c if row["Baseline"] == "local-context ridge")
    conv_ridge = next(row for row in table05c if row["Baseline"] == "convolutional filter-bank ridge")
    patch_retrieval = next(row for row in table05c if row["Baseline"] == "patch-embedding retrieval")
    tiny_cnn = next(row for row in table05c if row["Baseline"] == "trained tiny CNN")
    clip_overall = next(row for row in table15c if row["Group"] == "overall")

    verified = sum(row["verification_status"] == "verified" for row in citation_rows)
    resolver_verified = sum(row["verification_status"] == "resolver_verified" for row in citation_rows)
    bad_citations = [
        row["citation_key"]
        for row in citation_rows
        if row["verification_status"] not in {"verified", "resolver_verified", "publisher_url_verified"}
    ]

    checks: list[tuple[str, bool, str]] = [
        ("Draft word count reflected", word_count(DRAFT) >= 10000, f"{word_count(DRAFT)} words"),
        ("Full table count reflected in supplement text", contains(text, f"full {table_count()}-table evidence set"), f"{table_count()} tables"),
        ("Figure count remains indexed", figure_count() >= 9, f"{figure_count()} figures"),
        ("MapGenerator exact VLM agreement claim present", contains(text, mapgen_overall["Exact verdict agreement"]), mapgen_overall["Exact verdict agreement"]),
        ("MapGenerator feature agreement claim present", contains(text, mapgen_overall["Feature agreement"]), mapgen_overall["Feature agreement"]),
        ("MapGenerator CLIP scoring claim present", contains(text, f"all {clip_overall['Items']} pairs") and contains(text, f"score is {float(clip_overall['Mean CLIP score']):.3f}"), f"{clip_overall['Items']} pairs; mean={clip_overall['Mean CLIP score']}"),
        ("MapGenerator CLIP summary agrees with table", mapgen_embedding.get("scored_pairs") == int(clip_overall["Items"]) and abs(float(mapgen_embedding["mean_embedding_score"]) - float(clip_overall["Mean CLIP score"])) < 0.00001, f"summary={mapgen_embedding.get('scored_pairs')}; mean={mapgen_embedding.get('mean_embedding_score')}"),
        ("Choropleth exact VLM agreement claim present", contains(text, choro_overall["Exact verdict agreement"]), choro_overall["Exact verdict agreement"]),
        ("Choropleth usable/below agreement claim present", contains(text, choro_overall["Usable/below agreement"]), choro_overall["Usable/below agreement"]),
        ("MapGenerator adjudication queue claim present", contains(text, f"{mapgen_queue['Urgent human adjudication']} of {mapgen_queue['Items']}"), f"{mapgen_queue['Urgent human adjudication']} of {mapgen_queue['Items']}"),
        ("Choropleth adjudication queue claim present", contains(text, f"{choro_queue['Urgent human adjudication']} of {choro_queue['Items']}"), f"{choro_queue['Urgent human adjudication']} of {choro_queue['Items']}"),
        ("Choropleth stable adjudication claim present", contains(text, f"{choro_queue['Stable/low priority']} validator/reference"), f"{choro_queue['Stable/low priority']} stable/low"),
        ("VLM judge robustness claim present", contains(text, "judge-robustness audit") and contains(text, "schema adherence"), f"agreement={len(agreement_panel_rows)}; failed={len(failed_candidate_rows)}"),
        (
            "Cross-paradigm reliability matrix claim present",
            (contains(text, f"score of {cross_means['Text-to-map image data']}") or contains(text, f"score of {cross_means['Text-to-map image data']}:"))
            and contains(text, f"score of {cross_means['Remote-sensing-to-map tiles']}")
            and contains(text, f"score of {cross_means['LLM-generated choropleth maps']}"),
            "; ".join(f"{key}={value}" for key, value in sorted(cross_means.items())),
        ),
        ("Iterative repair completion claim present", contains(text, f"{qwen32['Completed']} of the {qwen32['Cases']}"), f"{qwen32['Completed']}/{qwen32['Cases']}"),
        ("Qwen 7B/14B repair-suite claim present", contains(text, "Qwen 7B and 14B matched suite each complete three of eight") or contains(text, "two smaller Qwen models each produced 14 safety-clean repair attempts and completed three of the eight cases"), f"{qwen7['Completed']}/{qwen7['Cases']}; {qwen14['Completed']}/{qwen14['Cases']}"),
        ("DeepSeek repair-suite claim present", contains(text, "DeepSeek 6.7B suite completes zero of eight") or contains(text, "DeepSeek completed none of the eight cases"), f"{deepseek['Completed']}/{deepseek['Cases']}"),
        ("Matched repair suite table populated", set(matched_suite) == {"qwen2.5-coder:14b", "qwen2.5-coder:7b", "deepseek-coder:6.7b"} and all(row["Matched cases"] == "8" for row in matched_suite.values()), f"models={len(matched_suite)}"),
        ("Matched repair suite score claims present", contains(text, matched_suite["qwen2.5-coder:14b"]["Mean final score"]) and contains(text, matched_suite["qwen2.5-coder:7b"]["Mean final score"]) and contains(text, matched_suite["deepseek-coder:6.7b"]["Mean final score"]), "; ".join(f"{key}={row['Mean final score']}" for key, row in sorted(matched_suite.items()))),
        ("Local-context ridge SSIM claim present", contains(text, f"SSIM {float(local_ridge['SSIM luma mean']):.3f}"), local_ridge["SSIM luma mean"]),
        ("Local-context ridge summary agrees with table", abs(scgm_local["global_ssim_luma"]["mean"] - float(local_ridge["SSIM luma mean"])) < 0.00001, str(scgm_local["global_ssim_luma"]["mean"])),
        ("Convolutional filter ridge SSIM claim present", contains(text, f"SSIM {float(conv_ridge['SSIM luma mean']):.3f}") and contains(text, f"edge-continuity mean {float(conv_ridge['Edge continuity mean']):.2f}"), f"SSIM={conv_ridge['SSIM luma mean']}; edge={conv_ridge['Edge continuity mean']}"),
        ("Convolutional filter ridge summary agrees with table", abs(scgm_conv["global_ssim_luma"]["mean"] - float(conv_ridge["SSIM luma mean"])) < 0.00001, str(scgm_conv["global_ssim_luma"]["mean"])),
        ("Patch-embedding retrieval claim present", contains(text, f"MAE {float(patch_retrieval['MAE RGB mean']):.2f}") and contains(text, f"SSIM {float(patch_retrieval['SSIM luma mean']):.3f}") and contains(text, f"edge-continuity mean {float(patch_retrieval['Edge continuity mean']):.2f}"), f"MAE={patch_retrieval['MAE RGB mean']}; SSIM={patch_retrieval['SSIM luma mean']}; edge={patch_retrieval['Edge continuity mean']}"),
        ("Patch-embedding retrieval summary agrees with table", abs(scgm_patch["global_ssim_luma"]["mean"] - float(patch_retrieval["SSIM luma mean"])) < 0.00001, str(scgm_patch["global_ssim_luma"]["mean"])),
        ("Tiny-CNN baseline claim present", contains(text, f"MAE {float(tiny_cnn['MAE RGB mean']):.2f}") and contains(text, f"SSIM {float(tiny_cnn['SSIM luma mean']):.3f}") and contains(text, f"edge-continuity mean {float(tiny_cnn['Edge continuity mean']):.2f}"), f"MAE={tiny_cnn['MAE RGB mean']}; SSIM={tiny_cnn['SSIM luma mean']}; edge={tiny_cnn['Edge continuity mean']}"),
        ("Tiny-CNN summary agrees with table", scgm_tiny_cnn.get("model_family") == "trained_cnn" and abs(scgm_tiny_cnn["global_ssim_luma"]["mean"] - float(tiny_cnn["SSIM luma mean"])) < 0.00001, str(scgm_tiny_cnn["global_ssim_luma"]["mean"])),
        ("Citation verification has no unresolved rows", not bad_citations, f"verified={verified}; resolver_verified={resolver_verified}; bad={bad_citations}"),
        ("Blinded manuscript regenerated from current draft", contains((MS_DIR / "submission/blinded_main_manuscript.md").read_text(encoding="utf-8"), f"full {table_count()}-table evidence set"), "blinded text table-count claim"),
        ("Main/supplement split matches table and figure counts", len(split_rows) == table_count() + figure_count(), f"{len(split_rows)} split rows"),
    ]

    lines = [
        "# Manuscript Consistency Audit",
        "",
        "This audit checks high-risk numerical and status claims in the manuscript draft against generated tables and summaries.",
        "",
        "| Check | Status | Evidence |",
        "|---|---|---|",
    ]
    for name, ok, evidence in checks:
        lines.append(f"| {name} | {status(ok)} | {evidence} |")
    lines += [
        "",
        f"- Automated consistency checks passed {sum(ok for _, ok, _ in checks)} of {len(checks)}",
        "",
    ]
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
