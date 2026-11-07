"""Zero-mean unsupported-effect prior: software only, no live policy."""
from inspect import signature
from math import sqrt
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.modules.body import (
    BodyLaws, CognitiveBudget, CognitiveFundingError, CognitiveWork)
from i3.modules.unknown_effect_prior import (
    DELTA_RADIUS, PRIOR_WORK, paid_zero_mean_stake_prior)

THETA = (60., 60., 60., 60., 60.)
POWERS = (2., 2., 2., 2., 2.)
WEIGHTS = (1., 1., 1., 1., 1.)


def budget(body):
    return CognitiveBudget(body, BodyLaws())


class ZeroMeanStakePriorTests(unittest.TestCase):
    def test_one_distressed_channel_produces_exact_opposite_max_radius_pair(self):
        body = (80., 80., 20., 80., 80.)
        b = budget(body)
        result = paid_zero_mean_stake_prior(
            body, THETA, POWERS, WEIGHTS, b)
        self.assertEqual(result["status"], "COMPLETE_ZERO_MEAN_STAKE_PRIOR")
        self.assertEqual(len(result["outcomes"]), 2)
        a, z = result["outcomes"]
        self.assertEqual(a.probability, .5)
        self.assertEqual(z.probability, .5)
        self.assertEqual(a.signal, z.signal)
        self.assertEqual(a.probe_delta, (0., 0., 100., 0., 0.))
        self.assertEqual(z.probe_delta, (0., 0., -100., 0., 0.))
        self.assertEqual(result["expected_external_delta"], (0., 0., 0., 0., 0.))
        self.assertEqual(b.work, PRIOR_WORK)

    def test_multiple_distressed_channels_follow_analytic_distress_gradient(self):
        body = (80., 20., 30., 80., 80.)
        weights = (1., 1.5, 2.0, 1., 1.)
        result = paid_zero_mean_stake_prior(
            body, THETA, POWERS, weights, budget(body))
        direction = result["distress_direction"]
        gf = 1.5 * 2.0 / 60.0 * ((60.0 - 20.0) / 60.0)
        gw = 2.0 * 2.0 / 60.0 * ((60.0 - 30.0) / 60.0)
        norm = sqrt(gf * gf + gw * gw)
        self.assertAlmostEqual(direction[1], gf / norm)
        self.assertAlmostEqual(direction[2], gw / norm)
        self.assertEqual(direction[0], 0.)
        self.assertEqual(direction[3], 0.)
        self.assertEqual(direction[4], 0.)
        plus = result["outcomes"][0].probe_delta
        minus = result["outcomes"][1].probe_delta
        self.assertAlmostEqual(sqrt(sum(x * x for x in plus)), DELTA_RADIUS)
        for p, m in zip(plus, minus):
            self.assertAlmostEqual(p, -m)
        for x in result["expected_external_delta"]:
            self.assertAlmostEqual(x, 0.)

    def test_locally_flat_distress_returns_no_motive_but_still_pays_computation(self):
        body = (80., 80., 80., 80., 80.)
        b = budget(body)
        receipt = {}
        result = paid_zero_mean_stake_prior(
            body, THETA, POWERS, WEIGHTS, b, work_receipt=receipt)
        self.assertEqual(result["status"], "NO_STAKE_RELEVANT_UNCERTAINTY")
        self.assertEqual(result["outcomes"], ())
        self.assertEqual(result["distress_direction"], (0.,) * 5)
        self.assertEqual(result["expected_external_delta"], (0.,) * 5)
        self.assertEqual(b.work, PRIOR_WORK)
        self.assertEqual(receipt["work"], {
            "cycles": 1, "simulated_steps": 0,
            "memory_items": 32, "replays": 0})

    def test_prior_api_has_no_action_token_map_or_world_input(self):
        names = tuple(signature(paid_zero_mean_stake_prior).parameters)
        for forbidden in ("action", "token", "map", "world", "resource"):
            self.assertNotIn(forbidden, names)

    def test_same_body_and_stakes_are_identical_without_any_external_identity(self):
        body = (70., 25., 15., 80., 50.)
        a = paid_zero_mean_stake_prior(
            body, THETA, POWERS, WEIGHTS, budget(body))
        b = paid_zero_mean_stake_prior(
            body, THETA, POWERS, WEIGHTS, budget(body))
        self.assertEqual(a, b)

    def test_invalid_inputs_and_dead_body_fail_before_spending(self):
        body = (80., 80., 20., 80., 80.)
        cases = [
            ((80., 80.), THETA, POWERS, WEIGHTS),
            (body, (0., 60., 60., 60., 60.), POWERS, WEIGHTS),
            (body, THETA, (.5, 2., 2., 2., 2.), WEIGHTS),
            (body, THETA, POWERS, (1., 1., 0., 1., 1.)),
        ]
        for bdy, th, p, w in cases:
            allowance = budget(body)
            with self.subTest(case=(bdy, th, p, w)), self.assertRaises(ValueError):
                paid_zero_mean_stake_prior(bdy, th, p, w, allowance)
            self.assertEqual(allowance.work, CognitiveWork())

        dead = (80., 80., 0., 80., 80.)
        allowance = budget(dead)
        with self.assertRaises(ValueError):
            paid_zero_mean_stake_prior(
                dead, THETA, POWERS, WEIGHTS, allowance)
        self.assertEqual(allowance.work, CognitiveWork())

    def test_unfunded_prior_returns_no_partial_hypothesis(self):
        body = (.01, 50., 20., 80., .01)
        allowance = budget(body)
        with self.assertRaises(CognitiveFundingError):
            paid_zero_mean_stake_prior(
                body, THETA, POWERS, WEIGHTS, allowance)
        self.assertEqual(allowance.work, CognitiveWork())

    def test_module_import_does_not_load_mind_world_or_runtime(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.modules.unknown_effect_prior; "
            "assert 'i3.modules.mind' not in sys.modules; "
            "assert 'i3.modules.world' not in sys.modules; "
            "assert 'i3.runtime.life' not in sys.modules"
        ], check=True)

    def test_work_contract_is_fixed_and_not_a_settlement_receipt(self):
        body = (80., 40., 20., 80., 80.)
        result = paid_zero_mean_stake_prior(
            body, THETA, POWERS, WEIGHTS, budget(body))
        self.assertEqual(result["work"], {
            "cycles": 1, "simulated_steps": 0,
            "memory_items": 32, "replays": 0})
        self.assertFalse(result["cost_is_physical_settlement_receipt"])
        self.assertFalse(result["action_input"])
        self.assertFalse(result["token_input"])
        self.assertFalse(result["world_access"])


if __name__ == "__main__":
    unittest.main()
