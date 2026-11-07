"""Observed-effect counterfactual view: software only, no live policy."""
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
from i3.modules.observed_effect_view import (
    VIEW_WORK, paid_simulate_after_observed_effect)

BODY = (80., 50., 30., 80., 80.)


def make_mind(*, observer=False):
    mind = Mind(
        midpoint(), 17,
        observer_decision_diagnostics=observer)
    mind.effects.observe(("attendre",), (0., -.2, -.4, .2, 0.))
    mind.effects.observe(("boire",), (0., 0., 8., 0., 0.))
    mind.effects.observe(("manger", "tok0"), (0., 7., 0., -1., 0.))
    mind.effects.observe(("manger", "tok1"), (0., 2., 0., -4., 0.))
    mind._drift = mind.drift()
    return mind


class ObservedEffectViewTests(unittest.TestCase):
    def test_exact_repeat_action_reads_observed_effect_with_zero_uncertainty(self):
        mind = make_mind(observer=True)
        result = paid_simulate_after_observed_effect(
            mind, BODY, (("boire",),), 4,
            ("boire",), (0., 0., 60., 0., 0.),
            CognitiveBudget(BODY, BodyLaws()))
        self.assertEqual(
            result["first_forecast"],
            {"action_key": ("boire",),
             "delta": (0., 0., 60., 0., 0.),
             "uncertainty": 0.0})
        self.assertEqual(result["max_uncertainty"], 0.0)

    def test_candidate_f_preserves_exact_observed_effect_override(self):
        mind = make_mind(observer=True)
        mind.simulation_mode = "candidate_f"
        mind.projection_accounting = "event_local_quadratic4"

        positive = paid_simulate_after_observed_effect(
            mind, BODY, (("boire",),), 4,
            ("boire",), (0., 0., 60., 0., 0.),
            CognitiveBudget(BODY, BodyLaws()))
        negative = paid_simulate_after_observed_effect(
            mind, BODY, (("boire",),), 4,
            ("boire",), (0., 0., -20., 0., 0.),
            CognitiveBudget(BODY, BodyLaws()))

        self.assertEqual(
            positive["first_forecast"],
            {"action_key": ("boire",),
             "delta": (0., 0., 60., 0., 0.),
             "uncertainty": 0.0})
        self.assertEqual(
            negative["first_forecast"],
            {"action_key": ("boire",),
             "delta": (0., 0., -20., 0., 0.),
             "uncertainty": 0.0})
        self.assertNotAlmostEqual(
            positive["value"], negative["value"], delta=1e-12)
        self.assertEqual(positive["max_uncertainty"], 0.0)
        self.assertEqual(negative["max_uncertainty"], 0.0)

    def test_candidate_f_proxy_does_not_mutate_owner_state(self):
        mind = make_mind(observer=True)
        mind.simulation_mode = "candidate_f"
        mind.projection_accounting = "event_local_quadratic4"
        before = {
            "effects": deepcopy(mind.effects.stats),
            "values": deepcopy(mind.values),
            "buffer": tuple(mind.buffer),
            "map": deepcopy(mind.map),
            "hist": deepcopy(mind.hist),
            "rng": mind.rng.getstate(),
            "budget_rng": mind._budget_rng.getstate(),
            "observer": deepcopy(getattr(
                mind, "_observer_first_forecast", None)),
        }
        paid_simulate_after_observed_effect(
            mind, BODY, (("boire",), ("attendre",)), 4,
            ("boire",), (0., 0., 60., 0., 0.),
            CognitiveBudget(BODY, BodyLaws()))
        after = {
            "effects": mind.effects.stats,
            "values": mind.values,
            "buffer": tuple(mind.buffer),
            "map": mind.map,
            "hist": mind.hist,
            "rng": mind.rng.getstate(),
            "budget_rng": mind._budget_rng.getstate(),
            "observer": getattr(
                mind, "_observer_first_forecast", None),
        }
        self.assertEqual(after, before)

    def test_unrelated_plan_value_matches_original_simulation(self):
        mind = make_mind()
        direct_budget = CognitiveBudget(BODY, BodyLaws())
        direct = mind.simulate(
            BODY, (("attendre",),), 4, direct_budget)

        view_budget = CognitiveBudget(BODY, BodyLaws())
        result = paid_simulate_after_observed_effect(
            mind, BODY, (("attendre",),), 4,
            ("boire",), (0., 0., 60., 0., 0.), view_budget)

        self.assertAlmostEqual(result["value"], direct[0])
        self.assertEqual(result["simulated_plan_steps"], direct[1])
        self.assertAlmostEqual(result["max_uncertainty"], direct[2])
        self.assertEqual(
            result["work_breakdown"]["view"],
            {"cycles": 1, "simulated_steps": 0,
             "memory_items": 7, "replays": 0})
        self.assertEqual(
            result["work_breakdown"]["simulation"],
            {"cycles": 0, "simulated_steps": 9,
             "memory_items": 0, "replays": 0})
        self.assertEqual(
            view_budget.work,
            CognitiveWork(cycles=1, simulated_steps=9, memory_items=7))

    def test_real_mind_state_rng_and_observer_sidecar_are_not_mutated(self):
        mind = make_mind(observer=True)
        mind._observer_first_forecast = {"sentinel": True}
        before = {
            "effects": deepcopy(mind.effects.stats),
            "values": deepcopy(mind.values),
            "buffer": tuple(mind.buffer),
            "map": deepcopy(mind.map),
            "hist": deepcopy(mind.hist),
            "rng": mind.rng.getstate(),
            "budget_rng": mind._budget_rng.getstate(),
            "observer": deepcopy(mind._observer_first_forecast),
        }
        paid_simulate_after_observed_effect(
            mind, BODY, (("boire",), ("attendre",)), 4,
            ("boire",), (0., 0., 60., 0., 0.),
            CognitiveBudget(BODY, BodyLaws()))
        after = {
            "effects": mind.effects.stats,
            "values": mind.values,
            "buffer": tuple(mind.buffer),
            "map": mind.map,
            "hist": mind.hist,
            "rng": mind.rng.getstate(),
            "budget_rng": mind._budget_rng.getstate(),
            "observer": mind._observer_first_forecast,
        }
        self.assertEqual(after, before)

    def test_token_override_is_exact_not_same_action_transfer(self):
        mind = make_mind(observer=True)
        tok0 = paid_simulate_after_observed_effect(
            mind, BODY, (("manger", "tok0"),), 4,
            ("manger", "tok0"), (0., 50., 0., 0., 0.),
            CognitiveBudget(BODY, BodyLaws()))
        self.assertEqual(
            tok0["first_forecast"]["delta"],
            (0., 50., 0., 0., 0.))

        direct_budget = CognitiveBudget(BODY, BodyLaws())
        direct = mind.simulate(
            BODY, (("manger", "tok1"),), 4, direct_budget)
        other = paid_simulate_after_observed_effect(
            mind, BODY, (("manger", "tok1"),), 4,
            ("manger", "tok0"), (0., 50., 0., 0., 0.),
            CognitiveBudget(BODY, BodyLaws()))
        self.assertAlmostEqual(other["value"], direct[0])
        self.assertAlmostEqual(other["max_uncertainty"], direct[2])

    def test_override_does_not_propagate_to_global_or_other_action(self):
        mind = make_mind(observer=True)
        result = paid_simulate_after_observed_effect(
            mind, BODY, (("attendre",),), 4,
            ("boire",), (0., 0., 100., 0., 0.),
            CognitiveBudget(BODY, BodyLaws()))
        expected, uncertainty = mind._read_plan_prediction(("attendre",))
        self.assertEqual(result["first_forecast"]["delta"], tuple(expected))
        self.assertEqual(result["first_forecast"]["uncertainty"], uncertainty)
        self.assertFalse(result["cross_action_transfer"])

    def test_invalid_or_predicted_dead_input_fails_before_spending(self):
        cases = (
            ((80., 50., 0., 80., 80.), (("boire",),),
             ("boire",), (0., 0., 10., 0., 0.)),
            (BODY, (("manger",),),
             ("boire",), (0., 0., 10., 0., 0.)),
            (BODY, (("boire",),),
             ("boire", "bad"), (0., 0., 10., 0., 0.)),
            (BODY, (("boire",),),
             ("boire",), (0., 0., 101., 0., 0.)),
        )
        for body, plan, key, delta in cases:
            allowance = CognitiveBudget(BODY, BodyLaws())
            with self.subTest(case=(body, plan, key, delta)), self.assertRaises(ValueError):
                paid_simulate_after_observed_effect(
                    make_mind(), body, plan, 4, key, delta, allowance)
            self.assertEqual(allowance.work, CognitiveWork())

    def test_view_funding_failure_returns_no_partial_simulation(self):
        body = (.001, 50., 30., 80., .001)
        allowance = CognitiveBudget(body, BodyLaws())
        with self.assertRaises(CognitiveFundingError):
            paid_simulate_after_observed_effect(
                make_mind(), body, (("boire",),), 4,
                ("boire",), (0., 0., 60., 0., 0.), allowance)
        self.assertEqual(allowance.work, CognitiveWork())

    def test_module_import_does_not_load_world_or_runtime(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.modules.observed_effect_view; "
            "assert 'i3.modules.world' not in sys.modules; "
            "assert 'i3.runtime.life' not in sys.modules"
        ], check=True)

    def test_fixed_view_work_is_not_physical_settlement(self):
        result = paid_simulate_after_observed_effect(
            make_mind(), BODY, (("boire",),), 4,
            ("boire",), (0., 0., 60., 0., 0.),
            CognitiveBudget(BODY, BodyLaws()))
        self.assertEqual(VIEW_WORK, CognitiveWork(cycles=1, memory_items=7))
        self.assertFalse(result["model_mutation_authorized"])
        self.assertFalse(result["world_access"])
        self.assertFalse(result["cost_is_physical_settlement_receipt"])


if __name__ == "__main__":
    unittest.main()
