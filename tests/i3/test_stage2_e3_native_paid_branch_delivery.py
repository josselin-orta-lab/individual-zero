"""Source-frozen E3.1 native Mind.decide mediation (all synthetic/no World)."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import stage2_e3_native_paid_branch_delivery as E
from i3.modules.body import BodyLaws, CognitiveBudget, CognitiveWork, VITAL
from i3.modules.genome import midpoint
from i3.modules.mind import Mind
from i3.modules.personal_outcomes import NoPersonalSupport
from i3.modules.reference_branches import ReferenceBranchMemory
from i3.modules.world import World


class E3NativePaidBranchDeliveryTests(unittest.TestCase):
    def test_real_native_decide_not_detached_action_and_never_world(self):
        with patch.object(World, "__init__", side_effect=AssertionError(
                "E3 MUST NOT create any World")):
            result = E.audit()
        self.assertEqual(result["fixed_histories"], 3)
        self.assertEqual(result["fixed_body"], E.BODY)
        self.assertEqual(result["fixed_seed"], 211)
        self.assertEqual(result["paired_native_Mind_decide_software_comparisons"], 3)
        self.assertTrue(result["real_VD_extra_operator_and_cost_parity"])
        self.assertTrue(result["native_Competition_and_Action_Control_retained"])
        self.assertFalse(result["physical_World_motor_executed"])
        self.assertFalse(result["physical_World_body_observed"])
        self.assertEqual(result["new_worlds"], 0)
        self.assertEqual(result["new_scientific_lives"], 0)
        self.assertFalse(result["stage2_2_go"])
        self.assertEqual(result["scientific_verdict"], "NOT_ISSUED")
        for unit in result["cases"]:
            with self.subTest(history=unit["history"]):
                v,d=unit["visible"],unit["paid_discard"]
                self.assertTrue(v["actual_native_Mind_decide_was_called"])
                self.assertTrue(d["actual_native_Mind_decide_was_called"])
                self.assertTrue(v["all_offered_options_scored"])
                self.assertTrue(d["all_offered_options_scored"])
                self.assertEqual(v["full_option_set_offered"],
                                 d["full_option_set_offered"])
                self.assertEqual(v["full_option_set_scored"],
                                 d["full_option_set_scored"])
                self.assertEqual(v["initial_native_rng_sha256"],
                                 d["initial_native_rng_sha256"])
                self.assertEqual(v["initial_native_budget_rng_sha256"],
                                 d["initial_native_budget_rng_sha256"])
                self.assertTrue(v["native_model_work_fully_debit_able"])
                self.assertTrue(d["native_model_work_fully_debit_able"])
                self.assertIn(v["action"], (None, "attendre", "dormir"))
                self.assertIn(d["action"], (None, "attendre", "dormir"))
                self.assertFalse(v["actual_World_motor_executed"])

    def test_every_supported_branch_operates_and_pays_in_discard_too(self):
        result=E.audit()
        for item in result["cases"]:
            v,d=item["visible"],item["paid_discard"]
            self.assertEqual(len(v["readout_events"]),
                             len(d["readout_events"]))
            for ev,ed in zip(v["readout_events"],d["readout_events"]):
                for key in ("action_key","plan_length","source_records",
                            "read_calls","view_constructions",
                            "native_branch_simulations","reduction_paid",
                            "original_score","empirical_score","work"):
                    self.assertEqual(ev[key],ed[key])
                self.assertEqual(ed["original_score"],ed["returned_score"])
                if ev["source_records"]:
                    self.assertEqual(ev["status"],"VISIBLE_READOUT")
                    self.assertEqual(ed["status"],"FULLY_COMPUTED_PAID_DISCARD")
                    self.assertEqual(ev["native_branch_simulations"],
                                     ev["source_records"])
                    self.assertEqual(ev["view_constructions"],
                                     ev["source_records"])
                    self.assertTrue(ev["reduction_paid"])
                    self.assertEqual(ev["empirical_score"],ev["returned_score"])
                if item["history"]=="none":
                    self.assertEqual(ev["source_records"],0)

    def test_discard_keeps_original_native_score_without_free_work(self):
        result=E.audit()
        for item in result["cases"]:
            source = item["paid_discard"]
            r = Mind(midpoint(), E.SEED, observer_full_competition=True)
            if item["history"]!="none":
                deltas=dict(E.FIXED_HISTORIES)[item["history"]]
                for delta in deltas:
                    r.effects.observe(E.NATIVE_KEY,delta)
            budget = CognitiveBudget(E.BODY, BodyLaws())
            action,param,work,info=r.decide(E.CAP,budget)
            raw = info["observer"]["score_witness"]
            paid = source["scores"]
            self.assertEqual([x["option"] for x in raw],
                             [x["option"] for x in paid])
            self.assertEqual(
                [x["total_score"] for x in raw],
                [x["total_score"] for x in paid])
            self.assertGreaterEqual(
                source["decision_work"]["cycles"], work.cycles)
            self.assertTrue(source["native_model_work_fully_debit_able"])

    def test_equal_source_mean_and_rng_across_precommitted_histories(self):
        r = E.audit()
        a,b = r["cases"][0]["visible"],r["cases"][1]["visible"]
        self.assertEqual(a["original_native_effect_stats"],
                         b["original_native_effect_stats"])
        self.assertEqual(a["initial_native_rng_sha256"],
                         b["initial_native_rng_sha256"])
        self.assertEqual(a["initial_native_budget_rng_sha256"],
                         b["initial_native_budget_rng_sha256"])
        self.assertEqual(a["initial_support_size"],2)
        self.assertEqual(b["initial_support_size"],2)
        self.assertEqual(len(a["predecision_model_store_work"]),2)
        self.assertEqual(len(b["predecision_model_store_work"]),2)

    def test_unaffordable_extra_quote_never_reads_memory(self):
        # Low energy retains enough for one bare native reference simulation,
        # but NOT a conservative complete additional source quotation.
        body = (1.,60.,60.,90.,1.)
        mind=E.E3NativeBranchResearchMind(midpoint(), E.SEED, mode="VISIBLE")
        with patch.object(ReferenceBranchMemory, "read_support",
                          side_effect=AssertionError("UNFUNDED DATA ACCESS")):
            budget=CognitiveBudget(body,BodyLaws())
            value, steps, u = mind.simulate(
                body,[("attendre",)],1,budget)
        self.assertEqual(mind.e3_events[0]["status"],"NO_FUNDED_SIGNAL")
        self.assertEqual(mind.e3_events[0]["read_calls"],0)
        self.assertEqual(mind.e3_events[0]["native_branch_simulations"],0)
        self.assertIsInstance(value,float)

    def test_dead_state_rejects_optional_work_before_any_branch_read(self):
        mind=E.E3NativeBranchResearchMind(midpoint(), E.SEED, mode="PAID_DISCARD")
        body=(70.,0.,60.,90.,70.)
        with patch.object(ReferenceBranchMemory, "read_support",
                          side_effect=AssertionError("POSTMORTEM SOURCE")):
            with self.assertRaises(ValueError):
                mind.simulate(body,[("attendre",)],1,
                              CognitiveBudget(body,BodyLaws()))
        self.assertEqual(mind.e3_events,[])

    def test_missing_other_action_cannot_transfer_or_invent_zero_outcome(self):
        mind=E.E3NativeBranchResearchMind(midpoint(), E.SEED, mode="VISIBLE")
        E._synthetic_source(mind, dict(E.FIXED_HISTORIES)["spread"])
        with self.assertRaises(NoPersonalSupport):
            mind.branch_memory.read_support(
                ("boire",None),CognitiveBudget(E.BODY,BodyLaws()))
        with self.assertRaises(ValueError):
            mind.branch_memory.read_support(
                ("manger",None),CognitiveBudget(E.BODY,BodyLaws()))
        with self.assertRaises(ValueError):
            E.E3NativeBranchResearchMind(midpoint(),E.SEED,mode="NOT_AN_ARM")
        self.assertEqual(tuple(x.key for x in mind.branch_memory._samples),
                         (E.KEY,E.KEY))

    def test_frozen_e3_outputs_are_deterministic_without_new_world(self):
        a,b=E.audit(),E.audit()
        self.assertEqual(a,b)
        self.assertEqual(a["aggregate_sha256"],b["aggregate_sha256"])
        self.assertEqual(len(a["aggregate_sha256"]),64)
        self.assertIn(a["mechanism_verdict"],(
            "E3_NATIVE_DECISION_SENSITIVITY_SOFTWARE_ONLY",
            "E3_FROZEN_NATIVE_ACTION_MEDIATION_NOT_SHOWN",
        ))
        print("I3_E3_NATIVE_PAID_BRANCH_SOFTWARE=" + E.json.dumps({
            "aggregate_sha256":a["aggregate_sha256"],
            "technical_verdict":a["mechanism_verdict"],
            "assigned_history_pairs":3,
            "native_motor_differences":a["positive_native_motor_difference_count"],
            "same_actual_optional_compute_and_cost":(
                a["real_VD_extra_operator_and_cost_parity"]),
            "worlds":a["new_worlds"], "lives":a["new_scientific_lives"],
            "scientific_verdict":a["scientific_verdict"],
            "statuses":[(x["history"],x["classification"]) for x in a["cases"]],
        },sort_keys=True))


if __name__=="__main__":
    unittest.main()
