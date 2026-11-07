"""Three-leaf target prior: software only, no live policy."""
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.modules.body import BodyLaws, CognitiveBudget, CognitiveWork
from i3.modules.three_leaf_target_prior import (
    COMPOSE_WORK, paid_three_leaf_target_prior)

BODY = (80., 80., 20., 80., 80.)
THETA = (60., 60., 60., 60., 60.)
POWERS = (2., 2., 2., 2., 2.)
WEIGHTS = (1., 1., 1., 1., 1.)


def allowance(body=BODY):
    return CognitiveBudget(body, BodyLaws())


class ThreeLeafTargetPriorTests(unittest.TestCase):
    def test_newborn_water_target_is_exact_three_leaf_zero_mean_tree(self):
        result = paid_three_leaf_target_prior(
            {}, BODY, THETA, POWERS, WEIGHTS, "water", allowance())
        self.assertEqual(result["status"], "COMPLETE_THREE_LEAF_TARGET_PRIOR")
        self.assertEqual(result["leaf_count"], 3)
        self.assertEqual(
            tuple((x["leaf"], x["probability"]) for x in result["leaves"]),
            (("NO_TARGET_MODALITY", .75),
             ("TARGET_MODALITY_TRIAL_POSITIVE", .125),
             ("TARGET_MODALITY_TRIAL_NEGATIVE", .125)))
        self.assertEqual(result["target_probability"], .25)
        self.assertEqual(
            result["non_target_probability_breakdown"],
            {"NO_RESOURCE": .5, "TOKEN_MODALITY": .25})
        self.assertEqual(result["expected_external_delta"], (0.,) * 5)
        self.assertEqual(
            result["leaves"][1]["effect_delta"],
            (0., 0., 100., 0., 0.))
        self.assertEqual(
            result["leaves"][2]["effect_delta"],
            (0., 0., -100., 0., 0.))

    def test_target_swap_changes_probability_only_not_effect_direction(self):
        personal_map = {
            (0, 0): (True, ()),
            (1, 0): (True, ()),
            (2, 0): (False, ("tok0",)),
            (3, 0): (False, ()),
        }
        water = paid_three_leaf_target_prior(
            personal_map, BODY, THETA, POWERS, WEIGHTS,
            "water", allowance())
        token = paid_three_leaf_target_prior(
            personal_map, BODY, THETA, POWERS, WEIGHTS,
            "token", allowance())
        self.assertNotEqual(
            water["target_probability"], token["target_probability"])
        self.assertEqual(
            water["effect_direction"], token["effect_direction"])
        self.assertEqual(
            water["leaves"][1]["effect_delta"],
            token["leaves"][1]["effect_delta"])
        self.assertEqual(
            water["leaves"][2]["effect_delta"],
            token["leaves"][2]["effect_delta"])

    def test_non_target_mass_remains_explicit_and_normalized(self):
        personal_map = {
            (0, 0): (False, ("a",)),
            (1, 0): (False, ()),
        }
        result = paid_three_leaf_target_prior(
            personal_map, BODY, THETA, POWERS, WEIGHTS,
            "water", allowance())
        self.assertAlmostEqual(
            sum(result["non_target_probability_breakdown"].values()),
            1.0 - result["target_probability"])
        self.assertIn(
            "TOKEN_MODALITY",
            result["non_target_probability_breakdown"])
        self.assertEqual(
            result["aggregation_semantics"],
            "NON_TARGET_OBSERVATIONS_RETAIN_PROBABILITY_BUT_RECEIVE_NO_"
            "TARGET_SPECIFIC_INFORMATION_CREDIT")

    def test_token_renaming_and_position_relabeling_do_not_change_result(self):
        a = {
            (0, 0): (False, ("tok0",)),
            (1, 0): (True, ()),
            (2, 0): None,
        }
        b = {
            (99, 5): None,
            (-4, 2): (True, ()),
            (12, 8): (False, ("renamed",)),
        }
        ra = paid_three_leaf_target_prior(
            a, BODY, THETA, POWERS, WEIGHTS, "water", allowance())
        rb = paid_three_leaf_target_prior(
            b, BODY, THETA, POWERS, WEIGHTS, "water", allowance())
        for key in (
                "target_probability", "non_target_probability_breakdown",
                "leaves", "expected_external_delta", "modality_prior",
                "effect_direction", "work"):
            self.assertEqual(ra[key], rb[key])

    def test_flat_stake_creates_no_trial_leaves(self):
        body = (80., 80., 80., 80., 80.)
        result = paid_three_leaf_target_prior(
            {}, body, THETA, POWERS, WEIGHTS, "water", allowance(body))
        self.assertEqual(result["status"], "NO_STAKE_RELEVANT_UNCERTAINTY")
        self.assertEqual(result["leaves"], ())
        self.assertEqual(result["leaf_count"], 0)
        self.assertEqual(result["expected_external_delta"], (0.,) * 5)
        self.assertEqual(result["target_probability"], .25)
        self.assertEqual(
            result["effect_prior_status"], "NO_STAKE_RELEVANT_UNCERTAINTY")

    def test_invalid_target_fails_before_spending(self):
        b = allowance()
        with self.assertRaises(ValueError):
            paid_three_leaf_target_prior(
                {}, BODY, THETA, POWERS, WEIGHTS, "food", b)
        self.assertEqual(b.work, CognitiveWork())

    def test_body_mismatch_fails_before_spending(self):
        b = allowance()
        with self.assertRaises(ValueError):
            paid_three_leaf_target_prior(
                {}, (79., 80., 20., 80., 80.),
                THETA, POWERS, WEIGHTS, "water", b)
        self.assertEqual(b.work, CognitiveWork())

    def test_work_breakdown_contains_both_priors_and_composition(self):
        b = allowance()
        result = paid_three_leaf_target_prior(
            {}, BODY, THETA, POWERS, WEIGHTS, "water", b)
        self.assertEqual(
            result["work_breakdown"]["modality_prior"],
            {"cycles": 1, "simulated_steps": 0,
             "memory_items": 8, "replays": 0})
        self.assertEqual(
            result["work_breakdown"]["effect_prior"],
            {"cycles": 1, "simulated_steps": 0,
             "memory_items": 32, "replays": 0})
        self.assertEqual(
            result["work_breakdown"]["composition"],
            {"cycles": 1, "simulated_steps": 0,
             "memory_items": 18, "replays": 0})
        self.assertEqual(
            b.work,
            CognitiveWork(cycles=3, memory_items=58))
        self.assertEqual(COMPOSE_WORK, CognitiveWork(cycles=1, memory_items=18))
        self.assertFalse(result["cost_is_physical_settlement_receipt"])
        self.assertFalse(result["world_access"])
        self.assertFalse(result["action_input"])

    def test_probability_mass_and_expected_effect_close_for_skewed_map(self):
        personal_map = {
            (0, 0): (True, ()),
            (1, 0): (True, ("a",)),
            (2, 0): (False, ("b",)),
            (3, 0): (False, ("c",)),
            (4, 0): (False, ()),
        }
        for target in ("water", "token"):
            with self.subTest(target=target):
                result = paid_three_leaf_target_prior(
                    personal_map, BODY, THETA, POWERS, WEIGHTS,
                    target, allowance())
                self.assertAlmostEqual(
                    sum(x["probability"] for x in result["leaves"]), 1.0)
                for value in result["expected_external_delta"]:
                    self.assertAlmostEqual(value, 0.0)
                self.assertLessEqual(result["leaf_count"], 3)

    def test_module_import_does_not_load_mind_world_or_runtime(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.modules.three_leaf_target_prior; "
            "assert 'i3.modules.mind' not in sys.modules; "
            "assert 'i3.modules.world' not in sys.modules; "
            "assert 'i3.runtime.life' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
