"""A2.30-S preregistered Stage3 observation probe on detached physics worlds.

Only living post-action captures may contribute to possible first-person evidence.
Terminal transitions are external physical records and never lived observations.
The P physical-fixture builder is reused, not its predictive learner or policy.
"""
from __future__ import annotations

import argparse
from collections import Counter
from itertools import combinations
import json
from pathlib import Path
import subprocess

from i0.interfaces import PrimitiveCommand
from i0.modules.perception import SymbolicPerception
from i0.modules.simulator import state_from_capture
from lab.determinism import canonical_causal_bytes, sha256_hex
from lab.world import WorldBody
from run_stage12_issue110_b_a230p_joint_prefix_experiment import build_physics

FOODS = (35.0, 45.0)
POSITIONS = ((5, 5), (7, 7))
VARIANTS = {
    "FOOD": ("benign", "toxin_7", "toxin_100"),
    "MOVE": ("clear", "danger_east_40", "lethal_east"),
    "DECAY": ("baseline", "food_decay_25", "water_decay_22"),
}
RISK_STEP = {"FOOD": 3, "MOVE": 2, "DECAY": 1}
WAIT = PrimitiveCommand("attendre")
PREFIX = {
    "FOOD": (
        WAIT, PrimitiveCommand("collecter", {"target": "berry_a"}),
        PrimitiveCommand("manger", {"target": "berry_a"}),
    ),
    "MOVE": (WAIT, PrimitiveCommand("se_deplacer", {"direction": "east"}), WAIT),
    "DECAY": (WAIT, WAIT, WAIT),
}
PHYSICAL_STEPS = {"FOOD": 36, "MOVE": 32, "DECAY": 36}


def first_person(world, time, perception):
    local = world.capture_local(t_monde=time).as_dict()
    sensed = perception.capture(local_state=local, telemetry=world.telemetry())
    return state_from_capture(
        capture=sensed, is_night=world.is_night(time)
    ).as_dict()


def single_world(family, variant, food, coords):
    physical_family = {"FOOD": "EAT", "MOVE": "MOV", "DECAY": "WAIT"}[family]
    config, layout = build_physics(
        physical_family, variant, food=food, position=coords,
    )
    world = WorldBody(config=config, layout=layout)
    sense = SymbolicPerception()
    identifier = f"a230s:{family}:{variant}:food{int(food)}:x{coords[0]}y{coords[1]}"
    initial = first_person(world, 1, sense)
    lived = [{"after_step": 0, "state": initial}]
    executed = []
    terminal_step = None
    for step, command in enumerate(PREFIX[family], 1):
        observed_before = first_person(world, step, sense)
        if observed_before != lived[-1]["state"]:
            raise AssertionError("noncontiguous accessible observation")
        transition = world.apply(command, t_monde=step)
        post_action = first_person(world, step + 1, sense)
        physical = {
            "step": step,
            "command": command.as_dict(),
            "before": observed_before,
            "after_for_external_audit_only": post_action,
            "terminal_for_external_audit_only": transition.lethal,
        }
        physical["physical_sha256"] = sha256_hex(
            canonical_causal_bytes(physical)
        )
        executed.append(physical)
        if transition.lethal:
            terminal_step = step
            world.freeze_terminal_state()
            break
        lived.append({"after_step": step, "state": post_action})
    if terminal_step is None and len(executed) != 3:
        raise AssertionError("nonterminal world truncated")
    return {
        "id": identifier, "family": family, "variant_external_only": variant,
        "food": food, "position": list(coords),
        "initial_capture_digest": sha256_hex(canonical_causal_bytes(initial)),
        "config_digest": config.digest(),
        "layout_digest": sha256_hex(canonical_causal_bytes(layout.as_dict())),
        "terminal_step_external_only": terminal_step,
        "steps_applied": len(executed),
        "possible_lived_captures": lived,
        "external_physical_evidence": executed,
        "postterminal_lived_capture_count": 0,
    }


def mutually_available_first_difference(one, two):
    a = {x["after_step"]: x["state"] for x in one["possible_lived_captures"]}
    b = {x["after_step"]: x["state"] for x in two["possible_lived_captures"]}
    for k in sorted(a.keys() & b.keys()):
        if a[k] != b[k]:
            return k
    return None


def study(outdir):
    outdir.mkdir(parents=True, exist_ok=False)
    examples = [
        single_world(family, var, food, pos)
        for family, variants in VARIANTS.items()
        for var in variants for food in FOODS for pos in POSITIONS
    ]
    pairs = []
    for family in VARIANTS:
        for food in FOODS:
            for pos in POSITIONS:
                siblings = [row for row in examples if
                            row["family"] == family and row["food"] == food
                            and tuple(row["position"]) == pos]
                if len(siblings) != 3 or len({
                    x["initial_capture_digest"] for x in siblings
                }) != 1:
                    raise AssertionError("latent physics leaked into perception")
                for a, b in combinations(siblings, 2):
                    first = mutually_available_first_difference(a, b)
                    if first == 0:
                        raise AssertionError("discriminated without any action")
                    pairs.append({
                        "family": family, "worlds": [a["id"], b["id"]],
                        "first_mutually_lived_difference": first,
                        "exposure_step": RISK_STEP[family],
                        "discrimination_before_exposure": (
                            first is not None and first < RISK_STEP[family]
                        ),
                        "one_or_both_terminal_external": bool(
                            a["terminal_step_external_only"]
                            or b["terminal_step_external_only"]
                        ),
                    })
    worlds_by_family = Counter(x["family"] for x in examples)
    steps_by_family = {
        kind: sum(x["steps_applied"] for x in examples if x["family"] == kind)
        for kind in VARIANTS
    }
    result = {
        "schema": "a230s-accessible-probes-physical-v1",
        "sha": subprocess.check_output(["git", "rev-parse", "HEAD"],
                                       text=True).strip(),
        "independent_lab_worlds": len(examples),
        "physical_lab_steps": sum(x["steps_applied"] for x in examples),
        "worlds_per_family": dict(worlds_by_family),
        "steps_per_family": steps_by_family,
        "external_terminals": sum(
            x["terminal_step_external_only"] is not None for x in examples
        ),
        "paired_comparisons": len(pairs),
        "jointly_lived_differences": sum(
            p["first_mutually_lived_difference"] is not None for p in pairs
        ),
        "jointly_lived_nonidentifications": sum(
            p["first_mutually_lived_difference"] is None for p in pairs
        ),
        "food_preexposure_distinctions": sum(
            p["family"] == "FOOD" and p["discrimination_before_exposure"]
            for p in pairs
        ),
        "move_preexposure_distinctions": sum(
            p["family"] == "MOVE" and p["discrimination_before_exposure"]
            for p in pairs
        ),
        "new_i0_births": 0,
        "new_i0_autonomous_steps": 0,
        "uc_cost_evaluated": False,
        "oracle_feedback_to_i0": False,
        "terminal_postcapture_considered_lived": False,
        "stage12": "PARTIAL",
        "issue110": "OPEN",
    }
    if (
        worlds_by_family != Counter({"FOOD":12, "MOVE":12, "DECAY":12})
        or steps_by_family != PHYSICAL_STEPS
        or result["physical_lab_steps"] != 104
        or len(pairs) != 36
        or result["external_terminals"] != 8
    ):
        raise AssertionError("physical preregistration count violated")
    (outdir / "a230s-worlds.json").write_text(
        json.dumps(examples, sort_keys=True, indent=2) + "\n"
    )
    (outdir / "a230s-pairs.json").write_text(
        json.dumps(pairs, sort_keys=True, indent=2) + "\n"
    )
    (outdir / "a230s-summary.json").write_text(
        json.dumps(result, sort_keys=True, indent=2) + "\n"
    )
    print("A230S_SUMMARY " + json.dumps(result, sort_keys=True), flush=True)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    study(args.output_dir)


if __name__ == "__main__":
    main()
