"""Read-only scientific content-original check. No World, genome or Mind."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from i3.lab import stage2_content_48_original_audit as A


class OriginalContentAuditTests(unittest.TestCase):
    def test_source_and_scientific_scope_pinned(self):
        self.assertEqual(len(A.SOURCE),40)
        self.assertEqual(len(A.FINGERPRINT),64)
        self.assertEqual(len(A.MANIFEST_SHA),64)
        self.assertEqual(A.PAIRS,48)
        self.assertEqual(A.HORIZON,400)
        self.assertEqual(A.POLICIES,(
            "p13_replay_gate_v1","p13_replay_gate_random_content_v1"))

    def test_empty_archive_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                A.audit(Path(tmp))

    def test_adverse_family_must_not_be_dropped_or_modified(self):
        expected={"stable":{"priority_only_survives":1},
                  "depletion":{"random_content_only_survives":4},
                  "pulse":{"random_content_only_survives":2}}
        A._same_tree(expected,deepcopy(expected))
        for modified in (
            {"stable":{"priority_only_survives":1},
             "depletion":{"random_content_only_survives":4}},
            {"stable":{"priority_only_survives":1},
             "depletion":{"random_content_only_survives":3},
             "pulse":{"random_content_only_survives":2}},
            {"stable":{"priority_only_survives":1},
             "depletion":{"random_content_only_survives":4},
             "pulse":{"random_content_only_survives":2},
             "other":{"random_content_only_survives":0}},
        ):
            with self.subTest(modified=modified),self.assertRaises(ValueError):
                A._same_tree(expected,modified)

    def test_all_matched_pairs_and_terminal_at_400(self):
        rows=[]
        for i in range(48):
            identity={"index":480000+i,"pair_id":f"content-dev-{i:06d}",
                      "cohort":"development",
                      "family":A.FAMILIES[i%3],
                      "world_seed":111+i,"genome_seed":211+i,
                      "life_seed":311+i,"world_sha256":str(i),
                      "genome_sha256":str(i),"source_sha256":"source"}
            for j,policy in enumerate(A.POLICIES):
                rows.append({**identity,"policy":policy,
                             "terminal":"censored","steps_lived":400,
                             "dead_at_horizon":False,
                             "paid_energy":6.,"paid_vigilance":7.,
                             "replays_paid":10,"sleep_steps":2,
                             "random_content_receipt":(
                                 None if j==0 else
                                 {"distinct_from_priority_subsets":1,
                                  "paid_replay_opportunities":1})})
        read=A._summaries(rows)
        self.assertEqual(read["overall"]["assigned_pairs"],48)
        self.assertEqual(read["overall"]["paired_risk_difference_priority_minus_random"],0)
        self.assertEqual(read["by_arm"][A.POLICIES[1]]["random_content_distinct_subsets"],48)
        altered=deepcopy(rows)
        altered[0]["terminal"]="dead"
        altered[0]["dead_at_horizon"]=True
        read=A._summaries(altered)
        self.assertEqual(read["overall"]["random_content_only_survives"],1)
        self.assertEqual(read["overall"]["paired_risk_difference_priority_minus_random"],-1/48)
        altered=deepcopy(rows)
        altered[1]["world_sha256"]="wrong"
        with self.assertRaises(ValueError):
            A._summaries(altered)


if __name__=="__main__":
    unittest.main()
