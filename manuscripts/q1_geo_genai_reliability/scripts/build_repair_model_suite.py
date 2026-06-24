#!/usr/bin/env python3
"""Build a matched repair-model suite ledger from iterative repair outputs."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MS_DIR = ROOT / "manuscripts/q1_geo_genai_reliability"
SCORES_DIR = ROOT / "experiments/05_choropleth_reliability_benchmark/outputs/scores"
OUT_DIR = MS_DIR / "submission/repair_model_suite"

REPAIR_MODELS = [
    ("qwen2.5-coder:14b", SCORES_DIR / "iterative_validator_repair_qwen2.5-coder_14b.csv"),
    ("qwen2.5-coder:7b", SCORES_DIR / "iterative_validator_repair_qwen2.5-coder_7b.csv"),
    ("deepseek-coder:6.7b", SCORES_DIR / "iterative_validator_repair_deepseek-coder_6.7b.csv"),
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def case_key(row: dict[str, str]) -> tuple[str, str, str]:
    return (row["source_model"], row["mode"], row["prompt_id"])


def case_id(key: tuple[str, str, str]) -> str:
    return "__".join(key)


def final_rows(rows: list[dict[str, str]]) -> dict[tuple[str, str, str], dict[str, str]]:
    finals: dict[tuple[str, str, str], dict[str, str]] = {}
    for row in rows:
        key = case_key(row)
        current = finals.get(key)
        if current is None or int(row["iteration"]) > int(current["iteration"]):
            finals[key] = row
    return finals


def normalize_failed_checks(value: str) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def build() -> tuple[list[dict[str, str]], list[dict[str, str]], str]:
    per_model_rows = {label: read_csv(path) for label, path in REPAIR_MODELS}
    per_model_final = {label: final_rows(rows) for label, rows in per_model_rows.items()}
    matched_cases = sorted(set.intersection(*(set(rows) for rows in per_model_final.values())))

    ledger: list[dict[str, str]] = []
    for key in matched_cases:
        for label, rows in per_model_final.items():
            row = rows[key]
            attempts = [item for item in per_model_rows[label] if case_key(item) == key]
            safe_attempts = sum(item["safe_to_run"] == "True" for item in attempts)
            best_score = max(float(item["score"]) for item in attempts)
            first_complete = next((item["iteration"] for item in attempts if item["complete"] == "True"), "")
            ledger.append(
                {
                    "Case id": case_id(key),
                    "Source model": key[0],
                    "Mode": key[1],
                    "Prompt": key[2],
                    "Repair model": label,
                    "Attempts": str(len(attempts)),
                    "Safe attempts": str(safe_attempts),
                    "One-pass score": row["one_pass_score"],
                    "Final iteration": row["iteration"],
                    "Final score": row["score"],
                    "Best score": f"{best_score:.3f}",
                    "Complete": row["complete"],
                    "First complete iteration": first_complete,
                    "Failed checks": row["failed_checks"],
                    "Safety issues": "; ".join(sorted({item["safety_issues"] for item in attempts if item["safety_issues"]})),
                }
            )

    summary: list[dict[str, str]] = []
    for label, rows in per_model_rows.items():
        finals = per_model_final[label]
        matched_final_rows = [finals[key] for key in matched_cases]
        attempts = [row for row in rows if case_key(row) in matched_cases]
        completed = [row for row in matched_final_rows if row["complete"] == "True"]
        final_scores = [float(row["score"]) for row in matched_final_rows]
        best_scores_by_case = []
        for key in matched_cases:
            case_attempts = [row for row in attempts if case_key(row) == key]
            best_scores_by_case.append(max(float(row["score"]) for row in case_attempts))
        failed_counter: Counter[str] = Counter()
        unsafe = 0
        for row in attempts:
            if row["safe_to_run"] != "True":
                unsafe += 1
                failed_counter.update(normalize_failed_checks(row["failed_checks"]) or ["unsafe"])
            else:
                failed_counter.update(normalize_failed_checks(row["failed_checks"]))
        completed_by_iter = Counter(row["iteration"] for row in completed)
        summary.append(
            {
                "Repair model": label,
                "Matched cases": str(len(matched_cases)),
                "Attempt rows": str(len(attempts)),
                "Safe attempts": str(sum(row["safe_to_run"] == "True" for row in attempts)),
                "Unsafe attempts": str(unsafe),
                "Completed cases": str(len(completed)),
                "Completion rate": f"{len(completed)}/{len(matched_cases)}",
                "Mean final score": f"{sum(final_scores) / len(final_scores):.3f}",
                "Mean best score": f"{sum(best_scores_by_case) / len(best_scores_by_case):.3f}",
                "Completed by iteration": "; ".join(f"iter {k}: {v}" for k, v in sorted(completed_by_iter.items())) or "none",
                "Top remaining failed checks": "; ".join(f"{k}: {v}" for k, v in failed_counter.most_common(4)) or "none",
            }
        )

    by_case: list[str] = []
    ledger_by_case: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in ledger:
        ledger_by_case[row["Case id"]].append(row)
    for cid in sorted(ledger_by_case):
        rows = ledger_by_case[cid]
        complete_models = [row["Repair model"] for row in rows if row["Complete"] == "True"]
        scores = ", ".join(f"{row['Repair model']}={row['Final score']}" for row in rows)
        by_case.append(f"- `{cid}`: completed by {', '.join(complete_models) if complete_models else 'none'}; final scores {scores}.")

    report = "\n".join(
        [
            "# Matched Repair-Model Suite",
            "",
            "This suite compares three smaller repair models on the same eight near-miss iterative-repair cases. It complements the qwen2.5-coder:32b full 40-case sweep by isolating model-size/model-family sensitivity on a matched subset.",
            "",
            "## Summary",
            "",
            "| Repair model | Matched cases | Attempt rows | Safe attempts | Completed cases | Completion rate | Mean final score | Mean best score | Completed by iteration |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---|",
            *[
                f"| {row['Repair model']} | {row['Matched cases']} | {row['Attempt rows']} | {row['Safe attempts']} | {row['Completed cases']} | {row['Completion rate']} | {row['Mean final score']} | {row['Mean best score']} | {row['Completed by iteration']} |"
                for row in summary
            ],
            "",
            "## Case-Level Pattern",
            "",
            *by_case,
            "",
            "## Interpretation",
            "",
            "- qwen2.5-coder:7b and qwen2.5-coder:14b complete the same number of matched near-miss cases, but their final scores and completion iteration expose case-specific repair sensitivity.",
            "- deepseek-coder:6.7b produces unsafe syntax-failing attempts on several cases and completes no matched cases in this suite.",
            "- The matched subset is deliberately smaller than the 40-case qwen2.5-coder:32b sweep; it should be reported as model-sensitivity evidence, not as a full benchmark ranking.",
            "",
        ]
    )
    return summary, ledger, report


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary, ledger, report = build()
    write_csv(OUT_DIR / "matched_repair_model_summary.csv", summary)
    write_csv(OUT_DIR / "matched_repair_case_ledger.csv", ledger)
    (OUT_DIR / "matched_repair_model_suite.md").write_text(report, encoding="utf-8")
    print(f"Wrote matched repair-model suite to {OUT_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
