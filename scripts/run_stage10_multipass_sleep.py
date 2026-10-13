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
from i0.modules.consolidation_batch import BatchSelectionPolicy
from i0.modules.consolidation_budget import ConsolidationBudgetConfig
from i0.modules.consolidation_replay_agenda import ReplayAgendaPolicy
from i0.modules.consolidation_semantics import SemanticPassPolicy

def enabled_sixpass_config(base, *, maximum_episodes=1):
    selector = BatchSelectionPolicy(
        version=f"issue133-batch-{maximum_episodes}-selection-v1",
        maximum_episodes=maximum_episodes, consequence_reference=1.0,
        surprise_reference=1.0, recency_window_steps=8,
        repetition_reference=1, weight_consequence=1.0,
        weight_surprise=1.0, weight_recency=1.0,
        weight_repetition=1.0, ageing_gain_per_step=0.1,
        scan_uc_per_episode=1,
    )
    policy = SemanticPassPolicy(
        version="issue133-sixpass-semantic-v1",
        replay=ReplayAgendaPolicy(
            version="issue133-sixpass-replay-v1",
            recent_window_steps=3, start_with_recent=True,
        ),
        skill_success_threshold=2, nearby_context_radius=1,
        rule_expiry_steps=20,
    )
    budget = ConsolidationBudgetConfig(
        version="issue133-sixpass-budget-v1",
        period_capacity_uc=600, step_slot_uc=100,
        operation_costs={
            "semantic_plan_build":1, "replay_agenda_scan":1,
            "episode_scan":1, "episode_replay":1, "rule_extraction":1,
            "skill_compilation":1, "kappa_recalibration":1,
            "index_maintenance":1, "pass_prepare":1, "pass_validate":1,
        },
    )
    return replace(base, selection_policy=selector, semantic_policy=policy,
                   sleep_work=budget, p_cons_min=0.0,
                   incremental_selection=True)

from i0.interfaces import PrimitiveCommand
from i0.equipment import train_exact_transition_table
from lab.world import WorldBody
from lab.equipment_corpus import EquipmentCorpusRecorder

def build_prebirth_equipment(config, layout):
    world = WorldBody(config=config, layout=layout)
    recorder = EquipmentCorpusRecorder(corpus_version="issue133-calibration-training-v1")
    for step,direction in ((1,"north"),(2,"south")):
        recorder.record_transition(world=world,t_monde=step,family="movement_free",
                                   command=PrimitiveCommand("se_deplacer",{"direction":direction}))
    recorder.record_transition(world=world,t_monde=3,family="drinking",
                               command=PrimitiveCommand("boire"))
    return train_exact_transition_table(corpus=recorder.build(),
               equipment_version="E-stage12-issue133-prebirth-controlled-v1")

WORLDS = ("reference_untrained",)
INITIAL_WATERS = (20.0,)
SLEEP_PROFILES = ("pass01", "pass03")
MAX_STEPS = 240


def run_life(folder: Path, world_name: str, water: float, sleep_name: str) -> dict:
    s11 = build_stage11_reference_runtime(enable_geography=True, autonomous_mortal=True)
    s10 = build_stage10_reference_runtime(autonomous_mortal=True)
    config = replace(s11.world.config,
        version="stage12-issue133-physical-v1",
        initial_body=replace(s11.world.config.initial_body, water=water))
    layout = s11.world._layout
    if world_name == "trained_water":
        layout = replace(layout, water_sources=frozenset({Position(2,2)}), resources=())
    elif world_name != "reference_untrained":
        raise ValueError("undeclared world")
    layout.validate(config)
    sleep = s10._stage10_config.sleep
    weights = {"pass01": 0.0, "pass03": 0.0}
    if sleep_name not in weights:
        raise ValueError("undeclared weight")
    sleep = replace(sleep, version=f"issue133-calibration-{sleep_name}-v1", consolidation_weight=weights[sleep_name])
    stage11_config = s11._stage11_config
    equipment = s11.equipment
    if world_name == "trained_water":
        equipment = build_prebirth_equipment(config, layout)
        cfg9 = stage11_config.stage9
        cfg8 = cfg9.stage8
        cfg7 = cfg8.stage7
        cfg6 = cfg7.stage6
        revised6 = replace(cfg6, evaluation=replace(cfg6.evaluation, version="issue133-eval-h2-v1", h_eff=2))
        stage11_config = replace(stage11_config, stage9=replace(cfg9, stage8=replace(cfg8, stage7=replace(cfg7, stage6=revised6))))
    combined = enabled_sixpass_config(replace(s10._stage10_config, stage9=stage11_config.stage9, sleep=sleep, version=f"stage10-issue133-{sleep_name}-v1"), maximum_episodes=3)
    combined = replace(combined, incremental_selection=True, maximum_passes_per_sleep_step=(1 if sleep_name=="pass01" else 3))
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
            version="stage12-issue133-precommitted-v1", window=12,
            stagnation_steps=4, stagnation_tolerance=0.05,
            loop_repetitions=3, loop_max_period=2,
            entropy_min_samples=4, entropy_warning_fraction=0.25,
            bias_min_outcomes_each=2, attribution_bias_threshold=0.75))
    Stage12OperatorConsole(substrate=life.stage3.substrate, mode="campaign",
        policy_version="stage12-issue133-fixed-50-v1", maximum_world_steps=MAX_STEPS)
    actions: Counter[str] = Counter()
    # External observation only: do not change any I0 cognitive state or price.
    work_steps = []
    work_uc_since_h = 0
    work_uc_per_publication = []
    last_h = life.slow_history.current_version
    prior_refs = set(life.slow_history.read_committed()["consolidated_episode_refs"])
    failure = None
    for index in range(MAX_STEPS):
        try:
            result = life.run_step()
            if result.execution_status != "applied":
                failure = "nonapplied:" + result.execution_status
                break
            actions[result.command_primitive] += 1
            step = index + 1
            work = life.consolidation_work
            paid_step_uc = (work.consumed_step_uc
                            if result.command_primitive == "dormir" else 0)
            paid_period_uc = (work.consumed_period_uc
                              if result.command_primitive == "dormir" else 0)
            if (paid_step_uc < 0 or paid_step_uc > combined.sleep_work.step_slot_uc
                    or paid_period_uc < 0
                    or paid_period_uc > combined.sleep_work.period_capacity_uc):
                raise ValueError("consolidation UC envelope exceeded")
            work_uc_since_h += paid_step_uc
            published_h = life.slow_history.current_version
            committed_refs = set(
                life.slow_history.read_committed()["consolidated_episode_refs"]
            )
            if published_h != last_h:
                new_refs = sorted(committed_refs - prior_refs)
                if not new_refs:
                    raise ValueError("h published without new episode refs")
                work_uc_per_publication.append({
                    "world_step": step,
                    "published_h": published_h,
                    "new_episode_refs": new_refs,
                    "work_uc_since_previous_publication": work_uc_since_h,
                })
                work_uc_since_h = 0
                last_h = published_h
            prior_refs = committed_refs
            eligible = sum(ep.end_t_monde < step for ep in life.memory.episodes)
            work_steps.append({
                "world_step": step,
                "primitive": result.command_primitive,
                "created_episodes": len(life.memory.episodes),
                "eligible_episodes_at_step_end": eligible,
                "committed_episode_refs": len(committed_refs),
                "unconsolidated_eligible_at_step_end": eligible - len(committed_refs),
                "work_step_uc": paid_step_uc,
                "work_period_uc_at_step_end": paid_period_uc,
            })

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
        entries = [entry.causal_event for entry in life.journal.entries]
        event_counts = Counter(e["kind"] for e in entries)
        pressures = [
            {"world_step":e["data"]["world_step"],
             "fatigue":e["data"]["fatigue"],
             "consolidation_pressure":e["data"]["consolidation_pressure"],
             "sleep_pressure":e["data"]["sleep_pressure"]}
            for e in entries if e["kind"] == "stage10_sleep_pressure_frozen"
        ]
        analyses = {
            "sixpass_checkpoint_count":event_counts["stage10_consolidation_pass_checkpointed"],
            "sixpass_activated":event_counts["stage10_consolidation_version_activated"],
            "sleep_entered":event_counts["stage10_sleep_entered"],
            "sleep_woke":event_counts["stage10_sleep_woke"],
            "sleep_deferred":event_counts["stage10_consolidation_work_deferred"],
            "incremental_scan_chunks":event_counts["stage10_consolidation_scan_checkpointed"],
            "incremental_scan_starts":event_counts["stage10_consolidation_scan_started"],
            "sleep_pressure_series":pressures,
            "episodes":len(life.memory.episodes),
            "consolidated_episode_refs":list(life.slow_history.read_committed()["consolidated_episode_refs"]),
            "unconsolidated_episodes_end":sum(e.id not in set(life.slow_history.read_committed()["consolidated_episode_refs"]) for e in life.memory.episodes),
            # The historic final-period counter is often zero after waking;
            # preserve exact per-step paid UC instead of interpreting it as
            # zero lifetime work.
            "consolidation_work_uc_period":life.consolidation_work.consumed_period_uc,
            "consolidation_paid_work_uc_total":sum(e["work_step_uc"] for e in work_steps),
            "consolidation_work_uc_per_step":work_steps,
            "consolidation_work_uc_per_published_h":work_uc_per_publication,
            "consolidation_work_uc_unfinished":work_uc_since_h,
            "consolidation_work_uc_max_step":max(
                (e["work_step_uc"] for e in work_steps), default=0),
            "consolidation_work_uc_max_period_observed":max(
                (e["work_period_uc_at_step_end"] for e in work_steps), default=0),
            "drinks_applied":actions["boire"],
            "goal_progress_followups":event_counts["stage12_goal_progress_followup"],
            "slow_history_version":life.slow_history.current_version,
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
        "schema": "stage12-issue133-multipass-life-v1",
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
                     "docs/research/stage10-multipass-sleep-prereg-2026-10-13.fr.md",
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
