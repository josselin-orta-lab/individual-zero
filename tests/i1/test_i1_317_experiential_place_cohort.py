"""Adversarial audit guards: no invented motor consequence from a score."""
import importlib.util,sys,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))
spec=importlib.util.spec_from_file_location("e317",ROOT/"tools/audit_i1_317_experiential_place_cohort.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class TestExperientialWAL(unittest.TestCase):
 def test_no_missing_lives(self):
  with TemporaryDirectory() as p:
   with self.assertRaises(ValueError):m.certify(Path(p))
 def test_nonnumeric_score(self):
  with self.assertRaises(ValueError):m.number({"nonsense":1})
 def test_no_false_equal_uc(self):
  a={"physical_motors":{1:("attendre",{}),2:("dormir",{})},"accepted_uc_by_step":{1:3,2:5},"competition_traces":{},"all_place_proposals":{}}
  b={"physical_motors":{1:("attendre",{}),2:("se_deplacer",{})},"accepted_uc_by_step":{1:4,2:5},"competition_traces":{},"all_place_proposals":{}}
  with self.assertRaises(ValueError):m.paired_effect(a,b)
 def test_score_alone_no_motor_credit(self):
  ref={"physical_motors":{1:("dormir",{})},"accepted_uc_by_step":{1:2},"competition_traces":{},"all_place_proposals":{}}
  self.assertIsNone(m.paired_effect(ref,ref)["first_physical_motor_divergence"])
if __name__=="__main__":unittest.main()
