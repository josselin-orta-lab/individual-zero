"""Frozen characterization of Stage-1 projection candidate C.

Protocol: docs/STAGE1_PROJECTION_EVENT_AWARE.md.
No World, no life, no study index.

    python -m i3.lab.projection_event_aware_characterization OUTPUT.json
"""
from __future__ import annotations

import json
import sys

from ..modules.body import BodyLaws, CognitiveBudget
from ..modules.genome import midpoint
from . import projection_consistency_characterization as P

SCHEMA = "i3-projection-event-aware-characterization/v1"
CANDIDATE = "event_quadratic"
TRUTH = "per_step"
BIAS_LIMIT = 1e-3
INVARIANT_LIMIT = 1e-3


def configure(mind, scheme):
    if scheme == TRUTH:
        mind.proj_chunks = P.PER_STEP
        mind.projection_accounting = "chunk_end"
    else:
        mind.projection_accounting = scheme
    return mind


def values(genome, body, scheme, **fixture):
    out = {}
    for name, plan in P.PLANS.items():
        mind = configure(P.make_mind(genome, **fixture), scheme)
        out[name] = mind.simulate(
            body, plan, P.HORIZON,
            CognitiveBudget(body, BodyLaws()))[0]
    return out


def direct_projection_units(genome, body, **fixture):
    mind = configure(P.make_mind(genome, **fixture), CANDIDATE)
    budget = CognitiveBudget(body, BodyLaws())
    mind.project(body, mind._drift, budget)
    return budget.work.simulated_steps


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
        "max_abs_gap_plus_1": 0.0,
        "max_abs_gap_plus_3": 0.0,
        "max_abs_prefix_error_vs_per_step": 0.0,
        "max_decision_bias_vs_per_step": 0.0,
    }
    invariant = 0.0
    units = []
    cases = 0

    for fixture_name, fixture in fixtures.items():
        for _genome_name, genome in P.genomes():
            for body in P.bodies():
                cases += 1
                truth = values(genome, body, TRUTH, **fixture)
                candidate = values(genome, body, CANDIDATE, **fixture)

                truth_g1 = truth["plus_1_wait"] - truth["prefix"]
                truth_g3 = truth["plus_3_waits"] - truth["prefix"]
                cand_g1 = candidate["plus_1_wait"] - candidate["prefix"]
                cand_g3 = candidate["plus_3_waits"] - candidate["prefix"]

                stats["max_abs_gap_plus_1"] = max(
                    stats["max_abs_gap_plus_1"], abs(cand_g1))
                stats["max_abs_gap_plus_3"] = max(
                    stats["max_abs_gap_plus_3"], abs(cand_g3))
                stats["max_abs_prefix_error_vs_per_step"] = max(
                    stats["max_abs_prefix_error_vs_per_step"],
                    abs(candidate["prefix"] - truth["prefix"]))
                stats["max_decision_bias_vs_per_step"] = max(
                    stats["max_decision_bias_vs_per_step"],
                    abs(cand_g1 - truth_g1),
                    abs(cand_g3 - truth_g3))

                if fixture_name == "projection_equivalent":
                    invariant = max(
                        invariant, abs(cand_g1), abs(cand_g3))

                units.append(
                    direct_projection_units(genome, body, **fixture))

    max_units = max(units)
    mean_units = sum(units) / len(units)
    min_units = min(units)

    passed = (
        stats["max_decision_bias_vs_per_step"] <= BIAS_LIMIT
        and invariant <= INVARIANT_LIMIT
        and max_units < len(P.PER_STEP)
    )

    report = {
        "schema": SCHEMA,
        "protocol": "STAGE1_PROJECTION_EVENT_AWARE.md",
        "world_access": False,
        "lives": 0,
        "cases": cases,
        "candidate": CANDIDATE,
        "truth": TRUTH,
        "stats": stats,
        "projection_equivalent_invariant_max_gap": invariant,
        "paid_projection_units": {
            "min": min_units,
            "mean": mean_units,
            "max": max_units,
            "per_step_truth": len(P.PER_STEP),
        },
        "selection": {
            "decision_bias_limit": BIAS_LIMIT,
            "invariant_limit": INVARIANT_LIMIT,
            "decision_bias_pass": (
                stats["max_decision_bias_vs_per_step"] <= BIAS_LIMIT),
            "invariant_pass": invariant <= INVARIANT_LIMIT,
            "strictly_cheaper_than_per_step_every_case": (
                max_units < len(P.PER_STEP)),
            "verdict": (
                "EVENT_AWARE_PROMOTED_AS_OPT_IN_CANDIDATE"
                if passed else "NO_CANDIDATE_PROMOTED"),
        },
    }
    with open(out_path, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    return report


if __name__ == "__main__":
    report = run(sys.argv[1])
    print(json.dumps({
        "stats": report["stats"],
        "projection_equivalent_invariant_max_gap":
            report["projection_equivalent_invariant_max_gap"],
        "paid_projection_units": report["paid_projection_units"],
        "selection": report["selection"],
    }, indent=1))
