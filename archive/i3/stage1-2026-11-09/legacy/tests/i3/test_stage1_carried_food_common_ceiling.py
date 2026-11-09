"""Common-ceiling carried-food audit: software only, no policy."""
from copy import deepcopy
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab.stage1_carried_food_common_ceiling import (
    audit_carried_food_common_ceiling)
from i3.modules.body import BodyLaws, CognitiveBudget, CognitiveWork
from i3.modules.genome import midpoint
from i3.modules.reference_memory_mind import ReferenceBranchMemoryMind

BASE = (50., 50., 50., 50., 50.)
SAFE = (0., 30., 0., 0., 0.)
TOXIC = (0., 30., 0., -35., 0.)


def remember(memory, key, delta):
    after = tuple(a + b for a, b in zip(BASE, delta))
    memory.observe(
        key, BASE, CognitiveWork(),
        CognitiveBudget(after, BodyLaws()))


def rich_mind(seed=149):
    mind = ReferenceBranchMemoryMind(midpoint(), seed)
    mind.effects.observe(("attendre",), (-.35, -.2, -.4, .2, 0.))
    mind.effects.observe(("dormir",), (3., -.35, -.4, 0., 4.))
    for key, delta in (
        (("manger", "known-safe"), SAFE),
        (("manger", "known-toxic"), TOXIC),
    ):
        mind.effects.observe(key, delta)
        remember(mind.branch_memory, key, delta)
    mind.tokens["known-here"] = "known-safe"
    mind.external["known-safe"] = "known-here"
    mind.tokens["known-neighbor"] = "known-toxic"
    mind.external["known-toxic"] = "known-neighbor"
    mind.effects.observe(("boire",), (0., 0., 35., 0., 0.))
    mind.effects.observe(("se_deplacer",), (-2., -.2, -.4, 0., 0.))
    mind.effects.observe(("collecter", "known-safe"), (-1., 0., 0., 0., 0.))
    mind.effects.observe(("collecter", "known-toxic"), (-1., 0., 0., 0., 0.))
    return mind


def rich_cap(body):
    return {
        "body": tuple(body),
        "inventory": (("mystery", 2),),
        "here": (True, ("known-here",)),
        "neighbors": (
            (False, ("known-neighbor",)),
            (False, ()),
            (False, ()),
            (False, ()),
        ),
    }


class CarriedFoodCommonCeilingTests(unittest.TestCase):
    def test_rich_grid_characterizes_cost_comparable_winner_boundary(self):
        rows = []
        mind = rich_mind()
        for food in (5., 25., 45.):
            for water in (5., 25., 45.):
                for integrity in (5., 25., 45.):
                    rows.append(audit_carried_food_common_ceiling(
                        mind,
                        rich_cap((60., food, water, integrity, 80.)),
                        BodyLaws(), "mystery"))

        self.assertEqual(len(rows), 27)
        allowed = {
            "COMPLETE_COMMON_CEILING_RAW_SCORE_AUDIT",
            "COMMON_CEILING_UNFUNDED",
        }
        self.assertTrue(all(row["status"] in allowed for row in rows))
        complete = [
            row for row in rows
            if row["status"] == "COMPLETE_COMMON_CEILING_RAW_SCORE_AUDIT"
        ]
        unfunded = [
            row for row in rows
            if row["status"] == "COMMON_CEILING_UNFUNDED"
        ]

        for row in complete:
            self.assertEqual(
                row["comparison_status"],
                "COST_COMPARABLE_FORECAST_BODY_NOT_POLICY")
            self.assertFalse(row["curiosity_prudence_included"])
            self.assertFalse(row["competition_replayed"])
            self.assertFalse(row["control_replayed"])
            self.assertFalse(row["world_step_executed"])
            for key in ("cycles", "simulated_steps", "memory_items", "replays"):
                self.assertLessEqual(
                    row["actual_work"][key],
                    row["common_forecast_work_ceiling"][key])

        stats = {
            "evaluated": len(rows),
            "complete": len(complete),
            "unfunded": len(unfunded),
            "positive_information": sum(
                row["candidate_base"]["information_value"] > 1e-12
                for row in complete),
            "meal_score_improved": sum(
                row["candidate_base"]["meal_minus_reference_meal"] > 1e-12
                for row in complete),
            "meal_raw_top_before": sum(
                row["reference_base"]["meal_raw_top"] for row in complete),
            "meal_raw_top_after": sum(
                row["candidate_base"]["meal_raw_top"] for row in complete),
            "winner_set_changed": sum(
                row["candidate_base"]["winner_set_changed"] for row in complete),
            "max_information_value": (
                max(row["candidate_base"]["information_value"] for row in complete)
                if complete else None),
        }
        print("CARRIED_FOOD_COMMON_CEILING_AUDIT", stats)
        # No positive behavioral outcome is required. An entirely unfunded
        # panel is an admissible cost result, not a test failure.

    def test_original_mind_is_unchanged(self):
        mind = rich_mind()
        before = {
            "tokens": deepcopy(mind.tokens),
            "external": deepcopy(mind.external),
            "effects": deepcopy(mind.effects.stats),
            "values": deepcopy(mind.values),
            "buffer": tuple(mind.buffer),
            "branch": tuple(
                (sample.key, sample.delta)
                for sample in mind.branch_memory._samples),
            "map": deepcopy(mind.map),
            "hist": deepcopy(mind.hist),
            "acc": deepcopy(mind.acc),
            "intention": mind.intention,
            "rng": mind.rng.getstate(),
            "budget_rng": mind._budget_rng.getstate(),
        }
        audit_carried_food_common_ceiling(
            mind, rich_cap((100., 25., 25., 50., 100.)),
            BodyLaws(), "mystery")
        after = {
            "tokens": mind.tokens,
            "external": mind.external,
            "effects": mind.effects.stats,
            "values": mind.values,
            "buffer": tuple(mind.buffer),
            "branch": tuple(
                (sample.key, sample.delta)
                for sample in mind.branch_memory._samples),
            "map": mind.map,
            "hist": mind.hist,
            "acc": mind.acc,
            "intention": mind.intention,
            "rng": mind.rng.getstate(),
            "budget_rng": mind._budget_rng.getstate(),
        }
        self.assertEqual(after, before)

    def test_invalid_inventory_fails_before_audit(self):
        bad = rich_cap((80., 25., 25., 50., 80.))
        bad["inventory"] = ()
        with self.assertRaises(ValueError):
            audit_carried_food_common_ceiling(
                rich_mind(), bad, BodyLaws(), "mystery")

    def test_module_import_does_not_load_runtime_life(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.lab.stage1_carried_food_common_ceiling; "
            "assert 'i3.runtime.life' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
