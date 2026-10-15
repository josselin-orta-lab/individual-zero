"""A2.30-ZT original-archive-only adversarial tests.

No physics, Stage6, original ZS or ZO runner is called. Reconstruct only the
unchanged source SHA-256-locked GitHub Actions artifacts from run 38801117723.
"""
from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from audit_stage12_issue110_b_a230zt_splitjob_archives import (
    ORIGINAL_HEAD,ORIGINAL_RUN,SEALED,REALIZED,
    causal_sha,independent_review,independent_predict,learn_from_sixteen,
    original_file,read_archives,
)


class IndependentlySealedTwoJobAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seal311=Path(os.environ["A230ZT_SEAL311"])
        cls.seal312=Path(os.environ["A230ZT_SEAL312"])
        cls.real311=Path(os.environ["A230ZT_REAL311"])
        cls.real312=Path(os.environ["A230ZT_REAL312"])
        cls.original=read_archives(
            cls.seal311,cls.real311,cls.seal312,cls.real312
        )

    def check(self,modified=None):
        return independent_review(*(deepcopy(x) for x in (
            self.original if modified is None else modified
        )))

    def test_seven_unchanged_original_Github_source_sha(self):
        self.assertEqual(len(SEALED),4)
        self.assertEqual(len(REALIZED),3)
        for name,expected in SEALED.items():
            self.assertEqual(
                original_file(self.seal311,name,expected),
                original_file(self.seal312,name,expected)
            )
        for name,expected in REALIZED.items():
            self.assertEqual(
                original_file(self.real311,name,expected),
                original_file(self.real312,name,expected)
            )

    def test_independent_reconstruction_of_120_actual_receipts_and_predictions(self):
        result=self.check()
        self.assertEqual(result["original_run_id"],ORIGINAL_RUN)
        self.assertEqual(result["original_head"],ORIGINAL_HEAD)
        self.assertEqual(result["training_physical_examples_independently_hashed"],16)
        self.assertEqual(result["heldout_physical_examples_independently_hashed"],104)
        self.assertEqual(result["locked_preaction_predictions_independently_recomputed"],104)
        self.assertEqual(result["original_exact_training_heldout_matches"],0)
        self.assertEqual(result["nominal_successful_partial_predictions"],64)
        self.assertEqual(result["source_ineligible_clamp_abstentions"],16)
        self.assertEqual(result["original_hidden_fatal_motors"],4)
        self.assertEqual(result["original_hidden_injuries"],8)
        self.assertEqual(result["original_forced_numeric_mismatches"],8)
        self.assertEqual(result["nominal_unobservable_B_twins_identical"],32)
        self.assertEqual(result["hidden_hazard_matched_preaction_controls"],24)
        self.assertFalse(result["CI_job_order_provable_from_JSON_alone"])
        self.assertTrue(result["CI_job_order_requires_original_GitHub_run_and_needs"])
        self.assertFalse(result["reviewer_reexecuted_physics"])
        self.assertEqual(result["reviewer_new_worlds"],0)
        self.assertFalse(result["motor_or_food_safety_proven"])
        self.assertEqual(result["Stage12"],"PARTIAL")

    def test_learning_reconstructs_original_two_delta_families(self):
        model,keys=learn_from_sixteen(self.original[1])
        self.assertEqual(len(keys),16)
        self.assertEqual(model,self.original[2]["model"])
        self.assertEqual(causal_sha(model),self.original[2]["model_sha256"])
        self.assertEqual(model["MOVE_E"]["physically_observed_training_examples"],8)
        self.assertEqual(model["COLLECT_B"]["physically_observed_training_examples"],8)
        for r in model.values():
            self.assertFalse(r["general_safety_claim"])
            self.assertIsNone(r["unresolved_terminality"])

    def test_independent_forecast_does_not_claim_safety_or_whole_future(self):
        model=self.original[2]["model"]
        for rec in self.original[3]:
            choice=("MOVE_E" if rec["command"]["primitive"]=="se_deplacer"
                    else "COLLECT_B")
            result=independent_predict(model,rec["preaction_first_person"],choice)
            self.assertEqual(result,rec["prediction"])
            self.assertIsNone(result["integrity"])
            self.assertIsNone(result["terminal"])
            self.assertIsNone(result["next_adjacency"])
            self.assertIsNone(result["safe"])

    def test_physical_hidden_lethal_not_known_before_action(self):
        physical=self.original[4]
        source=self.original[3]
        dead=[
            (locked,world) for locked,world in zip(source,physical)
            if world["physically_terminal_external_only"]
        ]
        self.assertEqual(len(dead),4)
        for locked,world in dead:
            self.assertEqual(
                world["hidden_intervention_external_only"],"hidden_lethal_east"
            )
            self.assertIsNone(locked["prediction"]["terminal"])
            self.assertIsNone(locked["prediction"]["safe"])
            self.assertEqual(
                locked["prediction"]["status"],
                "empirical_partial_not_certified"
            )

    def test_sealed_original_artifact_one_byte_alteration_fails(self):
        raw=original_file(
            self.seal311,"a230zs-preaction-forecast-receipts.json",
            SEALED["a230zs-preaction-forecast-receipts.json"]
        )
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/"a230zs-preaction-forecast-receipts.json"
            path.write_bytes(raw+b"\n")
            with self.assertRaisesRegex(ValueError,"SHA-256"):
                original_file(Path(temp),path.name,
                    SEALED["a230zs-preaction-forecast-receipts.json"])

    def test_duplicate_source_path_fails(self):
        raw=original_file(
            self.real311,"a230zs-summary.json",REALIZED["a230zs-summary.json"]
        )
        with tempfile.TemporaryDirectory() as temp:
            a=Path(temp)/"a"
            b=Path(temp)/"b"
            a.mkdir();b.mkdir()
            (a/"a230zs-summary.json").write_bytes(raw)
            (b/"a230zs-summary.json").write_bytes(raw)
            with self.assertRaisesRegex(ValueError,"duplicated"):
                original_file(temp,"a230zs-summary.json",
                              REALIZED["a230zs-summary.json"])

    def test_changed_model_after_physical_exposure_rejected(self):
        parts=deepcopy(self.original)
        parts[2]["model"]["MOVE_E"]["general_safety_claim"]=True
        with self.assertRaises(ValueError):
            self.check(parts)

    def test_changed_source_training_physical_example_rejected(self):
        parts=deepcopy(self.original)
        parts[1][0]["physical_example"]["observed_next_state"]["x"]+=1
        with self.assertRaises(ValueError):
            self.check(parts)

    def test_training_future_test_example_leaked_rejected(self):
        parts=deepcopy(self.original)
        parts[1][0]["world_id"]=parts[4][0]["world_id"]
        with self.assertRaises(ValueError):
            self.check(parts)

    def test_forged_preaction_predicted_safe_rejected(self):
        parts=deepcopy(self.original)
        parts[3][0]["prediction"]["safe"]=True
        parts[3][0]["prediction_sha256"]=causal_sha(parts[3][0]["prediction"])
        with self.assertRaises(ValueError):
            self.check(parts)

    def test_forged_hidden_variable_in_perceptual_state_rejected(self):
        parts=deepcopy(self.original)
        parts[3][0]["preaction_first_person"]["hidden_lethal_zone"]=True
        with self.assertRaises(ValueError):
            self.check(parts)

    def test_commit_manifest_says_heldout_executed_before_seal_rejected(self):
        parts=deepcopy(self.original)
        parts[0]["physical_heldout_actions_performed_before_seal"]=1
        with self.assertRaisesRegex(ValueError,"timeline"):
            self.check(parts)

    def test_bad_forecast_individually_rehashed_still_rejected(self):
        parts=deepcopy(self.original)
        part=parts[3][0]
        part["prediction"]["estimated"]["food"]+=12.0
        part["prediction_sha256"]=causal_sha(part["prediction"])
        with self.assertRaises(ValueError):
            self.check(parts)

    def test_forged_physical_terminal_state_rejected(self):
        parts=deepcopy(self.original)
        death=next(p for p in parts[4] if p["physically_terminal_external_only"])
        death["physically_terminal_external_only"]=False
        with self.assertRaises(ValueError):
            self.check(parts)

    def test_action_was_not_collecting_nonexistent_berry(self):
        parts=deepcopy(self.original)
        p=next(x for x in parts[3]
               if x["command"]["primitive"]=="collecter")
        p["preaction_first_person"]["current_resources"]=[]
        with self.assertRaises(ValueError):
            self.check(parts)

    def test_forged_success_score_rejected(self):
        parts=deepcopy(self.original)
        p=next(x for x in parts[5]
               if x["all_six_components_match_external_only"] is False)
        p["all_six_components_match_external_only"]=True
        with self.assertRaises(ValueError):
            self.check(parts)

    def test_externally_hidden_B_hazard_falsely_shown_before_action_rejected(self):
        parts=deepcopy(self.original)
        x=next(x for x in parts[3] if x["cohort"]=="HIDDEN")
        x["preaction_first_person"]["oracle_injury"]=10
        with self.assertRaises(ValueError):
            self.check(parts)

    def test_new_lived_I0_UC_claim_rejected(self):
        parts=deepcopy(self.original)
        parts[4][0]["actual_i0_uc_measured"]=5
        with self.assertRaises(ValueError):
            self.check(parts)

    def test_claim_of_mortal_I0_subject_rejected(self):
        parts=deepcopy(self.original)
        parts[4][0]["no_i0_birth_or_autonomous_step"]=False
        with self.assertRaises(ValueError):
            self.check(parts)

    def test_unsealed_extra_prediction_field_rejected(self):
        parts=deepcopy(self.original)
        parts[3][0]["actual_outcome_known_at_seal"]=True
        with self.assertRaisesRegex(ValueError,"future"):
            self.check(parts)

    def test_reviewer_never_imports_original_runner_or_physics(self):
        script=(Path(__file__).resolve().parents[1]/
            "scripts/audit_stage12_issue110_b_a230zt_splitjob_archives.py"
        ).read_text()
        self.assertNotIn("from lab.world import",script)
        self.assertNotIn("from lab.determinism import",script)
        self.assertNotIn("from i0.equipment import",script)
        self.assertNotIn("SimulatorPlanner(",script)
        self.assertNotIn("WorldBody(",script)
        self.assertNotIn("Stage12Runtime(",script)
        self.assertNotIn("import run_stage12_issue110_b_a230zs_sealed_forecast",script)
        self.assertNotIn("import run_stage12_issue110_b_a230zo_factorized_heldout",script)


if __name__=="__main__":
    unittest.main()
