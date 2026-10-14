"""A2.18: preregistered sequential first-person agency, external physical audit only.

No retrospective revision is implemented or inferred. The same real owner makes
two successive assessments; physical scenario truth never enters the owner.
"""
from dataclasses import asdict, replace
import argparse
import json
from pathlib import Path
import random
import subprocess

from i0.interfaces import PrimitiveCommand
from i0.modules.perception import SymbolicPerception
from i0.modules.stage12_goal_agency import GoalAgencyService
from lab.determinism import canonical_causal_bytes, sha256_hex
from lab.stage11_reference_fixture import build_stage11_reference_runtime
from lab.world import Position, WorldBody, WorldLayout

SEEDS = tuple(range(91, 99))
FAMILIES = ("success", "silent_failure", "new_obstacle")
ORIGINS = ("normal", "confounded")


def capture(world, step):
    return SymbolicPerception().capture(
        local_state=world.capture_local(t_monde=step).as_dict(),
        telemetry=world.telemetry(),
    )


def trial(config, seed, family, origin):
    rng = random.Random(seed * 991)
    start = Position(rng.randint(5, 19), rng.randint(5, 19))
    first = start.moved("east")
    second = first.moved("east")
    world = WorldBody(
        config=replace(config, initial_position=start),
        layout=WorldLayout(water_sources=frozenset({first, second})),
    )
    cmd = PrimitiveCommand("se_deplacer", {"direction": "east"})
    cmd_hash = sha256_hex(canonical_causal_bytes(cmd.as_dict()))
    owner = GoalAgencyService()
    before = capture(world, 1)
    commitments = []
    judgements = []
    physical = []
    interventions = []

    def register(step, observed, destination):
        assessment = owner.preregister(
            assessment_ref=f"assessment:{seed}:{family}:{origin}:{step}",
            intent_ref=f"intent:{seed}:{family}:{origin}:{step}",
            life_id=f"lab:{seed}:{family}:{origin}",
            goal_ref="goal:water", option_ref=f"option:move:{step}",
            command_hash=cmd_hash, world_step=step,
            measure="spatial_distance", command=cmd, capture=observed,
            spatial_target=(destination.x, destination.y, "water"),
        )
        commitments.append(assessment.as_dict())

    def evaluate(step, observed):
        result = owner.evaluate(
            capture=observed, world_step=step,
            cue_ref=f"physical:perception:{seed}:{family}:{origin}:{step}",
            paid=True,
        )
        assert result is not None and result.cue_ref
        judgements.append(result.as_dict())

    register(1, before, first)
    if origin == "confounded":
        event = {"primitive": "se_deplacer", "schedule": [True]}
        world.apply_scenario_event("set_action_failure_schedule", event)
        interventions.append({"step": 1, "operation": "set_action_failure_schedule", "payload": event})
    first_effect = world.apply(cmd, t_monde=1)
    first_before_intervention = world.position.as_dict()
    physical.append({"step": 1, "transition_sha256": sha256_hex(
        canonical_causal_bytes(first_effect.as_dict())),
        "effects": dict(first_effect.effects),
        "position_after_command": first_before_intervention,
    })
    if origin == "confounded":
        assert first_effect.effects.get("scenario_forced_failure") == "se_deplacer"
        assert first_before_intervention == start.as_dict()
        event = {"position": first.as_dict()}
        world.apply_scenario_event("set_position", event)
        interventions.append({"step": 1, "operation": "set_position", "payload": event})
    else:
        assert first_effect.effects.get("movement") == "moved"
        assert first_before_intervention == first.as_dict()

    middle = capture(world, 2)
    evaluate(2, middle)
    assert judgements[0]["subjective_agency"] == "self"
    register(2, middle, second)
    if family == "silent_failure":
        event = {"primitive": "se_deplacer", "schedule": [True]}
        world.apply_scenario_event("set_action_failure_schedule", event)
        interventions.append({"step": 2, "operation": "set_action_failure_schedule", "payload": event})
    if family == "new_obstacle":
        event = {"position": second.as_dict(), "active": True}
        world.apply_scenario_event("set_obstacle", event)
        interventions.append({"step": 2, "operation": "set_obstacle", "payload": event})
    second_effect = world.apply(cmd, t_monde=2)
    physical.append({"step": 2, "transition_sha256": sha256_hex(
        canonical_causal_bytes(second_effect.as_dict())),
        "effects": dict(second_effect.effects),
        "position_after_command": world.position.as_dict(),
    })
    after = capture(world, 3)
    evaluate(3, after)

    expected = {"success": "self", "silent_failure": "unknown", "new_obstacle": "world"}[family]
    assert judgements[1]["subjective_agency"] == expected
    assert judgements[0]["assessment_ref"] != judgements[1]["assessment_ref"]
    assert len(owner.export_causal_state()["seen_assessment_refs"]) == 2
    assert len(physical) == 2
    if family == "success":
        assert second_effect.effects.get("movement") == "moved"
        assert (after.x, after.y) == (second.x, second.y)
    elif family == "silent_failure":
        assert second_effect.effects.get("scenario_forced_failure") == "se_deplacer"
        assert (after.x, after.y) == (first.x, first.y)
    else:
        assert second_effect.effects.get("movement") == "blocked"
        assert (after.x, after.y) == (first.x, first.y)
    perceptions = [asdict(p) for p in (before, middle, after)]
    return {
        "seed": seed, "family": family, "origin": origin,
        "perceptions": perceptions,
        "perception_sha256": [sha256_hex(canonical_causal_bytes(p)) for p in perceptions],
        "commitments": commitments, "judgements": judgements,
        "physical": physical, "interventions": interventions,
        "retrospective_revision_observed": False,
        "proximal_distal_agency_conflated": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=False)
    cfg = build_stage11_reference_runtime().world.config
    pairs = 0
    worlds = transitions = relocations = obstacles = silent = 0
    outcomes = {}
    for seed in SEEDS:
        for family in FAMILIES:
            normal = trial(cfg, seed, family, "normal")
            confounded = trial(cfg, seed, family, "confounded")
            # Absolute inputs and all local captures must be equal, not only final position.
            assert normal["perceptions"] == confounded["perceptions"]
            assert normal["perception_sha256"] == confounded["perception_sha256"]
            assert [r["subjective_agency"] for r in normal["judgements"]] == [
                r["subjective_agency"] for r in confounded["judgements"]]
            # First transition differs in physical causal origin despite identical captures.
            assert normal["physical"][0]["effects"] != confounded["physical"][0]["effects"]
            pairs += 1
            for row in (normal, confounded):
                worlds += 1
                transitions += len(row["physical"])
                relocations += sum(e["operation"] == "set_position" for e in row["interventions"])
                obstacles += sum(e["operation"] == "set_obstacle" for e in row["interventions"])
                silent += int(family == "silent_failure")
                sequence = "->".join(r["subjective_agency"] for r in row["judgements"])
                outcomes[sequence] = outcomes.get(sequence, 0) + 1
                name = f'{family}-{row["origin"]}-{seed}.json'
                (args.output_dir / name).write_text(json.dumps(row, sort_keys=True, indent=2) + "\n")
    summary = {
        "schema": "stage12-a218-sequential-agency-v1",
        "code_sha": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "seeds": list(SEEDS), "physical_worlds": worlds, "physical_transitions": transitions,
        "confounded_pairs": pairs, "external_relocations": relocations,
        "second_step_silent_failures": silent, "new_obstacles": obstacles,
        "judgement_sequences": outcomes, "retrospective_revisions": 0,
        "autonomous_lives": 0, "ga06_pairs_from_probe": 0,
        "runtime_policy_changed": False, "stage12": "PARTIAL",
        "operator_reception": False,
    }
    assert (worlds, transitions, pairs, relocations, silent, obstacles) == (48, 96, 24, 24, 16, 16)
    assert outcomes == {"self->self": 16, "self->unknown": 16, "self->world": 16}
    (args.output_dir / "a218-summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print("A218_SUMMARY " + json.dumps(summary, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
