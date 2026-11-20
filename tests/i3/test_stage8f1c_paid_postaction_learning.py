"""F1C post-action outcome acquisition is native, paid, observable, falsifiable.

Synthetic engineering Worlds ONLY: no run_life, no birth/cohort, no Stage8-E2 retry.
"""
from __future__ import annotations

from copy import deepcopy
import unittest

from i3.modules.body import CognitiveWork
from tools import stage8f1c_paid_postaction_learning as P
from tools import stage8f1c_independent_postaction_audit as I


def reseal(report):
    """Malicious receipt re-signing: audit must reject physics/content, not just hashes."""
    for row in report["arms"].values():
        for field in ("private_before_decision", "private_before_postaction_learning",
                      "private_computed_postaction", "private_persisted_postaction"):
            row[field]["sha256"] = I.h(row[field]["data"])
        row["receipt_sha256"] = I.h({k: v for k, v in row.items()
                                      if k != "receipt_sha256"})
    report["provenance_chain_sha256"] = I.h({
        "source": P.BASE,
        "receipts": [report["arms"][k]["receipt_sha256"]
                     for k in ("retain", "discard_after_compute")],
        "terminal": report["terminal_no_learning"]})


class PaidPostActionNativeLearning(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proof = P.produce()
        cls.cold = I.audit(cls.proof, P.digest(cls.proof))

    def test_real_native_learning_payment_precedes_update(self):
        self.assertEqual(self.cold["native_world_step_receipts_verified"], 3)
        self.assertEqual(self.cold["paired_native_action_and_learning_cases"], 1)
        self.assertEqual(self.cold["paid_learning_computations"], 2)
        self.assertEqual(self.cold["retained_paid_updates"], 1)
        self.assertEqual(self.cold["equal_paid_discarded_updates"], 1)
        self.assertEqual(self.proof["native_full_lives_created"], 0)
        self.assertEqual(self.proof["new_scientific_cohorts"], 0)
        for mode in ("retain", "discard_after_compute"):
            r = self.proof["arms"][mode]
            self.assertEqual(r["action"], "dormir")
            self.assertEqual(r["native_motor_step"]["t"], 1)
            self.assertEqual(r["learning_work"], {
                "cycles": 2, "simulated_steps": 32,
                "memory_items": 3, "replays": 1})
            self.assertEqual(r["prepaid_replays"], r["executed_replays"])
            self.assertAlmostEqual(r["paid_postaction_learning"]["energy"]["paid"], .1096)
            self.assertAlmostEqual(r["paid_postaction_learning"]["vigilance"]["paid"], .174)
            self.assertTrue(r["unaffordable_extra_payment_rejected_without_mutation"])

    def test_complete_private_state_and_physical_pairing(self):
        keep = self.proof["arms"]["retain"]
        discard = self.proof["arms"]["discard_after_compute"]
        self.assertEqual(keep["private_before_decision"],
                         discard["private_before_decision"])
        self.assertEqual(keep["capture_sha256"], discard["capture_sha256"])
        self.assertEqual(keep["native_motor_step"], discard["native_motor_step"])
        self.assertEqual(keep["private_before_postaction_learning"],
                         discard["private_before_postaction_learning"])
        self.assertEqual(keep["learning_work"], discard["learning_work"])
        self.assertEqual(keep["paid_postaction_learning"],
                         discard["paid_postaction_learning"])
        self.assertEqual(keep["body_after_paid_learning"],
                         discard["body_after_paid_learning"])
        self.assertEqual(keep["private_computed_postaction"],
                         discard["private_computed_postaction"])

    def test_real_lived_effect_and_td_are_retained_only_in_active_mind(self):
        keep = self.proof["arms"]["retain"]
        discard = self.proof["arms"]["discard_after_compute"]
        self.assertNotEqual(keep["private_before_postaction_learning"],
                            keep["private_persisted_postaction"])
        self.assertEqual(keep["private_persisted_postaction"],
                         keep["private_computed_postaction"])
        self.assertEqual(discard["private_persisted_postaction"],
                         discard["private_before_postaction_learning"])
        self.assertNotEqual(discard["private_persisted_postaction"],
                            discard["private_computed_postaction"])
        delta = self.cold["effect_delta_observed_from_native_body"]
        self.assertEqual(len(delta), 5)
        self.assertGreater(delta[0], 0.)
        I.learned_delta_verified(keep["private_before_postaction_learning"],
                                 keep["private_persisted_postaction"],
                                 keep["before_body"], keep["body_after_paid_learning"])

    def test_independent_reduction_rejects_native_learning_payment_forgery(self):
        bad = deepcopy(self.proof)
        # Re-sign BOTH matched arms: a counterfeit that preserves equality
        # must still fail the independent physical two-currency computation.
        for arm in bad["arms"].values():
            arm["paid_postaction_learning"]["energy"]["paid"] = 0.
        reseal(bad)
        with self.assertRaisesRegex(ValueError, "unpaid|native|cognition"):
            I.audit(bad)

    def test_independent_reduction_rejects_unpaid_learning_reserve(self):
        bad = deepcopy(self.proof)
        bad["arms"]["retain"]["body_after_paid_learning"][0] += 1.
        bad["arms"]["discard_after_compute"]["body_after_paid_learning"][0] += 1.
        reseal(bad)
        with self.assertRaisesRegex(ValueError, "balance|resource|debit"):
            I.audit(bad)

    def test_independent_reduction_rejects_private_memory_mismatch(self):
        bad = deepcopy(self.proof)
        bad["arms"]["retain"]["private_before_decision"]["data"]["private"]["__dict__"][0][1] = 99.
        reseal(bad)
        with self.assertRaisesRegex(ValueError, "unmatched|private"):
            I.audit(bad)

    def test_independent_reduction_rejects_fabricated_learning_even_if_resealed(self):
        bad = deepcopy(self.proof)
        for mode, fields in (
            ("retain", ("private_computed_postaction", "private_persisted_postaction")),
            ("discard_after_compute", ("private_computed_postaction",))):
            for field in fields:
                snap = bad["arms"][mode][field]["data"]["private"]["__dict__"]
                effects = dict(snap)["effects"]["__effects_model__"]
                stats = dict(effects["__dict__"])["stats"]["__dict__"]
                for key, entry in stats:
                    if key.get("__tuple__") == ["dormir"]:
                        entry[1][0] += 0.25
        reseal(bad)
        with self.assertRaisesRegex(ValueError, "fabricated consequence"):
            I.audit(bad)

    def test_no_replay_or_learning_after_native_terminal_death(self):
        terminal = self.proof["terminal_no_learning"]
        self.assertEqual(terminal["death_causes"], ["zero_food"])
        self.assertEqual(terminal["prepaid_learning_work"],
                         {"cycles": 0, "simulated_steps": 0,
                          "memory_items": 0, "replays": 0})
        self.assertTrue(terminal["postmortem_payment_rejected_without_mutation"])
        bad = deepcopy(self.proof)
        bad["terminal_no_learning"]["death_causes"] = []
        reseal(bad)
        with self.assertRaisesRegex(ValueError, "death"):
            I.audit(bad)

    def test_same_inputs_reproduce_exact_complete_receipts(self):
        second = P.produce()
        self.assertEqual(P.digest(second), P.digest(self.proof))
        self.assertEqual(second["provenance_chain_sha256"],
                         self.proof["provenance_chain_sha256"])
        self.assertEqual(I.audit(second), I.audit(self.proof))

    def test_f1c_has_no_scientific_birth_policy(self):
        import inspect
        from i3.modules.stage8f1_paid_microdecision_mind import PaidMicrodecisionMind
        self.assertNotIn("run_life(", inspect.getsource(P.produce))
        self.assertNotIn("run_life(", inspect.getsource(P._full_action_and_learning))
        self.assertNotIn("run_life(", inspect.getsource(PaidMicrodecisionMind.decide))
        self.assertEqual(self.proof["frozen_negative_stage8e2"], P.NEGATIVE)
        self.assertEqual(self.proof["native_whole_life_evidence_head"], "NOT_CLAIMED")
        self.assertEqual(CognitiveWork(cycles=1).cycles, 1)


if __name__ == "__main__":
    unittest.main()
