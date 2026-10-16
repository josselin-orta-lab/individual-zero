"""A2.30-S tests: read-only shadow Stage6 and hidden-cause sensory boundaries."""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from run_stage12_issue110_b_a230s_firstperson_shadow import execute


class FirstPersonControlledExperiments(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix="a230s-")
        cls.path=Path(cls.temp.name)/"exp"
        cls.summary=execute(cls.path)
        cls.acted=json.loads((cls.path/"a230s-acted-worlds.json").read_text())
        cls.controls=json.loads((cls.path/"a230s-passive-worlds.json").read_text())
        cls.by_key={
            (r["kind"],r["variant_lab_only"],r["followup_precommitted"],
             r["initial_food"],tuple(r["initial_position"])):r
            for r in cls.acted
        }

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_preregistered_detached_physical_worlds_and_terminal_mortality(self):
        s=self.summary
        self.assertEqual(s["acted_detached_worlds"],64)
        self.assertEqual(s["passive_observation_only_worlds"],8)
        self.assertEqual(s["independent_lab_world_instances"],72)
        self.assertEqual(s["actual_lab_physical_steps"],196)
        self.assertEqual(s["food_physical_steps"],120)
        self.assertEqual(s["movement_physical_steps"],76)
        self.assertEqual(s["actually_executed_eat_commands"],44)
        self.assertEqual(s["new_I0_births"],0)
        self.assertEqual(s["new_I0_autonomous_steps"],0)
        self.assertTrue(s["no_shadow_commands_physically_executed"])
        self.assertFalse(s["subjective_causal_attribution_demonstrated"])
        ids=[r["id"] for r in self.acted+self.controls]
        self.assertEqual(len(ids),len(set(ids)))
        for row in self.acted:
            steps=row["physical_records"]
            self.assertEqual(len(steps),row["physical_step_count"])
            if row["first_terminal_step"] is not None:
                self.assertTrue(steps[-1]["terminal"])
                self.assertEqual(row["first_terminal_step"],len(steps))
                self.assertFalse(any(x["terminal"] for x in steps[:-1]))
            else:
                self.assertFalse(any(x["terminal"] for x in steps))

    def test_causal_food_ambiguity_is_complete_before_and_after_first_ingestion(self):
        pair=self.summary["comparison"]
        self.assertEqual(pair["paired_food_first_ingestion_same_accessible_input"],8)
        self.assertEqual(pair["paired_food_after_ingestion_identical_accessible_output"],8)
        for food in (40.0,45.0):
            for pos in ((2,2),(4,4)):
                for followup in ("wait","repeat_eat"):
                    mild=self.by_key[("food","toxic_mild",followup,food,pos)]
                    conf=self.by_key[("food","exogenous_confounded",followup,food,pos)]
                    self.assertEqual(mild["physical_records"][2]["state_before"],
                                     conf["physical_records"][2]["state_before"])
                    self.assertEqual(mild["physical_records"][2]["state_after"],
                                     conf["physical_records"][2]["state_after"])
                    self.assertEqual(mild["physical_records"][2]["command"],
                                     conf["physical_records"][2]["command"])
                    self.assertIsNone(mild["hidden_event_changed_capture"])
                    self.assertFalse(conf["hidden_event_changed_capture"])
                    self.assertEqual(len(conf["external_environment_interventions"]),1)
                    self.assertEqual(len(mild["external_environment_interventions"]),0)

    def test_wait_is_discriminating_at_real_bodily_cost_repeat_eat_is_not(self):
        c=self.summary["comparison"]
        self.assertEqual(c["mild_toxin_vs_exogenous_wait_distinguished"],4)
        self.assertEqual(
            c["mild_toxin_vs_exogenous_repeat_eat_still_indistinguishable"],4
        )
        for food in (40.0,45.0):
            for pos in ((2,2),(4,4)):
                a=self.by_key[("food","toxic_mild","wait",food,pos)]
                b=self.by_key[("food","exogenous_confounded","wait",food,pos)]
                self.assertEqual(a["physical_records"][3]["state_after"]["body"]["integrity"],93)
                self.assertEqual(b["physical_records"][3]["state_after"]["body"]["integrity"],86)
                repeat_a=self.by_key[("food","toxic_mild","repeat_eat",food,pos)]
                repeat_b=self.by_key[("food","exogenous_confounded","repeat_eat",food,pos)]
                self.assertEqual(
                    repeat_a["physical_records"][3]["state_after"],
                    repeat_b["physical_records"][3]["state_after"],
                )

    def test_first_lethal_food_contact_forbids_further_learning(self):
        terminal=[
            x for x in self.acted
            if x["kind"]=="food" and x["variant_lab_only"]=="toxic_lethal"
        ]
        self.assertEqual(len(terminal),8)
        self.assertTrue(all(x["first_terminal_step"]==3
                            and len(x["shadow_food"])==1
                            and len(x["physical_records"])==3
                            for x in terminal))
        self.assertEqual(self.summary["shadow_food_after_first_ingestion_queries"],24)

    def test_spatial_risk_observed_after_entry_escaping_only_as_precommitted_control(self):
        c=self.summary["comparison"]
        self.assertEqual(c["movement_paired_equal_first_step_outcomes"],16)
        self.assertEqual(c["hazardous_wait_future_terminal_worlds"],8)
        self.assertEqual(c["paired_precommitted_retreat_survives"],8)
        for food in (40.0,45.0):
            for pos in ((2,2),(4,4)):
                for risk in ("danger_40","danger_55"):
                    waiting=self.by_key[("movement",risk,"wait",food,pos)]
                    escaping=self.by_key[("movement",risk,"escape",food,pos)]
                    self.assertIsNotNone(waiting["first_terminal_step"])
                    self.assertIsNone(escaping["first_terminal_step"])
                    self.assertEqual(waiting["physical_records"][0]["state_after"],
                                     escaping["physical_records"][0]["state_after"])
                    self.assertEqual(escaping["physical_records"][1]["command"]["primitive"],
                                     "se_deplacer")

    def test_visible_local_resource_and_obstacle_require_no_exposure(self):
        self.assertEqual(len(self.controls),8)
        self.assertTrue(all(x["world_steps_applied"]==0 for x in self.controls))
        self.assertTrue(all(x["intended_visible_indicator"]==
                            x["detected_from_accessible_state"]
                            for x in self.controls))
        self.assertEqual(Counter(x["cue_kind"] for x in self.controls),
                         Counter({"food_resource_visible":4,
                                  "movement_obstacle_visible":4}))

    def test_shadow_uses_real_Stage6_and_only_past_accessible_transition_history(self):
        s=self.summary
        self.assertEqual(s["shadow_stage6_queries"],56)
        self.assertEqual(s["shadow_food_before_first_ingestion_queries"],32)
        self.assertEqual(s["shadow_food_after_first_ingestion_queries"],24)
        self.assertTrue(s["shadow_prior_actions_exact_model_not_actual_I0_learning"])
        self.assertEqual(s["body_goal_setpoint"],65.0)
        self.assertEqual(s["shadow_max_depth"],3)
        for row in self.acted:
            for q in row["shadow_food"]:
                self.assertTrue(q["no_shadow_command_dispatched"])
                self.assertTrue(all(p<q["t_query"]
                                    for p in q["previous_observed_steps"]))
                self.assertEqual(q["history_examples_count"],
                                 len(q["previous_observed_steps"]))
                self.assertEqual(q["h_eff"],3)
                self.assertEqual(q["r_eff"],1)
                self.assertIn(q["stage6_status"],(
                    "incomplete_model","partial_progress",
                    "plan_found","not_found_within_horizon",
                ))

    def test_no_original_stage6_or_Stage12_implementation_modified(self):
        code=(Path(__file__).resolve().parents[1]/
              "scripts/run_stage12_issue110_b_a230s_firstperson_shadow.py").read_text()
        self.assertNotIn("import Oracle",code)
        self.assertNotIn("Stage12Runtime(",code)
        self.assertNotIn("Stage4Runtime(",code)
        self.assertNotIn("from lab.stage4_reference_fixture import",code)


if __name__=="__main__":
    unittest.main()
