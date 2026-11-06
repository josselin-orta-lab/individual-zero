"""P5c prospective protocol software-only checks, never held-out exposure."""
from copy import deepcopy
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import p2_ecologies, p4a_validation, p5c_schedule, p5c_heldout
from i3.modules.genome import generation_zero, digest as genome_digest
from i3.runtime.life import run_life
from i3.runtime.provenance import digest, world_snapshot


class P5cSealedProspectiveTests(unittest.TestCase):
    def test_allocation_sealed_without_opening_worlds(self):
        with patch.object(p2_ecologies, "world_for",
                          side_effect=AssertionError("validation world opened")):
            schedule = p5c_schedule.manifest()
            self.assertEqual(schedule, p5c_schedule.manifest())
            self.assertEqual(schedule["lives"], 1152)
            self.assertEqual(len(schedule["exposure"]), 24)
            self.assertEqual({x["index"] for x in schedule["exposure"]},
                             set(range(96, 120)))
            self.assertEqual({x["world_seed"] for x in schedule["exposure"]},
                             set(range(30096, 30120)))
            self.assertEqual(len(p4a_validation.verify_frozen_genomes()), 48)
        for args in [(-1,"stable",0),(4,"stable",0),(0,"false",0),
                     (0,"pulse",2),(True,"stable",1)]:
            with self.assertRaises(ValueError):
                p5c_schedule.world_index(*args)

    def test_missing_prospective_locks_rejected_before_world_opened(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch.object(p2_ecologies, "world_for",
                              side_effect=AssertionError("world opened too early")):
                with self.assertRaises(RuntimeError):
                    p5c_heldout.run()

    def test_receipt_dev_life_paid_and_tampering_rejected(self):
        spec = p2_ecologies.world_for("stable", "development", 19)
        gene = generation_zero(761)
        life = run_life(gene, spec, 1326, 400, keep_trace=True,
                        observer_mind_digest=True,
                        observer_decision_diagnostics=True,
                        score_addend_mode="discard_curiosity_bonus")
        kw = {"mode":"discard_curiosity_bonus","population":0,"arm":"selected",
              "slot":0,"family":"stable","repeat":0,"index":96,
              "seed":1326,"world_hash":digest(world_snapshot(spec)),
              "genome_hash":genome_digest(gene)}
        receipt = p5c_heldout._receipt(life, **kw)
        self.assertTrue(receipt["early_witness"])
        self.assertTrue(any(x["scores"] for x in receipt["early_witness"]))
        corrupted = deepcopy(life)
        candidate = next(x for x in corrupted["trace"]
                         if x["info"]["observer"]["score_witness"])
        candidate["info"]["observer"]["score_witness"][0]["curiosity_bonus_applied"] += 1
        with self.assertRaises(RuntimeError):
            p5c_heldout._receipt(corrupted, **kw)
        corrupted = deepcopy(life)
        corrupted["cognitive_accounting"]["totals"]["energy"]["unpaid"] = 1
        with self.assertRaises(RuntimeError):
            p5c_heldout._receipt(corrupted, **kw)

    def test_shared_option_term_witness_does_not_use_later_body(self):
        def step(t, body, action, c, r):
            return {"t":t,"action":action,"param":None,
                    "pre_body":list(body),"funding":"FUNDED",
                    "scores":[{"option":"boire","base_return":3.,
                               "curiosity_applied":c,"risk_applied":r,
                               "bonus":c+r,"score":3.+c+r}]}
        full={"early_witness":[step(1,[60]*5,"attendre",2.,-1.),
                               step(2,[55]*5,"manger",2.,-1.)]}
        other={"early_witness":[step(1,[60]*5,"boire",0.,-1.),
                                step(2,[20]*5,"manger",100.,-1.)]}
        x=p5c_heldout._early_pair(full,other)
        self.assertEqual(x["first_action_difference_within_window"],1)
        self.assertEqual(x["first_shared_option_score_difference_before_action"],1)
        self.assertEqual(x["first_shared_option_curiosity_difference_before_action"],1)
        self.assertIsNone(x["first_shared_option_risk_difference_before_action"])
        self.assertIsNone(x["first_shared_option_base_return_difference_before_action"])

    def test_n4_exact_inference_is_not_confirmatory(self):
        self.assertEqual(p5c_heldout.p5a_screen._two_sided_sign_flip_p(
            [1,1,1,1]),.125)


if __name__ == "__main__":
    unittest.main()
