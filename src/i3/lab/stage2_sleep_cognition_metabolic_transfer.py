"""I3 Stage 2.1: native sleep-mediated transfer of optional cognition into food.

PURE software fixtures only. The original action is already fixed; no Mind,
World, run_life, policy, lived outcome, new birth or adaptive criterion.
All costs come from the unmodified native v2 CognitiveBudget/transition.
"""
from __future__ import annotations

from dataclasses import asdict
import json
from math import isclose

from ..modules.body import (
    ACTION_COSTS, BodyLaws, CognitiveBudget, CognitiveWork,
    cognitive_cost, transition, validate_body)
from ..modules.genome import midpoint
from .stage2_action_phase_readout_budget import proposed_readout_work
from .stage2_readout_learning_affordability import _authorize_optional

SCHEMA = "i3-stage2.1-sleep-cognition-food-transfer-pure-software/v1"
ORIGINAL = CognitiveWork(cycles=3, memory_items=12)
CASES = (
    ("sleep_saturated", (99.95, 60., 60., 90., 99.95), "dormir"),
    ("sleep_food_critical", (99.95, .23, 60., 90., 99.95), "dormir"),
    ("sleep_food_control", (99.95, .24, 60., 90., 99.95), "dormir"),
    ("sleep_unsaturated", (5., 60., 60., 90., 50.), "dormir"),
    ("wait_no_conversion", (99.95, 60., 60., 90., 99.95), "attendre"),
    ("sleep_readout_denied", (99.95, 60., 60., 90., .30), "dormir"),
)


def examine(body, *, action, request_readout):
    """Budget each arm before running a single unmodified pure motor transition."""
    if type(request_readout) is not bool:
        raise TypeError("explicit experimental readout arm required")
    before = validate_body(body)
    if type(action) is not str or action not in ("dormir", "attendre"):
        raise ValueError("predeclared action must be waiting or sleeping")
    laws = BodyLaws()
    budget = CognitiveBudget(before, laws)
    if not budget.try_spend(ORIGINAL):
        raise ValueError("originally selected decision not affordable")
    original_work = budget.work
    original_remaining = budget.remaining
    optional = proposed_readout_work(0)
    admitted = False
    if request_readout:
        admitted = _authorize_optional(budget, action=action, n=0)
        if not admitted and (
                budget.work != original_work or budget.remaining != original_remaining):
            raise RuntimeError("refused optional work consumed resources")
    expected_work = CognitiveWork(
        cycles=ORIGINAL.cycles + (optional.cycles if admitted else 0),
        memory_items=ORIGINAL.memory_items +
        (optional.memory_items if admitted else 0))
    if budget.work != expected_work:
        raise RuntimeError("native allowance mismatches original and optional work")
    energy, vigilance = cognitive_cost(laws, budget.work)
    if budget.remaining[0] + energy != before[0] and not isclose(
            budget.remaining[0] + energy, before[0], abs_tol=1e-12):
        raise RuntimeError("native prepaid energy invariant failed")
    if not isclose(budget.remaining[4] + vigilance, before[4], abs_tol=1e-12):
        raise RuntimeError("native prepaid vigilance invariant failed")
    if action != "dormir" and budget.remaining[0] < ACTION_COSTS[action]:
        raise RuntimeError("brain was allowed to steal the fixed motor command")
    after, dead = transition(before, action, laws, budget.work)
    # Reconstruct the actual sleep/rest food distribution from *native outputs*.
    # The repair and energy-recovery pathways can compete at very low food.
    food_after_decay = max(0., before[1] - laws.food_decay)
    water_after_decay = max(0., before[2] - laws.water_decay)
    hydrated = water_after_decay >= laws.min_water_for_metabolism
    energy_after_cognition = budget.remaining[0]
    recovered_energy = 0.
    if action == "dormir" and hydrated:
        recovered_energy = min(
            laws.sleep_energy_gain, max(0., 100. - energy_after_cognition),
            food_after_decay / laws.sleep_food_cost_per_energy)
    food_to_energy = recovered_energy * laws.sleep_food_cost_per_energy
    repair_delta = after[3] - before[3]
    food_to_repair = (max(0., repair_delta) * laws.rest_food_cost_per_integrity
                      if hydrated else 0.)
    food_expected = max(0., food_after_decay - food_to_energy - food_to_repair)
    if not isclose(after[1], food_expected, abs_tol=1e-10):
        raise RuntimeError("native food and sleep/repair accounting mismatch")
    if not isclose(after[0], min(100., (energy_after_cognition +
                  recovered_energy) if action == "dormir" else
                  (energy_after_cognition - ACTION_COSTS[action])), abs_tol=1e-10):
        raise RuntimeError("native energy recovery receipt mismatch")
    return {
        "status": ("NOT_REQUESTED" if not request_readout else
                   "MODEL_AUTHORIZED" if admitted else "NO_FUNDED_READOUT"),
        "selected_action": action,
        "selected_param": None,
        "initial_body": list(before),
        "original_decision_work": asdict(original_work),
        "proposed_extra_readout_work": asdict(optional),
        "actual_model_work": asdict(budget.work),
        "native_model_cognition_energy": energy,
        "native_model_cognition_vigilance": vigilance,
        "additional_native_model_energy": (
            cognitive_cost(laws, optional)[0] if admitted else 0.),
        "additional_native_model_vigilance": (
            cognitive_cost(laws, optional)[1] if admitted else 0.),
        "post_action_body": list(after),
        "native_terminal_reasons": list(dead),
        "modeled_sleep_energy_restored": recovered_energy,
        "modeled_food_converted_to_energy": food_to_energy,
        "modeled_food_spent_on_repair": food_to_repair,
        "worlds_opened": 0, "actual_world_debit_attested": False,
    }


def audit():
    # This is the reference genetic contract only; no individual Mind is born.
    genome = midpoint()
    if genome["schema"] != "i3-genome-v4":
        raise RuntimeError("reference genome schema changed unexpectedly")
    rows = []
    for label, body, action in CASES:
        plain = examine(body, action=action, request_readout=False)
        optional = examine(body, action=action, request_readout=True)
        if plain["selected_action"] != optional["selected_action"]:
            raise RuntimeError("already chosen action changed between study arms")
        rows.append({
            "case": label,
            "before_body": list(body),
            "reference": plain,
            "optional": optional,
            "net_food_difference_optional_minus_reference": (
                optional["post_action_body"][1] - plain["post_action_body"][1]),
            "same_post_energy_and_vigilance": (
                optional["post_action_body"][0] == plain["post_action_body"][0]
                and optional["post_action_body"][4] == plain["post_action_body"][4]),
            "terminal_only_after_optional": (
                not plain["native_terminal_reasons"]
                and bool(optional["native_terminal_reasons"])),
        })
    by = {row["case"]: row for row in rows}
    failures = []
    saturated = by["sleep_saturated"]
    if not (saturated["same_post_energy_and_vigilance"]
            and saturated["net_food_difference_optional_minus_reference"] < 0
            and saturated["reference"]["post_action_body"][0] == 100.
            and saturated["reference"]["post_action_body"][4] == 100.):
        failures.append("sleep_saturated")
    critical = by["sleep_food_critical"]
    if not (critical["terminal_only_after_optional"]
            and critical["optional"]["native_terminal_reasons"] == ["zero_food"]
            and critical["reference"]["native_terminal_reasons"] == []):
        failures.append("sleep_food_critical")
    control = by["sleep_food_control"]
    if not (control["reference"]["native_terminal_reasons"] == []
            and control["optional"]["native_terminal_reasons"] == []
            and control["net_food_difference_optional_minus_reference"] < 0):
        failures.append("sleep_food_control")
    unsaturated = by["sleep_unsaturated"]
    if (unsaturated["same_post_energy_and_vigilance"] or
            not isclose(unsaturated["net_food_difference_optional_minus_reference"],
                        0., abs_tol=1e-12)):
        failures.append("sleep_unsaturated")
    waiting = by["wait_no_conversion"]
    if not (isclose(waiting["net_food_difference_optional_minus_reference"],
                    0., abs_tol=1e-12)
            and waiting["reference"]["modeled_food_converted_to_energy"] == 0
            and waiting["optional"]["modeled_food_converted_to_energy"] == 0):
        failures.append("wait_no_conversion")
    denied = by["sleep_readout_denied"]
    if not (denied["optional"]["status"] == "NO_FUNDED_READOUT"
            and denied["optional"]["actual_model_work"] ==
            denied["reference"]["actual_model_work"]
            and denied["optional"]["post_action_body"] ==
            denied["reference"]["post_action_body"]
            and denied["optional"]["additional_native_model_energy"] == 0
            and denied["optional"]["additional_native_model_vigilance"] == 0):
        failures.append("sleep_readout_denied")
    return {
        "schema": SCHEMA,
        "status": ("SOFTWARE_METABOLIC_TRANSFER_GATE_PASS" if not failures
                   else "SOFTWARE_METABOLIC_TRANSFER_FALSIFIER_FAILED"),
        "fixed_synthetic_cases": len(rows),
        "failed_predeclared_cells": failures,
        "saturated_sleep_hides_energy_vigilance_bill_not_food": (
            "sleep_saturated" not in failures),
        "native_model_terminal_only_after_optional_cognition": (
            critical["terminal_only_after_optional"]),
        "rows": rows,
        "worlds_opened": 0, "scientific_lives": 0,
        "actually_lived_extra_readout_debits": 0,
        "cpu_to_body_calibrated": False,
        "scientific_verdict": "NOT_ISSUED", "stage2_2_go": False,
    }


if __name__ == "__main__":
    print("I3_SLEEP_COGNITION_FOOD_TRANSFER_RESULT="+json.dumps(
        audit(), sort_keys=True))
