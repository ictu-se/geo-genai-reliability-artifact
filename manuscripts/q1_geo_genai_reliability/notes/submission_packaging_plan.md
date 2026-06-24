# Submission Packaging Plan

This note separates the current evidence package into a likely main-text set and a supplementary set for a Q1-style submission. The current workspace intentionally has more tables than a paper should print.

## Main Text Tables

1. Table 1. Local Geo-GenAI artifact inventory.
2. Table 2. Reproducibility matrix.
3. Table 5c. SCGM generated-output baseline comparison.
4. Table 11. Cross-paradigm metric taxonomy.
5. Table 13. Choropleth benchmark model-mode aggregate.
6. Table 16. Screenshot-level choropleth artifact QA.
7. Table 19. Iterative validator-gated choropleth repair sweep.

## Main Text Figures

1. Figure 1. Cross-paradigm artifact chain.
2. Figure 2. Dataset inventory.
3. Figure 5. Choropleth benchmark score bars.
4. Figure 7. Screenshot-level QA bar chart.
5. Figure 9. SCGM generated-output baseline comparison.

## Supplementary Tables

- Table 3. MapGenerator caption audit.
- Table 4. SCGM split and cascade-reference coverage.
- Table 5. SCGM edge-continuity baseline.
- Table 5b. SCGM lightweight retrieval baseline.
- Table 6. Choropleth data and artifact QA.
- Table 7. Seed LLM choropleth candidates.
- Table 8. Literature claim vs local artifact availability.
- Table 9. MapGenerator proxy caption-fidelity review.
- Table 10. Expanded choropleth condition summary.
- Table 12. Deterministic choropleth reference baseline.
- Table 14. Rendered artifact QA summary.
- Table 15. MapGenerator VLM caption-fidelity pilot.
- Table 15b. MapGenerator two-VLM caption agreement pilot.
- Table 17. Geo-GenAI map-generation literature taxonomy.
- Table 18. Choropleth VLM cartographic-quality pilot.
- Table 18b. Choropleth two-VLM cartographic-quality agreement pilot.
- Table 20. Iterative repair model comparison pilot.

## Supplementary Figures and Artifacts

- MapGenerator proxy contact sheet.
- SCGM retrieval, learned-forest, compact-MLP, and local-context contact sheets.
- Screenshot QA contact sheet.
- Full generated-code safety scans.
- Full run manifests, stderr logs, and metadata JSON.
- VLM review CSVs and prompts.
- Paired VLM agreement tables and calibration notes.
- Reproducibility release plan specifying public, source-linked, and restricted artifacts.

## Main-Text Narrative Allocation

- Introduction and contribution: 2.5-3 pages.
- Related work: 4-5 pages.
- Conceptual framework: 3 pages.
- Data and methods: 5-6 pages.
- Results: 8-10 pages.
- Discussion, limitations, conclusion: 6-7 pages.

At standard manuscript density, the current 10,800+ word draft is near the 30-page target only if most evidence tables remain in the supplement. See `notes/page_budget_audit.md` and `submission/main_supplement_split.csv` for the generated display split and compression plan. A polished 30-page submission should prioritize citation detail, tighter figure/table captions, and journal-specific formatting rather than adding more raw tables to the main text.

## selected journal-Oriented Package

Primary package: double-anonymized selected journal main manuscript plus supplement.

Submission target note: see `notes/ijgis_submission_target_pack.md`.

For the selected journal `Critical Challenges in GeoAI` special issue path, the main manuscript should foreground the cross-paradigm evaluation framework and use the experiments as evidence for a broader artifact-validity problem in GeoAI. The 01 August 2026 abstract deadline and 01 December 2026 full manuscript deadline make the next near-term deliverable a short, sharp abstract rather than another table expansion.

Keep Table 5c in the main text because the learned SCGM forest, compact neural MLP, and local-context ridge baselines add fitted generated-output diagnostics beyond retrieval-only baselines. The table should be interpreted together with Figure 9: higher SSIM and edge continuity do not by themselves establish cartographic validity when learned outputs are smoothed, noisy, or lose fine map features.

Keep Table 20 as supplementary sensitivity evidence unless the repair-model comparison is expanded to a matched full-case design. The current Qwen 7B and 14B pilots are useful because each shows 3/8 near-miss completions with 14/14 safe attempts; the DeepSeek 6.7B pilot is useful as a negative contrast with 0/8 completions and 4/10 safe attempts. These pilots should not be presented as a full model ranking against the 32B full sweep.

## Reproducibility Release

Use `submission/reproducibility_release_plan.md` as the operational data/code availability plan. The release should publish scripts, derived CSV/JSON summaries, prompts, safety scans, manifests, figures, and contact sheets created by this study, while source-linking raw third-party datasets and upstream repositories unless redistribution is explicitly permitted. The final repository or DOI archive should include a minimal environment file and a `DATA_SOURCES.md` note for every excluded raw dataset.
