"""No-World E3 native-choice falsifier; existing action-bound empirical support.

Frozen protocol: docs/studies/stage2-replay-gate-selected-design/
E3_NATIVE_PAID_BRANCH_DELIVERY_PREFLIGHT_2026-11-11.md

The only controller extension is a LAB-ONLY subclass of a previously optional
reference branch-memory control. No World, registered runtime, new preference,
new learning rule, intrinsic target or physical life is introduced.
"""
from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
from math import fsum, isfinite
import json

from ..modules.body import (
    ACTION_COSTS, BodyLaws, CognitiveBudget, CognitiveFundingError,
    CognitiveWork, VITAL, debit_cognition,
)
from ..modules.genome import midpoint
from ..modules.mind import Mind, DIRS
from ..modules.observed_effect_view import _ObservedEffectView, VIEW_WORK
from ..modules.personal_outcomes import NoPersonalSupport, STORE_WORK, WINDOW
from ..modules.reference_branches import CAPACITY
from ..modules.reference_memory_mind import ReferenceBranchMemoryMind
from .stage2_paid_personal_branch_source_complement import (
    BODY, DECISION_WORK, FIXED_HISTORIES, KEY, NATIVE_KEY, SEED,
    _effects_rows,
)

SCHEMA = "i3-stage2-e3-native-paid-branch-delivery-software/v1"
MODES = ("VISIBLE", "PAID_DISCARD")
PREQUOTE_WORK = CognitiveWork(cycles=1, memory_items=2)
REDUCTION_CYCLE = 1
MOTOR_RESERVE = max(ACTION_COSTS.values())
CAP = {
    "body": BODY, "here": (False, ()),
    "neighbors": tuple(None for _ in DIRS), "inventory": (),
}


def _add_work(a, b):
    return CognitiveWork(
        cycles=a.cycles + b.cycles,
        simulated_steps=a.simulated_steps + b.simulated_steps,
        memory_items=a.memory_items + b.memory_items,
        replays=a.replays + b.replays,
    )


def _work_delta(a, b):
    return asdict(CognitiveWork(
        cycles=a.cycles - b.cycles,
        simulated_steps=a.simulated_steps - b.simulated_steps,
        memory_items=a.memory_items - b.memory_items,
        replays=a.replays - b.replays,
    ))


def _sha(value):
    return sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")).hexdigest()


def _future_ceiling(mind):
    """Unspent strictly conservative upper bound, NOT a billed fake ticket.

    Exactly one native simulated step + <=len(proj_chunks) projections for
    each of <=WINDOW recorded same-action bodily outcomes in reference mode.
    """
    if (mind.simulation_mode != "reference"
            or mind.projection_accounting not in ("chunk_end", "trapezoid")):
        raise ValueError("only frozen existing P1.3 reference simulator quoted")
    return CognitiveWork(
        cycles=1 + WINDOW * VIEW_WORK.cycles + REDUCTION_CYCLE,
        simulated_steps=WINDOW * (1 + len(mind.proj_chunks)),
        memory_items=(7 * CAPACITY + 2
                      + WINDOW * VIEW_WORK.memory_items + 2 * WINDOW),
    )


def _can_fund_optional(budget, quote):
    """Check full existing computation and worst legal motor reserve.

    This observer-free arithmetic does not access source history or debit a
    quote that was never executed.
    """
    try:
        future, _ = debit_cognition(
            budget.body, budget.laws, _add_work(budget.work, quote)
        )
    except CognitiveFundingError:
        return False
    return future[0] >= MOTOR_RESERVE and future[4] >= 0.0


class E3NativeBranchResearchMind(ReferenceBranchMemoryMind):
    """ONLY lab opt-in. Native Mind.decide owns options, scores, competition,
    authority, action-control and personal default RNG.
    """

    def __init__(self, genome, life_seed, *, mode, **kwargs):
        if mode not in MODES or type(mode) is not str:
            raise ValueError("one of two source-locked visibility modes required")
        super().__init__(genome, life_seed, **kwargs)
        self.e3_mode = mode
        self.e3_events = []

    def simulate(self, body, plan, horizon, budget):
        if not isinstance(budget, CognitiveBudget):
            raise TypeError("native first-person CognitiveBudget required")
        if any(body[c] <= 0 for c in VITAL):
            raise ValueError("no E3 branch computation after physical death")
        start = budget.work
        original_value, original_steps, original_uncertainty = Mind.simulate(
            self, body, plan, horizon, budget
        )
        event = {
            "action_key": tuple(plan[0]) if len(plan) == 1 else None,
            "plan_length": len(plan),
            "status": "NOT_ELIGIBLE_MULTISTEP",
            "original_score": original_value,
            "empirical_score": None,
            "returned_score": original_value,
            "source_records": 0,
            "read_calls": 0,
            "native_branch_simulations": 0,
            "view_constructions": 0,
            "reduction_paid": False,
            "original_simulation_steps": original_steps,
            "original_uncertainty": original_uncertainty,
        }
        if len(plan) != 1:
            event["work"] = _work_delta(budget.work, start)
            self.e3_events.append(event)
            return original_value, original_steps, original_uncertainty

        action = tuple(plan[0])
        if not action or type(action[0]) is not str:
            raise ValueError("actual native first plan action identity required")
        key = (action[0], action[1] if len(action) > 1 else None)
        if not budget.try_spend(PREQUOTE_WORK):
            event["status"] = "NO_FUNDED_SIGNAL"
            event["work"] = _work_delta(budget.work, start)
            self.e3_events.append(event)
            return original_value, original_steps, original_uncertainty
        if not _can_fund_optional(budget, _future_ceiling(self)):
            event["status"] = "NO_FUNDED_SIGNAL"
            event["work"] = _work_delta(budget.work, start)
            self.e3_events.append(event)
            return original_value, original_steps, original_uncertainty

        read_receipt = {}
        event["read_calls"] = 1
        try:
            support = self.branch_memory.read_support(
                key, budget, work_receipt=read_receipt
            )
        except NoPersonalSupport:
            if read_receipt.get("status") != "NO_SUPPORT":
                raise RuntimeError("unsupported existing source lacks paid receipt")
            event["status"] = "NO_PERSONAL_SUPPORT"
            event["read_work"] = read_receipt["work"]
            event["work"] = _work_delta(budget.work, start)
            self.e3_events.append(event)
            return original_value, original_steps, original_uncertainty

        if (read_receipt.get("status") != "COMPLETE"
                or len(support) == 0 or len(support) > WINDOW
                or read_receipt["branches"] != len(support)):
            raise RuntimeError("expected bounded genuine paid branch history")
        event["read_work"] = read_receipt["work"]
        event["source_records"] = len(support)

        # The same view construction and same native Mind.simulate are
        # actually called for BOTH VISIBLE and PAID_DISCARD.
        forecasts = []
        for delta in support:
            budget.spend(VIEW_WORK)
            view = _ObservedEffectView(self, action, delta)
            event["view_constructions"] += 1
            value, steps, uncertainty = Mind.simulate(
                view, body, plan, horizon, budget
            )
            if not isfinite(value) or steps != original_steps:
                raise RuntimeError("nonfinite or misaligned native branch score")
            forecasts.append(value)
            event["native_branch_simulations"] += 1
        budget.spend(CognitiveWork(
            cycles=REDUCTION_CYCLE, memory_items=2 * len(forecasts)
        ))
        branch_mean = fsum(forecasts) / len(forecasts)
        if not isfinite(branch_mean):
            raise RuntimeError("invalid native bodily consequence expectation")
        # Never replace uncertainty, inherited values or original curiosity.
        event["empirical_score"] = branch_mean
        event["status"] = "VISIBLE_READOUT" if self.e3_mode == "VISIBLE" \
            else "FULLY_COMPUTED_PAID_DISCARD"
        event["reduction_paid"] = True
        returned = branch_mean if self.e3_mode == "VISIBLE" else original_value
        event["returned_score"] = returned
        event["work"] = _work_delta(budget.work, start)
        self.e3_events.append(event)
        return returned, original_steps, original_uncertainty


def _synthetic_source(mind, deltas):
    """Recreate the exact frozen E2 input under existing modeled-store work.

    These are artificial inputs, NOT a World/capture/life, never source originals.
    """
    if type(deltas) is not tuple or len(deltas) not in (0, 2):
        raise ValueError("exact E3 source-form history only")
    after_decision, _ = debit_cognition(
        BODY, BodyLaws(), DECISION_WORK
    )
    receipts = []
    for delta in deltas:
        physical_after = tuple(x + dx for x, dx in zip(after_decision, delta))
        budget = CognitiveBudget(physical_after, BodyLaws())
        mind.branch_memory.observe(KEY, BODY, DECISION_WORK, budget)
        if budget.work != STORE_WORK:
            raise RuntimeError("artificial source was not model-prepaid")
        _, bill = debit_cognition(physical_after, BodyLaws(), budget.work)
        if any(x["unpaid"] != 0 for x in bill.values()):
            raise RuntimeError("artificial source model charged unpaid store")
        receipts.append(asdict(budget.work))
        mind.effects.observe(NATIVE_KEY, delta)
    return receipts


def _case(name, deltas, mode):
    mind = E3NativeBranchResearchMind(
        midpoint(), SEED, mode=mode, observer_full_competition=True
    )
    store = _synthetic_source(mind, deltas)
    initial_model = _effects_rows(mind)
    source_samples = tuple(mind.branch_memory._samples)
    initial_rng = mind.rng.getstate()
    initial_budget_rng = mind._budget_rng.getstate()
    allowance = CognitiveBudget(BODY, BodyLaws())
    action, param, work, info = mind.decide(CAP, allowance)
    if work != allowance.work:
        raise RuntimeError("native decision returned non-cumulative work")
    if source_samples != tuple(mind.branch_memory._samples):
        raise RuntimeError("controller read changed paid personal source")
    if _effects_rows(mind) != initial_model:
        raise RuntimeError("source native EffectsModel altered by information")
    if any(x["unpaid"] != 0 for x in debit_cognition(
            BODY, BodyLaws(), work)[1].values()):
        raise RuntimeError("model body decision cognition not fully debit-able")
    observer = info.get("observer", {})
    witnesses = observer.get("score_witness", [])
    return {
        "history": name, "mode": mode,
        "original_native_effect_stats": initial_model,
        "initial_native_rng_sha256": _sha(initial_rng),
        "initial_native_budget_rng_sha256": _sha(initial_budget_rng),
        "initial_support_size": len(source_samples),
        "predecision_model_store_work": store,
        "funding": info.get("funding"),
        "action": action, "param": param, "option": info.get("option"),
        "actual_native_Mind_decide_was_called": True,
        "full_option_set_offered": observer.get("offered_options"),
        "full_option_set_scored": observer.get("scored_options"),
        "all_offered_options_scored": (
            observer.get("offered_options") == observer.get("scored_options")
            and bool(observer.get("offered_options"))
        ),
        "scores": [{
            "option": x["option"],
            "native_base_return": x["base_return"],
            "total_score": x["total_score"],
            "original_bonus": x["curiosity_risk_bonus"],
        } for x in witnesses],
        "controller_finalization": observer.get("competition_witness", {}),
        "readout_events": mind.e3_events,
        "decision_work": asdict(work),
        "native_model_work_fully_debit_able": True,
        "actual_World_motor_executed": False,
        "actual_World_body_observed": False,
    }


def audit():
    histories = FIXED_HISTORIES + (("none", ()),)
    cases = {}
    for name, deltas in histories:
        cases[name] = {mode: _case(name, deltas, mode) for mode in MODES}
    results = []
    for name, arms in cases.items():
        v, d = (arms[m] for m in MODES)
        if (v["original_native_effect_stats"] != d["original_native_effect_stats"]
                or v["initial_native_rng_sha256"] != d["initial_native_rng_sha256"]
                or v["initial_native_budget_rng_sha256"] != d["initial_native_budget_rng_sha256"]
                or v["full_option_set_offered"] != d["full_option_set_offered"]
                or v["full_option_set_scored"] != d["full_option_set_scored"]
                or not v["all_offered_options_scored"]
                or not d["all_offered_options_scored"]):
            raise AssertionError("same learned source or native option coverage violated")
        events_v, events_d = v["readout_events"], d["readout_events"]
        if len(events_v) != len(events_d):
            raise AssertionError("visibility changed source-operator count")
        for ev, ed in zip(events_v, events_d):
            for key in ("action_key", "plan_length", "original_score",
                        "empirical_score", "source_records", "read_calls",
                        "native_branch_simulations", "view_constructions",
                        "reduction_paid", "work"):
                if ev[key] != ed[key]:
                    raise AssertionError("VISIBLE/DISCARD real compute or price mismatch: "+key)
            if ev["status"] != ed["status"] and (
                    ev["status"], ed["status"]
            ) != ("VISIBLE_READOUT", "FULLY_COMPUTED_PAID_DISCARD"):
                raise AssertionError("unequal no-support/quote decision statuses")
            if ed["returned_score"] != ed["original_score"]:
                raise AssertionError("paid discard leaked empirical score")
        if name == "none" and any(x["source_records"] for x in events_v):
            raise AssertionError("unknown source invented action effect")
        if name in ("spread", "flat") and not any(
                x["source_records"] == 2 and x["read_calls"] == 1
                for x in events_v):
            raise AssertionError("existing paid action bound source was not read")
        scores_d = d["scores"]
        if any(x["total_score"] != y["total_score"]
               for x, y in zip(v["scores"], d["scores"])) and (
               len(v["scores"]) != len(scores_d)):
            raise AssertionError("different score-vector cardinality")
        full_work_equal = v["decision_work"] == d["decision_work"]
        motor_change = (
            (v["action"], v["param"]) != (d["action"], d["param"])
        )
        distinct_total_scores = any(
            x["total_score"] != y["total_score"]
            for x, y in zip(v["scores"], d["scores"])
        )
        classification = (
            "NATIVE_ACTION_DIFFERENCE" if motor_change and full_work_equal else
            "ACTION_WITH_ENDOGENOUS_WORK_DIFFERENCE" if motor_change else
            "SCORE_ONLY" if distinct_total_scores else
            "NO_DISTINCT_SCORE"
        )
        results.append({
            "history": name, "visibility_modes": list(MODES),
            "motor_difference": motor_change,
            "same_complete_native_work": full_work_equal,
            "score_difference": distinct_total_scores,
            "classification": classification,
            "visible": v, "paid_discard": d,
        })
    positive = sum(x["classification"] == "NATIVE_ACTION_DIFFERENCE"
                   for x in results if x["history"] != "none")
    report = {
        "schema": SCHEMA, "source_kind": "SYNTHETIC_UNPAID_FIRST_PERSON_FORMAT",
        "fixed_body": BODY, "fixed_seed": SEED, "fixed_histories": 3,
        "paired_native_Mind_decide_software_comparisons": 3,
        "real_VD_extra_operator_and_cost_parity": True,
        "native_Competition_and_Action_Control_retained": True,
        "positive_native_motor_difference_count": positive,
        "mechanism_verdict": (
            "E3_NATIVE_DECISION_SENSITIVITY_SOFTWARE_ONLY" if positive
            else "E3_FROZEN_NATIVE_ACTION_MEDIATION_NOT_SHOWN"
        ),
        "nonmean_information_already_stored": True,
        "native_readout_delivered_in_optional_lab_mind": True,
        "physical_World_motor_executed": False,
        "physical_World_body_observed": False,
        "new_worlds": 0, "new_scientific_lives": 0,
        "scientific_verdict": "NOT_ISSUED", "stage2_2_go": False,
        "cases": results,
    }
    return {**report, "aggregate_sha256": _sha(report)}


if __name__ == "__main__":
    print("I3_E3_NATIVE_PAID_BRANCH_DELIVERY=" + json.dumps(
        audit(), sort_keys=True, separators=(",", ":"), allow_nan=False
    ))
