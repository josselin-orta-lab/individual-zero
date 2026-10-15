"""Falsification controls for derived food decision identifiability A2.30-V.

Reads ONLY immutable original Actions archives; no new physical worlds, I0
births, Oracle, SimulatorPlanner or producer runner.
"""
from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from audit_stage12_issue110_b_a230v_decision_equivalence import (
    audit_all, audit_food, audit_observable, audit_causal, load_pair,
)


class FirstPersonFoodDecisionCertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        def get(kind):
            return load_pair(
                kind,Path(os.environ["A230V_"+kind.upper()+"_311"]),
                Path(os.environ["A230V_"+kind.upper()+"_312"]),
            )
        cls.original_food=get("food")
        cls.original_observable=get("observable")
        cls.original_causal=get("causal")

    def food(self,worlds=None,pairs=None,summary=None):
        original=self.original_food
        return audit_food(
            deepcopy(worlds if worlds is not None else original["a230t-worlds.json"]),
            deepcopy(pairs if pairs is not None else original["a230t-paired.json"]),
            deepcopy(summary if summary is not None else original["a230t-summary.json"]),
        )

    def test_finite_policy_certificate_on_original_physics(self):
        result=audit_all(
            self.original_observable,self.original_food,self.original_causal
        )
        proof=result["food_decision"]
        self.assertEqual(proof["observational_equivalence_classes"],8)
        self.assertEqual(proof["contradictory_success_and_terminal_classes"],8)
        self.assertEqual(proof["tested_deterministic_policies"],256)
        self.assertEqual(proof["policies_with_zero_terminal_worlds"],1)
        self.assertEqual(
            proof["policies_with_zero_terminal_and_positive_food_goal"],0
        )
        self.assertEqual(proof["max_food_goal_worlds_if_zero_terminal"],0)
        self.assertEqual(proof["max_food_goal_worlds_if_all_classes_committed"],24)
        self.assertEqual(proof["terminal_worlds_if_all_classes_committed"],8)
        self.assertEqual(proof["insufficient_worlds_if_all_classes_committed"],8)
        self.assertEqual(
            proof["wait_predecision_total_physical_cost_across_20_pairs"],
            {"energy":-10.0,"food":-10.0,"water":-4.0},
        )
        self.assertTrue(proof["latent_physics_ever_used_in_decision_features"] is False)
        self.assertIsNone(proof["calibrated_death_probability"])
        self.assertEqual(result["new_physical_worlds"],0)
        self.assertEqual(result["new_i0_births"],0)
        self.assertFalse(result["uc_policy_inference_supported"])
        self.assertFalse(result["safety_of_alternative_food_plans_proven"])
        self.assertEqual(result["cognitive_deployment"],"NO-GO")

    def test_falsify_unknown_latent_feature_in_decision(self):
        worlds=deepcopy(self.original_food["a230t-worlds.json"])
        worlds[0]["decision_stage3_state"]["latent_external_only"]="benign"
        with self.assertRaisesRegex(ValueError,"observation contains"):
            self.food(worlds=worlds)

    def test_falsify_future_outcome_as_early_input(self):
        worlds=deepcopy(self.original_food["a230t-worlds.json"])
        original=worlds[0]["potential_lived_post_ingestion_if_survivor"]
        worlds[0]["decision_stage3_state"]=deepcopy(original)
        with self.assertRaisesRegex(ValueError,"future leakage"):
            self.food(worlds=worlds)

    def test_delete_one_hidden_variant_breaks_equivalence(self):
        worlds=deepcopy(self.original_food["a230t-worlds.json"])
        worlds[0]["latent_external_only"]="toxin_7"
        with self.assertRaisesRegex(ValueError,"identity|variant"):
            self.food(worlds=worlds)

    def test_duplicate_original_physical_world_fails(self):
        worlds=deepcopy(self.original_food["a230t-worlds.json"])
        worlds[0]["id"]=worlds[1]["id"]
        with self.assertRaisesRegex(ValueError,"duplicated"):
            self.food(worlds=worlds)

    def test_forged_survival_after_lethal_ingestion_fails(self):
        worlds=deepcopy(self.original_food["a230t-worlds.json"])
        lethal=next(x for x in worlds if x["latent_external_only"]=="toxin_100")
        lethal["physically_alive_after_ingestion"]=True
        with self.assertRaisesRegex(ValueError,"goal mislabeled|nonterminal"):
            self.food(worlds=worlds)

    def test_forged_subjective_postdeath_observation_fails(self):
        worlds=deepcopy(self.original_food["a230t-worlds.json"])
        lethal=next(x for x in worlds if x["latent_external_only"]=="toxin_100")
        lethal["potential_lived_post_ingestion_if_survivor"]={
            "fake_first_person_post_terminal":True
        }
        with self.assertRaisesRegex(ValueError,"terminal result"):
            self.food(worlds=worlds)

    def test_forged_shadow_safety_certificate_fails(self):
        worlds=deepcopy(self.original_food["a230t-worlds.json"])
        worlds[0]["shadow_forecast_precommitted"]["certifies_safe"]=True
        with self.assertRaisesRegex(ValueError,"false safety"):
            self.food(worlds=worlds)

    def test_break_precommitted_wait_receipt_fails(self):
        paired=deepcopy(self.original_food["a230t-paired.json"])
        paired[0]["food_cost_waiting_extra"]=0.0
        with self.assertRaisesRegex(ValueError,"time-cost"):
            self.food(pairs=paired)

    def test_biased_summary_deleted_deaths_fails(self):
        summary=deepcopy(self.original_food["a230t-summary.json"])
        summary["new_lab_physical_steps"]=100
        with self.assertRaisesRegex(ValueError,"invalid historical"):
            self.food(summary=summary)

    def test_fake_preexposure_information_in_parallel_S_fails(self):
        pairs=deepcopy(self.original_observable["a230s-pairs.json"])
        pairs[0]["discrimination_before_exposure"]=True
        with self.assertRaisesRegex(ValueError,"backward in time"):
            audit_observable(
                deepcopy(self.original_observable["a230s-worlds.json"]),
                pairs,deepcopy(self.original_observable["a230s-summary.json"]),
            )

    def test_oracular_input_into_parallel_shadow_planner_fails(self):
        worlds=deepcopy(self.original_causal["a230s-acted-worlds.json"])
        worlds[0]["oracle_information_in_cognitive_search"]=True
        with self.assertRaisesRegex(ValueError,"oracle"):
            audit_causal(
                worlds,deepcopy(self.original_causal["a230s-passive-worlds.json"]),
                deepcopy(self.original_causal["a230s-summary.json"]),
            )

    def test_false_known_root_in_parallel_Stage6_shadow_fails(self):
        worlds=deepcopy(self.original_causal["a230s-acted-worlds.json"])
        target=next(w for w in worlds if w["shadow_food"])
        target["shadow_food"][0]["stage6_diagnostic"]["root_available_edges"]=1
        with self.assertRaisesRegex(ValueError,"known first step"):
            audit_causal(
                worlds,deepcopy(self.original_causal["a230s-passive-worlds.json"]),
                deepcopy(self.original_causal["a230s-summary.json"]),
            )

    def test_no_cognitive_or_world_execution_dependencies(self):
        script=(Path(__file__).resolve().parents[1]/
            "scripts/audit_stage12_issue110_b_a230v_decision_equivalence.py"
        ).read_text()
        self.assertNotIn("from lab.world import",script)
        self.assertNotIn("WorldBody(",script)
        self.assertNotIn("SimulatorPlanner(",script)
        self.assertNotIn("import Oracle",script)
        self.assertNotIn("def predict(",script)


if __name__=="__main__":
    unittest.main()
