#!/usr/bin/env python3
"""Repair weak workflow specs with validator feedback."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

from generate_ollama_workflow_specs import DATA_PROFILE, TOOL_SCHEMA, VALIDATION_RULES, ask_ollama, extract_json
from score_workflow_specs import ROOT, SCORE_ROOT, SPEC_ROOT, TASKS_PATH, score_spec


def feedback_for(score: dict) -> list[str]:
    feedback = []
    checks = [
        ("TOOL_VALID", "Use the expected operation type exactly."),
        ("DATA_VALID", "Use only dataset names from the provided data profile."),
        ("FIELD_VALID", "Use only existing fields or fields explicitly created by the selected operation."),
        ("CRS_PLAN", "Add a safe CRS strategy: projected CRS for distance/area, raster CRS alignment for raster workflows."),
        ("SCHEMA_PLAN", "Declare all required output fields."),
        ("MAP_PLAN", "For maps, include field, classes, scheme, cmap, title, legend_title, and source_note."),
        ("OUTPUT_NAME", "Use the exact required output filename."),
    ]
    for key, message in checks:
        if float(score.get(key, 0)) < 1:
            feedback.append(f"- {key}: {message} Current score={score.get(key)}.")
    return feedback


def prompt_for_repair(task: dict, spec: dict, score: dict) -> str:
    feedback = "\n".join(feedback_for(score)) or "- The spec is already valid; keep it concise."
    return f"""You are repairing a GIS workflow JSON specification.

Return only one valid JSON object. Do not include Markdown.

{DATA_PROFILE}

{TOOL_SCHEMA}

{VALIDATION_RULES}

Natural language task:
{task['prompt']}

Task id: {task['task_id']}
Expected operation type: {task['type']}
Required output filename: {task['output']}
Required output fields: {task.get('required_fields', [])}

Validator feedback:
{feedback}

Current JSON specification:
{json.dumps(spec, indent=2)}

Repair rules:
- Keep the same JSON schema.
- Fix only the fields needed to satisfy the task and validator feedback.
- Use real layer names and real field names from the data profile.
- If the task requires a derived field, declare it in output.required_fields and use a parameter name that creates it when the allowed operation supports it.
- If the task cannot be represented by one allowed operation, choose the final requested operation and reference only fields that already exist.

JSON schema:
{{
  "task_id": "...",
  "operation": "one allowed operation",
  "inputs": {{}},
  "params": {{}},
  "output": {{"filename": "...", "type": "vector|raster|png", "required_fields": []}},
  "validation": {{"crs": [], "schema": [], "geometry": [], "raster": [], "map_quality": []}},
  "rationale": "short"
}}
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="qwen2.5-coder:32b")
    parser.add_argument("--source-mode", default="geoguard")
    parser.add_argument("--target-mode", default="geoguard_repair")
    parser.add_argument("--threshold", type=float, default=0.999)
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--task-ids", nargs="*", default=None)
    args = parser.parse_args()

    model_slug = args.model.replace(":", "_")
    tasks = {t["task_id"]: t for t in json.loads(TASKS_PATH.read_text(encoding="utf-8"))}
    source_dir = SPEC_ROOT / model_slug / args.source_mode
    target_dir = SPEC_ROOT / model_slug / args.target_mode
    target_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for task_id, task in sorted(tasks.items()):
        if args.task_ids and task_id not in set(args.task_ids):
            continue
        source_path = source_dir / f"{task_id}_{args.source_mode}.json"
        target_path = target_dir / f"{task_id}_{args.target_mode}.json"
        raw_path = target_dir / f"{task_id}_{args.target_mode}.raw.txt"
        if not source_path.exists():
            continue
        score = score_spec(task, source_path)
        if score.get("PRS", 0) >= args.threshold:
            if not target_path.exists():
                target_path.write_text(source_path.read_text(encoding="utf-8"), encoding="utf-8")
            status = "copied"
        elif target_path.exists():
            status = "cached"
        else:
            spec = json.loads(source_path.read_text(encoding="utf-8"))
            try:
                raw = ask_ollama(args.model, prompt_for_repair(task, spec, score), args.timeout)
                raw_path.write_text(raw, encoding="utf-8")
                repaired = extract_json(raw)
                target_path.write_text(json.dumps(repaired, indent=2), encoding="utf-8")
                status = "repaired"
            except Exception as exc:
                raw_path.write_text(str(exc), encoding="utf-8")
                status = "failed"
        repaired_score = score_spec(task, target_path)
        rows.append({"task_id": task_id, "source_prs": score.get("PRS", 0), "target_prs": repaired_score.get("PRS", 0), "status": status})
        print(f"{status}: {task_id} {score.get('PRS', 0)} -> {repaired_score.get('PRS', 0)}", flush=True)

    out_dir = SCORE_ROOT / model_slug
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = out_dir / f"{args.target_mode}_manifest.csv"
    with manifest.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["task_id", "source_prs", "target_prs", "status"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {manifest.relative_to(ROOT)}")


if __name__ == "__main__":
    sys.path.append(str(Path(__file__).resolve().parent))
    main()
