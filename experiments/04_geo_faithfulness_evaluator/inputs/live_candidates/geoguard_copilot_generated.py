#!/usr/bin/env python3
"""GeoGuard-style generated candidate with CRS, schema, topology, and map guards."""

from __future__ import annotations

import os
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import rasterio
from rasterio.mask import mask
from rasterstats import zonal_stats


DATA = Path(os.environ["GEOGUARD_DATA_DIR"])
OUT = Path(os.environ["GEOGUARD_OUTPUT_DIR"])


def metric(gdf: gpd.GeoDataFrame, epsg: int = 3857) -> gpd.GeoDataFrame:
    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326")
    return gdf.to_crs(epsg=epsg)


def repair(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    out = gdf.copy()
    out["geometry"] = out.geometry.buffer(0)
    return out


def restore_field(gdf: gpd.GeoDataFrame, field: str) -> gpd.GeoDataFrame:
    if field in gdf.columns:
        return gdf
    out = gdf.copy()
    for candidate in (f"{field}_1", f"{field}_left", f"{field}_x"):
        if candidate in out.columns:
            out[field] = out[candidate]
            break
    return out


def write(gdf: gpd.GeoDataFrame, filename: str, layer: str) -> None:
    gdf = repair(gdf)
    gdf.to_file(OUT / filename, layer=layer, driver="GPKG")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    hospitals = gpd.read_file(DATA / "hospital_points.gpkg")
    boundary = gpd.read_file(DATA / "study_boundary.gpkg")
    tracts = gpd.read_file(DATA / "census_tracts.gpkg")
    floods = gpd.read_file(DATA / "flood_zones.gpkg")
    schools = gpd.read_file(DATA / "school_points.gpkg")

    hospitals_m, boundary_m = metric(hospitals), metric(boundary)
    buf = hospitals_m.copy()
    buf["geometry"] = buf.geometry.buffer(1000)
    buf = gpd.overlay(buf, boundary_m, how="intersection")
    buf = restore_field(buf, "name")
    write(buf, "buffer_output.gpkg", "buffer_output")

    tracts_m, floods_m = metric(tracts), metric(floods)
    overlay = gpd.overlay(tracts_m, floods_m, how="intersection")
    overlay = restore_field(overlay, "tract_id")
    write(overlay, "overlay_output.gpkg", "overlay_output")

    schools_m = metric(schools)
    joined = gpd.sjoin(schools_m, tracts_m[["tract_id", "geometry"]], how="inner", predicate="intersects")
    counts = joined.groupby("tract_id").size().rename("school_count").reset_index()
    school_count = tracts_m.merge(counts, on="tract_id", how="left")
    school_count["school_count"] = school_count["school_count"].fillna(0).astype(int)
    write(school_count, "point_count_join_output.gpkg", "point_count_join_output")

    with rasterio.open(DATA / "temperature_raster.tif") as src:
        mask_gdf = boundary.to_crs(src.crs)
        clipped, transform = mask(src, [geom.__geo_interface__ for geom in mask_gdf.geometry], crop=True, nodata=src.nodata)
        meta = src.meta.copy()
        meta.update(height=clipped.shape[1], width=clipped.shape[2], transform=transform, nodata=src.nodata)
        with rasterio.open(OUT / "raster_clip_output.tif", "w", **meta) as dst:
            dst.write(clipped)

    with rasterio.open(DATA / "temperature_raster.tif") as src:
        work = tracts.to_crs(src.crs)
        stats = zonal_stats(work, src.name, stats=["mean", "sum"], nodata=src.nodata)
    zonal = metric(tracts)
    zonal["temp_mean"] = [row.get("mean") for row in stats]
    zonal["temp_sum"] = [row.get("sum") for row in stats]
    write(zonal, "zonal_stats_output.gpkg", "zonal_stats_output")

    fig, ax = plt.subplots(figsize=(10, 7))
    zonal.plot(
        column="temp_mean",
        cmap="Blues",
        scheme="Quantiles",
        k=5,
        legend=True,
        linewidth=0.08,
        edgecolor="white",
        legend_kwds={"title": "Mean temperature"},
        ax=ax,
    )
    ax.set_title("Temperature by Census Tract - Los Angeles County", fontsize=13)
    ax.set_axis_off()
    ax.annotate("Source: WorldClim + TIGER/Line census tracts", xy=(0.01, 0.01), xycoords="figure fraction", fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "choropleth.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()

