"""Prospectively balanced host inference, actual native body cost, true next Body."""
import json
import unittest
from unittest.mock import patch

from i3.lab import stage2_balanced_paid_compact_life_engineering as E
from i3.lab import stage2_replay_predictive_negative_control as NEG
from i3.lab.dev_worlds import dev_open_field
from i3.modules.body import (
    BodyLaws, CognitiveBudget, CognitiveWork, cognitive_cost)
from i3.modules.genome import midpoint
from i3.modules.mind import Mind
from i3.modules.world import World


class BalancedPaidCompactLifeTests(unittest.TestCase):
    def test_three_new_fixed_technical_lives_have_equal_host_and_native_work(self):
        report = E.rehearse()
        print("I3_BALANCED_PAID_COMPACT_LIFE_RESULT="+json.dumps(
            report, sort_keys=True))
        self.assertEqual(report["fixed_engineering_source_seeds"],list(E.SEEDS))
        self.assertEqual(report["engineering_full_lives"],12)
        self.assertEqual(report["chronological_eligible_slots_per_paid_life"],12)
        self.assertEqual(report["all_assigned_slots"]+
                         report["censored_missing_slots"],108)
        self.assertEqual(report["paid_full_trajectory_equal_triplets"],3)
        self.assertEqual(report["first_precharge_action_equal_reference_triplets"],3)
        self.assertTrue(report["counted_host_inference_paths_equal"])
        self.assertTrue(report["real_native_energy_vigilance_debit"])
        self.assertFalse(report["full_cpu_memory_hash_cost_calibrated_to_body"])
        self.assertTrue(report["no_independent_iid_ecology"])
        self.assertFalse(report["stage2_2_go"])
        self.assertEqual(report["scientific_lives"],0)
        self.assertEqual(report["scientific_verdict"],"NOT_ISSUED")
        self.assertEqual(report["matched_observed_priority_lower_sq_loss"]+
                         report["matched_observed_random_lower_sq_loss"]+
                         report["matched_observed_ties"],
                         report["actually_funded_scored_future_first_person_outcomes"]//3)

        for row in report["rows"]:
            self.assertTrue(row["paid_three_arm_full_trajectory_parity"])
            self.assertTrue(row["first_precharge_motor_matches_unpriced_reference"])
            self.assertEqual([arm["mode"] for arm in row["arms"]],list(E.MODES))
            streams=[arm["report"]["slots"] for arm in row["arms"]]
            for stream in streams:
                self.assertEqual([s["assigned_slot"] for s in stream],
                                 list(range(1,len(stream)+1)))
                self.assertEqual([s["actual_step"] for s in stream],
                                 sorted(set(s["actual_step"] for s in stream)))
                for s in stream:
                    if s["status"]=="PAID_AND_SCORED":
                        self.assertTrue(s["prediction_sha256"])
                        self.assertEqual(s["pretraining_predict_calls"],5)
                        self.assertEqual(s["training_updates"],3)
                        self.assertEqual(s["priority_key_visits"],
                                         s["eligible_memories"])
                        self.assertEqual(s["hmac_identity_messages"],
                                         s["eligible_memories"])
                        self.assertTrue(s["posttraining_inference_executed"])
                        self.assertEqual(s["incremental_work"]["cycles"],7)
                        self.assertEqual(s["incremental_work"]["memory_items"],
                                         4*s["eligible_memories"]+6)
                        self.assertEqual(s["incremental_work"]["replays"],3)
                        self.assertGreater(s["energy_paid"],0)
                        self.assertGreater(s["vigilance_paid"],0)
                        self.assertEqual(s["result"]["status"],
                                         "SCORED_ACTUAL_NEXT_BODY")
                        self.assertTrue(s["result"]["factual_executed_action_only"])
                        self.assertFalse(s["result"]["native_unpaid"])
                        self.assertGreaterEqual(s["result"]["squared_loss"],0)
                    else:
                        self.assertEqual(s["status"],"NO_FUNDED_FORECAST")
                        self.assertEqual(s["energy_paid"],0.)
                        self.assertEqual(s["vigilance_paid"],0.)
                        self.assertIsNone(s["prediction_sha256"])
            for triple in zip(*streams):
                self.assertEqual(len(set(s["status"] for s in triple)),1)
                if triple[0]["status"] == "PAID_AND_SCORED":
                    self.assertEqual(len(set(s["result"]["target"] for s in triple)),1)
                    self.assertEqual(len(set(s["energy_paid"] for s in triple)),1)
                    self.assertEqual(len(set(s["vigilance_paid"] for s in triple)),1)
                    self.assertEqual(
                        [s["pretraining_predict_calls"] for s in triple],[5,5,5])

    def test_early_horizon_is_explicit_censor_no_future_readout(self):
        life,receipt=E.run_balanced(midpoint(),dev_open_field(),990050,
                                    "priority",horizon=4)
        self.assertEqual(life["steps_lived"],4)
        self.assertEqual(receipt["eligible_assigned_slots"],0)
        self.assertEqual(receipt["unrealized_terminal_or_horizon_slots"],12)
        self.assertEqual(receipt["scored_actual_next_bodies"],0)
        self.assertEqual(receipt["scientific_lives"],0)

    def test_energy_motor_and_vigilance_refusals_prevent_any_head(self):
        mind=NEG.synthetic_personal_mind(7)
        original=E._source_seal(mind)
        for body,action in (
            ((.10,60.,60.,90.,80.),"attendre"),
            ((2.12,60.,60.,90.,80.),"se_deplacer"),
            ((70.,60.,60.,90.,.10),"attendre")):
            budget=CognitiveBudget(body,BodyLaws())
            witness=E.BalancedPaidWitness(mode="discard",seed=990051)
            with self.subTest(body=body),patch.object(
                    E,"CompactPersonalDistressHead",
                    side_effect=AssertionError("unfunded head attempted")
            ),patch.object(E,"balanced_refit_forecast",
                           side_effect=AssertionError("unfunded learning attempted")):
                witness.after_choice(mind,{"body":body},budget,
                                     action,None,CognitiveWork())
            record=witness.report()
            self.assertEqual(record["unfunded_slots"],1)
            self.assertEqual(record["scored_actual_next_bodies"],0)
            self.assertEqual(record["slots"][0]["status"],"NO_FUNDED_FORECAST")
            self.assertIsNone(record["slots"][0]["pretraining_predict_calls"])
            self.assertEqual(budget.work,CognitiveWork())
            self.assertEqual(E._source_seal(mind),original)

    def test_bad_act_or_tampered_prediction_cannot_rescore(self):
        mind=NEG.synthetic_personal_mind(8)
        body=(70.,60.,50.,90.,80.)
        budget=CognitiveBudget(body,BodyLaws())
        witness=E.BalancedPaidWitness(mode="priority",seed=990052)
        witness.after_choice(mind,{"body":body},budget,
                             "attendre",None,CognitiveWork())
        self.assertIsNotNone(witness.pending)
        with self.assertRaises(RuntimeError):
            witness.report()
        with self.assertRaises(RuntimeError):
            witness.after_choice(mind,{"body":body},budget,
                                 "attendre",None,budget.work)
        e,v=cognitive_cost(BodyLaws(),budget.work)
        class Laws:
            laws=BodyLaws()
        factual={"body":(69.,59.,49.,90.,79.),"dead":(),
                 "cognitive_accounting":{
                     "energy":{"paid":e,"requested":e,"unpaid":0.},
                     "vigilance":{"paid":v,"requested":v,"unpaid":0.}}}
        with self.assertRaises(RuntimeError):
            witness.after_world(Laws(),"boire",None,budget.work,factual)
        self.assertIsNotNone(witness.pending)
        # The inherited observer increments its step counter on every mocked
        # World-return attempt; restore ONLY this synthetic test spy counter
        # so the next exception checks the native bill rather than step order.
        witness.steps = 0
        with self.assertRaisesRegex(RuntimeError, "World did not fully debit"):
            shortfall={
                "body":factual["body"],"dead":(),
                "cognitive_accounting":{
                    "energy":{"paid":e-.01,"requested":e,"unpaid":.01},
                    "vigilance":{"paid":v,"requested":v,"unpaid":0.}}}
            witness.after_world(Laws(),"attendre",None,budget.work,shortfall)
        self.assertIsNotNone(witness.pending)
        witness.steps = 0
        payload,_,_=witness.pending
        payload["forecast"]=999.
        with self.assertRaises(RuntimeError):
            witness.after_world(Laws(),"attendre",None,budget.work,factual)
        self.assertIsNotNone(witness.pending)

    def test_terminal_target_remains_innate_adverse_not_imputed(self):
        mind=NEG.synthetic_personal_mind(9)
        body=(70.,60.,50.,90.,80.)
        budget=CognitiveBudget(body,BodyLaws())
        witness=E.BalancedPaidWitness(mode="discard",seed=990053)
        witness.after_choice(mind,{"body":body},budget,
                             "attendre",None,CognitiveWork())
        e,v=cognitive_cost(BodyLaws(),budget.work)
        class Laws:
            laws=BodyLaws()
        result={"body":(69.,59.,0.,90.,79.),"dead":("zero_water",),
                "cognitive_accounting":{
                    "energy":{"paid":e,"requested":e,"unpaid":0.},
                    "vigilance":{"paid":v,"requested":v,"unpaid":0.}}}
        witness.after_world(Laws(),"attendre",None,budget.work,result)
        receipt=witness.report()
        self.assertEqual(receipt["scored_actual_next_bodies"],1)
        self.assertEqual(receipt["unrealized_terminal_or_horizon_slots"],11)
        self.assertEqual(receipt["slots"][0]["pretraining_predict_calls"],5)
        scored=receipt["slots"][0]["result"]
        self.assertTrue(scored["terminal_observed"])
        self.assertEqual(scored["target"],-mind.d_max)
        self.assertGreater(scored["squared_loss"],0)

    def test_original_methods_restored_even_after_failure(self):
        decide, step = Mind.decide, World.step
        E.run_balanced(midpoint(),dev_open_field(),990050,"random",horizon=4)
        self.assertIs(Mind.decide,decide)
        self.assertIs(World.step,step)
        with patch.object(E,"run_life",side_effect=RuntimeError("lab abort")):
            with self.assertRaises(RuntimeError):
                E.run_balanced(midpoint(),dev_open_field(),
                               990050,"discard",horizon=8)
        self.assertIs(Mind.decide,decide)
        self.assertIs(World.step,step)
        with self.assertRaises(ValueError):
            E.BalancedPaidWitness(mode="not-a-mode",seed=990051)
        with self.assertRaises(ValueError):
            E.BalancedPaidWitness(mode="priority",seed=-1)


if __name__=="__main__":
    unittest.main()
