"""Canonical Decimal event segmentation against the #1117 direct oracle.

Protocol: docs/STAGE1_CANONICAL_EVENT_SEGMENTATION.md.
Laboratory-only. No runtime mode, World, life or scientific allocation.
"""
from __future__ import annotations

from decimal import Decimal, localcontext
import json
import sys

from ..modules.body import BodyLaws, CognitiveBudget, CognitiveWork, E, F, W, I, V
from . import projection_consistency_characterization as P
from . import projection_end_to_end_numeric_oracle as O

SCHEMA = "i3-canonical-event-segmentation/v1"
NUMERICAL_TOLERANCE = 1e-10


def _advance(body, drift, restore, theta, run):
    """Algebraic Decimal endpoint under one active event regime."""
    b = list(body)
    duration = Decimal(run)
    for channel in (F, W, I):
        b[channel] += duration * drift[channel]

    if restore is not None:
        zero = Decimal(0)
        need_e = max(zero, theta[E] - b[E]) / restore[0]
        need_v = (
            max(zero, theta[V] - b[V]) / restore[1]
            if restore[1] > zero else zero)
        # E/V do not passively drift. The total restoration over this interval
        # is the same bounded amount as repeated one-step restoration.
        n = min(duration, max(need_e, need_v))
        b[E] += n * restore[0]
        b[V] += n * restore[1]
        b[F] += n * restore[2]

    O._clamp_decimal(b)
    return b, O._dead_decimal(b)


def _next_segment(body, drift, restore, theta, remaining):
    """Integer run ending before the next canonical bodily regime event."""
    if type(remaining) is not int or remaining < 1:
        raise ValueError("positive integer projection remainder required")

    zero = Decimal(0)
    dremaining = Decimal(remaining)
    restore_time = None
    if restore is not None:
        need_e = max(zero, theta[E] - body[E]) / restore[0]
        need_v = (
            max(zero, theta[V] - body[V]) / restore[1]
            if restore[1] > zero else zero)
        need = max(need_e, need_v)
        if need > zero:
            restore_time = need

    phase = min(
        dremaining,
        restore_time if restore_time is not None else dremaining)
    active_restore = restore_time is not None
    rates = (
        restore[0] if active_restore else zero,
        drift[F] + (restore[2] if active_restore else zero),
        drift[W],
        drift[I],
        restore[1] if active_restore else zero,
    )

    events = []
    if restore_time is not None and restore_time <= dremaining:
        events.append(restore_time)

    hundred = Decimal(100)
    for channel, rate in enumerate(rates):
        if rate == zero:
            continue
        x = body[channel]
        for target in (zero, theta[channel], hundred):
            if rate > zero and x < target:
                event = (target - x) / rate
            elif rate < zero and x > target:
                event = (target - x) / rate
            else:
                continue
            if zero < event <= phase:
                events.append(event)

    if not events:
        return remaining

    event = min(events)
    integral = event.to_integral_value()
    if event == integral:
        before = int(integral) - 1
    else:
        before = int(event)  # Decimal -> int truncates toward zero; event > 0.
    return max(1, min(remaining, before if before >= 1 else 1))


def project_event_exact(mind, body, drift_spec, budget=None):
    """Evaluate every discrete endpoint inside canonical event segments."""
    if budget is None:
        budget = CognitiveBudget(body, BodyLaws())

    with localcontext() as ctx:
        ctx.prec = O.DECIMAL_PRECISION
        state = [O._d(x) for x in body]
        drift_raw, restore_raw = drift_spec
        drift = tuple(O._d(x) for x in drift_raw)
        restore = (
            tuple(O._d(x) for x in restore_raw)
            if restore_raw is not None else None)
        theta = tuple(O._d(x) for x in mind.theta)

        ret = [0.0, 0.0, 0.0]
        disc = [1.0, 1.0, 1.0]
        dead = O._dead_decimal(state)
        reward = (
            -mind.d_max if dead
            else -mind.distress(mind.feats(O._float_body(state))))
        segments = 0

        for outer in mind.proj_chunks:
            remaining = outer
            while remaining > 0:
                if dead:
                    budget.spend(CognitiveWork(simulated_steps=remaining))
                    for k, gamma in enumerate(mind.gammas):
                        g_run = gamma ** remaining
                        weight = (1.0 - g_run) / (1.0 - gamma)
                        ret[k] += disc[k] * (-mind.d_max) * weight
                        disc[k] *= g_run
                    remaining = 0
                    continue

                run = _next_segment(
                    state, drift, restore, theta, remaining)
                segments += 1
                end_state = list(state)
                end_dead = False

                for step in range(1, run + 1):
                    sample, sample_dead = _advance(
                        state, drift, restore, theta, step)
                    budget.spend(CognitiveWork(simulated_steps=1))
                    reward = (
                        -mind.d_max if sample_dead
                        else -mind.distress(
                            mind.feats(O._float_body(sample))))
                    for k, gamma in enumerate(mind.gammas):
                        ret[k] += disc[k] * reward
                        disc[k] *= gamma
                    end_state = sample
                    end_dead = sample_dead
                    if sample_dead and step < run:
                        tail = run - step
                        budget.spend(
                            CognitiveWork(simulated_steps=tail))
                        for k, gamma in enumerate(mind.gammas):
                            g_run = gamma ** tail
                            weight = (
                                (1.0 - g_run) / (1.0 - gamma))
                            ret[k] += (
                                disc[k] * (-mind.d_max) * weight)
                            disc[k] *= g_run
                        reward = -mind.d_max
                        break

                state = list(end_state)
                dead = end_dead
                remaining -= run

        for k, gamma in enumerate(mind.gammas):
            ret[k] += disc[k] * (reward / (1.0 - gamma))
        return (
            ret,
            O._float_body(state),
            segments,
            budget.work.simulated_steps,
        )


def direct(genome, body, **fixture):
    mind = P.make_mind(genome, **fixture)
    budget = CognitiveBudget(body, BodyLaws())
    return project_event_exact(
        mind, body, mind._drift, budget)


def run(out_path):
    fixtures = {
        "sleep_learned": {"sleep_learned": True},
        "sleep_unlearned": {"sleep_learned": False},
        "projection_equivalent": {
            "sleep_learned": False,
            "projection_equivalent": True,
        },
    }
    max_value_error = 0.0
    max_body_error = 0.0
    value_worst = None
    body_worst = None
    segment_counts = []
    paid_units = []
    cases = 0

    for fixture_name, fixture in fixtures.items():
        for genome_name, genome in P.genomes():
            for body in P.bodies():
                cases += 1
                event_values, event_body, segments, paid = direct(
                    genome, body, **fixture)
                oracle_values, oracle_body, oracle_paid = (
                    O.direct_projection(genome, body, **fixture))
                if oracle_paid != len(P.PER_STEP):
                    raise RuntimeError("authorized oracle cost changed")

                value_errors = tuple(
                    abs(a - b) for a, b in zip(
                        event_values, oracle_values))
                value_error = max(value_errors)
                if value_error > max_value_error:
                    max_value_error = value_error
                    value_worst = {
                        "fixture": fixture_name,
                        "genome": genome_name,
                        "body": list(body),
                        "horizon": value_errors.index(value_error),
                        "event_value": event_values[
                            value_errors.index(value_error)],
                        "oracle_value": oracle_values[
                            value_errors.index(value_error)],
                        "abs_error": value_error,
                    }

                body_errors = tuple(
                    abs(a - b) for a, b in zip(
                        event_body, oracle_body))
                body_error = max(body_errors)
                if body_error > max_body_error:
                    max_body_error = body_error
                    body_worst = {
                        "fixture": fixture_name,
                        "genome": genome_name,
                        "body": list(body),
                        "channel": body_errors.index(body_error),
                        "event_final_body": list(event_body),
                        "oracle_final_body": list(oracle_body),
                        "abs_error": body_error,
                    }

                segment_counts.append(segments)
                paid_units.append(paid)

    cost_pass = (
        min(paid_units) == len(P.PER_STEP)
        and max(paid_units) == len(P.PER_STEP))
    matched = (
        max_value_error <= NUMERICAL_TOLERANCE
        and max_body_error <= NUMERICAL_TOLERANCE
        and cost_pass)

    report = {
        "schema": SCHEMA,
        "protocol": "STAGE1_CANONICAL_EVENT_SEGMENTATION.md",
        "world_access": False,
        "lives": 0,
        "cases": cases,
        "numerical_tolerance": NUMERICAL_TOLERANCE,
        "max_projection_value_error_vs_oracle": max_value_error,
        "max_final_body_error_vs_oracle": max_body_error,
        "event_segments": {
            "min": min(segment_counts),
            "mean": sum(segment_counts) / len(segment_counts),
            "max": max(segment_counts),
        },
        "paid_endpoint_units": {
            "min": min(paid_units),
            "mean": sum(paid_units) / len(paid_units),
            "max": max(paid_units),
            "expected": len(P.PER_STEP),
        },
        "worst_cases": {
            "projection_value": value_worst,
            "final_body": body_worst,
        },
        "classification": (
            "CANONICAL_EVENT_SEGMENTATION_MATCHES_ORACLE"
            if matched else
            "CANONICAL_EVENT_SEGMENTATION_DIFFERS_FROM_ORACLE"),
        "event_boundaries_cleared_for_candidate_e": matched,
        "candidate_promoted": False,
        "omega_rerun_authorized": False,
    }
    with open(out_path, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    return report


if __name__ == "__main__":
    print(json.dumps(run(sys.argv[1]), indent=1, sort_keys=True))
