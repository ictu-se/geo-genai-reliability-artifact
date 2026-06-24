#!/usr/bin/env python3
"""Probe local feasibility of an official SCGM reproduction without running it."""

from __future__ import annotations

import ast
import csv
import importlib.util
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MS_DIR = ROOT / "manuscripts/q1_geo_genai_reliability"
OUT_DIR = MS_DIR / "submission/scgm_official_reproduction_audit"
SCGM_REPO = ROOT / "data/repos/SCGM"
LOCAL_DATA = ROOT / "data/raw/SCGM/extracted/TMGN_1814"
SCGM_OUTPUTS = ROOT / "experiments/03_scgm_subset_reproduction/outputs"
LOCAL_OVERRIDE_DIR = MS_DIR / "submission/scgm_official_reproduction_contract/local_overrides"


ENTRYPOINTS = [
    SCGM_REPO / "inference_refmap_batch_level.py",
    SCGM_REPO / "train.py",
    SCGM_REPO / "validate.py",
]
OFFICIAL_RUNS = [
    {
        "label": "2c_oz",
        "top_config": SCGM_REPO / "configs/test_refmap_level_2c_oz.yaml",
        "data_config": SCGM_REPO / "configs/datasetcfg/reference_map_test_level_2c_oz.yaml",
        "local_data_config": LOCAL_OVERRIDE_DIR / "reference_map_test_level_2c_oz_local.yaml",
        "planned_output": SCGM_OUTPUTS / "scgm_official_2c_oz_val",
    },
    {
        "label": "4c_oz",
        "top_config": SCGM_REPO / "configs/test_refmap_level_4c_oz.yaml",
        "data_config": SCGM_REPO / "configs/datasetcfg/reference_map_test_level_4c_oz.yaml",
        "local_data_config": LOCAL_OVERRIDE_DIR / "reference_map_test_level_4c_oz_local.yaml",
        "planned_output": SCGM_OUTPUTS / "scgm_official_4c_oz_val",
    },
]
IMPORT_PACKAGE_NAMES = {
    "cv2": "opencv-python",
    "PIL": "Pillow",
    "skimage": "scikit-image",
    "cleanfid": "clean-fid",
}
LOCAL_IMPORT_ROOTS = {"ldm", "utils", "dataloader", "model"}
STDLIB_IMPORT_ROOTS = set(getattr(sys, "stdlib_module_names", ())) | {
    "argparse",
    "collections",
    "copy",
    "csv",
    "functools",
    "glob",
    "itertools",
    "json",
    "math",
    "os",
    "pathlib",
    "random",
    "re",
    "shutil",
    "sys",
    "time",
    "typing",
    "warnings",
}


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def yaml_value(text: str, key: str) -> str:
    match = re.search(rf"^\s*{re.escape(key)}:\s*(.+?)\s*$", text, flags=re.M)
    return match.group(1).strip().strip("'\"") if match else ""


def imported_roots(path: Path) -> set[str]:
    roots: set[str] = set()
    if not path.exists():
        return roots
    tree = ast.parse(read_text(path), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            if node.level == 0:
                roots.add(node.module.split(".")[0])
    return roots


def spec_exists(module: str) -> bool:
    return importlib.util.find_spec(module) is not None


def checkpoint_reference(top_config: Path) -> str:
    return yaml_value(read_text(top_config), "resume")


def data_config_values(data_config: Path) -> dict[str, str]:
    content = read_text(data_config)
    return {
        "dataroot": yaml_value(content, "dataroot"),
        "datalist": yaml_value(content, "datalist"),
        "cascade_path": yaml_value(content, "cascade_path"),
        "scale": yaml_value(content, "scale"),
        "batch_size": yaml_value(content, "batch_size"),
    }


def status(ok: bool, warn: bool = False) -> str:
    if ok and not warn:
        return "pass"
    if ok and warn:
        return "warning"
    return "blocking_gap"


def build_rows() -> list[dict[str, str]]:
    if str(SCGM_REPO) not in sys.path:
        sys.path.insert(0, str(SCGM_REPO))

    rows: list[dict[str, str]] = []
    entry_imports: set[str] = set()
    for path in ENTRYPOINTS:
        entry_imports |= imported_roots(path)
    external_imports = sorted(root for root in entry_imports if root not in LOCAL_IMPORT_ROOTS and root not in STDLIB_IMPORT_ROOTS)
    missing_imports = [root for root in external_imports if not spec_exists(root)]
    present_imports = [root for root in external_imports if spec_exists(root)]
    local_missing = [root for root in sorted(LOCAL_IMPORT_ROOTS & entry_imports) if not spec_exists(root)]
    rows.append(
        {
            "check_id": "runtime_imports",
            "layer": "runtime",
            "status": status(not missing_imports and not local_missing),
            "evidence": f"present={','.join(present_imports) or 'none'}; missing={','.join(missing_imports + local_missing) or 'none'}",
            "next_action": "Install the drafted SCGM runtime environment before any official inference claim.",
        }
    )
    rows.append(
        {
            "check_id": "entrypoints_present",
            "layer": "code",
            "status": status(all(path.exists() for path in ENTRYPOINTS)),
            "evidence": "; ".join(f"{rel(path)}={path.exists()}" for path in ENTRYPOINTS),
            "next_action": "Use these entry points only after checkpoint and config-path blockers are resolved.",
        }
    )

    subset_rows = read_csv(SCGM_OUTPUTS / "scgm_complete_reference_subset_val_first200.csv")
    subset_ready = bool(subset_rows) and all(
        row.get("has_ref_scale_2") == "True" and row.get("has_ref_scale_4") == "True" for row in subset_rows
    )
    rows.append(
        {
            "check_id": "complete_reference_subset",
            "layer": "data",
            "status": status(subset_ready),
            "evidence": f"rows={len(subset_rows)}; all_ref2_ref4={subset_ready}",
            "next_action": "Use this subset as the controlled validation target for future official/cascade inference.",
        }
    )

    local_tilelists = sorted(path.name for path in (LOCAL_DATA / "val").glob("tilelist*.csv")) if (LOCAL_DATA / "val").exists() else []
    for run in OFFICIAL_RUNS:
        label = run["label"]
        ckpt_ref = checkpoint_reference(run["top_config"])
        ckpt_path = SCGM_REPO / ckpt_ref if ckpt_ref else SCGM_REPO / "__missing__"
        effective_data_config = run["local_data_config"] if run["local_data_config"].exists() else run["data_config"]
        values = data_config_values(effective_data_config)
        official_root = SCGM_REPO / values.get("dataroot", "")
        local_root = LOCAL_DATA / "val"
        datalist_name = values.get("datalist", "")
        official_datalist = official_root / datalist_name
        local_datalist = local_root / datalist_name
        cascade_path = SCGM_REPO / values.get("cascade_path", "")
        planned_output = run["planned_output"]
        rows.extend(
            [
                {
                    "check_id": f"{label}_top_config",
                    "layer": "config",
                    "status": status(run["top_config"].exists() and run["data_config"].exists() and effective_data_config.exists()),
                    "evidence": f"top_config={rel(run['top_config'])}; official_data_config={rel(run['data_config'])}; effective_data_config={rel(effective_data_config)}",
                    "next_action": "Freeze these configs or write a tracked local override before official inference.",
                },
                {
                    "check_id": f"{label}_checkpoint",
                    "layer": "checkpoint",
                    "status": status(ckpt_path.exists()),
                    "evidence": f"checkpoint_reference={ckpt_ref or 'missing'}; local_exists={ckpt_path.exists()}",
                    "next_action": "Obtain the referenced official checkpoint or document a training path before claiming reproduction.",
                },
                {
                    "check_id": f"{label}_dataroot",
                    "layer": "data",
                    "status": status(official_root.exists() or local_root.exists(), warn=not official_root.exists() and effective_data_config == run["data_config"]),
                    "evidence": f"official_dataroot_exists={official_root.exists()}; local_val_root_exists={local_root.exists()}; official={values.get('dataroot', '')}; local={rel(local_root)}",
                    "next_action": "Use the tracked local data-config override from the official dataroot to the local CSCMG bridge.",
                },
                {
                    "check_id": f"{label}_datalist",
                    "layer": "data",
                    "status": status(official_datalist.exists() or local_datalist.exists()),
                    "evidence": f"datalist={datalist_name}; official_exists={official_datalist.exists()}; local_exists={local_datalist.exists()}; available_local_tilelists={','.join(local_tilelists) or 'none'}",
                    "next_action": "Use the tracked local datalist override; regenerate it from the complete-reference subset if the subset changes.",
                },
                {
                    "check_id": f"{label}_cascade_path",
                    "layer": "data",
                    "status": status(cascade_path.exists()),
                    "evidence": f"cascade_path={values.get('cascade_path', '')}; local_exists={cascade_path.exists()}",
                    "next_action": "Populate cascade-path samples or configure inference to write/read cascade outputs deterministically.",
                },
                {
                    "check_id": f"{label}_planned_outputs",
                    "layer": "outputs",
                    "status": status((planned_output / 'samples').exists() and (planned_output / 'targets').exists()),
                    "evidence": f"samples_dir={(planned_output / 'samples').exists()}; targets_dir={(planned_output / 'targets').exists()}; output={rel(planned_output)}",
                    "next_action": "Run official inference only after runtime, checkpoint, datalist, and cascade-path blockers are closed.",
                },
            ]
        )
    return rows


def build_markdown(rows: list[dict[str, str]]) -> str:
    blocking = [row for row in rows if row["status"] == "blocking_gap"]
    warnings = [row for row in rows if row["status"] == "warning"]
    lines = [
        "# SCGM Official Feasibility Probe",
        "",
        "This probe checks local preconditions for an official SCGM reproduction without importing heavy model modules or running inference.",
        "",
        "## Summary",
        "",
        f"- Probe checks: {len(rows)}",
        f"- Blocking gaps: {len(blocking)}",
        f"- Warnings/local-override requirements: {len(warnings)}",
        "- Claim boundary: official SCGM reproduction is not locally runnable yet; current manuscript SCGM evidence remains diagnostic.",
        "",
        "## Probe Ledger",
        "",
        "| Check | Layer | Status | Evidence | Next action |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| {check_id} | {layer} | {status} | {evidence} | {next_action} |".format(
                **{key: value.replace("|", "/") for key, value in row.items()}
            )
        )
    lines += [
        "",
        "## Interpretation",
        "",
        "- The official repository and complete-reference validation subset are available locally.",
        "- The current machine lacks the required deep-learning runtime packages for the official entry point.",
        "- The official checkpoint references are not present locally.",
        "- Tracked local overrides now resolve dataroot, datalist, and cascade-path preparation; runtime, checkpoints, and generated official outputs remain open.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    rows = build_rows()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(OUT_DIR / "scgm_official_feasibility_probe.csv", rows)
    (OUT_DIR / "scgm_official_feasibility_probe.md").write_text(build_markdown(rows), encoding="utf-8")
    print(f"Wrote {rel(OUT_DIR / 'scgm_official_feasibility_probe.csv')}")
    print(f"Wrote {rel(OUT_DIR / 'scgm_official_feasibility_probe.md')}")


if __name__ == "__main__":
    main()
