"""Frozen characterization of Stage-1 projection Candidate E.

Protocol: docs/STAGE1_PROJECTION_CANDIDATE_E.md.
Truth: #1117 end-to-end high-precision laboratory oracle.
No World, life or study index.
"""
from __future__ import annotations

import json
import sys

from ..modules.body import BodyLaws, CognitiveBudget
from . import projection_consistency_characterization as P
from . import projection_end_to_end_numeric_oracle as O

SCHEMA = "i3-projection-candidate-e-characterization/v1"
CANDIDATE = "event_local_quadratic4"
BIAS_LIMIT = 1e-3
INVARIANT_LIMIT = 1e-3
BODY_LIMIT = 1e-10


def configure(mind):
    mind.projection_accounting = CANDIDATE
    return mind


def values(genome, body, **fixture):
    out = {}
    for name, plan in P.PLANS.items():
        mind = configure(P.make_mind(genome, **fixture))
        out[name] = mind.simulate(
            body, plan, P.HORIZON,
            CognitiveBudget(body, BodyLaws()))[0]
    return out


def direct(genome, body, **fixture):
    mind = configure(P.make_mind(genome, **fixture))
    budget = CognitiveBudget(body, BodyLaws())
    projected, final_body = mind.project(
        body, mind._drift, budget)
    return (
        projected,
        tuple(final_body),
        budget.work.simulated_steps,
    )


def run(out_path):
    fixtures = {
        "sleep_learned": {"sleep_learned": True},
        "sleep_unlearned": {"sleep_learned": False},
        "projection_equivalent": {
            "sleep_learned": False,
            "projection_equivalent": True,
        },
    }
    stats = {
        "max_abs_prefix_error_vs_oracle": 0.0,
        "max_decision_bias_vs_oracle": 0.0,
        "max_abs_gap_plus_1": 0.0,
        "max_abs_gap_plus_3": 0.0,
        "max_direct_projection_value_error_vs_oracle": 0.0,
        "max_direct_final_body_error_vs_oracle": 0.0,
    }
    invariant = 0.0
    paid_units = []
    cases = 0
    worst = {
        "prefix_error": None,
        "decision_bias": None,
        "direct_projection_value": None,
        "direct_final_body": None,
    }

    for fixture_name, fixture in fixtures.items():
        for genome_name, genome in P.genomes():
            for body in P.bodies():
                cases += 1
                oracle = O.values(genome, body, **fixture)
                candidate = values(genome, body, **fixture)

                oracle_g1 = oracle["plus_1_wait"] - oracle["prefix"]
                oracle_g3 = oracle["plus_3_waits"] - oracle["prefix"]
                cand_g1 = (
                    candidate["plus_1_wait"] - candidate["prefix"])
                cand_g3 = (
                    candidate["plus_3_waits"] - candidate["prefix"])

                stats["max_abs_gap_plus_1"] = max(
                    stats["max_abs_gap_plus_1"], abs(cand_g1))
                stats["max_abs_gap_plus_3"] = max(
                    stats["max_abs_gap_plus_3"], abs(cand_g3))

                prefix_error = abs(
                    candidate["prefix"] - oracle["prefix"])
                if prefix_error > stats[
                        "max_abs_prefix_error_vs_oracle"]:
                    stats[
                        "max_abs_prefix_error_vs_oracle"
                    ] = prefix_error
                    worst["prefix_error"] = {
                        "fixture": fixture_name,
                        "genome": genome_name,
                        "body": list(body),
                        "candidate": candidate["prefix"],
                        "oracle": oracle["prefix"],
                        "abs_error": prefix_error,
                    }

                bias_1 = abs(cand_g1 - oracle_g1)
                bias_3 = abs(cand_g3 - oracle_g3)
                decision_bias = max(bias_1, bias_3)
                if decision_bias > stats[
                        "max_decision_bias_vs_oracle"]:
                    stats["max_decision_bias_vs_oracle"] = (
                        decision_bias)
                    worst["decision_bias"] = {
                        "fixture": fixture_name,
                        "genome": genome_name,
                        "body": list(body),
                        "comparison": (
                            "plus_1_wait"
                            if bias_1 >= bias_3
                            else "plus_3_waits"),
                        "candidate_gap": (
                            cand_g1 if bias_1 >= bias_3
                            else cand_g3),
                        "oracle_gap": (
                            oracle_g1 if bias_1 >= bias_3
                            else oracle_g3),
                        "abs_bias": decision_bias,
                    }

                if fixture_name == "projection_equivalent":
                    invariant = max(
                        invariant, abs(cand_g1), abs(cand_g3))

                candidate_projection, candidate_body, paid = (
                    direct(genome, body, **fixture))
                oracle_projection, oracle_body, oracle_paid = (
                    O.direct_projection(genome, body, **fixture))
                if oracle_paid != len(P.PER_STEP):
                    raise RuntimeError("authorized oracle cost changed")
                paid_units.append(paid)

                value_errors = tuple(
                    abs(a - b) for a, b in zip(
                        candidate_projection, oracle_projection))
                value_error = max(value_errors)
                if value_error > stats[
                        "max_direct_projection_value_error_vs_oracle"]:
                    stats[
                        "max_direct_projection_value_error_vs_oracle"
                    ] = value_error
                    h = value_errors.index(value_error)
                    worst["direct_projection_value"] = {
                        "fixture": fixture_name,
                        "genome": genome_name,
                        "body": list(body),
                        "horizon": h,
                        "candidate": candidate_projection[h],
                        "oracle": oracle_projection[h],
                        "abs_error": value_error,
                    }

                body_errors = tuple(
                    abs(a - b) for a, b in zip(
                        candidate_body, oracle_body))
                body_error = max(body_errors)
                if body_error > stats[
                        "max_direct_final_body_error_vs_oracle"]:
                    stats[
                        "max_direct_final_body_error_vs_oracle"
                    ] = body_error
                    channel = body_errors.index(body_error)
                    worst["direct_final_body"] = {
                        "fixture": fixture_name,
                        "genome": genome_name,
                        "body": list(body),
                        "channel": channel,
                        "candidate_final_body":
                            list(candidate_body),
                        "oracle_final_body": list(oracle_body),
                        "abs_error": body_error,
                    }

    max_paid = max(paid_units)
    passed = (
        stats["max_decision_bias_vs_oracle"] <= BIAS_LIMIT
        and invariant <= INVARIANT_LIMIT
        and stats[
            "max_direct_final_body_error_vs_oracle"
        ] <= BODY_LIMIT
        and max_paid < len(P.PER_STEP)
    )

    report = {
        "schema": SCHEMA,
        "protocol": "STAGE1_PROJECTION_CANDIDATE_E.md",
        "world_access": False,
        "lives": 0,
        "cases": cases,
        "candidate": CANDIDATE,
        "truth":
            "end_to_end_high_precision_oracle_1117",
        "stats": stats,
        "projection_equivalent_invariant_max_gap": invariant,
        "paid_projection_units": {
            "min": min(paid_units),
            "mean": sum(paid_units) / len(paid_units),
            "max": max_paid,
            "oracle": len(P.PER_STEP),
        },
        "worst_cases": worst,
        "selection": {
            "decision_bias_limit": BIAS_LIMIT,
            "invariant_limit": INVARIANT_LIMIT,
            "final_body_limit": BODY_LIMIT,
            "decision_bias_pass":
                stats["max_decision_bias_vs_oracle"]
                <= BIAS_LIMIT,
            "invariant_pass": invariant <= INVARIANT_LIMIT,
            "final_body_pass":
                stats[
                    "max_direct_final_body_error_vs_oracle"
                ] <= BODY_LIMIT,
            "strictly_cheaper_than_oracle_every_case":
                max_paid < len(P.PER_STEP),
            "verdict": (
                "CANDIDATE_E_PROMOTED_AS_OPT_IN"
                if passed else "NO_CANDIDATE_PROMOTED"),
        },
        "default_changed": False,
        "omega_rerun_authorized": passed,
        "reference_adoption_authorized": False,
    }
    with open(out_path, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    return report


if __name__ == "__main__":
    print(json.dumps(run(sys.argv[1]), indent=1, sort_keys=True))
