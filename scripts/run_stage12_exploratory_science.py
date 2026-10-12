"""Prospectively fixed exploratory Stage12 mortal-life factorial. No scientific GO."""
from __future__ import annotations
import argparse
from collections import Counter
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

from i0.modules.stage12_detectors import Stage12DetectionPolicy
from lab.determinism import canonical_causal_bytes, sha256_hex
from lab.journal import HashChainedJournal
from lab.stage10_reference_fixture import build_stage10_reference_runtime
from lab.stage11_reference_fixture import build_stage11_reference_runtime
from lab.stage12_operator_console import Stage12OperatorConsole
from lab.stage12_runtime import Stage12Runtime
from lab.stage12_alignment import evaluate_goal_action_alignment
from lab.stage12_diagnostic_audit import audit_stage12_diagnostics
from lab.stage12_occupancy_audit import audit_stage12_occupancy
from lab.stage12_goal_progress_audit import audit_stage12_goal_progress
from lab.independent_journal_audit import audit_export_bytes
from lab.world import Position, WorldLayout, BodyState

ROOT = Path(__file__).resolve().parents[1]
WORLDS = ("path_obstructed", "reference", "water_available")
INITIAL_WATERS = (20.0, 35.0)
SLEEP_PROFILES = ("sleep_pressure_ablation", "sleep_reference")
MAX_STEPS = 50


def run_life(folder: Path, world_name: str, water: float, sleep_name: str) -> dict:
    s11 = build_stage11_reference_runtime(enable_geography=True, autonomous_mortal=True)
    s10 = build_stage10_reference_runtime(autonomous_mortal=True)
    config = replace(s11.world.config,
        version="stage12-exp-20261012-physical-v1",
        initial_body=replace(s11.world.config.initial_body, water=water))
    layout = s11.world._layout
    if world_name == "water_available":
        layout = replace(layout, water_sources=layout.water_sources | frozenset({Position(2,2)}),
                         resources=layout.resources + ((Position(2,2), "berry_a", 2),))
    elif world_name == "path_obstructed":
        layout = replace(layout, obstacles=layout.obstacles | frozenset({Position(3,2)}))
    elif world_name != "reference":
        raise ValueError("undeclared world")
    layout.validate(config)
    sleep = s10._stage10_config.sleep
    if sleep_name == "sleep_pressure_ablation":
        sleep = replace(sleep, fatigue_gain=0.0, night_weight=0.0, consolidation_weight=0.0)
    elif sleep_name != "sleep_reference":
        raise ValueError("undeclared sleep")
    combined = replace(s10._stage10_config, stage9=s11._stage11_config.stage9, sleep=sleep)
    life = Stage12Runtime(
        world_config=config, layout=layout,
        safety_config=s11.stage3.substrate.safety._config,
        safety_facts=s11._canonical_safety._innate,
        protected_integrity_threshold=s11.stage3.control._config.protected_integrity_threshold,
        stage11_config=s11._stage11_config, stage10_config=combined,
        equipment=s11.equipment, autonomous_mortal=True,
        wal_path=str(folder / "life.wal"),
        diagnostic_sample_cost_uc=1, module_occupancy_cost_uc=1,
        detector_policy=Stage12DetectionPolicy(
            version="stage12-exploratory-precommitted-v1", window=12,
            stagnation_steps=4, stagnation_tolerance=0.05,
            loop_repetitions=3, loop_max_period=2,
            entropy_min_samples=4, entropy_warning_fraction=0.25,
            bias_min_outcomes_each=2, attribution_bias_threshold=0.75))
    Stage12OperatorConsole(substrate=life.stage3.substrate, mode="campaign",
        policy_version="stage12-exploratory-fixed-50-v1", maximum_world_steps=MAX_STEPS)
    actions: Counter[str] = Counter()
    failure = None
    for index in range(MAX_STEPS):
        try:
            result = life.run_step()
            if result.execution_status != "applied":
                failure = "nonapplied:" + result.execution_status
                break
            actions[result.command_primitive] += 1
        except Exception as exc:
            failure = f"{type(exc).__name__}: {exc}"
            break
    raw = life.journal.canonical_bytes()
    (folder / "canonical.jsonl").write_bytes(raw)
    tail = {"expected_head": life.journal.head_hash,
            "expected_count": len(life.journal.entries)}
    audit_error = None
    analyses = {}
    try:
        durable = HashChainedJournal.audit_durable_wal(str(folder / "life.wal"))
        if (durable["head_hash"] != tail["expected_head"]
                or durable["verified_entries"] != tail["expected_count"]):
            raise ValueError("WAL and memory journal diverged")
        if not life.journal.verify():
            raise ValueError("invalid internal journal")
        base = audit_export_bytes(raw, **tail)
        if base.world_steps_closed != sum(actions.values()):
            raise ValueError("physical action and closure mismatch")
        alignment = evaluate_goal_action_alignment(raw, **tail)
        diagnostic = audit_stage12_diagnostics(raw, **tail)
        occupancy = audit_stage12_occupancy(raw, **tail)
        goal = audit_stage12_goal_progress(raw, **tail)
        counts = {"stagnation": Counter(), "reasoning_loop": Counter(),
                  "low_context_entropy": Counter()}
        for item in life.journal.entries:
            event = item.causal_event
            if event.get("kind") == "stage12_lived_diagnostics_published":
                for name in counts:
                    val = event["data"].get(name)
                    counts[name]["positive" if val is True else
                                 "negative" if val is False else "unknown"] += 1
        analyses = {
            "world_steps_closed": base.world_steps_closed,
            "actions": alignment.as_dict()["counts"],
            "diagnostics": diagnostic.as_dict(),
            "module_occupancy": occupancy.as_dict(),
            "goal_progress": goal.as_dict(),
            "context_detector_classes": {k: dict(v) for k,v in counts.items()},
        }
    except Exception as exc:
        audit_error = f"{type(exc).__name__}: {exc}"
    record = {
        "schema": "stage12-exploratory-life-v1",
        "world": world_name, "initial_water": water, "sleep_profile": sleep_name,
        "world_config_sha256": sha256_hex(canonical_causal_bytes(config.as_dict())),
        "layout_sha256": sha256_hex(canonical_causal_bytes(layout.as_dict())),
        "journal_sha256": sha256(raw).hexdigest(),
        "journal_head": tail["expected_head"], "occurrences": tail["expected_count"],
        "requested_steps": MAX_STEPS, "executed_steps": sum(actions.values()),
        "actions": dict(sorted(actions.items())), "mortal_status": life.stage3.substrate.mortal_status.value,
        "failure": failure, "audit_error": audit_error, "audits": analyses,
        "scientific_verdict": "not_performed", "operator_accepted": False,
        "m11_stage12_atomic_recovery_certified": False,
        "attribution_calibration_supported": False,
    }
    (folder / "life-result.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    return record


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args=parser.parse_args()
    root=args.output_dir.resolve()
    root.mkdir(parents=True, exist_ok=False)
    proc=subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,capture_output=True,text=True,check=True)
    rows=[]
    for name in WORLDS:
        for water in INITIAL_WATERS:
            for sleep in SLEEP_PROFILES:
                label=f"{name}-water{int(water)}-{sleep}"
                sub=root/label
                sub.mkdir()
                try:
                    rows.append(run_life(sub,name,water,sleep))
                except BaseException as exc:
                    # Preserve all previous evidence and record the exception.
                    row={"world":name,"initial_water":water,"sleep_profile":sleep,
                         "error":f"{type(exc).__name__}: {exc}",
                         "executed_steps":0}
                    rows.append(row)
                    (sub/"runner-error.json").write_text(json.dumps(row))
                (root/"index.json").write_text(json.dumps(
                    {"source_sha":proc.stdout.strip(),"preregistration":
                     "docs/research/stage12-exploratory-behavior-preregistration-2026-10-12.fr.md",
                     "n_planned":12,"n_completed":len(rows),"lives":rows,
                     "scientific_validation":"not_performed",
                     "operator_accepted":False},indent=2,sort_keys=True)+"\n")
    valid=[r for r in rows if "error" not in r and not r["audit_error"]]
    summary={"source_sha":proc.stdout.strip(),"planned_lives":12,"audited_lives":len(valid),
             "real_physical_steps":sum(r["executed_steps"] for r in valid),
             "failed_or_unverified_lives":len(rows)-len(valid),
             "scientific_status":"exploratory_data_only_not_confirmatory",
             "operator_accepted":False}
    (root/"summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print(json.dumps(summary,sort_keys=True))
    return 0 if len(valid)==12 else 2


if __name__=="__main__":
    raise SystemExit(main())
