#!/usr/bin/env python3
"""Build an SCGM official-reproduction readiness and gap audit.

The current manuscript has strong SCGM diagnostic baselines, but it should not
claim an official SCGM reproduction unless the official code, data references,
weights/checkpoints, runtime contract, and output metrics are all present. This
script turns that caveat into a reviewer-facing control artifact.
"""

from __future__ import annotations

import csv
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MS_DIR = ROOT / "manuscripts/q1_geo_genai_reliability"
OUT_DIR = MS_DIR / "submission/scgm_official_reproduction_audit"
CONTRACT_DIR = MS_DIR / "submission/scgm_official_reproduction_contract"
SCGM_REPO = ROOT / "data/repos/SCGM"
SCGM_DATA = ROOT / "data/raw/SCGM/extracted/TMGN_1814"
SCGM_OUTPUTS = ROOT / "experiments/03_scgm_subset_reproduction/outputs"


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def git_text(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def file_count(path: Path, suffix: str = ".png") -> int:
    return sum(1 for _ in path.glob(f"*{suffix}")) if path.exists() else 0


def config_resume_paths(config_dir: Path) -> list[str]:
    resumes: list[str] = []
    if not config_dir.exists():
        return resumes
    for path in sorted(config_dir.glob("*.yaml")):
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            match = re.match(r"resume:\s*(.+)$", stripped)
            if match:
                resumes.append(match.group(1).strip().strip("'\""))
    return sorted(set(resumes))


def checkpoint_files() -> list[Path]:
    if not SCGM_REPO.exists():
        return []
    suffixes = {".ckpt", ".pth", ".pt", ".safetensors", ".bin"}
    return sorted(path for path in SCGM_REPO.rglob("*") if path.is_file() and path.suffix.lower() in suffixes)


def load_split_summary() -> list[dict[str, object]]:
    path = SCGM_OUTPUTS / "scgm_split_summary.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def pct(part: int, total: int) -> str:
    return f"{(part / total * 100):.2f}%" if total else "0.00%"


def build_rows() -> list[dict[str, str]]:
    split_summary = load_split_summary()
    repo_files = {
        "README.md": SCGM_REPO / "README.md",
        "train.py": SCGM_REPO / "train.py",
        "validate.py": SCGM_REPO / "validate.py",
        "inference_refmap_batch_level.py": SCGM_REPO / "inference_refmap_batch_level.py",
        "LICENSE": SCGM_REPO / "LICENSE",
    }
    config_files = sorted((SCGM_REPO / "configs").glob("*.yaml")) if (SCGM_REPO / "configs").exists() else []
    resumes = config_resume_paths(SCGM_REPO / "configs")
    checkpoints = checkpoint_files()
    contract_report = CONTRACT_DIR / "scgm_official_reproduction_contract.md"
    runtime_contract = CONTRACT_DIR / "scgm_runtime_dependency_contract.csv"
    config_mapping = CONTRACT_DIR / "scgm_official_config_mapping.csv"
    run_commands = CONTRACT_DIR / "scgm_official_run_commands.csv"
    repo_head = git_text(["git", "-C", str(SCGM_REPO), "rev-parse", "HEAD"]) if SCGM_REPO.exists() else ""
    repo_remote = git_text(["git", "-C", str(SCGM_REPO), "remote", "get-url", "origin"]) if SCGM_REPO.exists() else ""

    train = next((row for row in split_summary if row.get("split") == "train"), {})
    val = next((row for row in split_summary if row.get("split") == "val"), {})
    train_pairs = int(train.get("rs_map_intersection", 0) or 0)
    val_pairs = int(val.get("rs_map_intersection", 0) or 0)
    train_ref2 = int(train.get("rs_with_ref_scale_2", 0) or 0)
    train_ref4 = int(train.get("rs_with_ref_scale_4", 0) or 0)
    val_ref2 = int(val.get("rs_with_ref_scale_2", 0) or 0)
    val_ref4 = int(val.get("rs_with_ref_scale_4", 0) or 0)

    generated_summaries = [
        "scgm_retrieval_baseline_summary.json",
        "scgm_multifeature_retrieval_summary.json",
        "scgm_learned_forest_summary.json",
        "scgm_mlp_summary.json",
        "scgm_local_context_ridge_summary.json",
        "scgm_convolutional_filter_ridge_summary.json",
        "scgm_patch_embedding_retrieval_summary.json",
        "scgm_tiny_cnn_summary.json",
        "scgm_mosaic_neighbor_stress_summary.json",
    ]
    existing_generated_summaries = [name for name in generated_summaries if (SCGM_OUTPUTS / name).exists()]

    return [
        {
            "component": "official_repository",
            "status": "present" if SCGM_REPO.exists() and repo_head else "missing",
            "evidence": f"remote={repo_remote}; commit={repo_head}",
            "blocker_or_next_action": "Freeze commit in release metadata and document any local patches before an official reproduction claim.",
        },
        {
            "component": "official_core_scripts",
            "status": "present" if all(path.exists() for path in repo_files.values()) else "incomplete",
            "evidence": "; ".join(f"{name}={path.exists()}" for name, path in repo_files.items()),
            "blocker_or_next_action": "Map train/validate/inference entry points to the local CSCMG layout before rerunning official inference.",
        },
        {
            "component": "official_configs",
            "status": "present" if len(config_files) >= 10 else "incomplete",
            "evidence": f"config files={len(config_files)}; resume references={len(resumes)}",
            "blocker_or_next_action": "Resolve datasetcfg/modelcfg paths and replace hard-coded GPU/checkpoint settings with documented local equivalents.",
        },
        {
            "component": "official_weights_or_checkpoints",
            "status": "blocking_gap" if not checkpoints else "present",
            "evidence": f"local weight/checkpoint files={len(checkpoints)}; config resume paths={'; '.join(resumes[:4])}",
            "blocker_or_next_action": "Obtain official checkpoints or train from documented initial weights before claiming official/cascade-conditioned reproduction.",
        },
        {
            "component": "base_rs_map_pairs",
            "status": "present" if train_pairs and val_pairs else "missing",
            "evidence": f"train matched={train_pairs}; val matched={val_pairs}; train rs files={file_count(SCGM_DATA / 'train/rs_256')}; val rs files={file_count(SCGM_DATA / 'val/rs_256')}",
            "blocker_or_next_action": "Base-pair availability supports local diagnostics and future official inference.",
        },
        {
            "component": "cascade_reference_coverage",
            "status": "partial",
            "evidence": f"train ref2={train_ref2}/{train_pairs} ({pct(train_ref2, train_pairs)}); train ref4={train_ref4}/{train_pairs} ({pct(train_ref4, train_pairs)}); val ref2={val_ref2}/{val_pairs} ({pct(val_ref2, val_pairs)}); val ref4={val_ref4}/{val_pairs} ({pct(val_ref4, val_pairs)})",
            "blocker_or_next_action": "Define whether official reproduction uses only complete-reference subsets or reconstructs missing cascade references.",
        },
        {
            "component": "runtime_dependency_contract",
            "status": "contract_drafted" if contract_report.exists() and runtime_contract.exists() else "blocking_gap",
            "evidence": "contract, environment draft, and GPU/runtime note exist" if contract_report.exists() and runtime_contract.exists() else "README lists PyTorch and Stable Diffusion SD-2.1-base but leaves other dependencies unspecified; configs assume GPU accelerator.",
            "blocker_or_next_action": "Instantiate and test the pinned runtime before claiming official SCGM reproduction.",
        },
        {
            "component": "official_run_contract",
            "status": "contract_drafted" if contract_report.exists() and config_mapping.exists() and run_commands.exists() else "missing",
            "evidence": f"contract={contract_report.exists()}; config_mapping={config_mapping.exists()}; run_commands={run_commands.exists()}",
            "blocker_or_next_action": "Use the contract to run official inference once checkpoints and runtime are available.",
        },
        {
            "component": "current_generated_output_diagnostics",
            "status": "present",
            "evidence": f"diagnostic summary files={len(existing_generated_summaries)}/{len(generated_summaries)}; baselines include retrieval, learned forest, MLP, local ridge, convolutional ridge, patch retrieval, tiny CNN, mosaic seam stress",
            "blocker_or_next_action": "Keep reporting these as leakage-guarded diagnostics, not as official SCGM outputs.",
        },
        {
            "component": "official_output_metrics",
            "status": "not_yet_run",
            "evidence": "No SCGM official inference output directory or official checkpoint-scored metrics are present in the manuscript package.",
            "blocker_or_next_action": "Run official inference on a complete-reference validation subset and score with the existing metric/mosaic-seam pipeline.",
        },
    ]


def build_markdown(rows: list[dict[str, str]]) -> str:
    blocking = [row for row in rows if row["status"] in {"blocking_gap", "missing", "not_yet_run"}]
    partial = [row for row in rows if row["status"] in {"partial", "contract_drafted"}]
    lines = [
        "# SCGM Official-Reproduction Readiness Audit",
        "",
        "This audit separates the current SCGM diagnostic evidence from the stronger claim of reproducing the official SCGM cascade-conditioned diffusion workflow.",
        "",
        "## Summary",
        "",
        f"- Components checked: {len(rows)}",
        f"- Blocking/not-yet-run components: {len(blocking)}",
        f"- Partial components: {len(partial)}",
        "- Current claim boundary: the manuscript has leakage-guarded generated-output diagnostics and mosaic-seam stress tests, but it should not claim official SCGM reproduction yet.",
        "",
        "## Component Audit",
        "",
        "| Component | Status | Evidence | Next action |",
        "|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| {component} | {status} | {evidence} | {blocker_or_next_action} |".format(
                component=row["component"],
                status=row["status"],
                evidence=row["evidence"].replace("|", "/"),
                blocker_or_next_action=row["blocker_or_next_action"].replace("|", "/"),
            )
        )
    lines += [
        "",
        "## Reproduction Upgrade Path",
        "",
        "1. Freeze the official repository commit and document exact config files used.",
        "2. Resolve official checkpoints or train from the documented initial weights.",
        "3. Instantiate and smoke-test the drafted SCGM runtime contract.",
        "4. Use the drafted complete-reference validation subset and config/command contract.",
        "5. Run official/cascade-conditioned inference and feed outputs into the existing MAE/PSNR/SSIM, edge-continuity, and mosaic neighbor-seam scoring scripts.",
        "6. Only then upgrade RQ3 wording from diagnostic baselines to official reproduction evidence.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    rows = build_rows()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(OUT_DIR / "scgm_official_reproduction_audit.csv", rows)
    (OUT_DIR / "scgm_official_reproduction_audit.md").write_text(build_markdown(rows), encoding="utf-8")
    print(f"Wrote {rel(OUT_DIR / 'scgm_official_reproduction_audit.csv')}")
    print(f"Wrote {rel(OUT_DIR / 'scgm_official_reproduction_audit.md')}")


if __name__ == "__main__":
    main()
