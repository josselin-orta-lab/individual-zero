"""A2.30-ZS adversarial archive tests on the ONE original CI sealed sources.

These tests READ existing artifacts made by a different CI job; they NEVER
instantiate WorldBody, never create a second physical cohort or I0, and never
call the --seal or --realize phases. Rejected manipulations must be observable
from the committed source artifacts.
"""
from __future__ import annotations

from collections import Counter,defaultdict
from copy import deepcopy
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import run_stage12_issue110_b_a230zs_sealed_forecast as zs
import run_stage12_issue110_b_a230zo_factorized_heldout as zo


class SealedProspectivePreactionAdversarialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=Path(os.environ["A230ZS_SEALED_SOURCE"])
        cls.output=Path(os.environ["A230ZS_REALIZED_OUTPUT"])
        cls.seal,cls.train,cls.model_block,cls.rec=(
            zs.read_existing_sealed_source(cls.source)
        )
        cls.physical=json.loads(
            (cls.output/"a230zs-realized-physical-worlds.json").read_text()
        )
        cls.scores=json.loads(
            (cls.output/"a230zs-sealed-predictions-scored.json").read_text()
        )
        cls.summary=json.loads(
            (cls.output/"a230zs-summary.json").read_text()
        )

    def check_wrong(self,filename,mutation,error):
        with tempfile.TemporaryDirectory(prefix="a230zs-tamper-") as folder:
            temp=Path(folder)
            for p in zs.FILES.values():
                shutil.copy2(self.source/p,temp/p)
            target=temp/zs.FILES[filename]
            mutation(target)
            with self.assertRaisesRegex(ValueError,error):
                zs.read_existing_sealed_source(temp)

    def test_signed_source_and_separate_process_gate(self):
        s=self.summary
        self.assertEqual(self.seal["state"],zs.SEAL_STAGE)
        self.assertEqual(self.seal["preregistered_before_code_sha"],
                         zs.PREREG_SHA)
        self.assertEqual(self.seal["physical_train_worlds_applied"],16)
        self.assertEqual(
            self.seal["physical_heldout_actions_performed_before_seal"],0
        )
        self.assertEqual(len(self.rec),104)
        self.assertEqual(len(self.train),16)
        self.assertEqual(len(self.physical),104)
        self.assertEqual(len(self.scores),104)
        self.assertEqual(s["preaction_heldout_forecast_count"],104)
        self.assertEqual(s["realized_physical_heldout_worlds_after_seal"],104)
        self.assertEqual(s["physically_applied_new_total_worlds"],120)
        self.assertTrue(s["ci_seal_job_required_before_realize_job"])
        self.assertTrue(s["new_process_and_job_for_realization"])
        self.assertTrue(s["source_source_files_unchanged_after_scoring"])
        self.assertTrue(
            s["preaction_receipts_verified_before_first_heldout_apply"]
        )
        self.assertEqual(
            s["true_heldout_forecast_receipt_timing"],
            "BEFORE_APPLY_DIFFERENT_CI_JOB",
        )
        self.assertEqual(s["source_model_sha256"],
                         self.seal["preaction_model_sha256"])
        self.assertEqual(s["source_prediction_files_sha256"],
                         self.seal["source_file_sha256"])
        self.assertEqual(s["source_prediction_seal_sha256"],
                         zs.sha256((self.source/zs.FILES["seal"]).read_bytes()
                         ).hexdigest())

    def test_frozen_prediction_histogram_matches_original_physical_replay(self):
        counts=Counter(x["prediction"]["status"] for x in self.rec)
        self.assertEqual(counts,{"empirical_partial_not_certified":88,
                                 "abstain_clamp":16})
        self.assertEqual(self.summary["sealed_preaction_statuses"],dict(counts))
        self.assertEqual(self.summary["nominal_heldout_worlds"],64)
        self.assertEqual(self.summary["hidden_intervention_worlds"],24)
        self.assertEqual(self.summary["clamp_boundary_worlds"],16)
        self.assertEqual(self.summary["nominal_six_component_physically_exact"],64)
        self.assertEqual(self.summary["hazard_hidden_motor_deaths"],4)
        self.assertEqual(self.summary["hazard_hidden_integrity_injuries"],8)
        self.assertEqual(self.summary["hazard_forced_primitive_failures"],8)
        self.assertEqual(self.summary["boundary_abstentions"],16)
        self.assertEqual(self.summary["safety_certificates_emitted"],0)
        self.assertEqual(self.summary["terminality_predictions_emitted"],0)

    def test_all_real_worlds_and_forecasts_join_unchanged(self):
        self.assertEqual(len({
            r["world_id"] for r in self.physical
        }),104)
        assert_all=True
        for i,(locked,actual,score) in enumerate(
            zip(self.rec,self.physical,self.scores)
        ):
            self.assertEqual(locked["world_id"],actual["world_id"])
            self.assertEqual(
                locked["preaction_first_person"],
                actual["preaction_first_person"]
            )
            self.assertEqual(
                locked["command"],actual["action_physically_applied"]
            )
            self.assertEqual(
                locked["prediction"],score["frozen_empirical_prediction"]
            )
            self.assertEqual(
                locked["prediction_sha256"],zs.digest(
                    score["frozen_empirical_prediction"])
            )
            self.assertEqual(locked["source_model_sha256"],
                             self.seal["preaction_model_sha256"])
            self.assertEqual(actual["physical_example"]["state"],
                             locked["preaction_first_person"])
            self.assertEqual(actual["physical_example_sha256"],
                             zs.digest(actual["physical_example"]))
            self.assertIsNone(locked["prediction"]["integrity"])
            self.assertIsNone(locked["prediction"]["terminal"])
            self.assertIsNone(locked["prediction"]["next_adjacency"])
            self.assertIsNone(locked["prediction"]["safe"])
            self.assertIsNone(actual["safety_certificate"])
            self.assertIsNone(actual["postdeath_lived_capture"])
            self.assertTrue(actual["no_i0_birth_or_autonomous_step"])

    def test_model_was_fit_only_on_sixteen_real_train_receipts(self):
        self.assertEqual(zo.fit_partial_empirical(self.train),
                         self.model_block["model"])
        self.assertEqual(zs.digest(self.model_block["model"]),
                         self.model_block["model_sha256"])
        self.assertTrue(all(
            row["source_or_heldout"]=="external_train"
            and row["preregistered_cohort"]=="TRAIN"
            and row["physical_example"]["terminal"] is False
            for row in self.train
        ))
        self.assertTrue(all(
            row["world_id"].startswith("a230zs:") for row in self.train
        ))
        self.assertFalse(any(
            row["world_id"]==test["world_id"] for row in self.train
            for test in self.physical
        ))

    def test_preexposure_hidden_berry_effect_pair_does_not_reveal_future(self):
        twins=defaultdict(list)
        for locked,physical in zip(self.rec,self.physical):
            if physical["preregistered_cohort"]!="NOMINAL":
                continue
            key=(
                tuple(physical["position_factor_external"]),
                tuple(physical["body_factor_external"]),
                physical["phase_factor_external"],
                physical["command_label"],
            )
            twins[key].append((locked,physical))
        self.assertEqual(len(twins),32)
        for pair in twins.values():
            self.assertEqual(len(pair),2)
            self.assertEqual(
                {x[1]["latent_berry_effect_external_only"] for x in pair},
                {"benign","toxic_lethal"},
            )
            self.assertEqual(
                pair[0][0]["preaction_first_person"],
                pair[1][0]["preaction_first_person"]
            )
            self.assertEqual(
                pair[0][0]["prediction"],pair[1][0]["prediction"]
            )

    def test_four_hidden_motor_deaths_cannot_be_certified_safe(self):
        affected=[
            (locked,out) for locked,out in zip(self.rec,self.physical)
            if out["physically_terminal_external_only"]
        ]
        self.assertEqual(len(affected),4)
        self.assertTrue(all(
            out["hidden_intervention_external_only"]=="hidden_lethal_east"
            and locked["prediction"]["status"]=="empirical_partial_not_certified"
            and locked["prediction"]["terminal"] is None
            and locked["prediction"]["safe"] is None
            and out["world_sealed_on_terminal"] is True
            for locked,out in affected
        ))

    def test_all_16_boundary_abstentions_precede_physical_execution(self):
        items=[
            (lock,world) for lock,world in zip(self.rec,self.physical)
            if world["preregistered_cohort"]=="BOUNDARY"
        ]
        self.assertEqual(len(items),16)
        for locked,world in items:
            self.assertEqual(locked["prediction"]["status"],"abstain_clamp")
            self.assertIsNone(locked["prediction"]["estimated"])
            self.assertTrue(world["physical_example"]["command"]["primitive"]
                            in ("se_deplacer","collecter"))
            self.assertTrue(world["no_i0_birth_or_autonomous_step"])

    def test_wrong_sealed_forecast_byte_fails(self):
        self.check_wrong(
            "forecasts",
            lambda p:p.write_bytes(p.read_bytes()+b"\n"),
            "SHA-256 mismatch",
        )

    def test_wrong_sealed_model_byte_fails(self):
        self.check_wrong(
            "model",
            lambda p:p.write_bytes(p.read_bytes().replace(
                b'"general_safety_claim": false',
                b'"general_safety_claim": true',1)),
            "SHA-256 mismatch",
        )

    def test_wrong_sealed_physical_training_byte_fails(self):
        self.check_wrong(
            "training",
            lambda p:p.write_bytes(p.read_bytes()+b" "),
            "SHA-256 mismatch",
        )

    def test_modified_seal_says_heldout_applied_before_commit_fails(self):
        def corrupt(p):
            data=json.loads(p.read_text())
            data["physical_heldout_actions_performed_before_seal"]=104
            p.write_text(json.dumps(data))
        self.check_wrong("seal",corrupt,"tampered or cross-commit")

    def test_wrong_commit_identity_cannot_reuse_source(self):
        def corrupt(p):
            data=json.loads(p.read_text())
            data["git_source_sha"]="0"*40
            p.write_text(json.dumps(data))
        self.check_wrong("seal",corrupt,"tampered or cross-commit")

    def test_hidden_field_in_prediction_input_refused_even_with_valid_model(self):
        fake=deepcopy(self.rec[0]["preaction_first_person"])
        fake["external_lethal_zone"]=True
        with self.assertRaisesRegex(ValueError,"hidden"):
            zs.sealed_prediction(self.model_block["model"],fake,"MOVE_E")

    def test_berry_collection_without_visible_resource_abstains(self):
        first=deepcopy(next(
            x["preaction_first_person"] for x in self.rec
            if x["command"]==zo.COLLECT.as_dict()
        ))
        first["current_resources"]=[]
        result=zs.sealed_prediction(self.model_block["model"],
                                    first,"COLLECT_B")
        self.assertEqual(result["status"],"abstain_ineligible")
        self.assertIsNone(result["safe"])

    def test_visible_blocked_east_abstains(self):
        first=deepcopy(next(
            x["preaction_first_person"] for x in self.rec
            if x["command"]==zo.MOVE.as_dict()
        ))
        for n in first["adjacent"]:
            if n["direction"]=="east":
                n["passable"]=False
        p=zs.sealed_prediction(self.model_block["model"],first,"MOVE_E")
        self.assertEqual(p["status"],"abstain_ineligible")

    def test_false_safe_forecast_rejected_even_when_rehashed_in_memory(self):
        source=deepcopy(self.rec)
        source[0]["prediction"]["safe"]=True
        source[0]["prediction_sha256"]=zs.digest(source[0]["prediction"])
        with self.assertRaisesRegex(ValueError,"future|safety|not|predict"):
            zs.preflight_source_payloads(
                self.train,self.model_block["model"],source
            )

    def test_forecast_on_wrong_command_rejected(self):
        source=deepcopy(self.rec)
        source[0]["command"]=zo.COLLECT.as_dict()
        with self.assertRaisesRegex(ValueError,"forged"):
            zs.preflight_source_payloads(
                self.train,self.model_block["model"],source
            )

    def test_future_physical_score_cannot_be_inserted_into_source_receipt(self):
        source=deepcopy(self.rec)
        source[0]["actual_world_body_after"]=self.physical[0][
            "postaction_external_only"
        ]
        with self.assertRaisesRegex(ValueError,"forged"):
            zs.preflight_source_payloads(
                self.train,self.model_block["model"],source
            )

    def test_made_up_prediction_does_not_pass_hash_or_model_check(self):
        source=deepcopy(self.rec)
        source[0]["prediction"]["status"]="safe_success"
        source[0]["prediction_sha256"]=zs.digest(source[0]["prediction"])
        with self.assertRaisesRegex(ValueError,"changed after"):
            zs.preflight_source_payloads(
                self.train,self.model_block["model"],source
            )

    def test_no_cognitive_module_or_world_result_used_to_issue_forecast(self):
        s=(Path(__file__).resolve().parents[1]/
           "scripts/run_stage12_issue110_b_a230zs_sealed_forecast.py"
           ).read_text()
        self.assertNotIn("Stage12Runtime(",s)
        self.assertNotIn("life.run_step(",s)
        self.assertNotIn("from lab.oracle import",s)
        self.assertNotIn("from i0.modules.stage12_detectors import",s)
        self.assertNotIn("model.declare_safe(",s)
        self.assertNotIn("WorldBody.apply(",s)
        self.assertTrue(all(
            d["had_no_heldout_action_when_sealed"] for d in self.rec
        ))
        self.assertTrue(all(
            d["no_hidden_fields_sent_to_predictor"] for d in self.rec
        ))


if __name__=="__main__":
    unittest.main()
