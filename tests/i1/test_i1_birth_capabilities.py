"""Born-I1 audit is passive and rejects changed or missing capabilities."""
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))
from audit_i1_birth_capabilities import SCHEMA,EXPECTED,enforce_manifest

class BirthCapabilityContractTests(unittest.TestCase):
    def sample(self):
        return {
            "schema":SCHEMA,"capabilities":dict(EXPECTED),
            "stage_configs":{str(i):"test" for i in range(4,13)},
            "effective_configuration":{
                "goal_manager":{"replacement_hysteresis":.04,"critical_pressure":.35},
                "toxic_berry_integrity_delta":-10.,
                "competition":{"base_threshold":.5,"gain":1.},
            },
            "invariants":{
                "stage4_10_11_owner_consistency":True,
                "unique_causal_owner_ids":True,
                "unstarted_without_observer_effect":True,
            },
        }
    def test_expected_contract(self):
        self.assertEqual(enforce_manifest(self.sample()),self.sample())
    def test_missing_capability_fails_closed(self):
        m=self.sample()
        del m["capabilities"]["stage8.td_learning"]
        with self.assertRaises(AssertionError):
            enforce_manifest(m)
    def test_false_positive_claim_fails_closed(self):
        m=self.sample()
        m["capabilities"]["i1.d2_movement_prudence"]="active"
        with self.assertRaises(AssertionError):
            enforce_manifest(m)
    def test_real_calibration_and_berry(self):
        for key,val in (("replacement_hysteresis",.10),("critical_pressure",.90)):
            m=self.sample()
            m["effective_configuration"]["goal_manager"][key]=val
            with self.assertRaises(AssertionError):
                enforce_manifest(m)
        m=self.sample()
        m["effective_configuration"]["toxic_berry_integrity_delta"]=-100.
        with self.assertRaises(AssertionError):
            enforce_manifest(m)
    def test_candidate_competition_mismatch(self):
        with self.assertRaises(AssertionError):
            enforce_manifest(self.sample(),expected_competition={"base_threshold":.35,"gain":1.2})

if __name__=="__main__":
    unittest.main()
