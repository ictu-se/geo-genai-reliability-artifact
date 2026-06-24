#!/usr/bin/env python3
"""Create deterministic reference outputs for the choropleth benchmark."""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path

import folium
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATA_DIR = ROOT / "data/repos/Materials-for-Creating-maps-by-Artificial-Intelligence/data_choropleth"
DEFAULT_OUT_DIR = ROOT / "experiments/05_choropleth_reliability_benchmark/outputs/reference_baseline"


def repair_geometry(geom):
    if geom is None or geom.is_empty or geom.is_valid:
        return geom
    try:
        from shapely import make_valid

        return make_valid(geom)
    except Exception:
        return geom.buffer(0)


def load_geodata(data_dir: Path) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame, dict[str, object]]:
    mainland_path = data_dir / "mainlandburn.shp"
    boundary_path = data_dir / "boundary.shp"
    mainland = gpd.read_file(mainland_path)
    boundary = gpd.read_file(boundary_path)

    diagnostics: dict[str, object] = {
        "mainland_rows": int(len(mainland)),
        "boundary_rows": int(len(boundary)),
        "mainland_crs_before": str(mainland.crs),
        "boundary_crs_before": str(boundary.crs),
        "mainland_invalid_before": int((~mainland.geometry.is_valid).sum()),
        "boundary_invalid_before": int((~boundary.geometry.is_valid).sum()),
    }

    if mainland.crs is None:
        mainland = mainland.set_crs("EPSG:4326")
        diagnostics["mainland_crs_action"] = "set_epsg_4326_from_lonlat_coordinates"
    if boundary.crs is None:
        boundary = boundary.set_crs("EPSG:4326")
        diagnostics["boundary_crs_action"] = "set_epsg_4326_from_lonlat_coordinates"

    mainland["geometry"] = mainland.geometry.apply(repair_geometry)
    boundary["geometry"] = boundary.geometry.apply(repair_geometry)
    mainland = mainland[~mainland.geometry.is_empty & mainland.geometry.notna()].copy()
    boundary = boundary[~boundary.geometry.is_empty & boundary.geometry.notna()].copy()

    diagnostics.update(
        {
            "mainland_crs_after": str(mainland.crs),
            "boundary_crs_after": str(boundary.crs),
            "mainland_invalid_after": int((~mainland.geometry.is_valid).sum()),
            "boundary_invalid_after": int((~boundary.geometry.is_valid).sum()),
            "mainland_rows_after_geometry_filter": int(len(mainland)),
            "boundary_rows_after_geometry_filter": int(len(boundary)),
        }
    )
    return mainland, boundary, diagnostics


def make_static_map(mainland: gpd.GeoDataFrame, boundary: gpd.GeoDataFrame, out_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.5, 9))
    mainland.plot(
        column="Burned_Are",
        cmap="YlOrRd",
        linewidth=0.45,
        edgecolor="#555555",
        legend=True,
        legend_kwds={"label": "Burned area"},
        ax=ax,
    )
    boundary.boundary.plot(ax=ax, color="#222222", linewidth=0.8)
    ax.set_title("Burned Area by Mainland Portuguese District", fontsize=13, pad=12)
    ax.text(0.01, 0.01, "Source: local Portugal wildfire choropleth materials", transform=ax.transAxes, fontsize=8)
    ax.set_axis_off()
    ax.set_aspect("equal")
    fig.tight_layout()
    fig.savefig(out_dir / "map_static.png", dpi=200)
    plt.close(fig)


def make_interactive_map(mainland: gpd.GeoDataFrame, out_dir: Path) -> None:
    gdf = mainland.to_crs("EPSG:4326")
    centroid = gdf.geometry.union_all().centroid
    fmap = folium.Map(location=[centroid.y, centroid.x], zoom_start=6, tiles="cartodbpositron")
    folium.Choropleth(
        geo_data=gdf.to_json(),
        data=gdf,
        columns=["NAME_1", "Burned_Are"],
        key_on="feature.properties.NAME_1",
        fill_color="YlOrRd",
        fill_opacity=0.75,
        line_opacity=0.45,
        legend_name="Burned area",
        name="Burned area",
    ).add_to(fmap)
    tooltip = folium.GeoJsonTooltip(fields=["NAME_1", "Burned_Are", "of_Fires"], aliases=["District", "Burned area", "Number of fires"])
    folium.GeoJson(gdf, name="District details", tooltip=tooltip, style_function=lambda _: {"fillOpacity": 0, "color": "#444", "weight": 0.6}).add_to(fmap)
    folium.LayerControl().add_to(fmap)
    fmap.save(out_dir / "map_interactive.html")


def make_time_series(data_dir: Path, out_dir: Path) -> dict[str, object]:
    csv_path = data_dir / "MCD64.006.yearly-ba-nf.2002-2022.PRT_Portugal.csv"
    df = pd.read_csv(csv_path)
    fig, ax1 = plt.subplots(figsize=(9, 4.8))
    ax1.plot(df["Year"], df["Burned Area [ha]"], marker="o", color="#b2182b", linewidth=1.8, label="Burned area")
    ax1.set_ylabel("Burned area [ha]")
    ax1.set_xlabel("Year")
    ax1.grid(axis="y", alpha=0.25)
    ax2 = ax1.twinx()
    ax2.plot(df["Year"], df["Number of Fires"], marker="s", color="#2166ac", linewidth=1.3, label="Number of fires")
    ax2.set_ylabel("Number of fires")
    ax1.set_title("Portugal Annual Burned Area and Number of Fires, 2002-2022")
    lines = ax1.get_lines() + ax2.get_lines()
    ax1.legend(lines, [line.get_label() for line in lines], loc="upper left")
    fig.tight_layout()
    fig.savefig(out_dir / "time_series.png", dpi=200)
    plt.close(fig)

    max_row = df.loc[df["Burned Area [ha]"].idxmax()]
    return {
        "time_series_rows": int(len(df)),
        "year_min": int(df["Year"].min()),
        "year_max": int(df["Year"].max()),
        "max_burned_area_year": int(max_row["Year"]),
        "max_burned_area_ha": float(max_row["Burned Area [ha]"]),
        "total_burned_area_ha": float(df["Burned Area [ha]"].sum()),
        "total_number_of_fires": int(df["Number of Fires"].sum()),
    }


def summarize_outputs(out_dir: Path) -> dict[str, object]:
    outputs = {}
    for name in ["map_static.png", "map_interactive.html", "time_series.png", "diagnostics.json"]:
        path = out_dir / name
        outputs[name] = {"exists": path.exists(), "bytes": path.stat().st_size if path.exists() else 0}
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=Path(os.environ.get("CHOROPLETH_DATA_DIR", DEFAULT_DATA_DIR)))
    parser.add_argument("--out-dir", type=Path, default=Path(os.environ.get("CHOROPLETH_OUTPUT_DIR", DEFAULT_OUT_DIR)))
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    mainland, boundary, diagnostics = load_geodata(args.data_dir)
    make_static_map(mainland, boundary, args.out_dir)
    make_interactive_map(mainland, args.out_dir)
    diagnostics.update(make_time_series(args.data_dir, args.out_dir))
    diagnostics["districts"] = sorted(str(value) for value in mainland["NAME_1"].dropna().unique())
    diagnostics["burned_area_min"] = float(mainland["Burned_Are"].min())
    diagnostics["burned_area_max"] = float(mainland["Burned_Are"].max())
    diagnostics["number_of_fires_min"] = float(mainland["of_Fires"].min())
    diagnostics["number_of_fires_max"] = float(mainland["of_Fires"].max())
    diagnostics["finite_numeric_checks"] = {
        key: bool(math.isfinite(value))
        for key, value in diagnostics.items()
        if isinstance(value, float)
    }
    diagnostics_path = args.out_dir / "diagnostics.json"
    diagnostics_path.write_text(json.dumps(diagnostics, indent=2), encoding="utf-8")
    diagnostics["outputs"] = summarize_outputs(args.out_dir)
    diagnostics_path.write_text(json.dumps(diagnostics, indent=2), encoding="utf-8")
    print(json.dumps(summarize_outputs(args.out_dir), indent=2))


if __name__ == "__main__":
    main()
