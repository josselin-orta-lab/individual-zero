"""A2.30-T precommitted laboratory food shadow risk and cost controls."""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from run_stage12_issue110_b_a230t_food_shadow import run


class FrozenShadowFoodPlanningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix="a230t-")
        cls.output=Path(cls.temp.name)/"study"
        cls.summary=run(Path(os.environ["A230T_TRAINING_SOURCE"]),cls.output)
        cls.rows=json.loads((cls.output/"a230t-worlds.json").read_text())
        cls.pairs=json.loads((cls.output/"a230t-paired.json").read_text())

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_pretrained_model_and_physical_disjoint_worlds(self):
        a=self.summary
        self.assertEqual(a["new_independent_lab_worlds"],40)
        self.assertEqual(a["new_lab_physical_steps"],132)
        self.assertEqual(a["external_deaths"],8)
        self.assertEqual(a["new_i0_births"],0)
        self.assertEqual(a["new_autonomous_i0_steps"],0)
        self.assertTrue(a["model_pretrained_and_frozen_before_all_worlds"])
        self.assertTrue(a["shadow_does_not_command_physics"])
        self.assertTrue(a["stage6_command_candidates_only_not_plans"])
        self.assertEqual(len({r["id"] for r in self.rows}),40)
        self.assertEqual(a["per_arm"]["no_wait"]["physical_steps"],56)
        self.assertEqual(a["per_arm"]["wait_first"]["physical_steps"],76)

    def test_observed_terminal_branch_blocks_naive_safe_claim(self):
        self.assertEqual(self.summary["shadow_safety_certificates"],0)
        for row in self.rows:
            s=row["shadow_forecast_precommitted"]
            self.assertEqual(s["observed_joint_branches"],4)
            self.assertEqual(s["risk_label"],"observed_terminal_possible")
            self.assertTrue(s["optimistic_goal_exists"])
            self.assertFalse(s["all_observed_branches_survive_and_meet_goal"])
            self.assertTrue(s["shadow_risk_veto"])
            self.assertFalse(s["certifies_safe"])
            self.assertTrue(s["uncertainty_unobserved_causes_not_excluded"])
            self.assertEqual(s["observed_terminal_steps"],[2])
            self.assertTrue(s["read_only_stage6_candidate_collect_available"])
            self.assertTrue(s["read_only_stage6_candidate_eat_unavailable_before_collect"])

    def test_optimism_is_not_physical_surviving_food_success(self):
        for arm in ("no_wait","wait_first"):
            measure=self.summary["per_arm"][arm]
            self.assertEqual(measure["physical_worlds"],20)
            self.assertEqual(measure["shadow_optimistic_goals"],20)
            self.assertEqual(measure["shadow_observed_branch_robust_goals"],0)
            self.assertEqual(measure["shadow_risk_veto"],20)
            self.assertEqual(measure["physical_surviving_food_goal"],12)
            self.assertEqual(measure["external_terminal_worlds"],4)
            self.assertEqual(measure["optimistic_false_food_success_external"],8)
        for row in self.rows:
            expected = row["latent_external_only"] in (
                "benign","toxin_7","toxin_30"
            )
            self.assertEqual(
                row["physical_food_goal_with_survival_external"], expected
            )
            if row["latent_external_only"]=="toxin_100":
                self.assertIsNone(
                    row["potential_lived_post_ingestion_if_survivor"]
                )
                self.assertFalse(row["physically_alive_after_ingestion"])

    def test_wait_stays_epistemically_uninformative_about_hidden_food(self):
        for arm in ("no_wait","wait_first"):
            for food in (35.0,45.0):
                for pos in ((5,5),(7,7)):
                    subset=[r for r in self.rows if r["arm"]==arm
                            and r["starting_food"]==food
                            and tuple(r["starting_position"])==pos]
                    self.assertEqual(len(subset),5)
                    self.assertEqual(len({
                        r["shadow_forecast_precommitted"]["input_digest_sha256"]
                        for r in subset
                    }),1)
        self.assertEqual(len(self.pairs),20)
        self.assertTrue(all(p["same_initial_perception"] for p in self.pairs))
        self.assertTrue(all(p["same_observed_branch_risk"] for p in self.pairs))
        self.assertTrue(all(
            p["physical_food_goal_no_wait"]
            == p["physical_food_goal_wait_first"]
            for p in self.pairs
        ))
        self.assertEqual(sum(p["terminal_in_both_arms"] for p in self.pairs),4)

    def test_wait_has_real_physical_cost_without_food_safety_gain(self):
        # Independently inspect paired external physical receipts.
        for p in self.pairs:
            first=next(x for x in self.rows if x["id"]==p["no_wait_id"])
            second=next(x for x in self.rows if x["id"]==p["wait_first_id"])
            a=first["physical_operations_not_chosen_by_shadow"][-1]["physical_after"]
            b=second["physical_operations_not_chosen_by_shadow"][-1]["physical_after"]
            self.assertAlmostEqual(
                b["body"]["food"]-a["body"]["food"],-0.5,places=8
            )
            self.assertAlmostEqual(
                b["body"]["energy"]-a["body"]["energy"],-0.5,places=8
            )
            self.assertAlmostEqual(
                b["body"]["water"]-a["body"]["water"],-0.2,places=8
            )

    def test_external_truth_never_in_shadow_forecast_input(self):
        for row in self.rows:
            forecast=row["shadow_forecast_precommitted"]
            self.assertTrue(row["no_command_emitted_to_i0"])
            self.assertTrue(row["no_subj_agency_claim"])
            self.assertNotIn("hidden_latent",forecast)
            self.assertNotIn("risk_certainty",forecast)
            self.assertNotIn("ground_truth",forecast)
            self.assertNotIn("plan_found",forecast)
            self.assertNotIn("terminal",forecast["input_stage3_state"])
            self.assertNotIn("berry_effects",forecast["input_stage3_state"])

    def test_candidate_does_not_implement_equipment_prediction(self):
        path=Path(__file__).resolve().parents[1]/"scripts"/(
            "run_stage12_issue110_b_a230t_food_shadow.py"
        )
        content=path.read_text()
        self.assertNotIn("world.ground_truth(",content)
        self.assertNotIn("Stage12Runtime(",content)
        self.assertNotIn("action_control.dispatch(",content)


if __name__=="__main__":
    unittest.main()
