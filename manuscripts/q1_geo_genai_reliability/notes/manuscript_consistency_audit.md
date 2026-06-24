# Manuscript Consistency Audit

This audit checks high-risk numerical and status claims in the manuscript draft against generated tables and summaries.

| Check | Status | Evidence |
|---|---|---|
| Draft word count reflected | PASS | 12267 words |
| Full table count reflected in supplement text | PASS | 33 tables |
| Figure count remains indexed | PASS | 9 figures |
| MapGenerator exact VLM agreement claim present | PASS | 3/20 |
| MapGenerator feature agreement claim present | PASS | 73/79 |
| MapGenerator CLIP scoring claim present | PASS | 200 pairs; mean=0.342781 |
| MapGenerator CLIP summary agrees with table | PASS | summary=200; mean=0.342781 |
| Choropleth exact VLM agreement claim present | PASS | 13/18 |
| Choropleth usable/below agreement claim present | PASS | 14/18 |
| MapGenerator adjudication queue claim present | PASS | 17 of 20 |
| Choropleth adjudication queue claim present | PASS | 4 of 18 |
| Choropleth stable adjudication claim present | PASS | 10 stable/low |
| VLM judge robustness claim present | PASS | agreement=4; failed=4 |
| Cross-paradigm reliability matrix claim present | PASS | LLM-generated choropleth maps=2.14; Remote-sensing-to-map tiles=2.00; Text-to-map image data=1.29 |
| Iterative repair completion claim present | PASS | 25/40 |
| Qwen 7B/14B repair-suite claim present | PASS | 3/8; 3/8 |
| DeepSeek repair-suite claim present | PASS | 0/8 |
| Matched repair suite table populated | PASS | models=3 |
| Matched repair suite score claims present | PASS | deepseek-coder:6.7b=0.204; qwen2.5-coder:14b=0.829; qwen2.5-coder:7b=0.808 |
| Local-context ridge SSIM claim present | PASS | 0.361186 |
| Local-context ridge summary agrees with table | PASS | 0.361186 |
| Convolutional filter ridge SSIM claim present | PASS | SSIM=0.347422; edge=6.235243 |
| Convolutional filter ridge summary agrees with table | PASS | 0.347422 |
| Patch-embedding retrieval claim present | PASS | MAE=16.335779; SSIM=0.273621; edge=11.403972 |
| Patch-embedding retrieval summary agrees with table | PASS | 0.273621 |
| Tiny-CNN baseline claim present | PASS | MAE=26.100397; SSIM=0.366129; edge=9.221896 |
| Tiny-CNN summary agrees with table | PASS | 0.366129 |
| Citation verification has no unresolved rows | PASS | verified=12; resolver_verified=2; bad=[] |
| Blinded manuscript regenerated from current draft | PASS | blinded text table-count claim |
| Main/supplement split matches table and figure counts | PASS | 42 split rows |

- Automated consistency checks passed 30 of 30
