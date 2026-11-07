"""P1.3 on the v2 substrate: revisable place beliefs (software contract only)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.modules import genome as G
from i3.modules.mind import Mind


def _capture(water_north):
    return {"body": (80.0, 60.0, 60.0, 100.0, 100.0), "inventory": (), "here": (False, ()),
            "neighbors": ((water_north, ()), (False, ()), (False, ()), (False, ()))}


class PlaceBeliefTests(unittest.TestCase):
    def test_belief_is_revised_at_the_inherited_rate(self):
        for rate, forgotten in ((0.5, True), (0.02, False)):
            g = G.midpoint()
            g["genes"]["belief_rate"] = rate
            m = Mind(G.validate(g), 0)
            for _ in range(20):
                m.perceive(_capture(True), 0.0)
            for _ in range(8):
                m.perceive(_capture(False), 0.0)
            m.visible = ()
            self.assertEqual(m.presence((0, -1)) == 0.0, forgotten)

    def test_schema_additions_are_drawn_last_and_share_prior_draws(self):
        self.assertEqual(
            G.GENE_ORDER[-2:], ("belief_rate", "omega"))
        self.assertEqual(len(G.GENE_ORDER), 31)

    def test_visible_cell_uses_current_observation(self):
        m = Mind(G.midpoint(), 0)
        m.perceive(_capture(True), 0.0)
        self.assertEqual(m.presence((0, -1)), 1.0)
        m.perceive(_capture(False), 0.0)
        self.assertEqual(m.presence((0, -1)), 0.0)


if __name__ == "__main__":
    unittest.main()
