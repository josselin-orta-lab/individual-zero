"""Exploratory G1-LAB readout: all five immutable, non-living regimes.

This is a *reporting regression*, not preregistered living science, proof
of improved learning, or extra post-hoc tuning. It runs the actual I2
G1-LAB source, never a parallel hand-reimplemented behavior simulator.
The baseline is independently initialized, equally funded, not a matched
life or a real M11 witness. Initial physiological energy is 24 and each
arm has 60 synthetic UC. Absent actions, vetoes, terminal truncation and
actual UC spending must be reported, including adverse/null results.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from i2.lab.integrated_loop import (  # noqa: E402
    COLLECT, EAT, DRINK, REGIMES, run_pair,
)

ABBR = {COLLECT: "C", EAT: "E", DRINK: "D", None: "_"}
SCHEMA = "i2-g1lab-exploratory-comparison-v1"
START_ENERGY = 24
START_UC = 60


def compact_arm(raw: dict) -> dict:
    """Keep exact realized actions/charges, no invented matched outcomes."""
    rows = raw["steps"]
    actual = [row for row in rows if "chosen" in row]
    refusals = [row["refusal"] for row in rows if "refusal" in row]
    if len(actual) != len(raw["actions"]):
        raise AssertionError("action trace and recorded captures disagree")
    if any(row["motor_authority"] != "NONE" for row in actual):
        raise AssertionError("live motor authority appeared in G1-LAB")
    cost = sum(row["uc_spent"] for row in actual)
    if cost != raw["spent_synthetic_uc"]:
        raise AssertionError("actual UC accounting mismatch")
    net = sum(row["result_net"] for row in actual)
    if net != raw["net_energy_change"]:
        raise AssertionError("physiological net accounting mismatch")
    terminal = bool(raw["terminal"])
    if terminal and (not actual or actual[-1]["energy"] != 0):
        raise AssertionError("a simulated death requires zero model energy")
    if len(actual) > 8 or any(row["uc_spent"] < 1 for row in actual):
        raise AssertionError("outside bounded, paid G1-LAB")
    if len(actual) and actual[0]["visible"] and EAT in actual[0]["visible"]:
        raise AssertionError("food was offered before collecting")
    return {
        "actions": "".join(ABBR[row["chosen"]] for row in actual),
        "net_energy": net,
        "last_energy": actual[-1]["energy"] if actual else START_ENERGY,
        "steps": len(actual),
        "terminal": terminal,
        "refusals": refusals,
        "spent_uc": cost,
        "remaining_uc": START_UC - cost,
        "abstentions": sum(row["chosen"] is None for row in actual),
        "vetoes": sum(row["control_status"] == "VETOED" for row in actual),
        "energy": [row["energy"] for row in actual],
        "step_net": [row["result_net"] for row in actual],
        "step_uc": [row["uc_spent"] for row in actual],
        "offered": [
            "".join(ABBR[a] for a in row["visible"]) for row in actual
        ],
    }


def five_scenario_comparison() -> dict:
    """Execute *only* frozen ADR-0005 regimes with no scoring changes."""
    results: dict[str, dict] = {}
    for name, deltas in REGIMES.items():
        raw = run_pair(deltas, initial_energy=START_ENERGY, initial_uc=START_UC)
        if (raw["status"] != "G1_LAB_ONLY_NOT_BORN" or
                raw["motor_authority"] != "NONE" or
                raw["m11_authenticated"] is not False or
                raw["same_initial_energy"] != START_ENERGY or
                raw["same_initial_uc"] != START_UC or
                set(raw["arms"]) != {"observational", "fixed"}):
            raise AssertionError("the experiment bypassed inert comparable arms")
        fixed = compact_arm(raw["arms"]["fixed"])
        learning = compact_arm(raw["arms"]["observational"])
        results[name] = {
            "fixed": fixed,
            "observational": learning,
            "net_difference": learning["net_energy"] - fixed["net_energy"],
            "uc_spent_difference": learning["spent_uc"] - fixed["spent_uc"],
            "first_action_divergence": next((
                i for i, (left, right) in enumerate(
                    zip(fixed["actions"], learning["actions"])
                ) if left != right
            ), None),
            "different_lengths": fixed["steps"] != learning["steps"],
        }
    return {
        "schema": SCHEMA, "gates": {
            "G1_LAB": "NON_LIVING_EXPLORATORY",
            "G1_LIVE": "REVIEW_REQUIRED",
            "M11": "NOT_ESTABLISHED",
            "I2_BIRTH": "FORBIDDEN",
        },
        "fixed_priors": {"collect": 3, "eat": 4, "drink": 1},
        "chosen_score_offset": 5,
        "initial_energy": START_ENERGY,
        "initial_synthetic_uc": START_UC,
        "n_independent_lives_per_arm": 1,
        "regimes": results,
    }


class G1LabFiveRegimeEvidence(unittest.TestCase):
    def test_report_complete_five_regimes_with_null_and_negative(self):
        report = five_scenario_comparison()
        self.assertEqual(tuple(report["regimes"]), tuple(REGIMES))
        self.assertTrue(all(
            len(row["fixed"]["actions"]) <= len(REGIMES[name]) and
            len(row["observational"]["actions"]) <= len(REGIMES[name])
            for name, row in report["regimes"].items()
        ))
        stable = report["regimes"]["stable"]
        # A collect/eat pattern also exists in the no-learning arm, so it
        # must never be counted as scientific proof of acquired learning.
        self.assertEqual(stable["fixed"]["actions"][:2], "CE")
        self.assertEqual(stable["observational"]["actions"][:2], "CE")
        self.assertLess(report["regimes"]["adverse"]["fixed"]["net_energy"], 0)
        print("I2_G1LAB_FIVE_SCENARIOS " +
              json.dumps(report, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    unittest.main()
