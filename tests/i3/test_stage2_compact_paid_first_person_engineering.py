"""First prospectively sealed compact shadow paid by unchanged native World."""
import json
import unittest
from unittest.mock import patch

from i3.lab import stage2_compact_paid_first_person_engineering as ENG
from i3.lab import stage2_replay_predictive_negative_control as NEG
from i3.lab.dev_worlds import dev_open_field
from i3.modules.body import BodyLaws, CognitiveBudget, CognitiveWork, cognitive_cost
from i3.modules.genome import midpoint
from i3.modules.mind import Mind
from i3.modules.world import World
from i3.lab.stage2_compact_distress_shadow import CompactPersonalDistressHead


class CompactPaidFirstPersonTests(unittest.TestCase):
    def test_new_technical_source_actual_payment_and_matched_triplets(self):
        result = ENG.rehearse()
        print("I3_COMPACT_PAID_FIRST_PERSON_RESULT="+json.dumps(
            result,sort_keys=True))
        self.assertEqual(result["engineering_sources"],3)
        self.assertEqual(result["engineering_actual_full_lives"],12)
        self.assertEqual(result["paid_forecasts_with_actual_next_outcomes"],9)
        self.assertEqual(
            result["paid_triplets_identical_full_physical_and_cognitive_traces"],3)
        self.assertEqual(result["first_precharge_actions_match_reference"],3)
        self.assertFalse(result["host_to_body_tariff_calibrated"])
        self.assertFalse(result["independent_iid_ecology_attested"])
        self.assertFalse(result["stage2_2_go"])
        self.assertEqual(result["scientific_lives"],0)
        self.assertEqual(result["scientific_verdict"],"NOT_ISSUED")
        for row in result["rows"]:
            self.assertEqual([a["mode"] for a in row["paid_arms"]],
                             list(ENG.MODES))
            self.assertTrue(row["all_paid_physical_and_decision_traces_identical"])
            self.assertTrue(row["precharge_motor_matches_unobserved_reference"])
            self.assertGreater(row["actual_body_paid_energy"],0)
            self.assertGreater(row["actual_body_paid_vigilance"],0)
            events=[a["receipt"]["first"] for a in row["paid_arms"]]
            losses=[]
            for item in events:
                self.assertEqual(item["status"],"PAID_AND_SCORED")
                self.assertEqual(item["trained_updates"],3)
                self.assertEqual(item["incremental_work"]["cycles"],7)
                self.assertEqual(item["incremental_work"]["replays"],3)
                self.assertTrue(item["prediction_sha256"])
                outcome=item["result"]
                self.assertEqual(outcome["status"],
                                 "SCORED_ACTUAL_NEXT_FIRST_PERSON_BODY")
                self.assertTrue(outcome["same_factual_selected_motor_command"])
                self.assertFalse(outcome["native_world_unpaid"])
                self.assertGreater(
                    outcome["native_world_paid_energy_full_step"],
                    item["energy_paid"])
                self.assertGreater(
                    outcome["native_world_paid_vigilance_full_step"],
                    item["vigilance_paid"])
                losses.append(outcome["squared_loss"])
            self.assertTrue(all(x>=0 for x in losses))
            self.assertEqual(len(set(
                e["result"]["observed_intrinsic_reward"] for e in events)),1)
            self.assertEqual(len(set(
                e["action_before_funding"] for e in events)),1)

    def test_failed_energy_motor_and_vigilance_never_construct_compact_head(self):
        source=NEG.synthetic_personal_mind(3)
        for body,action in (
            ((0.3,60.,60.,90.,80.),"attendre"),
            ((2.12,60.,60.,90.,80.),"se_deplacer"),
            ((70.,60.,60.,90.,0.05),"attendre"),
        ):
            budget=CognitiveBudget(body,BodyLaws())
            seal=ENG._source_seal(source)
            witness=ENG.CompactPaidFirstPersonWitness(
                mode="priority",seed=940051)
            with self.subTest(body=body),patch.object(
                    ENG,"CompactPersonalDistressHead",
                    side_effect=AssertionError("unfunded computation executed")):
                witness.after_choice(source,{"body":body},budget,
                                     action,None,CognitiveWork())
            self.assertEqual(witness.report()["status"],"NO_FUNDED_FORECAST")
            self.assertEqual(budget.work,CognitiveWork())
            self.assertIsNone(witness._head)
            self.assertEqual(ENG._source_seal(source),seal)
            self.assertEqual(witness.report()["first"]["energy_paid"],0.)
            self.assertIsNone(
                witness.report()["first"]["prediction_sha256"])

    def test_no_history_no_payment_and_invalid_mode_rejected(self):
        mind=Mind(midpoint(),940051)
        body=(75.,65.,60.,90.,70.)
        budget=CognitiveBudget(body,BodyLaws())
        witness=ENG.CompactPaidFirstPersonWitness(mode="discard",seed=940051)
        witness.after_choice(mind,{"body":body},budget,
                             "attendre",None,CognitiveWork())
        self.assertEqual(witness.report()["status"],"NO_ELIGIBLE_HISTORY")
        self.assertEqual(budget.work,CognitiveWork())
        with self.assertRaises(ValueError):
            ENG.CompactPaidFirstPersonWitness(mode="unknown",seed=940051)

    def test_wrong_action_and_tampered_seal_refused_not_rescored(self):
        mind=NEG.synthetic_personal_mind(7)
        body=(70.,60.,50.,90.,80.)
        budget=CognitiveBudget(body,BodyLaws())
        witness=ENG.CompactPaidFirstPersonWitness(mode="random",seed=940052)
        witness.after_choice(mind,{"body":body},budget,
                             "attendre",None,CognitiveWork())
        self.assertIsNotNone(witness.pending)
        with self.assertRaises(RuntimeError):
            witness.report()
        work=budget.work
        e,v=cognitive_cost(BodyLaws(),work)
        original={"body":(69.,59.,49.,90.,79.),"dead":(),
                  "cognitive_accounting":{
                      "energy":{"paid":e,"requested":e,"unpaid":0.},
                      "vigilance":{"paid":v,"requested":v,"unpaid":0.}}}
        class Laws:
            laws=BodyLaws()
        with self.assertRaises(RuntimeError):
            witness.after_world(Laws(),"boire",None,work,original)
        self.assertIsNotNone(witness.pending)
        payload,digest,expected=witness.pending
        payload["frozen_prediction"]=999.
        with self.assertRaises(RuntimeError):
            witness.after_world(Laws(),"attendre",None,work,original)
        self.assertIsNotNone(witness.pending)

    def test_terminal_result_uses_existing_innate_distress_terminal_penalty(self):
        mind=NEG.synthetic_personal_mind(9)
        body=(70.,60.,50.,90.,80.)
        budget=CognitiveBudget(body,BodyLaws())
        witness=ENG.CompactPaidFirstPersonWitness(mode="discard",seed=940053)
        witness.after_choice(mind,{"body":body},budget,
                             "attendre",None,CognitiveWork())
        e,v=cognitive_cost(BodyLaws(),budget.work)
        class Laws:
            laws=BodyLaws()
        result={"body":(69.,59.,0.,90.,79.),"dead":("zero_water",),
                "cognitive_accounting":{
                    "energy":{"requested":e,"paid":e,"unpaid":0.},
                    "vigilance":{"requested":v,"paid":v,"unpaid":0.}}}
        witness.after_world(Laws(),"attendre",None,budget.work,result)
        self.assertEqual(witness.report()["status"],"PAID_AND_SCORED")
        scored=witness.report()["first"]["result"]
        self.assertTrue(scored["terminal_observed"])
        self.assertEqual(scored["observed_intrinsic_reward"],-mind.d_max)
        self.assertGreater(scored["squared_loss"],0)

    def test_engineering_hooks_restored_even_on_exception(self):
        orig_mind,orig_world=Mind.decide,World.step
        ENG.run_paid_compact(midpoint(),dev_open_field(),940041,
                             "priority",12)
        self.assertIs(Mind.decide,orig_mind)
        self.assertIs(World.step,orig_world)
        with patch.object(ENG,"run_life",side_effect=RuntimeError("synthetic failure")):
            with self.assertRaises(RuntimeError):
                ENG.run_paid_compact(midpoint(),dev_open_field(),940055,
                                     "priority",8)
        self.assertIs(Mind.decide,orig_mind)
        self.assertIs(World.step,orig_world)


if __name__=="__main__":
    unittest.main()
