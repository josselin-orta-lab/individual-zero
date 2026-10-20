"""Adversarial tests: critical means observed body only, no command policy."""
from pathlib import Path
import importlib.util
import sys
import unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))
spec=importlib.util.spec_from_file_location("critical317",ROOT/"tools/run_i1_317_critical_wake_guard.py")
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
class CriticalWakeGuardTests(unittest.TestCase):
    body={"water":10.0,"food":10.001,"integrity":9.99,"energy":100.0}
    def test_exact_inclusive_threshold(self):
        self.assertEqual(module.witnessed_critical_channels(self.body),("water","integrity"))
    def test_noncritical(self):
        self.assertEqual(module.witnessed_critical_channels(
            {"water":11.0,"food":11.0,"integrity":11.0,"energy":100.0}),())
    def test_no_missing_or_nonfinite_signals(self):
        for body in ({"water":9,"food":9,"energy":9},
                     {"water":float("nan"),"food":9,"integrity":9,"energy":9},
                     {"water":101,"food":9,"integrity":9,"energy":9}):
            with self.assertRaises(ValueError):
                module.witnessed_critical_channels(body)
    def test_declared_bounded_experiment(self):
        self.assertEqual(module.PREDECLARED_SEEDS,(9601,9631))
        self.assertEqual(module.EXPERIMENTAL_LIMIT,10.0)
        self.assertEqual(module.HORIZON,300)
if __name__=="__main__":
    unittest.main()
