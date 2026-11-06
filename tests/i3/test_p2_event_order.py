"""Ecological event ordering: an action uses the state the agent just saw."""
from dataclasses import replace
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i3.lab import p2_ecologies as eco
from i3.modules.body import CognitiveWork
from i3.modules.world import WaterSource, World


class ExogenousEventBoundaryTests(unittest.TestCase):
    def test_source_exhaustion_does_not_invalidate_previously_visible_drink(self):
        original = eco.world_for("stable", "development", 0)
        here = original.spawn
        spec = replace(original,
                       water={here: WaterSource(25.0, stock=1, max_stock=1)},
                       food={q: f for q, f in original.food.items() if q != here},
                       changes=((1, "water_stock", here, 0),
                                (2, "water_stock", here, 1)))
        w = World(spec)
        self.assertTrue(w.capture()["here"][0])
        out = w.step("boire", None, CognitiveWork())
        self.assertEqual(out["t"], 1)
        self.assertEqual(w.water[here].stock, 0)
        self.assertFalse(w.capture()["here"][0])
        w.step("attendre", None, CognitiveWork())
        self.assertEqual(w.water[here].stock, 1)
        self.assertTrue(w.capture()["here"][0])
        w.step("boire", None, CognitiveWork())
        self.assertEqual(w.water[here].stock, 0)

    def test_hidden_effect_change_affects_only_next_action(self):
        original = eco.world_for("stable", "development", 1)
        here = original.spawn
        name = "safe-berry"
        from i3.modules.world import FoodPatch
        spec = replace(original, food={here: FoodPatch(name, 2, 2)},
                       token_effects={name: (10.0, 0.0)},
                       changes=((2, "token_effect", name, (0.0, -6.0)),))
        w = World(spec)
        w.step("collecter", name, CognitiveWork())  # t=1
        before = w.body
        w.step("manger", name, CognitiveWork())  # t=2, old effect still valid
        self.assertGreater(w.body[1], before[1])
        self.assertEqual(w.effects[name], (0.0, -6.0))
        w.step("collecter", name, CognitiveWork())  # t=3
        before = w.body
        w.step("manger", name, CognitiveWork())  # t=4, new effect
        self.assertLess(w.body[3], before[3])

    def test_invalid_action_still_rolls_back_schedule(self):
        original = eco.world_for("stable", "development", 2)
        here = original.spawn
        spec = replace(original,
                       water={here: WaterSource(25.0, stock=1, max_stock=1)},
                       changes=((1, "water_stock", here, 0),))
        w = World(spec)
        with self.assertRaises(ValueError):
            w.step("manger", "unowned", CognitiveWork())
        self.assertEqual(w.t, 0)
        self.assertEqual(w.water[here].stock, 1)
        self.assertEqual(len(w.effects), len(spec.token_effects))


if __name__ == "__main__":
    unittest.main()
