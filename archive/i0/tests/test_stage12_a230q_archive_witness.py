"""A2.30-Q archive-audit negative controls on the original locked P source."""
from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from audit_stage12_issue110_b_a230q_independent_archives import (
    sealed_source,independently_audit
)


class PhysicalArchiveTamperingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        original=sealed_source(Path(os.environ["A230Q_SOURCE_311"]))
        second=sealed_source(Path(os.environ["A230Q_SOURCE_312"]))
        if original!=second:
            raise AssertionError("the two language-version archives differ")
        cls.train=json.loads(original["a230p-training-manifest.json"])
        cls.heldout=json.loads(original["a230p-heldout-physical-results.json"])
        cls.summary=json.loads(original["a230p-summary.json"])

    def audit(self,train=None,heldout=None,summary=None):
        return independently_audit(
            deepcopy(train if train is not None else self.train),
            deepcopy(heldout if heldout is not None else self.heldout),
            deepcopy(summary if summary is not None else self.summary),
        )

    def test_independent_all_worlds_and_bounded_findings(self):
        out=self.audit()
        self.assertEqual(out["original_worlds_checked"],128)
        self.assertEqual(out["original_steps_checked"],352)
        self.assertEqual(out["id_joint_matches"],48)
        self.assertEqual(out["ood_novel_joint_branches"],24)
        self.assertEqual(out["unknown_context_abstentions"],8)
        self.assertEqual(out["late_deaths_without_first_step_terminal_example"],8)
        self.assertEqual(out["ood_terminal_step_misses"],8)
        self.assertEqual(out["new_i0_lives"],0)
        self.assertEqual(out["new_physical_steps"],0)
        self.assertFalse(out["safe_model_deployment_proven"])
        self.assertFalse(out["physical_worldbody_apply_independently_proven_from_json"])

    def test_forged_physical_example_sha_is_rejected(self):
        data=deepcopy(self.train)
        data["source_lab_physics"][0]["observed_physical_examples"][0][
            "physical_example_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"physical example tampered"):
            self.audit(train=data)

    def test_false_terminal_flag_is_rejected(self):
        data=deepcopy(self.heldout)
        data[0]["witness"]["steps"][0]["terminal"]=True
        with self.assertRaisesRegex(ValueError,"physical terminal mismatch"):
            self.audit(heldout=data)

    def test_postdeath_extension_is_rejected(self):
        data=deepcopy(self.heldout)
        event=next(
            p for p in data if p["witness"]["first_terminal_step"]==1
        )
        physics=event["source_lab_physics"]
        fake=deepcopy(physics["observed_physical_examples"][-1])
        fake["t_monde"]=2
        physics["observed_physical_examples"].append(fake)
        with self.assertRaisesRegex(ValueError,"different world-step counts"):
            self.audit(heldout=data)

    def test_fake_known_branch_is_rejected(self):
        data=deepcopy(self.heldout)
        unknown=next(x for x in data if
                     x["stage"]=="heldout_unknown_context")
        unknown["model"]["status"]="observed_joint_branches"
        with self.assertRaisesRegex(ValueError,"unseen context"):
            self.audit(heldout=data)

    def test_falsely_certified_safety_is_rejected(self):
        data=deepcopy(self.heldout)
        data[0]["model"]["certifies_safe"]=True
        with self.assertRaisesRegex(ValueError,"fake certainty"):
            self.audit(heldout=data)

    def test_invented_branch_rejected_even_when_input_known(self):
        data=deepcopy(self.heldout)
        initial=next(x for x in data if x["stage"]=="heldout_ID")
        branch=deepcopy(initial["model"]["empirical_branches"][0])
        branch["fingerprint"]="0"*64
        initial["model"]["empirical_branches"].append(branch)
        with self.assertRaisesRegex(ValueError,"branch count"):
            self.audit(heldout=data)

    def test_duplicate_training_test_world_invalid(self):
        data=deepcopy(self.heldout)
        data[0]["world_id"]=self.train["training_witnesses"][0]["world_id"]
        with self.assertRaisesRegex(ValueError,"world"):
            self.audit(heldout=data)

    def test_hiding_terminal_in_statistics_rejected(self):
        data=deepcopy(self.summary)
        data["strata"]["heldout_ID"]["late_terminal_worlds"]=0
        with self.assertRaisesRegex(ValueError,"strata metrics mismatch"):
            self.audit(summary=data)

    def test_reviewer_does_not_import_model_world_or_oracle(self):
        auditor=(Path(__file__).resolve().parents[1]/
            "scripts/audit_stage12_issue110_b_a230q_independent_archives.py").read_text()
        self.assertNotIn(
            "from audit_stage12_issue110_b_a230p_joint_trajectories import",auditor)
        self.assertNotIn(
            "from run_stage12_issue110_b_a230p_joint_prefix_experiment import",auditor)
        self.assertNotIn("from lab.world import",auditor)
        self.assertNotIn("import Oracle",auditor)


if __name__=="__main__":
    unittest.main()
