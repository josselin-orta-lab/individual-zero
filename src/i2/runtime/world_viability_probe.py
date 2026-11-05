"""Locked tiny exploratory I2 world viability battery; no scientific GO.

Uses only existing I2 WorldBody and paid cognition; no score or policy tuning.
All conditions fixed prospectively in this source; no cherry-picked successes.
"""
from __future__ import annotations

import argparse
import json

from i2.runtime.isolated_prototype import world_demo, WORLD_TICK_LIMIT

# Name, scripted environment, tick horizon, UC, initial energy, resources.
# Explicit negative controls prohibit claims based on no experience.
LOCKED_CASES = (
    ("adverse_full", "adverse", 12, 60, 40, 8),
    ("stable_full", "stable", 12, 60, 40, 8),
    ("neutral_full", "neutral", 12, 60, 40, 8),
    ("reversal_full", "reversal", 12, 60, 40, 8),
    ("adverse_no_food", "adverse", 12, 60, 40, 0),
    ("adverse_no_uc", "adverse", 12, 0, 40, 8),
    ("adverse_low_energy", "adverse", 12, 60, 12, 8),
)
LOCK_ID = "i2-world-viability-exploratory-v1"


def paired_tick_energy_time_course(observed: dict, fixed: dict) -> dict:
    """Audit-only paired energy trajectory, never a general survival estimate.

    A complete integral is meaningful as a *descriptive* toy-world number
    only if both arms are still alive at the same observed physical horizon.
    Any terminal event, unequal duration or misaligned physical tick makes
    the full-window integral unavailable. Never impute postmortem energy.
    """
    a = observed["execution"]["trace"]
    b = fixed["execution"]["trace"]
    prefix = min(len(a), len(b))
    aligned = all(
        a[i]["physical_tick"] == b[i]["physical_tick"] for i in range(prefix)
    )
    if not aligned:
        classification = "MISALIGNED_PHYSICAL_TICKS_NO_COMPARISON"
    elif (not a or len(a) != len(b) or
          any(x["terminal"] for x in a) or
          any(x["terminal"] for x in b)):
        classification = "TERMINAL_OR_UNEQUAL_WINDOW_NO_ENERGY_INTEGRAL"
    else:
        classification = "COMMON_NONTERMINAL_WINDOW_DESCRIPTIVE_ONLY"
    deltas = [
        a[i]["physical_end_energy"] - b[i]["physical_end_energy"]
        for i in range(prefix)
    ] if aligned else []
    integral_allowed = classification == "COMMON_NONTERMINAL_WINDOW_DESCRIPTIVE_ONLY"
    first_separation_tick = next(
        (a[i]["physical_tick"] for i, delta in enumerate(deltas) if delta != 0),
        None,
    )
    return {
        "classification": classification,
        "common_observed_tick_count": prefix if aligned else 0,
        "first_observed_energy_separation_tick": first_separation_tick,
        "complete_common_window_energy_delta_integral": (
            sum(deltas) if integral_allowed else None
        ),
        "observed_world_tick_deltas": [
            {"tick": a[i]["physical_tick"], "energy_delta": delta}
            for i, delta in enumerate(deltas)
        ] if integral_allowed else [],
        "generalized_survival_benefit": "NOT_ESTABLISHED",
        "natural_autonomous_learning": "NOT_ESTABLISHED",
    }


def run_locked_battery() -> dict:
    rows = []
    for name, scenario, ticks, uc, energy, resources in LOCKED_CASES:
        if ticks > WORLD_TICK_LIMIT:
            raise ValueError("case exceeds world horizon")
        result = world_demo(scenario, ticks=ticks, initial_uc=uc,
                            initial_energy=energy, resources=resources)
        observed = result["arms"]["observed_chosen"]
        fixed = result["arms"]["fixed"]
        oe, fe = observed["endpoint"], fixed["endpoint"]
        comparator = result["world_endpoint_contrast"]
        time_course = paired_tick_energy_time_course(observed, fixed)
        rows.append({
            "case": name,
            "environment": scenario,
            "planned_ticks": ticks,
            "initial_uc": uc,
            "initial_energy": energy,
            "initial_resources": resources,
            "first_choice_classification": result["first_choice_contrast"]["classification"],
            "first_choice_tick": next((
                d["physical_ticks_before"]
                for d in observed["decisions"]
                if d["seq"] == result["first_choice_contrast"]["first_divergence_seq"]
            ), None),
            "observational": oe,
            "no_learning": fe,
            "endpoint_classification": comparator["classification"],
            "common_window_energy_delta": comparator["ending_energy_difference"],
            "time_course": time_course,
            "observed_terminal_tick": oe["modeled_death_tick"],
            "fixed_terminal_tick": fe["modeled_death_tick"],
            "limits": "SCRIPTED_DETERMINISTIC_TOY;NO_NATURAL_LEARNING_GO",
        })
    return {
        "lock_id": LOCK_ID,
        "case_count": len(LOCKED_CASES),
        "parameter_lock": [list(c) for c in LOCKED_CASES],
        "rows": rows,
        "generalized_survival_benefit": "NOT_ESTABLISHED",
        "scientific_verdict": "EXPLORATORY_MODEL_SPECIFIC_ONLY",
        "no_policy_tuning": True,
        "m11_authenticated": False,
        "registry_unchanged": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run_locked_battery()
    if args.json:
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    else:
        for row in result["rows"]:
            print(row["case"], row["first_choice_classification"],
                  row["endpoint_classification"], row["common_window_energy_delta"])


if __name__ == "__main__":
    main()
