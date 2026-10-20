"""#317 pure non-oracular no-op spatial recall gate tests."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/"tools"))
sys.path.insert(0, str(ROOT/"scripts"))
spec=importlib.util.spec_from_file_location(
    "place_noop_guard317", ROOT/"tools/run_i1_317_place_noop_guard.py"
)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def target(x, y):
    return SimpleNamespace(observed_position=(x,y))

class LivedPlaceNoopGuard317(unittest.TestCase):
    def test_factorial_never_mutates_value_and_has_fresh_mortal_seeds(self):
        self.assertEqual(m.ARMS, ("canonical","guarded_recall"))
        self.assertEqual(m.SEEDS, (14083,14107))
        self.assertEqual(m.factors("canonical"), (False,False))
        self.assertEqual(m.factors("guarded_recall"), (True,False))
        with self.assertRaises(ValueError):m.factors("forced_thirst")
    def test_unfilled_prefix_cannot_be_extended_by_higher_limit(self):
        self.assertFalse(m.expanded_search_may_change_candidates(
            [target(8,9)], {(20,20):39.6}, (8,8), 3))
    def test_beneficial_current_site_never_needs_route(self):
        self.assertFalse(m.expanded_search_may_change_candidates(
            [target(8,9),target(9,8),target(10,8)],
            {(8,8):39.6}, (8,8), 3))
    def test_saturated_prefix_all_personally_supported_already_first(self):
        self.assertFalse(m.expanded_search_may_change_candidates(
            [target(8,8),target(8,9),target(9,8)],
            {(8,8):39.6}, (10,8), 3))
    def test_saturated_prefix_may_hide_personal_offsite_source(self):
        self.assertTrue(m.expanded_search_may_change_candidates(
            [target(8,9),target(9,8),target(10,8)],
            {(8,8):39.6}, (10,9), 3))
    def test_existing_prefix_can_be_reordered_with_personal_evidence(self):
        self.assertTrue(m.expanded_search_may_change_candidates(
            [target(8,9),target(8,8),target(9,8)],
            {(8,8):39.6}, (10,8), 3))
    def test_no_personal_experience_never_expands(self):
        self.assertFalse(m.expanded_search_may_change_candidates(
            [target(8,9),target(9,8),target(10,8)],
            {}, (10,9), 3))
    def test_rejects_forged_evidence_and_overcapacity(self):
        for bad in ({(8,8):0}, {(8,8):-1}, {(8,8):float('nan')},
                    {(8,8):float('inf')}, {'water_source':39.6}):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    m.expanded_search_may_change_candidates(
                        [target(8,9)]*3,bad,(10,8),3)
        with self.assertRaises(ValueError):
            m.expanded_search_may_change_candidates(
                [target(8,9)]*4,{(8,8):1},(10,8),3)

if __name__=="__main__":
    unittest.main()
