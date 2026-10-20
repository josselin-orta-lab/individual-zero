import importlib.util,sys,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))
spec=importlib.util.spec_from_file_location("a318",ROOT/"tools/audit_i1_318_alert_sleep_reentry.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class SleepWakeAudit318(unittest.TestCase):
 def test_missing_original_cohort_fails(self):
  with TemporaryDirectory() as d:
   with self.assertRaises(ValueError):m.audit(Path(d))
 def test_no_fake_motor_or_unreadable_wal(self):
  with TemporaryDirectory() as d:
   with self.assertRaises(ValueError):m.read_one_original_wal(Path(d)/"missing.wal")
 def test_all_16_births_only(self):
  self.assertEqual(len(m.ARMS)*len(m.SEEDS)*len(m.WORLDS),16)
if __name__=="__main__":unittest.main()
