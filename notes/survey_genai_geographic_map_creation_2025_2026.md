# Survey Notes - Generative AI for Geographic Map Creation (2025-2026)

Date: 2026-06-19  
Scope: papers from 2025 to current date about using generative AI/LLMs/diffusion/agents to create, style, evaluate, or assemble geographic maps.

## Snapshot

The field has moved beyond "ask a text-to-image model to draw a map." The strongest 2025-2026 work either:

1. Uses controlled generation, where vector data, remote sensing images, or smaller-scale map tiles constrain the model.
2. Uses LLM/MLLM agents to orchestrate GIS/cartographic tools while keeping authoritative geodata separate from styling.
3. Applies GenAI to specific cartographic subtasks: color scheme design, label placement, symbols, pictorial maps, map critique, and storytelling.

The main unsolved problem is not making something map-like. It is making maps that are geographically faithful, topologically valid, reproducible, evaluable, and useful in professional workflows.

## Paper Notes

### Affolter et al. 2025 - Generative AI in Map-Making

File: `papers/2025_affolter_genai_map_making.pdf`

Question: Can diffusion models generate accurate cartographic tiles if constrained by vector data?

Method:
- Stable Diffusion + ControlNet.
- Input is rasterized vector semantics plus a text prompt specifying style.
- Three styles: Swisstopo, Siegfried historical maps, Old National historical maps.
- Text masks prevent the model from learning/hallucinating labels.
- Post-processing handles color correction and contour lines.
- Gradio web app for non-GIS users.

Data:
- Swisstopo 1:25,000 raster maps and Vector25 data.
- Six sheets per style on average.
- 296,495 training tiles of 512x512 total.
- 100 test tiles per style.

Evaluation:
- Visual inspection.
- Professional cartographer user study with 11 participants.
- Fidelity tasks: distinguish real vs generated tiles.
- Usability: SUS score 82.73.

Findings:
- Best results for modern Swisstopo style; experts struggled to identify synthetic tiles in isolation.
- Historical styles are harder because modern vector data and historical maps are temporally misaligned.
- Participants saw promise for rapid prototyping, updating maps, scenario simulation, education, and illustrative historical style.

Limits/gaps:
- Incorrect topology, broken lines, edge misalignment, inconsistent style across stitched tiles.
- Label generation is avoided, not solved.
- Professional use still needs GIS integration and stronger quality checks.
- Good research gap: topology-aware, tile-sequence-aware controlled diffusion for vector-accurate cartography.

### Sun et al. 2025 - SCGM, Bridging Scales in Map Generation

File: `papers/2025_sun_scgm_bridging_scales_map_generation.pdf`

Question: How to generate seamless multi-scale map tiles from remote sensing images?

Method:
- Scale-aware cartographic generation framework (SCGM).
- Conditional guided diffusion.
- Scale modality encoding for resolution/scale/level.
- Cascaded generation: smaller-scale tiles constrain larger-scale outputs.
- Dual-branch feature adaptation for remote sensing and cascade references.

Data:
- CSCMG multi-scale remote-sensing-to-map dataset.
- Scale examples include levels 14-18, approx. 1:35,000 to 1:2,000.

Evaluation:
- Quantitative comparisons against GAN/I2I baselines.
- Map feature perception metric.
- Ablations on scale encoding and cascaded references.

Findings:
- Cascading helps remove tile discontinuities and preserve spatial coherence.
- Scale encoding reduces hallucinated roads/buildings and better mimics cartographic generalization.
- Strongest for urban/artificial features.

Limits/gaps:
- Weak for natural landscapes and small-scale maps below 1:35,000.
- Pixel-level cascades do not fully capture terrain/geomorphology or long-range dependencies.
- Good research gap: terrain-aware attention and topology/geometric constraints for multi-scale natural and mixed landscapes.

### Wang et al. 2025 - CartoAgent

File: `papers/2025_wang_cartoagent.pdf`

Question: Can multimodal LLM agents perform map style transfer while preserving geographic accuracy?

Method:
- Multi-agent MLLM framework simulating preparation, design, and evaluation.
- Agents include image appreciator, stylesheet designer, icon designer, file implementer, and map reviewer.
- Key design choice: manipulate stylesheets, not vector geometry.
- Uses MLLMs' world knowledge, visual aesthetics, and textual style reasoning.

Data:
- Mapbox vector/style ecosystem.
- Inspiration images/styles and multi-source/multi-scale map data.

Evaluation:
- Experiments on map style transfer.
- Human evaluation with 17 experts/students.
- MLLM map reviewer compared with human judgment.

Findings:
- Separating style from data prevents common image-generation failures: fictitious geography, distorted relations, nonsensical symbols.
- MLLMs are useful for aesthetic critique and semantic style assignment.
- Good fit for personalized/custom style transfer.

Limits/gaps:
- Style transfer is only one cartographic decision; projection, thematic mapping, generalization, labeling remain open.
- Copyright and ownership of style/inspiration sources are unresolved.
- MLLM evaluation is promising but not a substitute for human/cartographic metrics.
- Good research gap: formal evaluation loop combining MLLM critique, cartographic constraints, and human-in-the-loop preferences.

### Song et al. 2025 - LLM Agent with VGI Data for Mapping

File: `papers/2025_song_llm_agent_vgi_mapping.pdf`

Question: Can an LLM agent automatically create maps from VGI/OSM data and user requests?

Method:
- GPT-4o-turbo with temperature 0.
- Prompt engineering and tool-calling.
- Modules: LLM, VGI data acquisition, mapping tools.
- Retrieves OSM data, validates/fixes attributes/boundaries, processes Shapefiles, renders maps.

Data:
- OpenStreetMap/VGI.
- Case studies: Beijing land-use map, Wuhan museum distribution map, and other thematic examples.

Evaluation:
- Qualitative case studies showing tool-call chains and generated maps.

Findings:
- LLM can decompose requests, retrieve VGI data, calculate features, classify values, add legends/compass/title/scale, and output thematic maps.
- Lowers the barrier for non-experts.

Limits/gaps:
- Little quantitative cartographic quality evaluation.
- OSM/VGI quality varies by region and contributor density.
- Tool success depends on prompt specificity and brittle code/tool behavior.
- Good research gap: benchmarked LLM-agent mapping over heterogeneous VGI quality, with automated validation of cartographic completeness and spatial correctness.

### Li & Ning et al. 2025 - Autonomous GIS Research Agenda

File: `papers/2025_li_autonomous_gis_research_agenda.pdf`

Question: What does autonomous GIS look like in the GenAI era?

Method:
- Vision/agenda paper.
- Defines autonomous GIS goals, levels, functions, and scales.
- Includes proof-of-concept agents for retrieval, analysis, cartography, and QGIS copilot.

Relevant case:
- LLM-Cat uses GPT-4o vision to create maps from natural language and iteratively review/revise generated maps.
- It generates Python code, inspects the map, identifies one issue, revises code, and repeats.

Findings:
- Current systems are mostly workflow-aware: they can generate and run workflows.
- Result-aware and knowledge-aware systems are still future goals.
- Human/expert-in-the-loop remains essential.

Limits/gaps:
- GPT-4o showed weak map aesthetics/cartography skills in LLM-Cat.
- Need benchmarks, reviewer agents, FAIR and AI-ready geospatial data, and workforce adaptation.
- Good research gap: "result-aware" autonomous cartography agents that can detect map design and spatial errors with explicit rubrics.

### Yang et al. 2025 - MapColorAI

File: `papers/2025_yang_mapcolorai.pdf`

Question: Can an LLM design contextually relevant choropleth color schemes from natural language and data semantics?

Method:
- Three-stage workflow:
  - Data processing and classification.
  - Color concept design.
  - Color scheme design.
- Integrates color theory, color psychology, ColorBrewer-like concepts, and user interaction.

Data:
- Choropleth datasets used in system evaluation.
- User study with 60 participants.

Findings:
- Users found the system usable and efficient.
- LLMs help translate ambiguous intent like "summer-like" into map color decisions.
- Interaction improves controllability.

Limits/gaps:
- Theme library is limited.
- Needs cultural/regional/color-blindness awareness.
- Text-only interaction is limiting; authors propose image and voice interaction.
- Good research gap: multimodal color design that extracts style from images while preserving perceptual and accessibility constraints.

### Shomer & Xu 2025 - Automated Label Placement via LLMs

File: `papers/2025_shomer_maple_label_placement_llm.pdf`

Question: Can LLMs place map labels by reading cartographic guidelines?

Method:
- Formulates automatic label placement as structured data editing.
- Uses RAG to retrieve relevant labeling guidelines.
- Tests open-source LLMs: Llama3.1, Gemma2, Qwen3, Phi-4.
- Instruction tuning via QLoRA.
- Experiments with coordinate formats and neighboring context.

Data:
- MAPLE benchmark: 100 maps from three cities, over 1000 landmarks from OSM.
- Dataset split: 883 train, 126 validation, 267 test landmarks.

Evaluation:
- RMSE between predicted label coordinate and ground-truth label centroid.

Findings:
- Instruction tuning dramatically improves performance.
- Coordinate representation matters; list/XML formats outperform CSS in many settings.
- Performance varies strongly by landmark type.

Limits/gaps:
- Neighboring context strategy usually did not help, suggesting the context model is weak.
- Does not yet use map image/layout through VLMs.
- Good research gap: VLM + LLM label placement that reasons over actual rendered layout, occlusions, scale, and collisions.

### Pannoon & Netek 2025 - Creating Choropleth Maps by ChatGPT-4

File: `papers/2025_pannoon_choropleth_maps_chatgpt4.pdf`

Question: How good is ChatGPT-4 at producing static and interactive choropleth maps via code?

Method:
- Prompt engineering with two patterns:
  - Basic zero-shot.
  - Advanced Cognitive Verifier and Question Refinement.
- ChatGPT-4 generates Python code using GeoPandas and Folium.
- Compares AI-generated maps with human/GIS-made maps.

Data:
- Wildfire/country profile data and geospatial inputs from study repository.
- Outputs include static and interactive choropleth maps.

Evaluation:
- Attempts, error messages, incorrect outputs, map completeness.
- Suitability against cartographic rules.

Findings:
- Advanced prompts reduce errors and improve completeness.
- LLM code generation is useful for initial visualization and non-programmers.
- Code-based maps preserve geography better than pure text-to-image outputs.

Limits/gaps:
- Weaknesses in data normalization, geometry handling, layout, symbology, scale bars, and consistent code modification.
- Human-made maps remain more flexible and precise.
- Good research gap: prompt/RAG/code-agent systems with cartographic linting and auto-debugging.

### Sun et al. 2025 - Exploratory Review of GenAI in Cartography and GIS

File: `papers/2025_sun_genai_applications_cartography_gis_review.pdf`

Question: What has GenAI been used for in cartography and GIS?

Coverage:
- Map data processing: acquisition, retrieval, quality assessment.
- Map generation with LLMs and image models.
- Geographical analysis.
- Spatial cognition evaluation.

Key takeaways:
- GenAI in cartography is still early.
- LLM + GIS/tool integration is a major direction.
- Domain-specific datasets and foundation models for cartography are missing.

Limits/gaps identified:
- LLMs lack cartographic/domain expertise.
- Spatial relationships and coordinates remain hard.
- Black-box models, data security, and sensitive geodata are important concerns.

### Kang & Wang 2026 - Envisioning GenAI in Cartography

File: `papers/2026_kang_envisioning_genai_cartography.pdf`

Question: Where can GenAI help mapmaking and map use, and where should it not be trusted?

Framework:
- GenAI categories: LLMs, diffusion image models, GenAI agents.
- Benefits: world knowledge/generalizability, artistic style/creativity, multimodal integration.
- Tasks: conceptualization, data preparation, map design, symbolization, typography, evaluation, map reading, interpretation, analysis.

Ethics/challenges:
- Hallucination, reproducibility, bias, copyright, explainability.
- GenAI is less suitable for precision/reliability-critical tasks unless constrained and validated.

Research implication:
- Treat GenAI as assistant/co-designer, not authoritative map producer.

### Kausika & van Altena 2025 - GeoAI in Topographic Mapping

File: `papers/2025_kausika_geoai_topographic_mapping.pdf`

Question: What does GeoAI adoption mean for national mapping agencies?

Framework:
- Five dimensions: Technology & Process, Data, People, Governance, Policy & Compliance.

Findings:
- GeoAI can improve feature detection, change intelligence, real-time updates, 3D processing, and generalization.
- National mapping agencies need organization-wide transformation, not isolated pilots.

Limits/gaps:
- Data lineage, privacy, bias, cybersecurity, algorithm registers, AI regulation, digital sovereignty.
- Need AI literacy, cross-functional teams, data stewards, ethics/governance roles.
- Good research gap: operational MLOps/GeoAI governance framework for GenAI-assisted map production.

### Li et al. 2025 - CartoDirector

File: `papers/2025_li_cartodirector.pdf`

Question: Can LLMs convert text narratives into dynamic cartographic storytelling?

Method:
- Fine-tuned LLM with modules:
  - content enricher,
  - storyboard generator,
  - geospatial scene parser,
  - geospatial databases,
  - cartographic tools.
- Converts story text into scene files with geographic entities, scale, style, perspective, modality.

Status:
- Short ICA abstract, conceptual/prototype-level.

Gap:
- Needs full evaluation of spatial/temporal coherence, database grounding, and map narrative quality.

### Burghardt et al. 2025 - Generative Methods for Pictorial Maps

File: `papers/2025_burghardt_generative_methods_pictorial_maps.pdf`

Question: How can generative methods create pictorial map elements?

Methods:
- Neural Style Transfer for landmark pictograms.
- Stable Diffusion + LoRA for pictorial map signatures from geosocial media terms.
- Background removal and placement on base maps.

Findings:
- Useful for pictograms and expressive map signatures.
- Full-map style transfer causes distortions, topology errors, and pseudo-labels.

Gap:
- Need cartography-specific LoRA/style models and constraints for geometry/topology preservation.

## Relevant Paper Identified but Not Fully Downloaded

### Zhang et al. 2025 - MapGenerator

Status: T&F PDF endpoint returned HTML placeholder; GitHub/data page found.  
Why it matters: It is one of the most direct text-to-map diffusion papers.

Known from accessible sources:
- Diffusion-based text-to-map generation framework.
- Fine-tunes a general text-to-image model with PEFT.
- Constructs MGTrain and MGEval using self-instruct + expert refinement.
- MGTrain: 1000 map-description pairs.
- MGEval: 100 map-description pairs.
- Reports best FID and CLIP Score and stronger expert evaluation than baselines.

Gap:
- Need to obtain/read full PDF or use GitHub/data repository to inspect dataset design and metrics.

### Wang et al. 2025 - AI-guided Map Point Symbol Generation

Status: T&F PDF endpoint returned HTML placeholder; no public full text found via ResearchGate.  
Why it matters: point-symbol generation is an important subtask in automated cartographic design.

## What Data People Use

| Data type | Examples in papers | Strength | Weakness |
|---|---|---|---|
| Authoritative vector data | Swisstopo Vector25, Mapbox vector styles | Preserves geography and topology if style-only generation | Often unavailable, restricted, or not aligned with historical maps |
| Raster map sheets | Swisstopo, Siegfried, Old National maps | Good for learning style/appearance | Labels, scans, temporal mismatch, and dense detail cause artifacts |
| Remote sensing imagery | SCGM remote-sensing-to-map dataset | Enables rapid map generation from current imagery | Hard to preserve cartographic generalization and natural terrain fidelity |
| OSM/VGI | Song et al., MAPLE label placement | Open, global, fresh, cheap | Uneven quality/coverage, attribute errors, rural gaps |
| Human/expert annotations | MAPLE labels, cartographer studies | Enables supervised/benchmark evaluation | Expensive, narrow scope |
| Prompt/code repositories | Pannoon & Netek materials | Reproducible prompt experiments | Model versions change; prompts may not transfer |
| Inspiration images/styles | CartoAgent, pictorial maps | Supports creative/personalized design | Copyright and style ownership concerns |

## Current Technical Directions

### 1. Controlled diffusion/image generation

Representative papers: Affolter et al., SCGM, MapGenerator.

Where it works:
- Map-like tile generation.
- Style rendering when given strong spatial control.
- Remote-sensing-to-map translation.

Main issues:
- Topology and geometry errors.
- Tile boundary inconsistency.
- Text/label hallucination.
- Weak generalization to natural landscapes or unusual scales.

### 2. LLM/MLLM cartographic agents

Representative papers: CartoAgent, LLM/VGI mapping, LLM-Cat, CartoDirector, Pannoon & Netek.

Where it works:
- Tool orchestration.
- Code generation for GeoPandas/Folium/QGIS/Mapbox.
- Multi-step map assembly.
- Style critique and stylesheet generation.

Main issues:
- Brittle workflows and code bugs.
- Limited automated quality assessment.
- Weak map aesthetics unless strongly guided.
- Needs domain-specific memory, RAG, and validators.

### 3. GenAI for map design subtasks

Representative papers: MapColorAI, MAPLE label placement, pictorial maps, point symbols (identified).

Where it works:
- Natural-language-driven preferences.
- Domain rule retrieval and instruction tuning.
- User-controllable design decisions.

Main issues:
- Need multimodal context.
- Need accessibility/culture-aware design.
- Benchmarks are rare.

## Research Gaps Worth Doing

1. Topology-aware diffusion for maps  
Use vector constraints, graph losses, topology repair, or differentiable GIS checks to prevent broken roads, fake crossings, invalid polygons, and disconnected hydrography.

2. Tile-consistent and multi-scale map generation  
Build models that generate regions/sequences of tiles jointly, with explicit scale/generalization constraints.

3. Text and label generation as a first-class map problem  
Most diffusion systems mask text instead of solving labeling. Combine VLM layout understanding, LLM guideline reasoning, collision detection, and typography constraints.

4. Cartographic linting/evaluation benchmark  
Create a benchmark that evaluates completeness, layout, legend/title/scale/north arrow, projection, color accessibility, topology, symbol consistency, and task readability.

5. Result-aware cartographic agents  
Move beyond "LLM runs tools" to agents that inspect final maps, diagnose spatial/cartographic errors, and revise with measurable improvement.

6. Dataset gap for text-map pairs  
Current paired text-map datasets are tiny: MapGenerator reports 1000 training pairs and 100 eval pairs. There is room for a larger, multilingual, multi-style, multi-scale corpus with vector/raster/text triples.

7. Human preference and target-audience conditioning  
Agents should adapt maps for children, experts, color-blind readers, emergency responders, tourists, or planners, with validated perception studies.

8. VGI-aware uncertainty and provenance  
LLM map agents using OSM should show confidence/provenance and handle heterogeneous data quality.

9. Governance and reproducibility  
Need model/version/prompt/data lineage for AI-generated maps, especially for public-sector or national mapping workflows.

10. Multimodal style transfer without copyright leakage  
CartoAgent and pictorial map work raise style ownership questions. A useful direction is controllable style abstraction rather than copying specific artists/maps.

## Possible Thesis/Project Directions

### Direction A - Vietnamese/Local VGI Map Agent with Cartographic Validator

Build an LLM agent that takes Vietnamese natural-language requests, retrieves OSM/Natural Earth/GADM data, generates a thematic map, then runs a cartographic linter.

Novelty:
- Local language and local geography.
- Validation layer instead of only tool-calling.
- Useful for education/planning dashboards.

### Direction B - Topology-Constrained Text-to-Map Generation

Start from vector/raster/text triples, train or fine-tune a diffusion model with topology-aware losses/checks.

Novelty:
- Addresses the biggest weakness of current image generators.
- Can use generated map tiles plus vector constraints.

### Direction C - VLM-based Map Label Placement

Extend MAPLE: render maps, feed image plus vector/landmark metadata to a VLM/LLM, use collision metrics and cartographic rules.

Novelty:
- MAPLE authors explicitly leave VLM layout reasoning for future work.
- Practical and benchmarkable.

### Direction D - Cartographic Evaluation Benchmark for GenAI Maps

Create a benchmark suite and metric set for AI-generated maps, including topology, semantics, visual hierarchy, accessibility, and task-based map reading.

Novelty:
- Many 2025 papers complain about evaluation; few solve it.
- Could be used across diffusion and agent systems.

### Direction E - AI-ready Text-Map Dataset

Construct a dataset of map-description pairs with vector sources, rendered map, style metadata, labels, and prompts. Could start with OSM + map styles + synthetic descriptions refined by humans.

Novelty:
- Directly addresses dataset bottleneck.
- Enables text-to-map, map QA, style transfer, and evaluation.

