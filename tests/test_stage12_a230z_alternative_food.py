"""Adversarial and observational regression controls for A2.30-Z."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from run_stage12_issue110_b_a230z_alternative_food import (
    experiment, score_original_worlds, perceptual_food_policy,
    EAST, COLLECT_B, EAT_B, ACCESSIBLE_KEYS,
)


class AccessibleAlternativeFoodExperimentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix="stage12-a230z-")
        cls.output = Path(cls.tmp.name)/"original"
        cls.summary = experiment(cls.output)
        cls.worlds = json.loads(
            (cls.output/"a230z-physical-worlds.json").read_text()
        )
        cls.index = {x["world_id"]:x for x in cls.worlds}

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def score(self,worlds=None):
        return score_original_worlds(deepcopy(
            self.worlds if worlds is None else worlds
        ))

    def test_preregistered_worlds_steps_food_and_deaths(self):
        s=self.score()
        self.assertEqual(s["original_physical_worlds"],168)
        self.assertEqual(s["original_physical_actions"],244)
        self.assertEqual(s["ingestions_of_berry_b"],80)
        self.assertEqual(s["terminal_physical_ingestions"],20)
        self.assertEqual(s["surviving_food_gain_at_least_5"],40)
        self.assertEqual(s["surviving_food_gain_insufficient"],20)
        self.assertEqual(s["abstentions_from_berry_b_ingestion"],88)
        self.assertEqual(s["shadow_queries_actual_Stage6_algorithm"],80)
        self.assertEqual(s["unique_initial_firstperson_hidden_groups"],40)
        self.assertEqual(s["remote_B_truly_unseen_initial_paired_groups"],8)
        self.assertFalse(s["actual_I0_UC_cost_measured"])
        self.assertFalse(s["actual_I0_autonomous_food_achievement_proven"])
        self.assertFalse(s["stage6_production_plan_success_proven"])
        self.assertFalse(s["food_safety_proven"])
        self.assertEqual(s["new_living_I0_births"],0)

    def test_accessible_b_visible_and_direct_obstacle_controls(self):
        for x in self.worlds:
            arm=x["layout_external_only"]
            initially=x["initial_first_person"]
            east=next(n for n in initially["adjacent"]
                      if n["direction"]=="east")
            if arm=="B_LOCAL":
                self.assertIn("berry_b",initially["current_resources"])
                self.assertEqual(x["physical_step_count"],2)
            elif arm=="B_EAST_BLOCKED":
                self.assertNotIn("berry_b",initially["current_resources"])
                self.assertIn("berry_b",east["resources"])
                self.assertFalse(east["passable"])
                self.assertEqual(x["physical_step_count"],0)
            elif arm=="B_EAST_ADJACENT":
                self.assertIn("berry_b",east["resources"])
                self.assertTrue(east["passable"])
                self.assertEqual(x["physical_step_count"],3)
            elif arm=="B_EAST_TWO_STEPS":
                self.assertNotIn("berry_b",initially["current_resources"])
                self.assertNotIn("berry_b",east["resources"])
                self.assertEqual(x["physical_step_count"],(
                    4 if x["protocol_precommitted"]=="SINGLE_EAST_PROBE" else 0
                ))
            else:
                self.assertNotIn("berry_b",initially["current_resources"])
                self.assertNotIn("berry_b",east["resources"])
                self.assertEqual(x["physical_step_count"],(
                    1 if x["protocol_precommitted"]=="SINGLE_EAST_PROBE" else 0
                ))

    def test_hidden_effect_does_not_change_first_person_choices(self):
        groups={}
        for x in self.worlds:
            key=(x["layout_external_only"],x["protocol_precommitted"],
                 x["initial_food"],tuple(x["initial_position"]))
            groups.setdefault(key,[]).append(x)
        self.assertEqual(len(groups),40)
        for group in groups.values():
            preingestion=[]
            for x in group:
                seen=[]
                for choice in x["perceptual_policy_choices"]:
                    seen.append(choice["input_accessible_state"])
                    if choice["command"]==EAT_B.as_dict():
                        break
                preingestion.append(seen)
            self.assertTrue(all(h==preingestion[0] for h in preingestion))
        affected=[
            x for x in self.worlds if x["ingested_berry_b_external"]
        ]
        self.assertEqual(len(affected),80)
        self.assertTrue(all(x["stage6_shadow"] is not None for x in affected))

    def test_returning_from_shadow_does_not_execute_a_plan(self):
        for x in self.worlds:
            self.assertTrue(x["no_stage6_shadow_action_dispatched"])
            self.assertIsNone(x["actual_I0_UC_cost"])
            self.assertFalse(x["certifies_food_safety"])
            self.assertIsNone(x["lived_postterminal_capture"])
            if x["physical_terminal_step_external_only"] is not None:
                self.assertTrue(x["physical_steps_external"][-1][
                    "terminal_external_only"
                ])
                self.assertLessEqual(
                    x["lived_states_while_alive"][-1]["t_monde"],
                    x["physical_terminal_step_external_only"]
                )

    def test_lab_policy_cannot_access_hidden_physics(self):
        visible=deepcopy(self.worlds[0]["initial_first_person"])
        visible["latent_external_only"]="toxin_100"
        with self.assertRaisesRegex(ValueError,"hidden or future"):
            perceptual_food_policy(visible,"OBSERVED_ONLY",())

    def test_ghost_berry_b_not_in_capture_is_rejected(self):
        altered=deepcopy(self.worlds)
        target=next(x for x in altered if
            x["layout_external_only"]=="A_ONLY")
        target["perceptual_policy_choices"][0]["command"]=COLLECT_B.as_dict()
        with self.assertRaisesRegex(ValueError,"pretended to know"):
            self.score(altered)

    def test_blocked_east_move_is_rejected(self):
        altered=deepcopy(self.worlds)
        target=next(x for x in altered if
            x["layout_external_only"]=="B_EAST_BLOCKED")
        target["perceptual_policy_choices"][0]["command"]=EAST.as_dict()
        with self.assertRaisesRegex(ValueError,"pretended to know"):
            self.score(altered)

    def test_latent_leak_into_initial_perception_fails(self):
        altered=deepcopy(self.worlds)
        altered[0]["initial_first_person"]["hidden_food_safety"]=True
        with self.assertRaisesRegex(ValueError,"hidden or future"):
            self.score(altered)

    def test_forged_safety_certificate_rejected(self):
        altered=deepcopy(self.worlds)
        altered[0]["certifies_food_safety"]=True
        with self.assertRaisesRegex(ValueError,"false safety"):
            self.score(altered)

    def test_forged_postterminal_lived_capture_rejected(self):
        altered=deepcopy(self.worlds)
        target=next(x for x in altered if x[
            "physical_terminal_step_external_only"] is not None)
        target["lived_postterminal_capture"]=target[
            "physical_steps_external"][-1]["physical_after_external_only"]
        with self.assertRaisesRegex(ValueError,"postmortem|false safety"):
            self.score(altered)

    def test_tampered_physical_example_hash_rejected(self):
        altered=deepcopy(self.worlds)
        target=next(x for x in altered if x["physical_step_count"]>0)
        target["physical_steps_external"][0]["physical_example_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"physical example"):
            self.score(altered)

    def test_repeated_original_world_identity_rejected(self):
        altered=deepcopy(self.worlds)
        altered[1]["world_id"]=altered[0]["world_id"]
        with self.assertRaisesRegex(ValueError,"duplicate physical world"):
            self.score(altered)

    def test_stage6_shadow_safety_fabrication_rejected(self):
        altered=deepcopy(self.worlds)
        target=next(x for x in altered if x["stage6_shadow"])
        target["stage6_shadow"]["oracle_fed_to_shadow"]=True
        with self.assertRaisesRegex(ValueError,"Stage6 search fed future/Oracle"):
            self.score(altered)

    def test_world_specific_past_not_other_world_in_candidate_shadow(self):
        from run_stage12_issue110_b_a230z_alternative_food import (
            own_past_shadow_search,
        )
        # No access to another individual/corpus through the shadow search.
        from i0.equipment import EquipmentCorpusExample, SimulationState
        target=next(x for x in self.worlds if x["stage6_shadow"])
        shadow=target["stage6_shadow"]
        self.assertEqual(
            len(shadow["own_physical_examples"]),
            shadow["actual_own_history_step_count"]
        )
        self.assertTrue(all(
            x["terminal"] is False
            for x in shadow["own_physical_examples"]
        ))
        self.assertTrue(all(
            x["t_monde"] < shadow["t_monde"]
            for x in target["physical_steps_external"]
            if x["command"]!=EAT_B.as_dict()
        ))

    def test_source_model_not_registered_as_i0_equipment(self):
        source=(Path(__file__).resolve().parents[1]/
               "scripts/run_stage12_issue110_b_a230z_alternative_food.py"
        ).read_text()
        self.assertNotIn("I0Runtime(",source)
        self.assertNotIn("Oracle(",source)
        self.assertNotIn("def infer_hidden_safety(",source)
        self.assertNotIn("def install_model(",source)


if __name__=="__main__":
    unittest.main()
