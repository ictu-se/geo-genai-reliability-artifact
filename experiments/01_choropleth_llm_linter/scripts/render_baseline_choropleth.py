#!/usr/bin/env python3
"""Render baseline static and interactive choropleth maps."""

from __future__ import annotations

from pathlib import Path

import folium
import geopandas as gpd
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT / "data/repos/Materials-for-Creating-maps-by-Artificial-Intelligence/data_choropleth"
OUT_DIR = ROOT / "experiments/01_choropleth_llm_linter/outputs/baseline_maps"


def load_mainlandburn() -> gpd.GeoDataFrame:
    gdf = gpd.read_file(DATA_DIR / "mainlandburn.shp")
    if gdf.crs is None:
        # The coordinate bounds are longitude/latitude for mainland Portugal.
        gdf = gdf.set_crs("EPSG:4326")
    return gdf


def render_static(gdf: gpd.GeoDataFrame) -> Path:
    out_path = OUT_DIR / "portugal_burned_area_static.png"
    fig, ax = plt.subplots(figsize=(8.5, 9))
    gdf.plot(
        column="Burned_Are",
        cmap="YlOrRd",
        scheme="quantiles",
        k=5,
        linewidth=0.45,
        edgecolor="#4d4d4d",
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
    fig.savefig(out_path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return out_path


def render_interactive(gdf: gpd.GeoDataFrame) -> Path:
    out_path = OUT_DIR / "portugal_burned_area_interactive.html"
    minx, miny, maxx, maxy = gdf.total_bounds
    center = [float((miny + maxy) / 2), float((minx + maxx) / 2)]
    fmap = folium.Map(location=center, zoom_start=7, tiles="CartoDB positron")
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
        name="District values",
        tooltip=folium.GeoJsonTooltip(
            fields=["Region", "Burned_Are", "of_Fires"],
            aliases=["Region", "Burned area index", "Fire-count index"],
            localize=True,
        ),
        style_function=lambda _: {"fillOpacity": 0, "color": "#333333", "weight": 0.5},
    ).add_to(fmap)
    folium.LayerControl(collapsed=False).add_to(fmap)
    fmap.save(out_path)
    return out_path


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    gdf = load_mainlandburn()
    static_path = render_static(gdf)
    interactive_path = render_interactive(gdf)
    print(f"Wrote {static_path.relative_to(ROOT)}")
    print(f"Wrote {interactive_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
