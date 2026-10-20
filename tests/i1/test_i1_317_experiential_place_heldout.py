import importlib.util,sys,unittest,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"));sys.path.insert(0,str(ROOT/"scripts"))
spec=importlib.util.spec_from_file_location("heldout",ROOT/"tools/run_i1_317_experiential_place_heldout.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Heldout(unittest.TestCase):
 def test_registered_births_are_new(self):
  self.assertEqual(len(m.SEEDS)*len(m.PRESETS)*len(m.ARMS),32)
  self.assertTrue(set(m.SEEDS).isdisjoint({15121,15173,15313,14083,14107,13127,13219}))
  self.assertEqual({m.factors(a) for a in m.ARMS},{(True,False),(True,True)})
 def test_water_berry_separation(self):
  p=json.loads((ROOT/"src/i1/lab/world_presets/water-isolated-corridor.json").read_text())
  water={tuple(x) for x in p['layout']['water_sources']}
  berries={tuple(r['cell']) for r in p['layout']['resources'] if r['kind'].startswith('berry')}
  self.assertEqual(water,{(8,8)})
  self.assertEqual(berries,{(10,8)})
  self.assertFalse(water & berries)
 def test_no_unearned_association(self):
  self.assertEqual(m.lived_place_relevance(experienced_water_gain=20,current_observed_water=70,memory_confidence=.9,witnessed_hops=1),0)
  for v in (0,-1,float("nan")):
   with self.assertRaises(ValueError):m.lived_place_relevance(experienced_water_gain=v,current_observed_water=12,memory_confidence=.9,witnessed_hops=1)
if __name__=="__main__":unittest.main()
