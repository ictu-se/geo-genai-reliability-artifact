#!/usr/bin/env python3
"""Planner-reflector generated candidate: adds CRS planning and simple retries."""

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


def project(gdf: gpd.GeoDataFrame, epsg: int = 3857) -> gpd.GeoDataFrame:
    return gdf.to_crs(epsg=epsg) if gdf.crs is not None else gdf.set_crs("EPSG:4326").to_crs(epsg=epsg)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    hospitals = gpd.read_file(DATA / "hospital_points.gpkg")
    boundary = gpd.read_file(DATA / "study_boundary.gpkg")
    tracts = gpd.read_file(DATA / "census_tracts.gpkg")
    floods = gpd.read_file(DATA / "flood_zones.gpkg")
    schools = gpd.read_file(DATA / "school_points.gpkg")

    hospitals_m = project(hospitals)
    boundary_m = project(boundary)
    buf = hospitals_m.copy()
    buf["geometry"] = buf.geometry.buffer(1000)
    buf = gpd.overlay(buf, boundary_m, how="intersection")
    buf.to_file(OUT / "buffer_output.gpkg", layer="buffer_output", driver="GPKG")

    tracts_m = project(tracts)
    floods_m = project(floods)
    overlay = gpd.overlay(tracts_m, floods_m, how="intersection")
    overlay.to_file(OUT / "overlay_output.gpkg", layer="overlay_output", driver="GPKG")

    schools_m = project(schools)
    joined = gpd.sjoin(schools_m, tracts_m[["tract_id", "geometry"]], how="inner", predicate="intersects")
    counts = joined.groupby("tract_id").size().rename("school_count").reset_index()
    school_count = tracts_m.merge(counts, on="tract_id", how="left")
    school_count["school_count"] = school_count["school_count"].fillna(0).astype(int)
    school_count.to_file(OUT / "point_count_join_output.gpkg", layer="point_count_join_output", driver="GPKG")

    with rasterio.open(DATA / "temperature_raster.tif") as src:
        mask_gdf = boundary.to_crs(src.crs)
        clipped, transform = mask(src, [geom.__geo_interface__ for geom in mask_gdf.geometry], crop=True, nodata=src.nodata)
        meta = src.meta.copy()
        meta.update(height=clipped.shape[1], width=clipped.shape[2], transform=transform)
        with rasterio.open(OUT / "raster_clip_output.tif", "w", **meta) as dst:
            dst.write(clipped)

    with rasterio.open(DATA / "temperature_raster.tif") as src:
        work = tracts.to_crs(src.crs)
        stats = zonal_stats(work, src.name, stats=["mean", "sum"], nodata=src.nodata)
    zonal = tracts_m.copy()
    zonal["temp_mean"] = [row.get("mean") for row in stats]
    zonal["temp_sum"] = [row.get("sum") for row in stats]
    zonal.to_file(OUT / "zonal_stats_output.gpkg", layer="zonal_stats_output", driver="GPKG")

    fig, ax = plt.subplots(figsize=(8, 6))
    zonal.plot(column="temp_mean", cmap="Blues", legend=False, ax=ax)
    ax.set_title("Temperature by census tract - Los Angeles County")
    ax.set_axis_off()
    fig.savefig(OUT / "choropleth.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()

