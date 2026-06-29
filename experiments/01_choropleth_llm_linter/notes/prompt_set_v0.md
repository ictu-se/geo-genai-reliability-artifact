# Prompt Set v0

These prompts are for testing whether an LLM can generate correct map-making code from the same fixed GIS dataset.

## P01 Static Basic

Use Python, GeoPandas, and Matplotlib to create a static choropleth map of mainland Portugal using `mainlandburn.shp`. Color districts by `Burned_Are`. Add a title, legend, district borders, and data source note. Save the map as PNG.

## P02 Static With CRS Repair

Use Python, GeoPandas, and Matplotlib to create a static choropleth map of mainland Portugal using `mainlandburn.shp`. The shapefile may not declare a CRS, so inspect the bounds and set the correct CRS before rendering. Color districts by `Burned_Are` with five quantile classes. Add title, legend, district borders, and source note. Save the map as PNG.

## P03 Interactive Basic

Use Python, GeoPandas, and Folium to create an interactive choropleth map of mainland Portugal using `mainlandburn.shp`. Color districts by `Burned_Are`, add tooltip fields for `Region`, `Burned_Are`, and `of_Fires`, and save as HTML.

## P04 CSV Time Series

Use Python and Pandas to read `MCD64.006.yearly-ba-nf.2002-2022.PRT_Portugal.csv`. Plot annual burned area and number of fires from 2002 to 2022, report the year with maximum burned area, and save the plot as PNG.

## P05 Robust Cartographic Output

Create both a static PNG and interactive HTML choropleth for mainland Portugal. Use `mainlandburn.shp`, repair missing CRS if needed, validate geometries, classify `Burned_Are` into five quantile classes, use a sequential color ramp, and include title, legend, borders, tooltip, and source note. Also print a short report of missing values and invalid geometries.

