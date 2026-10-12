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
from i0.interfaces import PrimitiveCommand
from i0.equipment import train_exact_transition_table
from lab.world import WorldBody
from lab.equipment_corpus import EquipmentCorpusRecorder

def build_prebirth_equipment(config, layout):
    """Independent offline physical examples, never Oracle input or an agent command."""
    world = WorldBody(config=config, layout=layout)
    recorder = EquipmentCorpusRecorder(corpus_version="issue132-north-south-drink-real-world-v1")
    recorder.record_transition(world=world, t_monde=1, family="movement_free",
                               command=PrimitiveCommand("se_deplacer", {"direction": "north"}))
    recorder.record_transition(world=world, t_monde=2, family="movement_free",
                               command=PrimitiveCommand("se_deplacer", {"direction": "south"}))
    recorder.record_transition(world=world, t_monde=3, family="drinking",
                               command=PrimitiveCommand("boire"))
    return train_exact_transition_table(
        corpus=recorder.build(), equipment_version="E-stage12-issue132-lived-physical-v1")

WORLDS = ("trained_return_and_drink",)
INITIAL_WATERS = (20.0,)
SLEEP_PROFILES = ("horizon_one", "horizon_two")
MAX_STEPS = 50


def run_life(folder: Path, world_name: str, water: float, sleep_name: str) -> dict:
    s11 = build_stage11_reference_runtime(enable_geography=True, autonomous_mortal=True)
    s10 = build_stage10_reference_runtime(autonomous_mortal=True)
    config = replace(s11.world.config,
        version="stage12-exp-issue132-zero-cons-v1",
        initial_body=replace(s11.world.config.initial_body, water=water))
    layout = s11.world._layout
    if world_name not in WORLDS:
        raise ValueError("undeclared equipment condition")
    layout = replace(layout, water_sources=frozenset({Position(2, 2)}), resources=())
    layout.validate(config)
    sleep = s10._stage10_config.sleep
    if sleep_name not in SLEEP_PROFILES:
        raise ValueError("undeclared sleep")
    sleep = replace(sleep, version="stage12-issue132-zero-wc-development-v1",
                    consolidation_weight=0.0)
    stage11_config = s11._stage11_config
    if sleep_name == "horizon_two":
        cfg9 = stage11_config.stage9
        cfg8 = cfg9.stage8
        cfg7 = cfg8.stage7
        cfg6 = cfg7.stage6
        revised6 = replace(cfg6, evaluation=replace(cfg6.evaluation,
            version="stage12-issue132-two-step-value-v1", h_eff=2))
        stage11_config = replace(stage11_config, stage9=replace(cfg9,
            stage8=replace(cfg8, stage7=replace(cfg7, stage6=revised6))))
    combined = replace(s10._stage10_config, stage9=stage11_config.stage9, sleep=sleep)
    equipment = s11.equipment if world_name == "reference_equipment" else build_prebirth_equipment(config, layout)
    life = Stage12Runtime(
        world_config=config, layout=layout,
        safety_config=s11.stage3.substrate.safety._config,
        safety_facts=s11._canonical_safety._innate,
        protected_integrity_threshold=s11.stage3.control._config.protected_integrity_threshold,
        stage11_config=stage11_config, stage10_config=combined,
        equipment=equipment, autonomous_mortal=True,
        wal_path=str(folder / "life.wal"),
        diagnostic_sample_cost_uc=1, module_occupancy_cost_uc=1,
        detector_policy=Stage12DetectionPolicy(
            version="stage12-issue132-horizon-contrast-v1", window=12,
            stagnation_steps=4, stagnation_tolerance=0.05,
            loop_repetitions=3, loop_max_period=2,
            entropy_min_samples=4, entropy_warning_fraction=0.25,
            bias_min_outcomes_each=2, attribution_bias_threshold=0.75))
    Stage12OperatorConsole(substrate=life.stage3.substrate, mode="campaign",
        policy_version="stage12-issue132-fixed-50-v1", maximum_world_steps=MAX_STEPS)
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
        from collections import Counter as LocalCounter
        planning = [e.causal_event for e in life.journal.entries if e.causal_event.get("kind") == "stage6_planning_result"]
        slept = [e.causal_event for e in life.journal.entries if e.causal_event.get("kind") == "stage10_sleep_entered"]
        wakes = [e.causal_event for e in life.journal.entries if e.causal_event.get("kind") == "stage10_sleep_woke"]
        consolidations = [e.causal_event for e in life.journal.entries if e.causal_event.get("kind") == "stage10_consolidation_version_activated"]
        first_actual_drink = next((e.causal_event["t_monde"] for e in life.journal.entries
            if e.causal_event.get("kind") == "command_admitted"
            and e.causal_event.get("data",{}).get("primitive") == "boire"), None)
        analyses = {
            "first_drink_admitted_step": first_actual_drink,
            "equipment_artifact_sha256": equipment.artifact_digest,
            "planning_results": len(planning), "non_null_plans": sum(x.get("data",{}).get("proposal_ref") is not None for x in planning),
            "sleep_entries": len(slept), "sleep_wakes": len(wakes), "consolidations_activated": len(consolidations),
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
        "schema": "stage12-issue132-horizon-life-v1",
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
                     "docs/research/stage12-issue132-horizon-prereg-2026-10-12.fr.md",
                     "n_planned":2,"n_completed":len(rows),"lives":rows,
                     "scientific_validation":"not_performed",
                     "operator_accepted":False},indent=2,sort_keys=True)+"\n")
    valid=[r for r in rows if "error" not in r and not r["audit_error"]]
    summary={"source_sha":proc.stdout.strip(),"planned_lives":2,"audited_lives":len(valid),
             "real_physical_steps":sum(r["executed_steps"] for r in valid),
             "failed_or_unverified_lives":len(rows)-len(valid),
             "scientific_status":"exploratory_data_only_not_confirmatory",
             "operator_accepted":False}
    (root/"summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print(json.dumps(summary,sort_keys=True))
    return 0 if len(valid)==2 else 2


if __name__=="__main__":
    raise SystemExit(main())
