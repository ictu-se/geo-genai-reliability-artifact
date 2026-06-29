#!/usr/bin/env python3
"""Build long LaTeX appendix tables from the full workflow benchmark."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
EXP = ROOT / "experiments/07_grounded_gis_workflow_benchmark"
MANUSCRIPT = ROOT / "manuscripts/04_q1_grounded_gis_workflow_benchmark"
LATEX_TABLES = MANUSCRIPT / "submission/latex/tables"

TASKS_JSON = EXP / "inputs/workflow_tasks_30.json"
SCORES = EXP / "outputs/scores"
CATEGORY_MODEL_MODE = MANUSCRIPT / "tables/full_category_model_mode_summary.csv"

MODE_ORDER = {"basic": 0, "grounded": 1, "geoguard": 2}
FAMILY_ORDER = {
    "buffer_service_area": 0,
    "overlay_intersection": 1,
    "point_count_join": 2,
    "raster_clip": 3,
    "zonal_statistics": 4,
    "choropleth_export": 5,
}


def tex_escape(value: object) -> str:
    text = str(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def family_label(task_type: str) -> str:
    labels = {
        "buffer_service_area": "Buffer",
        "overlay_intersection": "Overlay",
        "point_count_join": "Point count",
        "raster_clip": "Raster",
        "zonal_statistics": "Zonal",
        "choropleth_export": "Choropleth",
    }
    return labels.get(task_type, task_type.replace("_", " ").title())


def fmt(value: object) -> str:
    try:
        return f"{float(value):.3f}"
    except (TypeError, ValueError):
        return str(value)


def load_task_lookup() -> dict[str, dict[str, object]]:
    with TASKS_JSON.open(encoding="utf-8") as f:
        tasks = json.load(f)
    return {task["task_id"]: task for task in tasks}


def write_task_suite() -> None:
    tasks = load_task_lookup().values()
    path = LATEX_TABLES / "task_suite_longtable.tex"
    lines = [
        r"\begin{longtable}{p{0.08\linewidth}p{0.18\linewidth}p{0.28\linewidth}p{0.34\linewidth}}",
        r"\caption{Complete 30-task workflow-specification suite.}\label{tab:task-suite-long}\\",
        r"\toprule",
        r"Task & Family & Required fields & Output artifact \\",
        r"\midrule",
        r"\endfirsthead",
        r"\toprule",
        r"Task & Family & Required fields & Output artifact \\",
        r"\midrule",
        r"\endhead",
    ]
    for task in tasks:
        fields = ", ".join(task.get("required_fields", [])) or "None"
        lines.append(
            " & ".join(
                [
                    tex_escape(task["task_id"]),
                    tex_escape(family_label(task["type"])),
                    tex_escape(fields),
                    tex_escape(task["output"]),
                ]
            )
            + r" \\"
        )
    lines.extend([r"\bottomrule", r"\end{longtable}", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def read_task_score_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in sorted(SCORES.glob("*/workflow_task_scores.csv")):
        with path.open(newline="", encoding="utf-8") as f:
            rows.extend(csv.DictReader(f))
    return rows


def write_task_mode_summary() -> None:
    task_lookup = load_task_lookup()
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in read_task_score_rows():
        grouped[(row["task_id"], row["mode"])].append(row)

    path = LATEX_TABLES / "task_mode_summary_longtable.tex"
    lines = [
        r"\begin{longtable}{p{0.08\linewidth}p{0.15\linewidth}p{0.12\linewidth}rrrrrr}",
        r"\caption{Task-by-mode mean scores across the twelve local models.}\label{tab:task-mode-long}\\",
        r"\toprule",
        r"Task & Family & Mode & JSON & Data & Field & CRS & WPHR & PRS \\",
        r"\midrule",
        r"\endfirsthead",
        r"\toprule",
        r"Task & Family & Mode & JSON & Data & Field & CRS & WPHR & PRS \\",
        r"\midrule",
        r"\endhead",
    ]

    for task_id in sorted(task_lookup):
        for mode in sorted(MODE_ORDER, key=MODE_ORDER.get):
            rows = grouped[(task_id, mode)]
            if not rows:
                continue
            means = {
                key: sum(float(row[key]) for row in rows) / len(rows)
                for key in ["JSON_VALID", "DATA_VALID", "FIELD_VALID", "CRS_PLAN", "WPHR", "PRS"]
            }
            lines.append(
                " & ".join(
                    [
                        tex_escape(task_id),
                        tex_escape(family_label(task_lookup[task_id]["type"])),
                        tex_escape(mode.title()),
                        fmt(means["JSON_VALID"]),
                        fmt(means["DATA_VALID"]),
                        fmt(means["FIELD_VALID"]),
                        fmt(means["CRS_PLAN"]),
                        fmt(means["WPHR"]),
                        fmt(means["PRS"]),
                    ]
                )
                + r" \\"
            )
    lines.extend([r"\bottomrule", r"\end{longtable}", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def write_task_prs_matrix() -> None:
    task_lookup = load_task_lookup()
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in read_task_score_rows():
        grouped[(row["task_id"], row["mode"])].append(row)

    path = LATEX_TABLES / "task_prs_matrix_table.tex"
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Compact task-level PRS matrix across prompting modes. Each cell averages twelve local models.}",
        r"\label{tab:task-prs-matrix}",
        r"\small",
        r"\setlength{\tabcolsep}{4pt}",
        r"\begin{tabular}{llrrrr}",
        r"\toprule",
        r"Task & Family & Basic & Grounded & GeoGuard & Gain \\",
        r"\midrule",
    ]
    for task_id in sorted(task_lookup):
        scores = {}
        for mode in MODE_ORDER:
            rows = grouped[(task_id, mode)]
            scores[mode] = sum(float(row["PRS"]) for row in rows) / len(rows)
        lines.append(
            " & ".join(
                [
                    tex_escape(task_id),
                    tex_escape(family_label(task_lookup[task_id]["type"])),
                    fmt(scores["basic"]),
                    fmt(scores["grounded"]),
                    fmt(scores["geoguard"]),
                    fmt(scores["geoguard"] - scores["basic"]),
                ]
            )
            + r" \\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table}", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def write_category_model_mode() -> None:
    with CATEGORY_MODEL_MODE.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    rows.sort(key=lambda r: (r["task_type"], r["model"], MODE_ORDER.get(r["mode"], 99)))

    path = LATEX_TABLES / "category_model_mode_prs_longtable.tex"
    lines = [
        r"\begin{longtable}{p{0.16\linewidth}p{0.24\linewidth}p{0.12\linewidth}rrrrrr}",
        r"\caption{Category-by-model-by-mode full-run reliability scores.}\label{tab:category-model-mode-long}\\",
        r"\toprule",
        r"Family & Model & Mode & JSON & Data & Field & CRS & WPHR & PRS \\",
        r"\midrule",
        r"\endfirsthead",
        r"\toprule",
        r"Family & Model & Mode & JSON & Data & Field & CRS & WPHR & PRS \\",
        r"\midrule",
        r"\endhead",
    ]
    for row in rows:
        lines.append(
            " & ".join(
                [
                    tex_escape(family_label(row["task_type"])),
                    tex_escape(row["model"]),
                    tex_escape(row["mode"].title()),
                    fmt(row["JSON_VALID"]),
                    fmt(row["DATA_VALID"]),
                    fmt(row["FIELD_VALID"]),
                    fmt(row["CRS_PLAN"]),
                    fmt(row["WPHR"]),
                    fmt(row["PRS"]),
                ]
            )
            + r" \\"
        )
    lines.extend([r"\bottomrule", r"\end{longtable}", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def write_geoguard_model_family_matrix() -> None:
    with CATEGORY_MODEL_MODE.open(newline="", encoding="utf-8") as f:
        rows = [row for row in csv.DictReader(f) if row["mode"] == "geoguard"]

    by_model: dict[str, dict[str, float]] = defaultdict(dict)
    for row in rows:
        by_model[row["model"]][row["task_type"]] = float(row["PRS"])

    family_keys = sorted(FAMILY_ORDER, key=FAMILY_ORDER.get)
    path = LATEX_TABLES / "geoguard_model_family_matrix_table.tex"
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Compact GeoGuard PRS matrix by model and GIS task family.}",
        r"\label{tab:geoguard-model-family-matrix}",
        r"\small",
        r"\setlength{\tabcolsep}{3pt}",
        r"\begin{tabular}{lrrrrrrr}",
        r"\toprule",
        r"Model & Buffer & Overlay & Points & Raster & Zonal & Choro. & Mean \\",
        r"\midrule",
    ]
    for model in sorted(by_model):
        values = [by_model[model].get(key, 0.0) for key in family_keys]
        lines.append(
            " & ".join(
                [tex_escape(model)]
                + [fmt(value) for value in values]
                + [fmt(sum(values) / len(values))]
            )
            + r" \\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table}", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def write_geoguard_hard_cases() -> None:
    task_lookup = load_task_lookup()
    rows = [
        row
        for row in read_task_score_rows()
        if row["mode"] == "geoguard" and float(row["JSON_VALID"]) == 1.0
    ]
    rows.sort(key=lambda r: (float(r["PRS"]), r["task_id"], r["model"]))
    hard_rows = rows[:18]

    path = LATEX_TABLES / "geoguard_hard_cases_table.tex"
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Lowest-scoring GeoGuard cases after excluding malformed JSON responses. This table focuses on geospatial planning weaknesses rather than format-compliance failures; the complete 360-row GeoGuard ledger remains in the repository CSV files.}",
        r"\label{tab:geoguard-hard-cases}",
        r"\small",
        r"\setlength{\tabcolsep}{2pt}",
        r"\begin{tabular}{lllrrrrrrr}",
        r"\toprule",
        r"Task & Family & Model & Tool & Data & Field & CRS & Map & Output & PRS \\",
        r"\midrule",
    ]
    for row in hard_rows:
        task = task_lookup[row["task_id"]]
        lines.append(
            " & ".join(
                [
                    tex_escape(row["task_id"]),
                    tex_escape(family_label(task["type"])),
                    tex_escape(row["model"]),
                    fmt(row["TOOL_VALID"]),
                    fmt(row["DATA_VALID"]),
                    fmt(row["FIELD_VALID"]),
                    fmt(row["CRS_PLAN"]),
                    fmt(row["MAP_PLAN"]),
                    fmt(row["OUTPUT_NAME"]),
                    fmt(row["PRS"]),
                ]
            )
            + r" \\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table}", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def write_geoguard_task_model_scores() -> None:
    task_lookup = load_task_lookup()
    rows = [row for row in read_task_score_rows() if row["mode"] == "geoguard"]
    rows.sort(key=lambda r: (r["task_id"], r["model"]))

    path = LATEX_TABLES / "geoguard_task_model_scores_longtable.tex"
    lines = [
        r"\small",
        r"\begin{longtable}{p{0.08\linewidth}p{0.16\linewidth}p{0.27\linewidth}rrrrr}",
        r"\caption{GeoGuard task-by-model scores for the full 30-task panel.}\label{tab:geoguard-task-model-long}\\",
        r"\toprule",
        r"Task & Family & Model & JSON & Data & Field & CRS & PRS \\",
        r"\midrule",
        r"\endfirsthead",
        r"\toprule",
        r"Task & Family & Model & JSON & Data & Field & CRS & PRS \\",
        r"\midrule",
        r"\endhead",
    ]
    for row in rows:
        task = task_lookup[row["task_id"]]
        lines.append(
            " & ".join(
                [
                    tex_escape(row["task_id"]),
                    tex_escape(family_label(task["type"])),
                    tex_escape(row["model"]),
                    fmt(row["JSON_VALID"]),
                    fmt(row["DATA_VALID"]),
                    fmt(row["FIELD_VALID"]),
                    fmt(row["CRS_PLAN"]),
                    fmt(row["PRS"]),
                ]
            )
            + r" \\"
        )
    lines.extend([r"\bottomrule", r"\end{longtable}", r"\normalsize", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    LATEX_TABLES.mkdir(parents=True, exist_ok=True)
    write_task_suite()
    write_task_mode_summary()
    write_task_prs_matrix()
    write_category_model_mode()
    write_geoguard_model_family_matrix()
    write_geoguard_hard_cases()
    write_geoguard_task_model_scores()
    for path in sorted(LATEX_TABLES.glob("*.tex")):
        print(f"Wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
