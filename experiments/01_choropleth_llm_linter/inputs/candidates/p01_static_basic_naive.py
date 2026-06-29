#!/usr/bin/env python3
"""Naive candidate for P01: static map without explicit CRS repair."""

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
    fig, ax = plt.subplots(figsize=(7, 9))
    gdf.plot(
        column="Burned_Are",
        cmap="OrRd",
        linewidth=0.5,
        edgecolor="black",
        legend=True,
        ax=ax,
    )
    ax.set_title("Burned Area in Mainland Portugal")
    ax.set_axis_off()
    ax.annotate(
        "Source: Materials for Creating Maps by Artificial Intelligence",
        xy=(0.02, 0.02),
        xycoords="figure fraction",
        fontsize=8,
    )
    fig.savefig(OUT_DIR / "map_static.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()

