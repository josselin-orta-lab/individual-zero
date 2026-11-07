"""Post-hoc audit of Candidate-F observed-effect proxy dispatch.

This audit is triggered by the first frozen omega-F rerun's exact equality
across all six omega arms. It does not modify that rerun or its protocol.
"""
from __future__ import annotations

import json
import sys

from ..modules.body import BodyLaws, CognitiveBudget
from ..modules.observed_effect_view import paid_simulate_after_observed_effect
from . import stage1_omega_falsifier as W

SCHEMA = "i3-candidate-f-observed-effect-dispatch-audit/v1"
BODY = (80.0, 80.0, 50.0, 80.0, 80.0)
PLAN = (("boire",),)
EFFECT_KEY = ("boire",)
POSITIVE = (0.0, 0.0, 10.0, 0.0, 0.0)
NEGATIVE = (0.0, 0.0, -10.0, 0.0, 0.0)
HORIZON = 4

def _json_forecast(value):
    if value is None:
        return None
    return {
        "action_key": list(value["action_key"]),
        "delta": list(value["delta"]),
        "uncertainty": value["uncertainty"],
    }



def _evaluate(simulation_mode, effect):
    mind = W.make_mind()
    mind.observer_decision_diagnostics = True
    mind.simulation_mode = simulation_mode
    if simulation_mode == "candidate_f":
        mind.projection_accounting = "event_local_quadratic4"
    return paid_simulate_after_observed_effect(
        mind, BODY, PLAN, HORIZON, EFFECT_KEY, effect,
        CognitiveBudget(BODY, BodyLaws()))


def run(out_path):
    reference_positive = _evaluate("reference", POSITIVE)
    reference_negative = _evaluate("reference", NEGATIVE)
    candidate_positive = _evaluate("candidate_f", POSITIVE)
    candidate_negative = _evaluate("candidate_f", NEGATIVE)

    reference_separates = (
        abs(reference_positive["value"] - reference_negative["value"]) > 1e-12
        and reference_positive["first_forecast"] is not None
        and reference_negative["first_forecast"] is not None
        and tuple(reference_positive["first_forecast"]["delta"]) == POSITIVE
        and tuple(reference_negative["first_forecast"]["delta"]) == NEGATIVE
    )
    candidate_collapses = (
        abs(candidate_positive["value"] - candidate_negative["value"]) <= 1e-15
        and candidate_positive["first_forecast"] is None
        and candidate_negative["first_forecast"] is None
    )
    bypass_confirmed = reference_separates and candidate_collapses

    report = {
        "schema": SCHEMA,
        "world_access": False,
        "lives": 0,
        "body": list(BODY),
        "plan": [list(key) for key in PLAN],
        "effect_key": list(EFFECT_KEY),
        "positive_effect": list(POSITIVE),
        "negative_effect": list(NEGATIVE),
        "reference": {
            "positive_value": reference_positive["value"],
            "negative_value": reference_negative["value"],
            "value_difference": (
                reference_positive["value"]
                - reference_negative["value"]),
            "positive_first_forecast":
                _json_forecast(reference_positive["first_forecast"]),
            "negative_first_forecast":
                _json_forecast(reference_negative["first_forecast"]),
        },
        "candidate_f": {
            "positive_value": candidate_positive["value"],
            "negative_value": candidate_negative["value"],
            "value_difference": (
                candidate_positive["value"]
                - candidate_negative["value"]),
            "positive_first_forecast":
                _json_forecast(candidate_positive["first_forecast"]),
            "negative_first_forecast":
                _json_forecast(candidate_negative["first_forecast"]),
        },
        "reference_separates_observed_effects": reference_separates,
        "candidate_f_collapses_observed_effects": candidate_collapses,
        "classification": (
            "OBSERVED_EFFECT_VIEW_BYPASSED_BY_CANDIDATE_F_DISPATCH"
            if bypass_confirmed
            else "DISPATCH_BYPASS_NOT_CONFIRMED"),
        "first_omega_rerun_measurement_valid": not bypass_confirmed,
        "scientific_no_capacity_claim_authorized": False,
    }
    with open(out_path, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    return report


if __name__ == "__main__":
    print(json.dumps(run(sys.argv[1]), indent=1, sort_keys=True))
