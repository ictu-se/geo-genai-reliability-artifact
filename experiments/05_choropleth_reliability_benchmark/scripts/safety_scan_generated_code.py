#!/usr/bin/env python3
"""Static safety scan for generated choropleth Python scripts."""

from __future__ import annotations

import argparse
import ast
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CODE_ROOT = ROOT / "experiments/05_choropleth_reliability_benchmark/outputs/generated_code"
REPAIR_ROOT = ROOT / "experiments/05_choropleth_reliability_benchmark/outputs/generated_code_repaired"
OUT_DIR = ROOT / "experiments/05_choropleth_reliability_benchmark/outputs/scores"


DISALLOWED_IMPORTS = {
    "requests",
    "urllib",
    "httpx",
    "socket",
    "subprocess",
    "shutil",
}

DISALLOWED_CALLS = {
    "eval",
    "exec",
    "compile",
    "__import__",
    "system",
    "popen",
    "remove",
    "unlink",
    "rmdir",
    "rmtree",
}


def scan_file(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    issues: list[str] = []
    if "GENERATION_FAILED" in text:
        issues.append("generation_failed")
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        return {
            "script": str(path.relative_to(ROOT)),
            "safe_to_run": "False",
            "issue_count": "1",
            "issues": f"syntax_error:{exc.msg}",
        }

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root in DISALLOWED_IMPORTS:
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
    return {
        "script": str(path.relative_to(ROOT)),
        "safe_to_run": str(not issues),
        "issue_count": str(len(issues)),
        "issues": ";".join(issues),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=None, help="Optional model name, e.g. qwen2.5-coder:7b")
    parser.add_argument("--repaired", action="store_true", help="Scan repaired generated code instead of initial generated code.")
    args = parser.parse_args()

    root = REPAIR_ROOT if args.repaired else CODE_ROOT
    if args.model:
        root = root / args.model.replace(":", "_")
    scripts = sorted(root.rglob("*.py"))
    rows = [scan_file(path) for path in scripts]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_name = "repaired_code_safety_scan.csv" if args.repaired else "generated_code_safety_scan.csv"
    out_paths = [OUT_DIR / out_name]
    if args.model:
        model_slug = args.model.replace(":", "_")
        prefix = "repaired_code_safety_scan" if args.repaired else "generated_code_safety_scan"
        out_paths.append(OUT_DIR / f"{prefix}_{model_slug}.csv")
    for out_path in out_paths:
        with out_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["script", "safe_to_run", "issue_count", "issues"])
            writer.writeheader()
            writer.writerows(rows)
    print(f"Wrote {out_path.relative_to(ROOT)}")
    print(f"scripts={len(rows)} safe={sum(row['safe_to_run'] == 'True' for row in rows)} unsafe={sum(row['safe_to_run'] != 'True' for row in rows)}")


if __name__ == "__main__":
    main()
