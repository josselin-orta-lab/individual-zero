"""The archived reuse characterization must keep the #1103 fixtures exactly."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from i3.lab import stage1_carried_food_reuse_characterization as C
import test_stage1_carried_food_rank_audit as T


class CharacterizationFixtureTests(unittest.TestCase):
    def test_effect_fixtures_match_the_1103_audit_tests(self):
        self.assertEqual(C.SAFE, T.SAFE)
        self.assertEqual(C.TOXIC, T.TOXIC)
        self.assertEqual(C.BASE, T.BASE)

    def test_states_and_capture_match(self):
        bodies = [(e, f, 80., i, 80.) for e in (35., 60., 85.)
                  for f in (5., 20., 40.) for i in (20., 50., 80.)]
        self.assertEqual(list(C.GRID), bodies)
        self.assertEqual(C._cap(bodies[0], 2), T.cap(bodies[0]))

    def test_minds_match(self):
        a, b = C._mind(C.MIXED), T.mind_with_mixed_food_history()
        self.assertEqual(a.effects.stats, b.effects.stats)
        a, b = C._mind(C.HARMFUL), T.mind_with_harmful_food_history()
        self.assertEqual(a.effects.stats, b.effects.stats)


if __name__ == "__main__":
    unittest.main()
