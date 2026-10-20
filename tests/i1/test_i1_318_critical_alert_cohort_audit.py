import importlib.util,sys,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"));sys.path.insert(0,str(ROOT/"scripts"))
sp=importlib.util.spec_from_file_location("a318c",ROOT/"tools/audit_i1_318_critical_alert_cohort.py")
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
class NewAlertCohortAudit(unittest.TestCase):
 def test_original_eight_pairs_only(self):
  self.assertEqual(len(m.ARMS)*len(m.WORLDS)*len(m.SEEDS),16)
  self.assertEqual(m.EXACT_RUN,39373722353)
 def test_unsealed_population_rejected(self):
  with TemporaryDirectory() as d:
   with self.assertRaises(ValueError):m.certify(Path(d))
if __name__=="__main__":unittest.main()
