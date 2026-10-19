import importlib.util,sys,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))
sp=importlib.util.spec_from_file_location("margin317",ROOT/"tools/audit_i1_317_place_competition_margins.py")
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
class Margins(unittest.TestCase):
 def test_incomplete_original_certificate_rejected(self):
  with TemporaryDirectory() as d:
   with self.assertRaises(ValueError):m.run(Path(d))
 def test_same_candidate_changed_score_not_motor_claim(self):
  key=(5,1,"option:place-memory:test")
  old={"learned_site_candidates_scored":{key:{"position":(8,8),"evidence":0.02,"crossed":False,"threshold_fraction":0.1}}}
  new={"learned_site_candidates_scored":{key:{"position":(8,8),"evidence":0.10,"crossed":False,"threshold_fraction":0.4}}}
  got=m.compare_scores(old,new)
  self.assertEqual(got["number_with_changed_evidence_or_crossing"],1)
  self.assertEqual(got["changed_crossing_outcomes"],0)
 def test_mortality_boundaries_not_bypassed(self):
  with self.assertRaises(ValueError):
   m.compare_motors({"physical_action_by_step":{1:("dormir",{})}},
                    {"physical_action_by_step":{1:("dormir",{}),2:("attendre",{})}})
if __name__=="__main__":unittest.main()
