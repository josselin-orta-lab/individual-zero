"""A2.30-ZN: 20 adversarial checks of the independent sealed ZM auditor.

NEVER runs any new WorldBody state, SimulatorPlanner or I0. The original
GitHub Actions archived experiments remain read-only.
"""
from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from audit_stage12_issue110_b_a230zn_independent_reentry import (
    ORIGINAL_CANONICAL_WORLDS_SHA, ORIGINAL_CODE_SHA,
    audit_all,audit_world,digest,key,sealed_source,visible,
    EAST,PATH,
)


class SealedIndependentFirstPersonReentryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.one=Path(os.environ["A230ZN_ORIGINAL_ZM_311"])
        cls.two=Path(os.environ["A230ZN_ORIGINAL_ZM_312"])
        cls.worlds,cls.header,cls.raw_sha=sealed_source(cls.one,cls.two)

    def check_one(self,modifier,match=None):
        modified=deepcopy(self.worlds)
        target=next(x for x in modified if modifier["predicate"](x))
        modifier["change"](target)
        if match is not None:
            with self.assertRaisesRegex(ValueError,match):
                audit_world(target)
        else:
            with self.assertRaises(ValueError):
                audit_world(target)

    def test_original_six_factor_worlds_and_real_stage6_diagnostics(self):
        r=audit_all(self.worlds,self.header)
        self.assertEqual(r["original_physical_worlds_checked"],64)
        self.assertEqual(r["original_motor_receipts_verified"],260)
        self.assertEqual(r["independent_root_search_counts_reconstructed"],64)
        self.assertEqual(r["full_firstperson_reentries"],4)
        self.assertEqual(r["only_spatial_site_reentries"],60)
        self.assertEqual(r["one_step_spatial_plans_supported"],4)
        self.assertEqual(r["incomplete_model_supported"],60)
        self.assertEqual(r["night_context_only_prevented_reuse"],4)
        self.assertEqual(r["actual_fifth_motor_outcomes_rechecked"],4)
        self.assertEqual(r["new_physical_worlds"],0)
        self.assertEqual(r["new_I0_births"],0)
        self.assertFalse(r["true_I0_UC_measured"])
        self.assertFalse(r["model_safe_motor_generalization_proven"])

    def test_original_two_python_artifacts_byte_equal_and_source_frozen(self):
        self.assertEqual(len(self.worlds),64)
        self.assertEqual(digest(self.worlds),ORIGINAL_CANONICAL_WORLDS_SHA)
        self.assertEqual(self.header["code_sha"],ORIGINAL_CODE_SHA)
        self.assertEqual(set(self.raw_sha),{
            "a230zm-physical-loop-worlds.json","a230zm-summary.json"
        })
        self.assertTrue(all(len(x)==64 for x in self.raw_sha.values()))

    def test_every_reentered_state_has_true_physical_fifth_outcome(self):
        positive=[w for w in self.worlds if w["full_firstperson_state_reentered"]]
        self.assertEqual(len(positive),4)
        self.assertTrue(all(audit_world(w)[
            "fifth_act_reproduced_prediction"] for w in positive))
        self.assertTrue(all(w["planner_stage6_shadow"][
            "commands"]==[EAST] for w in positive))

    def test_original_archive_mutated_byte_rejected(self):
        with tempfile.TemporaryDirectory(prefix="a230zn-falsify-") as tmp:
            folder=Path(tmp)
            for name in ("a230zm-summary.json","a230zm-physical-loop-worlds.json"):
                source=next(self.one.rglob(name)).read_bytes()
                (folder/name).write_bytes(
                    source+b"\n" if name=="a230zm-summary.json" else source
                )
            # All files exist. The single altered raw byte must fail parity.
            with self.assertRaisesRegex(ValueError,"not byte-identical"):
                sealed_source(folder,self.two)

    def test_altered_full_cohort_hash_rejected_before_scoring(self):
        worlds=deepcopy(self.worlds)
        worlds[0]["factor_movement_energy_cost"]=99.0
        with self.assertRaisesRegex(ValueError,"locked physical"):
            audit_all(worlds,self.header)

    def test_duplicate_factor_world_rejected(self):
        worlds=deepcopy(self.worlds)
        worlds[1]=deepcopy(worlds[0])
        with self.assertRaisesRegex(ValueError,"locked physical"):
            audit_all(worlds,self.header)

    def test_spatial_only_equality_is_refused(self):
        self.check_one({
            "predicate":lambda w:w["factor_movement_energy_cost"]>0.0,
            "change":lambda w:w.update(full_firstperson_state_reentered=True),
        },"same geographic coordinates")

    def test_fake_body_energy_no_decay_cannot_make_key_known(self):
        self.check_one({
            "predicate":lambda w:w["factor_movement_energy_cost"]>0.0,
            "change":lambda w:w["returned_firstperson"]["body"].update(energy=50.0),
        },"root/body")

    def test_water_decay_hidden_by_plan_refused(self):
        self.check_one({
            "predicate":lambda w:w["factor_water_decay"]>0.0,
            "change":lambda w:w["body_deltas_after_four_steps"].update(water=0.0),
        },"metabolic drift")

    def test_food_decay_hidden_by_plan_refused(self):
        self.check_one({
            "predicate":lambda w:w["factor_food_decay"]>0.0,
            "change":lambda w:w["body_deltas_after_four_steps"].update(food=0.0),
        },"metabolic drift")

    def test_forged_day_night_reentry_refused(self):
        self.check_one({
            "predicate":lambda w:w["factor_night_start"]==3,
            "change":lambda w:w["returned_firstperson"].update(is_night=False),
        },"root/body")

    def test_forged_adjacent_resource_without_world_control_refused(self):
        self.check_one({
            "predicate":lambda w:not w["factor_berry_B_local_visible"],
            "change":lambda w:w["all_four_physical_movements"][0][
                "physical_example"]["state"]["current_resources"].append("berry_b"),
        })

    def test_invalid_motor_physical_example_sha_refused(self):
        self.check_one({
            "predicate":lambda w:True,
            "change":lambda w:w["all_four_physical_movements"][0].update(
                physical_example_sha256="0"*64
            ),
        },"physical receipt SHA")

    def test_foreign_world_physical_transition_refused(self):
        self.check_one({
            "predicate":lambda w:True,
            "change":lambda w:w["all_four_physical_movements"][0].update(
                source_world="a230zm:another-individual"
            ),
        },"physical receipt SHA")

    def test_mortality_forged_as_lived_sense_refused(self):
        self.check_one({
            "predicate":lambda w:True,
            "change":lambda w:w["all_four_physical_movements"][1][
                "physical_example"].update(terminal=True),
        },"physical receipt SHA")

    def test_fifth_future_action_cannot_leak_into_prior_training(self):
        self.check_one({
            "predicate":lambda w:w["full_firstperson_state_reentered"],
            "change":lambda w:w["all_four_physical_movements"].append(
                deepcopy(w["all_four_physical_movements"][0])
            ),
        },"four real physical examples")

    def test_forged_stage6_predictable_edge_with_metabolic_drift_refused(self):
        self.check_one({
            "predicate":lambda w: not w["full_firstperson_state_reentered"],
            "change":lambda w:w["planner_stage6_shadow"].update(
                status="plan_found",root_available_edges=1,
                commands=[EAST]
            ),
        },"root diagnostics|body/night drift|exact-root")

    def test_forged_goal_food_propagation_refused(self):
        self.check_one({
            "predicate":lambda w:True,
            "change":lambda w:w["planner_stage6_shadow"].update(
                not_a_food_goal=False
            ),
        },"Stage6 root diagnostics")

    def test_fake_berry_b_ingestion_refused(self):
        self.check_one({
            "predicate":lambda w:True,
            "change":lambda w:w.update(no_berry_B_ingestion=False),
        },"root/body/agency")

    def test_forged_proven_safe_model_refused(self):
        self.check_one({
            "predicate":lambda w:True,
            "change":lambda w:w.update(model_certifies_safety=True),
        },"root/body/agency")

    def test_forged_lived_uc_and_real_i0_birth_refused(self):
        for field,value in (("real_i0_UC_cost_measured",True),
                            ("actual_i0_births",1)):
            self.check_one({
                "predicate":lambda w:True,
                "change":lambda w,wf=field,v=value:w.update({wf:v}),
            },"root/body/agency")

    def test_stage6_shadow_act_executed_refused(self):
        self.check_one({
            "predicate":lambda w:True,
            "change":lambda w:w["planner_stage6_shadow"].update(
                no_shadow_action_dispatched=False
            ),
        },"Stage6 root diagnostics")

    def test_fifth_physical_output_mismatch_refused(self):
        self.check_one({
            "predicate":lambda w:w["full_firstperson_state_reentered"],
            "change":lambda w:w["precommitted_fifth_positive_physical_control"][
                "predicted_next_state"]["body"].update(energy=12.0),
        },"fifth physical move")

    def test_no_physics_planner_or_model_import_in_separate_review(self):
        source=(Path(__file__).resolve().parents[1]/
                "scripts/audit_stage12_issue110_b_a230zn_independent_reentry.py"
        ).read_text()
        for forbidden in (
            "from run_stage12_issue110_b_a230zm_exact_reentry import",
            "from lab.world import",
            "from i0.equipment import",
            "SimulatorPlanner(", "WorldBody(", "Stage12Runtime(",
            "Oracle(", "EquipmentCorpusRecorder(",
        ):
            self.assertNotIn(forbidden,source)


if __name__=="__main__":
    unittest.main()
