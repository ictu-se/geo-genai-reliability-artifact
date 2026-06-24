#!/usr/bin/env python3
"""Build an executable contract for a future official SCGM reproduction run.

This does not claim that the official diffusion/cascade model has been run.
It turns the remaining SCGM gate into concrete runtime, subset, config, and
command contracts so the only unresolved pieces are visible and auditable.
"""

from __future__ import annotations

import csv
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MS_DIR = ROOT / "manuscripts/q1_geo_genai_reliability"
OUT_DIR = MS_DIR / "submission/scgm_official_reproduction_contract"
SCGM_REPO = ROOT / "data/repos/SCGM"
SCGM_OUTPUTS = ROOT / "experiments/03_scgm_subset_reproduction/outputs"
LOCAL_DATA = ROOT / "data/raw/SCGM/extracted/TMGN_1814"


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


def config_row(label: str, top_config: str, data_config: str, subset_manifest: str, output_dir: str) -> dict[str, str]:
    top_text = read_text(SCGM_REPO / top_config)
    data_text = read_text(SCGM_REPO / data_config)
    ckpt = yaml_value(top_text, "resume")
    dataroot = yaml_value(data_text, "dataroot")
    datalist = yaml_value(data_text, "datalist")
    scale = yaml_value(data_text, "scale")
    batch_size = yaml_value(data_text, "batch_size")
    subset_rows = read_csv(ROOT / subset_manifest)
    subset_status = "ready" if subset_rows and all(row.get("has_ref_scale_2") == "True" and row.get("has_ref_scale_4") == "True" for row in subset_rows) else "missing_or_incomplete"
    return {
        "run_label": label,
        "official_top_config": top_config,
        "official_data_config": data_config,
        "official_checkpoint_reference": ckpt,
        "official_dataroot": dataroot,
        "local_data_root": rel(LOCAL_DATA / "val"),
        "official_datalist": datalist,
        "local_subset_manifest": subset_manifest,
        "subset_rows": str(len(subset_rows)),
        "subset_reference_status": subset_status,
        "scale": scale,
        "official_batch_size": batch_size,
        "planned_output_dir": output_dir,
        "claim_status": "contract_only_not_run",
    }


def runtime_rows() -> list[dict[str, str]]:
    repo_head = git_text(["git", "-C", str(SCGM_REPO), "rev-parse", "HEAD"]) if SCGM_REPO.exists() else ""
    repo_remote = git_text(["git", "-C", str(SCGM_REPO), "remote", "get-url", "origin"]) if SCGM_REPO.exists() else ""
    return [
        {
            "item": "official_repo_commit",
            "status": "pinned" if repo_head else "missing",
            "evidence": f"{repo_remote}@{repo_head}",
            "notes": "Use this exact commit for any official/cascade-conditioned claim.",
        },
        {
            "item": "python_runtime",
            "status": "contract_drafted",
            "evidence": "python>=3.10,<3.12",
            "notes": "Chosen to match modern PyTorch/Lightning while avoiding untested Python 3.12 API drift.",
        },
        {
            "item": "core_deep_learning_stack",
            "status": "contract_drafted",
            "evidence": "pytorch, torchvision, pytorch-lightning, torchmetrics, omegaconf, einops, numpy, pillow, tqdm",
            "notes": "Derived from official entry-point imports and model utilities.",
        },
        {
            "item": "diffusion_dependency",
            "status": "contract_drafted",
            "evidence": "Stable Diffusion SD-2.1-base remains an upstream prerequisite in README.",
            "notes": "Model weights are not redistributed by this manuscript package.",
        },
        {
            "item": "device_policy",
            "status": "contract_drafted",
            "evidence": "official configs assume GPU; inference script has cpu/cuda/mps switch but heavy diffusion inference should be treated as GPU-preferred.",
            "notes": "CPU smoke tests may validate imports/configs, not final official metrics.",
        },
        {
            "item": "local_data_policy",
            "status": "ready",
            "evidence": rel(LOCAL_DATA),
            "notes": "Local CSCMG extract has base RS/map pairs and deterministic complete-reference subset manifests.",
        },
        {
            "item": "checkpoint_policy",
            "status": "external_blocker",
            "evidence": "official resume paths point to process/init weights that are not present locally.",
            "notes": "Do not claim official reproduction until obtained checkpoints or a documented training path exists.",
        },
    ]


def command_rows() -> list[dict[str, str]]:
    return [
        {
            "order": "1",
            "run_label": "2c_oz_val_complete_reference",
            "command": "cd data/repos/SCGM && python inference_refmap_batch_level.py --ckpt data/checkpoints/process_weight/g1-l1-2c+oz-1102-t165500-c30.771.ckpt --model_config configs/modelcfg/refmap_level_wc.yaml --data_config ../../../manuscripts/q1_geo_genai_reliability/submission/scgm_official_reproduction_contract/local_overrides/reference_map_test_level_2c_oz_local.yaml --output ../../../experiments/03_scgm_subset_reproduction/outputs/scgm_official_2c_oz_val --steps 50 --seed 231 --device cuda",
            "required_before_running": "official checkpoint present; local override dataroot bridge generated; GPU runtime available",
            "expected_artifacts": "samples/; targets/; log_metrics.txt",
            "claim_status": "not_run",
        },
        {
            "order": "2",
            "run_label": "4c_oz_val_complete_reference",
            "command": "cd data/repos/SCGM && python inference_refmap_batch_level.py --ckpt data/checkpoints/process_weight/g1-l1-4c+oz-0922-t169500-c30.700.ckpt --model_config configs/modelcfg/refmap_level_wc.yaml --data_config ../../../manuscripts/q1_geo_genai_reliability/submission/scgm_official_reproduction_contract/local_overrides/reference_map_test_level_4c_oz_local.yaml --output ../../../experiments/03_scgm_subset_reproduction/outputs/scgm_official_4c_oz_val --steps 50 --seed 231 --device cuda",
            "required_before_running": "official checkpoint present; local override dataroot bridge generated; GPU runtime available",
            "expected_artifacts": "samples/; targets/; log_metrics.txt",
            "claim_status": "not_run",
        },
        {
            "order": "3",
            "run_label": "metric_ingest",
            "command": "Feed official samples/targets into the existing MAE/PSNR/SSIM, edge-continuity, and mosaic neighbor-seam scoring scripts after normalizing filenames.",
            "required_before_running": "official samples and target tiles generated",
            "expected_artifacts": "official metrics CSV/JSON and report files under experiments/03_scgm_subset_reproduction/outputs",
            "claim_status": "not_run",
        },
    ]


def environment_text() -> str:
    return """name: scgm-official-reproduction
channels:
  - pytorch
  - nvidia
  - conda-forge
dependencies:
  - python>=3.10,<3.12
  - pytorch
  - torchvision
  - pytorch-cuda
  - pip
  - pip:
      - pytorch-lightning
      - torchmetrics
      - omegaconf
      - einops
      - numpy
      - pillow
      - tqdm
      - scipy
      - scikit-image
      - opencv-python
      - lpips
      - clean-fid
"""


def build_markdown(runtime: list[dict[str, str]], configs: list[dict[str, str]], commands: list[dict[str, str]]) -> str:
    lines = [
        "# SCGM Official Reproduction Contract",
        "",
        "This contract records the exact local bridge from the official SCGM repository to a future official/cascade-conditioned reproduction run. It is intentionally conservative: no official SCGM output claim is made until checkpoints, runtime, and scored outputs exist.",
        "",
        "## Runtime Contract",
        "",
        "| Item | Status | Evidence | Notes |",
        "|---|---|---|---|",
    ]
    for row in runtime:
        lines.append(f"| {row['item']} | {row['status']} | {row['evidence']} | {row['notes']} |")
    lines += [
        "",
        "## Config And Subset Mapping",
        "",
        "| Run | Official config | Data config | Checkpoint reference | Local subset | Rows | Reference status | Planned output |",
        "|---|---|---|---|---|---:|---|---|",
    ]
    for row in configs:
        lines.append(
            f"| {row['run_label']} | `{row['official_top_config']}` | `{row['official_data_config']}` | `{row['official_checkpoint_reference']}` | `{row['local_subset_manifest']}` | {row['subset_rows']} | {row['subset_reference_status']} | `{row['planned_output_dir']}` |"
        )
    lines += [
        "",
        "## Planned Commands",
        "",
        "| Order | Run | Command | Required before running | Expected artifacts |",
        "|---:|---|---|---|---|",
    ]
    for row in commands:
        lines.append(
            f"| {row['order']} | {row['run_label']} | `{row['command']}` | {row['required_before_running']} | {row['expected_artifacts']} |"
        )
    lines += [
        "",
        "## Claim Boundary",
        "",
        "- Current manuscript evidence remains diagnostic, not an official SCGM reproduction.",
        "- The complete-reference validation subset is ready for controlled official inference once checkpoint and runtime blockers are resolved.",
        "- Any future upgrade must add generated official samples, target copies, metric CSV/JSON files, and a manuscript-table update before changing the claim language.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    runtime = runtime_rows()
    configs = [
        config_row(
            "2c_oz_val_complete_reference",
            "configs/test_refmap_level_2c_oz.yaml",
            "configs/datasetcfg/reference_map_test_level_2c_oz.yaml",
            "experiments/03_scgm_subset_reproduction/outputs/scgm_complete_reference_subset_val_first200.csv",
            "experiments/03_scgm_subset_reproduction/outputs/scgm_official_2c_oz_val",
        ),
        config_row(
            "4c_oz_val_complete_reference",
            "configs/test_refmap_level_4c_oz.yaml",
            "configs/datasetcfg/reference_map_test_level_4c_oz.yaml",
            "experiments/03_scgm_subset_reproduction/outputs/scgm_complete_reference_subset_val_first200.csv",
            "experiments/03_scgm_subset_reproduction/outputs/scgm_official_4c_oz_val",
        ),
    ]
    commands = command_rows()
    write_csv(OUT_DIR / "scgm_runtime_dependency_contract.csv", runtime)
    write_csv(OUT_DIR / "scgm_official_config_mapping.csv", configs)
    write_csv(OUT_DIR / "scgm_official_run_commands.csv", commands)
    (OUT_DIR / "environment_scgm_official_reproduction.yml").write_text(environment_text(), encoding="utf-8")
    (OUT_DIR / "scgm_official_reproduction_contract.md").write_text(
        build_markdown(runtime, configs, commands),
        encoding="utf-8",
    )
    print(f"Wrote {rel(OUT_DIR / 'scgm_official_reproduction_contract.md')}")
    print(f"Wrote {rel(OUT_DIR / 'scgm_runtime_dependency_contract.csv')}")
    print(f"Wrote {rel(OUT_DIR / 'scgm_official_config_mapping.csv')}")
    print(f"Wrote {rel(OUT_DIR / 'scgm_official_run_commands.csv')}")


if __name__ == "__main__":
    main()
