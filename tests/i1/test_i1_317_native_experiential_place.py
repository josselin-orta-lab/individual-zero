"""#317: strict opt-in native learned-site Stage8 and M11 birth contract."""
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import importlib.util
import sys
import unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"src"))
from i1.experimental.lived_water import I1LivedWaterOwner
from i1.modules.experienced_place_relevance import (
    experienced_site_relevance, personally_supported_site_gain,
    MAX_RELEVANCE,
)

class NativeExperience317(unittest.TestCase):
    def test_pure_bound_and_thirst_gate(self):
        self.assertEqual(experienced_site_relevance(
            observed_gain=40,current_water=70,confidence=1,observed_hops=1),0)
        near=experienced_site_relevance(
            observed_gain=40,current_water=15,confidence=1,observed_hops=1)
        far=experienced_site_relevance(
            observed_gain=40,current_water=15,confidence=.5,observed_hops=8)
        self.assertTrue(0 < far < near <= MAX_RELEVANCE)
        for n in (0,-1,float("nan"),float("inf")):
            with self.assertRaises(ValueError):
                experienced_site_relevance(
                    observed_gain=n,current_water=15,confidence=1,observed_hops=1)
    def test_personal_owner_only(self):
        o=I1LivedWaterOwner(life_id="i1:test",enabled=True)
        self.assertIsNone(personally_supported_site_gain(o,site=(8,8),life_id="i1:test"))
        with self.assertRaises(ValueError):
            personally_supported_site_gain(o,site=(8,8),life_id="i1:other")
        o.record_applied(sent_world_step=1,before_water=20,x=8,y=8,
                         command_hash="physical",option_ref="option:a",
                         first_capture_hash="before")
        result=o.observe_followup(observed_world_step=2,x=8,y=8,
                         observed_water=55,current_water_source=True,
                         followup_capture_hash="after",paid_uc=True)
        self.assertTrue(result["admitted"])
        self.assertEqual(personally_supported_site_gain(
            o,site=(8,8),life_id="i1:test"),35)
        self.assertIsNone(personally_supported_site_gain(
            o,site=(9,8),life_id="i1:test"))
        snapshot=o.export_causal_state()
        new=I1LivedWaterOwner(life_id="i1:test",enabled=True)
        new._load_trusted_current_on_fresh(snapshot)
        self.assertEqual(personally_supported_site_gain(
            new,site=(8,8),life_id="i1:test"),35)
        with self.assertRaises(ValueError):
            new._load_trusted_current_on_fresh(snapshot)
if __name__=="__main__":
    unittest.main()
