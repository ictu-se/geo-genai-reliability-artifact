#!/usr/bin/env python3
"""Generate validator-gated reference repair scripts for all choropleth prompts.

These scripts are not model outputs. They are deterministic positive controls
for the repair condition: every script calls the same validated reference
baseline and is scored through the same safety/run/artifact QA pipeline.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
EXP_DIR = ROOT / "experiments/05_choropleth_reliability_benchmark"
TASKS_PATH = EXP_DIR / "inputs/prompts_expanded.json"
OUT_DIR = EXP_DIR / "outputs/generated_code/validator_repair_reference/validator"
REFERENCE_SCRIPT = "experiments/05_choropleth_reliability_benchmark/scripts/run_reference_choropleth_baseline.py"


TEMPLATE = '''#!/usr/bin/env python3
"""Validator-gated deterministic repair/reference for {prompt_id}.

This is an oracle-style repair target, not an LLM-generated script.

Required benchmark metadata:
- Task family: {family}
- Required outputs: {required_outputs}
- Uses CHOROPLETH_DATA_DIR and CHOROPLETH_OUTPUT_DIR.
- Known files: mainlandburn.shp, boundary.shp, MCD64.006.yearly-ba-nf.2002-2022.PRT_Portugal.csv.
- CRS rule: if mainlandburn.shp lacks CRS, set EPSG:4326.
- Geometry repair rule: use make_valid when available, otherwise buffer(0).
"""

from __future__ import annotations

import runpy


def main() -> None:
    # The referenced baseline performs CRS normalization, make_valid/buffer(0)
    # geometry repair, static PNG rendering, Folium HTML rendering, time-series
    # plotting, and diagnostics JSON writing using CHOROPLETH_DATA_DIR and
    # CHOROPLETH_OUTPUT_DIR.
    runpy.run_path("{reference_script}", run_name="__main__")


if __name__ == "__main__":
    main()
'''


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tasks = json.loads(TASKS_PATH.read_text(encoding="utf-8"))
    manifest = []
    for task in tasks:
        out_path = OUT_DIR / f"{task['prompt_id']}_validator.py"
        out_path.write_text(
            TEMPLATE.format(
                prompt_id=task["prompt_id"],
                family=task["family"],
                required_outputs=", ".join(task["required_outputs"]),
                reference_script=REFERENCE_SCRIPT,
            ),
            encoding="utf-8",
        )
        manifest.append(
            {
                "model": "validator_repair_reference",
                "mode": "validator",
                "prompt_id": task["prompt_id"],
                "family": task["family"],
                "required_outputs": task["required_outputs"],
                "script": str(out_path.relative_to(ROOT)),
                "status": "generated",
                "interpretation": "deterministic positive-control repair target, not an LLM output",
            }
        )
    manifest_path = OUT_DIR.parent / "generation_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Wrote {manifest_path.relative_to(ROOT)}")
    print(f"scripts={len(manifest)}")


if __name__ == "__main__":
    main()
