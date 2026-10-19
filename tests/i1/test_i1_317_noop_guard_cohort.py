import importlib.util,sys,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))
spec=importlib.util.spec_from_file_location("noop_audit317",ROOT/"tools/audit_i1_317_noop_guard_cohort.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class NoopAudit(unittest.TestCase):
 def test_missing_original_wal(self):
  with TemporaryDirectory() as d:
   with self.assertRaises(ValueError):m.certify(Path(d))
 def test_negative_unlived_effect(self):
  with self.assertRaises(ValueError):m.require(False,"test")
 def test_float_safety(self):
  with self.assertRaises(ValueError):m.f64({"wrong":"0x1p0"})
if __name__=="__main__":unittest.main()
