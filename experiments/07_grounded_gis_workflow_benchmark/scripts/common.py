"""Shared paths and utilities for the grounded GIS workflow benchmark."""

from __future__ import annotations

from pathlib import Path


def find_repo_root(start: Path | None = None) -> Path:
    """Return the repository root from a script path inside this experiment."""
    current = (start or Path(__file__)).resolve()
    for parent in [current, *current.parents]:
        if (parent / ".git").exists() or (parent / "experiments").exists():
            if (parent / "experiments/07_grounded_gis_workflow_benchmark").exists():
                return parent
    return Path(__file__).resolve().parents[3]


ROOT = find_repo_root()
EXP_ROOT = ROOT / "experiments/07_grounded_gis_workflow_benchmark"
INPUT_ROOT = EXP_ROOT / "inputs"
OUTPUT_ROOT = EXP_ROOT / "outputs"
SPEC_ROOT = OUTPUT_ROOT / "generated_specs"
SCORE_ROOT = OUTPUT_ROOT / "scores"
TASKS_PATH = INPUT_ROOT / "workflow_tasks_30.json"
MODEL_PANEL_PATH = INPUT_ROOT / "model_panel.json"


def model_slug(model: str) -> str:
    return model.replace(":", "_").replace("/", "_")
