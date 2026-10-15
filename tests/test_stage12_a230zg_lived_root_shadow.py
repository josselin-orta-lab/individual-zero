"""A2.30-ZG adversarial tests on ONE already-executed detached study.

No new WorldBody or Stage12Runtime instantiated by these tests. All test
worlds and real 14 physical steps are owned by the single preceding runner
invocation. The original 12 autonomous ZB lives are immutable source data.
"""
from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from run_stage12_issue110_b_a230zg_lived_root_shadow import (
    decode_state,digest,verify_result,verify_original_birth_sources,
    COLLECT_B,MOVE_E,EAT_B,
)


class PhysicalBirthRootShadowAdversarialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root=Path(os.environ["A230ZG_OUTPUT"])
        cls.manifest=json.loads(
            (root/"a230zg-physical-demonstrations.json").read_text()
        )
        cls.rows=json.loads(
            (root/"a230zg-lived-birth-shadow.json").read_text()
        )
        cls.summary=json.loads(
            (root/"a230zg-summary.json").read_text()
        )
        cls.original_roots=verify_original_birth_sources(
            Path(os.environ["A230ZG_ORIGINAL_311"]),
            Path(os.environ["A230ZG_ORIGINAL_312"]),
        )

    def review(self,rows=None):
        return verify_result(deepcopy(self.rows if rows is None else rows))

    def test_immutable_autonomous_sources_and_physical_training_contract(self):
        s=self.summary
        self.assertEqual(s["historical_I0_birth_roots_scored"],12)
        self.assertEqual(s["original_ZB_autonomous_steps_reused_read_only"],384)
        self.assertEqual(s["separate_detached_physical_worlds"],6)
        self.assertEqual(s["physical_A_reference_actions"],8)
        self.assertEqual(s["physical_B_non_ingestive_actions"],6)
        self.assertEqual(s["total_new_physical_training_steps"],14)
        self.assertEqual(s["actual_shadow_searches"],24)
        self.assertEqual(s["new_autonomous_I0_births"],0)
        self.assertEqual(s["new_autonomous_I0_steps"],0)
        self.assertEqual(s["original_roots_B_visible"],8)
        self.assertEqual(s["historical_A_B_root_unknown"],8)
        self.assertEqual(s["exact_B_demonstrations_match_visible_roots"],8)
        self.assertEqual(s["hidden_effect_parity_pairs"],6)
        self.assertEqual(s["model_predicted_B_ingestion_count"],0)
        self.assertFalse(s["actual_I0_berry_B_food_gain_proven"])
        self.assertFalse(s["actual_I0_berry_B_food_safety_proven"])
        self.assertFalse(s["model_was_installed_in_real_I0"])
        self.assertTrue(s["no_act_executed_from_shadow"])
        self.assertEqual(len(self.original_roots),12)
        self.assertEqual(len(self.rows),12)
        self.assertEqual(self.review()["actual_shadow_searches"],24)

    def test_demos_are_really_physical_and_have_exact_root_inputs(self):
        demos=self.manifest["all_physical_demonstrations"]
        self.assertEqual(len(demos),6)
        self.assertEqual(len({e["source_world_id"] for e in demos}),6)
        self.assertEqual(sum(d["physical_step_count"] for d in demos),14)
        self.assertEqual(sum(d["physical_step_count"] for d in demos
            if d["source_world_id"].startswith("B_DEMONSTRATOR")),6)
        index={d["source_world_id"]:d for d in demos}
        for d in demos:
            examples=d["physical_examples"]
            self.assertEqual(len(examples),d["physical_step_count"])
            self.assertEqual(
                [digest(e) for e in examples],d["physical_example_sha256"],
            )
            self.assertEqual(
                examples[0]["state"],d["root_first_person"],
            )
            self.assertTrue(all(not e["terminal"] for e in examples))
            self.assertTrue(d["not_an_I0_birth"])
            self.assertTrue(d["no_B_ingestion"])
            for i,e in enumerate(examples):
                if i>0:
                    self.assertEqual(
                        e["state"],examples[i-1]["observed_next_state"],
                    )
                if d["source_world_id"].startswith("B_DEMONSTRATOR"):
                    self.assertNotEqual(e["command"],EAT_B.as_dict())
                    self.assertNotEqual(e["command"]["primitive"],"manger")
        for row in self.rows:
            if row["layout"]=="B_NONE":
                self.assertIsNone(row["external_physical_source_world_id"])
                self.assertIsNone(row["eligible_B_first_step"])
            else:
                demo=index[row["external_physical_source_world_id"]]
                self.assertEqual(
                    row["first_person_root_state"],demo["root_first_person"],
                )
                self.assertEqual(
                    row["physically_witnessed_B_first_step_next_state"],
                    demo["physical_examples"][0]["observed_next_state"],
                )

    def test_hidden_lethal_has_identical_root_and_shadow_no_effect_inference(self):
        by={}
        for row in self.rows:
            by.setdefault((row["profile"],row["layout"]),[]).append(row)
        self.assertEqual(len(by),6)
        for key,pair in by.items():
            self.assertEqual(len(pair),2)
            self.assertEqual(pair[0]["first_person_root_state"],
                             pair[1]["first_person_root_state"])
            self.assertEqual(pair[0]["enriched_stage6"],
                             pair[1]["enriched_stage6"])
        self.assertFalse(any(
            row["enriched_stage6"]["berry_b_safety_certified"]
            for row in self.rows
        ))

    def test_prebirth_A_equipment_artifact_matches_historical_subjects(self):
        original={life["birth_id"]:life for life in self.original_roots}
        model_hash=self.manifest["original_A_model_sha256_by_profile"]
        self.assertEqual(set(model_hash),{"restored","sustained"})
        for row in self.rows:
            birth=original[row["original_birth_id"]]
            self.assertEqual(
                row["A_only_equipment_sha256"],
                model_hash[row["profile"]],
            )
            self.assertEqual(
                birth["equipment_sha256_A_only"],
                model_hash[row["profile"]],
            )
            self.assertEqual(
                birth["initial_accessible_projection"],
                row["first_person_root_state"],
            )

    def test_B_visible_candidate_is_known_only_after_demonstration(self):
        for row in self.rows:
            if row["layout"]!="B_NONE":
                self.assertTrue(
                    row["eligible_B_first_step_in_candidate_commands"])
                self.assertIs(row["B_first_step_known_in_historical_A"],False)
                self.assertIs(row["B_first_step_known_in_augmented_shadow"],True)
                self.assertEqual(
                    row["eligible_B_first_step"],
                    (COLLECT_B if row["layout"]=="B_LOCAL" else MOVE_E).as_dict(),
                )
            else:
                self.assertIsNone(row["eligible_B_first_step"])
                self.assertIsNone(row["B_first_step_known_in_augmented_shadow"])

    def test_hidden_or_future_feature_in_root_rejected(self):
        fake=deepcopy(self.rows)
        fake[0]["first_person_root_state"]["hidden_toxicity"]=False
        with self.assertRaisesRegex(ValueError,"hidden/future"):
            self.review(fake)

    def test_forged_birth_root_digest_rejected(self):
        fake=deepcopy(self.rows)
        fake[0]["first_person_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"first-person model source"):
            self.review(fake)

    def test_false_model_source_or_b_safety_claim_rejected(self):
        fake=deepcopy(self.rows)
        fake[0]["B_ingestion_safety_proven"]=True
        with self.assertRaisesRegex(ValueError,"cognitive/oracular safety"):
            self.review(fake)

    def test_forged_shadow_dispatched_command_rejected(self):
        fake=deepcopy(self.rows)
        fake[0]["enriched_stage6"]["no_shadow_action_dispatched"]=False
        with self.assertRaisesRegex(ValueError,"fake known-root"):
            self.review(fake)

    def test_fake_berry_B_ingestion_predicted_without_evidence_rejected(self):
        fake=deepcopy(self.rows)
        fake[0]["enriched_stage6"]["predicted_commands"].append(EAT_B.as_dict())
        with self.assertRaisesRegex(ValueError,"fake known-root"):
            self.review(fake)

    def test_impossible_berry_B_at_absent_root_rejected(self):
        fake=deepcopy(self.rows)
        target=next(x for x in fake if x["layout"]=="B_NONE")
        target["eligible_B_first_step"]=COLLECT_B.as_dict()
        with self.assertRaisesRegex(ValueError,"manufactured action"):
            self.review(fake)

    def test_physically_untrained_B_edge_falsification_rejected(self):
        fake=deepcopy(self.rows)
        target=next(x for x in fake if x["layout"]=="B_LOCAL")
        target["B_first_step_known_in_augmented_shadow"]=False
        with self.assertRaisesRegex(ValueError,"B root-edge provenance"):
            self.review(fake)

    def test_illegitimate_root_edge_score_rejected(self):
        fake=deepcopy(self.rows)
        fake[0]["baseline_stage6"]["root_available_edges"]=999
        with self.assertRaisesRegex(ValueError,"fake known-root"):
            self.review(fake)

    def test_hidden_physics_must_not_change_shadow_across_pair(self):
        fake=deepcopy(self.rows)
        x=next(x for x in fake if x["profile"]=="restored"
               and x["layout"]=="B_LOCAL"
               and x["hidden_effect_for_external_stratification_only"]=="toxic_lethal")
        x["enriched_stage6"]["status"]="plan_found"
        with self.assertRaisesRegex(ValueError,"hidden hazard changed"):
            self.review(fake)

    def test_no_i0_action_or_normative_model_was_implemented(self):
        source=(
            Path(__file__).resolve().parents[1]/
            "scripts/run_stage12_issue110_b_a230zg_lived_root_shadow.py"
        ).read_text()
        self.assertNotIn("life.run_step(",source)
        self.assertNotIn("Stage12Runtime(",source)
        self.assertNotIn("from lab.oracle import",source)
        self.assertNotIn("cognitive_model.install",source)
        self.assertNotIn("model.declare_safe(",source)


if __name__=="__main__":
    unittest.main()
