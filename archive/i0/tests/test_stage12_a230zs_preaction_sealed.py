"""A2.30-ZS: test the ONE original preregistered 120-world experiment.

Tests only READ the existing physical source, frozen training model, durable
pre-action ledger and post-action sealed outcomes. Never instantiate or apply
WorldBody in tests, and never count a Python rerun as additional I0 births.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from run_stage12_issue110_b_a230zs_preaction_sealed import (
    PREDICT,OUTCOME,LEDGER_RECORDS,MODEL_FREEZE_FILE,LEDGER_FILE,
    PRE_REGISTERED_SHA,ZO_MODEL_FINGERPRINT,GENESIS,
    audit_chain,digest,parse_chain,
)


def resign_and_serialize(events):
    """Even a fully rehashed forged chain must fail semantic integrity tests."""
    former=GENESIS
    copy=deepcopy(events)
    for i,ev in enumerate(copy):
        ev["prev_sha256"]=former
        ev["seq"]=i+1
        envelope={k:ev[k] for k in (
            "seq","prev_sha256","kind","payload"
        )}
        ev["event_sha256"]=digest(envelope)
        former=ev["event_sha256"]
    return b"".join(
        (json.dumps(x,sort_keys=True,separators=(",",":"))+"\n").encode("utf-8")
        for x in copy
    )


class DurablePreactionPhysicalForecastTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folder=Path(os.environ["A230ZS_ORIGINAL_SOURCE"])
        cls.training=json.loads(
            (cls.folder/"a230zs-physical-training.json").read_bytes()
        )
        cls.freeze_file=cls.folder/MODEL_FREEZE_FILE
        cls.freeze=json.loads(cls.freeze_file.read_bytes())
        cls.freeze_sha=sha256(cls.freeze_file.read_bytes()).hexdigest()
        cls.raw=(cls.folder/LEDGER_FILE).read_bytes()
        cls.entries=parse_chain(cls.raw)
        cls.heldout=json.loads(
            (cls.folder/"a230zs-heldout-worlds.json").read_bytes()
        )
        cls.scores=json.loads(
            (cls.folder/"a230zs-postaction-scoring.json").read_bytes()
        )
        cls.summary=json.loads(
            (cls.folder/"a230zs-summary.json").read_bytes()
        )

    def verify(self,entries=None,training=None,freeze=None,heldout=None,
               no_rehash=False):
        raw=(self.raw if entries is None else
             resign_and_serialize(entries))
        return audit_chain(
            raw,
            deepcopy(self.training if training is None else training),
            deepcopy(self.freeze if freeze is None else freeze),
            deepcopy(self.heldout if heldout is None else heldout),
            self.freeze["model_sha256"],
            self.freeze_sha,
        )

    def test_original_exact_120_world_104_forecast_prospective_cohort(self):
        s=self.summary
        self.assertEqual(s["schema"],"a230zs-durable-preaction-heldout-v1")
        self.assertEqual(s["ZS_preregistered_before_code_sha"],PRE_REGISTERED_SHA)
        self.assertEqual(s["actual_total_independent_new_physical_worlds"],120)
        self.assertEqual(s["train_physical_before_frozen_model"],16)
        self.assertEqual(s["new_heldout_physical_worlds"],104)
        self.assertEqual(s["actual_physical_actions"],120)
        self.assertEqual(s["preaction_fsync_receipts"],104)
        self.assertEqual(s["postaction_fsync_receipts"],104)
        self.assertEqual(s["valid_durable_events"],LEDGER_RECORDS)
        self.assertEqual(s["numerical_forecast_receipts"],88)
        self.assertEqual(s["clamp_abstention_receipts"],16)
        self.assertEqual(s["fatal_outcome_receipts_external"],4)
        self.assertEqual(s["nominal_six_component_physically_exact"],64)
        self.assertEqual(s["hazard_hidden_motor_deaths"],4)
        self.assertEqual(s["hazard_hidden_integrity_injuries"],8)
        self.assertEqual(s["hazard_forced_primitive_failures"],8)
        self.assertEqual(s["boundary_abstentions"],16)
        self.assertEqual(s["new_I0_births"],0)
        self.assertEqual(s["new_I0_autonomous_steps"],0)
        self.assertFalse(s["I0_UC_measured"])
        self.assertFalse(s["normative_MVP_or_cognition_changed"])
        self.assertFalse(s["full_independent_external_timing_attestation"])
        self.assertTrue(s["ledger_durable_flush_fsync_called_before_each_physical_apply"])
        self.assertEqual(s["operator_deployment"],"NO-GO")

    def test_sha_chain_and_original_file_receipts(self):
        self.assertEqual(self.verify()["valid_durable_events"],208)
        self.assertEqual(len(self.entries),208)
        self.assertEqual(len(self.heldout),104)
        self.assertEqual(len(self.training),16)
        self.assertEqual(
            self.summary["ledger_raw_file_sha256"],
            sha256(self.raw).hexdigest(),
        )
        self.assertEqual(
            self.summary["durable_model_file_sha256"],self.freeze_sha,
        )
        self.assertEqual(
            self.summary["chain_head_sha256"],
            self.entries[-1]["event_sha256"],
        )
        self.assertEqual(
            self.freeze["model_sha256"],ZO_MODEL_FINGERPRINT,
        )
        self.assertEqual(
            self.freeze["training_physical_source_sha256"],
            digest(self.training),
        )
        self.assertEqual(
            self.summary["heldout_source_data_sha256"],
            digest(self.heldout),
        )
        self.assertEqual(
            self.summary["heldout_numeric_scores_sha256"],
            digest(self.scores),
        )

    def test_every_heldout_action_has_PRE_and_then_POST_with_external_hazard(self):
        ids=set()
        for i in range(104):
            a,z=self.entries[i*2:i*2+2]
            self.assertEqual([a["kind"],z["kind"]],[PREDICT,OUTCOME])
            self.assertEqual(a["payload"]["world_token"],z["payload"]["world_token"])
            self.assertNotIn("intervention",a["payload"])
            self.assertNotIn("latent",a["payload"])
            self.assertEqual(
                z["payload"]["linked_preaction_event_sha256"],
                a["event_sha256"],
            )
            self.assertTrue(a["payload"]["no_action_yet_executed_for_this_world"])
            self.assertTrue(a["payload"]["no_hidden_world_parameters_in_forecast"])
            for key in ("integrity","terminal","next_adjacency","safe"):
                self.assertIsNone(a["payload"]["frozen_partial_forecast"][key])
            self.assertIsNone(z["payload"]["postterminal_lived_capture"])
            self.assertNotIn("manger",z["payload"]["action_physically_applied"]["primitive"])
            ids.add(z["payload"]["world_id_external_only"])
        self.assertEqual(len(ids),104)
        self.assertTrue(all(x.startswith("a230zs:") for x in ids))

    def test_unscored_source_model_is_frozen_before_first_heldout_world(self):
        f=self.freeze
        self.assertEqual(f["training_worlds"],16)
        self.assertEqual(f["training_examples_per_command"],{
            "MOVE_E":8,"COLLECT_B":8,
        })
        self.assertTrue(f["contains_no_heldout_worlds"])
        self.assertTrue(f["no_production_i0_model_contract"])
        self.assertTrue(all(k is None for k in (
            f["model"]["MOVE_E"]["unresolved_integrity"],
            f["model"]["MOVE_E"]["unresolved_terminality"],
            f["model"]["COLLECT_B"]["unresolved_food_safety"],
        )))
        self.assertNotEqual(f["exact_equipment_source_sha256"],f["model_sha256"])

    def test_remove_one_forecast_fails_even_after_rehash(self):
        bad=deepcopy(self.entries)
        del bad[10]
        with self.assertRaisesRegex(ValueError,"missing or duplicated"):
            parse_chain(resign_and_serialize(bad))

    def test_swap_outcome_and_forecast_fails_even_after_rehash(self):
        bad=deepcopy(self.entries)
        bad[0],bad[1]=bad[1],bad[0]
        with self.assertRaisesRegex(ValueError,"before action"):
            parse_chain(resign_and_serialize(bad))

    def test_break_original_sha_chain_fails(self):
        bad=deepcopy(self.entries)
        bad[0]["payload"]["command_label"]="COLLECT_B"
        with self.assertRaisesRegex(ValueError,"SHA-256"):
            parse_chain(b"".join(
                (json.dumps(e,separators=(",",":"))+"\n").encode("utf-8")
                for e in bad
            ))

    def test_even_rehashed_fake_numeric_prediction_fails(self):
        bad=deepcopy(self.entries)
        bad[0]["payload"]["frozen_partial_forecast"]["estimated"]["x"]=12345
        with self.assertRaisesRegex(ValueError,"differs from frozen"):
            self.verify(bad)

    def test_fake_hidden_toxicity_in_preaction_schema_fails(self):
        bad=deepcopy(self.entries)
        bad[0]["payload"]["hidden_lethal_zone"]=False
        with self.assertRaisesRegex(ValueError,"unexpected fields"):
            self.verify(bad)

    def test_false_safe_label_or_terminal_none_replaced_fails(self):
        for k,value in (
            ("safe",True),("terminal",False),
            ("integrity",100),("next_adjacency",[]),
        ):
            bad=deepcopy(self.entries)
            bad[0]["payload"]["frozen_partial_forecast"][k]=value
            with self.assertRaisesRegex(ValueError,"never frozen"):
                self.verify(bad)

    def test_forged_training_model_fails_even_with_same_hash_claim(self):
        frozen=deepcopy(self.freeze)
        frozen["model"]["MOVE_E"]["supported_empirical_deltas"]["x"]=999
        with self.assertRaisesRegex(ValueError,"frozen training-only"):
            self.verify(freeze=frozen)

    def test_actual_heldout_sample_added_to_training_fails(self):
        training=deepcopy(self.training)
        training[0]=deepcopy(self.heldout[0])
        with self.assertRaises(ValueError):
            self.verify(training=training)

    def test_wrong_preaction_model_sha_in_ledger_fails(self):
        bad=deepcopy(self.entries)
        bad[0]["payload"]["source_training_model_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"never frozen"):
            self.verify(bad)

    def test_wrong_preaction_state_in_ledger_fails(self):
        bad=deepcopy(self.entries)
        bad[0]["payload"]["preaction_accessible_state"]["x"]+=1
        with self.assertRaisesRegex(ValueError,"never frozen"):
            self.verify(bad)

    def test_counterfactual_external_terminal_as_lived_capture_fails(self):
        bad=deepcopy(self.heldout)
        target=next(x for x in bad if x["physically_terminal_external_only"])
        target["postdeath_lived_capture"]=target["postaction_external_only"]
        with self.assertRaisesRegex(ValueError,"physical example or UC"):
            self.verify(heldout=bad)

    def test_fake_I0_UC_or_forced_physical_action_fails(self):
        bad=deepcopy(self.heldout)
        bad[0]["actual_i0_uc_measured"]=10
        with self.assertRaisesRegex(ValueError,"physical example or UC"):
            self.verify(heldout=bad)
        bad=deepcopy(self.heldout)
        bad[0]["action_physically_applied"]={
            "primitive":"manger","parameters":{"target":"berry_b"}
        }
        with self.assertRaises(ValueError):
            self.verify(heldout=bad)

    def test_hidden_forced_failure_cannot_be_score_as_nominal(self):
        failures=[
            i for i,row in enumerate(self.heldout)
            if row["hidden_intervention_external_only"]==
            "hidden_forced_action_failure"
        ]
        self.assertEqual(len(failures),8)
        for i in failures:
            self.assertIs(
                self.scores[i]["all_six_components_match_external_only"],
                False,
            )
        forged=deepcopy(self.heldout)
        forged[failures[0]]["hidden_intervention_external_only"]="none"
        with self.assertRaisesRegex(ValueError,"joined after prediction"):
            self.verify(heldout=forged)

    def test_four_terminal_motor_hazards_never_get_subjective_followup(self):
        terminal=[(i,row) for i,row in enumerate(self.heldout)
                  if row["physically_terminal_external_only"]]
        self.assertEqual(len(terminal),4)
        for i,row in terminal:
            self.assertEqual(row["hidden_intervention_external_only"],
                             "hidden_lethal_east")
            self.assertEqual(row["command_label"],"MOVE_E")
            self.assertIsNone(row["postdeath_lived_capture"])
            after=self.entries[2*i+1]["payload"]
            self.assertTrue(after["physical_terminal_external_only"])
            self.assertTrue(after["world_terminal_frozen"])

    def test_physical_apply_occurs_only_after_fsynced_prediction(self):
        source=(Path(__file__).resolve().parents[1]/
            "scripts/run_stage12_issue110_b_a230zs_preaction_sealed.py"
        ).read_text()
        block=source.split("def prospective_one(",1)[1].split("def parse_chain(",1)[0]
        self.assertLess(block.index("ledger.append(PREDICT,first)"),
                        block.index("recorder.record_transition("))
        append=source.split("class DurableForecastLedger:",1)[1].split(
            "def prepare_training(",1
        )[0]
        self.assertIn("os.fsync(f.fileno())",append)
        self.assertNotIn("Stage12Runtime(",source)
        self.assertNotIn("life.run_step(",source)
        self.assertNotIn("from lab.oracle import",source)


if __name__=="__main__":
    unittest.main()
