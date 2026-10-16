"""A2.30-L: physical counterexamples to unsafe Stage6 generalization.

All examples are independently applied in detached WorldBody training worlds.
The script NEVER constructs I0, Oracle or evaluation Bench; hidden physics
is used only by the external test and never added to cognitive observations.

Preregistered before code:
docs/research/stage12-issue110-b-a230l-adversarial-generalization-prereg-2026-10-15.fr.md
"""
from __future__ import annotations

import argparse
from dataclasses import replace
import json
from pathlib import Path
import subprocess

from i0.equipment import (
    EquipmentCorpus, FrozenTableEquipment, train_exact_transition_table,
)
from i0.interfaces import PrimitiveCommand
from lab.determinism import canonical_causal_bytes, sha256_hex
from lab.equipment_corpus import EquipmentCorpusRecorder
from lab.world import (
    WorldBody, WorldLayout, WorldPhysicsConfig, BodyState, Position,
    BerryEffect, ToolRecipe, PRIMITIVE_ACTIONS,
)


def _physical_record(config, layout, commands, label):
    """One NEW lab WorldBody, with only physically applied examples."""
    world = WorldBody(config=config, layout=layout)
    recorder = EquipmentCorpusRecorder(
        corpus_version="stage12-a230l-" + label + "-v1"
    )
    result = []
    for step, (family, command) in enumerate(commands, start=1):
        if result and result[-1].terminal:
            raise ValueError("no continuation after a terminal physical event")
        result.append(recorder.record_transition(
            world=world, t_monde=step, family=family, command=command
        ))
    return tuple(result)


def _state_hash(state):
    return sha256_hex(canonical_causal_bytes(state.as_dict()))


def _physical_output_hash(example):
    return sha256_hex(canonical_causal_bytes({
        "next_state": example.observed_next_state.as_dict(),
        "terminal": example.terminal,
    }))


def _check_exact_collision(left, right, label):
    if (_state_hash(left.state) != _state_hash(right.state)
        or left.command != right.command
        or FrozenTableEquipment.input_digest(
            left.state, left.command
        ) != FrozenTableEquipment.input_digest(
            right.state, right.command
        )):
        raise AssertionError("hidden-input counterexample not matched: " + label)
    if (left.observed_next_state == right.observed_next_state
            and left.terminal == right.terminal):
        raise AssertionError("hidden-input outcomes did not contrast: " + label)
    corpus = EquipmentCorpus(
        version="a230l-hidden-conflict-" + label + "-v1",
        examples=(left, right),
    )
    try:
        train_exact_transition_table(
            corpus=corpus, equipment_version="E-a230l-negative-control-v1"
        )
    except ValueError as err:
        if "conflicting outcomes" not in str(err):
            raise
    else:
        raise AssertionError(
            "exact trainer accepted contradictory accessible input: " + label
        )
    return {
        "identical_accessible_input": True,
        "identical_primitive": True,
        "input_digest_sha256": FrozenTableEquipment.input_digest(
            left.state, left.command
        ),
        "distinct_physical_consequences": True,
        "output_sha256": [_physical_output_hash(left),
                          _physical_output_hash(right)],
        "trainer_rejected_conflicting_outcomes": True,
        "left_terminal": left.terminal,
        "right_terminal": right.terminal,
    }


def physical_fixture_config() -> WorldPhysicsConfig:
    """Pure physics config, not a Stage4Runtime or living I0 instance."""
    return WorldPhysicsConfig(
        version="stage12-a230l-standalone-physics-v1",
        width=32, height=32, day_steps=300, night_steps=100,
        night_start_step=200,
        initial_body=BodyState(
            energy=50.0, food=60.0, water=20.0, integrity=100.0
        ),
        initial_position=Position(2, 2),
        food_decay_per_step=0.0,
        water_decay_per_step=0.0,
        action_energy_costs={
            k: 0.0 for k in sorted(PRIMITIVE_ACTIONS)
        },
        sleep_energy_gain=0.0,
        rest_integrity_gain=0.0,
        drink_water_gain=40.0,
        berry_effects={
            "berry_a": BerryEffect(10.0, 0.0),
            "berry_b": BerryEffect(5.0, -100.0),
        },
        creature_damage=0.0, danger_zone_damage=10.0,
        tool_recipe=ToolRecipe(1, 1, 2),
    )


def _one_sided_shadow(known, physically_held_out, label):
    """Shadow-only exact table trained on just the benign observation.

    The other *already recorded* physical case is never given to Equipment.
    No additional I0 world, intervention or physical step is executed.
    """
    model = train_exact_transition_table(
        corpus=EquipmentCorpus(
            version="stage12-a230m-single-example-" + label + "-v1",
            examples=(known,),
        ),
        equipment_version="E-a230m-one-sided-" + label + "-v1",
    )
    if FrozenTableEquipment.input_digest(
        known.state, known.command
    ) != FrozenTableEquipment.input_digest(
        physically_held_out.state, physically_held_out.command
    ):
        raise AssertionError("unmatched shadow training/counterfactual key")
    predicted = model.predict(
        state=physically_held_out.state,
        command=physically_held_out.command,
    )
    if (predicted.next_state != known.observed_next_state
            or predicted.terminal != known.terminal
            or predicted.confidence != 1.0):
        raise AssertionError("single-example exact-table contract changed")
    if (predicted.next_state == physically_held_out.observed_next_state
            and predicted.terminal == physically_held_out.terminal):
        raise AssertionError("one-sided shadow outcome unexpectedly correct")
    return {
        "trained_on_one_benign_physical_example": True,
        "same_accessible_input_exact_hash": True,
        "nominal_model_confidence": predicted.confidence,
        "predicted_terminal": predicted.terminal,
        "physically_observed_terminal": physically_held_out.terminal,
        "predicted_integrity": predicted.next_state.body["integrity"],
        "physically_observed_integrity":
            physically_held_out.observed_next_state.body["integrity"],
        "actual_hidden_world_outcome_mismatch": True,
        "not_executed_as_i0_model": True,
        "does_not_estimate_error_frequency": True,
    }


def run_physical_counterexamples():
    reference = physical_fixture_config()
    reference.validate()
    start = reference.initial_position
    move = PrimitiveCommand("se_deplacer", {"direction": "east"})
    current = WorldLayout()
    lethal = WorldLayout(
        lethal_zones=frozenset({start.moved("east")})
    )
    free_transition = _physical_record(
        reference, current, (("movement", move),), "move-safe"
    )[0]
    fatal_transition = _physical_record(
        reference, lethal, (("movement", move),), "move-lethal"
    )[0]
    move_pair = _check_exact_collision(
        free_transition, fatal_transition, "hidden-lethal-zone"
    )
    one_sided_move = _one_sided_shadow(
        free_transition, fatal_transition, "hidden-lethal-movement"
    )
    if (free_transition.terminal or not fatal_transition.terminal):
        raise AssertionError("lethal-zone physical contrast not demonstrated")
    if (free_transition.state.adjacent != fatal_transition.state.adjacent):
        raise AssertionError("hidden lethal zone leaked into local adjacency")

    # Contextual toxic effect differs only in *hidden world physics*.
    berry_a = reference.berry_effects["berry_a"]
    no_toxin = replace(
        reference, version="a230l-berry-safe-v1",
        berry_effects={**reference.berry_effects,
                       "berry_a": replace(berry_a, integrity_delta=0.0)},
    )
    toxin = replace(
        reference, version="a230l-berry-toxic-v1",
        berry_effects={**reference.berry_effects,
                       "berry_a": replace(berry_a, integrity_delta=-7.0)},
    )
    fruit = WorldLayout(resources=((start, "berry_a", 2),))
    collect = PrimitiveCommand("collecter", {"target": "berry_a"})
    eat = PrimitiveCommand("manger", {"target": "berry_a"})
    path = (("collection", collect), ("ingestion", eat))
    safe_path = _physical_record(no_toxin, fruit, path, "berry-safe")
    toxic_path = _physical_record(toxin, fruit, path, "berry-toxic")
    if safe_path[0].observed_next_state != toxic_path[0].observed_next_state:
        raise AssertionError("pre-ingestion collection unexpectedly differs")
    eat_pair = _check_exact_collision(
        safe_path[1], toxic_path[1], "hidden-berry-integrity"
    )
    sa = safe_path[1].observed_next_state
    sb = toxic_path[1].observed_next_state
    if (
        sa.body["food"] != sb.body["food"]
        or sa.body["integrity"] <= sb.body["integrity"]
        or safe_path[1].terminal or toxic_path[1].terminal
    ):
        raise AssertionError(
            "food/integrity contrast did not isolate hidden toxicity"
        )
    one_sided_berry = _one_sided_shadow(
        safe_path[1], toxic_path[1], "hidden-berry-toxicity"
    )
    eat_pair.update(
        food_after_pair=[sa.body["food"], sb.body["food"]],
        integrity_after_pair=[
            sa.body["integrity"], sb.body["integrity"]
        ],
        same_visible_berry_species="berry_a",
    )

    # A field *visible* to I0 still may be physically necessary for
    # absolute-valued predictions, even without any hidden hazard.
    low = replace(
        reference, version="a230l-low-food-v1",
        initial_body=replace(reference.initial_body, food=35.0),
    )
    high = replace(
        reference, version="a230l-high-food-v1",
        initial_body=replace(reference.initial_body, food=40.0),
    )
    wait = PrimitiveCommand("attendre")
    low_wait = _physical_record(
        low, WorldLayout(), (("wait", wait),), "wait-low-food"
    )[0]
    high_wait = _physical_record(
        high, WorldLayout(), (("wait", wait),), "wait-high-food"
    )[0]
    a = low_wait.state.as_dict()
    b = high_wait.state.as_dict()
    if (a["body"]["food"], b["body"]["food"]) != (35.0, 40.0):
        raise AssertionError("controlled initial food levels not preserved")
    # Every other accessible feature must be the same.
    a_without_food = {
        **a, "body": {k: v for k, v in a["body"].items() if k != "food"}
    }
    b_without_food = {
        **b, "body": {k: v for k, v in b["body"].items() if k != "food"}
    }
    if a_without_food != b_without_food:
        raise AssertionError("food value was not the sole changed input field")
    if (low_wait.observed_next_state.body["food"] ==
            high_wait.observed_next_state.body["food"]):
        raise AssertionError("absolute next-food values unexpectedly identical")
    wait_pair = {
        "same_primitive": True,
        "difference_in_accessible_input": "body.food",
        "all_other_accessible_input_fields_equal": True,
        "food_before": [35.0, 40.0],
        "food_after": [
            low_wait.observed_next_state.body["food"],
            high_wait.observed_next_state.body["food"],
        ],
        "distinct_absolute_next_food": True,
        "predicting_absolute_food_after_without_food_input_is_unsound": True,
    }

    return {
        "schema": "stage12-a230l-physical-nonidentifiability-v1",
        "physical_lab_worlds": 6,
        "physically_applied_lab_steps": 8,
        "new_individual_zero_births": 0,
        "new_i0_autonomous_steps": 0,
        "hidden_lethal_movement": move_pair,
        "hidden_toxic_ingestion": eat_pair,
        "one_sided_hidden_movement": one_sided_move,
        "one_sided_hidden_berry": one_sided_berry,
        "observable_food_difference": wait_pair,
        "deterministic_exact_predictor_must_abstain_on_conflict": True,
        "generalization_of_safety_proven": False,
        "target_life_data_used_for_training": False,
        "oracle_to_i0_feedback": False,
        "mvp_norm_changed": False,
        "stage12": "PARTIAL",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=False)
    result = run_physical_counterexamples()
    result["code_sha"] = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], text=True
    ).strip()
    (args.output_dir / "a230l-summary.json").write_text(
        json.dumps(result, sort_keys=True, indent=2) + "\n"
    )
    print("A230L_SUMMARY " + json.dumps(result, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
