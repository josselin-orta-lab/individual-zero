import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"));sys.path.insert(0,str(ROOT/"scripts"))
spec=importlib.util.spec_from_file_location("cross318",ROOT/"tools/run_i1_318_cross_goal_local_cohort.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class CrossGoalBirth(unittest.TestCase):
 def test_preregistered_new_mortal_lives(self):
  self.assertEqual(len(m.PRESETS)*len(m.SEEDS)*len(m.ARMS),16)
  self.assertEqual({m.factors(a) for a in m.ARMS},{(True,False),(True,True)})
  self.assertTrue(set(m.SEEDS).isdisjoint({18121,18233,18367,18481,19121,19237,19373,19489}))
 def test_no_water_value_override(self):
  code=(ROOT/"tools/run_i1_318_cross_goal_local_cohort.py").read_text()
  self.assertIn("i1_cross_goal_local_opportunities=do_value",code)
  self.assertIn("i1_experienced_place_enabled=False",code)
  self.assertIn("i1_critical_alert_reentry_guard=False",code)
if __name__=="__main__":unittest.main()
