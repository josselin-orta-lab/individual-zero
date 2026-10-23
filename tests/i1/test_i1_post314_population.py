"""Protect new main I1 spatial memory and original native control."""
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))
from run_i1_post314_population import configure_before_birth,PROFILES,LOW_PROFILES,WORLDS

class Post314PopulationTests(unittest.TestCase):
    def test_native_unmodified(self):
        original={"stage11_config":object()}
        self.assertIs(configure_before_birth(original,0),original)
    def test_bounds_and_worlds(self):
        self.assertEqual(len(PROFILES),6)
        self.assertEqual(set(WORLDS),{"oasis","foraging","dry-valley","blocked-route"})
        for novelty,weight in PROFILES[1:]:
            self.assertTrue(0 < novelty <= .45)
            self.assertTrue(0 < weight <= .55)
    def test_lower_curiosity_is_bounded_and_untouched_control(self):
        self.assertEqual(len(LOW_PROFILES),4)
        original={"stage11_config":object()}
        self.assertIs(configure_before_birth(original,0,profiles=LOW_PROFILES),original)
        for novelty,weight in LOW_PROFILES[1:]:
            self.assertTrue(0 < novelty <= .15)
            self.assertTrue(0 < weight <= .35)
        with self.assertRaises(ValueError):
            configure_before_birth(original,4,profiles=LOW_PROFILES)

    def test_invalid_candidate(self):
        for value in (-1,6,1.0):
            with self.assertRaises(ValueError):
                configure_before_birth({"stage11_config":None},value)

if __name__=="__main__":
    unittest.main()
