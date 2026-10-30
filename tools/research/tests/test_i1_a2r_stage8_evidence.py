"""Pure Stage8 actual-equation adversarial checks, no births."""
import unittest
from math import tanh
from i1_a2r_stage8_evidence import expected_stage8_evidence, attest_native_stage8

CAL={"version":"v1","n0":2.,"evidence_scale":5.,"extrinsic_gain":1.}
TD="p31-stage8-reference-v1"
def row(q=None,sim=3.,evidence=None):
    learned=q is not None
    valid_sim=sim is not None
    if evidence is None and (learned or valid_sim):
        ext=(q/3+2*sim/3) if learned and valid_sim else (q if learned else sim)
        evidence=tanh(ext/5)
    return {"option_ref":"permanent:attendre","learning_signature":"primitive:attendre",
      "status":"evaluated" if learned or valid_sim else "not_evaluated",
      "learned_value_status":"learned" if learned else "unlearned",
      "learned_value":q,"simulated_value_status":"computed" if valid_sim else "unavailable",
      "simulated_value":sim,"evidence":evidence,"equipment_version":"e1","q_version":TD}
class EvidenceTests(unittest.TestCase):
    def test_simulation_only(self):
        self.assertAlmostEqual(expected_stage8_evidence(row(),update_count=0,calibration=CAL,td_version=TD),tanh(.6))
    def test_q_and_simulation(self):
        self.assertAlmostEqual(expected_stage8_evidence(row(q=6.),update_count=1,calibration=CAL,td_version=TD),tanh(.8))
    def test_q_only(self):
        x=row(q=6.,sim=None)
        self.assertAlmostEqual(expected_stage8_evidence(x,update_count=1,calibration=CAL,td_version=TD),tanh(1.2))
    def test_nothing_available(self):
        self.assertIsNone(expected_stage8_evidence(row(sim=None),update_count=0,calibration=CAL,td_version=TD))
    def test_wrong_evidence_and_counts_refused(self):
        x=row(q=6.)
        x["evidence"]=.9
        with self.assertRaises(ValueError):expected_stage8_evidence(x,update_count=1,calibration=CAL,td_version=TD)
        with self.assertRaises(ValueError):expected_stage8_evidence(row(q=6.),update_count=0,calibration=CAL,td_version=TD)
    def test_unpublished_non_q_fields_not_accepted(self):
        x=row()
        x["protection"]=False
        with self.assertRaises(ValueError):expected_stage8_evidence(x,update_count=0,calibration=CAL,td_version=TD)
    def test_missing_authenticated_replay_fails(self):
        with self.assertRaises(ValueError):
            attest_native_stage8([],q_replay={"full_q_replay_verified":False},calibration=CAL,td_version=TD)
if __name__=="__main__":unittest.main()
