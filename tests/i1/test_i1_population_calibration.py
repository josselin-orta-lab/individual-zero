"""Pure optimizer guards. No I1 actuation or behavior modifications."""
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))
from run_i1_population_calibration import candidates, prenatal_stage4, BASELINE, BOUNDS, WORLDS

class PopulationResearchTests(unittest.TestCase):
    def test_reference_and_bounded_reproducibility(self):
        self.assertEqual(candidates(), candidates())
        self.assertEqual(candidates()[0], BASELINE)
        self.assertEqual(len(candidates()),6)
        self.assertEqual(set(WORLDS), {"oasis", "foraging", "dry-valley"})
        for candidate in candidates():
            self.assertEqual(set(candidate),set(BOUNDS))
            for k,value in candidate.items():
                self.assertGreaterEqual(value,BOUNDS[k][0])
                self.assertLessEqual(value,BOUNDS[k][1])
    def test_native_control_is_noop(self):
        marker=object()
        params={"stage11_config":marker,"stage10_config":marker}
        self.assertIs(prenatal_stage4(params,BASELINE,0),params)
        with self.assertRaises(AssertionError):
            prenatal_stage4(params,candidates()[1],0)
    def test_reject_unregistered_parameters(self):
        with self.assertRaises(ValueError):
            candidates(25)
        with self.assertRaises(ValueError):
            prenatal_stage4({"stage11_config":None}, {**BASELINE,"critical":100},1)

if __name__=="__main__":
    unittest.main()
