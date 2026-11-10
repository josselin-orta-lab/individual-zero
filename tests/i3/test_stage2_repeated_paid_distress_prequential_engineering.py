"""Native paid longitudinal, factual first-person forecast engineering tests."""
import json
import unittest
from unittest.mock import patch

from i3.lab import stage2_repeated_paid_distress_prequential_engineering as E
from i3.lab import stage2_replay_predictive_negative_control as NEG
from i3.lab.dev_worlds import dev_open_field
from i3.modules.body import BodyLaws, CognitiveBudget, CognitiveWork, cognitive_cost
from i3.modules.genome import midpoint
from i3.modules.mind import Mind
from i3.modules.world import World


class RepeatedPaidPrequentialTests(unittest.TestCase):
    def test_twelve_chronological_slots_across_three_fixed_sources(self):
        result = E.rehearse()
        print("I3_REPEATED_PAID_PREQUENTIAL_RESULT="+json.dumps(result,sort_keys=True))
        self.assertEqual(result["fixed_engineering_source_units"],3)
        self.assertEqual(result["engineering_full_lives"],12)
        self.assertEqual(result["predeclared_eligible_slots_per_paid_arm"],12)
        self.assertEqual(result["assigned_paid_slots"]+result["censored_missing_slots"],108)
        self.assertEqual(result["paid_triplet_physical_parity"],3)
        self.assertEqual(result["first_choice_reference_parity"],3)
        self.assertEqual(result["scientific_lives"],0)
        self.assertEqual(result["scientific_verdict"],"NOT_ISSUED")
        self.assertFalse(result["stage2_2_go"])
        self.assertFalse(result["calibrated_host_cpu_to_body"])
        self.assertFalse(result["independent_iid_ecology"])
        self.assertEqual(
            result["matched_observed_priority_lower_loss"]+
            result["matched_observed_random_lower_loss"]+
            result["matched_observed_ties"],
            result["actual_scored_first_person_forecasts"]//3)
        for row in result["rows"]:
            self.assertTrue(row["paid_triplet_full_physical_cognition_parity"])
            self.assertEqual([a["mode"] for a in row["arms"]],list(E.MODES))
            sequences=[a["report"]["slots"] for a in row["arms"]]
            for series in sequences:
                self.assertLessEqual(len(series),12)
                self.assertEqual([s["assigned_slot"] for s in series],
                                 list(range(1,len(series)+1)))
                self.assertEqual(
                    [s["actual_step"] for s in series],
                    sorted(set(s["actual_step"] for s in series)))
                for item in series:
                    if item["status"] == "PAID_AND_SCORED":
                        self.assertEqual(item["training_updates"],3)
                        self.assertTrue(item["prediction_sha256"])
                        self.assertEqual(item["incremental_work"]["cycles"],7)
                        self.assertEqual(item["incremental_work"]["replays"],3)
                        self.assertEqual(
                            item["incremental_work"]["memory_items"],
                            4*item["eligible_memories"]+6)
                        self.assertGreater(item["energy_paid"],0.)
                        self.assertGreater(item["vigilance_paid"],0.)
                        self.assertEqual(item["result"]["status"],"SCORED_ACTUAL_NEXT_BODY")
                        self.assertFalse(item["result"]["native_unpaid"])
                        self.assertTrue(item["result"]["factual_executed_action_only"])
                        self.assertGreaterEqual(item["result"]["squared_loss"],0.)
                    else:
                        self.assertEqual(item["status"],"NO_FUNDED_FORECAST")
                        self.assertEqual(item["energy_paid"],0.)
                        self.assertIsNone(item["result"])
            for triple in zip(*sequences):
                self.assertEqual(len(set(s["status"] for s in triple)),1)
                if triple[0]["status"]=="PAID_AND_SCORED":
                    self.assertEqual(len(set(s["result"]["target"] for s in triple)),1)
                    self.assertEqual(len(set(s["energy_paid"] for s in triple)),1)
                    self.assertEqual(len(set(s["vigilance_paid"] for s in triple)),1)

    def test_short_life_retains_unrealized_censor_slots(self):
        life,receipt=E.run_repeated(midpoint(),dev_open_field(),950050,
                                    "priority",horizon=4)
        self.assertEqual(life["steps_lived"],4)
        self.assertEqual(receipt["eligible_assigned_slots"],0)
        self.assertEqual(receipt["unrealized_terminal_or_horizon_slots"],12)
        self.assertEqual(receipt["scored_actual_next_bodies"],0)
        self.assertEqual(receipt["scientific_lives"],0)

    def test_denied_energy_vigilance_motor_never_constructs_head(self):
        source=NEG.synthetic_personal_mind(3)
        for body,action in (
            ((.11,60.,60.,90.,80.),"attendre"),
            ((2.12,60.,60.,90.,80.),"se_deplacer"),
            ((70.,60.,60.,90.,.15),"attendre")):
            b=CognitiveBudget(body,BodyLaws())
            seal=E._source_seal(source)
            witness=E.RepeatedPaidWitness(mode="random",seed=950060)
            with self.subTest(body=body),patch.object(
                    E,"CompactPersonalDistressHead",
                    side_effect=AssertionError("unfunded head constructed")):
                witness.after_choice(source,{"body":body},b,
                                     action,None,CognitiveWork())
            report=witness.report()
            self.assertEqual(report["eligible_assigned_slots"],1)
            self.assertEqual(report["unfunded_slots"],1)
            self.assertEqual(report["scored_actual_next_bodies"],0)
            self.assertEqual(report["slots"][0]["status"],"NO_FUNDED_FORECAST")
            self.assertEqual(b.work,CognitiveWork())
            self.assertEqual(E._source_seal(source),seal)
            self.assertIsNone(witness._head)
            # An unfunded chronological slot remains assigned, never rescored.
            self.assertEqual(report["unrealized_terminal_or_horizon_slots"],11)

    def test_frozen_prediction_never_accepts_mismatched_action_or_modified_sha(self):
        source=NEG.synthetic_personal_mind(8)
        body=(70.,60.,50.,90.,80.)
        b=CognitiveBudget(body,BodyLaws())
        w=E.RepeatedPaidWitness(mode="priority",seed=950070)
        w.after_choice(source,{"body":body},b,"attendre",None,CognitiveWork())
        self.assertIsNotNone(w.pending)
        with self.assertRaises(RuntimeError):
            w.report()
        with self.assertRaises(RuntimeError):
            w.after_choice(source,{"body":body},b,"attendre",None,b.work)
        en,vi=cognitive_cost(BodyLaws(),b.work)
        class Laws:
            laws=BodyLaws()
        result={"body":(69.,59.,49.,90.,79.),"dead":(),
                "cognitive_accounting":{
                    "energy":{"requested":en,"paid":en,"unpaid":0.},
                    "vigilance":{"requested":vi,"paid":vi,"unpaid":0.}}}
        with self.assertRaises(RuntimeError):
            w.after_world(Laws(),"boire",None,b.work,result)
        self.assertIsNotNone(w.pending)
        frozen, digest, expected = w.pending
        frozen["forecast"]=999.
        with self.assertRaises(RuntimeError):
            w.after_world(Laws(),"attendre",None,b.work,result)
        self.assertIsNotNone(w.pending)

    def test_terminal_result_has_original_innate_penalty(self):
        source=NEG.synthetic_personal_mind(9)
        body=(70.,60.,50.,90.,80.)
        b=CognitiveBudget(body,BodyLaws())
        w=E.RepeatedPaidWitness(mode="discard",seed=950080)
        w.after_choice(source,{"body":body},b,"attendre",None,CognitiveWork())
        en,vi=cognitive_cost(BodyLaws(),b.work)
        class Laws:
            laws=BodyLaws()
        result={"body":(69.,59.,0.,90.,79.),"dead":("zero_water",),
                "cognitive_accounting":{
                    "energy":{"requested":en,"paid":en,"unpaid":0.},
                    "vigilance":{"requested":vi,"paid":vi,"unpaid":0.}}}
        w.after_world(Laws(),"attendre",None,b.work,result)
        report=w.report()
        self.assertEqual(report["scored_actual_next_bodies"],1)
        self.assertEqual(report["unrealized_terminal_or_horizon_slots"],11)
        s=report["slots"][0]["result"]
        self.assertTrue(s["terminal_observed"])
        self.assertEqual(s["target"],-source.d_max)
        self.assertGreater(s["squared_loss"],0.)

    def test_reference_source_and_scoped_hooks_are_unchanged(self):
        old_mind,old_world=Mind.decide,World.step
        E.run_repeated(midpoint(),dev_open_field(),950050,"priority",horizon=4)
        self.assertIs(Mind.decide,old_mind)
        self.assertIs(World.step,old_world)
        with patch.object(E,"run_life",side_effect=RuntimeError("engineering abort")):
            with self.assertRaises(RuntimeError):
                E.run_repeated(midpoint(),dev_open_field(),950080,"priority",horizon=8)
        self.assertIs(Mind.decide,old_mind)
        self.assertIs(World.step,old_world)
        with self.assertRaises(ValueError):
            E.RepeatedPaidWitness(mode="unknown",seed=950080)
        with self.assertRaises(ValueError):
            E.RepeatedPaidWitness(mode="priority",seed=-1)


if __name__ == "__main__":
    unittest.main()
