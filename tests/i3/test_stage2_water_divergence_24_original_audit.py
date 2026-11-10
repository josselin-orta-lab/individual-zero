"""Read-only post-original 48-life F0 water/replay auditor failure-mode tests."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from i3.lab import stage2_water_divergence_24_original_audit as A


class WaterDivergenceOriginalAuditTests(unittest.TestCase):
    def test_pinned_source_scope_and_no_biological_permission(self):
        self.assertEqual(A.PAIRS,24)
        self.assertEqual(A.HORIZON,400)
        for x in (A.FINGERPRINT,A.PLAN_SHA,A.WITNESS_SHA,A.MANIFEST_SHA):
            self.assertEqual(len(x),64)
        self.assertEqual(len(A.SOURCE),40)
        self.assertEqual(A.POLICIES,
                         ("p13_replay_gate_v1","p13_replay_gate_random_content_v1"))

    def test_missing_originals_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(FileNotFoundError):
                A.audit(Path(d))

    def test_family_failure_or_modified_first_difference_must_fail(self):
        good={"stable":{"belief_after":3},
              "depletion":{"belief_after":5},
              "pulse":{"belief_after":2}}
        A._same_tree(good,deepcopy(good))
        for modified in (
            {"stable":{"belief_after":3},"depletion":{"belief_after":5}},
            {"stable":{"belief_after":3},"depletion":{"belief_after":4},
             "pulse":{"belief_after":2}},
            {"stable":{"belief_after":3},"depletion":{"belief_after":5},
             "pulse":{"belief_after":2},"new":{"belief_after":0}},
        ):
            with self.subTest(modified=modified),self.assertRaises(ValueError):
                A._same_tree(good,modified)

    def test_paired_content_and_observed_equal_state_temporal_order(self):
        rows=[]
        for i in range(A.PAIRS):
            for arm,policy in enumerate(A.POLICIES):
                step={"step":1,"action":"dormir","param":None,
                      "decision_option":"dormir",
                      "pre_replay_state_sha256":"same",
                      "replay_count_prepaid":2,
                      "replay_memory_indices":[0,1] if arm==0 else [1,2],
                      "replay_priority_indices":[0,1],
                      "personal_water_belief_sha256":"same_water",
                      "personally_learned_drink_effect":None,
                      "predecision_learned_values_sha256":"same_values",
                      "predecision_personal_buffer_sha256":"same_buffer",
                      "postlearning_values_sha256":"different" if arm else "old",
                      "capture_water_before_decision":38,
                      "positive_water_uptake":False,
                      "paid_replays_actual":2}
                rows.append({
                    "index":510000+i,
                    "pair_id":f"water-div-{i:06d}",
                    "cohort":"development","family":A.FAMILIES[i%3],
                    "world_seed":10000+i,"genome_seed":20000+i,
                    "life_seed":30000+i,"policy":policy,
                    "world_sha256":"world"+str(i),
                    "genome_sha256":"genome"+str(i),"source_sha256":"source",
                    "terminal":"censored","steps_lived":400,
                    "dead_at_horizon":False,"paid_energy":1.,
                    "paid_vigilance":1.,"replays_paid":2,
                    "sleep_steps":1,
                    "random_content_receipt":(
                        {"distinct_from_priority_subsets":1,
                         "paid_replay_opportunities":1} if arm else None),
                    "chronology":{
                        "schema":"i3-stage2.1-replay-water-chronology/v1",
                        "steps":[step]},
                })
        summary=A._summaries(rows)
        self.assertEqual(summary["mechanism"]["assigned_pairs"],24)
        self.assertEqual(summary["mechanism"]["pairs_with_same_state_first_replay_difference"],24)
        self.assertEqual(summary["mechanism"]["belief_differences_after_first_replay_choice"],0)
        edited=deepcopy(rows)
        edited[1]["chronology"]["steps"][0]["pre_replay_state_sha256"]="mismatch"
        self.assertEqual(A._summaries(edited)["mechanism"]
                         ["pairs_with_same_state_first_replay_difference"],23)
        edited=deepcopy(rows)
        edited[0]["terminal"]="dead"
        edited[0]["dead_at_horizon"]=True
        self.assertEqual(A._summaries(edited)["overall"]["random_content_only_survives"],1)
        edited=deepcopy(rows)
        edited[1]["world_sha256"]="changed"
        with self.assertRaises(ValueError):
            A._summaries(edited)


if __name__=="__main__":
    unittest.main()
