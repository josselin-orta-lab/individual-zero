"""A2.30-ZP: adversarial tests of an independent archived-data auditor.

Only loads original CI artifacts; no WorldBody, trainer, I0 runtime or Oracle.
"""
from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"scripts"))
from audit_stage12_issue110_b_a230zp_sealed_factorized import (
    FILES, _original_bytes, digest, forecast, independently_audit, load_archives,
    independently_check_original_runner_chronology,
    reconstitute_train, validate_source_row, visible_state,
)


class SealedFactorizedArchiveAuditorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root_311=Path(os.environ["A230ZP_ZO311"])
        cls.root_312=Path(os.environ["A230ZP_ZO312"])
        cls.original=load_archives(cls.root_311,cls.root_312)

    def recheck(self,change=None):
        data=deepcopy(self.original)
        if change is not None:
            change(data)
        return independently_audit(*data)

    def test_all_five_original_sources_match_sealed_311_312_bytes(self):
        for name,hashvalue in FILES.items():
            a=_original_bytes(self.root_311,name,hashvalue)
            b=_original_bytes(self.root_312,name,hashvalue)
            self.assertEqual(a,b)

    def test_source_pin_catches_forged_archive_and_ambiguous_filename(self):
        name="a230zo-summary.json"
        original=_original_bytes(self.root_311,name,FILES[name])
        with TemporaryDirectory(prefix="a230zp-test-") as tmp:
            p=Path(tmp)/name
            p.write_bytes(original+b"\n")
            with self.assertRaisesRegex(ValueError,"SHA-256"):
                _original_bytes(Path(tmp),name,FILES[name])
            p.write_bytes(original)
            duplicate=Path(tmp)/"subdir"
            duplicate.mkdir()
            (duplicate/name).write_bytes(original)
            with self.assertRaisesRegex(ValueError,"ambiguous"):
                _original_bytes(Path(tmp),name,FILES[name])

    def test_full_model_and_heldout_counts_independently_reproduced(self):
        r=self.recheck()
        self.assertEqual(r["original_detached_training_worlds"],16)
        self.assertEqual(r["original_heldout_worlds"],104)
        self.assertEqual(r["independent_total_original_worlds"],120)
        self.assertEqual(r["original_one_step_physical_examples_independently_hashed"],120)
        self.assertEqual(r["nominal_independently_recomputed_exact_six_deltas"],64)
        self.assertEqual(r["nominal_denominator"],64)
        self.assertEqual(r["heldout_exact_fullstate_keys_known"],0)
        self.assertEqual(r["heldout_body_boundary_abstentions"],16)
        self.assertEqual(r["hidden_lethal_motor_transitions"],4)
        self.assertEqual(r["hidden_integrity_damage_transitions"],8)
        self.assertEqual(r["hidden_forced_action_failures"],8)
        self.assertEqual(r["nominal_latent_pair_parity_groups"],32)
        self.assertEqual(r["all_hidden_interventions_match_nominal_preaction_observation"],24)
        self.assertEqual(r["heldout_unknown_terminal_forecasts"],104)
        self.assertEqual(r["heldout_unknown_safety_forecasts"],104)
        self.assertEqual(r["new_autonomous_I0_births"],0)
        self.assertFalse(r["safety_guaranteed"])
        self.assertFalse(r["external_model_installed_into_I0"])

    def test_new_cognitive_action_has_no_current_heldout_exact_key(self):
        src, archive, heldout, scores, meta=self.original
        fresh,known=reconstitute_train(src)
        self.assertEqual(len(known),16)
        for row in heldout:
            self.assertNotIn(digest({
                "state":row["preaction_first_person"],
                "command":row["action_physically_applied"],
            }), known)
        self.assertEqual(fresh,archive["model"])

    def test_prediction_is_partial_and_all_four_unknowns_always_missing(self):
        source,ar,heldout,scores,meta=self.original
        for row,score in zip(heldout,scores):
            p=score["frozen_empirical_prediction"]
            self.assertEqual(p,forecast(ar["model"],row["preaction_first_person"],row["command_label"]))
            for name in ("safe","terminal","next_adjacency","integrity"):
                self.assertIsNone(p[name])
            self.assertIsNone(row["postdeath_lived_capture"])

    def test_no_per_action_forecast_receipt_was_sealed_before_physics(self):
        report=self.recheck()
        self.assertFalse(report["per_heldout_prediction_receipt_created_before_WorldBody_apply_proven"])
        self.assertTrue(report["original_ZO_prediction_scoring_executed_after_heldout_physics"])
        self.assertTrue(report["source_only_training_before_heldout_physics_confirmed_by_original_code"])
        self.assertFalse(report["independent_replay_of_WorldBody_apply"])

    def test_foreign_hidden_safety_field_rejected_in_first_person_input(self):
        def fake(data):
            data[2][0]["preaction_first_person"]["hidden_lethal_zone"]=True
        with self.assertRaisesRegex(ValueError,"hidden/future"):
            self.recheck(fake)

    def test_new_neighbor_oracle_feature_rejected(self):
        def fake(data):
            data[2][0]["preaction_first_person"]["adjacent"][0]["oracle_hazard"]=True
        with self.assertRaisesRegex(ValueError,"neighbor"):
            self.recheck(fake)

    def test_training_falsely_contains_heldout_example_rejected(self):
        def fake(data):
            data[0][0]=deepcopy(data[2][0])
        with self.assertRaisesRegex(ValueError,"cohort"):
            self.recheck(fake)

    def test_forged_training_measurement_rejected(self):
        def fake(data):
            data[0][0]["physical_example_sha256"]="f"*64
        with self.assertRaisesRegex(ValueError,"SHA"):
            self.recheck(fake)

    def test_hidden_unsafe_safety_flag_in_frozen_model_rejected(self):
        def fake(data):
            data[1]["model"]["MOVE_E"]["general_safety_claim"]=True
        with self.assertRaisesRegex(ValueError,"frozen model"):
            self.recheck(fake)

    def test_heldout_primitive_ingestion_injected_rejected(self):
        def fake(data):
            data[2][0]["action_physically_applied"]={
                "primitive":"manger","parameters":{"target":"berry_b"}}
        with self.assertRaisesRegex(ValueError,"safety|UC"):
            self.recheck(fake)

    def test_duplicate_physical_world_identity_rejected(self):
        def fake(data):
            data[2][1]["world_id"]=data[2][0]["world_id"]
        with self.assertRaises(ValueError):
            self.recheck(fake)

    def test_command_without_visible_berry_cannot_be_scored(self):
        def fake(data):
            target=next(x for x in data[2] if x["command_label"]=="COLLECT_B")
            target["preaction_first_person"]["current_resources"]=[]
        with self.assertRaises(ValueError):
            self.recheck(fake)

    def test_blocked_east_move_is_ineligible(self):
        frozen,known=reconstitute_train(self.original[0])
        row=next(x for x in self.original[2] if x["command_label"]=="MOVE_E")
        before=deepcopy(row["preaction_first_person"])
        for item in before["adjacent"]:
            if item["direction"]=="east":
                item["passable"]=False
        self.assertEqual(forecast(frozen,before,"MOVE_E")["status"],"abstain_ineligible")

    def test_forged_terminal_survival_cannot_overwrite_external_death(self):
        def fake(data):
            target=next(x for x in data[2] if x["physically_terminal_external_only"])
            target["physically_terminal_external_only"]=False
        with self.assertRaisesRegex(ValueError,"terminal"):
            self.recheck(fake)

    def test_forged_lived_postmortem_observation_is_rejected(self):
        def fake(data):
            target=next(x for x in data[2] if x["physically_terminal_external_only"])
            target["postdeath_lived_capture"]=target["postaction_external_only"]
        with self.assertRaisesRegex(ValueError,"lived cognition"):
            self.recheck(fake)

    def test_false_full_state_or_safety_forecast_is_rejected(self):
        for name,value in (
            ("safe",True),("terminal",False),("integrity",100.0),
            ("next_adjacency",[]),
        ):
            def fake(data):
                data[3][0]["frozen_empirical_prediction"][name]=value
            with self.assertRaisesRegex(ValueError,"prediction"):
                self.recheck(fake)

    def test_hidden_action_failure_cannot_be_scored_as_six_successes(self):
        def fake(data):
            idx=next(i for i,x in enumerate(data[2])
                     if x["hidden_intervention_external_only"]=="hidden_forced_action_failure")
            data[3][idx]["all_six_components_match_external_only"]=True
        with self.assertRaisesRegex(ValueError,"scorer"):
            self.recheck(fake)

    def test_false_clamp_abstention_status_rejected(self):
        def fake(data):
            i=next(i for i,x in enumerate(data[2]) if x["preregistered_cohort"]=="BOUNDARY")
            data[3][i]["frozen_empirical_prediction"]["status"]="empirical_partial_not_certified"
        with self.assertRaisesRegex(ValueError,"prediction"):
            self.recheck(fake)

    def test_false_exact_table_known_heldout_root_rejected(self):
        def fake(data):
            data[3][0]["original_train_model_firstperson_exact_key_known"]=True
        with self.assertRaisesRegex(ValueError,"prediction"):
            self.recheck(fake)

    def test_forged_unsafe_count_in_sealed_scientific_summary_rejected(self):
        def fake(data):
            data[4]["hazard_hidden_motor_deaths"]=0
        with self.assertRaisesRegex(ValueError,"aggregate"):
            self.recheck(fake)

    def test_latent_toxicity_pair_cannot_fake_first_person_difference(self):
        def fake(data):
            target=next(x for x in data[2] if
                        x["preregistered_cohort"]=="NOMINAL" and
                        x["latent_berry_effect_external_only"]=="toxic_lethal")
            target["preaction_first_person"]["body"]["food"]+=1
        with self.assertRaises(ValueError):
            self.recheck(fake)

    def test_false_uc_or_oracle_source_disallowed(self):
        def fake(data):
            data[2][0]["actual_i0_uc_measured"]=1
            data[2][0]["no_oracle_or_hidden_input_to_prediction"]=False
        with self.assertRaisesRegex(ValueError,"UC"):
            self.recheck(fake)

    def test_static_source_chronology_flags_postphysical_scoring(self):
        with TemporaryDirectory(prefix="a230zp-order-") as temp:
            sample=Path(temp)/"original_runner.py"
            sample.write_text(
                "def experiment(folder):\n"
                "    training_pairs=[apply_one(rec) for rec in train_recipes]\n"
                "    model=fit_partial_empirical(training_pairs)\n"
                "    heldout=[apply_one(rec) for rec in heldout_recipes]\n"
                "    scores=[compare_forecast(row,model,exact) for row in heldout]\n"
            )
            r=independently_check_original_runner_chronology(sample)
            self.assertFalse(r["prephysical_per_world_prediction_receipt_issued"])
            self.assertTrue(r["original_source_scorer_only_after_heldout_physics"])
            sample.write_text(
                "def experiment(folder):\n"
                "    training_pairs=[apply_one(rec) for rec in train_recipes]\n"
                "    model=fit_partial_empirical(training_pairs)\n"
                "    scores=[compare_forecast(row,model,exact) for row in heldout]\n"
                "    heldout=[apply_one(rec) for rec in heldout_recipes]\n"
            )
            with self.assertRaisesRegex(ValueError,"chronological"):
                independently_check_original_runner_chronology(sample)

    def test_source_uses_standard_library_without_original_scorer_or_worldbody(self):
        text=(Path(__file__).resolve().parents[1]/"scripts"/
              "audit_stage12_issue110_b_a230zp_sealed_factorized.py").read_text()
        for forbidden in (
            "from lab.world import", "import run_stage12_issue110_b_a230zo",
            "from i0.equipment import", "from i0.modules.stage6_planning import",
            "WorldBody(", "SimulatorPlanner(", "Stage12Runtime(", "Oracle(",
        ):
            self.assertNotIn(forbidden,text)

if __name__=="__main__":
    unittest.main()
