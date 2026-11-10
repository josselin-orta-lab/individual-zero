"""Read-only scientific original custody, independent of World and Mind."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from i3.lab import stage2_next_decision_24_original_audit as A


class NextDecision24OriginalAuditTests(unittest.TestCase):
    def test_frozen_original_identity_no_world_source(self):
        self.assertEqual(A.PAIRS,24)
        self.assertEqual(A.HORIZON,400)
        self.assertEqual(len(A.SOURCE),40)
        self.assertEqual(len(A.MANIFEST_SHA),64)
        self.assertEqual(len(A.PLAN_SHA),64)
        self.assertEqual(A.POLICIES,(
            "p13_replay_gate_v1","p13_replay_gate_random_content_v1"))

    def test_missing_or_modified_originals_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(FileNotFoundError):
                A.audit(Path(directory))

    def test_all_assigned_nulls_forks_and_secondary_discordances(self):
        rows=[]
        for i in range(A.PAIRS):
            source={
                "index":560000+i,"pair_id":f"next-decision-{i:06d}",
                "cohort":"development","family":A.FAMILIES[i%3],
                "world_seed":100+i,"genome_seed":200+i,"life_seed":300+i,
                "world_sha256":str(i),"genome_sha256":str(i),
                "source_sha256":"source"}
            for j,policy in enumerate(A.POLICIES):
                rows.append({**source,"policy":policy,
                             "terminal":"censored","steps_lived":400,
                             "dead_at_horizon":False,
                             "paid_energy":10.,"paid_vigilance":20.,
                             "sleep_steps":2,"replays_paid":3,
                             "random_content_receipt":(
                                 {"distinct_from_priority_subsets":1,
                                  "paid_replay_opportunities":1,
                                  "selected_replays_paid":3,
                                  "lived_sleep_ordinals":2} if j else None),
                             "next_decision_receipt":({
                                 "status":"NO_DIFFERENT_FUNDED_REPLAY",
                                 "funded_opportunities":0,
                                 "different_opportunities":0,
                                 "first_fork":None} if j else None)})
        original=A._summaries(rows)
        self.assertEqual(original["mechanism"]["assigned_pairs"],24)
        self.assertEqual(original["mechanism"]["no_different_funded_memory_fork"],24)
        self.assertEqual(original["mechanism"]["different_next_admitted_action_or_param"],0)
        changed=deepcopy(rows)
        changed[1]["next_decision_receipt"]["first_fork"]={
            "next_decision":{"same_admitted_action_and_param":False,
                             "same_decision_option":False},
            "shared_actual_transition_td_residual":None}
        x=A._summaries(changed)
        self.assertEqual(x["mechanism"]["different_next_admitted_action_or_param"],1)
        self.assertEqual(x["mechanism"]["primary_fraction_of_all_assigned"],1/24)
        no_next=deepcopy(rows)
        no_next[1]["next_decision_receipt"]["first_fork"]={
            "next_decision":None,"shared_actual_transition_td_residual":None}
        y=A._summaries(no_next)
        self.assertEqual(y["mechanism"]["first_fork_without_following_real_decision"],1)
        adverse=deepcopy(rows)
        adverse[0]["terminal"]="dead"
        adverse[0]["dead_at_horizon"]=True
        z=A._summaries(adverse)
        self.assertEqual(z["overall"]["random_content_only_survives"],1)
        with self.assertRaises(ValueError):
            A._summaries(rows[:-1])
        altered=deepcopy(rows)
        altered[1]["genome_sha256"]="tampered"
        with self.assertRaises(ValueError):
            A._summaries(altered)

    def test_finite_data_structure_cannot_drop_adverse_family(self):
        groups={"stable":{"assigned":8,"fork":7,"changed_action":1,"with_next":7},
                "depletion":{"assigned":10,"fork":7,"changed_action":0,"with_next":7},
                "pulse":{"assigned":6,"fork":6,"changed_action":0,"with_next":6}}
        A._same_tree(groups,deepcopy(groups))
        with self.assertRaises(ValueError):
            A._same_tree(groups,{**groups,"stable":{"assigned":8}})
        with self.assertRaises(ValueError):
            A._same_tree(groups,{k:v for k,v in groups.items() if k!="pulse"})


if __name__=="__main__":
    unittest.main()
