"""Pure adversarial A2-R postflight score and paired census contracts."""
import unittest
from i1_a2r_postflight import (
    score_cold_original, verify_birth_pair, describe_complete_pairs,
    reconcile_stage11_intrinsic_provenance,
)
from i1_a2r_archive_guard import ordered_rows

NEEDS=("energy","food","water","integrity")

def cold_fixture(mode="CANONICAL_ABS", dead=False):
    identity="id:"+mode
    ref={"identity":identity,"mode":mode,"runtime_contract":"contract:"+mode,
         "value_needs_config_version":"v:"+mode,
         "born_td":{"version":"tdv","feature_version":"f"},
         "q_at_birth_empty":True,"initial_body":dict.fromkeys(NEEDS,60.),
         "setpoints":dict.fromkeys(NEEDS,60.),
         "scales":dict.fromkeys(NEEDS,100.)}
    last={"step":1,"before":dict.fromkeys(NEEDS,60.),
          "after":dict.fromkeys(NEEDS,59.),"action":"attendre",
          "status":"dead" if dead else "active"}
    gen=1
    original={"identity":identity,"mode":mode,"role":"native","seed":2001,
              "generation":gen,"status":last["status"],
              "journal_head":"a"*64,"state_hash":"b"*64}
    cold={"receipt":{k:original[k] for k in
          ("identity","generation","status","journal_head","state_hash")},
          "analysis_admissible":True,"runtime_contract":ref["runtime_contract"],
          "owner":{"owner_config_version":ref["value_needs_config_version"],
          "td_config_version":"tdv","td_feature_version":"f"},
          "physical_steps":[last]}
    replay={"full_q_replay_verified":True,"study_admissible":True,
           "m11_identity":identity,"m11_journal_head":"a"*64,
           "m11_state_hash":"b"*64,"generation":gen,
           "status":last["status"],"mode":mode}
    return original,ref,cold,replay

class PostflightTests(unittest.TestCase):
    def test_death_is_penalized_to_h192(self):
        a,b,c,d=cold_fixture(dead=True)
        scored=score_cold_original(original=a,reference=b,cold=c,replay=d)
        self.assertTrue(scored["dead"])
        self.assertGreater(scored["primary_score"],.99)
        self.assertLessEqual(scored["primary_score"],1.)
    def test_tampered_owner_or_head_rejected(self):
        for point in ("owner","head","replay"):
            a,b,c,d=cold_fixture(dead=True)
            if point=="owner":c["owner"]["owner_config_version"]="forged"
            if point=="head":c["receipt"]["journal_head"]="c"*64
            if point=="replay":d["full_q_replay_verified"]=False
            with self.subTest(point=point),self.assertRaises(ValueError):
                score_cold_original(original=a,reference=b,cold=c,replay=d)
    def test_pair_parity_refuses_changed_non_reward_context(self):
        core={"role":"native","seed":2001,"q_at_birth_empty":True}
        a=dict(core,mode="CANONICAL_ABS",identity="a",runtime_contract="ca")
        b=dict(core,mode="RESEARCH_DEFICIT",identity="b",runtime_contract="cb")
        from i1_a2r_postflight import PARITY_FIELDS
        for k in PARITY_FIELDS:a[k]=b[k]=k
        self.assertTrue(verify_birth_pair(a,b))
        b["initial_body"]="changed"
        with self.assertRaises(ValueError):verify_birth_pair(a,b)

    def test_intrinsic_join_fails_closed_and_exact(self):
        a={"step":2,"cycle":1,"option":"frontier"}
        b={"step":3,"cycle":1,"option":"causal_test"}
        stage={"scope":"A2R_STAGE8_NATIVE_EVIDENCE_RECONSTRUCTED_NOT_L3",
            "unreplayed_evaluations":[
                dict(a,family="intrinsic_or_unknown"),
                dict(b,family="intrinsic_or_unknown"),
                {"step":3,"cycle":2,"option":"local","family":"local_affordance"}],
            "stage11_post_competition_occurrences":2}
        intrinsic={
            "scope":"A2R_STAGE11_PARTIAL_SOURCE_INTRINSIC_ARITHMETIC_NOT_L3",
            "stage11_intrinsic_occurrences":2,
            "direct_frontier_intrinsic_recomputed":1,
            "unreconstructed_owner_intrinsic_occurrences":1,
            "intrinsic_magnitude_verified":[dict(a,
                producer="exploration:p48_geographic",
                recomputed_intrinsic=.4,recomputed_evidence=.2)],
            "unreconstructed_owner_intrinsic":[dict(b,reason="history_missing")],
            "all_stage11_intrinsic_state_independently_replayed":False,
            "frontier_admissibility_independently_replayed":False,
            "preregistered_mechanism_exposed":False,"study_admissible":False,
            "general_L3":"NOT_ESTABLISHED"}
        result=reconcile_stage11_intrinsic_provenance(
            stage8=stage,intrinsic=intrinsic)
        self.assertEqual(result["stage11_original_events_reconciled"],2)
        self.assertEqual(result["still_quarantined_without_frontier_admissibility"],2)
        self.assertFalse(result["study_admissible"])
        from copy import deepcopy
        for attack in ("lost", "fabricated", "duplicate", "false_go",
                       "false_frontier", "bad_total", "wrong_family"):
            x,y=deepcopy(stage),deepcopy(intrinsic)
            if attack=="lost":y["unreconstructed_owner_intrinsic"]=[]
            if attack=="fabricated":y["intrinsic_magnitude_verified"][0]["cycle"]=50
            if attack=="duplicate":y["unreconstructed_owner_intrinsic"][0]=dict(a,reason="history_missing")
            if attack=="false_go":y["study_admissible"]=True
            if attack=="false_frontier":y["frontier_admissibility_independently_replayed"]=True
            if attack=="bad_total":y["stage11_intrinsic_occurrences"]=1
            if attack=="wrong_family":x["unreplayed_evaluations"][0]["family"]="external_adapter"
            with self.subTest(attack=attack),self.assertRaises(ValueError):
                reconcile_stage11_intrinsic_provenance(stage8=x,intrinsic=y)

    def test_all_48_pairs_are_only_descriptive(self):
        pairs=[]
        for row in ordered_rows():
            if row["mode"]!="CANONICAL_ABS":continue
            role,seed=row["role"],row["seed"]
            a={"role":role,"seed":seed,"mode":"CANONICAL_ABS",
               "identity":row["identity"],"primary_score":.5,
               "dead":False,"m11_head":"a"*64}
            b={"role":role,"seed":seed,"mode":"RESEARCH_DEFICIT",
               "identity":"other:"+row["identity"],"primary_score":.4,
               "dead":False,"m11_head":"b"*64}
            witness={"schema":"i1-a2r-pair-mechanism-witness/1",
                     "scope":"COLD_PAIRED_L1_DIAGNOSTIC_NOT_L3",
                     "general_L3":"NOT_ESTABLISHED",
                     "preregistered_mechanism_exposed":False,
                     "canonical_m11_head":"a"*64,
                     "candidate_m11_head":"b"*64,
                     "first_physical_reward_difference_step":1,
                     "descriptive_candidate_path_observed":True}
            pairs.append({"role":role,"seed":seed,"canonical":a,
                          "candidate":b,"witness":witness})
        result=describe_complete_pairs(pairs)
        self.assertEqual(result["paired_comparisons"],48)
        self.assertFalse(result["frozen_statistical_gate_called"])
        self.assertFalse(result["study_admissible"])
        with self.assertRaises(ValueError):describe_complete_pairs(pairs[:-1])
        with self.assertRaises(ValueError):describe_complete_pairs(pairs[:-1]+[pairs[0]])
if __name__=="__main__":
    unittest.main()
