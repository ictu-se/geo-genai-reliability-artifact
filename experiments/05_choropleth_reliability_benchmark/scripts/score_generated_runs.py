#!/usr/bin/env python3
"""Score generated choropleth reliability benchmark runs."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
EXP_DIR = ROOT / "experiments/05_choropleth_reliability_benchmark"
RUN_ROOT = EXP_DIR / "outputs/runs"
OUT_DIR = EXP_DIR / "outputs/scores"
TASKS_PATH = EXP_DIR / "inputs/prompts_expanded.json"


def load_tasks() -> dict[str, dict]:
    tasks = json.loads(TASKS_PATH.read_text(encoding="utf-8"))
    return {task["prompt_id"]: task for task in tasks}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def has_nonempty(run_dir: Path, filename: str) -> bool:
    path = run_dir / filename
    return path.exists() and path.stat().st_size > 0


def score_one(meta_path: Path, tasks: dict[str, dict]) -> dict[str, str]:
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    run_dir = meta_path.parent
    prompt_id = meta["prompt_id"]
    if prompt_id not in tasks and prompt_id.endswith("_repair"):
        prompt_id = prompt_id[: -len("_repair")]
    if prompt_id not in tasks and prompt_id.endswith(f"_{meta['mode']}"):
        prompt_id = prompt_id[: -len(f"_{meta['mode']}")]
    task = tasks.get(prompt_id, {})
    required_outputs = task.get("required_outputs", [])
    stdout = read(run_dir / "stdout.txt")
    stderr = read(run_dir / "stderr.txt")
    script = read(ROOT / meta["script"])
    repaired = bool(meta.get("repaired", False)) or "generated_code_repaired" in meta["script"]
    repair_model = ""
    if repaired:
        parts = Path(meta["script"]).parts
        if "generated_code_repaired" in parts:
            repair_model = parts[parts.index("generated_code_repaired") + 1]

    checks = {
        "execution_success": meta["returncode"] == 0 and not meta["timed_out"],
        "static_png": has_nonempty(run_dir, "map_static.png"),
        "interactive_html": has_nonempty(run_dir, "map_interactive.html"),
        "time_series_png": has_nonempty(run_dir, "time_series.png"),
        "diagnostic_json": has_nonempty(run_dir, "diagnostics.json"),
        "uses_env_vars": "CHOROPLETH_DATA_DIR" in script and "CHOROPLETH_OUTPUT_DIR" in script and "path/to" not in script,
        "uses_known_files": "mainlandburn.shp" in script or "MCD64.006.yearly-ba-nf.2002-2022.PRT_Portugal.csv" in script,
        "mentions_crs": "crs" in script.lower() or "EPSG:4326" in script,
        "mentions_geometry_repair": "make_valid" in script or "buffer(0)" in script,
    }
    output_map = {
        "static_png": "static_png",
        "interactive_html": "interactive_html",
        "time_series_png": "time_series_png",
        "diagnostic_json": "diagnostic_json",
    }
    required = ["execution_success", "uses_env_vars", "uses_known_files"]
    required.extend(output_map[name] for name in required_outputs if name in output_map)
    if task.get("family") in {"crs_geometry", "cartographic_design", "attribute_join"}:
        required.append("mentions_crs")
    if task.get("family") == "crs_geometry":
        required.append("mentions_geometry_repair")
    required = list(dict.fromkeys(required))
    passed = sum(1 for key in required if checks.get(key, False))
    score = passed / len(required) if required else 0.0
    error_tail = " | ".join(stderr.strip().splitlines()[-4:])
    if len(error_tail) > 240:
        error_tail = error_tail[:237] + "..."
    return {
        "model": meta["model"],
        "mode": meta["mode"],
        "prompt_id": prompt_id,
        "repaired": str(repaired),
        "repair_model": repair_model,
        "family": task.get("family", ""),
        "run_id": run_dir.name,
        "score": f"{score:.3f}",
        "passed": str(passed),
        "required": str(len(required)),
        "failed_checks": ", ".join(key for key in required if not checks.get(key, False)),
        "returncode": str(meta["returncode"]),
        "timed_out": str(meta["timed_out"]),
        "stderr_tail": error_tail,
        **{f"check_{key}": str(value) for key, value in sorted(checks.items())},
    }


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        return
    fields = sorted({key for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    lines = [
        "# Expanded Choropleth Benchmark Scores",
        "",
        f"Total runs: {len(rows)}",
        "",
        "| Model | Mode | Prompt | Score | Passed | Failed checks | Error tail |",
        "|---|---|---|---:|---:|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['model']} {'repair' if row['repaired'] == 'True' else 'initial'} | {row['mode']} | {row['prompt_id']} | {row['score']} | {row['passed']}/{row['required']} | {row['failed_checks']} | {row['stderr_tail'].replace('|', '/')} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tasks = load_tasks()
    rows = [score_one(path, tasks) for path in sorted(RUN_ROOT.glob("*/*/*/metadata.json"))]
    rows.sort(key=lambda row: (row["model"], row["mode"], row["prompt_id"], row["run_id"]))
    csv_path = OUT_DIR / "expanded_choropleth_benchmark_scores.csv"
    md_path = OUT_DIR / "expanded_choropleth_benchmark_scores.md"
    write_csv(csv_path, rows)
    write_markdown(md_path, rows)
    write_csv(OUT_DIR / "expanded_choropleth_pilot_scores.csv", rows)
    write_markdown(OUT_DIR / "expanded_choropleth_pilot_scores.md", rows)
    print(f"Wrote {csv_path.relative_to(ROOT)}")
    print(f"Wrote {md_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
