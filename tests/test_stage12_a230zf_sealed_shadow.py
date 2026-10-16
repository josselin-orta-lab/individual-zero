"""Negative tests for independent A2.30-ZF source-only Stage6 proof audit."""
from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from audit_stage12_issue110_b_a230zf_sealed_shadow import (
    independent_physical_training, independent_reaudit,
    read_sealed, recheck_trial, exact_key, valid_perception,
)


class NoLeakPhysicalStage6ArchiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        first=read_sealed(Path(os.environ["A230ZF_SOURCE_311"]))
        second=read_sealed(Path(os.environ["A230ZF_SOURCE_312"]))
        if first!=second:
            raise AssertionError("original Python results differ in bytes")
        cls.training=json.loads(first["a230ze-training-manifest.json"])
        cls.testcases=json.loads(first["a230ze-heldout-shadows.json"])
        cls.original=json.loads(first["a230ze-summary.json"])
        cls.proof=independent_reaudit(
            cls.training,cls.testcases,cls.original
        )

    def check(self,training=None,heldout=None,summary=None):
        return independent_reaudit(
            deepcopy(self.training if training is None else training),
            deepcopy(self.testcases if heldout is None else heldout),
            deepcopy(self.original if summary is None else summary),
        )

    def test_frozen_sources_have_expected_non_ingestion_world_counts(self):
        s=self.proof
        self.assertEqual(s["physical_source_worlds_reaudited"],9)
        self.assertEqual(s["physical_source_steps_reaudited"],13)
        self.assertEqual(s["heldout_worlds_reaudited"],24)
        self.assertEqual(s["heldout_worlds_physically_applied"],0)
        self.assertEqual(s["A_only_exact_input_keys"],1)
        self.assertEqual(s["unique_exact_input_keys"],7)
        self.assertEqual(s["new_I0_births"],0)
        self.assertEqual(s["new_physical_steps"],0)
        self.assertFalse(s["stage6_reexecuted_by_independent_archive_auditor"])
        self.assertFalse(s["worldbody_apply_independently_replayed_from_archive"])
        self.assertTrue(s["benign_and_toxic_variants_both_present_in_demonstrations"])

    def test_stage6_exacts_match_preregistered_eight_sixteen_split(self):
        t=self.proof["cohorts"]
        self.assertEqual(t["same_observable_input"]["baseline_incomplete"],8)
        self.assertEqual(t["same_observable_input"]["enriched_partial_progress"],8)
        self.assertEqual(t["same_observable_input"]["enriched_known_root"],8)
        self.assertEqual(t["same_observable_input"]["false_eat_prediction"],0)
        for name in ("unseen_coordinates","unavailable_or_blocked"):
            self.assertEqual(t[name]["test_worlds"],8)
            self.assertEqual(t[name]["baseline_incomplete"],8)
            self.assertEqual(t[name]["enriched_incomplete"],8)
            self.assertEqual(t[name]["enriched_known_root"],0)

    def test_physical_demonstrator_branches_are_contiguous_nonlethal(self):
        p=independent_physical_training(self.training)
        self.assertEqual(len(p["records"]),13)
        for x in p["records"]:
            self.assertFalse(x["terminal"])
            self.assertNotEqual(x["command"]["primitive"],"manger")
        sources=p["source_worlds"]
        self.assertEqual(len(sources),9)
        self.assertTrue(all(x["no_terminal"] for x in sources.values()))

    def test_tampered_executed_physical_example_sha_invalid(self):
        fake=deepcopy(self.training)
        fake["demonstrations"][0]["physical_example_sha256"][0]="0"*64
        with self.assertRaisesRegex(ValueError,"noncontiguous noningestive physical example"):
            self.check(training=fake)

    def test_hallucinated_B_ingestion_training_command_rejected(self):
        fake=deepcopy(self.training)
        source=next(x for x in fake["demonstrations"]
                    if x["layout_external_only"]=="B_LOCAL")
        source["observed_physical_examples"][0]["command"]={
            "primitive":"manger","parameters":{"target":"berry_b"}
        }
        with self.assertRaisesRegex(ValueError,"noncontiguous noningestive"):
            self.check(training=fake)

    def test_oracular_toxicity_field_in_initial_input_rejected(self):
        fake=deepcopy(self.testcases)
        fake[0]["first_person_state"]["hidden_B_lethality"]=True
        with self.assertRaisesRegex(ValueError,"hidden or future"):
            self.check(heldout=fake)

    def test_false_positive_plan_found_cannot_replace_partial(self):
        fake=deepcopy(self.testcases)
        row=next(x for x in fake if x["cohort"]=="same_observable_input")
        row["enriched_demonstrated_prefix"]["status"]="plan_found"
        with self.assertRaisesRegex(ValueError,"Stage6 shadow invented"):
            self.check(heldout=fake)

    def test_unsupported_ood_fabricated_first_edge_rejected(self):
        fake=deepcopy(self.testcases)
        row=next(x for x in fake if x["cohort"]=="unseen_coordinates")
        row["enriched_demonstrated_prefix"]["root_available_edges"]=1
        with self.assertRaisesRegex(ValueError,"Stage6 shadow invented"):
            self.check(heldout=fake)

    def test_blocked_east_cannot_become_passable_in_record(self):
        fake=deepcopy(self.testcases)
        row=next(x for x in fake if x["layout_external_only"]=="B_EAST_BLOCKED")
        east=next(n for n in row["first_person_state"]["adjacent"]
                  if n["direction"]=="east")
        east["passable"]=True
        with self.assertRaisesRegex(ValueError,"visible resource/obstacle"):
            self.check(heldout=fake)

    def test_duplicate_hidden_scenario_rejected_in_same_cohort(self):
        fake=deepcopy(self.testcases)
        same=[x for x in fake if x["cohort"]=="unavailable_or_blocked"]
        same[1]["layout_external_only"]=same[0]["layout_external_only"]
        same[1]["food_initial"]=same[0]["food_initial"]
        same[1]["hidden_effect_external_only"]=same[0][
            "hidden_effect_external_only"]
        with self.assertRaises(ValueError):
            self.check(heldout=fake)

    def test_test_world_CANNOT_be_renamed_as_its_training_world(self):
        fake=deepcopy(self.testcases)
        row=next(x for x in fake if x["cohort"]=="same_observable_input")
        row["world_id"]=row["paired_physical_demonstrator"]
        with self.assertRaisesRegex(ValueError,"test world was secretly trained"):
            self.check(heldout=fake)

    def test_no_physical_heldout_or_I0_UC_fabricated(self):
        fake=deepcopy(self.testcases)
        fake[0]["physical_steps_executed_in_heldout_world"]=1
        with self.assertRaisesRegex(ValueError,"test world was secretly trained"):
            self.check(heldout=fake)
        fake2=deepcopy(self.testcases)
        fake2[0]["enriched_demonstrated_prefix"]["true_I0_UC_measured"]=2
        with self.assertRaisesRegex(ValueError,"Stage6 shadow invented"):
            self.check(heldout=fake2)

    def test_byte_compare_and_independent_boundaries(self):
        script=(Path(__file__).resolve().parents[1]/
            "scripts/audit_stage12_issue110_b_a230zf_sealed_shadow.py"
        ).read_text()
        self.assertNotIn(
            "from run_stage12_issue110_b_a230ze_model_coverage import",script
        )
        self.assertNotIn("WorldBody(",script)
        self.assertNotIn("SimulatorPlanner(",script)
        self.assertNotIn("Stage12Runtime(",script)
        self.assertNotIn("build_life(",script)
        self.assertNotIn(".run_step(",script)


if __name__=="__main__":
    unittest.main()
