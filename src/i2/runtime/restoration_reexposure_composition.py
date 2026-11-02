"""Source-locked comparison of paid food re-exposure after hidden restoration.

Identical existing 40-energy restored/adverse worlds, three fresh policy
owners. The first adverse EAT must be personally experienced before any
later 'restoration' outcome is available. No controller-forced actions.
"""
from __future__ import annotations
import json
from pathlib import Path
import tempfile
from i2.runtime.isolated_prototype import (
    IsolatedI2, SCENARIOS, EAT, paired_decision_contrast, world_endpoint,
)

POLICIES = (("observational", False, False),
            ("last_resort", True, False),
            ("combined", True, True))
WORLDS = (("hidden_restoration", "restoration"),
          ("persistent_adversity", "adverse"))
CHANGE_TICK = 7
HORIZON = 16

def run_restoration_reexposure() -> dict:
    worlds = {}
    with tempfile.TemporaryDirectory(prefix="i2-restoration-reexposure-") as root:
        for label, scenario in WORLDS:
            arms = {}
            for name, reflex, deadline in POLICIES:
                life = IsolatedI2.create(
                    Path(root) / f"{label}-{name}.sqlite",
                    learning=True, impulses=SCENARIOS[scenario],
                    initial_energy=40, initial_uc=60, resources=8,
                    last_resort_exploration=reflex, deadline_aware=deadline,
                )
                execution = life.run_world(ticks=HORIZON)
                decisions = life.decision_evidence()
                contacts = []
                for row in decisions:
                    if row["chosen"] != EAT or row["physical_ticks_before"] < CHANGE_TICK:
                        continue
                    contacts.append({
                        "tick": row["physical_ticks_before"],
                        "net": row["energy_after"] - row["before_energy"],
                        "prior_personal_eat_nets": [
                            x["observed_net"] for x in row["subjective_outcomes_available"]
                            if x["action"] == EAT
                        ],
                        "emergency_priority_applied": row["last_resort_priority_applied"],
                        "later_personally_observed": any(
                            x["seq"] == row["seq"] and x["action"] == EAT
                            for later in decisions if later["seq"] > row["seq"]
                            for x in later["subjective_outcomes_available"]
                        ),
                    })
                arms[name] = {
                    "endpoint": world_endpoint(execution),
                    "contacts": contacts,
                    "decisions": decisions,
                    "paid_uc": life.audit()["actual_uc_spent"],
                }
            worlds[label] = {
                "arms": {
                    key: {field: value for field, value in arm.items()
                          if field != "decisions"}
                    for key, arm in arms.items()
                },
                "first_divergence_from_observational": {
                    key: paired_decision_contrast(
                        arms[key]["decisions"], arms["observational"]["decisions"])
                    for key in ("last_resort", "combined")
                },
            }
    return {
        "protocol": "i2-personal-aversion-hidden-restoration-composition-v1",
        "worlds": worlds,
        "hidden_change_first_tick": CHANGE_TICK,
        "initial_energy": 40,
        "tick_horizon": HORIZON,
        "interpretation": "EXPLORATORY_MODEL_SPECIFIC_ONLY",
        "independent_scientific_replication": False,
        "natural_learning": "NOT_ESTABLISHED",
        "m11_authenticated": False,
    }

if __name__ == "__main__":
    print(json.dumps(run_restoration_reexposure(), sort_keys=True, separators=(",", ":")))
