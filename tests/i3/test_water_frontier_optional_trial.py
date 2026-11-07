"""Water-frontier optional trial value: software only, no live policy."""
from copy import deepcopy
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.modules.body import BodyLaws, CognitiveBudget, CognitiveWork
from i3.modules.genome import midpoint
from i3.modules.mind import Mind
from i3.modules.water_frontier_optional_trial import (
    paid_water_frontier_optional_trial_value)

EXPLORE = (("se_deplacer",),)
COMMON = (
    ("ordinary-wait", (("attendre",),)),
)
POST = (
    ("post-wait", (("attendre",),)),
    ("post-sleep", (("dormir",),)),
)


def make_mind(body, *, sleep_energy=3.0):
    mind = Mind(midpoint(), 43)
    mind.map = {}
    mind.effects.observe(
        ("se_deplacer",), (-2., -.2, -.4, 0., 0.))
    mind.effects.observe(
        ("attendre",), (-.35, -.2, -.4, .2, 0.))
    mind.effects.observe(
        ("dormir",), (sleep_energy, -.35, -.4, 0., 4.))
    mind._drift = mind.drift()
    return mind


class WaterFrontierOptionalTrialTests(unittest.TestCase):
    def test_zero_mean_trial_can_be_selected_without_automatic_sampling_rule(self):
        body = (20., 80., 80., 80., 80.)
        mind = make_mind(body, sleep_energy=80.0)
        result = paid_water_frontier_optional_trial_value(
            mind, EXPLORE, COMMON, POST, 6,
            CognitiveBudget(body, BodyLaws()))
        self.assertEqual(
            result["status"],
            "COMPLETE_WATER_FRONTIER_OPTIONAL_TRIAL_ESTIMATE_NOT_POLICY")
        self.assertEqual(result["leaf_count"], 3)
        self.assertEqual(result["prior_expected_external_delta"], (0.,) * 5)
        self.assertGreater(result["trial_information_value"], 0.)
        self.assertIn(
            "TRIAL", result["target_node_best_choices"],
            msg={k: result[k] for k in (
                "ordinary_frontier_value", "trial_frozen_value",
                "trial_informed_value", "trial_information_value",
                "trial_advantage", "water_probability",
                "frontier_expected_value", "work")})
        self.assertGreaterEqual(result["water_revelation_advantage"], 0.)

    def test_risky_unknown_drink_can_be_declined_after_water_is_revealed(self):
        body = (80., 80., 40., 80., 80.)
        mind = make_mind(body)
        result = paid_water_frontier_optional_trial_value(
            mind, EXPLORE, COMMON, POST, 6,
            CognitiveBudget(body, BodyLaws()))
        self.assertEqual(
            result["target_node_best_choices"], ("DECLINE_TRIAL",))
        self.assertLess(result["trial_advantage"], 0.)
        self.assertEqual(result["water_revelation_advantage"], 0.0)

    def test_trial_information_and_trial_advantage_remain_distinct(self):
        body = (20., 80., 80., 80., 80.)
        result = paid_water_frontier_optional_trial_value(
            make_mind(body), EXPLORE, COMMON, POST, 6,
            CognitiveBudget(body, BodyLaws()))
        self.assertAlmostEqual(
            result["trial_information_value"],
            result["trial_informed_value"] - result["trial_frozen_value"])
        self.assertAlmostEqual(
            result["trial_advantage"],
            result["trial_informed_value"] - result["ordinary_frontier_value"])
        expected = (
            (1.0 - result["water_probability"])
            * result["ordinary_frontier_value"]
            + result["water_probability"]
            * max(result["ordinary_frontier_value"],
                  result["trial_informed_value"]))
        self.assertAlmostEqual(result["frontier_expected_value"], expected)

    def test_water_probability_comes_from_first_person_map_only(self):
        body = (20., 80., 80., 80., 80.)
        mind = make_mind(body)
        mind.map = {
            (0, 0): (True, ()),
            (1, 0): (False, ()),
        }
        result = paid_water_frontier_optional_trial_value(
            mind, EXPLORE, COMMON, POST, 6,
            CognitiveBudget(body, BodyLaws()))
        self.assertAlmostEqual(result["water_probability"], 1. / 3.)
        self.assertEqual(
            result["non_water_probability_breakdown"],
            {"NO_RESOURCE": .5, "TOKEN_MODALITY": 1. / 6.})

    def test_common_continuation_cannot_smuggle_unsupported_drink(self):
        body = (20., 80., 80., 80., 80.)
        b = CognitiveBudget(body, BodyLaws())
        with self.assertRaisesRegex(ValueError, "unsupported drink"):
            paid_water_frontier_optional_trial_value(
                make_mind(body), EXPLORE,
                (("bad", (("boire",),)),), POST, 6, b)
        self.assertEqual(b.work, CognitiveWork())

    def test_explorer_prefix_is_existing_move_only_repertoire(self):
        body = (20., 80., 80., 80., 80.)
        b = CognitiveBudget(body, BodyLaws())
        with self.assertRaisesRegex(ValueError, "moves only"):
            paid_water_frontier_optional_trial_value(
                make_mind(body), (("attendre",),),
                COMMON, POST, 6, b)
        self.assertEqual(b.work, CognitiveWork())

    def test_flat_stake_has_no_trial_matrix_and_keeps_ordinary_value(self):
        body = (80., 80., 80., 80., 80.)
        b = CognitiveBudget(body, BodyLaws())
        result = paid_water_frontier_optional_trial_value(
            make_mind(body), EXPLORE, COMMON, POST, 6, b)
        self.assertEqual(result["status"], "NO_STAKE_RELEVANT_UNCERTAINTY")
        self.assertEqual(result["leaf_count"], 0)
        self.assertIsNone(result["trial_frozen_value"])
        self.assertIsNone(result["trial_informed_value"])
        self.assertEqual(result["trial_information_value"], 0.0)
        self.assertEqual(
            result["target_node_best_choices"], ("DECLINE_TRIAL",))
        self.assertEqual(
            result["frontier_expected_value"],
            result["ordinary_frontier_value"])
        self.assertEqual(result["water_revelation_advantage"], 0.0)

    def test_complete_forecast_covers_actual_work(self):
        body = (20., 80., 80., 80., 80.)
        result = paid_water_frontier_optional_trial_value(
            make_mind(body), EXPLORE, COMMON, POST, 6,
            CognitiveBudget(body, BodyLaws()))
        for key in ("cycles", "simulated_steps", "memory_items", "replays"):
            self.assertLessEqual(
                result["work"][key],
                result["forecast_work_ceiling"][key])
        self.assertEqual(
            result["work_breakdown"]["total"], result["work"])
        self.assertFalse(result["cost_is_physical_settlement_receipt"])
        self.assertFalse(result["motor_command_authorized"])
        self.assertFalse(result["world_access"])
        self.assertTrue(result["trial_is_optional"])

    def test_real_learned_state_and_rng_are_unchanged(self):
        body = (20., 80., 80., 80., 80.)
        mind = make_mind(body)
        before = {
            "effects": deepcopy(mind.effects.stats),
            "values": deepcopy(mind.values),
            "buffer": tuple(mind.buffer),
            "map": deepcopy(mind.map),
            "hist": deepcopy(mind.hist),
            "rng": mind.rng.getstate(),
            "budget_rng": mind._budget_rng.getstate(),
        }
        paid_water_frontier_optional_trial_value(
            mind, EXPLORE, COMMON, POST, 6,
            CognitiveBudget(body, BodyLaws()))
        after = {
            "effects": mind.effects.stats,
            "values": mind.values,
            "buffer": tuple(mind.buffer),
            "map": mind.map,
            "hist": mind.hist,
            "rng": mind.rng.getstate(),
            "budget_rng": mind._budget_rng.getstate(),
        }
        self.assertEqual(after, before)

    def test_module_import_does_not_load_world_or_runtime(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.modules.water_frontier_optional_trial; "
            "assert 'i3.modules.world' not in sys.modules; "
            "assert 'i3.runtime.life' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
