"""Read-only audit of the worst #1114 projection death boundary."""
from __future__ import annotations

from decimal import Decimal
import json
import sys

from ..modules.body import F, W, I
from ..modules.genome import midpoint
from . import projection_consistency_characterization as P
from . import projection_event_error_decomposition as X

SCHEMA = "i3-projection-death-boundary-audit/v1"
BODY = (80.0, 10.0, 80.0, 80.0, 80.0)
TRACE_STEPS = (49, 50, 51)


def _dead(body):
    return body[F] <= 0.0 or body[W] <= 0.0 or body[I] <= 0.0


def _repeated_unit_trace(mind, body, max_steps=80):
    drift, restore = mind._drift
    current = list(body)
    rows = {}
    first_dead = None
    for step in range(1, max_steps + 1):
        current, dead = mind._projection_advance(
            current, drift, restore, 1)
        current = list(current)
        if step in TRACE_STEPS:
            rows[step] = {
                "body": tuple(current),
                "dead": dead,
            }
        if dead and first_dead is None:
            first_dead = step
            break
    return first_dead, rows, tuple(current)


def _algebraic_trace(mind, body, max_steps=80):
    drift, restore = mind._drift
    rows = {}
    first_dead = None
    dead_body = None
    for step in range(1, max_steps + 1):
        current, dead = mind._projection_advance(
            body, drift, restore, step)
        if step in TRACE_STEPS:
            rows[step] = {
                "body": tuple(current),
                "dead": dead,
            }
        if dead and first_dead is None:
            first_dead = step
            dead_body = tuple(current)
            break
    return first_dead, rows, dead_body


def run(out_path):
    mind = P.make_mind(midpoint(), sleep_learned=True)
    drift, restore = mind._drift

    # In this exposed worst case E/V start above the midpoint theta, so sleep
    # restoration exists in memory but is inactive for direct projection.
    need_e = max(0.0, mind.theta[0] - BODY[0]) / restore[0]
    need_v = (
        max(0.0, mind.theta[4] - BODY[4]) / restore[1]
        if restore[1] > 0.0 else 0.0)
    initial_restore_need = max(need_e, need_v)

    repeated_dead, repeated_rows, repeated_dead_body = (
        _repeated_unit_trace(mind, BODY))
    algebraic_dead, algebraic_rows, algebraic_dead_body = (
        _algebraic_trace(mind, BODY))

    decimal_food = {
        step: str(
            Decimal(str(BODY[F]))
            + Decimal(step) * Decimal(str(drift[F])))
        for step in TRACE_STEPS
    }

    _event_values, event_final, _event_paid = X.direct_event_exact(
        midpoint(), BODY, sleep_learned=True)
    _truth_values, per_step_final, _truth_paid = X.direct_per_step(
        midpoint(), BODY, sleep_learned=True)

    boundary_delta = tuple(
        repeated_dead_body[c] - algebraic_dead_body[c]
        for c in range(5))

    confirmed = (
        initial_restore_need == 0.0
        and algebraic_dead is not None
        and repeated_dead == algebraic_dead + 1
        and Decimal(decimal_food[algebraic_dead]) == Decimal("0")
        and abs(boundary_delta[W] - drift[W]) <= 1e-12
        and abs(boundary_delta[I] - drift[I]) <= 1e-12
        and max(abs(a - b) for a, b in zip(
            repeated_dead_body, per_step_final)) <= 1e-12
        and max(abs(a - b) for a, b in zip(
            algebraic_dead_body, event_final)) <= 1e-12
    )

    report = {
        "schema": SCHEMA,
        "protocol": "STAGE1_PROJECTION_DEATH_BOUNDARY_AUDIT.md",
        "world_access": False,
        "lives": 0,
        "source_case": {
            "fixture": "sleep_learned",
            "genome": "midpoint",
            "body": list(BODY),
        },
        "drift": list(drift),
        "restore": list(restore) if restore is not None else None,
        "initial_restore_need": initial_restore_need,
        "repeated_unit": {
            "first_dead_step": repeated_dead,
            "trace": {
                str(k): {
                    "body": list(v["body"]),
                    "dead": v["dead"],
                } for k, v in repeated_rows.items()
            },
            "dead_body": list(repeated_dead_body),
        },
        "algebraic_endpoint": {
            "first_dead_step": algebraic_dead,
            "trace": {
                str(k): {
                    "body": list(v["body"]),
                    "dead": v["dead"],
                } for k, v in algebraic_rows.items()
            },
            "dead_body": list(algebraic_dead_body),
        },
        "decimal_food": {
            str(k): v for k, v in decimal_food.items()
        },
        "death_endpoint_body_delta_repeated_minus_algebraic":
            list(boundary_delta),
        "event_exact_final_body": list(event_final),
        "per_step_final_body": list(per_step_final),
        "classification": (
            "FLOAT_ACCUMULATION_DELAYS_REFERENCE_DEATH_BOUNDARY"
            if confirmed else "BOUNDARY_CAUSE_NOT_CONFIRMED"),
        "historical_gate_changed": False,
        "candidate_promoted": False,
        "omega_rerun_authorized": False,
    }
    with open(out_path, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    return report


if __name__ == "__main__":
    print(json.dumps(run(sys.argv[1]), indent=1, sort_keys=True))
