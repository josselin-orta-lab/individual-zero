"""Blind environment restoration: bounded I2 information-limit falsifier.

The world changes food payoff from harmful to beneficial at a PREDECLARED
physical tick. No visible cue, future state, policy tuning, forced action or
exploration bonus is supplied to the individual. Compare the same existing
learned and fixed-prior policies against a persistently adverse control.

A failure to re-sample is an informative NEGATIVE result: when all personally
observed histories remain identical, hidden restoration cannot be inferred.
This is source-pinned exploratory toy evidence, not natural learning or M11.
"""
from __future__ import annotations

import argparse
import json

from i2.runtime.isolated_prototype import EAT, SCENARIOS, world_demo

PROTOCOL_ID = "i2-blind-restoration-identifiability-v1"
CHANGE_START_TICK = 7  # external physical-tick phase, not cognitive sequence
TICK_HORIZON = 16
INITIAL_UC = 60
INITIAL_ENERGY = 40
INITIAL_RESOURCES = 8
LOCKED_ENVIRONMENTS = (
    ("hidden_restoration", "restoration"),
    ("persistent_adversity", "adverse"),
)

# These fields are the agent's personally available state, chosen outcomes,
# paid valuation and decision. Exclude audit-only exogenous_food_phase and
# identity-specific cryptographic refs from cross-world comparability.
SUBJECT_VISIBLE_FIELDS = (
    "physical_ticks_before", "before_energy", "before_inventory",
    "before_resources", "visible", "subjective_outcomes_available",
    "outcomes_used_by_valuation", "candidate_scores", "chosen",
    "uc_before", "uc_spent", "uc_remaining", "energy_after",
    "inventory_after", "resources_after", "terminal",
)


def _subjective_history(decisions: tuple[dict, ...]) -> tuple[tuple, ...]:
    return tuple(
        tuple(json.dumps(d[k], sort_keys=True, separators=(",", ":"))
              for k in SUBJECT_VISIBLE_FIELDS)
        for d in decisions
    )


def _food_contact(decisions: tuple[dict, ...]) -> dict:
    """One chosen EAT is an exposure, not automatically a later observation."""
    contacts = []
    for d in decisions:
        if d["chosen"] != EAT or d["physical_ticks_before"] < CHANGE_START_TICK:
            continue
        net = d["energy_after"] - d["before_energy"]
        later = any(
            e["seq"] == d["seq"] and e["action"] == EAT and
            e["observed_net"] == net
            for subsequent in decisions if subsequent["seq"] > d["seq"]
            for e in subsequent["subjective_outcomes_available"]
        )
        contacts.append({
            "action_sequence": d["seq"],
            "world_tick": d["physical_ticks_before"],
            "net_energy": net,
            "personally_available_later": later,
        })
    return {
        "post_change_food_contacts": contacts,
        "first_post_change_food_contact_tick": (
            contacts[0]["world_tick"] if contacts else None),
        "first_positive_food_contact_tick": next(
            (c["world_tick"] for c in contacts if c["net_energy"] > 0), None),
        "positive_contact_available_in_later_capture": any(
            c["net_energy"] > 0 and c["personally_available_later"]
            for c in contacts
        ),
    }


def _arm_readout(arm: dict) -> dict:
    decisions = arm["decisions"]
    endpoint = arm["endpoint"]
    return {
        "choices": [
            {
                "sequence": d["seq"], "tick": d["physical_ticks_before"],
                "action": d["chosen"], "available": list(d["visible"]),
                "previously_experienced_eat_results": [
                    e["observed_net"]
                    for e in d["subjective_outcomes_available"]
                    if e["action"] == EAT
                ],
                "eat_score": d["candidate_scores"].get(EAT),
                "energy_after": d["energy_after"],
            }
            for d in decisions
        ],
        "ending_energy": endpoint["ending_energy"],
        "death_tick": endpoint["modeled_death_tick"],
        "censored": endpoint["right_censored"],
        "paid_decisions": endpoint["paid_decisions"],
        "actual_uc_spent": endpoint["actual_uc_spent"],
        **_food_contact(decisions),
    }


def run_blind_restoration_probe() -> dict:
    """Two locked worlds x two unchanged I2 policies, no exploratory tuning."""
    if (SCENARIOS["restoration"][:3] != SCENARIOS["adverse"][:3] or
            SCENARIOS["restoration"][3:] != (6,) * 5 or
            SCENARIOS["adverse"][3:] != (-8,) * 5):
        raise ValueError("hidden-change lock was modified")
    runs = {}
    for name, scenario in LOCKED_ENVIRONMENTS:
        world = world_demo(
            scenario, ticks=TICK_HORIZON, initial_uc=INITIAL_UC,
            initial_energy=INITIAL_ENERGY, resources=INITIAL_RESOURCES)
        runs[name] = {
            "observational": _arm_readout(world["arms"]["observed_chosen"]),
            "no_learning": _arm_readout(world["arms"]["fixed"]),
            "first_choice_contrast": world["first_choice_contrast"]["classification"],
        }
        # Keep private comparison projections for the immediate audit only.
        # They are not inputs to the world or either individual's policy.
        runs[name]["_subjective"] = {
            label: _subjective_history(world["arms"][source]["decisions"])
            for label, source in (
                ("observational", "observed_chosen"),
                ("no_learning", "fixed"),
            )
        }
    restored, persistent = (
        runs["hidden_restoration"], runs["persistent_adversity"])
    same_learning_history = (
        restored["_subjective"]["observational"] ==
        persistent["_subjective"]["observational"]
    )
    # Require a real, personally chosen postchange food exposure before
    # asserting that any later policy reaction could identify the change.
    learned_exposed = bool(restored["observational"]["post_change_food_contacts"])
    classification = (
        "HIDDEN_CHANGE_UNIDENTIFIABLE_WITHOUT_REEXPOSURE"
        if same_learning_history and not learned_exposed
        else "CONTACT_OCCURRED_ANALYZE_AFTER_EXPERIENCE"
        if learned_exposed else "DIFFERENT_HISTORIES_CAUSE_UNDETERMINED"
    )
    for case in runs.values():
        del case["_subjective"]
    return {
        "protocol_id": PROTOCOL_ID,
        "locked_worlds": [list(case) for case in LOCKED_ENVIRONMENTS],
        "world_change_first_tick": CHANGE_START_TICK,
        "tick_horizon": TICK_HORIZON,
        "initial_uc": INITIAL_UC,
        "initial_energy": INITIAL_ENERGY,
        "initial_resources": INITIAL_RESOURCES,
        "same_observational_subject_history_across_hidden_worlds":
            same_learning_history,
        "interpretation": classification,
        "runs": runs,
        "scientific_verdict": "MODEL_SPECIFIC_NEGATIVE_OR_INCONCLUSIVE",
        "natural_learning": "NOT_ESTABLISHED",
        "authenticated_m11": False,
        "active_engine": False,
        "no_exploration_bonus_or_oracle": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run_blind_restoration_probe()
    if args.json:
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    else:
        print(result["interpretation"])
        for world, report in result["runs"].items():
            for arm in ("observational", "no_learning"):
                row = report[arm]
                print(world, arm, row["ending_energy"],
                      row["death_tick"],
                      row["first_post_change_food_contact_tick"])


if __name__ == "__main__":
    main()
