"""Predeclared, bounded model-only comparison of emergency food re-exposure.

Two hidden regimes x observational control versus the same observational
policy with the opt-in survival priority. Identical world physics, resources,
UC and cadence; independently initialized I2 identities. No motor commands
are imposed by the experimenter and no hidden payoff is published to I2.

Exploratory, not preregistered independent scientific evidence.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile

from i2.runtime.isolated_prototype import (
    EAT, IsolatedI2, SCENARIOS, paired_decision_contrast, world_endpoint,
)

PROTOCOL_ID = "i2-last-resort-emergency-reexposure-exploratory-v1"
CASES = (("hidden_restoration", "restoration"),
         ("persistent_adversity", "adverse"))
TICKS = 16
INITIAL_ENERGY = 40
INITIAL_UC = 60
RESOURCES = 8
FIRST_HIDDEN_RESTORATION_TICK = 7


def run_last_resort_probe() -> dict:
    observations = {}
    with tempfile.TemporaryDirectory(prefix="i2-last-resort-") as root:
        for world_name, scenario in CASES:
            arms = {}
            for enabled, label in ((False, "observational_control"),
                                   (True, "survival_last_resort")):
                individual = IsolatedI2.create(
                    Path(root) / (world_name + "-" + label + ".sqlite"),
                    learning=True, impulses=SCENARIOS[scenario],
                    initial_uc=INITIAL_UC, initial_energy=INITIAL_ENERGY,
                    resources=RESOURCES, last_resort_exploration=enabled,
                )
                execution = individual.run_world(ticks=TICKS)
                decisions = individual.decision_evidence()
                contacts = []
                for row in decisions:
                    if (row["chosen"] == EAT and row["physical_ticks_before"] >=
                            FIRST_HIDDEN_RESTORATION_TICK):
                        later_seen = any(
                            e["seq"] == row["seq"] and e["action"] == EAT
                            for after in decisions if after["seq"] > row["seq"]
                            for e in after["subjective_outcomes_available"]
                        )
                        contacts.append({
                            "tick": row["physical_ticks_before"],
                            "observed_later": later_seen,
                            "chosen_outcome_net": (row["energy_after"] -
                                                   row["before_energy"]),
                        })
                arms[label] = {
                    "endpoint": world_endpoint(execution),
                    "contacts": contacts,
                    "first_person_eat_outcomes_by_decision": [
                        [e["observed_net"] for e in row["subjective_outcomes_available"]
                         if e["action"] == EAT] for row in decisions
                    ],
                    "last_resort_paid_choice_ticks": [
                        row["physical_ticks_before"] for row in decisions
                        if row["last_resort_priority_applied"]
                    ],
                    "decisions": decisions,
                }
            contrast = paired_decision_contrast(
                arms["survival_last_resort"]["decisions"],
                arms["observational_control"]["decisions"],
            )
            observations[world_name] = {
                "first_divergence": contrast,
                "arms": {
                    label: {
                        k: v for k, v in arm.items() if k != "decisions"
                    } for label, arm in arms.items()
                },
            }
    return {
        "protocol_id": PROTOCOL_ID,
        "locked_worlds": [list(c) for c in CASES],
        "planned_ticks": TICKS,
        "initial_energy": INITIAL_ENERGY,
        "initial_uc": INITIAL_UC,
        "initial_resources": RESOURCES,
        "restoration_hidden_until_personal_contact": True,
        "results": observations,
        "limits": "MODEL_ONLY;POST_HOC_EXPLORATORY;NOT_INDEPENDENT_REPLICATION",
        "scientific_verdict": "NOT_ESTABLISHED",
        "m11_authenticated": False,
        "active_generation": "I1",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = run_last_resort_probe()
    if args.json:
        print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    else:
        for world, data in report["results"].items():
            print(world, data["first_divergence"]["classification"])
            for label, arm in data["arms"].items():
                print(" ", label, arm["endpoint"]["ending_energy"],
                      arm["endpoint"]["modeled_death_tick"],
                      arm["last_resort_paid_choice_ticks"])


if __name__ == "__main__":
    main()
