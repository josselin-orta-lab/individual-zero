"""A2.30-ZT adversarial independent archive-only tests.

These tests read ONLY two original ZS source archives from GitHub Actions
run 38801013480. Never instantiate Stage12Runtime, WorldBody, Stage6,
Oracle, or an independent physics cohort. In-memory tampering never rewrites
the original immutable source artifacts.
"""
from __future__ import annotations

from copy import deepcopy
import json
import math
import os
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from audit_stage12_issue110_b_a230zt_independent_preaction import (
    ORIGINAL_DIGESTS,PREREG,PRETRAIN_HASH,
    evidence_sha,read_original,
    load_two_original_artifacts,
    reconstruct_model,reconstruct_forecast,
    verify_ledger,verify_dataset,
)


def recompute_chain(events):
    """A malicious actor can re-SHA the WHOLE chain; semantic checks must fail."""
    result=deepcopy(events)
    prior="0"*64
    for i,ev in enumerate(result):
        ev["seq"]=i+1
        ev["prev_sha256"]=prior
        ev["event_sha256"]=evidence_sha({
            "seq":ev["seq"],"prev_sha256":prior,
            "kind":ev["kind"],"payload":ev["payload"],
        })
        prior=ev["event_sha256"]
    return result


class SealedPreactionIndependentAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root311=Path(os.environ["A230ZT_ORIGINAL_311"])
        cls.root312=Path(os.environ["A230ZT_ORIGINAL_312"])
        cls.data=load_two_original_artifacts(cls.root311,cls.root312)
        cls.training=cls.data["training"]
        cls.freeze=cls.data["freeze"]
        cls.events=cls.data["events"]
        cls.heldout=cls.data["heldout"]
        cls.scores=cls.data["scores"]

    def check(self,data=None):
        return verify_dataset(
            **deepcopy(self.data if data is None else data)
        )

    def test_original_seven_sha_files_and_two_python_byte_identical(self):
        for name,original in ORIGINAL_DIGESTS.items():
            a=read_original(self.root311,name,original)
            b=read_original(self.root312,name,original)
            self.assertEqual(a,b,name)
        self.assertEqual(len(ORIGINAL_DIGESTS),7)

    def test_independent_recomputation_all_120_worlds_and_104_preactions(self):
        out=self.check()
        self.assertEqual(out["original_physical_examples_hashed"],120)
        self.assertEqual(out["training_worlds_verified"],16)
        self.assertEqual(out["heldout_worlds_verified"],104)
        self.assertEqual(out["durable_ledger_events_independently_rehashed"],208)
        self.assertEqual(out["preaction_outcome_pairs_independently_joined"],104)
        self.assertEqual(out["preaction_forecasts_independently_recomputed"],104)
        self.assertEqual(out["numeric_forecasts"],88)
        self.assertEqual(out["visible_bound_abstentions"],16)
        self.assertEqual(out["nominal_six_feature_exact_count"],64)
        self.assertEqual(out["hidden_motor_deaths_external_only"],4)
        self.assertEqual(out["hidden_injuries_external_only"],8)
        self.assertEqual(out["hidden_forced_failures_external_only"],8)
        self.assertEqual(out["hidden_B_nominal_paired_equalities"],32)
        self.assertFalse(out["any_safety_or_terminal_certification"])
        self.assertFalse(out["wall_clock_order_thirdparty_attested"])
        self.assertFalse(out["physical_simulator_reexecuted"])
        self.assertEqual(out["new_i0_births"],0)

    def test_normative_canonical_full_binary_float_and_unicode_NFC(self):
        self.assertEqual(evidence_sha({"a":-0.0}),evidence_sha({"a":0.0}))
        self.assertEqual(evidence_sha({"\u00e9":1.0}),
                         evidence_sha({"e\u0301":1.0}))
        self.assertNotEqual(evidence_sha(1),evidence_sha(1.0))
        with self.assertRaisesRegex(ValueError,"nonfinite"):
            evidence_sha(float("nan"))
        with self.assertRaisesRegex(ValueError,"NFC causal keys collide"):
            evidence_sha({"\u00e9":1,"e\u0301":2})

    def test_reconstructed_training_only_fingerprint_really_matches(self):
        model,keys=reconstruct_model(self.training)
        self.assertEqual(evidence_sha(model),PRETRAIN_HASH)
        self.assertEqual(model,self.freeze["model"])
        self.assertEqual(len(keys),16)
        for row in self.heldout:
            self.assertNotIn(evidence_sha({
                "state":row["preaction_first_person"],
                "command":row["action_physically_applied"],
            }),keys)

    def test_original_first_and_last_ledger_sequence_is_valid(self):
        self.assertEqual(len(self.events),208)
        self.assertEqual(verify_ledger(self.events),
                         self.data["summary"]["chain_head_sha256"])
        self.assertEqual([self.events[0]["kind"],self.events[1]["kind"]],
                         ["prediction_committed","outcome_sealed"])
        self.assertEqual(self.events[0]["payload"]["world_token"],
                         self.events[1]["payload"]["world_token"])

    def test_original_frozen_partial_never_claims_safety(self):
        for row in self.heldout:
            self.assertFalse(row["no_berry_ingestion"] is not True)
        for i,ev in enumerate(self.events):
            if i%2:
                self.assertIsNone(ev["payload"]["postterminal_lived_capture"])
            else:
                pred=ev["payload"]["frozen_partial_forecast"]
                for key in ("integrity","terminal","next_adjacency","safe"):
                    self.assertIsNone(pred[key])

    def test_missing_or_reordered_even_rehashed_events_rejected(self):
        data=deepcopy(self.data)
        data["events"].pop(20)
        with self.assertRaisesRegex(ValueError,"missing or duplicated"):
            self.check(data)
        data=deepcopy(self.data)
        data["events"][0],data["events"][1]=(
            data["events"][1],data["events"][0]
        )
        data["events"]=recompute_chain(data["events"])
        with self.assertRaisesRegex(ValueError,"order"):
            self.check(data)

    def test_plain_tampered_sha_file_refused(self):
        name="a230zs-frozen-training-model.json"
        original=read_original(self.root311,name,ORIGINAL_DIGESTS[name])
        with tempfile.TemporaryDirectory(prefix="zt-tamper-") as folder:
            (Path(folder)/name).write_bytes(original+b"\n")
            with self.assertRaisesRegex(ValueError,"SHA mismatch"):
                read_original(Path(folder),name,ORIGINAL_DIGESTS[name])

    def test_duplicate_original_source_file_refused(self):
        name="a230zs-physical-training.json"
        raw=read_original(self.root311,name,ORIGINAL_DIGESTS[name])
        with tempfile.TemporaryDirectory(prefix="zt-duplicate-") as folder:
            (Path(folder)/name).write_bytes(raw)
            (Path(folder)/"copy").mkdir()
            (Path(folder)/"copy"/name).write_bytes(raw)
            with self.assertRaisesRegex(ValueError,"duplicated"):
                read_original(Path(folder),name,ORIGINAL_DIGESTS[name])

    def test_rehashed_numeric_forecast_fabrication_refused(self):
        data=deepcopy(self.data)
        data["events"][0]["payload"]["frozen_partial_forecast"]["estimated"]["x"]=9999
        data["events"]=recompute_chain(data["events"])
        with self.assertRaisesRegex(ValueError,"forecast not identical"):
            self.check(data)

    def test_rehashed_future_hidden_B_label_in_prediction_refused(self):
        data=deepcopy(self.data)
        data["events"][0]["payload"]["hidden_lethal_east"]=True
        data["events"]=recompute_chain(data["events"])
        with self.assertRaisesRegex(ValueError,"unknown source"):
            self.check(data)

    def test_rehashed_safe_or_terminal_forecast_refused(self):
        for key,value in (("safe",True),("terminal",False),
                          ("integrity",100.0),("next_adjacency",[])):
            data=deepcopy(self.data)
            data["events"][0]["payload"]["frozen_partial_forecast"][key]=value
            data["events"]=recompute_chain(data["events"])
            with self.assertRaisesRegex(ValueError,"forecast not identical"):
                self.check(data)

    def test_rehashed_prediction_without_earlier_physical_state_refused(self):
        data=deepcopy(self.data)
        data["events"][0]["payload"]["preaction_accessible_state"]["x"]=123
        data["events"]=recompute_chain(data["events"])
        with self.assertRaises(ValueError):
            self.check(data)

    def test_post_outcome_forged_preaction_link_refused(self):
        data=deepcopy(self.data)
        data["events"][1]["payload"]["linked_preaction_event_sha256"]="0"*64
        data["events"]=recompute_chain(data["events"])
        with self.assertRaisesRegex(ValueError,"consequence not joined"):
            self.check(data)

    def test_source_training_example_taken_from_heldout_refused(self):
        data=deepcopy(self.data)
        data["training"][0]=deepcopy(self.heldout[0])
        with self.assertRaises(ValueError):
            self.check(data)

    def test_forged_model_from_training_refused(self):
        data=deepcopy(self.data)
        data["freeze"]["model"]["MOVE_E"]["supported_empirical_deltas"]["x"]=999
        with self.assertRaisesRegex(ValueError,"model was tampered"):
            self.check(data)

    def test_physically_forged_B_ingestion_refused(self):
        data=deepcopy(self.data)
        data["heldout"][0]["physical_example"]["command"]={
            "primitive":"manger","parameters":{"target":"berry_b"}
        }
        with self.assertRaises(ValueError):
            self.check(data)

    def test_false_lived_postdeath_capture_refused(self):
        data=deepcopy(self.data)
        index=next(i for i,x in enumerate(data["heldout"])
                   if x["physically_terminal_external_only"])
        data["heldout"][index]["postdeath_lived_capture"]=deepcopy(
            data["heldout"][index]["postaction_external_only"]
        )
        with self.assertRaises(ValueError):
            self.check(data)

    def test_false_uc_or_oracle_transfer_refused(self):
        data=deepcopy(self.data)
        data["heldout"][0]["actual_i0_uc_measured"]=1
        with self.assertRaisesRegex(ValueError,"UC"):
            self.check(data)
        data=deepcopy(self.data)
        data["heldout"][0]["no_oracle_or_hidden_input_to_prediction"]=False
        with self.assertRaisesRegex(ValueError,"UC"):
            self.check(data)

    def test_false_exact_key_from_test_in_training_refused(self):
        data=deepcopy(self.data)
        data["summary"]["exact_fullstate_heldout_keys_known"]=1
        with self.assertRaises(ValueError):
            self.check(data)

    def test_removed_hidden_lethal_death_refused(self):
        data=deepcopy(self.data)
        index=next(i for i,x in enumerate(data["heldout"])
                   if x["physically_terminal_external_only"])
        data["heldout"][index]["physically_terminal_external_only"]=False
        with self.assertRaises(ValueError):
            self.check(data)

    def test_corrupted_six_component_heldout_score_refused(self):
        data=deepcopy(self.data)
        data["scores"][0]["actual_partial_target_external_only"]["food"]+=0.25
        with self.assertRaisesRegex(ValueError,"score was falsified"):
            self.check(data)

    def test_b_hidden_pair_preaction_equality_cannot_be_forged(self):
        data=deepcopy(self.data)
        index=next(i for i,x in enumerate(data["heldout"])
                   if x["preregistered_cohort"]=="NOMINAL"
                   and x["latent_berry_effect_external_only"]=="toxic_lethal")
        data["heldout"][index]["latent_berry_effect_external_only"]="benign"
        with self.assertRaises(ValueError):
            self.check(data)

    def test_hidden_motor_intervention_does_not_enter_firstperson_root(self):
        data=deepcopy(self.data)
        index=next(i for i,x in enumerate(data["heldout"])
                   if x["preregistered_cohort"]=="HIDDEN")
        data["heldout"][index]["preaction_first_person"]["hidden_lethal"]=True
        with self.assertRaises(ValueError):
            self.check(data)

    def test_original_log_cannot_be_replaced_by_fake_success(self):
        data=deepcopy(self.data)
        data["log"]="all tests pass"
        with self.assertRaisesRegex(ValueError,"runner log"):
            self.check(data)

    def test_archive_auditor_has_no_simulator_or_oracle_dependency(self):
        source=(Path(__file__).resolve().parents[1]/
                "scripts/audit_stage12_issue110_b_a230zt_independent_preaction.py"
               ).read_text()
        self.assertNotIn("from lab.",source)
        self.assertNotIn("import lab.",source)
        self.assertNotIn("from i0.",source)
        self.assertNotIn("import i0.",source)
        self.assertNotIn("run_stage12_issue110_b_a230zs",source)
        self.assertNotIn("WorldBody(",source)
        self.assertNotIn("SimulatorPlanner(",source)
        self.assertNotIn("Stage12Runtime(",source)


if __name__=="__main__":
    unittest.main()
