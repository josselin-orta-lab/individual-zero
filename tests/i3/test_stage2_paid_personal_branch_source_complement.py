"""E2 existing paid action-keyed source capacity, WITHOUT a living World."""
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import stage2_paid_personal_branch_source_complement as E
from i3.modules.body import (
    BodyLaws, CognitiveBudget, CognitiveFundingError, CognitiveWork,
    debit_cognition,
)
from i3.modules.genome import midpoint
from i3.modules.mind import Mind
from i3.modules.personal_outcomes import NoPersonalSupport, STORE_WORK
from i3.modules.reference_branches import ReferenceBranchMemory
from i3.modules.world import World


class ExistingPaidPersonalBranchSourceE2(unittest.TestCase):
    def test_fixed_no_world_contrast_retains_different_past_outcomes(self):
        with patch.object(World, "__init__", side_effect=AssertionError(
                "NO World construction for frozen E2 software source")):
            result = E.audit()
        self.assertEqual(result["fixed_histories"], 2)
        self.assertEqual(result["fixed_records_per_history"], 2)
        self.assertEqual(result["source_kind"], E.SOURCE_KIND)
        self.assertTrue(result["equal_original_native_effect_stats"])
        self.assertTrue(result["equal_native_mean_action_forecasts"])
        self.assertTrue(result["equal_native_paid_read_work"])
        self.assertTrue(result["different_action_specific_empirical_branch_support"])
        self.assertFalse(result["additional_information_reaches_native_Mind_decide"])
        self.assertFalse(result["actual_World_settlement_attested"])
        self.assertFalse(result["new_inferred_controller_policy"])
        self.assertEqual(result["new_scientific_Worlds"], 0)
        self.assertEqual(result["new_scientific_lives"], 0)
        self.assertEqual(result["scientific_verdict"], "NOT_ISSUED")
        self.assertFalse(result["stage2_2_go"])
        a,b = result["rows"]
        self.assertEqual(a["native_effects_stats"], b["native_effects_stats"])
        self.assertEqual(a["native_forecast"], b["native_forecast"])
        self.assertNotEqual(a["empirical_support"], b["empirical_support"])
        self.assertEqual(a["read_model_payment"], b["read_model_payment"])
        self.assertEqual(
            [s[1] for s in a["empirical_support"]], [-4., 4.])
        self.assertEqual(
            [s[1] for s in b["empirical_support"]], [0., 0.])
        print("I3_STAGE2_PERSONAL_BRANCH_E2=" + json.dumps({
            "source":"synthetic_unpaid",
            "technical_verdict":result["technical_verdict"],
            "histories":result["fixed_histories"],
            "native_forecasts_same":result["equal_native_mean_action_forecasts"],
            "paid_branch_support_differs":(
                result["different_action_specific_empirical_branch_support"]),
            "read_model_payment":a["read_model_payment"],
            "aggregate_sha256":result["aggregate_sha256"],
            "lives":result["new_scientific_lives"],
            "science":result["scientific_verdict"],
        }, sort_keys=True))

    def test_each_existing_storage_and_read_charge_native_two_currencies(self):
        result = E.audit()
        laws = BodyLaws()
        for row in result["rows"]:
            with self.subTest(history=row["label"]):
                self.assertEqual(len(row["storage_model_payment_each"]), 2)
                self.assertEqual(row["stored_action_key"], E.KEY)
                self.assertEqual(row["stored_samples"], 2)
                self.assertEqual(row["read_receipt"]["status"], "COMPLETE")
                self.assertEqual(row["read_receipt"]["branches"], 2)
                self.assertEqual(row["read_receipt"]["access"], "direct_scan")
                self.assertEqual(row["read_receipt"]["work"], {
                    "cycles":1, "simulated_steps":0, "memory_items":16,
                    "replays":0})
                for ticket in row["storage_model_payment_each"]:
                    self.assertEqual(ticket["work"], {
                        "cycles": STORE_WORK.cycles,
                        "simulated_steps": STORE_WORK.simulated_steps,
                        "memory_items": STORE_WORK.memory_items,
                        "replays": STORE_WORK.replays,
                    })
                    self.assertTrue(ticket["both_currencies_paid_in_model"])
                    self.assertTrue(ticket["no_World_physical_settlement_claim"])
                    self.assertGreater(ticket["energy"], 0.)
                    self.assertGreater(ticket["vigilance"], 0.)
                read = row["read_model_payment"]
                self.assertTrue(read["both_currencies_paid_in_model"])
                self.assertGreater(read["energy"], 0.)
                self.assertGreater(read["vigilance"], 0.)
                self.assertEqual(read["work"], row["read_receipt"]["work"])

    def test_no_other_action_can_inherit_wait_outcome_or_become_favorable_zero(self):
        history = ReferenceBranchMemory()
        physical, _ = debit_cognition(E.BODY, BodyLaws(), E.DECISION_WORK)
        budget = CognitiveBudget(physical, BodyLaws())
        history.observe(E.KEY, E.BODY, E.DECISION_WORK, budget)
        self.assertEqual(budget.work, STORE_WORK)
        candidate = CognitiveBudget(E.BODY, BodyLaws())
        with self.assertRaises(NoPersonalSupport):
            history.read_support(("boire", None), candidate)
        self.assertEqual(candidate.work,
                         CognitiveWork(cycles=1, memory_items=9))
        self.assertEqual(len(history._samples), 1)

    def test_funding_denial_performs_no_read_or_store_and_no_eviction(self):
        history = ReferenceBranchMemory()
        physical, _ = debit_cognition(E.BODY, BodyLaws(), E.DECISION_WORK)
        first = CognitiveBudget(physical, BodyLaws())
        history.observe(E.KEY, E.BODY, E.DECISION_WORK, first)
        unchanged = tuple(history._samples)
        broke = CognitiveBudget((.0001, 60., 60., 90., 70.), BodyLaws())
        with patch.object(history, "_supports",
                          side_effect=AssertionError("unpaid source read")):
            with self.assertRaises(CognitiveFundingError):
                history.read_support(E.KEY, broke)
        self.assertEqual(broke.work, CognitiveWork())
        failed_store = CognitiveBudget((.0001, 60., 60., 90., 70.), BodyLaws())
        with self.assertRaises(CognitiveFundingError):
            history.observe(E.KEY, E.BODY, E.DECISION_WORK, failed_store)
        self.assertEqual(tuple(history._samples), unchanged)
        self.assertEqual(failed_store.work, CognitiveWork())

    def test_invalid_action_and_dead_body_fail_before_any_branch_access(self):
        h=ReferenceBranchMemory()
        with self.assertRaises(ValueError):
            h.read_support(("manger", None), CognitiveBudget(E.BODY, BodyLaws()))
        with self.assertRaises(ValueError):
            h.read_support(("attendre", "world-token"),
                           CognitiveBudget(E.BODY, BodyLaws()))
        dead = CognitiveBudget((70., 0., 60., 90., 70.), BodyLaws())
        with patch.object(h, "_supports",
                          side_effect=AssertionError("postmortem read")):
            with self.assertRaises(ValueError):
                h.read_support(E.KEY, dead)
        self.assertEqual(dead.work, CognitiveWork())

    def test_no_native_controller_or_inherited_goal_is_changed(self):
        a=Mind(midpoint(), E.SEED)
        b=Mind(midpoint(), E.SEED)
        self.assertFalse(hasattr(a, "branch_memory"))
        self.assertEqual(a.effects.stats, b.effects.stats)
        self.assertEqual(a.rng.getstate(), b.rng.getstate())
        self.assertEqual(a._budget_rng.getstate(), b._budget_rng.getstate())
        self.assertEqual(a.values, b.values)
        r=E.audit()
        self.assertTrue(all(x["original_source_not_mutated_by_paid_read"]
                            for x in r["rows"]))
        self.assertNotEqual(r["rows"][0]["support_sha256"],
                            r["rows"][1]["support_sha256"])

    def test_exact_deterministic_bounded_software_digest(self):
        a,b=E.audit(),E.audit()
        self.assertEqual(a, b)
        self.assertEqual(a["aggregate_sha256"], b["aggregate_sha256"])
        self.assertEqual(len(a["aggregate_sha256"]), 64)
        self.assertEqual(a["technical_verdict"],
                         "EXISTING_PAID_ACTION_BRANCHES_CONTAIN_"
                         "NONMEAN_PERSONAL_INFORMATION_SOFTWARE_ONLY")


if __name__ == "__main__":
    unittest.main()
