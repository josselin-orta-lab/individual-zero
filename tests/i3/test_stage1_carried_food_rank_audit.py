"""Software-only raw-rank audit for carried-food Stage-1 value."""
from copy import deepcopy
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab.stage1_carried_food_rank_audit import audit_carried_food_raw_rank
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


def mind_with_mixed_food_history(seed=127):
    mind = ReferenceBranchMemoryMind(midpoint(), seed)
    mind.effects.observe(("attendre",), (-.35, -.2, -.4, .2, 0.))
    mind.effects.observe(("dormir",), (3., -.35, -.4, 0., 4.))
    for key, delta in (
        (("manger", "known-safe"), SAFE),
        (("manger", "known-toxic"), TOXIC),
    ):
        mind.effects.observe(key, delta)
        remember(mind.branch_memory, key, delta)
    return mind


def mind_with_harmful_food_history(seed=127):
    mind = ReferenceBranchMemoryMind(midpoint(), seed)
    mind.effects.observe(("attendre",), (-.35, -.2, -.4, .2, 0.))
    mind.effects.observe(("dormir",), (3., -.35, -.4, 0., 4.))
    for key, delta in (
        (("manger", "known-a"), (0., 5., 0., -20., 0.)),
        (("manger", "known-b"), (0., 10., 0., -30., 0.)),
    ):
        mind.effects.observe(key, delta)
        remember(mind.branch_memory, key, delta)
    return mind


def cap(body, token="mystery", count=2):
    return {
        "body": tuple(body),
        "inventory": ((token, count),),
        "here": (False, ()),
        "neighbors": (None, None, None, None),
    }


class CarriedFoodRawRankAuditTests(unittest.TestCase):
    def test_mixed_history_grid_characterizes_rank_shift_without_policy_change(self):
        rows = []
        mind = mind_with_mixed_food_history()
        for energy in (35., 60., 85.):
            for food in (5., 20., 40.):
                for integrity in (20., 50., 80.):
                    body = (energy, food, 80., integrity, 80.)
                    result = audit_carried_food_raw_rank(
                        mind, cap(body), BodyLaws(), "mystery")
                    rows.append(result)

        complete = [
            row for row in rows
            if row["status"] == "COMPLETE_DESCRIPTIVE_RAW_RANK_AUDIT"
        ]
        self.assertTrue(complete)
        self.assertTrue(all(
            row["comparison_status"] == "DESCRIPTIVE_NOT_COST_MATCHED"
            for row in complete))
        self.assertTrue(all(
            row["cost_boundary"]["causal_or_cost_matched_rank_claim"] is False
            for row in complete))
        self.assertTrue(all(
            row["competition_replayed"] is False
            and row["control_replayed"] is False
            and row["world_step_executed"] is False
            for row in complete))

        stats = {
            "evaluated": len(rows),
            "complete": len(complete),
            "positive_information": sum(
                row["candidate"]["information_value"] > 1e-12
                for row in complete),
            "candidate_above_reference_meal_base": sum(
                row["placement_vs_reference_base"][
                    "candidate_minus_reference_meal"] > 1e-12
                for row in complete),
            "candidate_above_reference_meal_total": sum(
                row["placement_vs_reference_total"][
                    "candidate_minus_reference_meal"] > 1e-12
                for row in complete),
            "base_rank_improved": sum(
                row["placement_vs_reference_base"][
                    "candidate_improves_reference_meal_rank"]
                for row in complete),
            "total_rank_improved": sum(
                row["placement_vs_reference_total"][
                    "candidate_improves_reference_meal_rank"]
                for row in complete),
            "candidate_raw_top_base": sum(
                row["placement_vs_reference_base"]["candidate_raw_top"]
                for row in complete),
            "candidate_raw_top_total": sum(
                row["placement_vs_reference_total"]["candidate_raw_top"]
                for row in complete),
            "reference_chose_meal": sum(
                row["reference"]["chosen_option"] == row["meal_option"]
                for row in complete),
            "max_information_value": max(
                row["candidate"]["information_value"] for row in complete),
        }
        print("CARRIED_FOOD_RAW_RANK_AUDIT", stats)
        self.assertGreater(
            stats["positive_information"], 0,
            "mixed food history never produced information")

    def test_one_unit_has_zero_information_in_actual_reference_context(self):
        result = audit_carried_food_raw_rank(
            mind_with_mixed_food_history(),
            cap((80., 5., 80., 80., 80.), count=1),
            BodyLaws(), "mystery")
        self.assertEqual(
            result["status"], "COMPLETE_DESCRIPTIVE_RAW_RANK_AUDIT")
        self.assertEqual(result["candidate"]["information_value"], 0.0)
        self.assertEqual(result["candidate"]["future_repeat_units_modelled"], 0)

    def test_harmful_history_does_not_manufacture_information(self):
        result = audit_carried_food_raw_rank(
            mind_with_harmful_food_history(),
            cap((80., 80., 80., 40., 80.)),
            BodyLaws(), "mystery")
        self.assertEqual(
            result["status"], "COMPLETE_DESCRIPTIVE_RAW_RANK_AUDIT")
        self.assertEqual(result["candidate"]["information_value"], 0.0)

    def test_external_token_renaming_is_internalized_identically(self):
        body = (80., 5., 80., 80., 80.)
        a = audit_carried_food_raw_rank(
            mind_with_mixed_food_history(),
            cap(body, token="mystery"), BodyLaws(), "mystery")
        b = audit_carried_food_raw_rank(
            mind_with_mixed_food_history(),
            cap(body, token="renamed-external"), BodyLaws(),
            "renamed-external")
        self.assertEqual(a["meal_option"], "manger:tok0")
        self.assertEqual(b["meal_option"], "manger:tok0")
        for key in (
                "candidate", "placement_vs_reference_base",
                "placement_vs_reference_total"):
            self.assertEqual(a[key], b[key])

    def test_original_mind_is_not_mutated_by_audit(self):
        mind = mind_with_mixed_food_history()
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
        result = audit_carried_food_raw_rank(
            mind, cap((80., 5., 80., 80., 80.)),
            BodyLaws(), "mystery")
        self.assertEqual(
            result["status"], "COMPLETE_DESCRIPTIVE_RAW_RANK_AUDIT")
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

    def test_missing_branch_support_is_reported_not_invented(self):
        mind = ReferenceBranchMemoryMind(midpoint(), 127)
        mind.effects.observe(("attendre",), (-.35, -.2, -.4, .2, 0.))
        mind.effects.observe(("dormir",), (3., -.35, -.4, 0., 4.))
        result = audit_carried_food_raw_rank(
            mind, cap((80., 5., 80., 80., 80.)),
            BodyLaws(), "mystery")
        self.assertEqual(result["status"], "CANDIDATE_NO_PERSONAL_SUPPORT")
        self.assertEqual(result["comparison_status"], "NOT_EVALUATED")

    def test_invalid_inventory_fails_before_audit(self):
        mind = mind_with_mixed_food_history()
        bad = cap((80., 5., 80., 80., 80.))
        bad["inventory"] = ()
        with self.assertRaises(ValueError):
            audit_carried_food_raw_rank(
                mind, bad, BodyLaws(), "mystery")

    def test_module_import_does_not_load_world_or_runtime(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.lab.stage1_carried_food_rank_audit; "
            "assert 'i3.modules.world' not in sys.modules; "
            "assert 'i3.runtime.life' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
