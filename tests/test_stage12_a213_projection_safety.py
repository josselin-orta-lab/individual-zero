"""A2.13: all results are physical WorldBody.apply outputs, not predictions."""
import unittest
from i0.equipment import FrozenTableEquipment
from i0.interfaces import PrimitiveCommand
from i0.modules.perception import SymbolicPerception
from i0.modules.simulator import state_from_capture
from lab.stage11_reference_fixture import build_stage11_reference_runtime
from lab.world import Position, WorldBody, WorldLayout
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from run_stage12_issue110_a213 import (
    FAMILIES, PROJECTIONS, generate_pair, analyze_pair, make_world,
)

class PhysicalCounterexamples(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base=build_stage11_reference_runtime().world.config

    def test_six_preregistered_contrasts_are_physical(self):
        for family in FAMILIES:
            with self.subTest(family=family):
                a,b=generate_pair(family,41,self.base)
                r=analyze_pair(a,b,family,41)
                self.assertTrue(r["different_physical_outcome"])
                self.assertEqual(len(r["projections"]),len(PROJECTIONS))

    def test_unknown_exact_table_prediction_still_unavailable(self):
        reference=build_stage11_reference_runtime()
        w=WorldBody(config=reference.world.config,layout=WorldLayout())
        state=state_from_capture(
            capture=SymbolicPerception().capture(
                local_state=w.capture_local(t_monde=1).as_dict(),
                telemetry=w.telemetry()),
            is_night=w.is_night(1))
        with self.assertRaises(LookupError):
            reference.equipment.predict(state=state,
                command=PrimitiveCommand("manger",{"target":"berry_a"}))

if __name__=="__main__":
    unittest.main()
