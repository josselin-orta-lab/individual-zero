"""Frozen high-precision projection state oracle for future I3 methodology.

Protocol: docs/STAGE1_PROJECTION_HIGH_PRECISION_ORACLE.md.
Laboratory-only: no runtime projection mode, World, life or study allocation.
"""
from __future__ import annotations

from decimal import Decimal, localcontext
import json
import sys

from ..modules.body import BodyLaws, CognitiveBudget, CognitiveWork, E, F, W, I, V
from . import projection_consistency_characterization as P
from . import projection_event_error_decomposition as X

SCHEMA = "i3-projection-high-precision-oracle/v1"
DECIMAL_PRECISION = 100
NUMERICAL_TOLERANCE = 1e-10


def _decimal(value):
    return Decimal.from_float(float(value))


class _HighPrecisionView:
    __slots__ = ("owner",)

    def __init__(self, owner):
        self.owner = owner

    def __getattr__(self, name):
        return getattr(self.owner, name)

    def project(self, body, drift, budget=None):
        return project_high_precision(self.owner, body, drift, budget)


def project_high_precision(mind, body, drift_spec, budget=None):
    """255-step state recurrence with high-precision represented-float state."""
    if budget is not None:
        budget.spend(CognitiveWork(simulated_steps=len(P.PER_STEP)))

    drift, restore = drift_spec
    with localcontext() as ctx:
        ctx.prec = DECIMAL_PRECISION
        b = [_decimal(x) for x in body]
        theta = [_decimal(x) for x in mind.theta]
        ddrift = [_decimal(x) for x in drift]
        drestore = (
            tuple(_decimal(x) for x in restore)
            if restore is not None else None)
        zero, one, hundred = Decimal(0), Decimal(1), Decimal(100)

        ret = [0.0, 0.0, 0.0]
        disc = [1.0, 1.0, 1.0]
        dead = b[F] <= zero or b[W] <= zero or b[I] <= zero
        reward = (
            -mind.d_max if dead else
            -mind.distress(mind.feats(tuple(float(x) for x in b))))

        for _step in range(len(P.PER_STEP)):
            if not dead:
                for channel in (F, W, I):
                    b[channel] += ddrift[channel]

                if drestore is not None:
                    if drestore[0] <= zero:
                        raise ValueError(
                            "learned restoration energy gain must be positive")
                    need_e = max(zero, theta[E] - b[E]) / drestore[0]
                    need_v = (
                        max(zero, theta[V] - b[V]) / drestore[1]
                        if drestore[1] > zero else zero)
                    n = min(one, max(need_e, need_v))
                    b[E] += n * drestore[0]
                    b[V] += n * drestore[1]
                    b[F] += n * drestore[2]

                for channel in range(5):
                    if b[channel] < zero:
                        b[channel] = zero
                    elif b[channel] > hundred:
                        b[channel] = hundred

                dead = b[F] <= zero or b[W] <= zero or b[I] <= zero
                reward = (
                    -mind.d_max if dead else
                    -mind.distress(
                        mind.feats(tuple(float(x) for x in b))))

            for k, gamma in enumerate(mind.gammas):
                ret[k] += disc[k] * reward
                disc[k] *= gamma

        for k, gamma in enumerate(mind.gammas):
            ret[k] += disc[k] * (reward / (1.0 - gamma))
        return ret, [float(x) for x in b]


def high_precision_values(genome, body, **fixture):
    out = {}
    for name, plan in P.PLANS.items():
        mind = P.make_mind(genome, **fixture)
        view = _HighPrecisionView(mind)
        budget = CognitiveBudget(body, BodyLaws())
        out[name] = type(mind).simulate(
            view, body, plan, P.HORIZON, budget)[0]
    return out


def direct_high_precision(genome, body, **fixture):
    mind = P.make_mind(genome, **fixture)
    budget = CognitiveBudget(body, BodyLaws())
    values, final_body = project_high_precision(
        mind, body, mind._drift, budget)
    return values, tuple(final_body), budget.work.simulated_steps


def _empty_comparison():
    return {
        "max_abs_prefix_error_vs_oracle": 0.0,
        "max_decision_bias_vs_oracle": 0.0,
        "projection_equivalent_invariant_max_gap": 0.0,
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
        "event_exact": _empty_comparison(),
        "historical_per_step": _empty_comparison(),
    }
    oracle_invariant = 0.0
    units = []
    cases = 0
    worst = {
        "event_exact_decision_bias": None,
        "event_exact_final_body": None,
        "historical_per_step_decision_bias": None,
        "historical_per_step_final_body": None,
    }

    for fixture_name, fixture in fixtures.items():
        for genome_name, genome in P.genomes():
            for body in P.bodies():
                cases += 1
                oracle = high_precision_values(genome, body, **fixture)
                event = X.event_exact_values(genome, body, **fixture)
                historical = P.values(
                    genome, body, "per_step", **fixture)

                oracle_gaps = {
                    "plus_1_wait": (
                        oracle["plus_1_wait"] - oracle["prefix"]),
                    "plus_3_waits": (
                        oracle["plus_3_waits"] - oracle["prefix"]),
                }
                if fixture_name == "projection_equivalent":
                    oracle_invariant = max(
                        oracle_invariant,
                        *(abs(x) for x in oracle_gaps.values()))

                for comparison_name, values in (
                        ("event_exact", event),
                        ("historical_per_step", historical)):
                    st = comparisons[comparison_name]
                    st["max_abs_prefix_error_vs_oracle"] = max(
                        st["max_abs_prefix_error_vs_oracle"],
                        abs(values["prefix"] - oracle["prefix"]))
                    candidate_gaps = {
                        "plus_1_wait": (
                            values["plus_1_wait"] - values["prefix"]),
                        "plus_3_waits": (
                            values["plus_3_waits"] - values["prefix"]),
                    }
                    bias_by_plan = {
                        name: abs(candidate_gaps[name] - oracle_gaps[name])
                        for name in candidate_gaps
                    }
                    decision_bias = max(bias_by_plan.values())
                    if decision_bias > st["max_decision_bias_vs_oracle"]:
                        st["max_decision_bias_vs_oracle"] = decision_bias
                        worst[f"{comparison_name}_decision_bias"] = {
                            "fixture": fixture_name,
                            "genome": genome_name,
                            "body": list(body),
                            "comparison": max(
                                bias_by_plan, key=bias_by_plan.get),
                            "abs_bias": decision_bias,
                        }
                    if fixture_name == "projection_equivalent":
                        st[
                            "projection_equivalent_invariant_max_gap"
                        ] = max(
                            st[
                                "projection_equivalent_invariant_max_gap"],
                            *(abs(x) for x in candidate_gaps.values()))

                _ov, oracle_body, paid = direct_high_precision(
                    genome, body, **fixture)
                _ev, event_body, _event_paid = X.direct_event_exact(
                    genome, body, **fixture)
                _hv, historical_body, _historical_paid = (
                    X.direct_per_step(genome, body, **fixture))
                units.append(paid)

                for comparison_name, final_body in (
                        ("event_exact", event_body),
                        ("historical_per_step", historical_body)):
                    errors = tuple(
                        abs(a - b) for a, b in zip(
                            final_body, oracle_body))
                    error = max(errors)
                    st = comparisons[comparison_name]
                    if error > st[
                            "max_final_body_channel_error_vs_oracle"]:
                        st[
                            "max_final_body_channel_error_vs_oracle"
                        ] = error
                        worst[f"{comparison_name}_final_body"] = {
                            "fixture": fixture_name,
                            "genome": genome_name,
                            "body": list(body),
                            "channel": errors.index(error),
                            "comparison_final_body": list(final_body),
                            "oracle_final_body": list(oracle_body),
                            "abs_error": error,
                        }

    event = comparisons["event_exact"]
    historical = comparisons["historical_per_step"]
    event_matches = (
        event["max_decision_bias_vs_oracle"] <= NUMERICAL_TOLERANCE
        and event["projection_equivalent_invariant_max_gap"]
            <= NUMERICAL_TOLERANCE
        and event["max_final_body_channel_error_vs_oracle"]
            <= NUMERICAL_TOLERANCE
        and oracle_invariant <= NUMERICAL_TOLERANCE
    )
    historical_differs = (
        historical["max_decision_bias_vs_oracle"] > NUMERICAL_TOLERANCE
        or historical[
            "projection_equivalent_invariant_max_gap"]
            > NUMERICAL_TOLERANCE
        or historical[
            "max_final_body_channel_error_vs_oracle"]
            > NUMERICAL_TOLERANCE
    )

    if event_matches and historical_differs:
        classification = "EVENT_EXACT_MATCHES_HIGH_PRECISION_ORACLE"
        authorized = True
    elif event_matches:
        classification = "NO_NUMERICAL_SEMANTICS_DIFFERENCE_ON_FROZEN_GRID"
        authorized = True
    else:
        classification = "EVENT_SEGMENTATION_DIFFERS_FROM_HIGH_PRECISION_ORACLE"
        authorized = False

    report = {
        "schema": SCHEMA,
        "protocol": "STAGE1_PROJECTION_HIGH_PRECISION_ORACLE.md",
        "world_access": False,
        "lives": 0,
        "cases": cases,
        "decimal_precision": DECIMAL_PRECISION,
        "numerical_tolerance": NUMERICAL_TOLERANCE,
        "oracle_projection_equivalent_invariant_max_gap": oracle_invariant,
        "comparisons": comparisons,
        "paid_high_precision_projection_units": {
            "min": min(units),
            "mean": sum(units) / len(units),
            "max": max(units),
            "historical_per_step": len(P.PER_STEP),
        },
        "worst_cases": worst,
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
