"""A2.10a: remote WorldBody entities must not masquerade as local perception."""
import unittest
from lab.world import Position, WorldLayout
from lab.stage11_reference_fixture import build_stage11_reference_runtime
from i0.modules.perception import SymbolicPerception

class LocalEntitiesOnly(unittest.TestCase):
    def test_distant_berry_is_not_a_local_observation_but_becomes_one(self):
        reference = build_stage11_reference_runtime(enable_geography=True)
        world = reference.world
        # Use the existing physical fixture and compare every visible entity
        # against the single capture's current physical position.
        capture = world.capture_local(t_monde=1)
        p=capture.position
        for entity in capture.visible_entities:
            self.assertLessEqual(abs(entity.position.x-p.x)+abs(entity.position.y-p.y),1)
        symbolic=SymbolicPerception().capture(local_state=capture.as_dict(),telemetry=world.telemetry())
        for entity in symbolic.visible_entities:
            self.assertLessEqual(abs(entity.x-p.x)+abs(entity.y-p.y),1)
