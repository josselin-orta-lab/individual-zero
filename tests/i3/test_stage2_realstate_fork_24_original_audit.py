"""Independent realstate fork original custody, no World, no live Mind."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from i3.lab import stage2_realstate_fork_24_original_audit as A


class RealStateForkOriginalAuditTests(unittest.TestCase):
    def test_sources_and_scope(self):
        self.assertEqual(A.PAIRS,24)
        self.assertEqual(A.HORIZON,400)
        self.assertEqual(len(A.SOURCE),40)
        self.assertEqual(len(A.FINGERPRINT),64)
        self.assertEqual(len(A.MANIFEST_SHA),64)
        self.assertEqual(A.POLICIES,(
            "p13_replay_gate_v1","p13_replay_gate_random_content_v1"))

    def test_missing_originals_are_not_regenerated(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(FileNotFoundError):
                A.audit(Path(directory))

    def test_paired_first_realstate_null_counts_and_adverse_cases(self):
        rows=[]
        for i in range(24):
            common={
                "index":540000+i,"pair_id":f"fork-dev-{i:06d}",
                "family":A.FAMILIES[i%3],"cohort":"development",
                "world_seed":101+i,"genome_seed":201+i,"life_seed":301+i,
                "world_sha256":str(i),"genome_sha256":str(i),
                "source_sha256":"source"}
            for j,policy in enumerate(A.POLICIES):
                rows.append({**common,"policy":policy,
                             "terminal":"censored","steps_lived":400,
                             "dead_at_horizon":False,
                             "paid_energy":20.,"paid_vigilance":30.,
                             "sleep_steps":10,"replays_paid":5,
                             "random_content_receipt":(
                                 {"distinct_from_priority_subsets":2,
                                  "paid_replay_opportunities":3,
                                  "lived_sleep_ordinals":10,
                                  "selected_replays_paid":5}
                                 if j else None),
                             "realstate_fork_receipt":({
                                 "status":"NO_DIFFERING_FUNDED_REPLAY_OBSERVED",
                                 "prepaid_replay_opportunities_seen":0,
                                 "differing_replay_opportunities_seen":0,
                                 "first_fork":None} if j else None)})
        observed=A._summaries(rows)
        self.assertEqual(observed["mechanism"]["assigned_pairs"],24)
        self.assertEqual(observed["mechanism"]["first_fork_absent"],24)
        self.assertEqual(observed["mechanism"]["positive_learned_value_difference"],0)
        changed=deepcopy(rows)
        changed[1]["realstate_fork_receipt"]["first_fork"]={
            "l1_value_difference_between_detached_updates":0.1}
        observed=A._summaries(changed)
        self.assertEqual(observed["mechanism"]["positive_learned_value_difference"],1)
        self.assertEqual(observed["mechanism"]["primary_fraction_per_assigned_pair"],1/24)
        changed=deepcopy(rows)
        changed[0]["terminal"]="dead"
        changed[0]["dead_at_horizon"]=True
        observed=A._summaries(changed)
        self.assertEqual(observed["overall"]["random_content_only_survives"],1)
        broken=deepcopy(rows)
        broken[1]["genome_sha256"]="mismatch"
        with self.assertRaises(ValueError):
            A._summaries(broken)
        with self.assertRaises(ValueError):
            A._summaries(rows[:-1])

    def test_full_family_adverse_and_null_sections_must_match(self):
        groups={
            "stable":{"assigned":12,"captured":8,"positive":8},
            "depletion":{"assigned":7,"captured":6,"positive":6},
            "pulse":{"assigned":5,"captured":3,"positive":3},
        }
        A._same_tree(groups,deepcopy(groups))
        for bad in (
            {"stable":groups["stable"],"depletion":groups["depletion"]},
            {**groups,"pulse":{"assigned":5,"captured":3,"positive":2}},
        ):
            with self.assertRaises(ValueError):
                A._same_tree(groups,bad)


if __name__=="__main__":
    unittest.main()
