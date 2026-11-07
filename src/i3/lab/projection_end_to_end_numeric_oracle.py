"""Frozen end-to-end high-precision numerical oracle for I3 simulation.

Protocol: docs/STAGE1_END_TO_END_NUMERIC_ORACLE.md.
Laboratory-only. No runtime policy, World, life or scientific allocation.
"""
from __future__ import annotations

from decimal import Decimal, localcontext
import json
import sys

from ..modules.body import (
    BodyLaws, CognitiveBudget, CognitiveWork, E, F, W, I, V)
from . import projection_consistency_characterization as P
from . import projection_event_error_decomposition as X

SCHEMA = "i3-end-to-end-high-precision-oracle/v1"
DECIMAL_PRECISION = 100
NUMERICAL_TOLERANCE = 1e-10


def _d(value):
    return Decimal.from_float(float(value))


def _float_body(body):
    return tuple(float(x) for x in body)


def _clamp_decimal(body):
    zero, hundred = Decimal(0), Decimal(100)
    for channel in range(5):
        if body[channel] < zero:
            body[channel] = zero
        elif body[channel] > hundred:
            body[channel] = hundred


def _dead_decimal(body):
    zero = Decimal(0)
    return body[F] <= zero or body[W] <= zero or body[I] <= zero


def _project_decimal_state(mind, body, drift_spec, budget):
    """Continue one Decimal body through the 255-step bootstrap."""
    budget.spend(CognitiveWork(simulated_steps=len(P.PER_STEP)))
    drift, restore = drift_spec
    ddrift = tuple(_d(x) for x in drift)
    drestore = (
        tuple(_d(x) for x in restore)
        if restore is not None else None)
    theta = tuple(_d(x) for x in mind.theta)
    zero, one = Decimal(0), Decimal(1)

    ret = [0.0, 0.0, 0.0]
    disc = [1.0, 1.0, 1.0]
    dead = _dead_decimal(body)
    reward = (
        -mind.d_max if dead
        else -mind.distress(mind.feats(_float_body(body))))

    for _ in P.PER_STEP:
        if not dead:
            for channel in (F, W, I):
                body[channel] += ddrift[channel]

            if drestore is not None:
                if drestore[0] <= zero:
                    raise ValueError(
                        "learned restoration energy gain must be positive")
                need_e = max(zero, theta[E] - body[E]) / drestore[0]
                need_v = (
                    max(zero, theta[V] - body[V]) / drestore[1]
                    if drestore[1] > zero else zero)
                n = min(one, max(need_e, need_v))
                body[E] += n * drestore[0]
                body[V] += n * drestore[1]
                body[F] += n * drestore[2]

            _clamp_decimal(body)
            dead = _dead_decimal(body)
            reward = (
                -mind.d_max if dead
                else -mind.distress(mind.feats(_float_body(body))))

        for k, gamma in enumerate(mind.gammas):
            ret[k] += disc[k] * reward
            disc[k] *= gamma

    for k, gamma in enumerate(mind.gammas):
        ret[k] += disc[k] * (reward / (1.0 - gamma))
    return ret, body


def simulate_end_to_end(mind, body, plan, horizon, budget):
    """Mirror Mind.simulate with one Decimal state through plan and bootstrap."""
    with localcontext() as ctx:
        ctx.prec = DECIMAL_PRECISION
        b = [_d(x) for x in body]
        steps = 0
        ret = [0.0, 0.0, 0.0]
        disc = [1.0, 1.0, 1.0]
        dead = False
        u_max = 0.0
        i, n = 0, len(plan)

        while i < n and steps < horizon:
            budget.spend(CognitiveWork(simulated_steps=1))
            key = plan[i]
            run = 1
            if key[0] == "se_deplacer":
                while (
                        i + run < n
                        and plan[i + run] == key
                        and run < horizon):
                    run += 1
            i += run

            mean, uncertainty = mind._read_plan_prediction(key)
            u_max = max(u_max, uncertainty)
            drun = Decimal(run)
            for channel in range(5):
                b[channel] += drun * _d(mean[channel])
            _clamp_decimal(b)

            steps += 1
            dead = _dead_decimal(b)
            reward = (
                -mind.d_max if dead
                else -mind.distress(mind.feats(_float_body(b))))
            for k, gamma in enumerate(mind.gammas):
                g_run = gamma ** run
                ret[k] += (
                    disc[k] * reward
                    * ((1.0 - g_run) / (1.0 - gamma)))
                disc[k] *= g_run
            if dead:
                break

        phi = mind.feats(_float_body(b))
        projection = (
            None if dead
            else _project_decimal_state(
                mind, b, mind._drift, budget)[0])

        out = 0.0
        for k, gamma in enumerate(mind.gammas):
            boot = (
                -mind.d_max / (1.0 - gamma)
                if dead else mind.value(k, phi, projection))
            out += (1.0 - gamma) * (
                ret[k] + disc[k] * boot)
        return out / 3.0, steps, u_max


def values(genome, body, **fixture):
    out = {}
    for name, plan in P.PLANS.items():
        mind = P.make_mind(genome, **fixture)
        budget = CognitiveBudget(body, BodyLaws())
        out[name] = simulate_end_to_end(
            mind, body, plan, P.HORIZON, budget)[0]
    return out


def direct_projection(genome, body, **fixture):
    with localcontext() as ctx:
        ctx.prec = DECIMAL_PRECISION
        mind = P.make_mind(genome, **fixture)
        budget = CognitiveBudget(body, BodyLaws())
        decimal_body = [_d(x) for x in body]
        projection, final_body = _project_decimal_state(
            mind, decimal_body, mind._drift, budget)
        return (
            projection,
            _float_body(final_body),
            budget.work.simulated_steps,
        )


def _comparison():
    return {
        "max_abs_prefix_error_vs_oracle": 0.0,
        "max_decision_bias_vs_oracle": 0.0,
        "max_final_body_channel_error_vs_oracle": 0.0,
    }


def run(out_path):
    fixtures = {
        "sleep_learned": {"sleep_learned": True},
        "sleep_unlearned": {"sleep_learned": False},
        "projection_equivalent": {
            "sleep_learned": False,
            "projection_equivalent": True,
        },
    }
    comparisons = {
        "historical_per_step": _comparison(),
        "event_exact": _comparison(),
    }
    oracle_invariant = 0.0
    cases = 0
    direct_units = []
    worst = {
        "historical_per_step_decision_bias": None,
        "event_exact_decision_bias": None,
        "historical_per_step_final_body": None,
        "event_exact_final_body": None,
    }

    for fixture_name, fixture in fixtures.items():
        for genome_name, genome in P.genomes():
            for body in P.bodies():
                cases += 1
                oracle = values(genome, body, **fixture)
                historical = P.values(
                    genome, body, "per_step", **fixture)
                event = X.event_exact_values(
                    genome, body, **fixture)

                oracle_gaps = {
                    name: oracle[name] - oracle["prefix"]
                    for name in ("plus_1_wait", "plus_3_waits")
                }
                if fixture_name == "projection_equivalent":
                    oracle_invariant = max(
                        oracle_invariant,
                        *(abs(x) for x in oracle_gaps.values()))

                for comparison_name, candidate in (
                        ("historical_per_step", historical),
                        ("event_exact", event)):
                    stats = comparisons[comparison_name]
                    stats["max_abs_prefix_error_vs_oracle"] = max(
                        stats["max_abs_prefix_error_vs_oracle"],
                        abs(candidate["prefix"] - oracle["prefix"]))
                    candidate_gaps = {
                        name: candidate[name] - candidate["prefix"]
                        for name in (
                            "plus_1_wait", "plus_3_waits")
                    }
                    bias = {
                        name: abs(
                            candidate_gaps[name] - oracle_gaps[name])
                        for name in candidate_gaps
                    }
                    max_bias = max(bias.values())
                    if max_bias > stats["max_decision_bias_vs_oracle"]:
                        stats["max_decision_bias_vs_oracle"] = max_bias
                        worst[f"{comparison_name}_decision_bias"] = {
                            "fixture": fixture_name,
                            "genome": genome_name,
                            "body": list(body),
                            "comparison": max(bias, key=bias.get),
                            "abs_bias": max_bias,
                        }

                _op, oracle_body, paid = direct_projection(
                    genome, body, **fixture)
                _hp, historical_body, _hpaid = X.direct_per_step(
                    genome, body, **fixture)
                _ep, event_body, _epaid = X.direct_event_exact(
                    genome, body, **fixture)
                direct_units.append(paid)

                for comparison_name, candidate_body in (
                        ("historical_per_step", historical_body),
                        ("event_exact", event_body)):
                    errors = tuple(
                        abs(a - b) for a, b in zip(
                            candidate_body, oracle_body))
                    error = max(errors)
                    stats = comparisons[comparison_name]
                    if error > stats[
                            "max_final_body_channel_error_vs_oracle"]:
                        stats[
                            "max_final_body_channel_error_vs_oracle"
                        ] = error
                        worst[f"{comparison_name}_final_body"] = {
                            "fixture": fixture_name,
                            "genome": genome_name,
                            "body": list(body),
                            "channel": errors.index(error),
                            "comparison_final_body":
                                list(candidate_body),
                            "oracle_final_body": list(oracle_body),
                            "abs_error": error,
                        }

    boundary_body = (80.0, 10.0, 80.0, 80.0, 80.0)
    _bp, boundary_final, boundary_paid = direct_projection(
        P.midpoint(), boundary_body, sleep_learned=True)
    boundary_pass = (
        abs(boundary_final[F] - 0.0) <= NUMERICAL_TOLERANCE
        and abs(boundary_final[W] - 60.0) <= NUMERICAL_TOLERANCE
        and abs(boundary_final[I] - 90.0) <= NUMERICAL_TOLERANCE
    )
    cost_pass = (
        min(direct_units) == len(P.PER_STEP)
        and max(direct_units) == len(P.PER_STEP)
        and boundary_paid == len(P.PER_STEP)
    )
    invariant_pass = oracle_invariant <= NUMERICAL_TOLERANCE

    authorized = invariant_pass and boundary_pass and cost_pass
    classification = (
        "END_TO_END_HIGH_PRECISION_ORACLE_AUTHORIZED_FOR_FUTURE_CANDIDATES"
        if authorized
        else "END_TO_END_HIGH_PRECISION_ORACLE_REJECTED"
    )

    report = {
        "schema": SCHEMA,
        "protocol": "STAGE1_END_TO_END_NUMERIC_ORACLE.md",
        "world_access": False,
        "lives": 0,
        "cases": cases,
        "decimal_precision": DECIMAL_PRECISION,
        "numerical_tolerance": NUMERICAL_TOLERANCE,
        "oracle_projection_equivalent_invariant_max_gap":
            oracle_invariant,
        "boundary_witness": {
            "body": list(boundary_body),
            "final_body": list(boundary_final),
            "pass": boundary_pass,
        },
        "direct_projection_units": {
            "min": min(direct_units),
            "mean": sum(direct_units) / len(direct_units),
            "max": max(direct_units),
            "expected": len(P.PER_STEP),
            "pass": cost_pass,
        },
        "comparisons": comparisons,
        "worst_cases": worst,
        "gate": {
            "invariant_pass": invariant_pass,
            "boundary_pass": boundary_pass,
            "cost_pass": cost_pass,
            "runtime_mode_added": False,
        },
        "classification": classification,
        "oracle_authorized_for_future_candidates": authorized,
        "historical_gates_changed": False,
        "candidate_promoted": False,
        "omega_rerun_authorized": False,
    }
    with open(out_path, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    return report


if __name__ == "__main__":
    print(json.dumps(run(sys.argv[1]), indent=1, sort_keys=True))
