#!/usr/bin/env python3
"""Run a small validator-gated iterative repair loop for choropleth scripts."""

from __future__ import annotations

import argparse
import ast
import csv
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
EXP_DIR = ROOT / "experiments/05_choropleth_reliability_benchmark"
DATA_DIR = ROOT / "data/repos/Materials-for-Creating-maps-by-Artificial-Intelligence/data_choropleth"
TASKS_PATH = EXP_DIR / "inputs/prompts_expanded.json"
SCORES_DIR = EXP_DIR / "outputs/scores"
RUN_ROOT = EXP_DIR / "outputs/runs_iterative_repair"
CODE_ROOT = EXP_DIR / "outputs/generated_code_iterative_repair"
ONE_PASS_MANIFEST = EXP_DIR / "outputs/runs/qwen2.5-coder_32b/repair_run_manifest.json"
CONDITION_SUMMARY = SCORES_DIR / "expanded_choropleth_condition_summary.csv"


DATA_PROFILE = """
The script must use only local data through these environment variables:
- CHOROPLETH_DATA_DIR
- CHOROPLETH_OUTPUT_DIR

Available files:
- MCD64.006.yearly-ba-nf.2002-2022.PRT_Portugal.csv
- mainlandburn.shp
- boundary.shp

Known columns:
- CSV: Year, Burned Area [ha], Number of Fires
- mainlandburn.shp: Burned_Are, of_Fires, geometry

Known data issues:
- mainlandburn.shp may have missing CRS. If missing, set EPSG:4326.
- boundary.shp has an invalid geometry. Use shapely.make_valid if available, otherwise buffer(0).

Rules:
- Return only executable Python code, no Markdown fences.
- Do not download data.
- Do not hard-code fake filenames or path/to/data.
- Use pathlib.Path(os.environ["CHOROPLETH_DATA_DIR"]) and pathlib.Path(os.environ["CHOROPLETH_OUTPUT_DIR"]).
- Import all modules you use.
- For GeoPandas spatial joins, use predicate=, not op=.
- If static map is required, write map_static.png.
- If interactive map is required, write map_interactive.html.
- If a time series is required, write time_series.png.
- If diagnostics are required, write diagnostics.json.
"""

DISALLOWED_IMPORTS = {"requests", "urllib", "httpx", "socket", "subprocess", "shutil"}
DISALLOWED_CALLS = {"eval", "exec", "compile", "__import__", "system", "popen", "remove", "unlink", "rmdir", "rmtree"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def load_tasks() -> dict[str, dict]:
    return {task["prompt_id"]: task for task in json.loads(TASKS_PATH.read_text(encoding="utf-8"))}


def extract_code(text: str) -> str:
    text = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", text)
    stripped = text.strip()
    if "```" not in stripped:
        return stripped + "\n"
    for part in stripped.split("```"):
        candidate = part
        if candidate.lstrip().startswith("python"):
            candidate = candidate.lstrip()[len("python") :]
        if "import " in candidate or "from " in candidate:
            return candidate.strip() + "\n"
    return stripped.replace("```python", "").replace("```", "").strip() + "\n"


def scan_file(path: Path) -> tuple[bool, str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    issues: list[str] = []
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        return False, f"syntax_error:{exc.msg}"
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in DISALLOWED_IMPORTS:
                    issues.append(f"disallowed_import:{alias.name}")
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            if root in DISALLOWED_IMPORTS:
                issues.append(f"disallowed_import:{node.module}")
        elif isinstance(node, ast.Call):
            name = ""
            if isinstance(node.func, ast.Name):
                name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                name = node.func.attr
            if name in DISALLOWED_CALLS:
                issues.append(f"disallowed_call:{name}")
    issues = sorted(set(issues))
    return not issues, ";".join(issues)


def required_artifacts(task: dict) -> list[str]:
    output_map = {
        "static_png": "map_static.png",
        "interactive_html": "map_interactive.html",
        "time_series_png": "time_series.png",
        "diagnostic_json": "diagnostics.json",
    }
    return [output_map[name] for name in task.get("required_outputs", []) if name in output_map]


def has_nonempty(run_dir: Path, filename: str) -> bool:
    path = run_dir / filename
    return path.exists() and path.stat().st_size > 0


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def score_run(meta: dict[str, object], task: dict, script_path: Path) -> dict[str, str]:
    run_dir = ROOT / str(meta["run_dir"])
    script = read_text(script_path)
    stderr = read_text(run_dir / "stderr.txt")
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
    required = ["execution_success", "uses_env_vars", "uses_known_files"]
    required.extend(name for name in task.get("required_outputs", []) if name in checks)
    if task.get("family") in {"crs_geometry", "cartographic_design", "attribute_join"}:
        required.append("mentions_crs")
    if task.get("family") == "crs_geometry":
        required.append("mentions_geometry_repair")
    required = list(dict.fromkeys(required))
    passed = sum(1 for key in required if checks.get(key, False))
    score = passed / len(required) if required else 0.0
    stderr_tail = " | ".join(stderr.strip().splitlines()[-4:])
    return {
        "score": f"{score:.3f}",
        "passed": str(passed),
        "required": str(len(required)),
        "complete": str(score >= 0.999),
        "failed_checks": ", ".join(key for key in required if not checks.get(key, False)),
        "stderr_tail": stderr_tail[:300],
        **{f"check_{key}": str(value) for key, value in sorted(checks.items())},
    }


def run_script(script_path: Path, meta: dict[str, str], iteration: int, timeout: int) -> dict[str, object]:
    run_id = f"{meta['model']}_{meta['mode']}_{meta['prompt_id']}_iter{iteration:02d}_{time.strftime('%Y%m%d_%H%M%S')}"
    run_dir = RUN_ROOT / meta["model"] / meta["mode"] / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["CHOROPLETH_DATA_DIR"] = str(DATA_DIR)
    env["CHOROPLETH_OUTPUT_DIR"] = str(run_dir)
    started = time.time()
    try:
        proc = subprocess.run([sys.executable, str(script_path)], cwd=ROOT, env=env, text=True, capture_output=True, timeout=timeout)
        returncode: int | None = proc.returncode
        stdout = proc.stdout or ""
        stderr = proc.stderr or ""
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        returncode = None
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        timed_out = True
    elapsed = time.time() - started
    (run_dir / "stdout.txt").write_text(stdout, encoding="utf-8", errors="replace")
    (run_dir / "stderr.txt").write_text(stderr, encoding="utf-8", errors="replace")
    run_meta: dict[str, object] = {
        "model": meta["model"],
        "mode": meta["mode"],
        "prompt_id": meta["prompt_id"],
        "script": str(script_path.relative_to(ROOT)),
        "run_dir": str(run_dir.relative_to(ROOT)),
        "returncode": returncode,
        "timed_out": timed_out,
        "elapsed_seconds": round(elapsed, 3),
        "created_files": sorted(str(p.relative_to(run_dir)) for p in run_dir.rglob("*") if p.is_file()),
        "repaired": True,
        "repair_iteration": iteration,
    }
    (run_dir / "metadata.json").write_text(json.dumps(run_meta, indent=2), encoding="utf-8")
    return run_meta


def call_ollama(model: str, prompt: str, timeout: int) -> str:
    payload = {"model": model, "prompt": prompt, "stream": False, "options": {"temperature": 0.0}}
    req = urllib.request.Request(
        "http://127.0.0.1:11434/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return extract_code(data.get("response", ""))


def build_prompt(task: dict, meta: dict[str, str], previous_code: str, previous_score: dict[str, str], previous_stderr: str) -> str:
    return f"""You are repairing a Python GIS mapping script using validator feedback.

{DATA_PROFILE}

Task prompt:
{task.get('prompt', '')}

Required output files:
{json.dumps(required_artifacts(task))}

Source metadata:
{json.dumps({k: meta.get(k, '') for k in ['model', 'mode', 'prompt_id', 'script', 'run_dir']}, indent=2)}

Validator score from previous attempt:
{json.dumps(previous_score, indent=2)}

Previous stderr:
```
{previous_stderr[-5000:]}
```

Previous code:
```python
{previous_code}
```

Write a corrected full Python script. Prefer a simple robust implementation over cleverness. Ensure every required output file is written to CHOROPLETH_OUTPUT_DIR.
"""


def select_cases(limit: int, offset: int) -> list[dict[str, str]]:
    if not ONE_PASS_MANIFEST.exists():
        raise FileNotFoundError(ONE_PASS_MANIFEST)
    manifest = json.loads(ONE_PASS_MANIFEST.read_text(encoding="utf-8"))
    by_key = {(row["model"], row["mode"], row["prompt_id"]): row for row in manifest}
    summary_rows = [
        row
        for row in read_csv(CONDITION_SUMMARY)
        if row["condition"] == "repair_by_qwen2.5-coder_32b" and float(row["best_score"]) < 0.999
    ]
    # Near-miss cases are most diagnostic for whether validator feedback can close the loop.
    summary_rows.sort(key=lambda row: (-float(row["best_score"]), row["model"], row["mode"], row["prompt_id"]))
    selected = []
    for row in summary_rows[offset:]:
        meta = by_key.get((row["model"], row["mode"], row["prompt_id"]))
        if meta:
            selected.append({**meta, "one_pass_score": row["best_score"], "one_pass_failed_checks": row["failed_checks_best"]})
        if len(selected) >= limit:
            break
    return selected


def write_report(rows: list[dict[str, str]], path: Path, model: str) -> None:
    final_by_case: dict[tuple[str, str, str], dict[str, str]] = {}
    for row in rows:
        key = (row["source_model"], row["mode"], row["prompt_id"])
        current = final_by_case.get(key)
        if current is None or int(row["iteration"]) > int(current["iteration"]):
            final_by_case[key] = row
    completed = sum(row["complete"] == "True" for row in final_by_case.values())
    lines = [
        "# Iterative Validator-Gated Choropleth Repair Pilot",
        "",
        f"- repair model: `{model}`",
        f"- cases: {len(final_by_case)}",
        f"- completed after iterative repair: {completed}",
        "",
        "| Source model | Mode | Prompt | Iteration | Score | Passed | Complete | Failed checks |",
        "|---|---|---|---:|---:|---:|---|---|",
    ]
    for row in sorted(final_by_case.values(), key=lambda r: (r["source_model"], r["mode"], r["prompt_id"])):
        lines.append(
            f"| {row['source_model']} | {row['mode']} | {row['prompt_id']} | {row['iteration']} | {row['score']} | {row['passed']}/{row['required']} | {row['complete']} | {row['failed_checks']} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="qwen2.5-coder:32b")
    parser.add_argument("--case-limit", type=int, default=8)
    parser.add_argument("--case-offset", type=int, default=0)
    parser.add_argument("--max-iters", type=int, default=2)
    parser.add_argument("--ollama-timeout", type=int, default=240)
    parser.add_argument("--run-timeout", type=int, default=120)
    args = parser.parse_args()

    tasks = load_tasks()
    model_slug = args.model.replace(":", "_")
    out_root = CODE_ROOT / model_slug
    out_root.mkdir(parents=True, exist_ok=True)
    out_csv = SCORES_DIR / f"iterative_validator_repair_{model_slug}.csv"
    out_json = SCORES_DIR / f"iterative_validator_repair_summary_{model_slug}.json"
    out_md = SCORES_DIR / f"iterative_validator_repair_{model_slug}.md"
    rows: list[dict[str, str]] = read_csv(out_csv) if out_csv.exists() else []
    existing_attempts = {
        (row["source_model"], row["mode"], row["prompt_id"], row["iteration"])
        for row in rows
    }
    existing_rows = {
        (row["source_model"], row["mode"], row["prompt_id"], row["iteration"]): row
        for row in rows
    }

    for meta in select_cases(args.case_limit, args.case_offset):
        task = tasks[meta["prompt_id"]]
        previous_script = ROOT / meta["script"]
        previous_run_dir = ROOT / meta["run_dir"]
        previous_code = read_text(previous_script)
        previous_stderr = read_text(previous_run_dir / "stderr.txt")
        previous_score = {
            "score": meta["one_pass_score"],
            "failed_checks": meta["one_pass_failed_checks"],
            "returncode": str(meta["returncode"]),
            "timed_out": str(meta["timed_out"]),
            "created_files": meta.get("created_files", []),
        }
        for iteration in range(1, args.max_iters + 1):
            attempt_key = (meta["model"], meta["mode"], meta["prompt_id"], str(iteration))
            if attempt_key in existing_attempts:
                print(f"cached row: {meta['model']} {meta['mode']} {meta['prompt_id']} iter={iteration}", flush=True)
                cached_row = existing_rows[attempt_key]
                if cached_row["complete"] == "True":
                    break
                cached_script = ROOT / cached_row["script"]
                previous_code = read_text(cached_script)
                cached_run_dir = cached_row.get("run_dir", "")
                previous_stderr = read_text((ROOT / cached_run_dir) / "stderr.txt") if cached_run_dir else ""
                previous_score = {
                    "score": cached_row["score"],
                    "passed": cached_row["passed"],
                    "required": cached_row["required"],
                    "complete": cached_row["complete"],
                    "failed_checks": cached_row["failed_checks"],
                    "stderr_tail": cached_row["stderr_tail"],
                }
                continue
            script_dir = out_root / meta["model"] / meta["mode"]
            script_dir.mkdir(parents=True, exist_ok=True)
            script_path = script_dir / f"{meta['prompt_id']}_{meta['mode']}_iter{iteration:02d}.py"
            if not script_path.exists():
                prompt = build_prompt(task, meta, previous_code, previous_score, previous_stderr)
                repaired_code = call_ollama(args.model, prompt, args.ollama_timeout)
                script_path.write_text(repaired_code, encoding="utf-8")
            safe, issues = scan_file(script_path)
            if not safe:
                score = {
                    "score": "0.000",
                    "passed": "0",
                    "required": "0",
                    "complete": "False",
                    "failed_checks": f"unsafe:{issues}",
                    "stderr_tail": "",
                }
                run_meta = {"run_dir": "", "returncode": "", "timed_out": "", "elapsed_seconds": "", "created_files": []}
            else:
                run_meta = run_script(script_path, meta, iteration, args.run_timeout)
                score = score_run(run_meta, task, script_path)
            row = {
                "repair_model": args.model,
                "source_model": meta["model"],
                "mode": meta["mode"],
                "prompt_id": meta["prompt_id"],
                "iteration": str(iteration),
                "script": str(script_path.relative_to(ROOT)),
                "run_dir": str(run_meta.get("run_dir", "")),
                "safe_to_run": str(safe),
                "safety_issues": issues,
                "one_pass_score": meta["one_pass_score"],
                "one_pass_failed_checks": meta["one_pass_failed_checks"],
                "returncode": str(run_meta.get("returncode", "")),
                "timed_out": str(run_meta.get("timed_out", "")),
                "created_files": ";".join(run_meta.get("created_files", [])),
                **score,
            }
            rows.append(row)
            existing_attempts.add(attempt_key)
            existing_rows[attempt_key] = row
            print(f"{meta['model']} {meta['mode']} {meta['prompt_id']} iter={iteration} score={row['score']} complete={row['complete']}", flush=True)
            if row["complete"] == "True" or not safe:
                break
            previous_code = read_text(script_path)
            previous_stderr = read_text((ROOT / str(run_meta["run_dir"])) / "stderr.txt") if run_meta.get("run_dir") else ""
            previous_score = score

    write_csv(out_csv, rows)
    final_cases = {}
    for row in rows:
        final_cases[(row["source_model"], row["mode"], row["prompt_id"])] = row
    summary = {
        "repair_model": args.model,
        "cases": len(final_cases),
        "attempt_rows": len(rows),
        "completed_cases": sum(row["complete"] == "True" for row in final_cases.values()),
        "safe_attempts": sum(row["safe_to_run"] == "True" for row in rows),
    }
    out_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_report(rows, out_md, args.model)
    print(f"Wrote {out_csv.relative_to(ROOT)}")
    print(f"Wrote {out_json.relative_to(ROOT)}")
    print(f"Wrote {out_md.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
