"""I1 preset worlds are finite, physically valid and never scripted policy."""
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from run_i1_world_preset import available, load_preset


class WorldPresetsTests(unittest.TestCase):
    def test_registered_worlds_validate_without_a_birth(self):
        worlds = available()
        self.assertEqual({p["id"] for p, _ in worlds},
                         {"oasis", "foraging", "dry-valley", "empty-land",
                          "hazard-edge", "blocked-route", "memory-corridor",
                          "water-isolated-corridor"})
        self.assertEqual(len({digest for _p, digest in worlds}), len(worlds))
        for p, digest in worlds:
            with self.subTest(world=p["id"]):
                self.assertEqual(len(digest), 64)
                self.assertEqual(p["engine"], "I1")
                self.assertLessEqual(p["recommended_steps"], 300)
                self.assertNotIn("forced_actions", p)
                self.assertNotIn("learned_policy", p)

    def test_invalid_layout_and_hidden_injected_behaviour_rejected(self):
        original, _ = load_preset("oasis")
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "oasis.json"
            cases = [
                {**original, "spawn": [0, 0]},
                {**original, "extra_forced_action": "boire"},
                {**original, "layout": {**original["layout"],
                    "obstacles": [original["spawn"]]}},
                {**original, "layout": {**original["layout"],
                    "resources": [{"cell": [9, 9], "kind": "free_food",
                                   "quantity": 10}]}},
            ]
            for case in cases:
                path.write_text(json.dumps(case))
                with self.assertRaises(ValueError):
                    load_preset("oasis", presets_dir=tmp)

    def test_unknown_world_cannot_be_loaded(self):
        for name in ("../oasis", "missing", "", "OASIS", "oasis.json"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                load_preset(name)


if __name__ == "__main__":
    unittest.main()
