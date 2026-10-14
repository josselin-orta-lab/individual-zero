"""A2.10a: external global entities cannot masquerade as sensed neighbors."""
import unittest
from i0.modules.perception import SymbolicPerception
from lab.world import Position, WorldBody, WorldLayout
from test_symbolic_perception import world


class LocalEntitiesOnly(unittest.TestCase):
    def test_remote_berry_water_and_shelter_never_enter_perception(self):
        original=world()
        body=WorldBody(config=original.config, layout=WorldLayout(
            resources=((Position(3,1),"berry_a",2),
                       (Position(3,2),"berry_b",2),
                       (Position(2,2),"wood",1)),
            water_sources=frozenset({Position(9,9),Position(2,3)}),
            shelters=frozenset({Position(8,8),Position(2,2)}),
            creatures=frozenset({Position(7,7),Position(1,2)}),
        ))
        local=body.capture_local(t_monde=1)
        refs={x.entity_id for x in local.visible_entities}
        self.assertNotIn("berry_a:3:1",refs)
        self.assertIn("berry_b:3:2",refs)
        self.assertIn("wood:2:2",refs)
        self.assertIn("water_source:0",refs)  # local source sorted first
        self.assertNotIn("water_source:1",refs)
        for e in local.visible_entities:
            self.assertLessEqual(abs(e.position.x-2)+abs(e.position.y-2),1)
        perception=SymbolicPerception()
        cap=perception.capture(local_state=local.as_dict(),telemetry=body.telemetry())
        contributions=perception.publish_capture(capture=cap,cycle=1,ttl_steps=2)
        all_text=" ".join(str(x.payload) for x in contributions)
        self.assertNotIn("berry_a:3:1",all_text)
        self.assertNotIn("(9,9)",all_text.replace(" ",""))

    def test_remote_berry_becomes_visible_after_real_movement(self):
        body=WorldBody(config=world().config,layout=WorldLayout(
            resources=((Position(3,1),"berry_a",2),)))
        before={e.entity_id for e in body.capture_local(t_monde=1).visible_entities}
        self.assertNotIn("berry_a:3:1",before)
        from i0.interfaces import PrimitiveCommand
        body.apply(PrimitiveCommand("se_deplacer",{"direction":"north"}),t_monde=1)
        after={e.entity_id for e in body.capture_local(t_monde=2).visible_entities}
        self.assertIn("berry_a:3:1",after)


if __name__=="__main__":
    unittest.main()
