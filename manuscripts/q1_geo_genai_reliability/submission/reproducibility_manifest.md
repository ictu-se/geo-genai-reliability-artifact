# Reproducibility Manifest

This manifest records review-package and experiment-derived artifacts with file sizes and SHA-256 checksums. It excludes raw third-party datasets, generated map directories, and bulky render folders unless represented by derived summaries.

## Summary

- manifest rows: 1014
- total manifest-tracked bytes: 7130873
- checksum algorithm: SHA-256

## Artifact Groups

| Group | Files |
|---|---:|
| choropleth_benchmark | 232 |
| choropleth_linter | 11 |
| dataset_audit | 4 |
| figures | 7 |
| geo_faithfulness | 465 |
| manuscript | 1 |
| mapgenerator_audit | 28 |
| notes | 19 |
| protocols | 3 |
| scgm_reproduction | 45 |
| scripts | 42 |
| submission | 23 |
| submission_nested | 100 |
| tables | 34 |

## Rebuild Note

Run `python3 manuscripts/q1_geo_genai_reliability/scripts/build_submission_package.py` before regenerating this manifest so derived tables, manuscript variants, and submission ledgers are current.
