"""A2.30-ZL independent adversarial checks over sealed original ZK/ZB data.

No physics or planner re-execution: all mutations are on separate in-memory
copies. These are tests of the ZL scorer, not additional scientific worlds.
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
from audit_stage12_issue110_b_a230zl_ownworld_sealed import (
    B_COLLECT, B_EAT, MOVE_E, ZK_DIGESTS, ZB_DIGESTS,
    digest, exact_dictionary, immutable_sources, independent_audit,
    sealed_read,
)


class IndependentOwnWorldArchiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.roots={
            "zk311":Path(os.environ["A230ZL_ZK311"]),
            "zk312":Path(os.environ["A230ZL_ZK312"]),
            "zb311":Path(os.environ["A230ZL_ZB311"]),
            "zb312":Path(os.environ["A230ZL_ZB312"]),
        }
        cls.original=immutable_sources(*(
            cls.roots[x] for x in ("zk311","zk312","zb311","zb312")
        ))

    def evaluate(self, data=None):
        return independent_audit(*(deepcopy(x) for x in
            (self.original if data is None else data)))

    def test_preregistered_physical_and_exact_key_counts(self):
        s=self.evaluate()
        self.assertEqual(s["physical_training_worlds_ZK_verified_from_receipts"],2)
        self.assertEqual(s["physical_test_worlds_ZK_verified_from_receipts"],64)
        self.assertEqual(s["physical_A_reference_steps_ZK"],8)
        self.assertEqual(s["physical_test_steps_ZK"],20)
        self.assertEqual(s["physical_fatal_move_worlds_ZK"],4)
        self.assertEqual(s["physically_nonterminal_B_probe_steps_ZK"],16)
        self.assertEqual(s["former_states_learned_only_retrospectively"],16)
        self.assertEqual(
            s["Stage6_original_queries_root_counts_independently_verified"],80)
        self.assertEqual(s["Stage6_original_status_histogram"],{
            "partial_progress":16,"incomplete_model":64,
        })
        self.assertEqual(s["new_current_states_still_unknown_after_probing"],16)
        self.assertEqual(
            s["identical_visible_postmove_but_different_terminal_outcomes"],4)
        self.assertEqual(
            s["one_sided_model_falsely_predicts_nonterminal_in_deadly_worlds"],4)
        self.assertEqual(s["new_physical_worlds"],0)
        self.assertEqual(s["new_physical_steps"],0)
        self.assertEqual(s["new_I0_births"],0)
        self.assertEqual(s["new_I0_autonomous_steps"],0)
        self.assertFalse(s["I0_UC_measured"])
        self.assertFalse(s["alternative_food_safety_certified"])
        self.assertFalse(s["independent_rerun_of_WorldBody_apply"])
        self.assertFalse(s["independent_rerun_of_Stage6_search"])

    def test_zk_byte_agreement_but_zb_numeric_drift_preserved(self):
        for file_name,h in ZK_DIGESTS.items():
            self.assertEqual(
                sealed_read(self.roots["zk311"],file_name,h),
                sealed_read(self.roots["zk312"],file_name,h))
        self.assertNotEqual(
            sealed_read(self.roots["zb311"],"a230zb-summary.json",ZB_DIGESTS["3.11"]),
            sealed_read(self.roots["zb312"],"a230zb-summary.json",ZB_DIGESTS["3.12"]))

    def test_altered_sealed_archive_sha_is_rejected(self):
        name="a230zk-summary.json"
        payload=sealed_read(self.roots["zk311"],name,ZK_DIGESTS[name])
        with tempfile.TemporaryDirectory(prefix="a230zl-corruption-") as folder:
            (Path(folder)/name).write_bytes(payload+b"altered")
            with self.assertRaisesRegex(ValueError,"SHA256"):
                sealed_read(folder,name,ZK_DIGESTS[name])

    def test_hidden_zone_feature_inside_sensation_is_rejected(self):
        data=deepcopy(self.original)
        data[1][0]["firstperson_birth_state"]["hidden_lethal_east"]=True
        with self.assertRaisesRegex(ValueError,"non-first-person"):
            self.evaluate(data)

    def test_unobserved_root_prediction_is_rejected(self):
        data=deepcopy(self.original)
        row=next(w for w in data[1] if w["layout_external_only"]=="B_LOCAL")
        row["stage6_shadow_queries"][0]["planner"]["root_available_edges"]=27
        with self.assertRaisesRegex(ValueError,"Stage6 first-step"):
            self.evaluate(data)

    def test_forged_plan_found_is_rejected(self):
        data=deepcopy(self.original)
        row=next(w for w in data[1] if w["layout_external_only"]=="B_EAST")
        row["stage6_shadow_queries"][0]["planner"]["status"]="plan_found"
        with self.assertRaises(ValueError):
            self.evaluate(data)

    def test_false_uc_or_food_safety_certificate_is_rejected(self):
        for key,value in (
            ("lived_i0_UC_cost",1),
            ("berry_B_safety_certified",True),
            ("oracle_feedback_to_cognitive_policy",True),
        ):
            with self.subTest(key=key):
                data=deepcopy(self.original)
                data[1][0][key]=value
                with self.assertRaises(ValueError):
                    self.evaluate(data)

    def test_shadow_reported_dispatched_is_rejected(self):
        data=deepcopy(self.original)
        data[1][0]["stage6_shadow_queries"][0]["no_shadow_dispatch"]=False
        with self.assertRaises(ValueError):
            self.evaluate(data)

    def test_terminal_state_mistaken_as_lived_capture_is_rejected(self):
        data=deepcopy(self.original)
        dead=next(w for w in data[1] if
            w["physically_terminal_step_external_only"] is not None)
        dead["postterminal_firstperson_capture"]={"fabricated":True}
        with self.assertRaises(ValueError):
            self.evaluate(data)

    def test_shadow_search_after_death_is_rejected(self):
        data=deepcopy(self.original)
        dead=next(w for w in data[1] if
            w["physically_terminal_step_external_only"] is not None)
        dead["stage6_shadow_queries"].append(
            deepcopy(dead["stage6_shadow_queries"][0]))
        with self.assertRaises(ValueError):
            self.evaluate(data)

    def test_physical_receipt_tampered_sha_is_rejected(self):
        data=deepcopy(self.original)
        active=next(w for w in data[1] if w["real_physical_lab_receipts"])
        active["real_physical_lab_receipts"][0]["physical_example_sha256"]="0"*64
        with self.assertRaises(ValueError):
            self.evaluate(data)

    def test_unwitnessed_B_ingestion_is_rejected(self):
        data=deepcopy(self.original)
        active=next(w for w in data[1] if w["real_physical_lab_receipts"])
        active["real_physical_lab_receipts"][0]["physical_example"]["command"]=B_EAT
        with self.assertRaises(ValueError):
            self.evaluate(data)

    def test_B_collection_without_visible_B_is_rejected(self):
        data=deepcopy(self.original)
        active=next(w for w in data[1] if
            w["layout_external_only"]=="B_LOCAL" and
            w["protocol_frozen_before_physics"]=="VISIBLE_PROBE")
        active["real_physical_lab_receipts"][0]["physical_example"][
            "state"]["current_resources"]=[]
        with self.assertRaises(ValueError):
            self.evaluate(data)

    def test_ignoring_visible_obstacle_is_rejected(self):
        data=deepcopy(self.original)
        blocked=next(w for w in data[1] if
            w["layout_external_only"]=="B_EAST_BLOCKED")
        blocked["lab_perceptual_choices"][0][
            "preregistered_external_lab_proposal"]=MOVE_E
        with self.assertRaises(ValueError):
            self.evaluate(data)

    def test_inserting_future_into_prior_memory_is_rejected(self):
        data=deepcopy(self.original)
        active=next(w for w in data[1] if
            len(w["stage6_shadow_queries"])>1)
        active["stage6_shadow_queries"][0][
            "own_living_prior_examples"]=1
        with self.assertRaises(ValueError):
            self.evaluate(data)

    def test_cross_world_example_forged_as_own_memory_is_rejected(self):
        data=deepcopy(self.original)
        candidate=next(w for w in data[1] if
            len(w["real_physical_lab_receipts"])==2)
        candidate["real_physical_lab_receipts"][0]["world_id"]="foreign-world"
        with self.assertRaises(ValueError):
            self.evaluate(data)

    def test_terminal_counterfactual_safety_reinterpretation_rejected(self):
        data=deepcopy(self.original)
        data[0]["exact_mortal_counterfactual_controls"][0][
            "safety_calibration_inferred"]=True
        with self.assertRaises(ValueError):
            self.evaluate(data)

    def test_terminal_outcome_removed_from_denominator_rejected(self):
        data=deepcopy(self.original)
        idx=next(i for i,w in enumerate(data[1]) if
            w["physically_terminal_step_external_only"] is not None)
        data[1].pop(idx)
        with self.assertRaisesRegex(ValueError,"factorial"):
            self.evaluate(data)

    def test_cross_profile_training_hash_fails(self):
        data=deepcopy(self.original)
        ref=next(w for w in data[1] if w["profile"]=="restored")
        other=next(w for w in data[1] if w["profile"]=="sustained")
        ref["original_prebirth_A_equipment_sha256"] = other[
            "original_prebirth_A_equipment_sha256"]
        with self.assertRaises(ValueError):
            self.evaluate(data)

    def test_conflicting_same_key_outputs_refused(self):
        x=deepcopy(self.original[0]["A_reference_worlds"][0][
            "physical_examples"][0])
        y=deepcopy(x)
        y["observed_next_state"]["body"]["water"] -= 1
        with self.assertRaisesRegex(ValueError,"conflicting"):
            exact_dictionary([x,y])

    def test_auditor_does_not_instantiate_cognitive_or_physical_runtime(self):
        source=(Path(__file__).resolve().parents[1]/
            "scripts/audit_stage12_issue110_b_a230zl_ownworld_sealed.py"
        ).read_text()
        self.assertNotIn("from lab.world import",source)
        self.assertNotIn("from i0.equipment import",source)
        self.assertNotIn("SimulatorPlanner(",source)
        self.assertNotIn("WorldBody(",source)
        self.assertNotIn("Stage12Runtime(",source)
        self.assertNotIn("run_stage12_issue110_b_a230zk_ownworld_probe",source)
        self.assertNotIn("life.run_step(",source)


if __name__=="__main__":
    unittest.main()
