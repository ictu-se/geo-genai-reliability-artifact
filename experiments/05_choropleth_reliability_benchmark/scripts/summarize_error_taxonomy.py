#!/usr/bin/env python3
"""Summarize runtime error classes for expanded choropleth runs."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RUN_ROOT = ROOT / "experiments/05_choropleth_reliability_benchmark/outputs/runs"
OUT_DIR = ROOT / "experiments/05_choropleth_reliability_benchmark/outputs/scores"


PATTERNS = [
    ("hardcoded_path", ["path/to/data", "CHOROPLETH_DATA_DIR/", "No such file or directory"]),
    ("wrong_file_name", ["wildfires.csv", "portuguese_districts.shp", "district_boundaries.shp", "number_of_fires.csv"]),
    ("missing_import", ["NameError", "ImportError", "cannot import name", "name 'json' is not defined", "name 'os' is not defined"]),
    ("deprecated_api", ["op=", "unexpected keyword argument 'op'"]),
    ("schema_hallucination", ["KeyError", "longitude", "latitude", "district", "area", "fire_count"]),
    ("typo", ["CHORPLETH"]),
    ("geometry_crs", ["CRS", "geometry", "make_valid"]),
]


def classify(text: str) -> list[str]:
    found = []
    low = text.lower()
    for label, patterns in PATTERNS:
        if any(pattern.lower() in low for pattern in patterns):
            found.append(label)
    return found or ["other"]


def main() -> None:
    rows = []
    counts: dict[str, int] = {}
    for meta_path in sorted(RUN_ROOT.glob("*/*/*/metadata.json")):
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if meta.get("returncode") == 0 and not meta.get("timed_out"):
            continue
        stderr_path = meta_path.parent / "stderr.txt"
        stderr = stderr_path.read_text(encoding="utf-8", errors="replace") if stderr_path.exists() else ""
        labels = classify(stderr)
        for label in labels:
            counts[label] = counts.get(label, 0) + 1
        rows.append(
            {
                "run_id": meta_path.parent.name,
                "error_classes": ";".join(labels),
                "stderr_tail": " | ".join(stderr.strip().splitlines()[-4:])[:300],
            }
        )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    detail_path = OUT_DIR / "expanded_choropleth_error_taxonomy.csv"
    with detail_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["run_id", "error_classes", "stderr_tail"])
        writer.writeheader()
        writer.writerows(rows)

    summary_rows = [{"error_class": key, "runs": str(value)} for key, value in sorted(counts.items())]
    summary_path = OUT_DIR / "expanded_choropleth_error_taxonomy_summary.csv"
    with summary_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["error_class", "runs"])
        writer.writeheader()
        writer.writerows(summary_rows)

    lines = [
        "# Expanded Choropleth Error Taxonomy",
        "",
        "| Error class | Runs |",
        "|---|---:|",
    ]
    for row in summary_rows:
        lines.append(f"| {row['error_class']} | {row['runs']} |")
    (OUT_DIR / "expanded_choropleth_error_taxonomy.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {detail_path.relative_to(ROOT)}")
    print(f"Wrote {summary_path.relative_to(ROOT)}")
    print(f"Wrote {(OUT_DIR / 'expanded_choropleth_error_taxonomy.md').relative_to(ROOT)}")


if __name__ == "__main__":
    main()
