# Data Manifest: Generative AI for Geographic Map Creation

Updated: 2026-06-19

This note tracks experimental data found while surveying 2025-2026 papers on generative AI for geographic map creation. It separates datasets actually downloaded into this workspace from sources that are described in papers but not publicly packaged.

## Downloaded Data

### SCGM / CSCMG

- Paper/topic: scale-aware conditional generative mapping (SCGM), remote-sensing image to tile-map generation.
- Source repository: https://github.com/Magician-MO/SCGM
- Repository clone: `data/repos/SCGM`
- Repository commit checked: `a3ea795`
- Dataset source used: Google Drive file linked from SCGM README, id `1F7VHOVY8B0ANzUu22DXQ1pvlQb6_wOv2`
- Archive: `data/raw/SCGM/CSCMG.tar.gz`
- Extracted data: `data/raw/SCGM/extracted/TMGN_1814`
- Disk use: `data/raw/SCGM` is about 10 GB including both archive and extracted files; extracted data alone is about 6.2 GB.
- README description: real-world remote sensing images and tile maps from Glasgow and London, UK; 137,042 pairs total, with 135,571 training and 1,471 testing pairs; multiple map scales from 1:35,000 to 1:2,000.
- Local structure:
  - `train/map_256`: 135,572 files
  - `train/rs_256`: 135,572 files
  - `train/ref_scale_2_256`: 130,701 files
  - `train/ref_scale_4_256`: 115,595 files
  - `train/tilelist_18_15.csv`: 1 file
  - `train/tilelist_18_16.csv`: 1 file
  - `val/map_256`: 1,473 files
  - `val/rs_256`: 1,473 files
  - `val/ref_scale_2_256`: 1,192 files
  - `val/ref_scale_4_256`: 900 files
  - `val/tilelist_18_15.csv`: 1 file
  - `val/tilelist_18_15_400AVG.csv`: 1 file
  - `val/tilelist_18_16.csv`: 1 file
  - `val/tilelist_18_16_300AVG.csv`: 1 file
- Notes:
  - The extracted folder uses `val`, while the README/paper wording calls the held-out split testing.
  - Some image files have `.png` extensions but are detected as JPEG image data; analysis scripts should inspect image headers rather than rely only on extensions.

### MapGenerator / MGTrain and MGEval

- Paper/topic: instruction-driven geographic map generation with LLM planning plus layout/map-generation agents.
- Source repository: https://github.com/AGI-GIS/MapGenerator
- Repository clone: `data/repos/MapGenerator`
- Repository commit checked: `55b7156`
- Dataset archive from repo: `data/repos/MapGenerator/data.zip`
- Extracted data: `data/raw/MapGenerator`
- Disk use: extracted data about 42 MB; repository clone about 60 MB.
- Local structure:
  - `MapTrain/Images`: 750 `.jpg` files
  - `MapTrain/descriptions.xlsx`: 751 rows including header
  - `MGEval/Images`: 100 `.jpg` files
  - `MGEval/descriptions.xlsx`: 101 rows including header
- Notes:
  - The paper/README describe MGTrain as 1,000 image-text pairs and MGEval as 100 pairs. The currently published `data.zip` in the repository contains 750 training images and 100 evaluation images.
  - The descriptions are natural-language captions paired with map images, e.g. Google-map-like road/water/land-cover descriptions.
  - The repository license notice says the data is for research preview/non-commercial use and references the Stable Diffusion 3.5 license.

### Materials for Creating Maps by Artificial Intelligence

- Paper/topic: ChatGPT-4-assisted static and interactive choropleth map creation.
- Source repository: https://github.com/GeoAI-Map/Materials-for-Creating-maps-by-Artificial-Intelligence
- Repository clone: `data/repos/Materials-for-Creating-maps-by-Artificial-Intelligence`
- Repository commit checked: `f844100`
- Disk use: about 474 MB.
- File count: 113 files.
- Experimental data folder: `data/repos/Materials-for-Creating-maps-by-Artificial-Intelligence/data_choropleth`
- Key data files:
  - `MCD64.006.yearly-ba-nf.2002-2022.PRT_Portugal.csv`
  - `boundary.shp`, `boundary.dbf`, `boundary.prj`, `boundary.shx`, plus sidecar files
  - `mainlandburn.shp`, `mainlandburn.dbf`, `mainlandburn.shx`, plus sidecar files
- Notes:
  - This repository contains both inputs for the choropleth experiment and generated map artifacts/images.
  - The shapefile folder also contains `.sr.lock` files inherited from the source repository; these are not analysis data.

### Generative AI Mapmaking / Cartographic ControlNet

- Paper/topic: historical-map-style generation from contemporary map data using Stable Diffusion and ControlNet.
- Source repository: https://github.com/claudaff/generative-ai-mapmaking
- Repository clone: `data/repos/generative-ai-mapmaking`
- Repository commit checked: `4c8e16d`
- Disk use: about 360 KB.
- Downloaded content: code, workflow files, README, and small supporting image assets.
- Notes:
  - No experimental tile dataset is packaged in the repository.
  - The README describes a user-created training format with `target`, `source`, and `prompt.json` entries derived from Swiss map sheets and vector data.
  - The paper describes using Swiss topographic map sheets/scans and Swisstopo Vector25-like vector data, but the actual paired training/evaluation tiles are not released in the repository.
  - Pretrained models are on Hugging Face under `claudaff/Cartographic-ControlNet`, but those are model weights rather than the experiment dataset.

## Sources Not Downloaded

### CartoAgent / MapStyleTransfer

- Paper/topic: prompt-driven map style transfer using Mapbox static maps, LLM agents, and style rules.
- Paper-stated repository: https://github.com/Bonj0ur/MapStyleTransfer
- Status: repository lookup and clone returned 404 on 2026-06-19.
- Data status: no packaged dataset downloaded.
- Likely experimental data: Mapbox-rendered map images/styles generated through API calls, not a static public dataset in the currently reachable repository.

### MAPLE

- Paper/topic: multi-agent LLMs for advanced thematic map production.
- Paper-stated repository: https://github.com/HarryShomer/MAPLE
- Status: repository lookup and clone returned 404 on 2026-06-19; GitHub search found no matching public repository.
- Data status: no packaged dataset downloaded.

### MapColorAI

- Paper/topic: color-scheme generation/recommendation for thematic maps.
- Status: no public code or dataset repository found during this pass.
- Data status: no packaged dataset downloaded.
- Experimental data described in paper: an example GDP dataset for 30 Chinese provinces in 2023 and generated color-scheme outputs. The paper does not appear to publish a reusable dataset artifact.

### VGI Mapping with Chain-of-Thought LLMs

- Paper/topic: generating maps from volunteered geographic information through LLM reasoning and mapping code.
- Status: no packaged dataset found during this pass.
- Data status: no exact experimental dataset downloaded.
- Experimental data described in paper: OpenStreetMap/VGI-style geographic entities and map-making tasks. A current OSM extract could be fetched later, but it would not exactly reproduce the authors' snapshot unless the paper provides a timestamped extract.

### CartoDirector / Pictorial and Artistic Map Generation

- Paper/topic: LLM-assisted pictorial/artistic map generation with layout/content/style guidance.
- Status: short paper/abstract material does not expose a public experimental dataset in the artifacts checked so far.
- Data status: no packaged dataset downloaded.
- Likely experimental data: map/location prompts, geosocial media or landmark imagery, and generated pictorial map outputs; exact packaged inputs not found yet.

## Next Reading Checks

- While reading each paper in detail, verify whether the authors report any additional supplementary links, DOI-hosted artifacts, or benchmark snapshots not visible from the main repository.
- For unavailable datasets, record whether the barrier is a dead repository, API-only dynamic data, proprietary terms, or simply missing supplementary material.
- For datasets with API-derived content, decide whether to reproduce a fresh comparable dataset or only document that the original experiment is not exactly reproducible from public artifacts.
