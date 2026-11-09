"""Candidate-F post-contact guard for inherited first-contact expectation.

Software only. The inherited omega prior is intentionally absent from this
module's personal-history path. Once a personally observed carried-food effect
exists, the existing carried-food kernel must remain able to stop after a
harmful branch under Candidate F.
"""
from __future__ import annotations

import json
import sys

from ..modules.body import BodyLaws, CognitiveBudget, CognitiveFundingError, CognitiveWork
from ..modules.carried_food_information import paid_carried_unknown_food_information_value
from ..modules.genome import midpoint
from ..modules.reference_memory_mind import ReferenceBranchMemoryMind

SCHEMA = "i3-omega-post-contact-candidate-f-guard/v1"
BASE = (50., 50., 50., 50., 50.)
SAFE = (0., 30., 0., 0., 0.)
TOXIC = (0., 30., 0., -35., 0.)
MIXED = (
    (("manger", "known-safe"), SAFE),
    (("manger", "known-toxic"), TOXIC),
)
HARMFUL = (
    (("manger", "known-a"), (0., 5., 0., -20., 0.)),
    (("manger", "known-b"), (0., 10., 0., -30., 0.)),
)
GRID = tuple(
    (energy, food, 80., integrity, 80.)
    for energy in (35., 60., 85.)
    for food in (5., 20., 40.)
    for integrity in (20., 50., 80.)
)


def _remember(memory, key, delta):
    after = tuple(a + b for a, b in zip(BASE, delta))
    memory.observe(
        key, BASE, CognitiveWork(),
        CognitiveBudget(after, BodyLaws()))


def make_candidate(rows, seed=211):
    mind = ReferenceBranchMemoryMind(
        midpoint(), seed, simulation_mode="candidate_f")
    mind.projection_accounting = "event_local_quadratic4"
    mind.effects.observe(("attendre",), (-.35, -.2, -.4, .2, 0.))
    mind.effects.observe(("dormir",), (3., -.35, -.4, 0., 4.))
    for key, delta in rows:
        mind.effects.observe(key, delta)
        _remember(mind.branch_memory, key, delta)
    mind._drift = mind.drift()
    return mind


def evaluate(rows, body):
    mind = make_candidate(rows)
    budget = CognitiveBudget(body, BodyLaws())
    try:
        result = paid_carried_unknown_food_information_value(
            mind, mind.branch_memory, "novel", 2, budget)
    except CognitiveFundingError:
        return {
            "status": "UNFUNDED",
            "body": list(body),
            "work": {
                k: getattr(budget.work, k)
                for k in ("cycles", "simulated_steps", "memory_items", "replays")
            },
        }
    return {
        "status": "COMPLETE",
        "body": list(body),
        "information_value": result["information_value"],
        "conditional_choices": [
            {
                "effect_delta": list(row["effect_delta"]),
                "best_choices": list(row["best_choices"]),
            }
            for row in result["conditional_choices"]
        ],
        "work": dict(result["work"]),
        "forecast_work_ceiling": dict(result["forecast_work_ceiling"]),
        "world_access": result["world_access"],
        "motor_command_authorized": result["motor_command_authorized"],
    }


def _summary(rows):
    complete = [row for row in rows if row["status"] == "COMPLETE"]
    return {
        "evaluated": len(rows),
        "complete": len(complete),
        "unfunded": len(rows) - len(complete),
        "positive_information": sum(
            row["information_value"] > 1e-12 for row in complete),
        "branches_with_stop": sum(
            "STOP_AFTER_TRIAL" in branch["best_choices"]
            for row in complete
            for branch in row["conditional_choices"]),
        "branches_with_repeat": sum(
            "REPEAT_ONCE" in branch["best_choices"]
            for row in complete
            for branch in row["conditional_choices"]),
        "all_actual_work_within_ceiling": all(
            all(row["work"][key] <= row["forecast_work_ceiling"][key]
                for key in ("cycles", "simulated_steps", "memory_items", "replays"))
            for row in complete),
    }


def _choice_map(row):
    return {
        tuple(branch["effect_delta"]): tuple(branch["best_choices"])
        for branch in row["conditional_choices"]
    }


def run(out_path):
    mixed_witness = evaluate(MIXED, (80., 5., 80., 80., 80.))
    harmful_witness = evaluate(HARMFUL, (80., 80., 80., 40., 80.))

    mixed_choices = (
        _choice_map(mixed_witness)
        if mixed_witness["status"] == "COMPLETE" else {})
    harmful_choices = (
        _choice_map(harmful_witness)
        if harmful_witness["status"] == "COMPLETE" else {})

    mixed_pass = (
        mixed_witness["status"] == "COMPLETE"
        and mixed_witness["information_value"] > 1e-12
        and "REPEAT_ONCE" in mixed_choices.get(SAFE, ())
        and "STOP_AFTER_TRIAL" in mixed_choices.get(TOXIC, ())
    )
    harmful_pass = (
        harmful_witness["status"] == "COMPLETE"
        and abs(harmful_witness["information_value"]) <= 1e-12
        and harmful_choices
        and all(
            choices == ("STOP_AFTER_TRIAL",)
            for choices in harmful_choices.values())
    )

    mixed_grid = [evaluate(MIXED, body) for body in GRID]
    harmful_grid = [evaluate(HARMFUL, body) for body in GRID]
    mixed_summary = _summary(mixed_grid)
    harmful_summary = _summary(harmful_grid)
    work_pass = (
        mixed_summary["all_actual_work_within_ceiling"]
        and harmful_summary["all_actual_work_within_ceiling"]
    )

    passed = mixed_pass and harmful_pass and work_pass
    report = {
        "schema": SCHEMA,
        "world_access": False,
        "lives": 0,
        "candidate": {
            "simulation_mode": "candidate_f",
            "projection_accounting": "event_local_quadratic4",
        },
        "canonical_mixed_witness": mixed_witness,
        "canonical_harmful_witness": harmful_witness,
        "grid": {
            "states_per_history": len(GRID),
            "mixed": mixed_summary,
            "harmful": harmful_summary,
        },
        "gate": {
            "mixed_safe_repeat_toxic_stop": mixed_pass,
            "uniformly_harmful_stops": harmful_pass,
            "actual_work_within_forecast_ceiling": work_pass,
            "personal_path_reads_omega": False,
        },
        "verdict": (
            "POST_CONTACT_PERSONAL_HISTORY_OVERRIDES_INNATE_EXPECTATION"
            if passed else "POST_CONTACT_GUARD_FAILED"),
        "genome_change_authorized_by_this_report": False,
        "reference_adoption_authorized": False,
    }
    with open(out_path, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    return report


if __name__ == "__main__":
    print(json.dumps(run(sys.argv[1]), indent=1, sort_keys=True))
