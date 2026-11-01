import unittest
from copy import deepcopy
from i1_a2r_geo_intrinsic_join import reconcile_geographic_intrinsic as join
def fixture():
    key=dict(step=2,cycle=1,option="option:geographic:frontier:4:3:from:3:3")
    g=dict(scope="A2R_PHYSICAL_GEOGRAPHIC_VISIT_REPLAY_NOT_L3",
        frontier_occurrences=[dict(key,not_previously_registered=True,perceptual_passability_checked=False)],
        direct_frontier_candidates_checked=1,direct_frontier_passability_cues_checked=0,
        direct_frontier_passability_cues_absent=1,historic_visits_match_sealed_final_owner=True,
        per_neighbor_creature_absence_attested=False,action_control_admissibility_replayed=False,
        all_intrinsic_owner_history_replayed=False,study_admissible=False,
        preregistered_mechanism_exposed=False,general_L3="NOT_ESTABLISHED")
    i=dict(scope="A2R_STAGE11_PARTIAL_SOURCE_INTRINSIC_ARITHMETIC_NOT_L3",
        intrinsic_magnitude_verified=[dict(key,producer="exploration:p48_geographic",
            recomputed_intrinsic=.3,recomputed_evidence=.15)],
        unreconstructed_owner_intrinsic=[dict(step=3,cycle=1,option="old-question",reason="missing")],
        direct_frontier_intrinsic_recomputed=1,unreconstructed_owner_intrinsic_occurrences=1,
        stage11_intrinsic_occurrences=2,all_stage11_intrinsic_state_independently_replayed=False,
        frontier_admissibility_independently_replayed=False,study_admissible=False,
        preregistered_mechanism_exposed=False,general_L3="NOT_ESTABLISHED")
    j=dict(scope="A2R_STAGE11_SOURCE_FORMULA_JOIN_NOT_L3",stage11_original_events_reconciled=2,
        direct_frontier_formula_checked_not_novelty=1,owner_history_missing_occurrences=1,
        still_quarantined_without_frontier_admissibility=2,all_stage11_intrinsic_causes_proven=False,
        study_admissible=False,preregistered_mechanism_exposed=False,general_L3="NOT_ESTABLISHED")
    return g,i,j
class Tests(unittest.TestCase):
    def test_match_still_blocked(self):
        g,i,j=fixture();v=join(geography=g,intrinsic=i,stage11_join=j)
        self.assertEqual(v["direct_intrinsic_magnitudes_matched"],1)
        self.assertFalse(v["study_admissible"])
    def test_bad_input_refused(self):
        for attack in ("cycle","duplicate","missing","go","unsafe","duplicate_owner","nan"):
            g,i,j=deepcopy(fixture())
            if attack=="cycle":i["intrinsic_magnitude_verified"][0]["cycle"]=2
            if attack=="duplicate":g["frontier_occurrences"].append(deepcopy(g["frontier_occurrences"][0]))
            if attack=="missing":g["frontier_occurrences"]=[]
            if attack=="go":j["study_admissible"]=True
            if attack=="unsafe":g["action_control_admissibility_replayed"]=True
            if attack=="duplicate_owner":i["unreconstructed_owner_intrinsic"].append(deepcopy(i["unreconstructed_owner_intrinsic"][0]))
            if attack=="nan":i["intrinsic_magnitude_verified"][0]["recomputed_intrinsic"]=float("nan")
            with self.subTest(attack=attack),self.assertRaises(ValueError):join(geography=g,intrinsic=i,stage11_join=j)
    def test_unvalued_offer_not_fabricated(self):
        g,i,j=fixture();i["intrinsic_magnitude_verified"]=[]
        i["direct_frontier_intrinsic_recomputed"]=0;i["stage11_intrinsic_occurrences"]=1
        j["stage11_original_events_reconciled"]=1
        j["direct_frontier_formula_checked_not_novelty"]=0
        j["still_quarantined_without_frontier_admissibility"]=1
        self.assertEqual(join(geography=g,intrinsic=i,stage11_join=j)["direct_intrinsic_magnitudes_matched"],0)
if __name__=="__main__":unittest.main()
