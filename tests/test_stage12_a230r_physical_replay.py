"""Adversarial standalone physics replay of sealed A2.30-P source worlds."""
from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from replay_stage12_issue110_b_a230r_physical import (
    read_locked_source,audit_technical_replay
)
from lab.determinism import canonical_causal_bytes,sha256_hex


class IndependentPhysicsReplayControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        original=read_locked_source(Path(os.environ["A230R_SOURCE"]))
        cls.training=original["a230p-training-manifest.json"]
        cls.tests=original["a230p-heldout-physical-results.json"]
        cls.summary=original["a230p-summary.json"]

    def audit(self,training=None,tests=None,summary=None):
        return audit_technical_replay(
            deepcopy(training if training is not None else self.training),
            deepcopy(tests if tests is not None else self.tests),
            deepcopy(summary if summary is not None else self.summary)
        )

    def test_entire_original_cohort_physically_replayed(self):
        result=self.audit()
        self.assertEqual(result["technical_replay_world_instances"],128)
        self.assertEqual(result["technical_replay_physical_steps"],352)
        self.assertEqual(result["physical_outcome_differences"],0)
        self.assertEqual(result["terminal_revivals"],0)
        self.assertEqual(result["new_i0_births"],0)
        self.assertEqual(result["new_independent_scientific_samples"],0)
        self.assertTrue(
            result["standalone_physics_engine_replay_not_external_world_truth"]
        )

    def test_tampered_hidden_physics_configuration_rejected(self):
        data=deepcopy(self.training)
        data["source_lab_physics"][0]["physical_config_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"configuration/layout"):
            self.audit(training=data)

    def test_tampered_hidden_layout_configuration_rejected(self):
        data=deepcopy(self.tests)
        data[0]["source_lab_physics"]["physical_layout_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"configuration/layout"):
            self.audit(tests=data)

    def test_fake_postbody_even_with_recomputed_example_hash_rejected(self):
        data=deepcopy(self.tests)
        physics=data[0]["source_lab_physics"]
        item=physics["observed_physical_examples"][0]
        e=item["physical_example"]
        e["observed_next_state"]["body"]["food"]+=3.0
        item["physical_example_sha256"]=sha256_hex(canonical_causal_bytes(e))
        with self.assertRaisesRegex(ValueError,"independent physical replay differs"):
            self.audit(tests=data)

    def test_falsified_terminal_flag_even_with_consistent_public_hash_rejected(self):
        data=deepcopy(self.tests)
        affected=next(row for row in data if row["witness"]["first_terminal_step"]==1)
        e=affected["source_lab_physics"]["observed_physical_examples"][0]
        e["physical_example"]["terminal"]=False
        e["physical_example_sha256"]=sha256_hex(
            canonical_causal_bytes(e["physical_example"])
        )
        with self.assertRaisesRegex(ValueError,"independent physical replay differs"):
            self.audit(tests=data)

    def test_attempt_to_change_executed_prefix_is_rejected(self):
        data=deepcopy(self.tests)
        data[0]["witness"]["commands"][0]["parameters"]["direction"]="south"
        with self.assertRaisesRegex(ValueError,"different command prefix"):
            self.audit(tests=data)

    def test_unsupported_hidden_variant_must_fail(self):
        data=deepcopy(self.tests)
        data[0]["source_lab_physics"]["hidden_variant_for_lab_only"]="invented_lethal"
        with self.assertRaisesRegex(ValueError,"not preregistered"):
            self.audit(tests=data)

    def test_reviewer_is_independent_of_original_learner_and_recorder(self):
        path=Path(__file__).resolve().parents[1]/
            "scripts/replay_stage12_issue110_b_a230r_physical.py"
        code=path.read_text()
        self.assertNotIn(
            "from run_stage12_issue110_b_a230p_joint_prefix_experiment import",
            code)
        self.assertNotIn(
            "from audit_stage12_issue110_b_a230p_joint_trajectories import",
            code)
        self.assertNotIn("EquipmentCorpusRecorder(",code)
        self.assertNotIn("Stage4Runtime(",code)
        self.assertNotIn("import Oracle",code)


if __name__=="__main__":
    unittest.main()
