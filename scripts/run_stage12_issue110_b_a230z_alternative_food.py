"""A2.30-Z: preregistered alternative food, perceptual policy and Stage6 shadow.

Research-only physical laboratory. No I0 individual is instantiated; no
simulator/shadow action is ever physically dispatched. The bench owns hidden
berry effects, but policy inputs contain *only* a first-person SimulationState
and the fixed protocol choice. Actions stop on the first physical death.

All 168 independent worlds and 244 physical steps were locked BEFORE code in:
docs/research/stage12-issue110-b-a230z-physical-matrix-lock-2026-10-15.fr.md.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import replace
from itertools import product
import json
from pathlib import Path
import subprocess

from i0.equipment import EquipmentCorpus, train_exact_transition_table
from i0.interfaces import PrimitiveCommand
from i0.modules.perception import SymbolicPerception
from i0.modules.simulator import Simulator, SimulatorConfig, state_from_capture
from i0.modules.stage6_planning import SimulatorPlanner, Stage6PlanningConfig
from lab.determinism import canonical_causal_bytes, sha256_hex
from lab.equipment_corpus import EquipmentCorpusRecorder
from lab.world import Position, WorldBody, WorldLayout

from run_stage12_issue110_b_a230l_counterexamples import physical_fixture_config

LAYOUTS = (
    "A_ONLY", "B_LOCAL", "B_EAST_BLOCKED",
    "B_EAST_ADJACENT", "B_EAST_TWO_STEPS",
)
POLICIES = ("OBSERVED_ONLY", "SINGLE_EAST_PROBE")
FOODS = (35.0, 45.0)
POSITIONS = ((5, 5), (7, 7))
A_HIDDEN = ("benign", "toxin_7", "toxin_30", "toxin_100", "gain_zero")
B_HIDDEN = ("benign", "toxin_7", "toxin_100", "gain_zero")
EXPECTED_STEPS_BY_LAYOUT_POLICY = {
    ("A_ONLY", "OBSERVED_ONLY"): (20, 0),
    ("A_ONLY", "SINGLE_EAST_PROBE"): (20, 20),
    ("B_LOCAL", "OBSERVED_ONLY"): (16, 32),
    ("B_LOCAL", "SINGLE_EAST_PROBE"): (16, 32),
    ("B_EAST_BLOCKED", "OBSERVED_ONLY"): (16, 0),
    ("B_EAST_BLOCKED", "SINGLE_EAST_PROBE"): (16, 0),
    ("B_EAST_ADJACENT", "OBSERVED_ONLY"): (16, 48),
    ("B_EAST_ADJACENT", "SINGLE_EAST_PROBE"): (16, 48),
    ("B_EAST_TWO_STEPS", "OBSERVED_ONLY"): (16, 0),
    ("B_EAST_TWO_STEPS", "SINGLE_EAST_PROBE"): (16, 64),
}
EXPECTED_WORLDS = 168
EXPECTED_STEPS = 244
EXPECTED_INGESTIONS = 80
EXPECTED_TERMINALS = 20
EXPECTED_FOOD_SUCCESSES = 40
EXPECTED_INSUFFICIENT = 20
EXPECTED_NO_EAT = 88
EXPECTED_SHADOW_QUERIES = 80

EAST = PrimitiveCommand("se_deplacer", {"direction": "east"})
COLLECT_B = PrimitiveCommand("collecter", {"target": "berry_b"})
EAT_B = PrimitiveCommand("manger", {"target": "berry_b"})

ACCESSIBLE_KEYS = frozenset({
    "schema_version", "x", "y", "body", "inventory",
    "current_resources", "current_water_source", "adjacent",
    "known_shelter_here", "is_night",
})


def digest(payload):
    return sha256_hex(canonical_causal_bytes(payload))


def first_person(world: WorldBody, t: int):
    capture = SymbolicPerception().capture(
        local_state=world.capture_local(t_monde=t).as_dict(),
        telemetry=world.telemetry(),
    )
    state = state_from_capture(
        capture=capture, is_night=world.is_night(t),
    )
    state.validate()
    return state


def assert_accessible(state):
    if not isinstance(state, dict) or set(state) != ACCESSIBLE_KEYS:
        raise ValueError("hidden or future information in first-person state")
    if set(state["body"]) != {"energy", "food", "water", "integrity"}:
        raise ValueError("first-person body incomplete")
    if not isinstance(state["adjacent"], list) or len(state["adjacent"]) != 4:
        raise ValueError("neighbor perception incomplete")


def east_neighbor(state):
    """Only adjacent *accessible* capture, no WorldBody or world-layout data."""
    found = [n for n in state["adjacent"] if n["direction"] == "east"]
    if len(found) != 1:
        raise ValueError("east-facing first-person neighbor absent")
    return found[0]


def perceptual_food_policy(state, protocol, previous_commands):
    """Frozen finite decision function; NO access to physical configuration.

    One time-limited scouting move is permitted only when B is not currently
    visible and east is passable. The protocol itself is precommitted by Lab;
    this is not I0's option/goal competition or learned food policy.
    """
    assert_accessible(state)
    if protocol not in POLICIES:
        raise ValueError("unregistered protocol")
    for command in previous_commands:
        if command not in (EAST, COLLECT_B, EAT_B):
            raise ValueError("policy history contains a foreign command")
    if EAT_B in previous_commands:
        return None, "already_consumed_one_berry_b"
    if int(state["inventory"].get("berry_b", 0)) > 0:
        return EAT_B, "held_berry_b_accessible"
    if "berry_b" in state["current_resources"]:
        return COLLECT_B, "local_berry_b_visible"
    neighbor = east_neighbor(state)
    if "berry_b" in neighbor["resources"]:
        if neighbor["passable"]:
            return EAST, "eastern_berry_b_visible_passable"
        return None, "eastern_berry_b_visible_but_blocked"
    if (protocol == "SINGLE_EAST_PROBE"
        and not previous_commands and bool(neighbor["passable"])):
        return EAST, "one_blind_eastern_probe"
    return None, "no_visible_accessible_berry_b_abstain"


def build_physics(layout_name, hidden, food, position):
    """World configuration remains EXTERNAL to all decisions and Stage6."""
    if layout_name not in LAYOUTS:
        raise ValueError("unexpected physical layout")
    expected = A_HIDDEN if layout_name == "A_ONLY" else B_HIDDEN
    if hidden not in expected:
        raise ValueError("nonpreregistered hidden outcome")
    ref = physical_fixture_config()
    point = Position(*position)
    effects = dict(ref.berry_effects)
    if layout_name == "A_ONLY":
        effects["berry_a"] = replace(
            effects["berry_a"],
            food_gain=0.0 if hidden == "gain_zero" else 10.0,
            integrity_delta={
                "benign": 0.0, "toxin_7": -7.0,
                "toxin_30": -30.0, "toxin_100": -100.0,
                "gain_zero": 0.0,
            }[hidden],
        )
        effects["berry_b"] = replace(
            effects["berry_b"], food_gain=12.0, integrity_delta=0.0,
        )
    else:
        effects["berry_a"] = replace(
            effects["berry_a"], food_gain=10.0,
            integrity_delta=-100.0,
        )
        effects["berry_b"] = replace(
            effects["berry_b"],
            food_gain=0.0 if hidden == "gain_zero" else 12.0,
            integrity_delta={
                "benign": 0.0, "toxin_7": -7.0,
                "toxin_100": -100.0, "gain_zero": 0.0,
            }[hidden],
        )
    cost = dict(ref.action_energy_costs)
    cost.update({
        "se_deplacer": 1.0, "collecter": 0.75,
        "manger": 0.5, "attendre": 0.5,
    })
    config = replace(
        ref,
        version="stage12-a230z-alternative-food-pure-world-v1",
        initial_body=replace(ref.initial_body, food=float(food)),
        initial_position=point,
        berry_effects=effects,
        action_energy_costs=cost,
        food_decay_per_step=0.5, water_decay_per_step=0.2,
        rest_integrity_gain=0.0,
    )
    local = ((point, "berry_a", 2),)
    east = point.moved("east")
    two_east = east.moved("east")
    if layout_name == "B_LOCAL":
        resources = local + ((point, "berry_b", 2),)
    elif layout_name in ("B_EAST_BLOCKED", "B_EAST_ADJACENT"):
        resources = local + ((east, "berry_b", 2),)
    elif layout_name == "B_EAST_TWO_STEPS":
        resources = local + ((two_east, "berry_b", 2),)
    else:
        resources = local
    obstacles = (frozenset({east}) if layout_name == "B_EAST_BLOCKED"
                 else frozenset())
    layout = WorldLayout(resources=resources, obstacles=obstacles)
    config.validate()
    layout.validate(config)
    return config, layout


def locked_cells():
    for layout in LAYOUTS:
        hidden_variants = A_HIDDEN if layout == "A_ONLY" else B_HIDDEN
        for protocol, hidden, food, position in product(
            POLICIES, hidden_variants, FOODS, POSITIONS,
        ):
            yield {
                "layout_name": layout, "protocol": protocol,
                "hidden": hidden, "food": food, "position": position,
            }


def own_past_shadow_search(*, world_id, t, state, own_history):
    """Actual Stage6 algorithm, but IDEALIZED and entirely passive.

    The sole corpus consists of previous WorldBody.apply consequences of the
    exact SAME standalone world, observed before t. No oracle or heldout
    outcome; no action chosen by this search can be executed by this runner.
    """
    if not own_history or max(x["t"] for x in own_history) >= t:
        raise AssertionError("unlived physical future leaked into Stage6 shadow")
    examples = tuple(x["example"] for x in own_history)
    if any(x["world_id"] != world_id for x in own_history):
        raise AssertionError("another world's physical memory was injected")
    if any(ex.terminal for ex in examples):
        raise AssertionError("terminal event used as active memory for later act")
    if examples[-1].observed_next_state != state:
        raise AssertionError("Stage6 shadow input does not match own last sense")
    corpus = EquipmentCorpus(
        version=f"z-own-past-{world_id}-t{t}", examples=examples,
    )
    equipment = train_exact_transition_table(
        corpus=corpus,
        equipment_version=f"z-exact-own-past-{world_id}-t{t}",
    )
    simulator = Simulator(
        config=SimulatorConfig(
            version="z-shadow-simulator-v1", r_max=1, h_max=3,
        ),
        equipment=equipment,
    )
    target = float(state.body["food"]) + 5.0
    planner = SimulatorPlanner(
        config=Stage6PlanningConfig(
            version="z-readonly-stage6-shadow-v1",
            option_ttl_steps=5, max_depth=3, revision_delta=0.0,
            setpoints={
                "energy": 65.0, "food": target,
                "water": 65.0, "integrity": 65.0,
            },
            progressive_subgoals=True,
        ),
        simulator=simulator,
    )
    result = planner.search(
        initial_state=state,
        target=lambda s: float(s.body["food"]) >= target,
        progress_measure="food",
    )
    diag = planner.last_search_diagnostic
    if diag is None:
        raise AssertionError("Stage6 root diagnostic missing")
    return {
        "t_monde": t,
        "input_first_person": state.as_dict(),
        "input_first_person_sha256": digest(state.as_dict()),
        "actual_own_history_step_count": len(own_history),
        "own_physical_examples": [x["example"].as_dict()
                                 for x in own_history],
        "actual_own_history_step_indices": [x["t"] for x in own_history],
        "history_corpus_sha256": corpus.digest(),
        "target_food": target,
        "max_depth": 3,
        "r_eff": 1,
        "model_kind": "own_prior_experience_only_exact_shadow",
        "stage6_status": result.status,
        "stage6_root_candidate_edges": result.root_candidate_edges,
        "stage6_root_available_edges": result.root_available_edges,
        "stage6_root_unavailable_edges": result.root_unavailable_edges,
        "stage6_diagnostic": diag,
        "stage6_candidate_commands_only": [
            command.as_dict() for command in result.commands
        ],
        "no_shadow_command_dispatched": True,
        "true_I0_UC_used": None,
        "not_a_lived_I0_memory": True,
        "oracle_fed_to_shadow": False,
    }


def run_world(*, layout_name, protocol, hidden, food, position):
    world_id = (
        f"a230z:{layout_name}:{protocol}:{hidden}:"
        f"food{int(food)}:x{position[0]}y{position[1]}"
    )
    config, layout = build_physics(layout_name, hidden, food, position)
    body = WorldBody(config=config, layout=layout)
    recorder = EquipmentCorpusRecorder(corpus_version="z-"+world_id)
    initial = first_person(body, 1).as_dict()
    assert_accessible(initial)
    lived_history = [{"t_monde": 1, "state": initial}]
    physical = []
    choices = []
    own_history = []
    shadow = None
    post_ingestion_external = None
    pre_ingestion_state = None
    physical_terminal_step = None
    nonterminal_after_last = initial

    for index in range(1, 6):  # max FOUR physical actions, plus abstention check
        state = first_person(body, index)
        observable = state.as_dict()
        if observable != nonterminal_after_last:
            raise AssertionError("visible state unexpectedly skipped or altered")
        executed = tuple(x["example"].command for x in own_history)
        next_command, reason = perceptual_food_policy(
            observable, protocol, executed,
        )
        if index > 4 and next_command is not None:
            raise AssertionError("policy exceeded frozen physical horizon")
        choices.append({
            "t_monde": index, "input_accessible_state": observable,
            "input_sha256": digest(observable),
            "previous_actually_executed_commands": [
                c.as_dict() for c in executed
            ],
            "command": None if next_command is None
                else next_command.as_dict(),
            "decision_reason_from_observation_only": reason,
            "external_hidden_configuration_not_used": True,
            "certifies_safe": False,
        })
        if next_command is None:
            break
        candidate = SimulatorPlanner.candidate_commands(state)
        if next_command not in candidate:
            raise AssertionError("lab policy tried a Stage6-unavailable command")
        if next_command == EAT_B:
            if shadow is not None:
                raise AssertionError("repeated B ingestion")
            if int(observable["inventory"].get("berry_b", 0)) < 1:
                raise AssertionError("cannot ingest unheld resource")
            pre_ingestion_state = observable
            shadow = own_past_shadow_search(
                world_id=world_id, t=index, state=state,
                own_history=own_history,
            )
        ex = recorder.record_transition(
            world=body, t_monde=index,
            family="a230z_physically_executed_alternative",
            command=next_command,
        )
        if ex.state != state:
            raise AssertionError("perceptual pre-action capture changed")
        before = ex.state.as_dict()
        after = ex.observed_next_state.as_dict()
        evidence = ex.as_dict()
        physical.append({
            "t_monde": index, "command": ex.command.as_dict(),
            "state_before": before,
            "physical_after_external_only": after,
            "terminal_external_only": ex.terminal,
            "physical_example_sha256": digest(evidence),
            "physical_example": evidence,
            "not_dispatched_by_shadow": True,
        })
        own_history.append({
            "t": index, "world_id": world_id, "example": ex,
        })
        if next_command == EAT_B:
            post_ingestion_external = after
        if ex.terminal:
            physical_terminal_step = index
            body.freeze_terminal_state()
            break
        lived_history.append({
            "t_monde": index+1, "state": after,
        })
        nonterminal_after_last = after

    if not choices:
        raise AssertionError("protocol produced no first-person decision")
    if physical_terminal_step is not None and (
        len(physical) != physical_terminal_step
        or not physical[-1]["terminal_external_only"]
        or lived_history[-1]["t_monde"] > physical_terminal_step
    ):
        raise AssertionError("postmortem transition or lived sense fabricated")
    if len(physical) != sum(x["command"] is not None for x in choices):
        raise AssertionError("lab actions differ from first-person selection")
    if len(physical) > 4:
        raise AssertionError("precommitted horizon exceeded")
    ingested = post_ingestion_external is not None
    if ingested and (shadow is None or pre_ingestion_state is None):
        raise AssertionError("ingestion was not preceded by Stage6 shadow")
    if not ingested and shadow is not None:
        raise AssertionError("shadow built without prospective ingestion")
    success = bool(
        ingested and physical_terminal_step is None
        and (post_ingestion_external["body"]["food"]
             - pre_ingestion_state["body"]["food"]) >= 5.0
    )
    no_gain = bool(ingested and physical_terminal_step is None and not success)
    initial_body = initial["body"]
    final_body = (physical[-1]["physical_after_external_only"]["body"]
                  if physical else initial_body)
    cost = {
        k: round(float(final_body[k]) - float(initial_body[k]), 8)
        for k in ("energy", "food", "water", "integrity")
    }
    return {
        "world_id": world_id,
        "layout_external_only": layout_name,
        "latent_berry_effect_external_only": hidden,
        "protocol_precommitted": protocol,
        "initial_food": float(food),
        "initial_position": list(position),
        "config_sha256_external_only": config.digest(),
        "layout_sha256_external_only": digest(layout.as_dict()),
        "initial_first_person": initial,
        "initial_first_person_sha256": digest(initial),
        "lived_states_while_alive": lived_history,
        "perceptual_policy_choices": choices,
        "physical_steps_external": physical,
        "physical_step_count": len(physical),
        "pre_ingestion_lived_state": pre_ingestion_state,
        "post_ingestion_external_only": post_ingestion_external,
        "physical_terminal_step_external_only": physical_terminal_step,
        "lived_postterminal_capture": None,
        "ingested_berry_b_external": ingested,
        "food_success_with_survival_external": success,
        "insufficient_food_with_survival_external": no_gain,
        "physical_body_delta_external": cost,
        "stage6_shadow": shadow,
        "no_oracle_information_in_policy": True,
        "no_stage6_shadow_action_dispatched": True,
        "no_i0_birth_or_autonomous_step": True,
        "actual_I0_UC_cost": None,
        "certifies_food_safety": False,
    }


def score_original_worlds(worlds):
    """Independent post-hoc analysis, never consulted by physical policy."""
    if len(worlds) != EXPECTED_WORLDS:
        raise ValueError("wrong original detached physical cohort size")
    groups = defaultdict(list)
    ids = set()
    steps = 0
    ingestions = 0
    terminal = 0
    success = 0
    insufficient = 0
    no_eat = 0
    shadow_counts = Counter()
    per_arm = defaultdict(Counter)
    for row in worlds:
        name = row["world_id"]
        if name in ids:
            raise ValueError("duplicate physical world")
        ids.add(name)
        arm = row["layout_external_only"]
        protocol = row["protocol_precommitted"]
        variant = row["latent_berry_effect_external_only"]
        if arm not in LAYOUTS or protocol not in POLICIES:
            raise ValueError("unknown preregistered physical layout or policy")
        if variant not in (A_HIDDEN if arm == "A_ONLY" else B_HIDDEN):
            raise ValueError("physical latent variants changed")
        if row["initial_food"] not in FOODS or tuple(
            row["initial_position"]
        ) not in POSITIONS:
            raise ValueError("changed preregistered physical body/position")
        if (row["lived_postterminal_capture"] is not None
            or row["certifies_food_safety"] is not False
            or row["actual_I0_UC_cost"] is not None
            or not row["no_oracle_information_in_policy"]
            or not row["no_stage6_shadow_action_dispatched"]
            or not row["no_i0_birth_or_autonomous_step"]):
            raise ValueError("injected oracle, UC or false safety certificate")
        start = row["initial_first_person"]
        assert_accessible(start)
        if digest(start) != row["initial_first_person_sha256"]:
            raise ValueError("first-person state hash changed")
        if len(row["physical_steps_external"]) != row["physical_step_count"]:
            raise ValueError("physical receipt count misreported")
        if row["physical_step_count"] > 4:
            raise ValueError("postmortem or excessive physical action")
        for idx, rec in enumerate(row["physical_steps_external"], 1):
            source = rec["physical_example"]
            if (rec["t_monde"] != idx or
                rec["physical_example_sha256"] != digest(source)
                or rec["state_before"] != source["state"]
                or rec["physical_after_external_only"] != source["observed_next_state"]
                or rec["terminal_external_only"] != source["terminal"]
                or rec["command"] != source["command"]):
                raise ValueError("physical example or receipt mutated")
            if rec["terminal_external_only"] and idx != row["physical_step_count"]:
                raise ValueError("physical action after terminal death")
            if idx == 1 and source["state"] != start:
                raise ValueError("first physical act did not use accessible initial")
            if idx > 1 and source["state"] != row[
                "physical_steps_external"][idx-2]["physical_after_external_only"]:
                raise ValueError("broken first-person action/outcome chain")
        if len(row["perceptual_policy_choices"]) < row["physical_step_count"]:
            raise ValueError("unrecorded physical policy action")
        for idx, choice in enumerate(row["perceptual_policy_choices"]):
            assert_accessible(choice["input_accessible_state"])
            if choice["input_sha256"] != digest(choice["input_accessible_state"]):
                raise ValueError("hidden/future feature entered policy input")
            if choice["external_hidden_configuration_not_used"] is not True:
                raise ValueError("lab hidden state selected a policy action")
            known_commands = tuple(
                PrimitiveCommand(
                    p["primitive"], p["parameters"],
                ) for p in choice["previous_actually_executed_commands"]
            )
            actual_cmd, actual_reason = perceptual_food_policy(
                choice["input_accessible_state"], protocol, known_commands,
            )
            if choice["command"] != (
                actual_cmd.as_dict() if actual_cmd is not None else None
            ) or choice["decision_reason_from_observation_only"] != actual_reason:
                raise ValueError("lab policy pretended to know an unseen resource")
            if choice["certifies_safe"]:
                raise ValueError("food action improperly claimed guaranteed safety")
            if idx < row["physical_step_count"]:
                physical = row["physical_steps_external"][idx]
                if choice["command"] != physical["command"]:
                    raise ValueError("physical command selected by another source")
        if row["physical_terminal_step_external_only"] is not None:
            if (not row["physical_steps_external"] or
                row["physical_terminal_step_external_only"] !=
                row["physical_step_count"] or
                row["lived_states_while_alive"][-1]["t_monde"] >
                row["physical_terminal_step_external_only"]):
                raise ValueError("death falsely reported as subjective experience")
        groups[(arm, protocol, row["initial_food"],
                tuple(row["initial_position"]))].append(row)
        steps += row["physical_step_count"]
        ingestions += row["ingested_berry_b_external"]
        terminal += row["physical_terminal_step_external_only"] is not None
        success += row["food_success_with_survival_external"]
        insufficient += row["insufficient_food_with_survival_external"]
        no_eat += not row["ingested_berry_b_external"]
        by = per_arm[(arm, protocol)]
        by["worlds"] += 1
        by["physical_steps"] += row["physical_step_count"]
        by["ingestions"] += row["ingested_berry_b_external"]
        by["terminals"] += row["physical_terminal_step_external_only"] is not None
        by["food_successes"] += row["food_success_with_survival_external"]
        by["insufficient"] += row["insufficient_food_with_survival_external"]
        by["abstained_from_food"] += not row["ingested_berry_b_external"]
        shadow = row["stage6_shadow"]
        if bool(shadow) != row["ingested_berry_b_external"]:
            raise ValueError("Stage6 shadow missing or leaked beyond intended ingestions")
        if shadow:
            if (shadow["input_first_person"] != row["pre_ingestion_lived_state"]
                or shadow["no_shadow_command_dispatched"] is not True
                or shadow["oracle_fed_to_shadow"] is not False
                or shadow["true_I0_UC_used"] is not None
                or shadow["not_a_lived_I0_memory"] is not True):
                raise ValueError("Stage6 search fed future/Oracle or claimed I0 memory")
            shadow_counts[shadow["stage6_status"]] += 1

    for (arm, protocol), (expected_worlds, expected_steps) in (
        EXPECTED_STEPS_BY_LAYOUT_POLICY.items()
    ):
        v = per_arm[(arm, protocol)]
        if (v["worlds"], v["physical_steps"]) != (
            expected_worlds, expected_steps
        ):
            raise ValueError("preregistered physical world-step count violated")
    if (steps, ingestions, terminal, success, insufficient, no_eat,
        sum(shadow_counts.values())) != (
        EXPECTED_STEPS, EXPECTED_INGESTIONS, EXPECTED_TERMINALS,
        EXPECTED_FOOD_SUCCESSES, EXPECTED_INSUFFICIENT, EXPECTED_NO_EAT,
        EXPECTED_SHADOW_QUERIES,
    ):
        raise ValueError("preregistered result counts drifted, preserve failure")

    equivalent_before = 0
    groups_with_undetected_lethal_B = 0
    for key, cases in groups.items():
        arm,protocol,food,position=key
        hidden_expected = A_HIDDEN if arm == "A_ONLY" else B_HIDDEN
        if len(cases) != len(hidden_expected) or {
            case["latent_berry_effect_external_only"] for case in cases
        } != set(hidden_expected):
            raise ValueError("unbalanced physical hidden-outcome cohort")
        initial = cases[0]["initial_first_person"]
        if any(case["initial_first_person"] != initial for case in cases):
            raise ValueError("latent effect visible before any berry ingestion")
        signatures = [(
            [choice["command"] for choice in case["perceptual_policy_choices"]],
            case["pre_ingestion_lived_state"],
            [
                receipt["state_before"] for receipt in
                case["physical_steps_external"]
            ],
        ) for case in cases]
        if any(sig != signatures[0] for sig in signatures[1:]):
            raise ValueError("hidden berry effects contaminated preingestion decisions")
        equivalent_before += 1
        if arm != "A_ONLY" and cases[0]["ingested_berry_b_external"]:
            if (sum(c["physical_terminal_step_external_only"] is not None
                for c in cases) != 1
                or sum(c["food_success_with_survival_external"] for c in cases) != 2
                or sum(c["insufficient_food_with_survival_external"] for c in cases) != 1):
                raise ValueError("dangerous hidden B branch not represented")
            groups_with_undetected_lethal_B += 1

    # Remote B is not initially accessible in the full first-person state;
    # a real exploratory move MAY reveal it, but the physical resource can
    # never be treated as present before that move.
    paired_remote_unseen = 0
    for protocol, food, position in product(POLICIES, FOODS, POSITIONS):
        a = groups[("A_ONLY", protocol, food, position)][0]
        remote = groups[("B_EAST_TWO_STEPS", protocol, food, position)][0]
        if a["initial_first_person"] != remote["initial_first_person"]:
            raise ValueError("remote B leaked into initial sensory field")
        paired_remote_unseen += 1

    return {
        "schema": "a230z-accessible-alternative-food-physical-v1",
        "original_physical_worlds":len(ids),
        "original_physical_actions":steps,
        "unique_initial_firstperson_hidden_groups":equivalent_before,
        "remote_B_truly_unseen_initial_paired_groups":paired_remote_unseen,
        "ingestions_of_berry_b":ingestions,
        "terminal_physical_ingestions":terminal,
        "surviving_food_gain_at_least_5":success,
        "surviving_food_gain_insufficient":insufficient,
        "abstentions_from_berry_b_ingestion":no_eat,
        "known_alternative_with_hidden_lethal_possibility_groups":
            groups_with_undetected_lethal_B,
        "shadow_queries_actual_Stage6_algorithm":sum(shadow_counts.values()),
        "shadow_status_counts":dict(sorted(shadow_counts.items())),
        "actual_I0_UC_cost_measured":False,
        "actual_I0_autonomous_food_achievement_proven":False,
        "stage6_production_plan_success_proven":False,
        "food_safety_proven":False,
        "stage12":"PARTIAL", "issue110":"OPEN",
        "new_living_I0_births":0, "new_autonomous_I0_steps":0,
        "normative_mvp_modified":False,
        "oracle_to_i0_feedback":False,
        "per_arm": {
            f"{layout}/{policy}": dict(counter)
            for (layout,policy), counter in sorted(per_arm.items())
        },
    }


def experiment(output_dir: Path):
    output_dir.mkdir(parents=True,exist_ok=False)
    worlds = [run_world(**case) for case in locked_cells()]
    summary = score_original_worlds(worlds)
    summary.update({
        "analysis_code_sha":subprocess.check_output(
            ["git","rev-parse","HEAD"], text=True,
        ).strip(),
        "frozen_matrix_sha256": digest({
            "layouts":LAYOUTS, "policies":POLICIES, "foods":FOODS,
            "positions":POSITIONS, "A_hidden":A_HIDDEN, "B_hidden":B_HIDDEN,
            "expected_physical_steps":EXPECTED_STEPS,
        }),
        "world_data_sha256":digest(worlds),
        "results_are_repeatable_deterministic_not_independent_py_seeds":True,
    })
    (output_dir/"a230z-physical-worlds.json").write_text(
        json.dumps(worlds,sort_keys=True,indent=2)+"\n",
    )
    (output_dir/"a230z-summary.json").write_text(
        json.dumps(summary,sort_keys=True,indent=2)+"\n",
    )
    print("A230Z_SUMMARY "+json.dumps({
        k:v for k,v in summary.items() if k!="per_arm"
    },sort_keys=True),flush=True)
    return summary


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output-dir",type=Path,required=True)
    args=ap.parse_args()
    experiment(args.output_dir)


if __name__=="__main__":
    main()
