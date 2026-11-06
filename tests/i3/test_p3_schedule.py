"""P3 schedule preflight; neither selection nor validation worlds are opened."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i3.lab import p3_schedule as sched
from i3.lab import p2_ecologies as eco


class P3ScheduleTests(unittest.TestCase):
    def test_manifest_is_deterministic_and_no_reserved_condition(self):
        a = sched.schedule_manifest()
        self.assertEqual(a, sched.schedule_manifest())
        self.assertEqual(len(a["selection_keys"]), 72)
        self.assertEqual(len(a["validation_keys_unopened"]), 24)
        self.assertNotIn("reserve", {x["cohort"] for x in a["selection_keys"] +
                                       a["validation_keys_unopened"]})
        self.assertEqual(a["horizon"], eco.HORIZON)
        self.assertEqual(a["selection_cohort_policy"], "NO_RUN_BEFORE_PREREGISTRATION")

    def test_each_population_and_generation_uses_unique_worlds(self):
        m = sched.schedule_manifest()
        seen = {(row["family"], row["seed"]) for row in m["selection_keys"]}
        self.assertEqual(len(seen), 72)
        self.assertTrue(all(x["seed"] in eco.COHORTS["selection"] for x in m["selection_keys"]))
        self.assertEqual(len({(x["family"], x["seed"]) for x in m["validation_keys_unopened"]}), 24)
        self.assertTrue(all(x["seed"] in eco.COHORTS["validation"]
                            for x in m["validation_keys_unopened"]))

    def test_both_arms_share_g0_and_world_keys(self):
        m = sched.schedule_manifest()
        self.assertEqual(len(m["generation_zero_seeds"]), 4)
        self.assertEqual(len(set(sum(m["generation_zero_seeds"], []))), 24)
        self.assertEqual(m["arms"], ["selected", "random_parent"])
        self.assertEqual(sched.life_seed(0, 0, "stable", 0), 60_000)
        self.assertNotEqual(sched.mutation_seed(0, 1, 0, "selected"),
                            sched.mutation_seed(0, 1, 0, "random_parent"))

    def test_reject_bad_indices_and_inheritance_leak_schedules(self):
        for callback in (
            lambda: sched.selection_world_index(0, 3, "stable", 0),
            lambda: sched.selection_world_index(0, 0, "fake", 0),
            lambda: sched.selection_world_index(0, 0, "pulse", True),
            lambda: sched.validation_world_index(4, "stable", 0),
            lambda: sched.generation_zero_seed(0, 6),
            lambda: sched.mutation_seed(0, 0, 0, "selected"),
            lambda: sched.mutation_seed(0, 1, 0, "bogus"),
        ):
            with self.subTest(callback=callback), self.assertRaises(ValueError):
                callback()


if __name__ == "__main__":
    unittest.main()
