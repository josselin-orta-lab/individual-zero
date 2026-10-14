"""Issue110: preregistered alignment with the first lived Stage6 state.

Physical prebirth corpus. No forced decisions, no cognition from the lab.
"""
from __future__ import annotations
import argparse
from collections import Counter
from dataclasses import replace
from hashlib import sha256
import json
import os
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
from lab.stage12_first_person_agency_audit import audit_stage12_first_person_agency
from lab.stage12_attribution_pair_audit import audit_stage12_attribution_pairs
from lab.stage12_spatial_cue_audit import audit_spatial_visible_cues
from lab.independent_journal_audit import audit_export_bytes
from lab.world import Position, WorldLayout, BodyState

ROOT = Path(__file__).resolve().parents[1]
from i0.interfaces import PrimitiveCommand
from i0.equipment import train_exact_transition_table
from lab.world import WorldBody
from lab.equipment_corpus import EquipmentCorpusRecorder

def build_prebirth_equipment(config, layout, *, food_target: bool):
    """Physically applied exterior examples before I0's birth, no causal labels."""
    world = WorldBody(config=config, layout=layout)
    family = "food" if food_target else "water"
    recorder = EquipmentCorpusRecorder(
        corpus_version="issue110-lived-north-east-" + family + "-physical-v1",
    )
    recorder.record_transition(
        world=world, t_monde=1, family="movement_free",
        command=PrimitiveCommand("se_deplacer", {"direction": "north"}),
    )
    recorder.record_transition(
        world=world, t_monde=2, family="movement_free",
        command=PrimitiveCommand("se_deplacer", {"direction": "east"}),
    )
    if food_target:
        recorder.record_transition(
            world=world, t_monde=3, family="collection_without_tool",
            command=PrimitiveCommand("collecter", {"target": "berry_a"}),
        )
        recorder.record_transition(
            world=world, t_monde=4, family="resource_consumption",
            command=PrimitiveCommand("manger", {"target": "berry_a"}),
        )
    else:
        recorder.record_transition(
            world=world, t_monde=3, family="drinking",
            command=PrimitiveCommand("boire"),
        )
    return train_exact_transition_table(
        corpus=recorder.build(),
        equipment_version="E-stage12-issue110-lived-state-" + family + "-physical-v1",
    )


WORLDS = ("near_food_free", "near_food_blocked", "near_water_free", "near_water_blocked")
INITIAL_WATERS = (70.0,)
SLEEP_PROFILES = ("horizon_three",)
MAX_STEPS = 50


def build_life(
    world_name: str, water: float, sleep_name: str, *,
    wal_path: str | None = None, m11_sqlite_custody: bool = False,
    birth_life_id: str | None = None,
    a2_external_obstacle: bool = False,
    a2_obstacle_clear_step: int | None = None,
    calibration_food_profile: str | None = None,
    planning_depth: int = 3,
    progressive_planning: bool = False,
    progressive_evaluation_prefix: bool = False,
):
    """Build the exact preregistered life for standalone WAL or M11 SQLite.

    M11 owns all state when opted-in. The training WorldBody is still
    physically distinct and exists only before I0's birth.
    """
    s11 = build_stage11_reference_runtime(enable_geography=True, autonomous_mortal=True)
    s10 = build_stage10_reference_runtime(autonomous_mortal=True)
    config = replace(s11.world.config,
        version="stage12-issue110-food-world-v1",
        initial_body=replace(
            s11.world.config.initial_body,
            water=water,
            food=(35.0 if world_name.startswith("near_food") else 70.0),
        ),
        berry_effects={**s11.world.config.berry_effects,
                       "berry_a": replace(s11.world.config.berry_effects["berry_a"],
                                           food_gain=30.0, integrity_delta=0.0)})
    layout = s11.world._layout
    if world_name not in WORLDS:
        raise ValueError("undeclared equipment condition")
    adjacent = Position(3, 1)
    target_food = world_name.startswith("near_food")
    blocked = world_name.endswith("_blocked")
    layout = replace(
        layout, water_sources=frozenset({Position(2, 2) if target_food else adjacent}),
        resources=((adjacent if target_food else Position(2, 2), "berry_a", 2),),
        obstacles=frozenset({adjacent}) if blocked else frozenset(),
    )
    # Physical sensitivity conditions are fixed BEFORE the newborn's world
    # and the detached prebirth Equipment corpus are constructed. Existing
    # environments preserve byte-for-byte historical configurations.
    if calibration_food_profile is not None:
        profiles = {
            "sustained": (24.0, 6.0, 0.7, 12),
            "episodic": (33.0, 12.0, 1.6, 8),
            "marginal": (22.0, 3.0, 1.3, 12),
            "restored": (35.0, 30.0, 0.0, 12),
            "replenished": (35.0, 40.0, 2.0, 12),
            "urgent": (35.0, 50.0, 4.0, 12),
        }
        if (type(calibration_food_profile) is not str
                or calibration_food_profile not in profiles
                or world_name != "near_food_free"):
            raise ValueError("unknown prebirth calibration food profile")
        initial_food, gain, decay, quantity = profiles[calibration_food_profile]
        config = replace(
            config,
            version=config.version + "-calibration-" + calibration_food_profile + "-v1",
            initial_body=replace(config.initial_body, food=initial_food),
            food_decay_per_step=decay,
            berry_effects={**config.berry_effects,
                           "berry_a": replace(config.berry_effects["berry_a"],
                                               food_gain=gain)},
        )
        layout = replace(layout, resources=((adjacent, "berry_a", quantity),))
    layout.validate(config)
    sleep = s10._stage10_config.sleep
    if sleep_name not in SLEEP_PROFILES:
        raise ValueError("undeclared sleep")
    sleep = replace(sleep, version="stage12-issue110-food-zero-wc-development-v1",
                    consolidation_weight=0.0)
    stage11_config = s11._stage11_config
    cfg9 = stage11_config.stage9
    cfg8 = cfg9.stage8
    cfg7 = cfg8.stage7
    cfg6 = cfg7.stage6
    horizon = 2 if sleep_name == "horizon_two" else 3
    if type(planning_depth) is not int or planning_depth not in (3, 4, 5, 6):
        raise ValueError("experimental Stage6 depth must be 3, 4, 5, or 6")
    revised6 = replace(
        cfg6,
        simulator=replace(cfg6.simulator,
                          version=("stage12-issue110-food-simulator-v1" if planning_depth == 3
                                   else f"stage12-issue110-food-simulator-depth{planning_depth}-v1"),
                          h_max=planning_depth),
        planning=replace(cfg6.planning,
                         version=("stage12-issue110-food-planner-v1" if planning_depth == 3
                                  else f"stage12-issue110-food-planner-depth{planning_depth}-v1")
                         + ("-progressive-prefix-v1" if progressive_evaluation_prefix else
                            "-progressive-v1" if progressive_planning else ""),
                         max_depth=planning_depth,
                         progressive_subgoals=progressive_planning,
                         progressive_evaluation_prefix=progressive_evaluation_prefix),
        evaluation=replace(cfg6.evaluation,
                           version="stage12-issue110-food-horizon-"+str(horizon)+"-v1",
                           h_eff=horizon),
    )
    stage11_config = replace(
        stage11_config,
        stage9=replace(cfg9, stage8=replace(
            cfg8, stage7=replace(cfg7, stage6=revised6),
        )),
    )
    combined = replace(s10._stage10_config, stage9=stage11_config.stage9,
                       sleep=sleep)
    training_layout = replace(layout, obstacles=frozenset())
    equipment = build_prebirth_equipment(
        config, training_layout, food_target=target_food,
    )
    from lab.injected_scenario import ScenarioEvent
    if a2_obstacle_clear_step is not None and (
            not a2_external_obstacle or type(a2_obstacle_clear_step) is not int
            or a2_obstacle_clear_step < 3):
        raise ValueError("A2 removal requires an obstacle and step >= 3")
    a2_events = (
        (ScenarioEvent(t_monde=2, sequence=0,
            operation="set_obstacle",
            payload={"position": {"x": 3, "y": 1}, "active": True},
            phase="after_admission"),)
        + ((ScenarioEvent(t_monde=a2_obstacle_clear_step, sequence=0,
            operation="set_obstacle",
            payload={"position": {"x": 3, "y": 1}, "active": False},
            phase="before_step"),) if a2_obstacle_clear_step is not None else ())
        if a2_external_obstacle else ()
    )
    life = Stage12Runtime(
        scenario_id=("issue110-a2-fixed-external" if a2_events else None),
        scenario_version=("a2-after-admission-v1" if a2_events else None),
        scenario_events=a2_events,
        world_config=config, layout=layout,
        safety_config=s11.stage3.substrate.safety._config,
        safety_facts=s11._canonical_safety._innate,
        protected_integrity_threshold=s11.stage3.control._config.protected_integrity_threshold,
        stage11_config=stage11_config, stage10_config=combined,
        equipment=equipment, autonomous_mortal=True,
        wal_path=wal_path, m11_sqlite_custody=m11_sqlite_custody,
        birth_life_id=birth_life_id,
        diagnostic_sample_cost_uc=1, module_occupancy_cost_uc=1,
        subjective_goal_agency=True, goal_agency_cost_uc=1,
        spatial_goal_progress=True, spatial_goal_cost_uc=1,
        spatial_agency_cost_uc=1,
        attribution_join=True, attribution_join_cost_uc=1,
        detector_policy=Stage12DetectionPolicy(
            version="stage12-issue110-food-first-person-v1", window=12,
            stagnation_steps=4, stagnation_tolerance=0.05,
            loop_repetitions=3, loop_max_period=2,
            entropy_min_samples=4, entropy_warning_fraction=0.25,
            bias_min_outcomes_each=2, attribution_bias_threshold=0.75))
    return life, config, layout, equipment


def run_life(
    folder: Path, world_name: str, water: float, sleep_name: str, *,
    cohort_id: str = "software-fixture",
) -> dict:
    if (type(cohort_id) is not str or not cohort_id
            or len(cohort_id) > 45
            or any(c not in "abcdefghijklmnopqrstuvwxyz"
                            "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-" for c in cohort_id)):
        raise ValueError("invalid or missing independent scientific cohort ID")
    birth_id = "i0:issue110:" + cohort_id + ":" + world_name + ":" + sleep_name
    life, config, layout, equipment = build_life(
        world_name, water, sleep_name,
        wal_path=str(folder / "life.wal"), birth_life_id=birth_id,
    )
    target_food = world_name.startswith("near_food")
    Stage12OperatorConsole(substrate=life.stage3.substrate, mode="campaign",
        policy_version="stage12-issue110-food-50-v1", maximum_world_steps=MAX_STEPS)
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
        agency = audit_stage12_first_person_agency(raw, **tail)
        pairs = audit_stage12_attribution_pairs(raw, **tail)
        spatial = audit_spatial_visible_cues(raw, **tail)
        spatial_criteria = sum(
            1 for row in life.journal.entries
            if row.causal_event.get("kind") == "stage12_goal_progress_preregistered"
            and row.causal_event.get("data", {}).get("contract_version")
                == "stage12-lived-goal-spatial-progress-v1"
        )
        pre_captures = {}
        motives = {}
        for item in life.journal.entries:
            ev = item.causal_event
            key = (ev.get("t_monde"), ev.get("attempt_ref"))
            if ev.get("kind") == "perceptual_capture":
                pre_captures[key] = ev["data"]
            if ev.get("kind") == "stage12_action_motive_attested":
                motives[key] = ev["data"]
        east = east_blocked = east_target_visible = east_target_goal = 0
        east_missing_first_person_cue = 0
        for item in life.journal.entries:
            ev = item.causal_event
            if (ev.get("kind") != "command_experienced"
                    or ev.get("primitive") != "se_deplacer"
                    or ev.get("parameters", {}).get("direction") != "east"):
                continue
            east += 1
            key = (ev["t_monde"], ev["attempt_ref"])
            candidates = [c for c in pre_captures.get(key, {}).get("agency_visible_adjacent", [])
                          if c.get("direction") == "east"]
            if not candidates:
                # Some admitted actions have only the baseline Stage3
                # position receipt. They are physically experienced but
                # NOT first-person agency evidence; abstain explicitly.
                east_missing_first_person_cue += 1
                continue
            if len(candidates) != 1:
                raise ValueError("ambiguous duplicated perceptual east cue")
            cue = candidates[0]
            east_blocked += int(not cue["passable"])
            relevant = ("berry_a" in cue["resources"]) if target_food else cue["water_source"]
            if relevant:
                east_target_visible += 1
                if motives.get(key, {}).get("motive_type") == "active_goal":
                    east_target_goal += 1
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
            "agency": agency.as_dict(),
            "attribution_pairs": pairs.as_dict(),
            "spatial_cue_receipts": spatial.as_dict(),
            "spatial_goal_criteria": spatial_criteria,
            "east_movements": east,
            "east_without_first_person_cue": east_missing_first_person_cue,
            "east_toward_perceived_blocked_cell": east_blocked,
            "east_toward_perceived_goal_target": east_target_visible,
            "east_toward_goal_target_with_active_goal_motive": east_target_goal,
            "context_detector_classes": {k: dict(v) for k,v in counts.items()},
        }
    except Exception as exc:
        audit_error = f"{type(exc).__name__}: {exc}"
    record = {
        "schema": "stage12-issue110-spatial-lived-state-life-v1",
        "world": world_name, "initial_water": water, "sleep_profile": sleep_name,
        "life_id": birth_id,
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
    parser.add_argument(
        "--cohort-id", default=(
            "gha" + os.environ.get("GITHUB_RUN_ID", "") + "a"
            + os.environ.get("GITHUB_RUN_ATTEMPT", "")
            if os.environ.get("GITHUB_RUN_ID") else None
        ),
        help="Unique identifier of independent scientific cohort; required locally",
    )
    args=parser.parse_args()
    if not args.cohort_id:
        parser.error("unique --cohort-id is required for independent cohort")
    root=args.output_dir.resolve()
    root.mkdir(parents=True, exist_ok=False)
    proc=subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,capture_output=True,text=True,check=True)
    rows=[]
    for name in WORLDS:
        for baseline_water in INITIAL_WATERS:
            # Never label water-goal lives as water70 when their actual
            # preregistered initial physical water was 20.
            water = baseline_water if name.startswith("near_food") else 20.0
            for sleep in SLEEP_PROFILES:
                label=f"{name}-water{int(water)}-{sleep}"
                sub=root/label
                sub.mkdir()
                try:
                    rows.append(run_life(
                        sub, name, water, sleep, cohort_id=args.cohort_id,
                    ))
                except BaseException as exc:
                    # Preserve all previous evidence and record the exception.
                    row={"world":name,"initial_water":water,"sleep_profile":sleep,
                         "error":f"{type(exc).__name__}: {exc}",
                         "executed_steps":0}
                    rows.append(row)
                    (sub/"runner-error.json").write_text(json.dumps(row))
                (root/"index.json").write_text(json.dumps(
                    {"source_sha":proc.stdout.strip(),
                      "cohort_id":args.cohort_id,"preregistration":
                     "docs/research/stage12-issue110-option-a-first-planning-state-prereg-2026-10-14.fr.md",
                     "n_planned":4,"n_completed":len(rows),"lives":rows,
                     "scientific_validation":"not_performed",
                     "operator_accepted":False},indent=2,sort_keys=True)+"\n")
    valid=[r for r in rows if "error" not in r and not r["audit_error"]]
    def total(section, key):
        return sum(x["audits"][section][key] for x in valid)
    summary={
        "schema":"stage12-issue110-spatial-lived-state-summary-v1",
        "source_sha":proc.stdout.strip(),"cohort_id":args.cohort_id,"planned_lives":4,
        "audited_lives":len(valid),
        "real_physical_steps":sum(x["executed_steps"] for x in valid),
        "failed_or_unverified_lives":len(rows)-len(valid),
        "non_null_goal_plans":sum(x["audits"]["non_null_plans"] for x in valid),
        "spatial_goal_criteria":sum(x["audits"]["spatial_goal_criteria"] for x in valid),
        "observed_east_movements":sum(x["audits"]["east_movements"] for x in valid),
        "east_without_first_person_cue":sum(x["audits"]["east_without_first_person_cue"] for x in valid),
        "observed_moves_into_blocked_east":sum(x["audits"]["east_toward_perceived_blocked_cell"] for x in valid),
        "observed_east_toward_perceived_target":sum(x["audits"]["east_toward_perceived_goal_target"] for x in valid),
        "observed_goal_motivated_east_toward_target":sum(x["audits"]["east_toward_goal_target_with_active_goal_motive"] for x in valid),
        "audited_adjacent_perceptions":sum(x["audits"]["spatial_cue_receipts"]["legal_adjacent_receipts"] for x in valid),
        "goal_precommits":total("goal_progress","preregistered_one_step_criteria"),
        "verified_successes":total("goal_progress","verified_one_step_resource_gains"),
        "verified_failures":total("goal_progress","verified_one_step_no_gains"),
        "agency_precommits":total("agency","precommits"),
        "agency_self":total("agency","judgements_self"),
        "agency_world":total("agency","judgements_world"),
        "agency_unknown":total("agency","judgements_unknown"),
        "agency_unavailable":total("agency","unavailable"),
        "agency_uc_charged":total("agency","charged_uc"),
        "agency_uc_refused":total("agency","refused_uc"),
        "admitted_pairs":total("attribution_pairs","admitted_pairs"),
        "applied_pairs":total("attribution_pairs","applied_pairs"),
        "join_uc_charged":total("attribution_pairs","join_uc"),
        "join_uc_refused":total("attribution_pairs","rejected_join_uc"),
        "actions":[{"equipment":x["world"],"horizon":x["sleep_profile"],
                    "actual_actions":x["actions"],"goal_plans":x["audits"]["non_null_plans"],
                    "agency_self":x["audits"]["agency"]["judgements_self"],
                    "pairs_admitted":x["audits"]["attribution_pairs"]["admitted_pairs"],
                    "failure":x["failure"]} for x in valid],
        "scientific_status":"exploratory_first_lived_state_no_scientific_go",
        "operator_accepted":False,"scientific_validation":"not_performed"}
    (root/"summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print(json.dumps(summary,sort_keys=True))
    return 0 if len(valid)==4 else 2


if __name__=="__main__":
    raise SystemExit(main())
