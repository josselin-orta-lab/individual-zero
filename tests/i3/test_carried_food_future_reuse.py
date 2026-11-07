"""Opt-in inventory-bounded future reuse in the carried-food kernel (software only)."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.modules.body import BodyLaws, CognitiveBudget, CognitiveWork
from i3.modules.carried_food_information import (
    paid_carried_unknown_food_information_value)
from i3.modules.genome import midpoint
from i3.modules.mind import Mind
from i3.modules.reference_branches import ReferenceBranchMemory

BASE = (50., 50., 50., 50., 50.)


def record(memory, key, delta):
    after = tuple(a + b for a, b in zip(BASE, delta))
    memory.observe(key, BASE, CognitiveWork(), CognitiveBudget(after, BodyLaws()))


def make_mind():
    mind = Mind(midpoint(), 109)
    mind.effects.observe(("attendre",), (-.35, -.2, -.4, .2, 0.))
    mind.effects.observe(("dormir",), (3., -.35, -.4, 0., 4.))
    mind._drift = mind.drift()
    return mind


def memory_with(*rows):
    memory = ReferenceBranchMemory()
    for name, delta in rows:
        record(memory, ("manger", name), delta)
    return memory


MIXED = (("known-safe", (0., 30., 0., 0., 0.)),
         ("known-toxic", (0., 30., 0., -35., 0.)))
HARMFUL = (("known-a", (0., 5., 0., -20., 0.)),
           ("known-b", (0., 10., 0., -30., 0.)))
HUNGRY = (80., 5., 80., 80., 80.)


def value(memory, inventory, body=HUNGRY, **kw):
    return paid_carried_unknown_food_information_value(
        make_mind(), memory, "novel", inventory,
        CognitiveBudget(body, BodyLaws()), **kw)


class FutureReuseTests(unittest.TestCase):
    def test_default_is_the_bounded_1102_kernel(self):
        a = value(memory_with(*MIXED), 5)
        b = value(memory_with(*MIXED), 5, max_future_repeats=1)
        self.assertEqual(a["future_repeat_units_modelled"], 1)
        self.assertEqual(a["additional_units_ignored_by_stage1_bound"], 3)
        for key in ("information_value", "informed_value", "frozen_value", "work"):
            self.assertEqual(a[key], b[key])

    def test_repeats_are_bounded_by_carried_units(self):
        r = value(memory_with(*MIXED), 3, max_future_repeats=8)
        self.assertEqual(r["future_repeat_units_modelled"], 2)
        self.assertEqual(r["additional_units_ignored_by_stage1_bound"], 0)
        self.assertEqual(len(r["plan_expected_values"]), 3)
        one = value(memory_with(*MIXED), 1, max_future_repeats=8)
        self.assertEqual(one["future_repeat_units_modelled"], 0)
        self.assertEqual(one["information_value"], 0.0)

    def test_outcome_branches_stay_personal_rows_only(self):
        for k in (1, 2, 4):
            r = value(memory_with(*MIXED), k + 1, max_future_repeats=k)
            self.assertEqual(r["subjective_branches"], 2)
            for choice in r["conditional_choices"]:
                self.assertEqual(len(choice["plan_values"]), k + 1)

    def test_information_only_from_branch_disagreement(self):
        # Corrected invariant (characterization Amendment 1): information is
        # positive only when the personally best plan differs between effect
        # branches, harmful or not; when branches agree it is exactly zero.
        for rows in (MIXED, HARMFUL):
            for body in (HUNGRY, (60., 20., 80., 80., 80.), (85., 40., 80., 50., 80.)):
                for k in (1, 2, 4, 8):
                    r = value(memory_with(*rows), k + 1, body=body,
                              max_future_repeats=k)
                    best = [set(c["best_choices"]) for c in r["conditional_choices"]]
                    disagree = not set.intersection(*best)
                    if disagree:
                        self.assertGreater(r["information_value"], 0.0)
                    else:
                        self.assertEqual(r["information_value"], 0.0)

    def test_harmful_positive_information_predates_this_slice(self):
        # The same value at the default bound: the #1102 kernel already has it.
        r = value(memory_with(*HARMFUL), 2)
        self.assertAlmostEqual(r["information_value"], 0.037307836963297314, places=12)

    def test_every_represented_plan_is_paid(self):
        works = [value(memory_with(*MIXED), k + 1, max_future_repeats=k)["work"]
                 for k in (1, 2, 4, 8)]
        for small, large in zip(works, works[1:]):
            self.assertGreater(large["simulated_steps"], small["simulated_steps"])
            self.assertGreater(large["cycles"], small["cycles"])
            self.assertGreater(large["memory_items"], small["memory_items"])
        r = value(memory_with(*MIXED), 9, max_future_repeats=8)
        for key, spent in r["work"].items():
            self.assertLessEqual(spent, r["forecast_work_ceiling"][key])

    def test_informed_value_bounds(self):
        r = value(memory_with(*MIXED), 5, max_future_repeats=4)
        self.assertGreaterEqual(r["informed_value"], r["frozen_value"])
        self.assertEqual(r["frozen_value"], max(r["plan_expected_values"]))
        self.assertGreaterEqual(r["information_value"], 0.0)

    def test_invalid_repeat_bound_rejected(self):
        for bad in (0, -1, 1.5, True):
            with self.assertRaises(ValueError):
                value(memory_with(*MIXED), 3, max_future_repeats=bad)

    def test_token_renaming_invariant(self):
        a = paid_carried_unknown_food_information_value(
            make_mind(), memory_with(*MIXED), "novel", 4,
            CognitiveBudget(HUNGRY, BodyLaws()), max_future_repeats=3)
        b = paid_carried_unknown_food_information_value(
            make_mind(), memory_with(*MIXED), "zz-other", 4,
            CognitiveBudget(HUNGRY, BodyLaws()), max_future_repeats=3)
        for key in ("information_value", "informed_value", "frozen_value", "work"):
            self.assertEqual(a[key], b[key])


if __name__ == "__main__":
    unittest.main()
