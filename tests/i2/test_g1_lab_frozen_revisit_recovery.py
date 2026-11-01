"""G1-LAB preregistered-parameter, exploratory recovery test, NOT living I2.

Protocol freeze: issue #662 comment 6559888186 at main 175a78f877b2a0085d20c980f03968b2dbd58fec.
All cases use the existing paid G1-LAB and old G2 revisit_after=2,
revisit_bonus=9. No parameter search, no newly supplied unchosen result.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from i2.lab.integrated_loop import (  # noqa: E402
    EAT, IntegratedLab, REGIMES, run_pair, LabRefusal,
)

INITIAL_ENERGY = 24
INITIAL_UC = 60
ARM_NAMES = ("fixed", "observational", "revisit")


def frozen_revisit_report() -> dict:
    result = {}
    for name, regime in REGIMES.items():
        output = run_pair(regime, initial_energy=INITIAL_ENERGY,
                          initial_uc=INITIAL_UC, include_revisit=True)
        if (output["status"] != "G1_LAB_ONLY_NOT_BORN" or
                output["m11_authenticated"] is not False or
                output["motor_authority"] != "NONE" or
                set(output["arms"]) != set(ARM_NAMES)):
            raise AssertionError("G1-LIVE bypass or missing comparison arm")
        arms = {}
        for label in ARM_NAMES:
            data = output["arms"][label]
            steps = [r for r in data["steps"] if "chosen" in r]
            if (len(steps) != len(data["actions"]) or
                    sum(s["uc_spent"] for s in steps) != data["spent_synthetic_uc"] or
                    any(s["motor_authority"] != "NONE" for s in steps)):
                raise AssertionError("invented events or unbilled lab choice")
            arms[label] = {
                "actions": ["C" if s["chosen"] and ":collect:" in s["chosen"]
                            else "E" if s["chosen"] == EAT
                            else "D" if s["chosen"] and ":drink:" in s["chosen"]
                            else "_" for s in steps],
                "energy": [s["energy"] for s in steps],
                "net": [s["result_net"] for s in steps],
                "offered": [list(s["visible"]) for s in steps],
                "spent_uc": data["spent_synthetic_uc"],
                "remaining_uc": INITIAL_UC - data["spent_synthetic_uc"],
                "terminal": data["terminal"],
                "death_capture": next((i + 1 for i,s in enumerate(steps)
                                       if s["terminal"]), None),
                "refusals": [r["refusal"] for r in data["steps"] if "refusal" in r],
                "harmful_eats": sum(s["chosen"] == EAT and s["result_net"] < 0
                                    for s in steps),
                "recovered_eat_captures": [
                    i + 1 for i,s in enumerate(steps)
                    if i >= 4 and s["chosen"] == EAT
                ] if name == "recovery" else [],
            }
        common = min(len(arms[a]["energy"]) for a in ARM_NAMES)
        result[name] = {
            "arms": arms, "common_prefix_captures": common,
            "energy_at_common_prefix": {
                a: arms[a]["energy"][common - 1] if common else INITIAL_ENERGY
                for a in ARM_NAMES
            },
        }
    return {
        "schema": "i2-g1lab-frozen-revisit-recovery-exploratory-v1",
        "protocol_issue_comment": 6559888186,
        "model_sha_before_intervention": "175a78f877b2a0085d20c980f03968b2dbd58fec",
        "revisit_after": 2, "revisit_bonus": 9,
        "chosen_score_offset": 5,
        "fixed_priors": {"collect":3,"eat":4,"drink":1},
        "initial_energy": INITIAL_ENERGY, "initial_uc": INITIAL_UC,
        "G1_LIVE": "REVIEW_REQUIRED", "M11": "NOT_ESTABLISHED",
        "birth": "FORBIDDEN", "regimes": result,
        "recovery_revisit_actually_eats_at_capture_5_to_8":
            bool(result["recovery"]["arms"]["revisit"]["recovered_eat_captures"]),
    }


class FrozenRevisitRecoveryTests(unittest.TestCase):
    def test_frozen_three_arm_comparison_preserves_failure_and_harm(self):
        data=frozen_revisit_report()
        self.assertEqual(tuple(data["regimes"]), tuple(REGIMES))
        for name, row in data["regimes"].items():
            self.assertEqual(set(row["arms"]), set(ARM_NAMES))
            for arm in row["arms"].values():
                self.assertLessEqual(len(arm["actions"]), 8)
                self.assertGreater(arm["spent_uc"], 0)
                self.assertLessEqual(arm["spent_uc"], INITIAL_UC)
                if arm["terminal"]:
                    self.assertEqual(arm["energy"][-1], 0)
            self.assertEqual(row["arms"]["fixed"]["actions"][:2],
                             row["arms"]["observational"]["actions"][:2])
            self.assertEqual(row["arms"]["fixed"]["actions"][:2],
                             row["arms"]["revisit"]["actions"][:2])
        self.assertEqual(
            data["regimes"]["stable"]["arms"]["fixed"]["actions"][:2], ["C","E"]
        )
        print("I2_G1LAB_FROZEN_REVISIT " +
              json.dumps(data,sort_keys=True,separators=(",",":")))

    def test_revisit_parameter_bound_to_single_reopenable_lab_owner(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"revisit.sqlite"
            lab=IntegratedLab.create(path,life_ref="lab:revisit:owned",
                genesis_ref="lab:revisit:genesis",learning=True,
                revisit=True,deltas=REGIMES["recovery"],initial_energy=24)
            lab.step()
            lab.step()
            reopened=IntegratedLab.reopen(path,life_ref="lab:revisit:owned",
                genesis_ref="lab:revisit:genesis")
            self.assertEqual(reopened.audit()["revision"], 2)
            self.assertEqual(reopened.step().index, 2)

    def test_revisit_not_available_to_no_learning_arm(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(LabRefusal, "invalid bounded"):
                IntegratedLab.create(Path(d)/"forbidden.sqlite",
                    life_ref="lab:fixed",genesis_ref="lab:fixed:genesis",
                    learning=False,revisit=True,deltas=REGIMES["stable"])


if __name__ == "__main__":
    unittest.main()
