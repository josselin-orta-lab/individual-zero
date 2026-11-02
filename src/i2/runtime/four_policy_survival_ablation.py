"""Exploratory four-policy I2 survival comparison on identical world schedules.

Each arm uses a fresh, independent SQLite owner. No hidden food payoff
enters the subject; the researcher sees it only in the audited readout.
These single deterministic traces are NOT independent statistical evidence.
"""
from __future__ import annotations

import json
from pathlib import Path
import tempfile

from i2.runtime.isolated_prototype import (
    IsolatedI2, SCENARIOS, EAT, world_endpoint,
)

POLICIES = (
    ("observational", False, False),
    ("last_resort", True, False),
    ("deadline", False, True),
    ("combined", True, True),
)
ENVIRONMENTS = ("stable", "adverse", "restoration")
TICKS = 16
INITIAL_ENERGY = 40
INITIAL_UC = 60



def describe_pair(control: dict, intervention: dict) -> dict:
    """First observed action divergence, not an inferred counterfactual."""
    a, b = control["chosen_actions"], intervention["chosen_actions"]
    at, bt = control["chosen_at_ticks"], intervention["chosen_at_ticks"]
    first = next(
        (i for i in range(min(len(a), len(b)))
         if a[i] != b[i] or at[i] != bt[i]), None
    )
    if first is None and len(a) != len(b):
        classification = "UNEQUAL_COGNITIVE_EXPOSURE"
    elif first is None:
        classification = "NO_OBSERVED_ACTION_DIVERGENCE"
    else:
        classification = "FIRST_OBSERVED_POLICY_DIVERGENCE"
    left = control["endpoint"]
    right = intervention["endpoint"]
    common_nonterminal_window = (
        left["ending_physical_tick"] == right["ending_physical_tick"]
        and not left["modeled_terminal_observed"]
        and not right["modeled_terminal_observed"]
    )
    return {
        "classification": classification,
        "first_divergent_decision_index": None if first is None else first + 1,
        "control_tick": None if first is None else at[first],
        "intervention_tick": None if first is None else bt[first],
        "control_action": None if first is None else a[first],
        "intervention_action": None if first is None else b[first],
        "control_death_tick": left["modeled_death_tick"],
        "intervention_death_tick": right["modeled_death_tick"],
        "control_right_censored": left["right_censored"],
        "intervention_right_censored": right["right_censored"],
        "energy_difference_only_common_nonterminal_window": (
            right["ending_energy"] - left["ending_energy"]
            if common_nonterminal_window else None
        ),
        "no_causal_survival_attribution": True,
    }


def run_four_policy_ablation(*, initial_energy: int = INITIAL_ENERGY) -> dict:
    if type(initial_energy) is not int or not 1 <= initial_energy <= 100:
        raise ValueError("invalid bounded experimental energy")
    outcomes = {}
    with tempfile.TemporaryDirectory(prefix="i2-four-policy-") as root:
        for env in ENVIRONMENTS:
            variants = {}
            for name, last_resort, deadline in POLICIES:
                subject = IsolatedI2.create(
                    Path(root) / f"{env}-{name}.sqlite",
                    learning=True, impulses=SCENARIOS[env],
                    initial_energy=initial_energy, initial_uc=INITIAL_UC,
                    last_resort_exploration=last_resort,
                    deadline_aware=deadline,
                )
                execution = subject.run_world(ticks=TICKS)
                decisions = subject.decision_evidence()
                endpoint = world_endpoint(execution)
                variants[name] = {
                    "endpoint": endpoint,
                    "chosen_actions": [d["chosen"] for d in decisions],
                    "chosen_at_ticks": [d["physical_ticks_before"] for d in decisions],
                    "food_contact_ticks": [
                        d["physical_ticks_before"] for d in decisions
                        if d["chosen"] == EAT
                    ],
                    "deadline_suppressions": sum(
                        bool(d["deadline_infeasible_collect_suppressed"])
                        for d in decisions),
                    "last_resort_raises": sum(
                        bool(d["last_resort_priority_applied"])
                        for d in decisions),
                    "uc_spent": endpoint["actual_uc_spent"],
                }
            outcomes[env] = {
                "arms": variants,
                "contrasts_vs_observational": {
                    name: describe_pair(variants["observational"], variants[name])
                    for name in ("last_resort", "deadline", "combined")
                },
            }
    return {
        "protocol": "i2-four-policy-survival-ablation-exploratory-v1",
        "environments": list(ENVIRONMENTS),
        "policies": [name for name, *_ in POLICIES],
        "initial_energy": initial_energy,
        "initial_uc": INITIAL_UC,
        "physical_tick_horizon": TICKS,
        "results": outcomes,
        "conclusion": "EXPLORATORY_MODEL_SPECIFIC_ONLY",
        "general_survival_benefit": "NOT_ESTABLISHED",
        "natural_learning": "NOT_ESTABLISHED",
        "m11_authenticated": False,
    }


def main() -> None:
    print(json.dumps(run_four_policy_ablation(), sort_keys=True,
                     separators=(",", ":")))


if __name__ == "__main__":
    main()
