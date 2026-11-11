"""Frozen Stage-2 E1 no-World native decision-depth falsifier.

Prospective protocol:
docs/studies/stage2-replay-gate-selected-design/
NATIVE_OPTION_SET_DEPTH_DECISION_PREFLIGHT_2026-11-11.md

All training effects are SYNTHETIC_UNPAID. No born individual, no World,
no extrapolated survival/utility claim. The real native Mind.decide
still owns all scoring, Competition and Action Control.
"""
from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
import json
from math import isfinite

from ..modules.body import (
    ACTION_COSTS, BodyLaws, CognitiveBudget, CognitiveWork, cognitive_cost,
    debit_cognition, validate_body
)
from ..modules.genome import midpoint
from ..modules.mind import Mind

SCHEMA = "i3-stage2-native-option-depth-choice-software/v1"
SOURCE_KIND = "SYNTHETIC_UNPAID_PRIOR_NEVER_BORN"
SEED = 211
BODIES = (
    (80., 60., 60., 80., 80.),
    (45., 40., 40., 75., 70.),
    (30., 25., 25., 70., 50.),
)
CONTEXTS = ("water_here", "food_here", "frontier", "carried_food")
MODES = ("cap1", "cap4", "full", "reference")
EFFECTS = (
    (("attendre",), (-.35, -.2, -.4, .2, 0.)),
    (("dormir",), (3., -.35, -.4, 0., 4.)),
    (("boire",), (-.5, -.2, 35., 0., 0.)),
    (("se_deplacer",), (-2., -.2, -.4, 0., 0.)),
    (("collecter",), (-.5, -.2, -.4, 0., 0.)),
    (("manger", "tok0"), (-.5, 35., -.4, 0., 0.)),
)


class LabDepthCapMind(Mind):
    """No policy modification; cap only native simulated depth in the lab."""

    def __init__(self, genome, life_seed, *, depth_cap, **kwargs):
        if depth_cap is not None and (
            type(depth_cap) is not int or depth_cap not in (1, 4)
        ):
            raise ValueError("frozen E1 depth caps are 1, 4 or none")
        self._stage2_lab_depth_cap = depth_cap
        super().__init__(genome, life_seed, **kwargs)

    def simulate(self, body, plan, horizon, budget):
        cap = self._stage2_lab_depth_cap
        return super().simulate(body, plan, min(cap, horizon) if cap else horizon,
                                budget)


def _fresh(mode):
    if mode not in MODES:
        raise ValueError("unknown frozen mode")
    genome = midpoint()
    if mode == "reference":
        mind = Mind(genome, SEED, observer_decision_diagnostics=True)
    else:
        cap = {"cap1": 1, "cap4": 4, "full": None}[mode]
        mind = LabDepthCapMind(genome, SEED, depth_cap=cap,
                              observer_decision_diagnostics=True)
    for key, delta in EFFECTS:
        mind.effects.observe(key, delta)
    return mind


def _capture(body, context):
    body = validate_body(body)
    if context not in CONTEXTS:
        raise ValueError("unknown frozen first-person-shaped fixture")
    neighbors = ((False, ()), None, None, None)
    here = (False, ())
    inventory = ()
    if context == "water_here":
        here = (True, ())
    elif context == "food_here":
        here = (False, ("opaque-resource",))
    elif context == "carried_food":
        neighbors = (None,) * 4
        inventory = (("opaque-resource", 2),)
    return {"body": body, "here": here, "neighbors": neighbors,
            "inventory": inventory}


def _run(body, context, mode):
    mind = _fresh(mode)
    capture = _capture(body, context)
    laws = BodyLaws()
    budget = CognitiveBudget(capture["body"], laws)
    action, param, work, info = mind.decide(capture, budget)

    if type(work) is not CognitiveWork or work != budget.work:
        raise AssertionError("native returned work differs from prepaid allowance")
    if info.get("option") is None and action is not None:
        raise AssertionError("motor action absent native selected option")
    if action is not None and action not in ACTION_COSTS:
        raise AssertionError("unrecognized native physical motor action")
    if action not in (None, "dormir") and (
        budget.remaining[0] + 1e-12 < ACTION_COSTS[action]
    ):
        raise AssertionError("native motor did not retain its energy reserve")
    post, account = debit_cognition(capture["body"], laws, work)
    if post != budget.remaining:
        raise AssertionError("two-currency native model budget mismatch")
    if any(account[k]["unpaid"] != 0. for k in ("energy", "vigilance")):
        raise AssertionError("simulated work cannot be unpaid")
    paid_energy, paid_vigilance = cognitive_cost(laws, work)
    if any(not isfinite(v) for v in (paid_energy, paid_vigilance)):
        raise AssertionError("nonfinite cognitive model price")

    observer = info.get("observer") or {}
    witnesses = observer.get("score_witness") or []
    if observer.get("scored_options") != len(witnesses):
        raise AssertionError("native scores not captured as original work")
    offered = observer.get("offered_options")
    if type(offered) is not int or offered < len(witnesses):
        raise AssertionError("invalid offered-option count")
    if any(type(w.get("total_score")) not in (int, float)
           or not isfinite(w["total_score"]) for w in witnesses):
        raise AssertionError("invalid native score readout")
    score_rows = [
        {"option": w["option"], "total_score": w["total_score"],
         "base_return": w["base_return"], "curiosity": w["curiosity_bonus_applied"],
         "risk": w["risk_penalty_applied"]}
        for w in witnesses
    ]
    if len({w["option"] for w in score_rows}) != len(score_rows):
        raise AssertionError("duplicate native scored option")

    return {
        "context": context,
        "mode": mode,
        "body": capture["body"],
        "source": SOURCE_KIND,
        "offered_options": offered,
        "scored_options": len(score_rows),
        "score_rows": score_rows,
        "option": info.get("option"),
        "action": action, "param": param,
        "native_horizon": info.get("horizon"),
        "funding": info.get("funding"),
        "work": asdict(work),
        "model_energy_paid": paid_energy,
        "model_vigilance_paid": paid_vigilance,
        "post_model_budget_body": post,
        "no_real_World_debit": True,
    }


def _parity(full, reference):
    keys = (
        "body", "offered_options", "scored_options", "score_rows", "option",
        "action", "param", "native_horizon", "funding", "work",
        "model_energy_paid", "model_vigilance_paid", "post_model_budget_body",
    )
    return all(full[key] == reference[key] for key in keys)


def _comparison(short, full):
    same_offered_count = short["offered_options"] == full["offered_options"]
    same_complete_scored = (
        full["offered_options"] > 0
        and full["scored_options"] == full["offered_options"]
        and short["scored_options"] == short["offered_options"]
    )
    same_order = ([w["option"] for w in short["score_rows"]] ==
                  [w["option"] for w in full["score_rows"]])
    complete_comparable = (
        same_offered_count and same_complete_scored and same_order
    )
    changed_scores = (
        complete_comparable and any(
            abs(a["total_score"] - b["total_score"]) > 1e-9
            for a, b in zip(short["score_rows"], full["score_rows"])
        )
    )
    changed_action = ((short["action"], short["param"]) !=
                      (full["action"], full["param"]))
    changed_option = short["option"] != full["option"]
    return {
        "mode": short["mode"],
        "complete_comparable": complete_comparable,
        "same_order": same_order,
        "changed_scores": changed_scores,
        "changed_option": changed_option,
        "changed_actual_action": changed_action,
        "motor_divergence_with_full_funding": (
            complete_comparable and changed_scores and changed_action
        ),
        "funding_or_offered_confound": (
            not complete_comparable and (changed_option or changed_action)
        ),
        "energy_delta_short_minus_full": (
            short["model_energy_paid"] - full["model_energy_paid"]
        ),
        "vigilance_delta_short_minus_full": (
            short["model_vigilance_paid"] - full["model_vigilance_paid"]
        ),
    }


def audit():
    rows = []
    comparisons = []
    for body_index, body in enumerate(BODIES):
        for context in CONTEXTS:
            by_mode = {mode: _run(body, context, mode) for mode in MODES}
            if not _parity(by_mode["full"], by_mode["reference"]):
                raise AssertionError(
                    "uncapped lab Mind differs from unmodified P1.3 Mind"
                )
            rows.append({"body_index": body_index, "context": context,
                         "modes": by_mode})
            for mode in ("cap1", "cap4"):
                comparisons.append({
                    "body_index": body_index, "context": context,
                    **_comparison(by_mode[mode], by_mode["full"])
                })
    complete = [c for c in comparisons if c["complete_comparable"]]
    changed_motors = [c for c in complete
                      if c["motor_divergence_with_full_funding"]]
    payload = {
        "schema": SCHEMA,
        "source_kind": SOURCE_KIND,
        "rows": rows,
        "comparisons": comparisons,
        "native_decision_calls": len(BODIES) * len(CONTEXTS) * len(MODES),
        "scenarios": len(rows),
        "pairwise_depth_comparisons": len(comparisons),
        "complete_comparable": len(complete),
        "different_score_vector": sum(c["changed_scores"] for c in complete),
        "different_native_option": sum(c["changed_option"] for c in complete),
        "different_actual_motor": sum(c["changed_actual_action"]
                                      for c in complete),
        "action_divergence_with_full_funding": len(changed_motors),
        "incomplete_or_offered_confound": sum(
            c["funding_or_offered_confound"] for c in comparisons),
        "reference_parity": True,
        "mechanism_verdict": (
            "NATIVE_ACTION_DISCRIMINATION_SOFTWARE_ONLY"
            if changed_motors else "NO_DECISION_DISCRIMINATION_ON_FROZEN_GRID"
        ),
        "science": "NOT_ISSUED", "worlds_opened": 0,
        "new_scientific_lives": 0,
        "stage2_2_go": False, "stage2_3_go": False,
    }
    digest = sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"),
                               allow_nan=False).encode("utf-8")).hexdigest()
    return {**payload, "payload_sha256": digest}


if __name__ == "__main__":
    print(json.dumps(audit(), sort_keys=True, indent=2, allow_nan=False))
