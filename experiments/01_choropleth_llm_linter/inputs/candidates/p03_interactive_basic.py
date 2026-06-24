#!/usr/bin/env python3
"""Candidate for P03: interactive Folium choropleth."""

from __future__ import annotations

import os
from pathlib import Path

import folium
import geopandas as gpd


DATA_DIR = Path(os.environ["CHOROPLETH_DATA_DIR"])
OUT_DIR = Path(os.environ["CHOROPLETH_OUTPUT_DIR"])


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    gdf = gpd.read_file(DATA_DIR / "mainlandburn.shp")
    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326")
    minx, miny, maxx, maxy = gdf.total_bounds
    fmap = folium.Map(location=[(miny + maxy) / 2, (minx + maxx) / 2], zoom_start=7, tiles="CartoDB positron")
    folium.Choropleth(
        geo_data=gdf.to_json(),
        data=gdf,
        columns=["Region", "Burned_Are"],
        key_on="feature.properties.Region",
        fill_color="YlOrRd",
        fill_opacity=0.75,
        line_opacity=0.55,
        legend_name="Burned area index",
    ).add_to(fmap)
    folium.GeoJson(
        gdf,
        tooltip=folium.GeoJsonTooltip(
            fields=["Region", "Burned_Are", "of_Fires"],
            aliases=["Region", "Burned area index", "Fire-count index"],
            localize=True,
        ),
        style_function=lambda _: {"fillOpacity": 0, "color": "#333333", "weight": 0.5},
    ).add_to(fmap)
    fmap.save(OUT_DIR / "map_interactive.html")


if __name__ == "__main__":
    main()

