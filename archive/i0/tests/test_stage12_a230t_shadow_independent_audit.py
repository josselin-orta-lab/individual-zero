"""Adversarial controls for the independent S first-person archive audit."""
from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from audit_stage12_issue110_b_a230t_shadow_archives import (
    from_archive,audit_independent
)


class FrozenShadowArchiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        x=from_archive(Path(os.environ["A230T_SOURCE_311"]))
        y=from_archive(Path(os.environ["A230T_SOURCE_312"]))
        if x!=y:
            raise AssertionError("two original frozen source archives differ")
        cls.worlds=json.loads(x["a230s-acted-worlds.json"])
        cls.passive=json.loads(x["a230s-passive-worlds.json"])
        cls.summary=json.loads(x["a230s-summary.json"])

    def audit(self,acted=None,passive=None,summary=None):
        return audit_independent(
            deepcopy(self.worlds if acted is None else acted),
            deepcopy(self.passive if passive is None else passive),
            deepcopy(self.summary if summary is None else summary),
        )

    def test_independent_same_world_shadow_root_proof_and_causal_aliasing(self):
        a=self.audit()
        self.assertTrue(a["all_original_56_shadow_root_proofs_recomputed"])
        self.assertEqual(a["external_shadow_plan_status"],"incomplete_model")
        self.assertEqual(a["original_worlds_archived"],72)
        self.assertEqual(a["original_physical_steps_archived"],196)
        self.assertEqual(a["paired_causal_aliases"],8)
        self.assertEqual(a["discriminating_waits"],4)
        self.assertEqual(a["uninformative_second_ingestions"],4)
        self.assertEqual(a["precommitted_retreated_survivors"],8)
        self.assertFalse(a["WorldBody_physics_independently_replayed"])
        self.assertFalse(a["Stage6_cognitive_change_deployed"])

    def test_corrupted_physical_example_sha_fails(self):
        x=deepcopy(self.worlds)
        x[0]["physical_records"][0]["physical_example_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"SHA mismatch"):
            self.audit(acted=x)

    def test_cognitive_history_cannot_include_future_event(self):
        x=deepcopy(self.worlds)
        q=x[0]["shadow_food"][0]
        q["previous_observed_steps"]=[1,2,3]
        q["history_examples_count"]=3
        with self.assertRaisesRegex(ValueError,"causal time boundary"):
            self.audit(acted=x)

    def test_false_known_first_step_is_rejected(self):
        x=deepcopy(self.worlds)
        x[0]["shadow_food"][0]["stage6_root_available_edges"]=1
        with self.assertRaisesRegex(ValueError,"root known/action count"):
            self.audit(acted=x)

    def test_forged_exogenous_hazard_is_rejected(self):
        x=deepcopy(self.worlds)
        scenario=next(z for z in x if z["variant_lab_only"]=="exogenous_confounded")
        scenario["external_environment_interventions"][0]["active"]=False
        with self.assertRaisesRegex(ValueError,"intervention"):
            self.audit(acted=x)

    def test_fake_ingestion_effect_rejected_even_if_summary_unchanged(self):
        x=deepcopy(self.worlds)
        source=x[0]["physical_records"][2]
        source["state_after"]["body"]["integrity"]=82.0
        with self.assertRaisesRegex(ValueError,"SHA mismatch"):
            self.audit(acted=x)

    def test_post_terminal_continuation_is_rejected(self):
        x=deepcopy(self.worlds)
        source=next(z for z in x if z["first_terminal_step"] is not None)
        source["physical_records"].append(deepcopy(source["physical_records"][-1]))
        source["physical_step_count"]+=1
        with self.assertRaisesRegex(ValueError,"SHA mismatch|postterminal"):
            self.audit(acted=x)

    def test_world_identity_reuse_and_passive_fake_action_fail(self):
        x=deepcopy(self.worlds)
        x[1]["id"]=x[0]["id"]
        with self.assertRaisesRegex(ValueError,"identifier|repeated"):
            self.audit(acted=x)
        y=deepcopy(self.passive)
        y[0]["world_steps_applied"]=1
        with self.assertRaisesRegex(ValueError,"passive world"):
            self.audit(passive=y)

    def test_auditor_does_not_import_original_shadow_or_physical_engine(self):
        p=Path(__file__).resolve().parents[1]/"scripts"/(
            "audit_stage12_issue110_b_a230t_shadow_archives.py"
        )
        c=p.read_text()
        self.assertNotIn("from run_stage12_issue110_b_a230s_firstperson_shadow import",c)
        self.assertNotIn("from lab.world import",c)
        self.assertNotIn("from i0.modules.stage6_planning import",c)
        self.assertNotIn("train_exact_transition_table",c)


if __name__=="__main__":
    unittest.main()
