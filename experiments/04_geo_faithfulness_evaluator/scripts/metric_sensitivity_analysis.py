#!/usr/bin/env python3
"""Sensitivity analysis for plan reliability under alternative metric weights."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
SCORE_ROOT = ROOT / "experiments/04_geo_faithfulness_evaluator/outputs/workflow_spec_benchmark/scores"


COMPONENTS = [
    "JSON_VALID",
    "TOOL_VALID",
    "DATA_VALID",
    "FIELD_VALID",
    "CRS_PLAN",
    "SCHEMA_PLAN",
    "MAP_PLAN",
    "OUTPUT_NAME",
    "ANTI_WPHR",
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-slug", default="qwen2.5-coder_32b")
    parser.add_argument("--n-draws", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=20260620)
    args = parser.parse_args()

    rng = np.random.default_rng(args.seed)
    df = pd.read_csv(SCORE_ROOT / args.model_slug / "workflow_task_scores.csv")
    df["ANTI_WPHR"] = 1 - df["WPHR"]
    modes = ["basic", "grounded", "geoguard", "geoguard_repair", "geoguard_exec_repair"]
    modes = [m for m in modes if m in set(df["mode"])]

    rows = []
    pair_wins = {
        ("basic", "geoguard"): 0,
        ("grounded", "geoguard"): 0,
        ("geoguard", "geoguard_exec_repair"): 0,
        ("geoguard_repair", "geoguard_exec_repair"): 0,
    }
    top_counts = {m: 0 for m in modes}
    for _ in range(args.n_draws):
        weights = rng.dirichlet(np.ones(len(COMPONENTS)))
        weighted = []
        for mode in modes:
            sub = df[df["mode"] == mode]
            score = float((sub[COMPONENTS].to_numpy(dtype=float) @ weights).mean())
            weighted.append((mode, score))
        score_map = dict(weighted)
        top = max(weighted, key=lambda x: x[1])[0]
        top_counts[top] += 1
        for a, b in pair_wins:
            if a in score_map and b in score_map and score_map[b] > score_map[a]:
                pair_wins[(a, b)] += 1

    for mode in modes:
        rows.append({
            "analysis": "top_condition",
            "condition_a": "",
            "condition_b": mode,
            "probability": round(top_counts[mode] / args.n_draws, 4),
            "n_draws": args.n_draws,
            "seed": args.seed,
        })
    for (a, b), wins in pair_wins.items():
        if a in modes and b in modes:
            rows.append({
                "analysis": "pairwise_b_better_than_a",
                "condition_a": a,
                "condition_b": b,
                "probability": round(wins / args.n_draws, 4),
                "n_draws": args.n_draws,
                "seed": args.seed,
            })

    out_dir = ROOT / "experiments/04_geo_faithfulness_evaluator/outputs/workflow_metric_sensitivity" / args.model_slug
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "metric_weight_sensitivity.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(out.relative_to(ROOT))


if __name__ == "__main__":
    main()
