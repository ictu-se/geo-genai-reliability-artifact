#!/usr/bin/env python3
"""Create synthetic geospatial map panels for the workflow benchmark paper."""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PatchCollection
from matplotlib.patches import Circle, Polygon, Rectangle


ROOT = Path(__file__).resolve().parents[3]
FIGURES = ROOT / "manuscripts/04_q1_grounded_gis_workflow_benchmark/figures"
LATEX_FIGURES = ROOT / "manuscripts/04_q1_grounded_gis_workflow_benchmark/submission/latex/figures"


def county_polygon() -> np.ndarray:
    return np.array(
        [
            [0.4, 0.8],
            [2.2, 0.3],
            [4.8, 0.4],
            [6.7, 1.1],
            [7.8, 2.4],
            [7.6, 4.5],
            [6.1, 5.7],
            [3.8, 6.1],
            [1.5, 5.4],
            [0.2, 3.6],
        ]
    )


def tract_patches() -> list[Rectangle]:
    patches: list[Rectangle] = []
    for i in range(6):
        for j in range(4):
            x = 0.9 + i * 1.05
            y = 1.0 + j * 1.05
            patches.append(Rectangle((x, y), 0.94, 0.92))
    return patches


HOSPITALS = np.array(
    [
        [1.5, 1.5],
        [2.4, 4.7],
        [3.4, 2.6],
        [4.2, 4.0],
        [5.6, 1.9],
        [6.2, 3.7],
    ]
)
SCHOOLS = np.array(
    [
        [1.3, 2.4],
        [1.9, 3.7],
        [2.8, 1.6],
        [3.2, 4.6],
        [4.6, 2.2],
        [5.0, 4.9],
        [5.8, 3.0],
        [6.5, 4.2],
    ]
)


def setup_map(ax: plt.Axes, title: str) -> None:
    poly = county_polygon()
    ax.add_patch(Polygon(poly, closed=True, facecolor="#f7f4ee", edgecolor="#2d3436", linewidth=1.1))
    collection = PatchCollection(tract_patches(), facecolor="none", edgecolor="#b8b2a7", linewidth=0.55)
    ax.add_collection(collection)
    ax.set_xlim(0, 8.1)
    ax.set_ylim(0, 6.3)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(title, fontsize=10, loc="left", pad=6)
    for spine in ax.spines.values():
        spine.set_visible(False)


def add_north_scale(ax: plt.Axes) -> None:
    ax.annotate("N", xy=(7.42, 5.62), ha="center", va="bottom", fontsize=8)
    ax.arrow(7.42, 5.18, 0, 0.33, head_width=0.12, head_length=0.14, color="#2d3436", linewidth=0.7)
    ax.plot([5.95, 7.15], [0.78, 0.78], color="#2d3436", linewidth=2)
    ax.text(6.55, 0.5, "10 km", ha="center", fontsize=7)


def save(fig: plt.Figure, name: str) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    LATEX_FIGURES.mkdir(parents=True, exist_ok=True)
    for out_dir in (FIGURES, LATEX_FIGURES):
        path = out_dir / name
        fig.savefig(path, dpi=240, bbox_inches="tight")
        print(f"Wrote {path.relative_to(ROOT)}")
    plt.close(fig)


def draw_task_suite_examples() -> None:
    fig, axes = plt.subplots(2, 2, figsize=(9.0, 7.0))
    axes = axes.ravel()

    setup_map(axes[0], "A. Metric hospital buffers clipped to boundary")
    for x, y in HOSPITALS:
        axes[0].add_patch(Circle((x, y), 0.55, facecolor="#88c7b1", edgecolor="#16745b", alpha=0.42, linewidth=0.8))
    axes[0].scatter(HOSPITALS[:, 0], HOSPITALS[:, 1], s=30, c="#0b5d4b", edgecolor="white", linewidth=0.6, zorder=5)
    add_north_scale(axes[0])

    setup_map(axes[1], "B. Flood-zone overlay with tract polygons")
    flood = np.array([[1.2, 1.1], [2.5, 0.9], [4.6, 1.8], [6.8, 2.9], [6.4, 4.0], [4.0, 3.2], [2.0, 2.6]])
    axes[1].add_patch(Polygon(flood, closed=True, facecolor="#4e9ad8", edgecolor="#1d5f94", alpha=0.45, linewidth=0.9))
    axes[1].text(4.8, 2.55, "overlay\nintersection", ha="center", va="center", fontsize=8, color="#12476c")
    add_north_scale(axes[1])

    setup_map(axes[2], "C. Raster clip and zonal statistics")
    xs = np.linspace(0.5, 7.6, 80)
    ys = np.linspace(0.8, 5.8, 70)
    xx, yy = np.meshgrid(xs, ys)
    temp = 0.55 * xx + 0.35 * yy + 0.55 * np.sin(xx * 1.4)
    axes[2].imshow(temp, extent=[0.5, 7.6, 0.8, 5.8], origin="lower", cmap="YlOrRd", alpha=0.72)
    axes[2].add_patch(Polygon(county_polygon(), closed=True, facecolor="none", edgecolor="#2d3436", linewidth=1.2))
    axes[2].text(1.05, 5.45, "mask aligns\nto raster CRS", fontsize=8, ha="left", va="top")
    add_north_scale(axes[2])

    setup_map(axes[3], "D. Choropleth export contract")
    values = np.linspace(0.15, 0.95, len(tract_patches()))
    patches = tract_patches()
    collection = PatchCollection(patches, cmap="viridis", edgecolor="white", linewidth=0.55)
    collection.set_array(values)
    axes[3].add_collection(collection)
    axes[3].scatter(SCHOOLS[:, 0], SCHOOLS[:, 1], marker="^", s=22, c="#f6f1d1", edgecolor="#333333", linewidth=0.45)
    cb = fig.colorbar(collection, ax=axes[3], fraction=0.035, pad=0.02)
    cb.set_label("Thematic field", fontsize=7)
    cb.ax.tick_params(labelsize=6)
    add_north_scale(axes[3])

    fig.suptitle("Synthetic GIS task artifacts represented in the workflow-specification benchmark", fontsize=13, y=0.99)
    fig.text(0.5, 0.015, "Illustrative synthetic geometry; no third-party geospatial data are redistributed.", ha="center", fontsize=8)
    fig.tight_layout(rect=[0, 0.03, 1, 0.965])
    save(fig, "geo_task_suite_map_examples.png")


def draw_validation_examples() -> None:
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.8))

    setup_map(axes[0], "A. Basic: missing metric CRS")
    for x, y in HOSPITALS[:4]:
        axes[0].add_patch(Circle((x, y), 0.78, facecolor="#ef9a9a", edgecolor="#b23b3b", alpha=0.45, linewidth=0.8))
    axes[0].scatter(HOSPITALS[:4, 0], HOSPITALS[:4, 1], s=28, c="#9c2d2d", edgecolor="white", linewidth=0.6)
    axes[0].text(0.75, 5.65, "risk: buffer in degrees", fontsize=8, color="#8a1f1f")

    setup_map(axes[1], "B. Grounded: known layers and fields")
    axes[1].scatter(HOSPITALS[:, 0], HOSPITALS[:, 1], s=30, c="#0b5d4b", edgecolor="white", linewidth=0.6, label="hospitals.name")
    axes[1].scatter(SCHOOLS[:, 0], SCHOOLS[:, 1], marker="^", s=26, c="#355c9c", edgecolor="white", linewidth=0.5, label="schools")
    axes[1].legend(loc="lower left", fontsize=7, frameon=True)

    setup_map(axes[2], "C. GeoGuard: CRS and map contract")
    for x, y in HOSPITALS:
        axes[2].add_patch(Circle((x, y), 0.48, facecolor="#92c6a3", edgecolor="#176d4f", alpha=0.45, linewidth=0.8))
    axes[2].scatter(HOSPITALS[:, 0], HOSPITALS[:, 1], s=30, c="#0b5d4b", edgecolor="white", linewidth=0.6)
    axes[2].text(0.75, 5.65, "project -> buffer -> clip -> validate", fontsize=8, color="#176d4f")
    for ax in axes:
        add_north_scale(ax)

    fig.suptitle("Geospatial validation failure modes encoded by the benchmark scorer", fontsize=13, y=0.98)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    save(fig, "geo_validation_contract_examples.png")


def draw_task_family_coverage() -> None:
    families = ["Buffer", "Overlay", "Point\ncount", "Raster\nclip", "Zonal\nstats", "Choropleth"]
    angles = np.linspace(0, 2 * math.pi, len(families), endpoint=False)
    radius = np.array([1.0, 0.9, 0.82, 0.94, 0.88, 0.96])
    x = radius * np.cos(angles)
    y = radius * np.sin(angles)

    fig, ax = plt.subplots(figsize=(7.2, 5.8))
    setup_map(ax, "Benchmark task families over a shared synthetic study area")
    colors = ["#2a9d8f", "#457b9d", "#6d597a", "#e76f51", "#bc6c25", "#588157"]
    for xi, yi, label, color in zip(x, y, families, colors):
        ax.plot([4.0, 4.0 + xi * 1.8], [3.1, 3.1 + yi * 1.25], color=color, linewidth=1.2)
        ax.scatter([4.0 + xi * 1.8], [3.1 + yi * 1.25], s=180, color=color, edgecolor="white", linewidth=1.1, zorder=5)
        ax.text(4.0 + xi * 2.25, 3.1 + yi * 1.55, label, ha="center", va="center", fontsize=9)
    ax.scatter([4.0], [3.1], s=220, color="#222222", edgecolor="white", linewidth=1.2, zorder=6)
    ax.text(4.0, 3.1, "30\ntasks", color="white", ha="center", va="center", fontsize=8)
    add_north_scale(ax)
    fig.tight_layout()
    save(fig, "geo_task_family_coverage.png")


def draw_operation_gallery() -> None:
    fig, axes = plt.subplots(2, 3, figsize=(11.2, 7.0))
    axes = axes.ravel()

    setup_map(axes[0], "A. Buffer service areas")
    for x, y in HOSPITALS[:5]:
        axes[0].add_patch(Circle((x, y), 0.5, facecolor="#8ecae6", edgecolor="#126782", alpha=0.45, linewidth=0.8))
    axes[0].scatter(HOSPITALS[:5, 0], HOSPITALS[:5, 1], s=24, c="#023047", edgecolor="white", linewidth=0.5)

    setup_map(axes[1], "B. Overlay intersection")
    flood = np.array([[1.0, 1.0], [2.1, 1.5], [3.4, 1.2], [6.8, 3.4], [6.0, 4.2], [3.3, 3.1], [1.7, 2.6]])
    axes[1].add_patch(Polygon(flood, closed=True, facecolor="#48cae4", edgecolor="#0077b6", alpha=0.44, linewidth=0.8))
    axes[1].add_patch(Polygon(np.array([[2.0, 1.3], [5.2, 2.0], [6.1, 3.4], [3.4, 3.2]]), closed=True, facecolor="#e76f51", edgecolor="#9d2f1e", alpha=0.28, linewidth=0.8))

    setup_map(axes[2], "C. Point-count joins")
    values = [1, 0, 2, 1, 3, 2, 0, 1, 2, 4, 1, 2, 3, 1, 0, 2, 1, 3, 2, 1, 0, 2, 3, 1]
    collection = PatchCollection(tract_patches(), cmap="BuPu", edgecolor="white", linewidth=0.45)
    collection.set_array(np.array(values))
    axes[2].add_collection(collection)
    axes[2].scatter(SCHOOLS[:, 0], SCHOOLS[:, 1], marker="^", s=22, c="#ffbe0b", edgecolor="#333333", linewidth=0.4)

    setup_map(axes[3], "D. Raster clip")
    xs = np.linspace(0.5, 7.6, 80)
    ys = np.linspace(0.8, 5.8, 70)
    xx, yy = np.meshgrid(xs, ys)
    raster = np.sin(xx * 0.8) + np.cos(yy * 1.1) + xx * 0.12
    axes[3].imshow(raster, extent=[0.5, 7.6, 0.8, 5.8], origin="lower", cmap="terrain", alpha=0.78)
    axes[3].add_patch(Polygon(county_polygon(), closed=True, facecolor="none", edgecolor="#222222", linewidth=1.2))

    setup_map(axes[4], "E. Zonal statistics")
    zones = np.linspace(0.2, 0.9, 24)
    collection = PatchCollection(tract_patches(), cmap="YlOrRd", edgecolor="white", linewidth=0.55)
    collection.set_array(zones)
    axes[4].add_collection(collection)
    axes[4].text(1.0, 5.35, "temp_mean\nby tract_id", fontsize=8, ha="left", va="top")

    setup_map(axes[5], "F. Choropleth export")
    risk = np.array([0.15, 0.18, 0.24, 0.30, 0.36, 0.43, 0.21, 0.28, 0.34, 0.45, 0.55, 0.66,
                     0.29, 0.38, 0.50, 0.59, 0.71, 0.80, 0.35, 0.46, 0.61, 0.73, 0.84, 0.94])
    collection = PatchCollection(tract_patches(), cmap="magma", edgecolor="white", linewidth=0.55)
    collection.set_array(risk)
    axes[5].add_collection(collection)
    cb = fig.colorbar(collection, ax=axes[5], fraction=0.04, pad=0.02)
    cb.ax.tick_params(labelsize=6)
    cb.set_label("risk score", fontsize=7)

    for ax in axes:
        add_north_scale(ax)
    fig.suptitle("Map-level view of all six benchmark operation families", fontsize=13, y=0.99)
    fig.tight_layout(rect=[0, 0, 1, 0.965])
    save(fig, "geo_operation_family_gallery.png")


def draw_failure_case_maps() -> None:
    fig, axes = plt.subplots(2, 2, figsize=(9.2, 7.0))
    axes = axes.ravel()

    setup_map(axes[0], "A. CRS weak: oversized degree buffer")
    for x, y in HOSPITALS[:3]:
        axes[0].add_patch(Circle((x, y), 0.95, facecolor="#ffb4a2", edgecolor="#b23a48", alpha=0.42, linewidth=1.0))
    axes[0].scatter(HOSPITALS[:3, 0], HOSPITALS[:3, 1], s=28, c="#7f1d1d", edgecolor="white", linewidth=0.6)
    axes[0].text(0.75, 5.55, "missing projected CRS", fontsize=8, color="#7f1d1d")

    setup_map(axes[1], "B. Data weak: hallucinated layer")
    axes[1].scatter(HOSPITALS[:, 0], HOSPITALS[:, 1], s=24, c="#0b5d4b", edgecolor="white", linewidth=0.5)
    axes[1].add_patch(Rectangle((2.1, 2.0), 3.2, 1.2, facecolor="white", edgecolor="#cc0000", linewidth=1.2, linestyle="--"))
    axes[1].text(3.7, 2.6, "parks.shp?\nnot in profile", ha="center", va="center", fontsize=8, color="#aa0000")

    setup_map(axes[2], "C. Raster weak: shifted mask")
    xs = np.linspace(0.4, 7.3, 80)
    ys = np.linspace(0.7, 5.6, 70)
    xx, yy = np.meshgrid(xs, ys)
    raster = xx * 0.2 + np.sin(yy * 1.5)
    axes[2].imshow(raster, extent=[0.4, 7.3, 0.7, 5.6], origin="lower", cmap="Spectral_r", alpha=0.70)
    shifted = county_polygon() + np.array([0.45, -0.35])
    axes[2].add_patch(Polygon(shifted, closed=True, facecolor="none", edgecolor="#d00000", linewidth=1.4, linestyle="--"))
    axes[2].add_patch(Polygon(county_polygon(), closed=True, facecolor="none", edgecolor="#222222", linewidth=1.0))
    axes[2].text(0.75, 5.5, "mask/raster CRS mismatch", fontsize=8, color="#b00000")

    setup_map(axes[3], "D. Map weak: missing legend contract")
    collection = PatchCollection(tract_patches(), cmap="viridis", edgecolor="white", linewidth=0.55)
    collection.set_array(np.linspace(0.1, 0.9, 24))
    axes[3].add_collection(collection)
    axes[3].text(0.75, 5.55, "no title, no legend,\nfield unclear", fontsize=8, color="#333333")

    for ax in axes:
        add_north_scale(ax)
    fig.suptitle("Geospatial failure cases targeted by the workflow scorer", fontsize=13, y=0.99)
    fig.tight_layout(rect=[0, 0, 1, 0.965])
    save(fig, "geo_failure_case_maps.png")


def draw_contract_anatomy() -> None:
    fig, ax = plt.subplots(figsize=(8.4, 6.2))
    setup_map(ax, "Anatomy of a grounded GIS workflow contract")
    flood = np.array([[1.1, 1.1], [3.1, 1.4], [5.8, 2.7], [6.3, 3.8], [4.2, 3.4], [2.1, 2.6]])
    ax.add_patch(Polygon(flood, closed=True, facecolor="#90caf9", edgecolor="#1976d2", alpha=0.52, linewidth=1.0))
    ax.scatter(HOSPITALS[:, 0], HOSPITALS[:, 1], s=32, c="#00695c", edgecolor="white", linewidth=0.7, zorder=5)
    ax.scatter(SCHOOLS[:, 0], SCHOOLS[:, 1], marker="^", s=30, c="#f9a825", edgecolor="#333333", linewidth=0.45, zorder=5)

    callouts = [
        ((1.5, 1.5), (0.25, 0.35), "inputs:\nhospitals.name"),
        ((4.2, 2.6), (5.9, 0.55), "operation:\noverlay/intersect"),
        ((5.7, 4.0), (6.55, 5.6), "validation:\nCRS + geometry"),
        ((2.1, 4.7), (0.55, 5.65), "schema:\ntract_id, area_m2"),
        ((6.2, 1.2), (6.8, 1.55), "output:\n.gpkg or .png"),
    ]
    for xy, text_xy, label in callouts:
        ax.annotate(
            label,
            xy=xy,
            xytext=text_xy,
            arrowprops={"arrowstyle": "->", "linewidth": 0.8, "color": "#333333"},
            fontsize=8,
            ha="center",
            va="center",
            bbox={"boxstyle": "round,pad=0.25", "facecolor": "white", "edgecolor": "#777777", "alpha": 0.88},
        )
    add_north_scale(ax)
    fig.tight_layout()
    save(fig, "geo_workflow_contract_anatomy.png")


def draw_cartographic_export_variants() -> None:
    fig, axes = plt.subplots(1, 3, figsize=(11.0, 3.8))
    values = np.array([0.15, 0.18, 0.24, 0.30, 0.36, 0.43, 0.21, 0.28, 0.34, 0.45, 0.55, 0.66,
                       0.29, 0.38, 0.50, 0.59, 0.71, 0.80, 0.35, 0.46, 0.61, 0.73, 0.84, 0.94])
    titles = ["A. Weak map contract", "B. Grounded thematic field", "C. GeoGuard export contract"]
    cmaps = ["gray", "YlGnBu", "plasma"]
    for ax, title, cmap in zip(axes, titles, cmaps):
        setup_map(ax, title)
        collection = PatchCollection(tract_patches(), cmap=cmap, edgecolor="white", linewidth=0.55)
        collection.set_array(values)
        ax.add_collection(collection)
        if title.startswith("A"):
            ax.text(0.75, 5.55, "field not declared", fontsize=8)
        elif title.startswith("B"):
            ax.text(0.75, 5.55, "field: temp_mean", fontsize=8)
        else:
            cb = fig.colorbar(collection, ax=ax, fraction=0.045, pad=0.02)
            cb.ax.tick_params(labelsize=6)
            cb.set_label("temp_mean", fontsize=7)
            ax.text(0.75, 5.55, "title + legend + source", fontsize=8)
        add_north_scale(ax)
    fig.suptitle("Cartographic export variants for choropleth tasks", fontsize=13, y=0.98)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    save(fig, "geo_cartographic_export_variants.png")


def main() -> None:
    draw_task_suite_examples()
    draw_validation_examples()
    draw_task_family_coverage()
    draw_operation_gallery()
    draw_failure_case_maps()
    draw_contract_anatomy()
    draw_cartographic_export_variants()


if __name__ == "__main__":
    main()
