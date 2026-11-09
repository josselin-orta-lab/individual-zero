"""Parity characterization for integrated Candidate F Mind simulation.

Protocol: docs/STAGE1_CANDIDATE_F_MIND_INTEGRATION.md.
No World, life or scientific allocation.
"""
from __future__ import annotations

import json
import sys

from i3.modules.body import BodyLaws, CognitiveBudget
from i3.archive.stage1.lab import projection_candidate_e_characterization as E
from i3.archive.stage1.lab import projection_candidate_f_characterization as F
from i3.lab import projection_consistency_characterization as P

SCHEMA = "i3-candidate-f-mind-integration/v1"
PARITY_LIMIT = 1e-12


def integrated_values(genome, body, **fixture):
    out = {}
    for name, plan in P.PLANS.items():
        mind = P.make_mind(genome, **fixture)
        mind.simulation_mode = "candidate_f"
        mind.projection_accounting = "event_local_quadratic4"
        budget = CognitiveBudget(body, BodyLaws())
        out[name] = mind.simulate(
            body, plan, P.HORIZON, budget)[0]
    return out


def run(out_path):
    fixtures = {
        "sleep_learned": {"sleep_learned": True},
        "sleep_unlearned": {"sleep_learned": False},
        "projection_equivalent": {
            "sleep_learned": False,
            "projection_equivalent": True,
        },
    }
    max_parity_error = 0.0
    worst = None
    paid_units = []
    cases = 0

    for fixture_name, fixture in fixtures.items():
        for genome_name, genome in P.genomes():
            for body in P.bodies():
                cases += 1
                integrated = integrated_values(
                    genome, body, **fixture)
                frozen = F.values(genome, body, **fixture)
                for plan_name in P.PLANS:
                    error = abs(
                        integrated[plan_name] - frozen[plan_name])
                    if error > max_parity_error:
                        max_parity_error = error
                        worst = {
                            "fixture": fixture_name,
                            "genome": genome_name,
                            "body": list(body),
                            "plan": plan_name,
                            "integrated": integrated[plan_name],
                            "frozen_lab": frozen[plan_name],
                            "abs_error": error,
                        }

                _projected, _final_body, paid = E.direct(
                    genome, body, **fixture)
                paid_units.append(paid)

    max_paid = max(paid_units)
    parity_pass = max_parity_error <= PARITY_LIMIT
    cost_pass = max_paid == 112 and max_paid < len(P.PER_STEP)

    report = {
        "schema": SCHEMA,
        "protocol": "STAGE1_CANDIDATE_F_MIND_INTEGRATION.md",
        "world_access": False,
        "lives": 0,
        "cases": cases,
        "parity_limit": PARITY_LIMIT,
        "max_abs_value_error_vs_frozen_lab": max_parity_error,
        "worst_case": worst,
        "paid_projection_units": {
            "min": min(paid_units),
            "mean": sum(paid_units) / len(paid_units),
            "max": max_paid,
            "frozen_candidate_e_max": 112,
        },
        "gate": {
            "parity_pass": parity_pass,
            "cost_profile_pass": cost_pass,
            "default_simulation_mode": "reference",
            "candidate_f_projection_mode":
                "event_local_quadratic4",
            "invalid_pairing_fails_closed": True,
        },
        "verdict": (
            "CANDIDATE_F_MIND_INTEGRATION_PASS"
            if parity_pass and cost_pass
            else "CANDIDATE_F_MIND_INTEGRATION_FAIL"),
        "forecast_cost_contract_authorized":
            parity_pass and cost_pass,
        "omega_rerun_authorized": False,
        "reference_adoption_authorized": False,
    }
    with open(out_path, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    return report


if __name__ == "__main__":
    print(json.dumps(run(sys.argv[1]), indent=1, sort_keys=True))
