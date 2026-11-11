"""Value-of-computation IDENTIFIABILITY boundary for the I3 Stage-2.1 lab.

PURE software, no born World or policy. This experiment connects the native
decision work, physical action transition, next actual Mind.prepare_learning
model allocation, and the individual's innate distress readout. It cannot
identify the benefit of information from an already fixed motor action.
Synthetic effects are expressly NOT previously paid first-person evidence.
"""
from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
import json
from math import isfinite

from ..modules.body import (
    ACTION_COSTS, BodyLaws, CognitiveBudget, CognitiveWork, cognitive_cost,
    debit_cognition, transition, validate_body)
from ..modules.genome import midpoint
from ..modules.mind import Mind
from .stage2_action_conditional_existing_effects import passive_readouts
from .stage2_action_phase_readout_budget import proposed_readout_work
from .stage2_readout_learning_affordability import (
    _authorize_optional, _source_seal)

SCHEMA = "i3-stage2.1-personal-cost-not-information-value-software/v1"
MODES = ("reference", "paid_visible", "paid_discard")
ENERGIES = (0.45, 0.56, 5., 99.95)
FOODS = (0.23, 1., 60., 80.)
VIGILANCES = (0.30, 0.55, 5., 99.95)
ACTIONS = ("attendre", "dormir")
PERSONAL_FOOD_WEIGHTS = (0.2, 2.0)
WATER = 60.
INTEGRITY = 90.
ORIGINAL_DECISION = CognitiveWork(cycles=3, memory_items=12)


def _hash(obj):
    """External-laboratory checksum, never attributed to native cognition."""
    return sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"),
                             allow_nan=False, default=str).encode()).hexdigest()


def _source(before, action, food_weight):
    """Construct an explicitly synthetic, never-born personal model."""
    if food_weight not in PERSONAL_FOOD_WEIGHTS or type(food_weight) is not float:
        raise ValueError("only two prospectively frozen inherited food weights")
    if action not in ACTIONS or type(action) is not str:
        raise ValueError("already selected synthetic action required")
    genome = midpoint()
    genome["genes"]["w.food"] = food_weight
    mind = Mind(genome, 130201)
    # These two software records are NOT actual paid first-person experiences.
    mind.effects.observe(("attendre",), (-3., -1., -1., 0., -1.))
    mind.effects.observe(("dormir",), (6., -2., -1., 0., 7.))
    mind.last = (before, (action,), action, None)
    return mind


def _intrinsic(mind, body, dead):
    """Exactly original inherited distress, no cost or survival bonus."""
    return (-mind.d_max if dead else
            -mind.distress(mind.feats(validate_body(body))))


def project_model_arm(before_body, *, action, food_weight, mode):
    """One action-fixed cost branch, NEVER an observed future/World life."""
    if mode not in MODES or type(mode) is not str:
        raise ValueError("reference or named cost-matched lab branch required")
    if action not in ACTIONS or type(action) is not str:
        raise ValueError("fixed selected native action required")
    before = validate_body(before_body)
    if before[2] != WATER or before[3] != INTEGRITY:
        raise ValueError("only fixed grid water/integrity may enter this audit")
    if before[0] not in ENERGIES or before[1] not in FOODS or before[4] not in VIGILANCES:
        raise ValueError("only predeclared pure software bodily grid allowed")
    source = _source(before, action, food_weight)
    original_seal = _source_seal(source)
    laws = BodyLaws()
    allowance = CognitiveBudget(before, laws)
    if not allowance.try_spend(ORIGINAL_DECISION):
        raise RuntimeError("the predeclared original decision cannot be funded")

    grant = False
    synthetic_forecast_count = 0
    forecast_hash = None
    laboratory_forecasts = None
    initial_allowance = allowance.work
    initial_remaining = allowance.remaining
    if mode != "reference":
        grant = _authorize_optional(
            allowance, action=action, n=len(source.buffer))
        if grant:
            # Only AFTER approval; both modes genuinely execute the same
            # action/global/persistence lab forecast and SHA operations.
            forecast = passive_readouts(source, before, action)
            scalar = forecast["scalar_forecasts"]
            if tuple(scalar) != ("action", "global", "persistence"):
                raise RuntimeError("unexpected personal forecast modes")
            forecast_hash = _hash(scalar)
            synthetic_forecast_count = len(scalar)
            if mode == "paid_visible":
                laboratory_forecasts = dict(scalar)
        elif (allowance.work != initial_allowance or
              allowance.remaining != initial_remaining):
            raise RuntimeError("denied extra readout changed native allowance")
    if original_seal != _source_seal(source):
        raise RuntimeError("lab readout modified source Mind, effects or RNG")

    added_work = proposed_readout_work(len(source.buffer))
    expected = CognitiveWork(
        cycles=ORIGINAL_DECISION.cycles + (added_work.cycles if grant else 0),
        simulated_steps=ORIGINAL_DECISION.simulated_steps,
        memory_items=ORIGINAL_DECISION.memory_items +
        (added_work.memory_items if grant else 0),
        replays=ORIGINAL_DECISION.replays)
    if allowance.work != expected:
        raise RuntimeError("model work was not charged in both currencies")
    if action != "dormir" and allowance.remaining[0] < ACTION_COSTS[action]:
        raise RuntimeError("optional cognition consumed admitted motor")
    direct_cost = cognitive_cost(laws, allowance.work)

    # This is the actual pure v2 bodily law on synthetic inputs, not World.step.
    immediate, terminal_reasons = transition(
        before, action, laws, allowance.work)
    if terminal_reasons:
        learning_status = "TERMINAL_NO_LEARNING"
        learning_budget = CognitiveBudget(immediate, laws)
        post_learning = immediate
        replay_count = None
    else:
        learning_budget = CognitiveBudget(immediate, laws)
        replay_count = source.prepare_learning(
            {"body": immediate, "dead": terminal_reasons}, learning_budget)
        if replay_count is None:
            learning_status = "NO_FUNDED_LEARNING"
            post_learning = immediate
            if learning_budget.work != CognitiveWork():
                raise RuntimeError("unfunded learning carried phantom work")
        else:
            learning_status = "MODEL_FUNDED_LEARNING"
            post_learning, accounting = debit_cognition(
                immediate, laws, learning_budget.work)
            if any(x["unpaid"] != 0. for x in accounting.values()):
                raise RuntimeError("post-learning pure bill has unpaid work")
    if original_seal != _source_seal(source):
        raise RuntimeError("synthetic model projected learning mutated source Mind")

    immediate_target = _intrinsic(source, immediate, bool(terminal_reasons))
    primary_target = _intrinsic(source, post_learning, bool(terminal_reasons))
    if not isfinite(immediate_target) or not isfinite(primary_target):
        raise RuntimeError("invalid native personally inherited scalar distress")
    return {
        "mode": mode,
        "food_weight": food_weight,
        "chosen_action": action,
        "original_body": before,
        "optional_ticket_requested": mode != "reference",
        "optional_admitted": grant,
        "optional_status": (
            "NOT_REQUESTED" if mode == "reference" else
            "MODEL_AUTHORIZED" if grant else "NO_FUNDED_READOUT"),
        "reference_work": asdict(ORIGINAL_DECISION),
        "total_declared_decision_work": asdict(allowance.work),
        "model_decision_energy": direct_cost[0],
        "model_decision_vigilance": direct_cost[1],
        "synthetic_readouts_actually_executed": synthetic_forecast_count,
        "synthetic_readout_sha256": forecast_hash,
        "laboratory_readouts_visible": laboratory_forecasts,
        "immediate_post_action_body": immediate,
        "native_terminal_reasons": terminal_reasons,
        "next_learning_status": learning_status,
        "next_learning_work": asdict(learning_budget.work),
        "next_sleep_replays_reserved": replay_count,
        "post_paid_learning_model_body": post_learning,
        "immediate_intrinsic_target": immediate_target,
        "post_learning_intrinsic_target": primary_target,
        "primary_target_phase": "POST_PAID_LEARNING",
        "secondary_target_phase": "IMMEDIATE_POST_WORLD",
        "source_mind_unchanged": True,
        "external_forecast_never_controls_action": True,
        "native_living_body_debit_attested": False,
        "expected_information_benefit": None,
        "realized_future_action_effect": None,
        "net_value_of_computation": None,
        "scientific_lives": 0,
    }


def _same_paid_physical_receipt(visible, discarded):
    """Only observer visibility may differ, never a native physical outcome."""
    keys = (
        "chosen_action", "original_body", "optional_admitted",
        "optional_status", "total_declared_decision_work",
        "model_decision_energy", "model_decision_vigilance",
        "synthetic_readouts_actually_executed",
        "synthetic_readout_sha256", "immediate_post_action_body",
        "native_terminal_reasons", "next_learning_status",
        "next_learning_work", "next_sleep_replays_reserved",
        "post_paid_learning_model_body", "immediate_intrinsic_target",
        "post_learning_intrinsic_target",
    )
    return all(visible[k] == discarded[k] for k in keys)


def audit():
    rows = []
    for e in ENERGIES:
        for f in FOODS:
            for v in VIGILANCES:
                before = (e, f, WATER, INTEGRITY, v)
                for action in ACTIONS:
                    for weight in PERSONAL_FOOD_WEIGHTS:
                        original = project_model_arm(
                            before, action=action, food_weight=weight,
                            mode="reference")
                        visible = project_model_arm(
                            before, action=action, food_weight=weight,
                            mode="paid_visible")
                        discarded = project_model_arm(
                            before, action=action, food_weight=weight,
                            mode="paid_discard")
                        if not _same_paid_physical_receipt(visible, discarded):
                            raise RuntimeError(
                                "visible and discarded equally paid cognition "
                                "changed physical, learning or inherited value")
                        if (visible["synthetic_readouts_actually_executed"] !=
                                3 * int(visible["optional_admitted"]) or
                                discarded["synthetic_readouts_actually_executed"] !=
                                visible["synthetic_readouts_actually_executed"]):
                            raise RuntimeError("readout computed before admission")
                        if (visible["next_learning_work"] !=
                                discarded["next_learning_work"]):
                            raise RuntimeError("equal-cost learning comparison failed")
                        if not visible["optional_admitted"] and (
                                visible["post_paid_learning_model_body"] !=
                                original["post_paid_learning_model_body"] or
                                visible["immediate_post_action_body"] !=
                                original["immediate_post_action_body"]):
                            raise RuntimeError("denied cognition changed living law")
                        if any(x is not None for x in (
                                visible["expected_information_benefit"],
                                visible["realized_future_action_effect"],
                                visible["net_value_of_computation"])):
                            raise RuntimeError(
                                "no causal action effect: information value cannot be scored")
                        # This is an intrinsic cost-only comparator, never
                        # positive evidence that information helped the motor.
                        delta = (visible["post_learning_intrinsic_target"] -
                                 original["post_learning_intrinsic_target"])
                        if not isfinite(delta):
                            raise RuntimeError("nonfinite native personal valuation")
                        rows.append({
                            "body": before, "chosen_action": action,
                            "hypothetical_food_weight": weight,
                            "extra_admitted": visible["optional_admitted"],
                            "reference_learning": original["next_learning_status"],
                            "extra_learning": visible["next_learning_status"],
                            "reference_terminal": original["native_terminal_reasons"],
                            "extra_terminal": visible["native_terminal_reasons"],
                            "reference_post_learning_intrinsic":
                                original["post_learning_intrinsic_target"],
                            "extra_post_learning_intrinsic":
                                visible["post_learning_intrinsic_target"],
                            "cost_only_intrinsic_difference": delta,
                            "extra_food_difference": (
                                visible["post_paid_learning_model_body"][1] -
                                original["post_paid_learning_model_body"][1]),
                            "readout_hash": visible["synthetic_readout_sha256"],
                            "equal_cost_visible_discard_physical": True,
                            "readouts_executed_in_each_paid_arm":
                                visible["synthetic_readouts_actually_executed"],
                        })
    signs = {
        "negative": sum(x["cost_only_intrinsic_difference"] < 0
                        for x in rows if x["extra_admitted"]),
        "zero": sum(x["cost_only_intrinsic_difference"] == 0
                    for x in rows if x["extra_admitted"]),
        "positive": sum(x["cost_only_intrinsic_difference"] > 0
                        for x in rows if x["extra_admitted"]),
    }
    samples = [
        x for x in rows
        if ((x["body"][0], x["body"][1], x["body"][4]) in (
            (99.95, 0.23, 99.95), (99.95, 60., 99.95),
            (0.56, 60., 0.55), (5., 80., 5.))
            and x["hypothetical_food_weight"] == 2.0)
    ]
    return {
        "schema": SCHEMA,
        "status": "FIXED_ACTION_PERSONAL_COST_ONLY_INFORMATION_UNIDENTIFIED",
        "factorial_grid_size": len(rows),
        "synthetic_personal_genome_levels": list(PERSONAL_FOOD_WEIGHTS),
        "exact_full_grid_sha256": _hash(rows),
        "optional_funded_cells": sum(x["extra_admitted"] for x in rows),
        "optional_denied_cells": sum(not x["extra_admitted"] for x in rows),
        "native_learning_lost_after_extra": sum(
            x["extra_admitted"] and x["reference_learning"] ==
            "MODEL_FUNDED_LEARNING" and x["extra_learning"] !=
            "MODEL_FUNDED_LEARNING" for x in rows),
        "native_terminal_only_after_extra": sum(
            x["extra_admitted"] and not x["reference_terminal"]
            and bool(x["extra_terminal"]) for x in rows),
        "cost_only_intrinsic_signs_on_funded": signs,
        "all_paid_visible_discard_equivalent": True,
        "sampled_predeclared_receipts": samples,
        "rows": rows,
        "expected_information_benefit": None,
        "realized_future_action_effect": None,
        "net_value_of_computation": None,
        "forecast_source_history": "SYNTHETIC_UNPAID_ACTION_EFFECTS",
        "actual_personal_outcomes_scored": 0,
        "worlds_opened": 0, "scientific_lives": 0,
        "scientific_verdict": "NOT_ISSUED",
        "cpu_to_body_calibrated": False, "stage2_2_go": False,
    }


if __name__ == "__main__":
    complete = audit()
    print("I3_VOI_IDENTIFIABILITY_SOFTWARE_RESULT="+json.dumps(
        {k: v for k, v in complete.items() if k != "rows"}, sort_keys=True))
