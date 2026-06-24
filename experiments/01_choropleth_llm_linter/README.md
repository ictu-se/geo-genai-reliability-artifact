# 01 Choropleth LLM Linter

Start here first.

This track uses the Portugal wildfire choropleth data to test whether LLM-generated GIS code can create correct thematic maps, then checks the outputs with cartographic lint rules.

Data source:

- `../../data/repos/Materials-for-Creating-maps-by-Artificial-Intelligence/data_choropleth`

Initial tasks:

1. Inspect CSV and shapefile schemas.
2. Create a prompt set for static and interactive choropleth generation.
3. Generate baseline GeoPandas/Folium code.
4. Run the code and capture errors.
5. Build a linter for joins, CRS, invalid geometries, missing values, legend, color ramp, and classification.

