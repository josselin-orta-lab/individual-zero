"""Frozen Candidate F forecast-ceiling characterization.

Protocol: docs/STAGE1_CANDIDATE_F_FORECAST_CEILING.md.
Software only. No World, life or study allocation.
"""
from __future__ import annotations

import json
import sys

from ..modules.body import BodyLaws, CognitiveBudget, CognitiveFundingError
from ..modules.forecast_work import projection_simulated_steps_ceiling
from ..modules.genome import midpoint
from ..modules.water_future_opportunity import (
    paid_water_one_future_opportunity_value)
from . import projection_candidate_e_characterization as E
from . import projection_consistency_characterization as P
from . import stage1_omega_falsifier as W

SCHEMA = "i3-candidate-f-forecast-ceiling/v1"


def candidate_f_mind():
    mind = W.make_mind()
    mind.simulation_mode = "candidate_f"
    mind.projection_accounting = "event_local_quadratic4"
    return mind


def run(out_path):
    reference = W.make_mind()
    reference_quote = projection_simulated_steps_ceiling(reference)

    candidate = candidate_f_mind()
    candidate_quote = projection_simulated_steps_ceiling(candidate)

    rejected_fail_closed = {}
    for mode in ("event_quadratic", "event_quartic"):
        probe = W.make_mind()
        probe.projection_accounting = mode
        try:
            projection_simulated_steps_ceiling(probe)
        except ValueError:
            rejected_fail_closed[mode] = True
        else:
            rejected_fail_closed[mode] = False

    actual_direct = []
    for fixture in (
            {"sleep_learned": True},
            {"sleep_learned": False},
            {"sleep_learned": False, "projection_equivalent": True}):
        for _genome_name, genome in P.genomes():
            for body in P.bodies():
                _projected, _final, paid = E.direct(
                    genome, body, **fixture)
                actual_direct.append(paid)

    omega_rows = []
    ceiling_covers = True
    evaluated = unfunded = 0
    max_actual_simulated = 0
    max_ceiling_simulated = 0
    for channel, level, body, horizon in W.grid():
        model = candidate_f_mind()
        try:
            result = paid_water_one_future_opportunity_value(
                model, W.realistic_memory(), W.EXPLORE,
                W.STOP_AFTER_PREFIX, horizon,
                CognitiveBudget(body, BodyLaws()), omega=0.0)
        except CognitiveFundingError:
            unfunded += 1
            omega_rows.append({
                "channel": channel,
                "level": level,
                "horizon": horizon,
                "status": "UNFUNDED",
            })
            continue

        evaluated += 1
        work = result["work"]
        ceiling = result["forecast_work_ceiling"]
        covered = all(
            work[key] <= ceiling[key]
            for key in ("cycles", "simulated_steps", "memory_items", "replays"))
        ceiling_covers = ceiling_covers and covered
        max_actual_simulated = max(
            max_actual_simulated, work["simulated_steps"])
        max_ceiling_simulated = max(
            max_ceiling_simulated, ceiling["simulated_steps"])
        omega_rows.append({
            "channel": channel,
            "level": level,
            "horizon": horizon,
            "status": "EVALUATED",
            "covered": covered,
            "work": work,
            "forecast_work_ceiling": ceiling,
        })

    direct_bound_pass = max(actual_direct) <= candidate_quote
    reference_pass = reference_quote == len(reference.proj_chunks) == 8
    rejected_pass = all(rejected_fail_closed.values())
    omega_pass = evaluated > 0 and ceiling_covers

    passed = (
        direct_bound_pass and reference_pass
        and rejected_pass and omega_pass)

    report = {
        "schema": SCHEMA,
        "protocol": "STAGE1_CANDIDATE_F_FORECAST_CEILING.md",
        "world_access": False,
        "lives": 0,
        "reference_projection_quote": reference_quote,
        "candidate_f_projection_quote": candidate_quote,
        "candidate_f_direct_actual": {
            "min": min(actual_direct),
            "mean": sum(actual_direct) / len(actual_direct),
            "max": max(actual_direct),
            "cases": len(actual_direct),
        },
        "rejected_dynamic_modes_fail_closed": rejected_fail_closed,
        "omega_zero_kernel": {
            "cases": evaluated + unfunded,
            "evaluated": evaluated,
            "unfunded": unfunded,
            "all_actual_work_within_ceiling": ceiling_covers,
            "max_actual_simulated_steps": max_actual_simulated,
            "max_forecast_ceiling_simulated_steps":
                max_ceiling_simulated,
            "rows": omega_rows,
        },
        "gate": {
            "reference_receipt_unchanged": reference_pass,
            "candidate_f_direct_bound_pass": direct_bound_pass,
            "rejected_modes_fail_closed": rejected_pass,
            "omega_kernel_ceiling_pass": omega_pass,
        },
        "verdict": (
            "CANDIDATE_F_FORECAST_CEILING_PASS"
            if passed else "CANDIDATE_F_FORECAST_CEILING_FAIL"),
        "omega_rerun_authorized": passed,
        "reference_adoption_authorized": False,
    }
    with open(out_path, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    return report


if __name__ == "__main__":
    print(json.dumps(run(sys.argv[1]), indent=1, sort_keys=True))
