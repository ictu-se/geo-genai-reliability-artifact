#!/usr/bin/env python3
"""Bootstrap confidence intervals and paired differences for workflow scores."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
PLAN_SCORES = ROOT / "experiments/04_geo_faithfulness_evaluator/outputs/workflow_spec_benchmark/scores"
EXEC_SCORES = ROOT / "experiments/04_geo_faithfulness_evaluator/outputs/workflow_spec_execution/scores"


def ci(values: np.ndarray, rng: np.random.Generator, n_boot: int) -> tuple[float, float, float]:
    values = np.asarray(values, dtype=float)
    n = len(values)
    if n == 0:
        return 0.0, 0.0, 0.0
    idx = rng.integers(0, n, size=(n_boot, n))
    means = values[idx].mean(axis=1)
    return float(values.mean()), float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))


def paired_diff(
    df: pd.DataFrame,
    metric: str,
    mode_a: str,
    mode_b: str,
    rng: np.random.Generator,
    n_boot: int,
) -> dict:
    piv = df.pivot_table(index="task_id", columns="mode", values=metric, aggfunc="first").dropna(subset=[mode_a, mode_b])
    diff = (piv[mode_b] - piv[mode_a]).to_numpy(dtype=float)
    idx = rng.integers(0, len(diff), size=(n_boot, len(diff)))
    boots = diff[idx].mean(axis=1)
    if diff.mean() >= 0:
        p_two_sided = 2 * min(float((boots <= 0).mean()), float((boots >= 0).mean()))
    else:
        p_two_sided = 2 * min(float((boots >= 0).mean()), float((boots <= 0).mean()))
    return {
        "metric": metric,
        "mode_a": mode_a,
        "mode_b": mode_b,
        "mean_diff_b_minus_a": round(float(diff.mean()), 4),
        "ci95_low": round(float(np.quantile(boots, 0.025)), 4),
        "ci95_high": round(float(np.quantile(boots, 0.975)), 4),
        "bootstrap_p_two_sided": round(min(p_two_sided, 1.0), 4),
        "paired_tasks": len(diff),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-slug", default="qwen2.5-coder_32b")
    parser.add_argument("--n-boot", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=20260620)
    args = parser.parse_args()

    rng = np.random.default_rng(args.seed)
    plan = pd.read_csv(PLAN_SCORES / args.model_slug / "workflow_task_scores.csv")
    execution = pd.read_csv(EXEC_SCORES / args.model_slug / "execution_task_scores.csv")
    out_dir = ROOT / "experiments/04_geo_faithfulness_evaluator/outputs/workflow_stat_tests" / args.model_slug
    out_dir.mkdir(parents=True, exist_ok=True)

    ci_rows = []
    for source, df, metrics in [
        ("plan", plan, ["WPHR", "PRS", "DATA_VALID", "FIELD_VALID", "CRS_PLAN"]),
        ("execution", execution, ["ES", "artifact", "readable", "schema_ok", "nonempty"]),
    ]:
        for mode in sorted(df["mode"].unique()):
            sub = df[df["mode"] == mode]
            for metric in metrics:
                mean, low, high = ci(sub[metric].to_numpy(dtype=float), rng, args.n_boot)
                ci_rows.append({
                    "source": source,
                    "mode": mode,
                    "metric": metric,
                    "mean": round(mean, 4),
                    "ci95_low": round(low, 4),
                    "ci95_high": round(high, 4),
                    "tasks": len(sub),
                    "n_boot": args.n_boot,
                    "seed": args.seed,
                })

    comparisons = [
        ("basic", "grounded"),
        ("grounded", "geoguard"),
        ("geoguard", "geoguard_repair"),
        ("geoguard_repair", "geoguard_exec_repair"),
        ("geoguard", "geoguard_exec_repair"),
        ("basic", "geoguard"),
    ]
    diff_rows = []
    for metric in ["PRS", "WPHR"]:
        for a, b in comparisons:
            if a in set(plan["mode"]) and b in set(plan["mode"]):
                diff_rows.append({"source": "plan", **paired_diff(plan, metric, a, b, rng, args.n_boot)})
    for metric in ["ES", "schema_ok"]:
        for a, b in comparisons:
            if a in set(execution["mode"]) and b in set(execution["mode"]):
                diff_rows.append({"source": "execution", **paired_diff(execution, metric, a, b, rng, args.n_boot)})

    for name, rows in [("bootstrap_ci.csv", ci_rows), ("paired_differences.csv", diff_rows)]:
        path = out_dir / name
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
