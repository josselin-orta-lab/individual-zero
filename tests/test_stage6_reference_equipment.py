from __future__ import annotations

import unittest

from lab.equipment_corpus import REQUIRED_EQUIPMENT_FAMILIES
from lab.stage6_reference_corpus import build_stage6_reference_corpus
from lab.stage6_reference_equipment import (
    REFERENCE_EQUIPMENT_VERSIONS,
    build_stage6_reference_equipment_bundle,
)


class Stage6ReferenceCorpusTests(unittest.TestCase):
    def test_reference_corpus_contains_all_real_required_families(self) -> None:
        corpus = build_stage6_reference_corpus()
        self.assertEqual(set(corpus.families()), set(REQUIRED_EQUIPMENT_FAMILIES))
        self.assertEqual(len(corpus.examples), len(REQUIRED_EQUIPMENT_FAMILIES))

    def test_free_and_blocked_movement_are_real_contrasts(self) -> None:
        corpus = build_stage6_reference_corpus()
        by_family = {example.family: example for example in corpus.examples}

        free = by_family["movement_free"]
        blocked = by_family["movement_blocked"]

        self.assertNotEqual(free.state.x, free.observed_next_state.x)
        self.assertEqual(blocked.state.x, blocked.observed_next_state.x)

    def test_tool_changes_collection_quantity(self) -> None:
        corpus = build_stage6_reference_corpus()
        by_family = {example.family: example for example in corpus.examples}

        plain = by_family["collection_without_tool"]
        tool = by_family["collection_with_tool"]

        plain_gain = (
            plain.observed_next_state.inventory["wood"]
            - plain.state.inventory["wood"]
        )
        tool_gain = (
            tool.observed_next_state.inventory["wood"]
            - tool.state.inventory["wood"]
        )
        self.assertEqual(plain_gain, 1)
        self.assertGreater(tool_gain, plain_gain)
        self.assertGreater(tool.state.inventory["tool"], 0)

    def test_day_night_creature_contrast_changes_integrity_only_at_night(self) -> None:
        corpus = build_stage6_reference_corpus()
        by_family = {example.family: example for example in corpus.examples}

        day = by_family["creature_day"]
        night = by_family["creature_night"]

        day_loss = day.state.body["integrity"] - day.observed_next_state.body["integrity"]
        night_loss = (
            night.state.body["integrity"]
            - night.observed_next_state.body["integrity"]
        )
        self.assertFalse(day.state.is_night)
        self.assertTrue(night.state.is_night)
        self.assertEqual(day_loss, 0.0)
        self.assertGreater(night_loss, 0.0)

    def test_shelter_example_is_actual_closed_shelter_transition(self) -> None:
        corpus = build_stage6_reference_corpus()
        shelter = next(
            example
            for example in corpus.examples
            if example.family == "shelter_state"
        )

        self.assertFalse(shelter.state.known_shelter_here)
        self.assertTrue(shelter.observed_next_state.known_shelter_here)


class Stage6ReferenceEquipmentTests(unittest.TestCase):
    def test_all_three_reference_versions_pass_conjunctive_equivalence(self) -> None:
        bundle = build_stage6_reference_equipment_bundle()

        self.assertEqual(
            tuple(model.version for model in bundle.models),
            REFERENCE_EQUIPMENT_VERSIONS,
        )
        self.assertTrue(
            all(result.equivalent for result in bundle.benchmark_results)
        )
        self.assertTrue(
            all(result.failed_criteria == () for result in bundle.benchmark_results)
        )

    def test_three_versions_are_distinct_immutable_artifacts(self) -> None:
        bundle = build_stage6_reference_equipment_bundle()
        digests = {model.artifact_digest for model in bundle.models}

        self.assertEqual(len(digests), 3)


if __name__ == "__main__":
    unittest.main()
