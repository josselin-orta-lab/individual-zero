import unittest
from types import SimpleNamespace
from i1.experimental.experienced_place_relevance import experienced_site_relevance, personally_supported_site_gain

class Place(unittest.TestCase):
    def test_physical_provenance(self):
        owner=SimpleNamespace(life_id="i1:alpha",enabled=True,examples=[{"source_position":[2,3],"delta_water":12.0,"sent_world_step":1,"observed_world_step":2}])
        self.assertEqual(personally_supported_site_gain(owner,site=(2,3),life_id="i1:alpha"),12.0)
        self.assertIsNone(personally_supported_site_gain(owner,site=(3,2),life_id="i1:alpha"))
        with self.assertRaises(ValueError): personally_supported_site_gain(owner,site=(2,3),life_id="i1:wrong")
        self.assertGreater(experienced_site_relevance(observed_gain=12,current_water=10,confidence=.8,observed_hops=2),0)
        self.assertEqual(experienced_site_relevance(observed_gain=12,current_water=90,confidence=.8,observed_hops=2),0)
