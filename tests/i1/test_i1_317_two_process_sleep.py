"""No motor oracle or physiology changes in research-only sleep birth policy."""
import importlib.util
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))
spec=importlib.util.spec_from_file_location("two_process",ROOT/"tools/run_i1_317_two_process_sleep.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
class TwoProcessTests(unittest.TestCase):
    def test_distinct_locked_profiles(self):
        self.assertEqual(m.ARMS,("canonical","homeostatic","circadian"))
        self.assertEqual(m.SEEDS,(9761,9791))
        self.assertEqual(len(m.PRESETS),4)
        for key in ("homeostatic","circadian"):
            d=m.PROFILES[key]
            self.assertLess(d["consolidation_weight"],0.25)
            self.assertGreater(d["sleep_fatigue_recovery"],0.3)
            self.assertGreater(d["unconsolidated_episode_reference"],8)
            self.assertLess(d["fatigue_gain"],0.7)
    def test_daily_sleep_runs_and_no_forced_actions(self):
        self.assertEqual(m._run_lengths([True,True,False,True]),[2,1])
        self.assertEqual(m._run_lengths([False,False]),[])
        self.assertEqual(m._run_lengths([True,True]),[2])
    def test_unregistered_profile_rejected(self):
        with self.assertRaises(ValueError):
            m.calibrate_native_birth(None,"unknown")
if __name__=="__main__":unittest.main()
