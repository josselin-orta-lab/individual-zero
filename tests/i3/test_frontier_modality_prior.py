"""Frontier modality prior: software only, no live policy."""
from inspect import signature
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.modules.body import BodyLaws, CognitiveBudget, CognitiveWork
from i3.modules.frontier_modality_prior import paid_frontier_modality_prior

BODY = (80., 80., 80., 80., 80.)


def allowance(body=BODY):
    return CognitiveBudget(body, BodyLaws())


class FrontierModalityPriorTests(unittest.TestCase):
    def test_empty_personal_map_is_symmetric_without_actionable_value(self):
        b = allowance()
        result = paid_frontier_modality_prior({}, b)
        self.assertEqual(result["resource_base_rate"], .5)
        self.assertEqual(result["conditional_modality"], {
            "water": .5, "token": .5})
        self.assertEqual(
            tuple((x["signal"], x["probability"]) for x in result["branches"]),
            (("NO_RESOURCE", .5),
             ("WATER_MODALITY", .25),
             ("TOKEN_MODALITY", .25)))
        self.assertEqual(
            b.work, CognitiveWork(cycles=1, memory_items=8))
        self.assertFalse(result["body_input"])
        self.assertFalse(result["action_effect_input"])

    def test_resource_rate_is_exact_existing_p13_laplace_formula(self):
        personal_map = {
            (0, 0): (True, ()),
            (1, 0): (False, ()),
        }
        result = paid_frontier_modality_prior(
            personal_map, allowance())
        self.assertEqual(result["resource_base_rate"], .5)
        self.assertEqual(result["conditional_modality"], {
            "water": 2. / 3., "token": 1. / 3.})
        self.assertAlmostEqual(
            result["branches"][1]["probability"], 1. / 3.)
        self.assertAlmostEqual(
            result["branches"][2]["probability"], 1. / 6.)

    def test_mixed_cell_contributes_one_incidence_to_each_modality(self):
        result = paid_frontier_modality_prior(
            {(0, 0): (True, ("tok0",))}, allowance())
        self.assertAlmostEqual(result["resource_base_rate"], 2. / 3.)
        self.assertEqual(result["conditional_modality"], {
            "water": .5, "token": .5})
        self.assertEqual(result["personal_counts"], {
            "seen_passable_cells": 1,
            "resource_cells": 1,
            "water_incidences": 1,
            "token_incidences": 1})
        self.assertEqual(
            result["mixed_cell_semantics"],
            "ONE_INCIDENCE_PER_MODALITY_THEN_NORMALIZED_NO_SEPARATE_MIXED_BRANCH")

    def test_token_renaming_and_position_relabeling_do_not_change_probabilities(self):
        a = {
            (0, 0): (False, ("tok0",)),
            (1, 0): (True, ()),
            (2, 0): (False, ()),
            (3, 0): None,
        }
        b = {
            (99, -5): None,
            (4, 7): (False, ()),
            (-2, 8): (True, ()),
            (12, 3): (False, ("completely-renamed",)),
        }
        ra = paid_frontier_modality_prior(a, allowance())
        rb = paid_frontier_modality_prior(b, allowance())
        for key in (
                "resource_base_rate", "conditional_modality",
                "personal_counts", "branches", "work"):
            self.assertEqual(ra[key], rb[key])
        self.assertFalse(ra["token_identity_input"])

    def test_edges_do_not_enter_probability_counts_but_are_paid_to_scan(self):
        personal_map = {
            (0, 0): (False, ()),
            (1, 0): None,
            (-1, 0): None,
        }
        result = paid_frontier_modality_prior(
            personal_map, allowance())
        self.assertEqual(result["personal_counts"]["seen_passable_cells"], 1)
        self.assertEqual(
            result["work"],
            {"cycles": 1, "simulated_steps": 0,
             "memory_items": 14, "replays": 0})

    def test_api_has_no_body_action_effect_or_world_input(self):
        params = tuple(signature(paid_frontier_modality_prior).parameters)
        self.assertEqual(params, (
            "personal_map", "budget", "work_receipt"))
        for forbidden in (
                "body", "action", "effect", "token", "world",
                "water_need", "food_need", "utility"):
            self.assertNotIn(forbidden, params)

    def test_dead_body_fails_before_map_scan(self):
        b = allowance((80., 0., 80., 80., 80.))
        with self.assertRaises(ValueError):
            paid_frontier_modality_prior({}, b)
        self.assertEqual(b.work, CognitiveWork())

    def test_malformed_cell_is_rejected_after_paid_first_person_scan(self):
        b = allowance()
        with self.assertRaises(ValueError):
            paid_frontier_modality_prior(
                {(0, 0): ("water", ())}, b)
        self.assertEqual(
            b.work, CognitiveWork(cycles=1, memory_items=10))

    def test_receipt_matches_paid_work_and_is_not_settlement(self):
        receipt = {}
        result = paid_frontier_modality_prior(
            {(0, 0): (True, ())}, allowance(),
            work_receipt=receipt)
        self.assertEqual(receipt["work"], result["work"])
        self.assertEqual(
            receipt["status"], "COMPLETE_FIRST_PERSON_MODALITY_PRIOR")
        self.assertFalse(result["cost_is_physical_settlement_receipt"])
        self.assertFalse(result["world_access"])

    def test_module_import_does_not_load_mind_world_or_runtime(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.modules.frontier_modality_prior; "
            "assert 'i3.modules.mind' not in sys.modules; "
            "assert 'i3.modules.world' not in sys.modules; "
            "assert 'i3.runtime.life' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
