"""#317 native pre-registered candidate identities and actor opt-in."""
import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"));sys.path.insert(0,str(ROOT/"scripts"))
spec=importlib.util.spec_from_file_location("nativecohort317",ROOT/"tools/run_i1_317_native_experiential_cohort.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class NativeCohort(unittest.TestCase):
 def test_frozen_matched_pairs(self):
  self.assertEqual(len(m.PRESETS)*len(m.SEEDS)*len(m.ARMS),16)
  self.assertEqual({m.factors(a) for a in m.ARMS},{(True,False),(True,True)})
  self.assertTrue(set(m.SEEDS).isdisjoint({15121,15173,15313,16127,16249,16381,16513}))
  with self.assertRaises(ValueError):m.factors('forced_movement')
 def test_native_impl_never_imports_lab_score_adapter(self):
  source=(ROOT/"tools/run_i1_317_native_experiential_cohort.py").read_text()
  self.assertNotIn('class FirstPersonPlaceValueAdapter',source)
  self.assertIn('i1_experienced_place_enabled=do_value',source)
  self.assertIn('native_stage8_opt_in',source)
if __name__=="__main__":unittest.main()
