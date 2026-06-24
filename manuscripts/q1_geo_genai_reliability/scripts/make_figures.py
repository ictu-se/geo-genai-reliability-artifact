#!/usr/bin/env python3
"""Create manuscript draft figures from current experiment outputs."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
FIG_DIR = ROOT / "manuscripts/q1_geo_genai_reliability/figures"


def figure_inventory() -> None:
    df = pd.read_csv(ROOT / "experiments/00_dataset_reproducibility_audit/outputs/dataset_inventory.csv")
    df["size_gb"] = df["size_bytes"].astype(float) / (1024**3)
    df = df.sort_values("size_gb", ascending=True)
    labels = [name.replace(" / ", "\n") for name in df["dataset"]]
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.barh(labels, df["size_gb"], color="#4c78a8")
    ax.set_xlabel("Local size (GB)")
    ax.set_title("Local Geo-GenAI artifact inventory")
    ax.grid(axis="x", alpha=0.25)
    for i, value in enumerate(df["size_gb"]):
        ax.text(value + 0.05, i, f"{value:.2f} GB", va="center", fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "figure_02_dataset_inventory.png", dpi=200)
    plt.close(fig)


def figure_scgm_edge() -> None:
    df = pd.read_csv(ROOT / "experiments/03_scgm_subset_reproduction/outputs/scgm_edge_continuity_val.csv")
    df["edge_absdiff_rgb"] = df["edge_absdiff_rgb"].astype(float)
    df["group"] = df["folder"] + "/" + df["direction"]
    order = ["map_256/right", "map_256/down", "rs_256/right", "rs_256/down"]
    data = [df.loc[df["group"] == group, "edge_absdiff_rgb"].values for group in order]
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.boxplot(data, tick_labels=order, showmeans=True)
    ax.set_ylabel("Mean absolute RGB border difference")
    ax.set_title("SCGM validation tile-edge continuity baseline")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "figure_04_scgm_edge_continuity.png", dpi=200)
    plt.close(fig)


def figure_scgm_retrieval_comparison() -> None:
    df = pd.read_csv(ROOT / "manuscripts/q1_geo_genai_reliability/tables/table_05c_scgm_retrieval_comparison.csv")
    metrics = ["MAE RGB mean", "PSNR mean", "SSIM luma mean", "Edge continuity mean"]
    fig, axes = plt.subplots(1, 4, figsize=(12, 3.8))
    palette = ["#4c78a8", "#54a24b", "#f58518", "#b279a2"]
    for ax, metric in zip(axes, metrics):
        values = df[metric].astype(float)
        ax.bar(df["Baseline"].str.replace(" retrieval", "", regex=False), values, color=palette[: len(df)])
        ax.set_title(metric.replace(" mean", ""))
        ax.tick_params(axis="x", labelrotation=25, labelsize=8)
        ax.grid(axis="y", alpha=0.25)
    fig.suptitle("SCGM generated-output baselines expose metric trade-offs")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "figure_09_scgm_retrieval_comparison.png", dpi=200)
    plt.close(fig)


def figure_choropleth_benchmark() -> None:
    df = pd.read_csv(ROOT / "manuscripts/q1_geo_genai_reliability/tables/table_13_choropleth_model_mode_summary.csv")
    df["Mean score"] = df["Mean score"].astype(float)
    df["Executed"] = df["Executed"].astype(int)
    df["Complete"] = df["Complete"].astype(int)
    df["label"] = df["Model"].str.replace("_", "\n", regex=False) + "\n" + df["Mode"]
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    colors = ["#4c78a8" if mode == "basic" else "#f58518" for mode in df["Mode"]]
    ax.bar(range(len(df)), df["Mean score"], color=colors)
    for i, row in df.iterrows():
        ax.text(i, row["Mean score"] + 0.03, f"exec {row['Executed']}\ncomplete {row['Complete']}", ha="center", va="bottom", fontsize=8)
    ax.set_xticks(range(len(df)))
    ax.set_xticklabels(df["label"], rotation=0, fontsize=8)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Mean prompt-level rubric score")
    ax.set_title("Expanded choropleth benchmark by model and prompting mode")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "figure_05_choropleth_benchmark_scores.png", dpi=200)
    plt.close(fig)


def figure_screenshot_qa() -> None:
    df = pd.read_csv(ROOT / "manuscripts/q1_geo_genai_reliability/tables/table_16_screenshot_level_choropleth_qa.csv")
    df["Screenshot QA pass"] = df["Screenshot QA pass"].astype(int)
    df = df[df["Screenshot QA pass"] > 0].copy()
    df["label"] = df["Source"].str.replace("_", "\n", regex=False) + "\n" + df["Artifact kind"].str.replace("_", " ", regex=False)
    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    colors = ["#4c78a8" if "reference" in source else "#54a24b" for source in df["Source"]]
    ax.bar(range(len(df)), df["Screenshot QA pass"], color=colors)
    ax.set_xticks(range(len(df)))
    ax.set_xticklabels(df["label"], fontsize=8)
    ax.set_ylabel("Artifacts passing screenshot-level QA")
    ax.set_title("Screenshot-level QA separates visual artifacts from file existence")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "figure_07_screenshot_level_qa.png", dpi=200)
    plt.close(fig)


def write_figure_index() -> None:
    lines = [
        "# Figure Index",
        "",
        "| Figure | File | Status |",
        "|---|---|---|",
        "| Figure 1 | `figure_01_artifact_chain.mmd` | conceptual Mermaid draft |",
        "| Figure 2 | `figure_02_dataset_inventory.png` | generated |",
        "| Figure 3 | `../../experiments/02_mapgenerator_image_text_audit/outputs/mapgenerator_proxy_review_contact_sheet.jpg` | generated proxy-review contact sheet |",
        "| Figure 4 | `figure_04_scgm_edge_continuity.png` | generated |",
        "| Figure 5 | `figure_05_choropleth_benchmark_scores.png` | generated |",
        "| Figure 6 | `../../experiments/03_scgm_subset_reproduction/outputs/scgm_retrieval_baseline_contact_sheet.jpg` | generated retrieval-baseline contact sheet |",
        "| Figure 7 | `figure_07_screenshot_level_qa.png` | generated |",
        "| Figure 8 | `../../experiments/05_choropleth_reliability_benchmark/outputs/scores/screenshot_qa/screenshot_qa_contact_sheet.jpg` | generated screenshot-QA contact sheet |",
        "| Figure 9 | `figure_09_scgm_retrieval_comparison.png` | generated |",
        "",
    ]
    (FIG_DIR / "figure_index.md").write_text("\n".join(lines), encoding="utf-8")


def write_mermaid() -> None:
    text = """flowchart LR
  A[Source geodata] --> B[Prompt or caption]
  B --> C{Geo-GenAI paradigm}
  C --> D[Text-to-map image]
  C --> E[RS-to-map tile]
  C --> F[LLM GIS/code map]
  D --> G[Image/VLM/OCR QA]
  E --> H[Pixel + edge-continuity QA]
  F --> I[Execution + GIS lint + screenshot QA]
  G --> J[Failure taxonomy]
  H --> J
  I --> K[Lint feedback repair]
  K --> F
  I --> J
"""
    (FIG_DIR / "figure_01_artifact_chain.mmd").write_text(text, encoding="utf-8")


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    figure_inventory()
    figure_scgm_edge()
    figure_scgm_retrieval_comparison()
    figure_choropleth_benchmark()
    figure_screenshot_qa()
    write_mermaid()
    write_figure_index()
    print(f"Wrote figures to {FIG_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
