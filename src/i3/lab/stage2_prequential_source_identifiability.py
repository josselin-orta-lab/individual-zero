"""No-World source-separability witness for past self-forecast errors.

The two input histories were frozen BEFORE this software implementation,
though prior real DEV error histories were already examined. No World, Mind
decision, cognitive payment, policy, survival or independent study is implied.
"""
from __future__ import annotations

from hashlib import sha256
import json
from math import fsum, isfinite

from ..modules.mind import EffectsModel
from ..modules.personal_outcomes import WINDOW

SCHEMA = "i3-stage2.1-prequential-source-identifiability/v1"
KEY = ("boire",)
ORDER_A = (0, 0, 0, 8, 4, 4, 4, 4)
ORDER_B = (8, 0, 0, 0, 4, 4, 4, 4)
MAX_STEPS = 8


def _trace(water_effects):
    """Scored pre-outcome, then learned: original EffectsModel, no oracle."""
    if (type(water_effects) is not tuple or
            len(water_effects) != MAX_STEPS or
            any(type(v) not in (int, float) or not isfinite(v)
                or not -100 <= v <= 100 for v in water_effects)):
        raise ValueError("complete finite eight-event artificial history required")
    learned = EffectsModel()
    events = []
    for index, observed in enumerate(water_effects, start=1):
        # The native learned mean is frozen *before* its factual next delta.
        mean, uncertainty = learned.predict(KEY)
        if len(mean) != 5 or not isfinite(uncertainty):
            raise ValueError("unexpected native five-channel predictor")
        observed_vector = (0., 0., float(observed), 0., 0.)
        loss = fsum((a-b)**2 for a, b in zip(mean, observed_vector)) / 5.
        if not isfinite(loss) or loss < 0:
            raise ValueError("invalid prequential squared loss")
        previous_support = learned.stats.get(KEY)
        events.append({
            "step": index,
            "previous_exact_count": previous_support[2] if previous_support else 0,
            "native_preoutcome_forecast": tuple(mean),
            "native_preoutcome_uncertainty": uncertainty,
            "lived_outcome_delta": observed_vector,
            "prequential_five_channel_mse": loss,
        })
        # This is only the *same original model update* on an abstract input.
        learned.observe(KEY, observed_vector)
    terminal_mean, terminal_u = learned.predict(KEY)
    exact = learned.stats.get(KEY)
    if not exact or exact[2] != MAX_STEPS:
        raise ValueError("native model lost exact-key history")
    stats = tuple(sorted(
        (str(key), n, tuple(mean), count)
        for key, (n, mean, count) in learned.stats.items()
    ))
    return {
        "events": events,
        "water_effects": water_effects,
        "terminal_model_stats": stats,
        "terminal_prediction": tuple(terminal_mean),
        "terminal_uncertainty": terminal_u,
        "terminal_exact_count": exact[2],
        "last_bounded_effect_support": water_effects[-WINDOW:],
        "total_prequential_five_channel_mse": fsum(
            item["prequential_five_channel_mse"] for item in events),
    }


def audit():
    """Frozen A/B contrast, no search over permutations or original worlds."""
    if (ORDER_A, ORDER_B) != (
            (0, 0, 0, 8, 4, 4, 4, 4),
            (8, 0, 0, 0, 4, 4, 4, 4)):
        raise ValueError("frozen preflight pair changed")
    if WINDOW != 3:
        raise ValueError("original bounded branch support contract changed")
    a, b = _trace(ORDER_A), _trace(ORDER_B)
    if (sorted(a["water_effects"]) != sorted(b["water_effects"]) or
            a["last_bounded_effect_support"] != b["last_bounded_effect_support"] or
            a["terminal_model_stats"] != b["terminal_model_stats"] or
            a["terminal_prediction"] != b["terminal_prediction"] or
            a["terminal_uncertainty"] != b["terminal_uncertainty"] or
            a["terminal_exact_count"] != b["terminal_exact_count"] or
            a["terminal_exact_count"] != MAX_STEPS):
        raise ValueError("same terminal model and bounded support not established")
    if abs(a["total_prequential_five_channel_mse"] -
           b["total_prequential_five_channel_mse"]) <= 1e-10:
        raise ValueError("no different personally experienced forecast errors")
    if _trace(ORDER_A) != a:
        raise ValueError("identity control failed")
    result = {
        "schema": SCHEMA,
        "status": "SOFTWARE_SOURCE_SEPARABILITY_WITNESS_PASS",
        "scope": "FROZEN_ARTIFICIAL_EIGHT_EVENT_NO_WORLD",
        "source_frozen_before_witness_code": True,
        "same_final_native_model": True,
        "same_full_outcome_multiset": True,
        "same_last_three_action_effects": True,
        "different_past_own_prediction_errors": True,
        "not_proven_novel_vs_full_ordered_history": True,
        "incremental_prospective_predictive_value_demonstrated": False,
        "actual_optional_cognition_purchased": False,
        "native_motor_mediation_demonstrated": False,
        "real_world_cognitive_debit": False,
        "independent_ecology_or_population": False,
        "new_worlds": 0, "scientific_lives": 0,
        "scientific_verdict": "NOT_ISSUED",
        "order_a": a, "order_b": b,
    }
    result["deterministic_sha256"] = sha256(json.dumps(
        result, sort_keys=True, separators=(",", ":"),
        allow_nan=False
    ).encode("utf-8")).hexdigest()
    return result


if __name__ == "__main__":
    print("I3_PREQUENTIAL_SOURCE_IDENTIFIABILITY="+json.dumps(
        audit(), sort_keys=True, separators=(",", ":"), allow_nan=False))
