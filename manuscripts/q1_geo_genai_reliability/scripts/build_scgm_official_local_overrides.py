#!/usr/bin/env python3
"""Build local path/config overrides for a future official SCGM inference run."""

from __future__ import annotations

import csv
import os
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MS_DIR = ROOT / "manuscripts/q1_geo_genai_reliability"
CONTRACT_DIR = MS_DIR / "submission/scgm_official_reproduction_contract"
OVERRIDE_DIR = CONTRACT_DIR / "local_overrides"
SCGM_REPO = ROOT / "data/repos/SCGM"
LOCAL_DATA = ROOT / "data/raw/SCGM/extracted/TMGN_1814"
SCGM_OUTPUTS = ROOT / "experiments/03_scgm_subset_reproduction/outputs"
BRIDGE_ROOT = SCGM_OUTPUTS / "scgm_official_local_bridge"
BRIDGE_VAL = BRIDGE_ROOT / "val"
CASCADE_DIR = BRIDGE_ROOT / "cascade_seed_samples"
SUBSET = SCGM_OUTPUTS / "scgm_complete_reference_subset_val_first200.csv"
LOCAL_DATALIST = "tilelist_18_16_3L.csv"


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def repo_rel(path: Path) -> str:
    return os.path.relpath(path, SCGM_REPO).replace(os.sep, "/")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields or list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def replace_yaml_value(content: str, key: str, value: str) -> str:
    pattern = re.compile(rf"^(\s*{re.escape(key)}:\s*).*$", flags=re.M)
    if pattern.search(content):
        return pattern.sub(lambda match: f"{match.group(1)}{value}", content)
    return content.rstrip() + f"\n{key}: {value}\n"


def ensure_symlink(link: Path, target: Path) -> str:
    link.parent.mkdir(parents=True, exist_ok=True)
    relative_target = os.path.relpath(target, link.parent)
    if link.is_symlink():
        current = os.readlink(link)
        if current == relative_target:
            return "ready"
        link.unlink()
    elif link.exists():
        return "path_exists_not_symlink"
    link.symlink_to(relative_target)
    return "created"


def build_datalist() -> int:
    subset_rows = read_csv(SUBSET)
    rows = [{"tilename": row["tile"]} for row in subset_rows]
    write_csv(BRIDGE_VAL / LOCAL_DATALIST, rows, ["tilename"])
    return len(rows)


def build_data_config(source: Path, output: Path, scale: str) -> None:
    content = source.read_text(encoding="utf-8")
    content = replace_yaml_value(content, "dataroot", repo_rel(BRIDGE_VAL))
    content = replace_yaml_value(content, "datalist", LOCAL_DATALIST)
    content = replace_yaml_value(content, "cascade_path", repo_rel(CASCADE_DIR))
    content = replace_yaml_value(content, "scale", scale)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")


def build_rows(datalist_rows: int, link_status: dict[str, str]) -> list[dict[str, str]]:
    outputs = {
        "2c_oz": OVERRIDE_DIR / "reference_map_test_level_2c_oz_local.yaml",
        "4c_oz": OVERRIDE_DIR / "reference_map_test_level_4c_oz_local.yaml",
    }
    return [
        {
            "artifact": "bridge_dataroot",
            "status": "ready" if BRIDGE_VAL.exists() else "missing",
            "path": rel(BRIDGE_VAL),
            "evidence": "; ".join(f"{name}={state}" for name, state in sorted(link_status.items())),
            "claim_boundary": "Local bridge only; does not create official model outputs.",
        },
        {
            "artifact": "bridge_datalist",
            "status": "ready" if (BRIDGE_VAL / LOCAL_DATALIST).exists() and datalist_rows == 200 else "missing_or_incomplete",
            "path": rel(BRIDGE_VAL / LOCAL_DATALIST),
            "evidence": f"rows={datalist_rows}; required_column=tilename; loader_minmax_from_filename=18_16",
            "claim_boundary": "Derived from complete-reference validation subset for controlled future inference.",
        },
        {
            "artifact": "bridge_cascade_path",
            "status": "ready" if CASCADE_DIR.exists() else "missing",
            "path": rel(CASCADE_DIR),
            "evidence": "directory exists for deterministic future cascade outputs",
            "claim_boundary": "Empty seed directory; future official inference must populate samples.",
        },
        {
            "artifact": "2c_local_data_config",
            "status": "ready" if outputs["2c_oz"].exists() else "missing",
            "path": rel(outputs["2c_oz"]),
            "evidence": f"dataroot={repo_rel(BRIDGE_VAL)}; datalist={LOCAL_DATALIST}; cascade_path={repo_rel(CASCADE_DIR)}",
            "claim_boundary": "Config override only; checkpoint/runtime still required.",
        },
        {
            "artifact": "4c_local_data_config",
            "status": "ready" if outputs["4c_oz"].exists() else "missing",
            "path": rel(outputs["4c_oz"]),
            "evidence": f"dataroot={repo_rel(BRIDGE_VAL)}; datalist={LOCAL_DATALIST}; cascade_path={repo_rel(CASCADE_DIR)}",
            "claim_boundary": "Config override only; checkpoint/runtime still required.",
        },
    ]


def build_report(rows: list[dict[str, str]]) -> str:
    lines = [
        "# SCGM Official Local Overrides",
        "",
        "These artifacts close local path and datalist preparation gaps for a future official SCGM inference run. They do not supply model checkpoints, runtime packages, or generated official outputs.",
        "",
        "| Artifact | Status | Path | Evidence | Claim boundary |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| {artifact} | {status} | `{path}` | {evidence} | {claim_boundary} |".format(
                **{key: value.replace("|", "/") for key, value in row.items()}
            )
        )
    lines += [
        "",
        "## Usage Note",
        "",
        "Run official SCGM inference from `data/repos/SCGM` with the local data-config override after installing the runtime and obtaining the referenced checkpoints. The bridge dataroot uses relative symlinks to avoid copying or mutating the raw CSCMG extract.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    BRIDGE_VAL.mkdir(parents=True, exist_ok=True)
    CASCADE_DIR.mkdir(parents=True, exist_ok=True)
    link_status = {
        folder: ensure_symlink(BRIDGE_VAL / folder, LOCAL_DATA / "val" / folder)
        for folder in ("rs_256", "map_256", "ref_scale_2_256", "ref_scale_4_256")
    }
    datalist_rows = build_datalist()
    build_data_config(
        SCGM_REPO / "configs/datasetcfg/reference_map_test_level_2c_oz.yaml",
        OVERRIDE_DIR / "reference_map_test_level_2c_oz_local.yaml",
        "2",
    )
    build_data_config(
        SCGM_REPO / "configs/datasetcfg/reference_map_test_level_4c_oz.yaml",
        OVERRIDE_DIR / "reference_map_test_level_4c_oz_local.yaml",
        "4",
    )
    rows = build_rows(datalist_rows, link_status)
    write_csv(OVERRIDE_DIR / "scgm_official_local_override_manifest.csv", rows)
    (OVERRIDE_DIR / "scgm_official_local_overrides.md").write_text(build_report(rows), encoding="utf-8")
    print(f"Wrote {rel(OVERRIDE_DIR / 'scgm_official_local_override_manifest.csv')}")
    print(f"Wrote {rel(OVERRIDE_DIR / 'scgm_official_local_overrides.md')}")
    print(f"Wrote {rel(BRIDGE_VAL / LOCAL_DATALIST)}")


if __name__ == "__main__":
    main()
