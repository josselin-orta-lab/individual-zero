"""Pure independent local-affordance score contracts, no cohort births."""
import unittest
from math import tanh
from i1_a2r_affordance_cold import audit_native_affordance_evidence

def fixture(learned=False, wrong=False):
    identity="i1:eco:a2r:reward:test"
    prior=.35
    q=2.0 if learned else None
    evidence=.25*prior+.75*tanh(q/5) if learned else prior
    if wrong:evidence+=.1
    option="option:i1:local:t1:boire:here"
    sig="i1:affordance:boire:here"
    status="learned" if learned else "unlearned"
    events=[{"kind":"i1_local_opportunity_proposed","t_monde":1,"cycle":1,
             "data":{"option_ref":option,"learning_signature":sig,
                     "learned_value_status":status,"prior_evidence":prior}},
            {"kind":"stage8_option_evaluation","t_monde":1,"cycle":1,
             "data":{"option_ref":option,"learning_signature":sig,
                     "status":"evaluated","learned_value_status":status,
                     "learned_value":q,"simulated_value_status":"unavailable",
                     "simulated_value":None,"intrinsic_status":"not_applicable",
                     "intrinsic_value":None,"evidence":evidence}}]
    replay={"scope":"A2R_COLD_NATIVE_Q_FULL_VECTOR_NOT_L3",
            "full_q_replay_verified":True,"mode":"CANONICAL_ABS",
            "m11_identity":identity,
            "stage8_observations":[{"step":1,"cycle":1,"option":option,
                                    "signature":sig,"status":status,"q":q}]}
    birth={"identity":identity,"mode":"CANONICAL_ABS",
           "q_at_birth_empty":True,
           "born_temperament":{"exploration_coefficient":0.,
                               "uncertainty_penalty_scale":0.},
           "born_td_evidence_scale":5.,
           "stage11_intrinsic_weight":.3}
    return events,replay,birth

class AffordanceColdTests(unittest.TestCase):
    def test_unlearned_native_local_prior(self):
        a,q,b=fixture()
        result=audit_native_affordance_evidence(a,q_replay=q,birth=b)
        self.assertEqual(result["native_local_affordance_recomputed"],1)
        self.assertFalse(result["preregistered_mechanism_exposed"])
    def test_learned_native_q_mix(self):
        a,q,b=fixture(learned=True)
        result=audit_native_affordance_evidence(a,q_replay=q,birth=b)
        self.assertEqual(result["local_with_learned_q"],1)
    def test_forged_evidence_refused(self):
        a,q,b=fixture(wrong=True)
        with self.assertRaises(ValueError):
            audit_native_affordance_evidence(a,q_replay=q,birth=b)
    def test_source_temperament_change_refused(self):
        a,q,b=fixture()
        b["born_temperament"]["exploration_coefficient"]=1.
        with self.assertRaises(ValueError):
            audit_native_affordance_evidence(a,q_replay=q,birth=b)
    def test_unjoined_stage11_intrinsic_refused(self):
        a,q,b=fixture()
        a.append({"kind":"stage11_intrinsic_evaluation","t_monde":1,"cycle":1,
                  "data":{"option_ref":"other","status":"evaluated",
                          "intrinsic_value":0.1}})
        with self.assertRaises(ValueError):
            audit_native_affordance_evidence(a,q_replay=q,birth=b)
if __name__=="__main__":
    unittest.main()
