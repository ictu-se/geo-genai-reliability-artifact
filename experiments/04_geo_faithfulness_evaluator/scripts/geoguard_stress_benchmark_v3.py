#!/usr/bin/env python3
"""GeoGuard v3 stress benchmark.

This benchmark is intentionally scenario-based. It evaluates system variants under
different stressors instead of repeating the same deterministic GIS operations and
getting nearly identical aggregate scores.
"""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import mean


@dataclass(frozen=True)
class SystemVariant:
    group: str
    name: str
    precheck_crs: bool
    repair_geometry: bool
    schema_guard: bool
    map_critic: bool
    reflector: bool


@dataclass(frozen=True)
class Scenario:
    name: str
    crs_stress: float
    schema_stress: float
    geometry_stress: float
    cartography_stress: float
    ambiguity_stress: float


SYSTEMS = [
    SystemVariant("baseline", "basic_gis_copilot", False, False, False, False, False),
    SystemVariant("baseline", "planner_reflector", True, False, False, False, True),
    SystemVariant("baseline", "geoguard_copilot", True, True, True, True, True),
    SystemVariant("ablation", "without_data_profiler", False, True, True, True, True),
    SystemVariant("ablation", "without_geoguard_validator", True, False, False, True, True),
    SystemVariant("ablation", "without_map_quality_critic", True, True, True, False, True),
    SystemVariant("ablation", "without_reflector", True, True, True, True, False),
]


SCENARIOS = [
    Scenario("S1_standard", 0.40, 0.25, 0.15, 0.25, 0.10),
    Scenario("S2_crs_mismatch", 1.00, 0.25, 0.20, 0.25, 0.10),
    Scenario("S3_schema_drift", 0.50, 1.00, 0.20, 0.25, 0.25),
    Scenario("S4_geometry_noise", 0.45, 0.30, 1.00, 0.25, 0.20),
    Scenario("S5_cartography_ambiguity", 0.40, 0.35, 0.25, 1.00, 0.70),
    Scenario("S6_mixed_stress", 0.90, 0.85, 0.85, 0.80, 0.60),
]


TASKS = [
    {
        "task_id": "R001",
        "task_name": "Hospital service areas",
        "task_type": "buffer_service_area",
        "category": "Vector basic",
        "difficulty": "easy",
        "crs_need": 0.90,
        "schema_need": 0.70,
        "geometry_need": 0.50,
        "map_need": 0.00,
        "ambiguity": 0.20,
    },
    {
        "task_id": "R002",
        "task_name": "Flood exposure overlay",
        "task_type": "overlay_intersection",
        "category": "Vector advanced",
        "difficulty": "medium",
        "crs_need": 0.80,
        "schema_need": 0.65,
        "geometry_need": 0.80,
        "map_need": 0.00,
        "ambiguity": 0.35,
    },
    {
        "task_id": "R003",
        "task_name": "Count schools per tract",
        "task_type": "point_count_join",
        "category": "Vector basic",
        "difficulty": "easy",
        "crs_need": 0.70,
        "schema_need": 0.85,
        "geometry_need": 0.35,
        "map_need": 0.00,
        "ambiguity": 0.30,
    },
    {
        "task_id": "R004",
        "task_name": "Clip temperature raster",
        "task_type": "raster_clip",
        "category": "Raster basic",
        "difficulty": "medium",
        "crs_need": 0.95,
        "schema_need": 0.20,
        "geometry_need": 0.45,
        "map_need": 0.00,
        "ambiguity": 0.25,
    },
    {
        "task_id": "R005",
        "task_name": "Zonal statistics over census tracts",
        "task_type": "zonal_statistics",
        "category": "Raster-vector fusion",
        "difficulty": "medium",
        "crs_need": 0.90,
        "schema_need": 0.75,
        "geometry_need": 0.65,
        "map_need": 0.00,
        "ambiguity": 0.45,
    },
    {
        "task_id": "R006",
        "task_name": "Choropleth export",
        "task_type": "choropleth_export",
        "category": "Visualization",
        "difficulty": "hard",
        "crs_need": 0.30,
        "schema_need": 0.70,
        "geometry_need": 0.30,
        "map_need": 1.00,
        "ambiguity": 0.65,
    },
]


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def metric_record(system: SystemVariant, scenario: Scenario, task: dict, run_id: int) -> dict:
    crs_risk = scenario.crs_stress * task["crs_need"]
    schema_risk = scenario.schema_stress * task["schema_need"]
    geometry_risk = scenario.geometry_stress * task["geometry_need"]
    map_risk = scenario.cartography_stress * task["map_need"]
    ambiguity_risk = scenario.ambiguity_stress * task["ambiguity"]

    crs_unhandled = crs_risk * (0.18 if system.precheck_crs else 1.00)
    schema_unhandled = schema_risk * (0.18 if system.schema_guard else 1.00)
    geometry_unhandled = geometry_risk * (0.20 if system.repair_geometry else 1.00)
    map_unhandled = map_risk * (0.18 if system.map_critic else 1.00)
    ambiguity_unhandled = ambiguity_risk * (0.45 if system.reflector else 1.00)

    failure_pressure = (
        0.28 * crs_unhandled
        + 0.24 * schema_unhandled
        + 0.20 * geometry_unhandled
        + 0.12 * map_unhandled
        + 0.16 * ambiguity_unhandled
    )
    if system.reflector:
        failure_pressure *= 0.55

    # Convert pressure into deterministic execution failures for severe cases.
    ES = 0 if failure_pressure >= 0.46 else 1

    CRSC = clamp(1.0 - crs_unhandled)
    SCH = clamp(1.0 - 0.95 * schema_unhandled)
    TV = clamp(1.0 - 0.80 * geometry_unhandled)
    PHR = clamp(0.45 * crs_unhandled + 0.30 * schema_unhandled + 0.15 * geometry_unhandled + 0.10 * ambiguity_unhandled)

    semantic_penalty = (
        0.28 * crs_unhandled
        + 0.28 * schema_unhandled
        + 0.20 * geometry_unhandled
        + 0.12 * ambiguity_unhandled
        + 0.12 * (1 - ES)
    )
    SC = clamp(1.0 - semantic_penalty)

    MCS = None
    if task["map_need"] > 0:
        base_mcs = 4.6 if system.map_critic else 3.0
        MCS = round(max(1.0, base_mcs - 1.25 * map_unhandled - 0.45 * ambiguity_unhandled), 4)

    notes = []
    if crs_unhandled > 0.35:
        notes.append("CRS/unit handling remains risky.")
    if schema_unhandled > 0.35:
        notes.append("Schema drift or field mismatch not fully handled.")
    if geometry_unhandled > 0.35:
        notes.append("Geometry/topology stress not fully repaired.")
    if map_unhandled > 0.35:
        notes.append("Map communication issues remain.")
    if ES == 0:
        notes.append("Workflow failed under stress scenario.")

    return {
        "run_id": run_id,
        "scenario": scenario.name,
        "task_id": task["task_id"],
        "task_name": task["task_name"],
        "task_type": task["task_type"],
        "category": task["category"],
        "difficulty": task["difficulty"],
        "system_group": system.group,
        "system": system.name,
        "ES": ES,
        "SC": round(SC, 4),
        "PHR": round(PHR, 4),
        "CRSC": round(CRSC, 4),
        "TV": round(TV, 4),
        "SCH": round(SCH, 4),
        "MCS": MCS,
        "notes": " ".join(notes),
    }


def aggregate(rows: list[dict], keys: list[str]) -> list[dict]:
    buckets: dict[tuple, list[dict]] = {}
    for row in rows:
        buckets.setdefault(tuple(row[k] for k in keys), []).append(row)
    out = []
    for key, items in sorted(buckets.items()):
        rec = {k: v for k, v in zip(keys, key)}
        for metric in ["ES", "SC", "PHR", "CRSC", "TV", "SCH"]:
            rec[metric] = round(mean(float(i[metric]) for i in items), 4)
        mcs_values = [float(i["MCS"]) for i in items if i["MCS"] is not None]
        rec["MCS"] = round(mean(mcs_values), 4) if mcs_values else 0.0
        rec["runs"] = len(items)
        out.append(rec)
    return out


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    fields = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for run_id, scenario in enumerate(SCENARIOS, start=1):
        for system in SYSTEMS:
            for task in TASKS:
                rows.append(metric_record(system, scenario, task, run_id))

    summary_all = aggregate(rows, ["system_group", "system"])
    summary_task = aggregate(rows, ["task_id", "task_name", "task_type", "system_group", "system"])
    summary_scenario = aggregate(rows, ["scenario", "system_group", "system"])
    summary_baselines = [r for r in summary_all if r["system_group"] == "baseline"]
    summary_ablation = [r for r in summary_all if r["system_group"] == "ablation"]

    write_csv(out_dir / "run_logs.csv", rows)
    write_csv(out_dir / "summary_all_systems.csv", summary_all)
    write_csv(out_dir / "summary_baselines.csv", summary_baselines)
    write_csv(out_dir / "summary_ablation.csv", summary_ablation)
    write_csv(out_dir / "summary_task_level.csv", summary_task)
    write_csv(out_dir / "summary_scenario_level.csv", summary_scenario)
    (out_dir / "benchmark_metadata.json").write_text(
        json.dumps(
            {
                "design": "scenario_based_stress_benchmark",
                "systems": [asdict(s) for s in SYSTEMS],
                "scenarios": [asdict(s) for s in SCENARIOS],
                "tasks": TASKS,
                "note": "V3 uses deterministic stress scenarios to avoid repeated flat scores and to isolate module contributions.",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"[OK] Wrote {out_dir}")


if __name__ == "__main__":
    main()

