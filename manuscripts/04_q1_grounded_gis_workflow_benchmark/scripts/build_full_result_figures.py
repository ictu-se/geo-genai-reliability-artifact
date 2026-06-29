#!/usr/bin/env python3
"""Build manuscript figures for the grounded GIS workflow benchmark."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "manuscripts/04_q1_grounded_gis_workflow_benchmark/tables"
FIGURES = ROOT / "manuscripts/04_q1_grounded_gis_workflow_benchmark/figures"
LATEX_FIGURES = ROOT / "manuscripts/04_q1_grounded_gis_workflow_benchmark/submission/latex/figures"

MODE_ORDER = ["basic", "grounded", "geoguard"]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save(fig, name: str) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    LATEX_FIGURES.mkdir(parents=True, exist_ok=True)
    for folder in [FIGURES, LATEX_FIGURES]:
        fig.savefig(folder / name, dpi=220, bbox_inches="tight")
    plt.close(fig)


def mode_metric_profile() -> None:
    rows = {r["mode"]: r for r in read_csv(TABLES / "full_mode_summary.csv")}
    metrics = ["JSON_VALID", "DATA_VALID", "FIELD_VALID", "CRS_PLAN", "MAP_PLAN", "PRS"]
    labels = ["JSON", "Data", "Field", "CRS", "Map", "PRS"]
    x = np.arange(len(metrics))
    width = 0.25
    fig, ax = plt.subplots(figsize=(9, 4.8))
    colors = {"basic": "#7f8c8d", "grounded": "#2e86ab", "geoguard": "#2ca25f"}
    for i, mode in enumerate(MODE_ORDER):
        values = [float(rows[mode][m]) for m in metrics]
        ax.bar(x + (i - 1) * width, values, width, label=mode, color=colors[mode])
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Mean score")
    ax.set_title("Workflow-plan reliability improves with grounding and validation")
    ax.legend(frameon=False, ncol=3, loc="upper left")
    ax.grid(axis="y", alpha=0.25)
    save(fig, "full_mode_metric_profile.png")


def model_prs_heatmap() -> None:
    rows = read_csv(TABLES / "full_model_mode_summary.csv")
    models = sorted({r["model"] for r in rows})
    matrix = np.zeros((len(models), len(MODE_ORDER)))
    lookup = {(r["model"], r["mode"]): float(r["PRS"]) for r in rows}
    for i, model in enumerate(models):
        for j, mode in enumerate(MODE_ORDER):
            matrix[i, j] = lookup[(model, mode)]
    fig, ax = plt.subplots(figsize=(7.2, 6.6))
    im = ax.imshow(matrix, cmap="YlGnBu", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(np.arange(len(MODE_ORDER)))
    ax.set_xticklabels(MODE_ORDER)
    ax.set_yticks(np.arange(len(models)))
    ax.set_yticklabels(models, fontsize=8)
    for i in range(len(models)):
        for j in range(len(MODE_ORDER)):
            ax.text(j, i, f"{matrix[i, j]:.2f}", ha="center", va="center", fontsize=7, color="black")
    ax.set_title("Plan reliability score by model and prompting mode")
    fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02, label="PRS")
    save(fig, "full_model_prs_heatmap.png")


def category_prs() -> None:
    rows = read_csv(TABLES / "full_category_mode_summary.csv")
    categories = sorted({r["task_type"] for r in rows})
    lookup = {(r["task_type"], r["mode"]): float(r["PRS"]) for r in rows}
    x = np.arange(len(categories))
    width = 0.25
    fig, ax = plt.subplots(figsize=(10, 5.2))
    colors = {"basic": "#7f8c8d", "grounded": "#2e86ab", "geoguard": "#2ca25f"}
    for i, mode in enumerate(MODE_ORDER):
        values = [lookup[(cat, mode)] for cat in categories]
        ax.bar(x + (i - 1) * width, values, width, label=mode, color=colors[mode])
    ax.set_xticks(x)
    ax.set_xticklabels([c.replace("_", "\n") for c in categories], fontsize=8)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Mean PRS")
    ax.set_title("Task-family differences in workflow-plan reliability")
    ax.legend(frameon=False, ncol=3, loc="upper left")
    ax.grid(axis="y", alpha=0.25)
    save(fig, "full_category_prs_by_mode.png")


def failure_counts() -> None:
    rows = {r["mode"]: r for r in read_csv(TABLES / "full_failure_mode_summary.csv")}
    failures = ["json_invalid", "data_invalid", "field_weak", "crs_weak", "schema_weak", "map_plan_weak"]
    labels = ["JSON", "Data", "Field", "CRS", "Schema", "Map"]
    x = np.arange(len(failures))
    width = 0.25
    fig, ax = plt.subplots(figsize=(9, 4.8))
    colors = {"basic": "#7f8c8d", "grounded": "#2e86ab", "geoguard": "#2ca25f"}
    for i, mode in enumerate(MODE_ORDER):
        values = [int(rows[mode][f]) for f in failures]
        ax.bar(x + (i - 1) * width, values, width, label=mode, color=colors[mode])
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Failure count out of 360 tasks")
    ax.set_title("Grounding reduces data hallucination; validation reduces CRS weakness")
    ax.legend(frameon=False, ncol=3, loc="upper right")
    ax.grid(axis="y", alpha=0.25)
    save(fig, "full_failure_counts_by_mode.png")


def main() -> None:
    mode_metric_profile()
    model_prs_heatmap()
    category_prs()
    failure_counts()
    print(f"Wrote figures to {FIGURES.relative_to(ROOT)} and {LATEX_FIGURES.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
