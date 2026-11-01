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


def run_four_policy_ablation() -> dict:
    outcomes = {}
    with tempfile.TemporaryDirectory(prefix="i2-four-policy-") as root:
        for env in ENVIRONMENTS:
            variants = {}
            for name, last_resort, deadline in POLICIES:
                subject = IsolatedI2.create(
                    Path(root) / f"{env}-{name}.sqlite",
                    learning=True, impulses=SCENARIOS[env],
                    initial_energy=INITIAL_ENERGY, initial_uc=INITIAL_UC,
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
            outcomes[env] = variants
    return {
        "protocol": "i2-four-policy-survival-ablation-exploratory-v1",
        "environments": list(ENVIRONMENTS),
        "policies": [name for name, *_ in POLICIES],
        "initial_energy": INITIAL_ENERGY,
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
