"""Source-frozen four technical-life prequential native effects audit."""
import json
import unittest
from unittest.mock import patch

from i3.lab import stage2_native_effect_reliability_observer as E
from i3.modules.body import BodyLaws, CognitiveWork
from i3.modules.mind import Mind
from i3.modules.world import World


class NativeEffectsPrequentialTests(unittest.TestCase):
    def test_all_four_fixed_engineering_lives_reproduce_native_baseline(self):
        report = E.audit()
        print("I3_PREQUENTIAL_NATIVE_EFFECT_RELIABILITY=" +
              json.dumps(report, sort_keys=True, separators=(",", ":")))
        self.assertEqual(report["status"],
                         "PREQUENTIAL_FIRST_PERSON_EFFECT_CUSTODY_PASS")
        self.assertEqual(report["engineering_full_lives"], 4)
        self.assertEqual(report["source_worlds"],
                         ["dev-open-field", "dev-failing-well"])
        self.assertEqual(report["fixed_laboratory_seeds"], [840061, 840062])
        self.assertEqual(report["fixed_horizon"], 80)
        self.assertEqual(report["scientific_lives"], 0)
        self.assertEqual(report["scientific_verdict"], "NOT_ISSUED")
        self.assertFalse(report["stage2_2_go"])
        self.assertEqual(len(report["deterministic_aggregate_sha256"]), 64)
        self.assertTrue(report["all_four_baseline_trace_and_accounting_equal"])
        self.assertEqual(report["all_assigned_factual_steps"],
                         sum(row["steps_lived"] for row in report["rows"]))
        self.assertEqual(report["scored_native_forecasts"],
                         sum(r["report"]["scored_forecasts"]
                             for r in report["rows"]))
        for row in report["rows"]:
            r = row["report"]
            self.assertTrue(row["baseline_native_trajectory_unchanged"])
            self.assertEqual(r["all_assigned"], row["steps_lived"])
            self.assertEqual(r["scored_forecasts"] + r["null_decisions"],
                             r["all_assigned"])
            self.assertTrue(r["proper_point_mean_score_only"])
            self.assertTrue(r["prediction_error_not_uncertainty_calibration"])
            self.assertTrue(r["observer_cpu_not_billed_as_organism_work"])
            self.assertEqual(
                r["paid_learning_outcomes"]
                + r["unfunded_learning_outcomes"]
                + r["terminal_outcomes"]
                + r["null_decisions"], r["all_assigned"])
            for step in r["events"]:
                self.assertEqual(len(step["body_before"]), 5)
                self.assertEqual(len(step["post_paid_learning_body"]), 5)
                self.assertEqual(len(step["immediate_post_world_body"]), 5)
                self.assertEqual(len(step["actual_delta"]), 5)
                if step["action"] is not None:
                    self.assertEqual(len(step["forecast_delta"]), 5)
                    self.assertEqual(len(step["squared_errors"]), 5)
                    self.assertEqual(len(step["preoutcome_forecast_sha256"]),64)
                    self.assertTrue(all(x>=0 for x in step["squared_errors"]))
                for name in ("energy", "vigilance"):
                    rec = step["native_decision_bill"][name]
                    self.assertEqual(rec["requested"], rec["paid"])
                    self.assertEqual(rec["unpaid"], 0)
                if step["learning_status"] == "PAID_LEARNING":
                    self.assertIsNotNone(step["native_learning_bill"])
                    for name in ("energy", "vigilance"):
                        l = step["native_learning_bill"][name]
                        self.assertEqual(l["requested"], l["paid"])
                        self.assertEqual(l["unpaid"], 0)

    def test_preoutcome_cannot_be_scored_before_factual_world(self):
        w = E.PrequentialWitness()
        with self.assertRaisesRegex(RuntimeError, "World outcome before"):
            w.after_world(None, "attendre", None, CognitiveWork(),
                          {"body":(60.,)*5,"cognitive_accounting":{}})
        mind = Mind(E.midpoint(), 840061)
        body = (70.,60.,50.,90.,80.)
        budget = E.CognitiveBudget(body, BodyLaws()) if hasattr(
            E, "CognitiveBudget") else None
        from i3.modules.body import CognitiveBudget
        budget = CognitiveBudget(body, BodyLaws())
        w.before_choice(mind, {"body":body}, budget, None, None,
                        CognitiveWork(), {"funding":"NO_PROCESSING_BUDGET"})
        with self.assertRaisesRegex(RuntimeError, "never reached factual World"):
            w.report()

    def test_outcome_payment_is_required_before_learning(self):
        witness = E.PrequentialWitness()
        mind = Mind(E.midpoint(), 840061)
        body = (70.,60.,50.,90.,80.)
        from i3.modules.body import CognitiveBudget
        budget = CognitiveBudget(body, BodyLaws())
        mind.last=(body,("attendre",),"attendre",None)
        witness.before_choice(mind, {"body":body}, budget, "attendre", None,
                              CognitiveWork(), {"funding":"FUNDED"})
        world = World(E.dev_open_field())
        world.body=body
        result=world.step("attendre",None,CognitiveWork())
        witness.after_world(world,"attendre",None,CognitiveWork(),result)
        with self.assertRaisesRegex(RuntimeError, "no funded learning bill"):
            witness.before_learn_update(mind,result,0)

    def test_cannot_fabricate_payment_or_wrong_source_grid(self):
        w = E.PrequentialWitness()
        with self.assertRaisesRegex(RuntimeError, "missing actual"):
            E._check_paid(BodyLaws(), CognitiveWork(cycles=1), {})
        with self.assertRaises(ValueError):
            E.run_observed(E.dev_open_field, 999)
        with self.assertRaises(ValueError):
            E.run_observed(lambda: E.dev_open_field(), 840061)


if __name__ == "__main__":
    unittest.main()
