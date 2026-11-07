"""Carried unknown-food information: software-only Stage-1 tests."""
from copy import deepcopy
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.modules.body import BodyLaws, CognitiveBudget, CognitiveWork
from i3.modules.carried_food_information import (
    paid_carried_unknown_food_information_value)
from i3.modules.genome import midpoint
from i3.modules.mind import Mind
from i3.modules.personal_outcomes import NoPersonalSupport
from i3.modules.reference_branches import ReferenceBranchMemory

BASE = (50., 50., 50., 50., 50.)


def record(memory, key, delta):
    after = tuple(a + b for a, b in zip(BASE, delta))
    memory.observe(
        key, BASE, CognitiveWork(),
        CognitiveBudget(after, BodyLaws()))


def make_mind():
    mind = Mind(midpoint(), 109)
    mind.effects.observe(
        ("attendre",), (-.35, -.2, -.4, .2, 0.))
    mind.effects.observe(
        ("dormir",), (3., -.35, -.4, 0., 4.))
    mind._drift = mind.drift()
    return mind


def mixed_food_memory():
    memory = ReferenceBranchMemory()
    # Both are personally survived eating outcomes from other internal tokens.
    # Safe branch rewards repeated feeding; toxic branch makes repetition costly.
    record(memory, ("manger", "known-safe"), (0., 30., 0., 0., 0.))
    record(memory, ("manger", "known-toxic"), (0., 30., 0., -35., 0.))
    return memory


class CarriedUnknownFoodInformationTests(unittest.TestCase):
    def test_mixed_same_action_food_history_has_positive_information_with_two_units(self):
        body = (80., 5., 80., 80., 80.)
        result = paid_carried_unknown_food_information_value(
            make_mind(), mixed_food_memory(), "novel", 2,
            CognitiveBudget(body, BodyLaws()))
        self.assertEqual(
            result["status"],
            "COMPLETE_CARRIED_UNKNOWN_FOOD_ESTIMATE_NOT_POLICY")
        self.assertEqual(result["subjective_branches"], 2)
        self.assertEqual(result["future_repeat_units_modelled"], 1)
        self.assertGreater(result["information_value"], 0.0)
        choices = {
            tuple(row["effect_delta"]): row["best_choices"]
            for row in result["conditional_choices"]}
        self.assertIn(
            "REPEAT_ONCE",
            choices[(0., 30., 0., 0., 0.)])
        self.assertIn(
            "STOP_AFTER_TRIAL",
            choices[(0., 30., 0., -35., 0.)])
        self.assertFalse(result["trial_forced"])
        self.assertFalse(result["motor_command_authorized"])

    def test_one_carried_unit_has_zero_information_because_no_repeat_exists(self):
        body = (80., 5., 80., 80., 80.)
        result = paid_carried_unknown_food_information_value(
            make_mind(), mixed_food_memory(), "novel", 1,
            CognitiveBudget(body, BodyLaws()))
        self.assertEqual(result["future_repeat_units_modelled"], 0)
        self.assertIsNone(result["repeat_expected_value"])
        self.assertEqual(result["information_value"], 0.0)
        self.assertEqual(
            {choice for row in result["conditional_choices"]
             for choice in row["best_choices"]},
            {"STOP_AFTER_TRIAL"})

    def test_more_than_two_units_stays_bounded_to_one_repeat(self):
        body = (80., 5., 80., 80., 80.)
        result = paid_carried_unknown_food_information_value(
            make_mind(), mixed_food_memory(), "novel", 5,
            CognitiveBudget(body, BodyLaws()))
        self.assertEqual(result["future_repeat_units_modelled"], 1)
        self.assertEqual(result["additional_units_ignored_by_stage1_bound"], 3)
        self.assertEqual(result["subjective_branches"], 2)

    def test_uniformly_harmful_support_does_not_manufacture_information(self):
        memory = ReferenceBranchMemory()
        record(memory, ("manger", "a"), (0., 5., 0., -20., 0.))
        record(memory, ("manger", "b"), (0., 10., 0., -30., 0.))
        body = (80., 80., 80., 40., 80.)
        result = paid_carried_unknown_food_information_value(
            make_mind(), memory, "novel", 2,
            CognitiveBudget(body, BodyLaws()))
        self.assertEqual(result["information_value"], 0.0)
        for row in result["conditional_choices"]:
            self.assertEqual(
                row["best_choices"], ("STOP_AFTER_TRIAL",))

    def test_exact_token_support_precedes_diverse_same_action_fallback(self):
        memory = mixed_food_memory()
        record(memory, ("manger", "novel"), (0., 12., 0., -2., 0.))
        body = (80., 5., 80., 80., 80.)
        result = paid_carried_unknown_food_information_value(
            make_mind(), memory, "novel", 2,
            CognitiveBudget(body, BodyLaws()))
        self.assertEqual(result["support_records"], 1)
        self.assertEqual(result["subjective_branches"], 2)
        # One exact sample is duplicated only to satisfy the 2-branch kernel;
        # identical branches cannot create information.
        self.assertEqual(result["information_value"], 0.0)
        self.assertEqual(
            result["conditional_choices"][0]["effect_delta"],
            result["conditional_choices"][1]["effect_delta"])

    def test_same_action_fallback_is_token_renaming_invariant(self):
        a = ReferenceBranchMemory()
        b = ReferenceBranchMemory()
        effects = (
            (0., 30., 0., 0., 0.),
            (0., 30., 0., -35., 0.),
        )
        for token, delta in zip(("food-a", "food-b"), effects):
            record(a, ("manger", token), delta)
        for token, delta in zip(("renamed-x", "renamed-y"), effects):
            record(b, ("manger", token), delta)
        body = (80., 5., 80., 80., 80.)
        ra = paid_carried_unknown_food_information_value(
            make_mind(), a, "new-a", 2,
            CognitiveBudget(body, BodyLaws()))
        rb = paid_carried_unknown_food_information_value(
            make_mind(), b, "new-b", 2,
            CognitiveBudget(body, BodyLaws()))
        for key in (
                "stop_expected_value", "repeat_expected_value",
                "frozen_value", "informed_value", "information_value",
                "conditional_choices", "work"):
            self.assertEqual(ra[key], rb[key])

    def test_empty_food_history_has_no_invented_support(self):
        body = (80., 5., 80., 80., 80.)
        budget = CognitiveBudget(body, BodyLaws())
        with self.assertRaises(NoPersonalSupport):
            paid_carried_unknown_food_information_value(
                make_mind(), ReferenceBranchMemory(), "novel", 2, budget)
        self.assertGreater(budget.work.cycles, 0)

    def test_complete_forecast_covers_actual_work(self):
        body = (80., 5., 80., 80., 80.)
        result = paid_carried_unknown_food_information_value(
            make_mind(), mixed_food_memory(), "novel", 2,
            CognitiveBudget(body, BodyLaws()))
        for key in ("cycles", "simulated_steps", "memory_items", "replays"):
            self.assertLessEqual(
                result["work"][key],
                result["forecast_work_ceiling"][key])
        self.assertEqual(result["work_breakdown"]["total"], result["work"])
        self.assertFalse(result["world_access"])
        self.assertFalse(result["cost_is_physical_settlement_receipt"])

    def test_kernel_does_not_mutate_mind_or_memory(self):
        body = (80., 5., 80., 80., 80.)
        memory = mixed_food_memory()
        mind = make_mind()
        before_memory = tuple(
            (sample.key, sample.delta) for sample in memory._samples)
        before = {
            "effects": deepcopy(mind.effects.stats),
            "values": deepcopy(mind.values),
            "buffer": tuple(mind.buffer),
            "rng": mind.rng.getstate(),
            "budget_rng": mind._budget_rng.getstate(),
        }
        paid_carried_unknown_food_information_value(
            mind, memory, "novel", 2,
            CognitiveBudget(body, BodyLaws()))
        self.assertEqual(
            tuple((sample.key, sample.delta) for sample in memory._samples),
            before_memory)
        self.assertEqual(mind.effects.stats, before["effects"])
        self.assertEqual(mind.values, before["values"])
        self.assertEqual(tuple(mind.buffer), before["buffer"])
        self.assertEqual(mind.rng.getstate(), before["rng"])
        self.assertEqual(mind._budget_rng.getstate(), before["budget_rng"])

    def test_module_import_does_not_load_world_or_runtime(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.modules.carried_food_information; "
            "assert 'i3.modules.world' not in sys.modules; "
            "assert 'i3.runtime.life' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
