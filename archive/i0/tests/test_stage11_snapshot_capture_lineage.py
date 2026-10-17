"""Stage11 geographic snapshot physical-capture lineage, unit only.

Fixtures represent local-Perception-shaped objects and are not lived
observations, causal evidence, safety facts or held-out experiments.
"""
from copy import deepcopy
from types import SimpleNamespace
from unittest import TestCase

from i0.modules.geographic_exploration import (
    GeographicExploration, GeographicExplorationConfig,
)


def config(mode: str) -> GeographicExplorationConfig:
    if mode not in ("plain_v1", "observed_v2", "refresh_v3"):
        raise ValueError("undeclared unit snapshot mode")
    return GeographicExplorationConfig(
        version="p48-local-capture-lineage-unit-" + mode,
        novelty_weight=0.7,
        max_distinct_sites=4,
        max_targets_per_cycle=1,
        observe_routes=(mode != "plain_v1"),
        refresh_surveys=(mode == "refresh_v3"),
    )


def physical_shaped_capture(step: int, x: int = 2, y: int = 2):
    directions = (
        ("north", 0, -1), ("east", 1, 0),
        ("south", 0, 1), ("west", -1, 0),
    )
    return SimpleNamespace(
        t_monde=step, x=x, y=y,
        adjacent=tuple(
            SimpleNamespace(
                direction=name, x=x + dx, y=y + dy,
                passable=name == "east", creature=False,
            ) for name, dx, dy in directions
        ),
    )


class GeographicCaptureLineageSnapshotTests(TestCase):
    def test_pristine_owner_roundtrips_and_rejects_forged_capture_atomically(self):
        for mode in ("plain_v1", "observed_v2", "refresh_v3"):
            with self.subTest(mode=mode):
                owner = GeographicExploration(config(mode))
                pristine = owner.export_causal_state()
                self.assertEqual(pristine["visits"], [])
                self.assertIsNone(pristine["last_capture"])
                clone = GeographicExploration(config(mode))
                clone.restore_causal_state(deepcopy(pristine))
                self.assertEqual(clone.export_causal_state(), pristine)

                impossible = deepcopy(pristine)
                impossible["last_capture"] = [1, 2, 2]
                with self.assertRaises(ValueError):
                    clone.restore_causal_state(impossible)
                self.assertEqual(clone.export_causal_state(), pristine)

    def test_nonempty_ledger_requires_last_real_shaped_capture_even_without_survey(self):
        for mode in ("plain_v1", "observed_v2", "refresh_v3"):
            with self.subTest(mode=mode):
                initial = physical_shaped_capture(1)
                owner = GeographicExploration(config(mode))
                self.assertTrue(owner.observe_capture(initial))
                saved = owner.export_causal_state()
                self.assertEqual(saved["visits"], [[2, 2, 1]])
                self.assertEqual(saved["last_capture"], [1, 2, 2])
                if mode != "plain_v1":
                    # Paid Exploration may be unavailable. A valid v2/v3
                    # owner can retain a real visit with NO recorded survey.
                    self.assertEqual(saved["surveys"], [])

                clone = GeographicExploration(config(mode))
                clone.restore_causal_state(deepcopy(saved))
                self.assertEqual(clone.export_causal_state(), saved)

                corrupted = deepcopy(saved)
                corrupted["last_capture"] = None
                with self.assertRaisesRegex(ValueError, "last physical capture"):
                    clone.restore_causal_state(corrupted)
                self.assertEqual(
                    clone.export_causal_state(), saved,
                    "rejected restore must never partially replace owner state",
                )

                # A later legitimate same-site physical capture does not
                # invent a new site, and normal survey ownership still works.
                next_capture = physical_shaped_capture(2)
                self.assertFalse(clone.observe_capture(next_capture))
                self.assertEqual(clone.distinct_sites, 1)
                self.assertEqual(clone.visit_count, 1)
                if mode == "plain_v1":
                    self.assertFalse(clone.record_survey(next_capture))
                else:
                    self.assertTrue(clone.record_survey(next_capture))
                    self.assertEqual(len(clone.surveys), 1)
                latest = clone.export_causal_state()
                self.assertEqual(latest["last_capture"], [2, 2, 2])
                self.assertEqual(latest["visits"], [[2, 2, 1]])

    def test_populated_survey_snapshots_still_roundtrip_exactly(self):
        for mode in ("observed_v2", "refresh_v3"):
            with self.subTest(mode=mode):
                owner = GeographicExploration(config(mode))
                captured = physical_shaped_capture(1)
                owner.observe_capture(captured)
                self.assertTrue(owner.record_survey(captured))
                state = owner.export_causal_state()
                self.assertEqual(len(state["surveys"]), 1)
                clone = GeographicExploration(config(mode))
                clone.restore_causal_state(deepcopy(state))
                self.assertEqual(clone.export_causal_state(), state)
                self.assertEqual(clone.surveys[0].world_step, 1)


if __name__ == "__main__":
    import unittest
    unittest.main()
