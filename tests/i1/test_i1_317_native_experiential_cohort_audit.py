"""Fail closed if native Stage8 mortal cohort or its proof is incomplete."""
import importlib.util,sys,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"));sys.path.insert(0,str(ROOT/"scripts"))
sp=importlib.util.spec_from_file_location("auditnative317",ROOT/"tools/audit_i1_317_native_experiential_cohort.py")
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
class NativeMortalityAudit(unittest.TestCase):
 def test_exact_new_birth_schedule(self):
  self.assertEqual(len(m.WORLDS)*len(m.SEEDS)*len(m.ARMS),16)
  self.assertEqual(m.EXACT_RUN,39328430028)
 def test_missing_original_wal_fails(self):
  with TemporaryDirectory() as d:
   with self.assertRaises(ValueError):m.certify(Path(d))
 def test_score_is_not_motor_claim(self):
  with self.assertRaises(ValueError):m.number({"bad":"float"})
if __name__=="__main__":unittest.main()
