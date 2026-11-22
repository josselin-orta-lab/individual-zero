"""F1L preregistration and DEV_ONLY tests. Never run reserved L01..L32."""
from __future__ import annotations

from copy import deepcopy
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from i3.modules.genome import midpoint
from i3.modules.mind import Mind
from tools import stage8f1c_paid_postaction_learning as C
from tools import stage8f1l_paid_content_body_value_dev as P
from tools.stage8f1j_fixed_round_paid_competition import F1JFixedRoundMind


class F1LNoHoldoutExposure(unittest.TestCase):
    def test_preregistration_exact_sha_and_32_new_reserves_readonly(self):
        self.assertEqual(P.git_blob(Path(P.GRID_PATH).read_bytes()), P.GRID_BLOB)
        self.assertEqual(P.git_blob(Path(P.PROTOCOL_PATH).read_bytes()),
                         P.PROTOCOL_BLOB)
        grid = P.verify_readonly_prereg()  # only reads bytes, no births
        self.assertEqual(len(grid["origins"]), 32)
        self.assertEqual(len(grid["ecologies"]), 8)
        self.assertFalse(grid["scientific_exposure_authorized"])
        self.assertEqual([r["seed"] for r in grid["origins"]],
                         list(range(202611229501, 202611229533)))
        self.assertEqual(grid["frozen_prior_results"]["F1K"],
                         "INCONCLUSIVE_NO_REAL_SURCHARGE")

    def test_dev_is_exactly_separate_and_locked(self):
        reserve = P.verify_readonly_prereg()
        for grid in [P.dev_grid(), P.dev_grid(full=True)]:
            self.assertEqual(P.validate_dev(grid), grid)
            self.assertFalse(
                {r["seed"] for r in grid["origins"]} &
                {r["seed"] for r in reserve["origins"]})
            self.assertFalse(
                {e["id"] for e in grid["ecologies"]} &
                {e["id"] for e in reserve["ecologies"]})
            self.assertTrue(all(r["id"].startswith("DEV_L")
                                for r in grid["origins"]))
        self.assertEqual(P.dev_grid()["final_tick"], 9)
        self.assertEqual(P.dev_grid(full=True)["final_tick"], 60)
        self.assertEqual(len(P.dev_grid(full=True)["origins"]), 8)

    def test_science_is_denied_before_world_creation_even_if_grid_is_authentic(self):
        grid = P.verify_readonly_prereg()
        with patch.object(P, "new_world", side_effect=AssertionError(
                "forbidden reserved World.step")):
            with self.assertRaises(PermissionError):
                P.produce(grid, phase="F1L_HELDOUT_RELEASE")
            with self.assertRaises(ValueError):
                P.produce(grid, phase="DEV_ONLY")
        with self.assertRaises(PermissionError):
            P.new_world(grid, grid["origins"][0])

    def test_original_p13_and_f1j_stay_unchanged(self):
        self.assertEqual(P.git_blob(Path(
            "src/i3/modules/mind.py").read_bytes()),
            P.SOURCE_BLOBS["src/i3/modules/mind.py"])
        self.assertEqual(P.git_blob(Path(
            "tools/stage8f1j_fixed_round_paid_competition.py").read_bytes()),
            P.SOURCE_BLOBS[
                "tools/stage8f1j_fixed_round_paid_competition.py"])
        self.assertIs(type(Mind(midpoint(), 202611229607)), Mind)
        self.assertIs(type(F1JFixedRoundMind(midpoint(), 202611229607)),
                      F1JFixedRoundMind)

    def test_semantic_sham_ignores_only_label_not_physical_receipts(self):
        original = {"readout_mode": "full", "receipt_sha256": "a",
                    "cognitive_work": {"cycles": 5},
                    "native_motor": {"body": [12, 15, 18, 20, 30]}}
        sham = deepcopy(original)
        sham["readout_mode"] = "full_sham"
        sham["receipt_sha256"] = "b"
        self.assertEqual(P.semantic_sham_step(original),
                         P.semantic_sham_step(sham))
        sham["native_motor"]["body"][0] += 1
        self.assertNotEqual(P.semantic_sham_step(original),
                            P.semantic_sham_step(sham))


@unittest.skipUnless(os.getenv("I3_F1L_DEV_CI") == "1",
                     "native DEV_L steps only in dedicated F1L workflow")
class F1LNativeDevOnly(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.grid = P.dev_grid()
        cls.report = P.produce(cls.grid)

    def test_two_dev_roots_have_real_paid_sources_and_neutral_sham(self):
        self.assertEqual(self.report["phase"], "DEV_ONLY")
        self.assertEqual(self.report["producer_only_status"],
                         "DEV_ONLY_NOT_SCIENTIFIC")
        self.assertEqual(self.report["scientific_verdict"], None)
        self.assertEqual(self.report["origin_count"], 2)
        for r in self.report["rows"]:
            self.assertTrue(r["source"]["valid_paid_personal_source"],
                            r["source"]["source_error"])
            self.assertEqual(len(r["source"]["source_steps"]), 4)
            self.assertTrue(r["comparison"]["sham_neutral"])
            self.assertTrue(r["comparison"]["arm_valid"])
            self.assertTrue(r["comparison"]["equal_t5_decision_cost"],
                            r["origin"]["id"])
            self.assertEqual(set(r["arms"]), set(P.ARMS))
            for arm in r["arms"].values():
                self.assertTrue(all(s["no_experimental_action_override"]
                                    for s in arm["steps"]))

    def test_two_dev_runs_are_byte_identical(self):
        other = P.produce(self.grid)
        self.assertEqual(C.digest(self.report), C.digest(other))

    def test_nonnative_t5_bill_and_fake_sham_fail_preliminary_comparison(self):
        row = self.report["rows"][0]
        arms = deepcopy(row["arms"])
        arms["stale_owned_t1_means"]["steps"][0]["cognitive_work"]["cycles"] += 1
        compare = P.compare(arms, True)
        self.assertFalse(compare["equal_t5_decision_cost"])
        self.assertTrue(compare["sham_neutral"])
        arms = deepcopy(row["arms"])
        arms["full_sham"]["steps"][0]["native_motor"]["body"][0] += 1
        self.assertFalse(P.compare(arms, True)["sham_neutral"])


if __name__ == "__main__":
    unittest.main()
