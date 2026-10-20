import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"));sys.path.insert(0,str(ROOT/"scripts"))
spec=importlib.util.spec_from_file_location("exp317",ROOT/"tools/run_i1_317_experiential_place_relevance.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class ExperientialRelevance(unittest.TestCase):
 def test_matched_retrieval_and_fresh_births(self):
  self.assertEqual(m.ARMS,("guard_control","guard_experiential"))
  self.assertEqual({m.factors(a) for a in m.ARMS},{(True,False),(True,True)})
  self.assertEqual(len(m.ARMS)*len(m.SEEDS)*len(m.PRESETS),18)
  self.assertTrue(set(m.SEEDS).isdisjoint({13127,13219,14083,14107}))
 def test_no_personal_evidence_no_value(self):
  for water in (30.01,65,100):
   self.assertEqual(m.lived_place_relevance(experienced_water_gain=35,current_observed_water=water,memory_confidence=.9,witnessed_hops=1),0)
 def test_bounded_uncertainty(self):
  near=m.lived_place_relevance(experienced_water_gain=35,current_observed_water=10,memory_confidence=.9,witnessed_hops=1)
  far=m.lived_place_relevance(experienced_water_gain=35,current_observed_water=10,memory_confidence=.9,witnessed_hops=8)
  self.assertTrue(0<far<near<=m.MAX_ASSOCIATIVE_RELEVANCE)
  for d in (0,-1,float("nan"),float("inf")):
   with self.assertRaises(ValueError):
    m.lived_place_relevance(experienced_water_gain=d,current_observed_water=10,memory_confidence=.9,witnessed_hops=1)
  with self.assertRaises(ValueError):
   m.lived_place_relevance(experienced_water_gain=35,current_observed_water=10,memory_confidence=.9,witnessed_hops=9)
if __name__=="__main__":unittest.main()
