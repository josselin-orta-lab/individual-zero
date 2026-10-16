"""A2.30-ZO: archived physical and hidden-hazard falsification controls.

Tests exclusively read ONE original CI experiment. Never run the 120-world
physical experiment again as if a second independent cohort existed.
"""
from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from run_stage12_issue110_b_a230zo_factorized_heldout import (
    ACTIONS,BOUNDARY_N,DELTA_KEYS,HIDDEN_N,NOMINAL_N,TRAIN_N,
    VISIBLE_KEYS,body_delta,digest,fit_partial_empirical,partial_forecast,
    registered_recipes,review_results,
)


class PreregisteredFactorizedHeldoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        src=Path(os.environ["A230ZO_ORIGINAL_SOURCE"])
        cls.training=json.loads(
            (src/"a230zo-physical-training.json").read_text()
        )
        cls.model_archive=json.loads(
            (src/"a230zo-frozen-partial-model.json").read_text()
        )
        cls.model=cls.model_archive["model"]
        cls.heldout=json.loads(
            (src/"a230zo-original-heldout-worlds.json").read_text()
        )
        cls.scores=json.loads(
            (src/"a230zo-prospective-scores.json").read_text()
        )
        cls.summary=json.loads(
            (src/"a230zo-summary.json").read_text()
        )

    def audit(self,training=None,heldout=None,model=None,scores=None):
        return review_results(
            deepcopy(self.training if training is None else training),
            deepcopy(self.heldout if heldout is None else heldout),
            deepcopy(self.model if model is None else model),
            deepcopy(self.scores if scores is None else scores),
        )

    def test_all_original_physical_cohorts_and_counts(self):
        s=self.audit()
        self.assertEqual(s["original_physical_worlds"],120)
        self.assertEqual(s["physical_actions_applied"],120)
        self.assertEqual(s["independent_training_worlds"],16)
        self.assertEqual(s["nominal_heldout_worlds"],64)
        self.assertEqual(s["hidden_intervention_worlds"],24)
        self.assertEqual(s["clamp_boundary_worlds"],16)
        self.assertEqual(s["exact_fullstate_heldout_keys_known"],0)
        self.assertEqual(s["nominal_six_component_physically_exact"],64)
        self.assertEqual(s["nominal_partial_predictions_emitted"],64)
        self.assertEqual(s["hazard_hidden_motor_deaths"],4)
        self.assertEqual(s["hazard_hidden_integrity_injuries"],8)
        self.assertEqual(s["hazard_forced_primitive_failures"],8)
        self.assertEqual(s["boundary_abstentions"],16)
        self.assertEqual(s["nominal_hidden_berry_twins_with_identical_observations"],32)
        self.assertEqual(s["new_I0_births"],0)
        self.assertEqual(s["new_I0_autonomous_steps"],0)
        self.assertFalse(s["I0_UC_measured"])
        self.assertFalse(s["Stage6_fullstate_equipment_promoted"])
        self.assertFalse(s["Stage12_operator_ready_proven"])

    def test_original_manifest_is_preregistered_and_unique(self):
        train,nominal,hazards,boundaries=registered_recipes()
        self.assertEqual([len(t) for t in (
            train,nominal,hazards,boundaries
        )],[16,64,24,16])
        full=train+nominal+hazards+boundaries
        self.assertEqual(len({r["world_id"] for r in full}),120)
        self.assertEqual(
            {r["world_id"] for r in full},
            {r["world_id"] for r in self.training+self.heldout},
        )

    def test_training_model_is_frozen_from_training_only(self):
        self.assertEqual(fit_partial_empirical(self.training),self.model)
        self.assertEqual(self.model_archive["model_sha256"],digest(self.model))
        self.assertTrue(self.model_archive[
            "model_has_no_production_equipment_contract"
        ])
        for command,record in self.model.items():
            self.assertEqual(record["physically_observed_training_examples"],8)
            self.assertEqual(set(record["supported_empirical_deltas"]),set(DELTA_KEYS))
            self.assertFalse(record["general_safety_claim"])
            self.assertIsNone(record["unresolved_integrity"])
            self.assertIsNone(record["unresolved_terminality"])
            self.assertIsNone(record["unresolved_new_adjacency"])
            self.assertIsNone(record["unresolved_food_safety"])

    def test_train_deltas_are_physically_measured_not_hidden_cause(self):
        for x in self.training:
            delta=body_delta(
                x["preaction_first_person"],x["postaction_external_only"]
            )
            self.assertEqual(
                delta,self.model[x["command_label"]]["supported_empirical_deltas"]
            )

    def test_no_hazard_or_fullstate_prediction_on_any_heldout_case(self):
        for x,y in zip(self.heldout,self.scores):
            p=y["frozen_empirical_prediction"]
            self.assertEqual(set(p),{
                "status","estimated","integrity","terminal",
                "next_adjacency","safe",
            })
            self.assertIsNone(p["integrity"])
            self.assertIsNone(p["terminal"])
            self.assertIsNone(p["next_adjacency"])
            self.assertIsNone(p["safe"])
            self.assertTrue(y["no_hazard_or_safe_inferred"])
            self.assertIsNone(x["postdeath_lived_capture"])
            self.assertTrue(x["no_i0_birth_or_autonomous_step"])
            self.assertIsNone(x["actual_i0_uc_measured"])

    def test_boundary_clamp_causes_abstention_without_negative_body(self):
        for x,y in zip(self.heldout,self.scores):
            if x["preregistered_cohort"]=="BOUNDARY":
                self.assertEqual(y["frozen_empirical_prediction"]["status"],
                                 "abstain_clamp")
                self.assertIsNone(y["frozen_empirical_prediction"]["estimated"])
                for v in ("energy","food","water"):
                    self.assertGreaterEqual(x["postaction_external_only"]["body"][v],0)

    def test_hidden_lethal_motor_deaths_have_no_lived_after_state(self):
        doomed=[x for x in self.heldout
                if x["physically_terminal_external_only"]]
        self.assertEqual(len(doomed),4)
        for x in doomed:
            self.assertEqual(x["command_label"],"MOVE_E")
            self.assertEqual(x["hidden_intervention_external_only"],
                             "hidden_lethal_east")
            self.assertTrue(x["world_sealed_on_terminal"])
            self.assertIsNone(x["postdeath_lived_capture"])

    def test_latent_berry_effect_is_not_a_non_ingestive_safe_signal(self):
        groups={}
        for x,y in zip(self.heldout,self.scores):
            if x["preregistered_cohort"]=="NOMINAL":
                key=(tuple(x["position_factor_external"]),
                     tuple(x["body_factor_external"]),
                     x["phase_factor_external"],x["command_label"])
                groups.setdefault(key,[]).append((x,y))
        self.assertEqual(len(groups),32)
        for pair in groups.values():
            self.assertEqual(len(pair),2)
            a,b=pair
            self.assertEqual(a[0]["preaction_first_person"],
                             b[0]["preaction_first_person"])
            self.assertEqual(a[1]["frozen_empirical_prediction"],
                             b[1]["frozen_empirical_prediction"])
            self.assertEqual(a[0]["postaction_external_only"],
                             b[0]["postaction_external_only"])

    def test_future_hidden_feature_as_model_input_rejected(self):
        fake=deepcopy(self.heldout)
        fake[0]["preaction_first_person"]["hidden_lethal_zone"]=False
        with self.assertRaises(ValueError):
            self.audit(heldout=fake)

    def test_forged_training_source_hash_rejected(self):
        fake=deepcopy(self.training)
        fake[0]["physical_example_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"tampered|unsafe"):
            self.audit(training=fake)

    def test_forged_safe_and_terminal_clearance_rejected(self):
        for k,value in (("safe",True),("terminal",False),
                        ("integrity",100),("next_adjacency",[])):
            changed=deepcopy(self.scores)
            changed[0]["frozen_empirical_prediction"][k]=value
            with self.assertRaisesRegex(ValueError,"safety|terminal"):
                self.audit(scores=changed)

    def test_perceived_berry_B_without_current_visible_resource_abstains(self):
        raw=deepcopy(self.heldout[0]["preaction_first_person"])
        raw["current_resources"]=[]
        estimate=partial_forecast(self.model,raw,"COLLECT_B")
        self.assertEqual(estimate["status"],"abstain_ineligible")
        self.assertIsNone(estimate["estimated"])

    def test_visible_east_obstacle_vetoes_motor_prediction(self):
        raw=deepcopy(self.heldout[0]["preaction_first_person"])
        for n in raw["adjacent"]:
            if n["direction"]=="east":
                n["passable"]=False
        estimate=partial_forecast(self.model,raw,"MOVE_E")
        self.assertEqual(estimate["status"],"abstain_ineligible")

    def test_heldout_data_cannot_be_used_to_fit_source_model(self):
        fake=deepcopy(self.training)
        fake[0]=deepcopy(self.heldout[0])
        with self.assertRaisesRegex(ValueError,"heldout"):
            fit_partial_empirical(fake)

    def test_forged_success_of_hidden_failed_action_is_detected(self):
        fake=deepcopy(self.scores)
        idx=next(i for i,x in enumerate(self.heldout)
                 if x["hidden_intervention_external_only"]==
                 "hidden_forced_action_failure")
        fake[idx]["all_six_components_match_external_only"]=True
        with self.assertRaisesRegex(ValueError,"heldout scoring"):
            self.audit(scores=fake)

    def test_forged_postmortem_lived_capture_is_rejected(self):
        fake=deepcopy(self.heldout)
        x=next(x for x in fake if x["physically_terminal_external_only"])
        x["postdeath_lived_capture"]=x["postaction_external_only"]
        with self.assertRaisesRegex(ValueError,"unsafe"):
            self.audit(heldout=fake)

    def test_duplicate_world_hidden_in_cohort_is_rejected(self):
        fake=deepcopy(self.heldout)
        fake[1]["world_id"]=fake[0]["world_id"]
        with self.assertRaisesRegex(ValueError,"missing/duplicated"):
            self.audit(heldout=fake)

    def test_berry_B_ingestion_in_physical_receipt_is_rejected(self):
        fake=deepcopy(self.heldout)
        fake[0]["physical_example"]["command"]={
            "primitive":"manger","parameters":{"target":"berry_b"}
        }
        with self.assertRaises(ValueError):
            self.audit(heldout=fake)

    def test_fraudulent_lived_I0_UC_cost_rejected(self):
        fake=deepcopy(self.heldout)
        fake[0]["actual_i0_uc_measured"]=1
        with self.assertRaisesRegex(ValueError,"unsafe"):
            self.audit(heldout=fake)

    def test_runner_cannot_construct_living_stage12_or_oracle(self):
        source=(Path(__file__).resolve().parents[1]/
                "scripts/run_stage12_issue110_b_a230zo_factorized_heldout.py"
               ).read_text()
        self.assertNotIn("Stage12Runtime(",source)
        self.assertNotIn("I0Runtime(",source)
        self.assertNotIn("Oracle(",source)
        self.assertNotIn("life.run_step(",source)
        self.assertNotIn("safe=True",source)
        self.assertNotIn("def learn_from_oracle(",source)


if __name__=="__main__":
    unittest.main()
