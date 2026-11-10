"""I3 paid next-distress learning without new motor or scientific permission."""
import json
import unittest

from i3.lab import stage2_paid_distress_shadow_engineering as ENG
from i3.lab import stage2_replay_predictive_negative_control as NEG
from i3.lab.dev_worlds import dev_open_field
from i3.modules.body import BodyLaws, CognitiveBudget, CognitiveWork, cognitive_cost
from i3.modules.genome import midpoint
from i3.modules.mind import Mind
from i3.modules.world import World


class PaidDistressShadowEngineeringTests(unittest.TestCase):
    def test_three_paid_memory_content_arms_score_same_actual_lived_outcome(self):
        result = ENG.rehearse()
        print("I3_PAID_DISTRESS_ENGINEERING_RESULT="+json.dumps(result,sort_keys=True))
        self.assertEqual(result["engineering_matched_triplets"], 2)
        self.assertEqual(result["funded_and_scored_events"], 6)
        self.assertEqual(result["equal_cost_and_physical_triplets"], 2)
        self.assertEqual(result["scientific_lives"], 0)
        self.assertEqual(result["scientific_verdict"], "NOT_ISSUED")
        self.assertTrue(result["cost_tariff_is_provisional_not_cpu_calibrated"])
        for row in result["rows"]:
            self.assertEqual([x["mode"] for x in row["branches"]], list(ENG.MODES))
            forecasts=[]
            for branch in row["branches"]:
                receipt=branch["witness"]
                event=receipt["first"]
                self.assertEqual(receipt["status"], "PAID_AND_SCORED")
                self.assertTrue(receipt["fee_paid_in_native_world_step"])
                self.assertTrue(event["prediction_sha256"])
                self.assertEqual(event["training_updates_executed"], 3)
                self.assertEqual(event["status"], "PAID_AND_SCORED")
                self.assertEqual(event["shadow_work"]["replays"], 3)
                self.assertGreater(event["energy_paid"], 0)
                self.assertGreater(event["vigilance_paid"], 0)
                self.assertEqual(event["result"]["status"],
                                 "ACTUAL_FIRST_PERSON_OUTCOME_SCORED")
                forecasts.append(event["result"]["frozen_prediction"])
            self.assertEqual(len(set(forecasts)) >= 2, True)
            # Every arm experiences the same actual paid-body transition.
            targets=[x["witness"]["first"]["result"]["observed_intrinsic_reward"]
                     for x in row["branches"]]
            self.assertEqual(len(set(targets)),1)
            self.assertEqual(len(set(
                x["witness"]["first"]["energy_paid"] for x in row["branches"])),1)
            self.assertEqual(len(set(
                x["witness"]["first"]["vigilance_paid"] for x in row["branches"])),1)

    def test_funding_rejection_leaves_original_action_and_budget_untouched(self):
        mind=NEG.synthetic_personal_mind(3)
        low=(0.2,60.,60.,80.,0.1)
        capture={"body":low}
        budget=CognitiveBudget(low,BodyLaws())
        monitor=ENG.PaidDistressWitness("priority",930043)
        monitor.after_choice_before_world(mind,capture,budget,"se_deplacer",None)
        report=monitor.report()
        self.assertEqual(report["status"],"NO_FUNDED_FORECAST")
        self.assertEqual(budget.work,CognitiveWork())
        self.assertEqual(report["first"]["energy_paid"],0.)
        self.assertEqual(report["first"]["vigilance_paid"],0.)
        self.assertFalse(report["fee_paid_in_native_world_step"])
        self.assertIsNone(report["first"]["prediction_sha256"])
        self.assertIsNone(monitor._reference)
        with self.assertRaises(ValueError):
            ENG.PaidDistressWitness("invalid",930043)

    def test_action_reservation_must_survive_paid_head(self):
        mind=NEG.synthetic_personal_mind(3)
        initial=(2.10,60.,60.,80.,60.)
        budget=CognitiveBudget(initial,BodyLaws())
        spy=ENG.PaidDistressWitness("random",930043)
        spy.after_choice_before_world(mind,{"body":initial},budget,
                                       "se_deplacer",None)
        self.assertEqual(spy.report()["status"],"NO_FUNDED_FORECAST")
        self.assertEqual(budget.work,CognitiveWork())
        self.assertIsNone(spy._reference)

    def test_no_history_is_explicit_null_not_free_positive_result(self):
        mind=Mind(midpoint(),930041)
        capture={"body":(65.,55.,50.,90.,70.)}
        budget=CognitiveBudget(capture["body"],BodyLaws())
        w=ENG.PaidDistressWitness("discard",930041)
        w.after_choice_before_world(mind,capture,budget,"attendre",None)
        self.assertEqual(w.report()["status"],"NO_ELIGIBLE_HISTORY")
        self.assertEqual(w.report()["steps"],0)
        self.assertEqual(budget.work,CognitiveWork())

    def test_post_decision_pre_outcome_seal_cannot_be_replaced(self):
        mind=NEG.synthetic_personal_mind(4)
        before=(70.,60.,50.,90.,80.)
        budget=CognitiveBudget(before,BodyLaws())
        w=ENG.PaidDistressWitness("priority",930043)
        w.after_choice_before_world(mind,{"body":before},budget,"attendre",None)
        self.assertIsNotNone(w.pending)
        with self.assertRaises(RuntimeError):
            w.report()
        with self.assertRaises(RuntimeError):
            w.after_actual_world_step("boire",None,
                 {"body":(69.,59.,49.,89.,79.),"dead":()})
        # Failed attempts never silently settle a different factual action.
        self.assertIsNotNone(w.pending)
        with self.assertRaises(RuntimeError):
            w.after_choice_before_world(mind,{"body":before},budget,
                                        "attendre",None)

    def test_cost_uses_actual_native_v2_laws_and_spies_restore(self):
        work=ENG._tariff(6)
        self.assertEqual(work,CognitiveWork(cycles=5,memory_items=9,replays=3))
        a,b=cognitive_cost(BodyLaws(),work)
        self.assertGreater(a,0)
        self.assertGreater(b,0)
        old_decide,old_step=Mind.decide,World.step
        ENG.run_paid_reference(midpoint(),dev_open_field(),930041,"priority",12)
        self.assertIs(Mind.decide,old_decide)
        self.assertIs(World.step,old_step)


if __name__=="__main__":
    unittest.main()
