# 02 MapGenerator Image-Text Audit

This track audits whether MapGenerator captions faithfully describe their paired map images.

Data source:

- `../../data/raw/MapGenerator/MapTrain`
- `../../data/raw/MapGenerator/MGEval`

Implemented tasks:

1. Parse `descriptions.xlsx`.
2. Extract geographic entities and spatial relations from captions.
3. Verify image existence and dimensions.
4. Generate heuristic caption-quality flags.
5. Run deterministic proxy caption-fidelity review on 200 sampled pairs.
6. Produce contact sheets for flagged/proxy-mismatch examples.

Regenerate:

```bash
python3 experiments/02_mapgenerator_image_text_audit/scripts/audit_mapgenerator_pairs.py
python3 experiments/02_mapgenerator_image_text_audit/scripts/review_caption_visual_proxies.py
python3 experiments/02_mapgenerator_image_text_audit/scripts/run_clip_siglip_caption_scoring.py --local-files-only
```

The embedding scorer requires optional PyTorch/Transformers dependencies; see `../../manuscripts/q1_geo_genai_reliability/submission/environment_optional_embedding.yml`.

Current outputs:

- `outputs/mapgenerator_pairs_audit.csv`
- `outputs/mapgenerator_audit_summary.json`
- `outputs/mapgenerator_audit_report.md`
- `outputs/mapgenerator_flagged_contact_sheet.jpg`
- `outputs/mapgenerator_proxy_caption_review.csv`
- `outputs/mapgenerator_proxy_caption_review_summary.json`
- `outputs/mapgenerator_proxy_caption_review.md`
- `outputs/mapgenerator_proxy_review_contact_sheet.jpg`
- `outputs/mapgenerator_clip_caption_embedding_summary.json`
- `outputs/mapgenerator_clip_caption_embedding_scores.csv`

Remaining Q1-strengthening task:

- run the optional CLIP/SigLIP scoring layer with a local or downloadable model, then validate proxy/VLM findings with human labels or a calibrated multi-judge protocol.
