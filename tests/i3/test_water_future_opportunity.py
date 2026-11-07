"""One-future-water-opportunity Stage-1 software falsifiers."""
from copy import deepcopy
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.modules.body import (
    BodyLaws, CognitiveBudget, CognitiveFundingError, CognitiveWork)
from i3.modules.genome import midpoint
from i3.modules.mind import Mind
from i3.modules.reference_branches import ReferenceBranchMemory
from i3.modules.water_future_opportunity import (
    _future_opportunity_reduction,
    paid_water_one_future_opportunity_value)

BASE = (50., 50., 50., 50., 50.)
EXPLORE = (("se_deplacer",),)
ORDINARY = (
    ("ordinary-wait", (("attendre",),)),
    ("ordinary-sleep", (("dormir",),)),
)


def record(memory, key, delta):
    after = tuple(a + b for a, b in zip(BASE, delta))
    memory.observe(
        key, BASE, CognitiveWork(),
        CognitiveBudget(after, BodyLaws()))


def realistic_memory():
    memory = ReferenceBranchMemory()
    for key, delta in (
        (("se_deplacer", None), (-2., -.2, -.4, 0., 0.)),
        (("attendre", None), (-.35, -.2, -.4, .2, 0.)),
        (("dormir", None), (3., -.35, -.4, 0., 4.)),
    ):
        record(memory, key, delta)
    return memory


def high_scale_memory():
    memory = ReferenceBranchMemory()
    for key, delta in (
        (("se_deplacer", None), (35., 20., 20., 15., 25.)),
        (("attendre", None), (-40., -25., -30., -10., -30.)),
        (("dormir", None), (30., -20., 25., -20., 20.)),
    ):
        record(memory, key, delta)
    return memory


def make_mind():
    mind = Mind(midpoint(), 97)
    mind.map = {}
    mind.effects.observe(
        ("se_deplacer",), (-2., -.2, -.4, 0., 0.))
    mind.effects.observe(
        ("attendre",), (-.35, -.2, -.4, .2, 0.))
    mind.effects.observe(
        ("dormir",), (3., -.35, -.4, 0., 4.))
    mind._drift = mind.drift()
    return mind


class FutureOpportunityReductionTests(unittest.TestCase):
    def test_zero_future_opportunity_collapses_information_to_zero(self):
        conditional = (.5, .5)
        ordinary = (
            {"wait": 1.0, "sleep": 2.0},
            {"wait": 2.0, "sleep": 1.0},
        )
        reuse = (
            {"wait": 10.0, "sleep": 0.0},
            {"wait": 0.0, "sleep": 10.0},
        )
        result = _future_opportunity_reduction(
            conditional, ordinary, reuse, 0.0)
        self.assertEqual(result["information_value"], 0.0)
        self.assertAlmostEqual(result["informed_value"], 1.5)
        self.assertAlmostEqual(result["frozen_value"], 1.5)

    def test_future_opportunity_can_make_effect_information_positive(self):
        conditional = (.5, .5)
        ordinary = (
            {"wait": 2.0, "sleep": 2.0},
            {"wait": 2.0, "sleep": 2.0},
        )
        reuse = (
            {"wait": 8.0, "sleep": 7.0},
            {"wait": -3.0, "sleep": -4.0},
        )
        result = _future_opportunity_reduction(
            conditional, ordinary, reuse, .25)
        self.assertGreater(result["information_value"], 0.0)
        self.assertGreaterEqual(
            result["informed_value"], result["frozen_value"])

    def test_invalid_future_probability_fails(self):
        ordinary = (
            {"wait": 1.0},
            {"wait": 1.0},
        )
        for p in (-.1, 1.1):
            with self.assertRaises(ValueError):
                _future_opportunity_reduction(
                    (.5, .5), ordinary, ordinary, p)


class WaterOneFutureOpportunityTests(unittest.TestCase):
    def test_realistic_grid_has_selective_epistemic_trials(self):
        memory = realistic_memory()
        rows = []
        for channel in range(5):
            for level in (20., 30., 40., 50.):
                body = [80., 80., 80., 80., 80.]
                body[channel] = level
                body = tuple(body)
                for horizon in (4, 6, 8, 12):
                    try:
                        result = paid_water_one_future_opportunity_value(
                            make_mind(), memory, EXPLORE, ORDINARY, horizon,
                            CognitiveBudget(body, BodyLaws()))
                    except CognitiveFundingError:
                        continue
                    rows.append((
                        body,
                        horizon,
                        result["target_node_best_choices"],
                        result["trial_information_value"],
                        result["trial_advantage"],
                    ))
        self.assertTrue(rows)
        selected = [
            row for row in rows
            if "TRIAL" in row[2] and row[3] > 1e-12
        ]
        declined = [
            row for row in rows
            if row[2] == ("DECLINE_TRIAL",)
        ]
        stats = {
            "evaluated": len(rows),
            "selected_epistemic": len(selected),
            "declined": len(declined),
            "max_information_value": max(row[3] for row in rows),
            "best_trial_advantage": max(row[4] for row in rows),
            "worst_trial_advantage": min(row[4] for row in rows),
        }
        print("ONE_FUTURE_OPPORTUNITY_SWEEP", stats)
        self.assertTrue(
            selected,
            "future-opportunity model never selects epistemic trial: "
            + repr(stats))
        self.assertTrue(
            declined,
            "future-opportunity model forces all trials: " + repr(stats))

    def test_high_personal_scale_can_reject_trial(self):
        body = (80., 80., 25., 80., 80.)
        result = paid_water_one_future_opportunity_value(
            make_mind(), high_scale_memory(), EXPLORE, ORDINARY, 6,
            CognitiveBudget(body, BodyLaws()))
        self.assertEqual(
            result["target_node_best_choices"], ("DECLINE_TRIAL",))
        self.assertLess(result["trial_advantage"], 0.0)

    def test_future_opportunity_is_not_current_source_persistence(self):
        body = (20., 80., 80., 80., 80.)
        result = paid_water_one_future_opportunity_value(
            make_mind(), realistic_memory(), EXPLORE, ORDINARY, 6,
            CognitiveBudget(body, BodyLaws()))
        self.assertEqual(
            result["future_opportunity_semantics"],
            "ONE_GENERIC_FUTURE_ONE_CELL_WATER_OPPORTUNITY_"
            "NOT_CURRENT_SOURCE_PERSISTENCE")
        self.assertTrue(result["future_availability_marginalized"])
        self.assertFalse(
            result["future_availability_simulated_as_extra_branch"])
        self.assertEqual(result["subjective_leaf_count"], 3)
        self.assertEqual(result["prior_expected_external_delta"], (0.,) * 5)

    def test_empty_map_uses_first_person_symmetric_water_probability(self):
        body = (20., 80., 80., 80., 80.)
        result = paid_water_one_future_opportunity_value(
            make_mind(), realistic_memory(), EXPLORE, ORDINARY, 6,
            CognitiveBudget(body, BodyLaws()))
        self.assertEqual(result["water_probability"], .25)
        self.assertEqual(
            result["future_water_opportunity_probability"], .25)

    def test_complete_forecast_covers_actual_work(self):
        body = (20., 80., 80., 80., 80.)
        result = paid_water_one_future_opportunity_value(
            make_mind(), realistic_memory(), EXPLORE, ORDINARY, 6,
            CognitiveBudget(body, BodyLaws()))
        for key in ("cycles", "simulated_steps", "memory_items", "replays"):
            self.assertLessEqual(
                result["work"][key],
                result["forecast_work_ceiling"][key])
        self.assertEqual(result["work_breakdown"]["total"], result["work"])
        self.assertFalse(result["world_access"])
        self.assertFalse(result["motor_command_authorized"])
        self.assertFalse(result["cost_is_physical_settlement_receipt"])

    def test_kernel_does_not_mutate_mind_or_memory(self):
        body = (20., 80., 80., 80., 80.)
        memory = realistic_memory()
        mind = make_mind()
        before_memory = tuple(
            (sample.key, sample.delta) for sample in memory._samples)
        before = {
            "effects": deepcopy(mind.effects.stats),
            "values": deepcopy(mind.values),
            "buffer": tuple(mind.buffer),
            "map": deepcopy(mind.map),
            "hist": deepcopy(mind.hist),
            "rng": mind.rng.getstate(),
            "budget_rng": mind._budget_rng.getstate(),
        }
        paid_water_one_future_opportunity_value(
            mind, memory, EXPLORE, ORDINARY, 6,
            CognitiveBudget(body, BodyLaws()))
        self.assertEqual(
            tuple((sample.key, sample.delta) for sample in memory._samples),
            before_memory)
        self.assertEqual(mind.effects.stats, before["effects"])
        self.assertEqual(mind.values, before["values"])
        self.assertEqual(tuple(mind.buffer), before["buffer"])
        self.assertEqual(mind.map, before["map"])
        self.assertEqual(mind.hist, before["hist"])
        self.assertEqual(mind.rng.getstate(), before["rng"])
        self.assertEqual(mind._budget_rng.getstate(), before["budget_rng"])

    def test_module_import_does_not_load_world_or_runtime(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.modules.water_future_opportunity; "
            "assert 'i3.modules.world' not in sys.modules; "
            "assert 'i3.runtime.life' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
