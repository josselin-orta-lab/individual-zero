"""P3 deterministic runner software tests. NEVER execute a selection cohort."""
from copy import deepcopy
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import p3_pilot, p3_schedule, p2_ecologies
from i3.modules.genome import validate, digest


class P3PilotTests(unittest.TestCase):
    def test_preflight_has_zero_selection_world_exposure(self):
        with patch.object(p2_ecologies, "world_for",
                          side_effect=AssertionError("selection world opened")):
            schedule = p3_schedule.schedule_manifest()
            self.assertEqual(len(schedule["selection_keys"]), 72)
            self.assertEqual(len(schedule["validation_keys_unopened"]), 24)
        self.assertEqual(p3_pilot.MAX_SELECTION_LIVES, 864)
        self.assertEqual(p3_pilot.MAX_SELECTION_LIVES * p3_pilot.HORIZON, 345600)

    def test_run_refuses_missing_or_wrong_lock_before_world_generation(self):
        with patch.dict(os.environ, {
            "I3_P3_SOURCE_SHA": "0"*40,
            "I3_P3_SCHEDULE_SHA": "0"*64,
            "I3_P3_APPROVED_PROTOCOL": p3_pilot.PROTOCOL,
        }), patch.object(p2_ecologies, "world_for",
                         side_effect=AssertionError("must not open selection")):
            with self.assertRaises(RuntimeError):
                p3_pilot.run()

    def test_p3_birth_is_genome_only_and_deterministic(self):
        cohort = p3_pilot._newborns(0)
        self.assertEqual(cohort, p3_pilot._newborns(0))
        self.assertEqual(len(cohort), 6)
        for row in cohort:
            validate(row["genome"])
            self.assertEqual(set(row["genome"]), {"schema", "genes"})
            self.assertIsNone(row["parent_slot"])
            self.assertEqual(row["genome_sha256"], digest(row["genome"]))
            row["fitness"] = (row["slot"] % 2, row["slot"] * 10)
        first = p3_pilot._offspring(cohort, 0, 1, "selected")
        second = p3_pilot._offspring(cohort, 0, 1, "selected")
        self.assertEqual(first, second)
        for child in first:
            self.assertEqual(set(child["genome"]), {"schema", "genes"})
            validate(child["genome"])
            self.assertNotIn("memories", child)
            self.assertNotIn("map", child)
            self.assertNotIn("body", child)
            self.assertIsNone(child["fitness"])
            self.assertIn(child["parent_slot"], range(6))
            self.assertEqual(child["parent_genome_sha256"],
                             digest(cohort[child["parent_slot"]]["genome"]))

    def test_selected_parent_ranks_only_by_persistence(self):
        cohort = p3_pilot._newborns(0)
        for row in cohort:
            row["fitness"] = (0, 10*row["slot"])
        ranked = p3_pilot._rank(cohort)
        self.assertEqual([r["slot"] for r in ranked], [5, 4, 3, 2, 1, 0])
        cohort[0]["fitness"] = (1, 1)
        self.assertEqual(p3_pilot._rank(cohort)[0]["slot"], 0)
        cohort[1]["fitness"] = None
        with self.assertRaises(ValueError):
            p3_pilot._rank(cohort)

    def test_uniform_parent_control_is_reproducible(self):
        cohort = p3_pilot._newborns(2)
        for row in cohort:
            row["fitness"] = (0, 1)
        a = p3_pilot._offspring(cohort, 2, 1, "random_parent")
        b = p3_pilot._offspring(cohort, 2, 1, "random_parent")
        self.assertEqual(a, b)
        self.assertEqual(len(a), p3_schedule.GENOTYPES)

    def test_mutation_refuses_to_inherit_non_genetic_state(self):
        cohort = p3_pilot._newborns(0)
        for row in cohort:
            row["fitness"] = (0, 10)
        polluted = deepcopy(cohort)
        polluted[0]["genome"]["memories"] = ["secret"]
        with self.assertRaises(ValueError):
            p3_pilot._offspring(polluted, 0, 1, "selected")


if __name__ == "__main__":
    unittest.main()
