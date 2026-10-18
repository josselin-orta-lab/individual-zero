"""Operator-only prenatal curiosity screen: native arm never changed."""
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))
from run_i1_geo_population import PROFILES, configure_before_birth
class GeoPopulationTests(unittest.TestCase):
    def test_registered_profiles_and_native_identity(self):
        self.assertEqual(len(PROFILES),6)
        self.assertIsNone(PROFILES[0])
        token=object()
        original={"stage11_config":token}
        self.assertIs(configure_before_birth(original,0),original)
        for novelty,intrinsic in PROFILES[1:]:
            self.assertTrue(0 < novelty <= 1)
            self.assertTrue(0 < intrinsic <= 1)
        for n in (-1,6,1.0):
            with self.assertRaises(ValueError):
                configure_before_birth(original,n)
if __name__=="__main__":
    unittest.main()
