"""Safety, WAL, blinded-world and provenance tests for A2.30-ZB births."""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from run_stage12_issue110_b_a230zb_autonomous_food import (
    experiment,paired_comparison,recipes,birth_effect,
    PROFILES,LAYOUTS,VARIANTS,
)
from lab.stage11_reference_fixture import build_stage11_reference_runtime
from lab.independent_journal_audit import audit_export_bytes


class AutonomousAlternativeFoodBTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory(prefix="a230zb-autonomous-")
        cls.path=Path(cls.tmp.name)/"cohort"
        cls.result=experiment(cls.path)
        cls.lives=cls.result["lives"]

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_all_twelve_independently_born_with_real_bounded_world_steps(self):
        s=self.result
        self.assertEqual(s["schema"],"a230zb-autonomous-alternative-lived-v1")
        self.assertEqual(s["independent_new_I0_births"],12)
        self.assertEqual(s["preregistered_max_world_steps"],384)
        self.assertLessEqual(s["actual_autonomous_world_steps"],384)
        self.assertGreater(s["actual_autonomous_world_steps"],0)
        self.assertEqual(len(self.lives),12)
        self.assertEqual(len({x["birth_id"] for x in self.lives}),12)
        self.assertEqual(len(recipes()),12)
        self.assertEqual(len(s["pairs"]),6)
        self.assertTrue(s["all_WALs_authenticated"])
        self.assertTrue(s["all_actions_autonomous"])
        self.assertTrue(s["no_Oracle_to_I0"])
        self.assertTrue(s["no_safe_B_prior_installed"])
        self.assertFalse(s["operator_stage12_acceptance"])

    def test_each_birth_has_own_verified_WAL_closures_and_no_death_replay(self):
        for life in self.lives:
            self.assertGreater(life["world_steps"],0)
            self.assertLessEqual(life["world_steps"],32)
            self.assertTrue(life["independent_WAL_P48_dual_agency_audits"])
            self.assertTrue(life["birth_id"].startswith("i0:stage12:b:a230zb:"))
            self.assertTrue(life["no_forced_commands"])
            self.assertFalse(life["postterminal_revival"])
            self.assertEqual(
                len(life["executed_motor_commands"]),life["world_steps"]
            )
            self.assertEqual(len(life["journal_head"]),64)
            self.assertEqual(len(life["journal_sha256"]),64)
            filename=(self.path/(
                life["profile"]+"-"+life["layout"]+"-"+
                life["hidden_B_external_only"])/"canonical.jsonl")
            self.assertTrue(filename.is_file())
            audit=audit_export_bytes(
                filename.read_bytes(),expected_head=life["journal_head"],
                expected_count=life["journal_count"],
            )
            self.assertEqual(audit.world_steps_closed,life["world_steps"])

    def test_resource_presence_is_perceptible_only_in_intended_layout(self):
        for life in self.lives:
            root=life["initial_accessible_projection"]
            east=next(x for x in root["adjacent"] if x["direction"]=="east")
            layout=life["layout"]
            self.assertEqual("berry_b" in root["current_resources"],
                             layout=="B_LOCAL")
            self.assertEqual("berry_b" in east["resources"],
                             layout=="B_EAST")
            self.assertFalse(life["hidden_B_external_only"] in root)
            self.assertIsNone(root.get("berry_b_integrity_delta"))
            self.assertEqual(len(root["adjacent"]),4)
            if layout=="B_EAST":
                self.assertTrue(east["passable"])

    def test_hidden_b_berry_is_not_in_prebirth_equipment(self):
        for life in self.lives:
            self.assertEqual(len(life["equipment_sha256_A_only"]),64)
            self.assertFalse(life["birth_id"]==life["equipment_sha256_A_only"])
        self.assertEqual(self.result["initial_same_accessible_pairs"],6)
        pairs=paired_comparison(self.lives)
        self.assertEqual(len(pairs),6)
        for pair in pairs:
            self.assertTrue(pair["first_person_at_birth_equal"])
            self.assertTrue(pair["births_are_distinct_not_same_individual"])

    def test_berry_absent_cannot_physically_be_eaten(self):
        for life in self.lives:
            if life["layout"]=="B_NONE":
                self.assertFalse(life["confirmed_B_ingestions"])
            for e in life["confirmed_B_ingestions"]:
                self.assertTrue(e["food_after"] is not None)
                self.assertTrue(e["integrity_after"] is not None)
                self.assertGreaterEqual(e["step"],1)

    def test_stage6_plans_distinct_from_executed_eats_and_uc_really_lived(self):
        for life in self.lives:
            self.assertIsInstance(life["stage6_status_counts"],dict)
            self.assertIsInstance(life["lived_UC_refusals"],dict)
            self.assertGreaterEqual(life["stage6_available_root_edge_attempts"],0)
            self.assertGreaterEqual(life["stage6_no_known_root_searches"],0)
            for act in life["experienced_B_commands_with_motives"]:
                self.assertEqual(type(act["step"]),int)
                self.assertIn(act["primitive"],("collecter","manger"))
        self.assertEqual(
            self.result["B_ingestions_physically_confirmed"],
            sum(len(x["confirmed_B_ingestions"]) for x in self.lives),
        )

    def test_latent_berry_effect_does_not_change_initial_perception(self):
        grouped={}
        for x in self.lives:
            grouped.setdefault((x["profile"],x["layout"]),[]).append(x)
        self.assertEqual(len(grouped),6)
        for group in grouped.values():
            self.assertEqual(len(group),2)
            self.assertEqual(
                group[0]["initial_accessible_projection"],
                group[1]["initial_accessible_projection"],
            )
            self.assertEqual(
                group[0]["equipment_sha256_A_only"],
                group[1]["equipment_sha256_A_only"],
            )
            self.assertNotEqual(
                group[0]["world_birth_configuration_external"][
                    "config_sha256_external"],
                group[1]["world_birth_configuration_external"][
                    "config_sha256_external"],
            )

    def test_born_world_effects_are_configured_only_in_physics(self):
        s11=build_stage11_reference_runtime(
            enable_geography=True,autonomous_mortal=True,
        )
        config=s11.world.config
        layout=s11.world._layout
        physical=[]
        for var in VARIANTS:
            result,changed=birth_effect(config,layout,"B_LOCAL",var)
            physical.append(result)
            self.assertTrue(any(k=="berry_b" for _,k,_ in changed.resources))
            self.assertEqual(result.berry_effects["berry_b"].food_gain,30.0)
        self.assertEqual(
            tuple(round(x.berry_effects["berry_b"].integrity_delta)
                  for x in physical),(0,-100),
        )

    def test_corrupt_equipment_provenance_breaks_blind_pair(self):
        fake=deepcopy(self.lives)
        target=next(x for x in fake if x["hidden_B_external_only"]=="benign")
        target["equipment_sha256_A_only"]="0"*64
        with self.assertRaisesRegex(ValueError,"Equipment"):
            paired_comparison(fake)

    def test_hidden_safety_forged_in_lived_input_breaks_pair(self):
        fake=deepcopy(self.lives)
        fake[0]["initial_accessible_projection"]["berry_b_safe"]=True
        with self.assertRaisesRegex(ValueError,"first-person"):
            paired_comparison(fake)

    def test_remove_one_birth_from_factorial_matrix_breaks_pair(self):
        fake=deepcopy(self.lives)
        fake.pop()
        with self.assertRaisesRegex(ValueError,"missing B"):
            paired_comparison(fake)

    def test_no_unsafe_production_model_or_i0_commands_were_injected(self):
        source=(Path(__file__).resolve().parents[1]/
                "scripts/run_stage12_issue110_b_a230zb_autonomous_food.py"
               ).read_text()
        self.assertNotIn("life.stage3.control.dispatch(",source)
        self.assertNotIn("life.stage3.world.apply(",source)
        self.assertNotIn("set_body",source)
        self.assertNotIn("from lab.oracle import",source)
        self.assertNotIn("def install_prediction(",source)


if __name__=="__main__":
    unittest.main()
