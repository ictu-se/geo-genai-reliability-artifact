# Validation Layers and Pass Criteria

| Layer | What it checks | Pass criterion | Why it matters |
|---|---|---|---|
| Static safety scan | Syntax and prohibited operations before execution | Script is safe to run under the benchmark scanner | Prevents malformed or unsafe code from entering execution |
| Controlled execution | Return code, timeout, stdout, stderr, created files | Script exits without timeout and produces observable run artifacts | Separates runnable code from fluent but broken code |
| Data grounding | Known file names and expected schema references | Script uses benchmark inputs and required data fields | Catches hallucinated paths, columns, and joins |
| Geospatial validity | CRS handling and geometry repair when required | Required CRS/geometry checks are present and pass | Prevents silent spatial assumptions and invalid layers |
| Required outputs | Prompt-specific artifact files | All required files exist with expected names | Keeps scoring aligned with the requested map workflow |
| Rendered artifact QA | File size, parseability, non-empty content, validity proxies | Artifact is present and inspectable as the expected type | Distinguishes written files from usable artifacts |
| Screenshot QA | Browser/static rendering, nonblank pixels, visual variation | Rendered output passes screenshot-level heuristics | Catches blank or visually degenerate maps |
| Content QA | Map-like structure, thematic content, expected artifact type | Visual output contains task-relevant cartographic content | Narrows structural success to visually meaningful artifacts |
| VLM/human review | Higher-level cartographic readability and completeness | Used as sensitivity or adjudication evidence | Flags design issues beyond deterministic checks |
