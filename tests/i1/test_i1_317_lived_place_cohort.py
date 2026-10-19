"""Adversarial bounded evidence validation for 24 original mortal place WAL."""
import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
import sys,unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))
spec=importlib.util.spec_from_file_location("audit24",ROOT/"tools/audit_i1_317_lived_place_cohort.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class PlaceCohort317Tests(unittest.TestCase):
 def test_missing_cohort_fails(self):
  with TemporaryDirectory() as d:
   with self.assertRaises(ValueError):m.certify(Path(d))
 def test_invalid_water_bodily_claim_fails(self):
  with self.assertRaises(ValueError):m.measured({"invalid":15})
  with self.assertRaises(ValueError):m.measured(float("nan"))
 def test_no_nonphysical_events(self):
  with TemporaryDirectory() as d:
   p=Path(d)/"fake.wal"
   p.write_text('{"causal_event":{"kind":"perceptual_capture","t_monde":301}}\n')
   with self.assertRaises(ValueError):m.classify_original(p,10)
if __name__=="__main__":unittest.main()
