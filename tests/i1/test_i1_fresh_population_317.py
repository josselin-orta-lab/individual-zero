"""Adversarial preregistration controls; no synthetic life proves survival."""
import importlib.util
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))
spec=importlib.util.spec_from_file_location(
    "fresh_population_317",ROOT/"tools/audit_i1_317_fresh_population.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class Preregistered317Tests(unittest.TestCase):
    def test_exactly_twenty_unique_predeclared_world_seed_pairs(self):
        result=m.design(list(m.PRESETS),list(m.FRESH_SEEDS))
        self.assertEqual(len(result),20)
        self.assertEqual(len(set(result)),20)

    def test_missing_extra_duplicate_or_reused_birth_is_rejected(self):
        with self.assertRaises(ValueError):
            m.design(list(m.PRESETS)[:-1],list(m.FRESH_SEEDS))
        with self.assertRaises(ValueError):
            m.design(list(m.PRESETS)+["oasis"],list(m.FRESH_SEEDS))
        with self.assertRaises(ValueError):
            m.design(list(m.PRESETS),[8411,8431,8467,1141])
        with self.assertRaises(ValueError):
            m.design(list(m.PRESETS),[8411,8431,8467,8411])

    def test_missing_evidence_cannot_pass_as_empty_population(self):
        with self.assertRaises(ValueError):
            m.analyse(Path("/no-such-i1-317-audited-population"),
                      expected_sha="a"*40)


if __name__=="__main__":
    unittest.main()
