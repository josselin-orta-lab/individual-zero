"""Fail-closed exact native evidence join. No experimental lives."""
import unittest
from i1_a2r_postflight import reconcile_native_evidence

def fixture():
    key={"step":2,"cycle":3,"option":"option:i1:local:t2:boire:here"}
    stage8={"scope":"A2R_STAGE8_NATIVE_EVIDENCE_RECONSTRUCTED_NOT_L3",
        "stage8_evaluations_recomputed":3,"stage8_other_evaluations_unreplayed":1,
        "learned_q_reads_recomputed":1,"all_native_evidence_recomputed":False,
        "preregistered_mechanism_exposed":False,
        "unreplayed_evaluations":[dict(key,family="local_affordance")]}
    local={"scope":"A2R_NATIVE_LOCAL_AFFORDANCE_ARITHMETIC_NOT_L3",
        "native_local_affordance_recomputed":1,"local_with_learned_q":1,
        "preregistered_mechanism_exposed":False,
        "verified_evaluations":[dict(key,path="local",q_active_used=True,expected_evidence=.35)]}
    replay={"full_q_replay_verified":True,"stage8_read_count":4,
            "learned_stage8_reads":2}
    return stage8,local,replay

class JoinTests(unittest.TestCase):
    def test_exact_covered_and_no_go(self):
        a,b,c=fixture()
        result=reconcile_native_evidence(stage8=a,local=b,replay=c)
        self.assertEqual(result["local_affordance_equations_recomputed"],1)
        self.assertFalse(result["study_admissible"])
    def test_forged_family_rejected(self):
        a,b,c=fixture()
        a["unreplayed_evaluations"][0]["family"]="intrinsic_or_unknown"
        with self.assertRaises(ValueError):
            reconcile_native_evidence(stage8=a,local=b,replay=c)
    def test_changed_cycle_rejected(self):
        a,b,c=fixture()
        b["verified_evaluations"][0]["cycle"]=4
        with self.assertRaises(ValueError):
            reconcile_native_evidence(stage8=a,local=b,replay=c)
    def test_unreplayed_intrinsic_blocks_full_census(self):
        a,b,c=fixture()
        a["unreplayed_evaluations"].append(
            {"step":3,"cycle":1,"option":"intrinsic","family":"intrinsic_or_unknown"})
        a["stage8_other_evaluations_unreplayed"]=2
        c["stage8_read_count"]=5
        with self.assertRaisesRegex(ValueError,"unreplayed"):
            reconcile_native_evidence(stage8=a,local=b,replay=c)
        result=reconcile_native_evidence(stage8=a,local=b,replay=c,require_complete=False)
        self.assertEqual(result["unreplayed_other_producer_occurrences"],1)
    def test_count_forgery_refused(self):
        a,b,c=fixture()
        c["stage8_read_count"]=5
        with self.assertRaises(ValueError):
            reconcile_native_evidence(stage8=a,local=b,replay=c)
if __name__=="__main__":
    unittest.main()
