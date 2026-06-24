#!/usr/bin/env python3
"""Candidate for P02: static choropleth with CRS repair and quantile classes."""

from __future__ import annotations

import os
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt


DATA_DIR = Path(os.environ["CHOROPLETH_DATA_DIR"])
OUT_DIR = Path(os.environ["CHOROPLETH_OUTPUT_DIR"])


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    gdf = gpd.read_file(DATA_DIR / "mainlandburn.shp")
    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326")

    fig, ax = plt.subplots(figsize=(8.5, 9))
    gdf.plot(
        column="Burned_Are",
        cmap="YlOrRd",
        scheme="quantiles",
        k=5,
        linewidth=0.45,
        edgecolor="#444444",
        legend=True,
        legend_kwds={"title": "Burned area index", "loc": "center left", "bbox_to_anchor": (1.02, 0.5)},
        ax=ax,
    )
    ax.set_title("Portugal Mainland Burned Area by District", fontsize=14, pad=12)
    ax.set_axis_off()
    ax.annotate(
        "Source: Materials for Creating Maps by Artificial Intelligence",
        xy=(0.01, 0.01),
        xycoords="figure fraction",
        fontsize=8,
    )
    fig.subplots_adjust(left=0.04, right=0.78, top=0.92, bottom=0.08)
    fig.savefig(OUT_DIR / "map_static.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()

