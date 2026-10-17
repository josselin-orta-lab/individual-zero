from __future__ import annotations

import unittest

from i0.equipment import EquipmentCorpus, EquipmentCorpusExample
from i0.interfaces import PrimitiveCommand
from lab.equipment_corpus import (
    REQUIRED_EQUIPMENT_FAMILIES,
    EquipmentCorpusRecorder,
    evaluate_corpus_coverage,
    require_corpus_coverage,
)
from lab.world import Position, WorldBody, WorldLayout

from test_stage4_runtime import world_config


class EquipmentCorpusTests(unittest.TestCase):
    def test_recorder_uses_accessible_state_and_inventory(self) -> None:
        world = WorldBody(
            config=world_config(),
            layout=WorldLayout(
                resources=((Position(2, 2), "wood", 1),),
            ),
        )
        recorder = EquipmentCorpusRecorder(
            corpus_version="stage6-corpus-test-v1"
        )

        example = recorder.record_transition(
            world=world,
            t_monde=1,
            family="collection_without_tool",
            command=PrimitiveCommand(
                "collecter",
                {"target": "wood"},
            ),
        )

        self.assertEqual(example.state.inventory["wood"], 0)
        self.assertEqual(example.observed_next_state.inventory["wood"], 1)
        self.assertIn("wood", example.state.current_resources)
        self.assertNotIn("wood", example.observed_next_state.current_resources)

    def test_missing_required_family_is_explicit(self) -> None:
        world = WorldBody(
            config=world_config(),
            layout=WorldLayout(),
        )
        recorder = EquipmentCorpusRecorder(
            corpus_version="stage6-corpus-test-v1"
        )
        recorder.record_transition(
            world=world,
            t_monde=1,
            family="wait",
            command=PrimitiveCommand("attendre"),
        )
        corpus = recorder.build()

        coverage = evaluate_corpus_coverage(corpus)

        self.assertFalse(coverage.complete)
        self.assertIn("movement_free", coverage.missing)
        with self.assertRaisesRegex(ValueError, "missing required families"):
            require_corpus_coverage(corpus)

    def test_closed_required_family_set_can_be_satisfied(self) -> None:
        world = WorldBody(
            config=world_config(),
            layout=WorldLayout(),
        )
        recorder = EquipmentCorpusRecorder(
            corpus_version="stage6-corpus-test-v1"
        )
        base = recorder.record_transition(
            world=world,
            t_monde=1,
            family="wait",
            command=PrimitiveCommand("attendre"),
        )

        examples = tuple(
            EquipmentCorpusExample(
                family=family,
                state=base.state,
                command=base.command,
                observed_next_state=base.observed_next_state,
                terminal=False,
            )
            for family in sorted(REQUIRED_EQUIPMENT_FAMILIES)
        )
        corpus = EquipmentCorpus(
            version="coverage-only-test-v1",
            examples=examples,
        )

        coverage = evaluate_corpus_coverage(corpus)
        self.assertTrue(coverage.complete)
        self.assertEqual(coverage.missing, ())


if __name__ == "__main__":
    unittest.main()
