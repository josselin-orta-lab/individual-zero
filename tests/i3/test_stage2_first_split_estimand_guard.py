"""No-World guard for distinct total-effect vs direct-motor estimands."""
from copy import deepcopy
import json
import unittest
from unittest.mock import patch

from i3.lab import stage2_first_split_estimand_guard as G
from i3.modules.mind import Mind
from i3.modules.world import World


def work(cycles):
    return {"cycles": cycles, "memory_items": 4, "simulated_steps": 0,
            "replays": 0}


def pair(name="a", cycles=(15, 14), motors=None):
    motors = motors or (["attendre", None], ["attendre", None])
    extra = cycles[0] - cycles[1]
    return {
        "pair_id": name, "exposure": "EXPOSED", "initial_matched": True,
        "source_matched": True, "exogenous_computed_paid_equal": True,
        "visible": {"motor": motors[0], "decision_work": work(cycles[0]),
                    "after_payment_body": [
                        50-0.02*extra, 60., 60., 90., 50-0.05*extra]},
        "discard": {"motor": motors[1], "decision_work": work(cycles[1]),
                    "after_payment_body": [50., 60., 60., 90., 50.]},
    }


def no_exposure(name, reason):
    return {"pair_id": name, "exposure": reason, "initial_matched": True,
            "source_matched": None, "exogenous_computed_paid_equal": None,
            "visible": None, "discard": None}


class FirstSplitEstimandGuardTests(unittest.TestCase):
    def test_exact_archived_four_are_not_reexecuted_or_promoted(self):
        with patch.object(World, "__init__",
                          side_effect=AssertionError("World forbidden")), patch.object(
                              Mind, "decide",
                              side_effect=AssertionError("Mind forbidden")):
            result = G.audit_archived_first_splits()
        print("I3_FIRST_SPLIT_ESTIMAND_GUARD="+json.dumps(
            result, sort_keys=True, separators=(",", ":")))
        self.assertEqual(result["status"], "ARCHIVED_FIRST_SPLIT_METHODS_GUARD_PASS")
        self.assertEqual(result["assigned"], 4)
        self.assertEqual(result["counts"]["NATIVE_COST_ONLY"], 3)
        self.assertEqual(result["counts"]["NO_OBSERVED_SPLIT"], 1)
        self.assertEqual(result["counts"]["MOTOR_ONLY"], 0)
        self.assertEqual(result["controlled_direct_motor_examples"], 0)
        self.assertEqual(result["upstream_status_unchanged"],
                         "PAID_RESIDUAL_READOUT_STOP_NATIVE_COST_CONFOUND")
        self.assertEqual(result["new_worlds"], 0)
        self.assertEqual(result["new_scientific_lives"], 0)
        self.assertEqual(result["scientific_verdict"], "NOT_ISSUED")
        self.assertEqual(len(result["deterministic_sha256"]), 64)

    def test_cost_mediator_is_natural_total_not_direct_motor(self):
        r = G.classify_receipt(pair())
        self.assertEqual(r["classification"], "NATIVE_COST_ONLY")
        self.assertAlmostEqual(r["extra_visible_model_energy"], .02)
        self.assertAlmostEqual(r["extra_visible_model_vigilance"], .05)
        self.assertLess(r["same_motor_cost_body_residual"], G.TOL)
        self.assertTrue(r["natural_total_effect_eligible"])
        self.assertFalse(r["controlled_direct_motor_eligible"])

    def test_no_split_direct_motor_and_mixed_mediator(self):
        self.assertEqual(G.classify_receipt(pair(cycles=(14,14)))["classification"],
                         "NO_OBSERVED_SPLIT")
        changed = (["attendre",None], ["dormir",None])
        direct = G.classify_receipt(pair(cycles=(14,14), motors=changed))
        self.assertEqual(direct["classification"], "MOTOR_ONLY")
        self.assertTrue(direct["controlled_direct_motor_eligible"])
        mixed = G.classify_receipt(pair(cycles=(15,14), motors=changed))
        self.assertEqual(mixed["classification"], "MOTOR_AND_NATIVE_COST")
        self.assertFalse(mixed["controlled_direct_motor_eligible"])

    def test_all_assigned_no_information_denial_terminal_censor(self):
        reasons = G.NO_EXPOSURE
        receipts = [pair("a")] + [no_exposure(str(i), x)
                                  for i, x in enumerate(reasons)]
        ids = ["a"]+[str(i) for i in range(len(reasons))]
        out = G.reduce_assigned(receipts, ids)
        self.assertEqual(out["total_assigned"], 5)
        self.assertEqual(out["exposed"], 1)
        self.assertEqual(out["counts"]["NO_EXPOSURE"], 4)
        self.assertEqual(sum(out["counts"].values()), 5)
        self.assertFalse(out["effect_size_inferred"])
        self.assertFalse(out["independent_ecology_attested"])
        self.assertFalse(out["autonomous_compute_purchase_demonstrated"])
        self.assertEqual(out["scientific_verdict"], "NOT_ISSUED")

    def test_missing_duplicate_extra_and_fake_exposure_rejected(self):
        a=pair("a")
        for receipts, ids in (([a,a], ["a","b"]), ([a], ["a","b"]),
                              ([a], ["a","a"]), ([a], ["b"])):
            with self.subTest(ids=ids, n=len(receipts)):
                with self.assertRaises(ValueError):
                    G.reduce_assigned(receipts, ids)
        bad=pair()
        bad["source_matched"]=False
        with self.assertRaises(ValueError):
            G.classify_receipt(bad)
        bad=pair()
        bad["exogenous_computed_paid_equal"]=False
        with self.assertRaises(ValueError):
            G.classify_receipt(bad)
        bad=no_exposure("a", "DENIED")
        bad["visible"]={"motor":["attendre",None]}
        with self.assertRaises(ValueError):
            G.classify_receipt(bad)

    def test_unexplained_same_motor_body_and_unpaid_work_rejected(self):
        bad=pair()
        bad["visible"]["after_payment_body"][2]=59
        with self.assertRaisesRegex(ValueError, "unexplained body difference"):
            G.classify_receipt(bad)
        for invalid in (-1, 0.1, True, "1"):
            bad=pair()
            bad["visible"]["decision_work"]["cycles"]=invalid
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                G.classify_receipt(bad)
        for invalid in (float("nan"), float("inf"), -1, 101):
            bad=pair()
            bad["visible"]["after_payment_body"][0]=invalid
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                G.classify_receipt(bad)
        bad=pair()
        bad["discard"]["decision_work"].pop("memory_items")
        with self.assertRaises(ValueError):
            G.classify_receipt(bad)

    def test_read_only_deterministic_and_original_stays_frozen(self):
        source=G.ORIGINAL.SOURCE.read_bytes()
        a=G.audit_archived_first_splits()
        b=G.audit_archived_first_splits()
        self.assertEqual(a,b)
        self.assertEqual(source,G.ORIGINAL.SOURCE.read_bytes())
        with patch.object(G.ORIGINAL, "audit", return_value={"status": "FORGED"}):
            with self.assertRaises(ValueError):
                G.audit_archived_first_splits()


if __name__ == "__main__":
    unittest.main()
