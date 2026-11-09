"""Frozen software falsifier for omega, the innate expectation toward the unknown.

Protocol: docs/STAGE1_OMEGA_SOFTWARE_FALSIFIER.md. No World, no life, no study
index. Fixtures are byte-for-byte those of tests/i3/test_water_future_opportunity.py
(the #1101 grid), copied so the laboratory never imports test code.

    python -m i3.lab.stage1_omega_falsifier OUTPUT.json
"""
from __future__ import annotations

import json
import sys

from ..modules.body import BodyLaws, CognitiveBudget, CognitiveFundingError, CognitiveWork
from ..modules.genome import midpoint
from ..modules.mind import Mind
from ..modules.reference_branches import ReferenceBranchMemory
from ..modules.water_future_opportunity import paid_water_one_future_opportunity_value

SCHEMA = "i3-stage1-omega-software-falsifier/v1"
BASE = (50., 50., 50., 50., 50.)
EXPLORE = (("se_deplacer",),)
STOP_AFTER_PREFIX = (("stop-after-prefix", ()),)
OMEGAS = (-1.0, -0.5, 0.0, 0.25, 0.5, 1.0)
REFERENCE_1101 = {"selected_epistemic": 0, "declined": 28,
                  "max_information_value": 0.000592902270,
                  "best_trial_advantage": 0.0695239461}


def _record(memory, key, delta):
    after = tuple(a + b for a, b in zip(BASE, delta))
    memory.observe(key, BASE, CognitiveWork(), CognitiveBudget(after, BodyLaws()))


def realistic_memory():
    memory = ReferenceBranchMemory()
    for key, delta in (
        (("se_deplacer", None), (-2., -.2, -.4, 0., 0.)),
        (("attendre", None), (-.35, -.2, -.4, .2, 0.)),
        (("dormir", None), (3., -.35, -.4, 0., 4.)),
    ):
        _record(memory, key, delta)
    return memory


def make_mind():
    mind = Mind(midpoint(), 97)
    mind.map = {}
    mind.effects.observe(("se_deplacer",), (-2., -.2, -.4, 0., 0.))
    mind.effects.observe(("attendre",), (-.35, -.2, -.4, .2, 0.))
    mind.effects.observe(("dormir",), (3., -.35, -.4, 0., 4.))
    mind._drift = mind.drift()
    return mind


def grid():
    for channel in range(5):
        for level in (20., 30., 40., 50.):
            body = [80., 80., 80., 80., 80.]
            body[channel] = level
            for horizon in (4, 6, 8, 12):
                yield channel, level, tuple(body), horizon


def evaluate(omega):
    rows = []
    for channel, level, body, horizon in grid():
        try:
            r = paid_water_one_future_opportunity_value(
                make_mind(), realistic_memory(), EXPLORE, STOP_AFTER_PREFIX,
                horizon, CognitiveBudget(body, BodyLaws()), omega=omega)
        except CognitiveFundingError:
            rows.append({"channel": channel, "level": level, "horizon": horizon,
                         "status": "UNFUNDED"})
            continue
        rows.append({
            "channel": channel, "level": level, "horizon": horizon,
            "status": "EVALUATED",
            "choices": list(r["target_node_best_choices"]),
            "trial_information_value": r["trial_information_value"],
            "trial_advantage": r["trial_advantage"],
            "water_revelation_advantage": r["water_revelation_advantage"],
            "work": dict(r["work"]),
        })
    done = [x for x in rows if x["status"] == "EVALUATED"]
    return rows, {
        "evaluated": len(done),
        "trial_selected": sum("TRIAL" in x["choices"] for x in done),
        "selected_epistemic": sum(
            "TRIAL" in x["choices"] and x["trial_information_value"] > 1e-12 for x in done),
        "declined": sum(x["choices"] == ["DECLINE_TRIAL"] for x in done),
        "positive_revelation": sum(x["water_revelation_advantage"] > 1e-12 for x in done),
        "max_revelation_advantage": max(x["water_revelation_advantage"] for x in done),
        "max_information_value": max(x["trial_information_value"] for x in done),
        "best_trial_advantage": max(x["trial_advantage"] for x in done),
        "worst_trial_advantage": min(x["trial_advantage"] for x in done),
    }


def run(out_path):
    arms = {omega: evaluate(omega) for omega in OMEGAS}
    zero_rows = arms[0.0][0]
    zero = arms[0.0][1]
    r0 = (zero["selected_epistemic"] == REFERENCE_1101["selected_epistemic"]
          and zero["declined"] == REFERENCE_1101["declined"]
          and abs(zero["max_information_value"] - REFERENCE_1101["max_information_value"]) < 1e-9
          and abs(zero["best_trial_advantage"] - REFERENCE_1101["best_trial_advantage"]) < 1e-9)
    r1 = all(
        [x.get("work") for x in rows] == [x.get("work") for x in zero_rows]
        for rows, _ in arms.values())
    zero_positive = {(x["channel"], x["level"], x["horizon"]) for x in zero_rows
                     if x["status"] == "EVALUATED" and x["water_revelation_advantage"] > 1e-12}
    new_positive = {
        str(omega): sum(1 for x in rows if x["status"] == "EVALUATED"
                        and x["water_revelation_advantage"] > 1e-12
                        and (x["channel"], x["level"], x["horizon"]) not in zero_positive)
        for omega, (rows, _) in arms.items() if omega > 0}
    order = sorted(OMEGAS)
    r2 = all(arms[a][1]["trial_selected"] <= arms[b][1]["trial_selected"] and
             arms[a][1]["positive_revelation"] <= arms[b][1]["positive_revelation"]
             for a, b in zip(order, order[1:]))
    report = {
        "schema": SCHEMA, "protocol": "STAGE1_OMEGA_SOFTWARE_FALSIFIER.md",
        "world_access": False, "lives": 0,
        "summary": {str(o): s for o, (_, s) in arms.items()},
        "states_newly_positive_vs_omega0": new_positive,
        "rules": {
            "R0_identity_with_1101": r0,
            "R1_identical_paid_work_across_omega": r1,
            "R2_direction_monotone": r2,
            "R3_capacity_some_positive_omega_adds_positive_revelation":
                any(v > 0 for v in new_positive.values()),
        },
        "rows": {str(o): rows for o, (rows, _) in arms.items()},
    }
    report["verdict"] = (
        "DEFECT_STOP" if not (r0 and r1) else
        "CAPACITY_SHOWN" if report["rules"]["R3_capacity_some_positive_omega_adds_positive_revelation"]
        else "NO_CAPACITY_THROUGH_THIS_KERNEL")
    with open(out_path, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    return report


if __name__ == "__main__":
    rep = run(sys.argv[1])
    print("verdict", rep["verdict"], rep["rules"])
    for o, s in rep["summary"].items():
        print("omega", o, s)
    print("newly positive vs omega 0:", rep["states_newly_positive_vs_omega0"])
