#!/usr/bin/env python3
"""Intentionally brittle candidate: uses a plausible but wrong column name."""

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
    gdf.plot(column="Burned Area [ha]", cmap="YlOrRd", legend=True, ax=ax)
    ax.set_axis_off()
    fig.savefig(OUT_DIR / "map_static.png")


if __name__ == "__main__":
    main()

