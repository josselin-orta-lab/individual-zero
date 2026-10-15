"""A2.30-U corruption controls against sealed S/T/P experiment archives."""
from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from audit_stage12_issue110_b_a230u_independent import (
    read_equal_archive,sealed_files,independent_P_food_branches,
    review_S,review_T,S_FILES,T_FILES,
)


class SAndTBlindArchiveControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        s,_=read_equal_archive(
            Path(os.environ["A230U_S311"]),Path(os.environ["A230U_S312"]),S_FILES
        )
        t,_=read_equal_archive(
            Path(os.environ["A230U_T311"]),Path(os.environ["A230U_T312"]),T_FILES
        )
        p=sealed_files(Path(os.environ["A230U_P"]),(
            "a230p-training-manifest.json",
        ))
        cls.s_worlds=s["a230s-worlds.json"]
        cls.s_pairs=s["a230s-pairs.json"]
        cls.s_summary=s["a230s-summary.json"]
        cls.t_worlds=t["a230t-worlds.json"]
        cls.t_pairs=t["a230t-paired.json"]
        cls.t_summary=t["a230t-summary.json"]
        cls.p_scores=independent_P_food_branches(
            json.loads(p["a230p-training-manifest.json"])
        )

    def s(self,worlds=None,pairs=None,summary=None):
        return review_S(
            deepcopy(self.s_worlds if worlds is None else worlds),
            deepcopy(self.s_pairs if pairs is None else pairs),
            deepcopy(self.s_summary if summary is None else summary)
        )

    def t(self,worlds=None,pairs=None,summary=None):
        return review_T(
            deepcopy(self.t_worlds if worlds is None else worlds),
            deepcopy(self.t_pairs if pairs is None else pairs),
            deepcopy(self.t_summary if summary is None else summary),
            deepcopy(self.p_scores),
        )

    def test_all_original_s_t_data_independently_recalculated(self):
        s=self.s()
        t=self.t()
        self.assertEqual(s["worlds"],36)
        self.assertEqual(s["physical_receipts"],104)
        self.assertEqual(s["external_terminals"],8)
        self.assertEqual(s["mutually_observable_differences"],20)
        self.assertEqual(s["undistinguishable_due_to_terminal_branch"],16)
        self.assertEqual(t["worlds"],40)
        self.assertEqual(t["physical_receipts"],132)
        self.assertEqual(t["actual_surviving_food_goals"],24)
        self.assertEqual(t["optimistic_proxy_false_successes"],16)
        self.assertEqual(t["external_terminals"],8)
        self.assertEqual(t["shadow_safety_certificates"],0)

    def test_forged_S_physical_hash_rejected(self):
        examples=deepcopy(self.s_worlds)
        examples[0]["external_physical_evidence"][0]["physical_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"SHA altered"):
            self.s(worlds=examples)

    def test_forged_postterminal_lived_capture_rejected(self):
        examples=deepcopy(self.s_worlds)
        victim=next(x for x in examples if x["terminal_step_external_only"])
        last=victim["external_physical_evidence"][-1]
        victim["possible_lived_captures"].append({
            "after_step":last["step"],
            "state":last["after_for_external_audit_only"],
        })
        with self.assertRaisesRegex(ValueError,"postterminal"):
            self.s(worlds=examples)

    def test_forged_S_external_death_step_rejected(self):
        examples=deepcopy(self.s_worlds)
        victim=next(x for x in examples if x["terminal_step_external_only"])
        victim["terminal_step_external_only"]=None
        with self.assertRaisesRegex(ValueError,"terminal physical"):
            self.s(worlds=examples)

    def test_S_early_oracle_discrimination_rejected(self):
        comparisons=deepcopy(self.s_pairs)
        comparison=next(x for x in comparisons if x["family"]=="FOOD")
        comparison["first_mutually_lived_difference"]=1
        comparison["discrimination_before_exposure"]=True
        with self.assertRaisesRegex(ValueError,"discrimination evidence"):
            self.s(pairs=comparisons)

    def test_T_fabricated_forecast_input_rejected(self):
        worlds=deepcopy(self.t_worlds)
        worlds[0]["shadow_forecast_precommitted"]["input_stage3_state"][
            "body"]["food"]=99.0
        with self.assertRaisesRegex(ValueError,"predicted input"):
            self.t(worlds=worlds)

    def test_T_fake_safety_certificate_rejected(self):
        worlds=deepcopy(self.t_worlds)
        worlds[0]["shadow_forecast_precommitted"]["certifies_safe"]=True
        with self.assertRaisesRegex(ValueError,"certainty"):
            self.t(worlds=worlds)

    def test_T_false_lived_postmortem_food_rejected(self):
        worlds=deepcopy(self.t_worlds)
        died=next(x for x in worlds if x["terminal_step_external_only"])
        died["potential_lived_post_ingestion_if_survivor"]={
            "body":{"food":999.0}
        }
        with self.assertRaisesRegex(ValueError,"postterminal"):
            self.t(worlds=worlds)

    def test_T_false_positive_goal_result_rejected(self):
        worlds=deepcopy(self.t_worlds)
        died=next(x for x in worlds if x["terminal_step_external_only"])
        died["physical_food_goal_with_survival_external"]=True
        with self.assertRaisesRegex(ValueError,"food success"):
            self.t(worlds=worlds)

    def test_T_tampered_optimistic_branch_rejected(self):
        worlds=deepcopy(self.t_worlds)
        worlds[0]["shadow_forecast_precommitted"]["branch_scores"][0][
            "surviving_food_goal_possible_in_branch"
        ]=False
        with self.assertRaisesRegex(ValueError,"sealed shadow receipt|P outcomes"):
            self.t(worlds=worlds)

    def test_T_duplicate_world_rejected(self):
        worlds=deepcopy(self.t_worlds)
        worlds[1]["id"]=worlds[0]["id"]
        with self.assertRaisesRegex(ValueError,"duplicate T shadow"):
            self.t(worlds=worlds)

    def test_T_corrupt_aggregate_rejected(self):
        summary=deepcopy(self.t_summary)
        summary["per_arm"]["no_wait"]["physical_surviving_food_goal"]=19
        with self.assertRaisesRegex(ValueError,"per-arm metrics"):
            self.t(summary=summary)

    def test_independent_auditor_never_imports_original_models_or_world(self):
        auditor=(Path(__file__).resolve().parents[1]/"scripts" /
                 "audit_stage12_issue110_b_a230u_independent.py").read_text()
        self.assertNotIn("from lab.world import",auditor)
        self.assertNotIn("from run_stage12_issue110_b_a230s",auditor)
        self.assertNotIn("from run_stage12_issue110_b_a230t",auditor)
        self.assertNotIn("from audit_stage12_issue110_b_a230p_joint",auditor)
        self.assertNotIn("WorldBody(",auditor)
        self.assertNotIn("Stage4Runtime(",auditor)


if __name__=="__main__":
    unittest.main()
