import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"));sys.path.insert(0,str(ROOT/"scripts"))
spec=importlib.util.spec_from_file_location("exp318",ROOT/"tools/run_i1_318_critical_alert_sleep_cohort.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class CriticalAlertCohort(unittest.TestCase):
 def test_fresh_mortal_pairs(self):
  self.assertEqual(len(m.SEEDS)*len(m.PRESETS)*len(m.ARMS),16)
  self.assertEqual({m.factors(a) for a in m.ARMS},{(True,False),(True,True)})
  self.assertTrue(set(m.SEEDS).isdisjoint({13127,13219,14083,14107,15121,15173,15313,16127,16249,16381,16513,17123,17257,17383,17491,18121,18233,18367,18481}))
 def test_only_reentry_gate(self):
  src=(ROOT/"tools/run_i1_318_critical_alert_sleep_cohort.py").read_text()
  self.assertIn("i1_critical_alert_reentry_guard=do_value",src)
  self.assertIn("i1_experienced_place_enabled=False",src)
  self.assertNotIn('FirstPersonPlaceValueAdapter',src)
if __name__=="__main__":unittest.main()
