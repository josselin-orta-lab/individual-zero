"""A2.30-T: shadow-only food opportunities versus physically observed outcomes.

The P laboratory model is frozen from sealed P TRAINING records before any
new T world is created. Forecasts use only Stage3 first-person captures.
No I0 instance, no Stage6 plan adoption, no model-selected action, no oracle
feedback and no after-death subjective observation. Independent WorldBody
cells are physically applied ONLY to score the external counterfactuals.

Preregistered at 1df0a78f96bb53d556f0f939dec8651cf1b3ab8c.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import subprocess

from i0.equipment import SimulationNeighbor, SimulationState
from i0.interfaces import PrimitiveCommand
from i0.modules.perception import SymbolicPerception
from i0.modules.simulator import state_from_capture
from i0.modules.stage6_planning import SimulatorPlanner
from lab.determinism import canonical_causal_bytes, sha256_hex
from lab.world import WorldBody
from run_stage12_issue110_b_a230p_joint_prefix_experiment import build_physics
from audit_stage12_issue110_b_a230p_joint_trajectories import (
    JointStep, PhysicalPrefixWitness, LaboratoryJointPrefixModel,
)

ORIGINAL_P_RUN = 38730415503
ORIGINAL_P_SHA = "3ab03a90b38d6c968cddcd9ed699c3f089d0544c"
ORIGINAL_P_TRAINING_SHA = (
    "f706cd25a31b8f716c4bb0a5a7e617bed87c0b8b47577d8b9dd31221cf23839e"
)
FOODS = (35.0, 45.0)
POSITIONS = ((5,5), (7,7))
LATENTS = ("benign", "toxin_7", "toxin_30", "toxin_100", "gain_zero")
ARMS = ("no_wait", "wait_first")
COLLECT = PrimitiveCommand("collecter", {"target": "berry_a"})
EAT = PrimitiveCommand("manger", {"target": "berry_a"})
WAIT = PrimitiveCommand("attendre")
PREFIX = (COLLECT, EAT, WAIT)


def as_state(src):
    state = SimulationState(
        schema_version=src["schema_version"],
        x=src["x"], y=src["y"], body=src["body"],
        inventory=src["inventory"],
        current_water_source=src["current_water_source"],
        current_resources=tuple(src["current_resources"]),
        adjacent=tuple(SimulationNeighbor(
            direction=n["direction"], x=n["x"], y=n["y"],
            passable=n["passable"], water_source=n["water_source"],
            resources=tuple(n["resources"]), creature=n["creature"],
        ) for n in src["adjacent"]),
        known_shelter_here=src["known_shelter_here"],
        is_night=src["is_night"],
    )
    state.validate()
    if state.as_dict() != src:
        raise AssertionError("P source state altered by reconstruction")
    return state


def load_locked_training(directory: Path):
    matches = list(directory.rglob("a230p-training-manifest.json"))
    if len(matches) != 1:
        raise ValueError("P original training artifact missing or ambiguous")
    raw = matches[0].read_bytes()
    if sha256(raw).hexdigest() != ORIGINAL_P_TRAINING_SHA:
        raise ValueError("original training SHA-256 does not match preregistration")
    source = json.loads(raw)
    original = source["training_witnesses"]
    if len(original) != 48 or source["physical_training_worlds"] != 48:
        raise ValueError("not original 48-world P training cohort")
    if sha256_hex(canonical_causal_bytes(original)) != source[
        "training_witness_corpus_sha256"
    ]:
        raise ValueError("P training witness corpus digest diverged")
    witnesses = []
    for row in original:
        entry = PhysicalPrefixWitness(
            world_id=row["world_id"],
            initial=as_state(row["initial"]),
            commands=tuple(PrimitiveCommand(
                x["primitive"], x["parameters"]
            ) for x in row["commands"]),
            steps=tuple(JointStep(
                cumulative_delta=step["cumulative_delta"],
                terminal=step["terminal"],
            ) for step in row["steps"]),
        )
        entry.validate()
        witnesses.append(entry)
    # NO physical T world is instantiated before the model is frozen.
    model = LaboratoryJointPrefixModel(tuple(witnesses))
    if model.training_worlds != 48 or model.contexts != 3:
        raise AssertionError("P model was retrained on wrong corpus")
    return model, source["training_witness_corpus_sha256"]


def accessible(world, time, perception):
    capture = perception.capture(
        local_state=world.capture_local(t_monde=time).as_dict(),
        telemetry=world.telemetry(),
    )
    return state_from_capture(
        capture=capture, is_night=world.is_night(time)
    )


def shadow_receipt(model, state, *, t_monde):
    """A potential plan, never an adopted Stage6 option or command."""
    before = state.as_dict()
    candidates = SimulatorPlanner.candidate_commands(state)
    if COLLECT not in candidates or EAT in candidates:
        raise AssertionError("food-action preconditions are not as preregistered")
    forecast = model.forecast(initial=state, commands=PREFIX)
    if (
        forecast.status != "observed_joint_branches"
        or len(forecast.branches) != 4
        or forecast.risk_label != "observed_terminal_possible"
        or 2 not in forecast.observed_terminal_steps
        or forecast.certifies_safe
        or not forecast.could_have_unobserved_hidden_hazard
    ):
        raise AssertionError("shadow received false certainty or wrong P corpus")
    # A physically living food goal requires survival after ingestion AND
    # a +5 body.food gain. A terminally dead body is NOT an experienced meal.
    branch_scores = []
    for branch in forecast.branches:
        step2 = branch.observed_steps[1] if len(branch.observed_steps) >= 2 else None
        surviving = (
            step2 is not None and (
                branch.first_terminal_step is None or
                branch.first_terminal_step > 2
            )
        )
        food_gain = (
            None if step2 is None else
            float(step2["cumulative_delta"]["body.food"])
        )
        branch_scores.append({
            "physical_training_worlds": branch.physical_training_worlds,
            "observed_first_terminal_step": branch.first_terminal_step,
            "predicted_food_gain_after_ingestion": food_gain,
            "surviving_food_goal_possible_in_branch": bool(
                surviving and food_gain is not None and food_gain >= 5.0
            ),
        })
    optimistic = any(x["surviving_food_goal_possible_in_branch"]
                     for x in branch_scores)
    robust = all(x["surviving_food_goal_possible_in_branch"]
                 for x in branch_scores)
    return {
        "input_stage3_state": before,
        "input_digest_sha256": sha256_hex(canonical_causal_bytes(before)),
        "forecast_time_t_monde": t_monde,
        "model_version": model.version,
        "context_group_key": forecast.context_key,
        "training_worlds_in_context": forecast.evidence_worlds,
        "observed_joint_branches": len(forecast.branches),
        "observed_terminal_steps": list(forecast.observed_terminal_steps),
        "risk_label": forecast.risk_label,
        "uncertainty_unobserved_causes_not_excluded": True,
        "optimistic_goal_exists": optimistic,
        "all_observed_branches_survive_and_meet_goal": robust,
        "shadow_risk_veto": bool(forecast.observed_terminal_steps),
        "certifies_safe": False,
        "read_only_stage6_candidate_collect_available": True,
        "read_only_stage6_candidate_eat_unavailable_before_collect": True,
        "branch_scores": branch_scores,
    }


def applied_world(model, latent, food, coords, arm):
    """Model cannot select any action; precommitted lab prefix is immutable."""
    if latent not in LATENTS or arm not in ARMS:
        raise ValueError("unregistered T treatment cell")
    config, layout = build_physics(
        "EAT", latent, food=food, position=coords
    )
    world = WorldBody(config=config, layout=layout)
    perception = SymbolicPerception()
    identifier = (
        f"a230t:{arm}:{latent}:food{int(food)}:x{coords[0]}y{coords[1]}"
    )
    before_probe = accessible(world, 1, perception)
    operations = []
    steps = 0
    terminal_step = None
    current_alive = before_probe
    if arm == "wait_first":
        transition = world.apply(WAIT, t_monde=1)
        if transition.lethal:
            raise AssertionError("prereg wait control unexpectedly terminal")
        steps = 1
        current_alive = accessible(world, 2, perception)
        operations.append({
            "t_monde": 1, "command": WAIT.as_dict(),
            "physical_after": current_alive.as_dict(),
            "terminal_external_only": False,
        })
    forecast = shadow_receipt(model, current_alive, t_monde=steps + 1)
    # The model's output does NOT feed the physical motor schedule.
    forecast_frozen_sha = sha256_hex(canonical_causal_bytes(forecast))
    food_at_decision = float(current_alive.body["food"])
    after_collect = None
    after_ingestion_external = None
    alive_after_ingestion = False
    for command in PREFIX:
        steps += 1
        before = accessible(world, steps, perception)
        transition = world.apply(command, t_monde=steps)
        after = accessible(world, steps+1, perception)
        if command == COLLECT:
            after_collect = after
            candidates = SimulatorPlanner.candidate_commands(after)
            if EAT not in candidates or before.inventory.get("berry_a",0):
                raise AssertionError("Stage6 food affordance not independently reproduced")
        if command == EAT:
            after_ingestion_external = after
            alive_after_ingestion = not transition.lethal
        operations.append({
            "t_monde": steps, "command": command.as_dict(),
            "physical_after": after.as_dict(),
            "terminal_external_only": transition.lethal,
        })
        if transition.lethal:
            terminal_step = steps
            world.freeze_terminal_state()
            break
    if after_collect is None or after_ingestion_external is None:
        raise AssertionError("the food action was not physically applied")
    survived_with_food = bool(
        alive_after_ingestion and
        float(after_ingestion_external.body["food"]) - food_at_decision >= 5.0
    )
    post_ingestion_lived = (
        after_ingestion_external.as_dict() if alive_after_ingestion else None
    )
    return {
        "id": identifier,
        "arm": arm, "latent_external_only": latent,
        "starting_food": food,
        "starting_position": list(coords),
        "physical_config_sha256": config.digest(),
        "physical_layout_sha256": sha256_hex(canonical_causal_bytes(layout.as_dict())),
        "preprobe_stage3_state": before_probe.as_dict(),
        "decision_stage3_state": current_alive.as_dict(),
        "decision_food": food_at_decision,
        "shadow_forecast_precommitted": forecast,
        "shadow_sha256_before_all_food_actions": forecast_frozen_sha,
        "physical_operations_not_chosen_by_shadow": operations,
        "real_physical_steps": steps,
        "terminal_step_external_only": terminal_step,
        "physically_alive_after_ingestion": alive_after_ingestion,
        "actual_food_gain_after_ingestion_external": (
            float(after_ingestion_external.body["food"]) - food_at_decision
        ),
        "potential_lived_post_ingestion_if_survivor": post_ingestion_lived,
        "physical_food_goal_with_survival_external": survived_with_food,
        "no_command_emitted_to_i0": True,
        "no_subj_agency_claim": True,
    }


def run(source_training: Path, output_dir: Path):
    model, training_sha = load_locked_training(source_training)
    output_dir.mkdir(parents=True, exist_ok=False)
    all_rows = [
        applied_world(model, latent, food, coords, arm)
        for latent in LATENTS for food in FOODS for coords in POSITIONS
        for arm in ARMS
    ]
    if len({x["id"] for x in all_rows}) != 40:
        raise AssertionError("duplicate T physics world identifier")
    paired = []
    for latent in LATENTS:
        for food in FOODS:
            for coords in POSITIONS:
                old, new = (
                    next(x for x in all_rows if x["latent_external_only"] == latent
                         and x["starting_food"] == food
                         and tuple(x["starting_position"]) == coords
                         and x["arm"] == arm)
                    for arm in ARMS
                )
                if old["preprobe_stage3_state"] != new["preprobe_stage3_state"]:
                    raise AssertionError("unpaired physical initial observation")
                if (
                    old["shadow_forecast_precommitted"]["context_group_key"]
                    != new["shadow_forecast_precommitted"]["context_group_key"]
                ):
                    raise AssertionError("waiting changed only visible bodily values")
                if (
                    old["shadow_forecast_precommitted"]["risk_label"]
                    != new["shadow_forecast_precommitted"]["risk_label"]
                ):
                    raise AssertionError("wait fabricated or hid risk")
                paired.append({
                    "latent_external_only": latent, "food": food,
                    "coords": list(coords),
                    "no_wait_id": old["id"], "wait_first_id": new["id"],
                    "same_initial_perception": True,
                    "same_observed_branch_risk": True,
                    "physical_food_goal_no_wait":
                        old["physical_food_goal_with_survival_external"],
                    "physical_food_goal_wait_first":
                        new["physical_food_goal_with_survival_external"],
                    "terminal_in_both_arms": (
                        old["terminal_step_external_only"] is not None and
                        new["terminal_step_external_only"] is not None
                    ),
                    "food_cost_waiting_extra": (
                        float(new["physical_operations_not_chosen_by_shadow"][-1]
                              ["physical_after"]["body"]["food"])
                        - float(old["physical_operations_not_chosen_by_shadow"][-1]
                                ["physical_after"]["body"]["food"])
                    ),
                })
    per_arm = {}
    for arm in ARMS:
        rows = [r for r in all_rows if r["arm"] == arm]
        per_arm[arm] = {
            "physical_worlds": len(rows),
            "physical_steps": sum(r["real_physical_steps"] for r in rows),
            "shadow_optimistic_goals": sum(
                r["shadow_forecast_precommitted"]["optimistic_goal_exists"]
                for r in rows
            ),
            "shadow_observed_branch_robust_goals": sum(
                r["shadow_forecast_precommitted"]
                ["all_observed_branches_survive_and_meet_goal"]
                for r in rows
            ),
            "shadow_risk_veto": sum(
                r["shadow_forecast_precommitted"]["shadow_risk_veto"]
                for r in rows
            ),
            "physical_surviving_food_goal": sum(
                r["physical_food_goal_with_survival_external"] for r in rows
            ),
            "external_terminal_worlds": sum(
                r["terminal_step_external_only"] is not None for r in rows
            ),
            "optimistic_false_food_success_external": sum(
                r["shadow_forecast_precommitted"]["optimistic_goal_exists"]
                and not r["physical_food_goal_with_survival_external"]
                for r in rows
            ),
        }
    report = {
        "schema": "a230t-shadow-food-planning-v1",
        "code_sha": subprocess.check_output(
            ["git","rev-parse","HEAD"], text=True
        ).strip(),
        "sealed_training_from_run": ORIGINAL_P_RUN,
        "sealed_training_code_sha": ORIGINAL_P_SHA,
        "sealed_training_archive_sha256": ORIGINAL_P_TRAINING_SHA,
        "sealed_training_witness_sha256": training_sha,
        "model_pretrained_and_frozen_before_all_worlds": True,
        "stage6_command_candidates_only_not_plans": True,
        "shadow_does_not_command_physics": True,
        "new_independent_lab_worlds": len(all_rows),
        "new_lab_physical_steps": sum(r["real_physical_steps"] for r in all_rows),
        "new_i0_births": 0,
        "new_autonomous_i0_steps": 0,
        "external_deaths": sum(
            r["terminal_step_external_only"] is not None for r in all_rows
        ),
        "shadow_safety_certificates": sum(
            r["shadow_forecast_precommitted"]["certifies_safe"] for r in all_rows
        ),
        "per_arm": per_arm,
        "paired_worlds": len(paired),
        "stage12": "PARTIAL", "issue110": "OPEN",
        "no_cognitive_runtime_changed": True,
        "uncalibrated_latent_danger_not_excluded": True,
    }
    if (
        report["new_lab_physical_steps"] != 132
        or per_arm["no_wait"]["physical_steps"] != 56
        or per_arm["wait_first"]["physical_steps"] != 76
        or report["external_deaths"] != 8
        or report["shadow_safety_certificates"] != 0
        or len(paired) != 20
    ):
        raise AssertionError("physical shadow preregistration was violated")
    (output_dir/"a230t-worlds.json").write_text(
        json.dumps(all_rows,indent=2,sort_keys=True) + "\n"
    )
    (output_dir/"a230t-paired.json").write_text(
        json.dumps(paired,indent=2,sort_keys=True) + "\n"
    )
    (output_dir/"a230t-summary.json").write_text(
        json.dumps(report,indent=2,sort_keys=True) + "\n"
    )
    print("A230T_SUMMARY "+json.dumps(report,sort_keys=True),flush=True)
    return report


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source-training",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    a = p.parse_args()
    run(a.source_training,a.output_dir)


if __name__ == "__main__":
    main()
