"""Safety and provenance contracts for the preregistered A2.30-J corpus."""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from run_stage12_issue110_b_a230j_coverage_ablation import (
    prebirth_candidate, recipes, cmd,
)
from run_stage12_issue110_first_planning_state import (
    build_prebirth_equipment,
)
from lab.stage4_reference_fixture import build_stage4_reference_runtime
from lab.world import WorldLayout, Position
from lab.equipment_corpus import EquipmentCorpusRecorder
from lab.world import WorldBody
from i0.interfaces import PrimitiveCommand


class PrebirthCoverageSafetyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        stage4 = build_stage4_reference_runtime()
        cls.config = stage4.world.config
        cls.layout = WorldLayout(
            water_sources=frozenset({Position(2, 2)}),
            resources=((Position(3, 1), "berry_a", 12),),
        )

    def test_recipes_are_fixed_bounded_and_do_not_reference_future_lives(self):
        all_recipes = recipes()
        self.assertEqual(len(all_recipes), 14)
        self.assertTrue(all(1 <= len(path) <= 8 for _, path in all_recipes))
        self.assertEqual(len({name for name, _ in all_recipes}), 14)
        self.assertEqual(sum(len(path) for _, path in all_recipes), 43)
        self.assertTrue(all(
            command.primitive in ("attendre", "dormir", "boire",
                                  "se_deplacer", "collecter", "manger")
            for _, path in all_recipes for command in path
        ))
        self.assertFalse(any(
            command.parameters.get("target") == "berry_b"
            for _, path in all_recipes for command in path
        ))

    def test_preserves_original_four_predictive_inputs_and_refuses_unknowns(self):
        expanded, audit = prebirth_candidate(
            self.config, self.layout, build_prebirth_equipment,
            food_target=True,
        )
        self.assertEqual(audit["historical_examples"], 4)
        self.assertEqual(audit["physically_applied_extra_examples"], 43)
        self.assertGreater(audit["new_unique_exact_keys"], 0)
        self.assertTrue(audit["preserved_all_historical_predictions"])
        self.assertTrue(audit["unseen_body_input_unavailable"])
        self.assertTrue(audit["unseen_berry_b_unavailable"])
        self.assertNotEqual(
            audit["baseline_equipment_sha256"], audit["equipment_sha256"]
        )
        # Direct real training-state witness: wait at the first birth state.
        example = EquipmentCorpusRecorder(
            corpus_version="test-a230j-wait"
        ).record_transition(
            world=WorldBody(config=self.config, layout=self.layout),
            t_monde=1, family="wait",
            command=PrimitiveCommand("attendre"),
        )
        prediction = expanded.predict(
            state=example.state, command=example.command
        )
        self.assertEqual(prediction.next_state, example.observed_next_state)

    def test_rejects_nonfood_or_previously_extended_corpus(self):
        with self.assertRaisesRegex(ValueError, "only baseline food"):
            prebirth_candidate(
                self.config, self.layout, build_prebirth_equipment,
                food_target=False,
            )
        with self.assertRaisesRegex(ValueError, "only baseline food"):
            prebirth_candidate(
                self.config, self.layout, build_prebirth_equipment,
                food_target=True, extended=True,
            )


if __name__ == "__main__":
    unittest.main()
