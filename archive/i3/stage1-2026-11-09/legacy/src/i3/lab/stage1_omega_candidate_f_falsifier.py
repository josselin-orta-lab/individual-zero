"""Frozen omega software falsifier rerun with integrated Candidate F.

Protocol: docs/STAGE1_OMEGA_CANDIDATE_F_RERUN.md.
No World, life or study index.
"""
from __future__ import annotations

import json
import sys

from ..modules.body import BodyLaws, CognitiveBudget, CognitiveFundingError
from ..modules.water_future_opportunity import (
    paid_water_one_future_opportunity_value)
from . import stage1_omega_falsifier as W

SCHEMA = "i3-stage1-omega-candidate-f-falsifier/v1"


def make_candidate_f_mind():
    mind = W.make_mind()
    mind.simulation_mode = "candidate_f"
    mind.projection_accounting = "event_local_quadratic4"
    return mind


def evaluate(omega):
    rows = []
    for channel, level, body, horizon in W.grid():
        try:
            result = paid_water_one_future_opportunity_value(
                make_candidate_f_mind(),
                W.realistic_memory(),
                W.EXPLORE,
                W.STOP_AFTER_PREFIX,
                horizon,
                CognitiveBudget(body, BodyLaws()),
                omega=omega)
        except CognitiveFundingError:
            rows.append({
                "channel": channel,
                "level": level,
                "horizon": horizon,
                "status": "UNFUNDED",
            })
            continue

        rows.append({
            "channel": channel,
            "level": level,
            "horizon": horizon,
            "status": "EVALUATED",
            "choices": list(result["target_node_best_choices"]),
            "trial_information_value":
                result["trial_information_value"],
            "trial_advantage": result["trial_advantage"],
            "water_revelation_advantage":
                result["water_revelation_advantage"],
            "work": dict(result["work"]),
            "forecast_work_ceiling":
                dict(result["forecast_work_ceiling"]),
        })

    done = [row for row in rows if row["status"] == "EVALUATED"]
    if not done:
        summary = {
            "evaluated": 0,
            "unfunded": len(rows),
            "trial_selected": 0,
            "selected_epistemic": 0,
            "declined": 0,
            "positive_revelation": 0,
            "max_revelation_advantage": None,
            "max_information_value": None,
            "best_trial_advantage": None,
            "worst_trial_advantage": None,
        }
    else:
        summary = {
            "evaluated": len(done),
            "unfunded": len(rows) - len(done),
            "trial_selected": sum(
                "TRIAL" in row["choices"] for row in done),
            "selected_epistemic": sum(
                "TRIAL" in row["choices"]
                and row["trial_information_value"] > 1e-12
                for row in done),
            "declined": sum(
                row["choices"] == ["DECLINE_TRIAL"]
                for row in done),
            "positive_revelation": sum(
                row["water_revelation_advantage"] > 1e-12
                for row in done),
            "max_revelation_advantage": max(
                row["water_revelation_advantage"]
                for row in done),
            "max_information_value": max(
                row["trial_information_value"]
                for row in done),
            "best_trial_advantage": max(
                row["trial_advantage"]
                for row in done),
            "worst_trial_advantage": min(
                row["trial_advantage"]
                for row in done),
        }
    return rows, summary


def run(out_path):
    arms = {omega: evaluate(omega) for omega in W.OMEGAS}

    r0f = all(
        summary["evaluated"] == 80
        and summary["unfunded"] == 0
        for _rows, summary in arms.values())

    ordered_rows = {
        omega: rows for omega, (rows, _summary) in arms.items()
    }
    zero_rows = ordered_rows[0.0]

    common_ceiling = True
    work_within_ceiling = True
    max_actual_simulated_range = 0
    for index in range(len(zero_rows)):
        ceilings = []
        actual_simulated = []
        for omega in W.OMEGAS:
            row = ordered_rows[omega][index]
            if row["status"] != "EVALUATED":
                common_ceiling = False
                work_within_ceiling = False
                continue
            ceiling = row["forecast_work_ceiling"]
            work = row["work"]
            ceilings.append(ceiling)
            actual_simulated.append(work["simulated_steps"])
            if not all(
                    work[key] <= ceiling[key]
                    for key in (
                        "cycles", "simulated_steps",
                        "memory_items", "replays")):
                work_within_ceiling = False
        if ceilings and any(
                ceiling != ceilings[0] for ceiling in ceilings[1:]):
            common_ceiling = False
        if actual_simulated:
            max_actual_simulated_range = max(
                max_actual_simulated_range,
                max(actual_simulated) - min(actual_simulated))

    r1f = common_ceiling and work_within_ceiling

    order = sorted(W.OMEGAS)
    r2 = all(
        arms[a][1]["trial_selected"]
            <= arms[b][1]["trial_selected"]
        and arms[a][1]["positive_revelation"]
            <= arms[b][1]["positive_revelation"]
        for a, b in zip(order, order[1:]))

    zero_positive = {
        (row["channel"], row["level"], row["horizon"])
        for row in zero_rows
        if row["status"] == "EVALUATED"
        and row["water_revelation_advantage"] > 1e-12
    }
    newly_positive = {
        str(omega): sum(
            1 for row in ordered_rows[omega]
            if row["status"] == "EVALUATED"
            and row["water_revelation_advantage"] > 1e-12
            and (row["channel"], row["level"], row["horizon"])
                not in zero_positive)
        for omega in W.OMEGAS if omega > 0
    }
    r3 = any(count > 0 for count in newly_positive.values())

    if not (r0f and r1f):
        verdict = "DEFECT_STOP"
    elif r3:
        verdict = "CAPACITY_SHOWN_WITH_CANDIDATE_F"
    else:
        verdict = "NO_CAPACITY_THROUGH_CANDIDATE_F"

    report = {
        "schema": SCHEMA,
        "protocol": "STAGE1_OMEGA_CANDIDATE_F_RERUN.md",
        "world_access": False,
        "lives": 0,
        "candidate": {
            "simulation_mode": "candidate_f",
            "projection_accounting":
                "event_local_quadratic4",
        },
        "summary": {
            str(omega): summary
            for omega, (_rows, summary) in arms.items()
        },
        "states_newly_positive_vs_omega0": newly_positive,
        "cost_diagnostics": {
            "common_forecast_ceiling_identical_across_omega":
                common_ceiling,
            "all_actual_work_within_ceiling":
                work_within_ceiling,
            "max_statewise_actual_simulated_steps_range_across_omega":
                max_actual_simulated_range,
        },
        "rules": {
            "R0F_all_80_states_evaluated_each_arm": r0f,
            "R1F_common_ceiling_and_actual_work_covered": r1f,
            "R2_direction_monotone": r2,
            "R3_capacity_some_positive_omega_adds_positive_revelation":
                r3,
        },
        "verdict": verdict,
        "rows": {
            str(omega): rows
            for omega, (rows, _summary) in arms.items()
        },
        "reference_adoption_authorized": False,
        "survival_claim_authorized": False,
    }
    with open(out_path, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    return report


if __name__ == "__main__":
    report = run(sys.argv[1])
    print(json.dumps({
        "summary": report["summary"],
        "newly_positive":
            report["states_newly_positive_vs_omega0"],
        "cost": report["cost_diagnostics"],
        "rules": report["rules"],
        "verdict": report["verdict"],
    }, indent=1, sort_keys=True))
