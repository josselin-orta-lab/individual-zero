import importlib.util,sys,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"));sys.path.insert(0,str(ROOT/"scripts"))
spec=importlib.util.spec_from_file_location("holdaudit",ROOT/"tools/audit_i1_317_experiential_place_heldout.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class HeldoutEvidence(unittest.TestCase):
 def test_design(self):
  self.assertEqual(len(m.SEEDS)*len(m.WORLDS)*len(m.ARMS),32)
  self.assertEqual(m.EXACT_RUN,39324485459)
 def test_incomplete_cohort(self):
  with TemporaryDirectory() as d:
   with self.assertRaises(ValueError):m.certify(Path(d))
 def test_no_unnatural_motor_credit(self):
  with self.assertRaises(ValueError):m.require(False,"no forged credit")
if __name__=="__main__":unittest.main()
