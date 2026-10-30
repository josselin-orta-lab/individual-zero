"""Pure source-born Stage11 intrinsic arithmetic, no cohort."""
import unittest
from math import tanh
from i1_a2r_intrinsic_cold import audit_stage11_intrinsic_magnitude

def fixture(value=.4, evidence=.2, producer="exploration:p48_geographic"):
    option="option:frontier:one"
    stage={"kind":"stage8_option_evaluation","t_monde":1,"cycle":1,
        "data":{"option_ref":option,"status":"evaluated",
                "intrinsic_status":"applicable","intrinsic_value":value,
                "learning_signature":"frontier:one",
                "learned_value_status":"unlearned","learned_value":None,
                "simulated_value_status":"unavailable","simulated_value":None,
                "evidence":evidence}}
    provenance={"kind":"stage11_intrinsic_evaluation","t_monde":1,"cycle":1,
        "data":{"option_ref":option,"status":"evaluated",
                "intrinsic_value":value,"intrinsic_producers":[producer],
                "signal_ids":["exploration:frontier:one:t1"],
                "P15_intrinsic_weight":.5}}
    replay={"scope":"A2R_COLD_NATIVE_Q_FULL_VECTOR_NOT_L3",
        "full_q_replay_verified":True,"m11_identity":"id",
        "mode":"CANONICAL_ABS","td_recurrences":[],"q_update_counts":{}}
    audit={"scope":"A2R_STAGE8_NATIVE_EVIDENCE_RECONSTRUCTED_NOT_L3",
        "same_full_m11_q_replay":True,"preregistered_mechanism_exposed":False}
    birth={"scope":"SOURCE_RECONSTRUCTED_ZERO_STEP_REFERENCE_NOT_NEW_LIFE",
        "identity":"id","mode":"CANONICAL_ABS","q_at_birth_empty":True,
        "born_temperament":{"exploration_coefficient":0.},
        "stage11_geographic_novelty_weight":.4,"stage11_intrinsic_weight":.5,
        "stage8_evaluation":{"version":"test","n0":2.,
          "evidence_scale":5.,"extrinsic_gain":1.}}
    return [stage,provenance],replay,audit,birth

class IntrinsicColdTests(unittest.TestCase):
    def test_direct_frontier_arithmetic(self):
        events,q,s,b=fixture()
        result=audit_stage11_intrinsic_magnitude(events,q_replay=q,stage8_audit=s,birth=b)
        self.assertEqual(result["direct_frontier_intrinsic_recomputed"],1)
        self.assertFalse(result["study_admissible"])
        self.assertFalse(result["all_stage11_intrinsic_state_independently_replayed"])
    def test_tampered_intrinsic_rejected(self):
        events,q,s,b=fixture(value=.7)
        with self.assertRaises(ValueError):
            audit_stage11_intrinsic_magnitude(events,q_replay=q,stage8_audit=s,birth=b)
    def test_tampered_evidence_rejected(self):
        events,q,s,b=fixture(evidence=.3)
        with self.assertRaises(ValueError):
            audit_stage11_intrinsic_magnitude(events,q_replay=q,stage8_audit=s,birth=b)
    def test_missing_history_remains_quarantined(self):
        events,q,s,b=fixture(producer="exploration:p48")
        result=audit_stage11_intrinsic_magnitude(events,q_replay=q,stage8_audit=s,birth=b)
        self.assertEqual(result["direct_frontier_intrinsic_recomputed"],0)
        self.assertEqual(result["unreconstructed_owner_intrinsic_occurrences"],1)
        self.assertEqual(len(result["unreconstructed_owner_intrinsic"]),1)
        self.assertEqual(result["unreconstructed_owner_intrinsic"][0]["option"],
                         events[1]["data"]["option_ref"])
    def test_duplicate_intrinsic_refused(self):
        events,q,s,b=fixture()
        with self.assertRaises(ValueError):
            audit_stage11_intrinsic_magnitude(events+[events[1]],q_replay=q,stage8_audit=s,birth=b)

if __name__=="__main__": unittest.main()
