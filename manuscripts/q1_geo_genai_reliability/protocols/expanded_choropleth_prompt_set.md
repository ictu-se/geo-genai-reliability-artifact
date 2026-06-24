# Expanded Choropleth Prompt Set

This prompt set is designed for the Q1 manuscript's LLM-code mapmaking experiment.

## Data Context

Available data:

- Portugal wildfire CSV: `MCD64.006.yearly-ba-nf.2002-2022.PRT_Portugal.csv`
- Boundary shapefile: `boundary.shp`
- Mainland burned-area shapefile: `mainlandburn.shp`

Known data issues:

- `boundary.shp` has one invalid geometry.
- `mainlandburn.shp` lacks CRS metadata.

## Prompt Families

### F1 Static Choropleth Basics

P01. Create a static choropleth map of burned area by Portuguese district.

P02. Create a static choropleth map of number of fires by Portuguese district.

P03. Create a static choropleth map with title, legend, source note, and district boundaries.

### F2 CRS and Geometry Robustness

P04. Detect and set missing CRS for the mainland shapefile before mapping.

P05. Repair invalid geometries before joining and rendering the map.

P06. Validate that all geometries are non-empty and report any dropped features.

### F3 Attribute and Join Robustness

P07. Join the wildfire CSV to the district geometry using the correct key and report unmatched records.

P08. Create a map while intentionally checking that the burned-area column exists before plotting.

P09. Create a map using number of fires, and fail gracefully if the column is missing.

P10. Produce a diagnostic CSV listing input rows, output rows, missing values, and unmatched keys.

### F4 Cartographic Design

P11. Use a sequential color ramp appropriate for burned area.

P12. Use a color-blind-safe color ramp and explain the choice in a metadata JSON file.

P13. Classify burned area into five quantile classes.

P14. Classify burned area using natural breaks or a documented fallback if natural breaks is unavailable.

P15. Include title, legend, source, scale cue, and readable boundaries.

### F5 Interactive Maps

P16. Create an interactive Folium choropleth with tooltips for district, burned area, and number of fires.

P17. Create an interactive map with a layer control and a legend.

P18. Create both static PNG and interactive HTML outputs from the same cleaned data.

### F6 Time-Series and Multi-Output Reports

P19. Plot a time series of annual burned area from 2002 to 2022.

P20. Identify the maximum burned-area year and include it in a text report.

P21. Produce a combined report containing static map, time-series plot, and data diagnostics.

### F7 Adversarial / Failure-Seeking Prompts

P22. Use a wrong burned-area column name, but detect and correct it using available columns.

P23. Try to map a non-existent attribute and return a clear diagnostic instead of crashing.

P24. Create a map after checking whether CRS metadata are present and valid.

P25. Create a robust map script that can be re-run from a clean workspace.

## Conditions

### C1 Basic

Natural-language task only.

### C2 Data-Grounded

Task plus exact file names and known columns.

### C3 Cartographic-Rules

Task plus file names, columns, CRS/geometry requirements, and map completeness rubric.

### C4 Lint-Repair

Initial output plus structured linter feedback.

## Required Outputs Per Run

- generated Python script;
- stdout/stderr;
- return code;
- static PNG if requested;
- interactive HTML if requested;
- diagnostic JSON/CSV if requested;
- screenshot-level QA result;
- lint score before and after repair.

