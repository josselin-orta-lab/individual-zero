"""Stage-1 kernel tests. Synthetic forecasts are NOT scientific observations."""
from copy import deepcopy
from dataclasses import replace
from math import fsum
from pathlib import Path
import pickle
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.modules.body import BodyLaws, CognitiveBudget, CognitiveFundingError, CognitiveWork, debit_cognition
from i3.modules.information_value import SubjectiveOutcome, paid_information_value

ZERO = (0.,) * 5
BODY = (40., 40., 40., 80., 40.)
GOOD = (0., 20., 0., 0., 0.)
BAD = (0., -20., 0., 0., 0.)


def branches(signals=("left", "right")):
    return (SubjectiveOutcome(.5, signals[0], ZERO, (("a", GOOD), ("b", BAD))),
            SubjectiveOutcome(.5, signals[1], ZERO, (("a", BAD), ("b", GOOD))))


class StationaryProjection:
    """Synthetic stationary distress model, only for arithmetic unit tests."""
    gammas = (.7, .9, .99)
    proj_chunks = (1, 2, 4, 8, 16, 32, 64, 128)
    d_max = 5.

    def __init__(self):
        self.calls = []
        self.drift_calls = 0

    def feats(self, body):
        return tuple((100 - x) / 100 for x in body)

    def distress(self, features):
        return sum(features)

    def drift(self):
        self.drift_calls += 1
        return ZERO, None

    def project(self, body, drift, budget=None):
        budget.spend(CognitiveWork(simulated_steps=len(self.proj_chunks)))
        self.calls.append((tuple(body), budget.work))
        r = (-self.d_max if any(body[k] <= 0 for k in (1, 2, 3))
             else -self.distress(self.feats(body)))
        ret, disc = [0.] * 3, [1.] * 3
        for run in self.proj_chunks:
            for k, g in enumerate(self.gammas):
                ret[k] += disc[k] * r * (1 - g ** run) / (1 - g)
                disc[k] *= g ** run
        return [v + d * r / (1 - g) for v, d, g in zip(ret, disc, self.gammas)], list(body)

    def value(self, index, features, projection):
        return projection[index]


class InformationKernelTests(unittest.TestCase):
    def evaluate(self, outcomes=None, **kwargs):
        model, budget = StationaryProjection(), CognitiveBudget(BODY, BodyLaws())
        result = paid_information_value(model, branches() if outcomes is None else outcomes, budget, **kwargs)
        return result, model, budget

    def test_information_changes_continuation_not_best_hidden_outcome(self):
        r, _, _ = self.evaluate()
        self.assertGreater(r["information_value"], 0)
        self.assertEqual([x["best_continuations"] for x in r["conditional_choices"]], [("a",), ("b",)])
        self.assertAlmostEqual(r["informed_value"], fsum(.5 * max(row) for row in r["branch_values"]))
        self.assertAlmostEqual(r["uninformed_value"], max(fsum(.5 * row[j] for row in r["branch_values"]) for j in range(2)))

    def test_indistinguishable_signals_give_exactly_zero_information(self):
        r, _, _ = self.evaluate(branches(("same", "same")))
        self.assertEqual(r["information_value"], 0)
        self.assertEqual(len(r["conditional_choices"]), 1)

    def test_sensed_body_is_an_observation_not_a_hidden_branch_index(self):
        b = branches(("same", "same"))
        b = (b[0], replace(b[1], probe_delta=(0., 1., 0., 0., 0.)))
        r, _, _ = self.evaluate(b)
        self.assertEqual(len(r["conditional_choices"]), 2)
        self.assertGreater(r["information_value"], 0)

    def test_no_information_when_the_same_continuation_is_always_best(self):
        b = branches()
        r, _, _ = self.evaluate((b[0], replace(b[1], continuations=b[0].continuations)))
        self.assertEqual(r["information_value"], 0)

    def test_three_outcomes_average_risk_instead_of_optimistic_maximum(self):
        outcomes = tuple(SubjectiveOutcome(p, str(i), ZERO, (("only", d),))
                         for i, (p, d) in enumerate(((.25, GOOD), (.5, ZERO), (.25, BAD))))
        r, model, _ = self.evaluate(outcomes)
        expected = fsum(b.probability * row[0] for b, row in zip(outcomes, r["branch_values"]))
        self.assertAlmostEqual(r["informed_value"], expected)
        self.assertLess(r["informed_value"], max(row[0] for row in r["branch_values"]))
        self.assertEqual(r["information_value"], 0)
        self.assertEqual(len(model.calls), 3)

    def test_every_matrix_cell_and_reduction_is_prepaid(self):
        r, model, budget = self.evaluate()
        self.assertEqual(r["work"], dict(cycles=6, simulated_steps=40, memory_items=34, replays=0))
        self.assertEqual(len(model.calls), 4)
        for i, (_, work) in enumerate(model.calls, 1):
            self.assertEqual(work.simulated_steps, i * 10)
            self.assertEqual(work.cycles, i + 1)
        self.assertEqual(budget.work, CognitiveWork(**r["work"]))
        self.assertEqual(r["body_after_computation"], debit_cognition(BODY, BodyLaws(), budget.work)[0])
        self.assertEqual(r["forecast_start_body"], budget.remaining)
        self.assertFalse(r["cost_is_physical_settlement_receipt"])

    def test_zero_perceived_cost_still_pays_all_actual_work(self):
        paid, _, budget = self.evaluate()
        blind, _, other = self.evaluate(perceive_cost=False)
        self.assertEqual(paid["work"], blind["work"])
        self.assertEqual(budget.remaining, other.remaining)
        self.assertEqual(blind["forecast_start_body"], BODY)
        self.assertGreater(blind["informed_value"], paid["informed_value"])

    def test_prior_spending_is_never_ignored_even_by_zero_cost_diagnostic(self):
        for include in (False, True):
            model, budget = StationaryProjection(), CognitiveBudget(BODY, BodyLaws())
            earlier = CognitiveWork(cycles=7)
            budget.spend(earlier)
            before = budget.remaining
            r = paid_information_value(model, branches(), budget, perceive_cost=include)
            self.assertEqual(budget.work.cycles, earlier.cycles + r["work"]["cycles"])
            self.assertEqual(r["forecast_start_body"], budget.remaining if include else before)

    def test_unfunded_preparation_does_no_projection_or_drift(self):
        model, budget = StationaryProjection(), CognitiveBudget((0., 40., 40., 80., 40.), BodyLaws())
        with self.assertRaises(CognitiveFundingError):
            paid_information_value(model, branches(), budget)
        self.assertEqual(budget.work, CognitiveWork())
        self.assertEqual((model.calls, model.drift_calls), ([], 0))

    def test_failed_complete_quote_retains_only_executed_preparation(self):
        for include in (True, False):
            model, budget = StationaryProjection(), CognitiveBudget((.05, 40., 40., 80., 40.), BodyLaws())
            with self.assertRaises(CognitiveFundingError):
                paid_information_value(model, branches(), budget, perceive_cost=include)
            self.assertEqual(budget.work, CognitiveWork(cycles=1, memory_items=34))
            self.assertEqual((model.calls, model.drift_calls), ([], 1))

    def test_projection_exception_never_returns_a_partial_estimate_or_refunds(self):
        class Broken(StationaryProjection):
            def project(self, body, drift, budget=None):
                out = super().project(body, drift, budget)
                if len(self.calls) == 2:
                    raise RuntimeError("synthetic model failure")
                return out
        model, budget = Broken(), CognitiveBudget(BODY, BodyLaws())
        with self.assertRaisesRegex(RuntimeError, "synthetic model failure"):
            paid_information_value(model, branches(), budget)
        self.assertEqual(budget.work, CognitiveWork(cycles=3, simulated_steps=20, memory_items=34))

    def test_projection_without_its_declared_payment_is_rejected(self):
        class Unpaid(StationaryProjection):
            def project(self, body, drift, budget=None):
                return [0., 0., 0.], body
        with self.assertRaisesRegex(RuntimeError, "funded quote"):
            paid_information_value(Unpaid(), branches(), CognitiveBudget(BODY, BodyLaws()))

    def test_predicted_death_is_absorbing_despite_favorable_later_delta(self):
        b = SubjectiveOutcome(.5, "fatal", (0., -100., 0., 0., 0.), (("later", (0., 100., 0., 0., 0.)),))
        r, model, _ = self.evaluate((b, replace(b, signal="other")))
        self.assertEqual(r["informed_value"], -model.d_max)
        self.assertTrue(all(body[1] == 0 for body, _ in model.calls))
        self.assertEqual(len(model.calls), 2)

    def test_actual_terminal_body_rejects_all_computation(self):
        model, budget = StationaryProjection(), CognitiveBudget((40., 0., 40., 80., 40.), BodyLaws())
        with self.assertRaisesRegex(ValueError, "physical death"):
            paid_information_value(model, branches(), budget)
        self.assertEqual(budget.work, CognitiveWork())
        self.assertEqual((model.calls, model.drift_calls), ([], 0))

    def test_labels_and_order_carry_no_action_preference(self):
        original, _, _ = self.evaluate()
        b = tuple(replace(x, signal="renamed-" + x.signal,
                          continuations=tuple(("z" if n == "a" else "y", d) for n, d in reversed(x.continuations)))
                  for x in reversed(branches()))
        renamed, _, _ = self.evaluate(b)
        for key in ("informed_value", "uninformed_value", "information_value", "work", "body_after_computation"):
            self.assertEqual(original[key], renamed[key])

    def test_inputs_are_not_modified(self):
        b = branches()
        before = deepcopy(b)
        self.evaluate(b)
        self.assertEqual(b, before)

    def test_unknown_prior_and_incomplete_continuations_are_not_invented(self):
        b = branches()
        for invalid in ((), (b[0],), b + b, (b[0], replace(b[1], continuations=(("foreign", ZERO),)))):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                self.evaluate(invalid)

    def test_bad_probabilities_deltas_and_signals_fail_before_work(self):
        b = branches()
        invalid = [replace(b[0], probability=x) for x in (0, -1, True, float("nan"), float("inf"), .4)]
        invalid += [replace(b[0], probe_delta=x) for x in ((0.,) * 4, (True, 0., 0., 0., 0.), (101., 0., 0., 0., 0.))]
        invalid += [replace(b[0], signal=""), replace(b[0], continuations=(("a", ZERO), ("a", GOOD)))]
        for branch in invalid:
            model, budget = StationaryProjection(), CognitiveBudget(BODY, BodyLaws())
            with self.subTest(branch=branch), self.assertRaises(ValueError):
                paid_information_value(model, (branch, b[1]), budget)
            self.assertEqual(budget.work, CognitiveWork())

    def test_nonfinite_model_output_has_no_valid_score(self):
        class Broken(StationaryProjection):
            def value(self, index, features, projection):
                return float("nan")
        with self.assertRaisesRegex(ValueError, "nonfinite"):
            paid_information_value(Broken(), branches(), CognitiveBudget(BODY, BodyLaws()))


class InformationKernelIntegrationTests(unittest.TestCase):
    def test_actual_mind_projection_and_world_debit_without_policy_mutation(self):
        from i3.modules.genome import midpoint
        from i3.modules.mind import Mind
        from i3.modules.world import World, WorldSpec
        mind = Mind(midpoint(), 901)
        before = pickle.dumps(mind.__dict__)
        world = World(WorldSpec("stage1-software-only", 3, 3, (1, 1), BODY))
        budget = CognitiveBudget(world.body, world.laws)
        r = paid_information_value(mind, branches(), budget)
        self.assertEqual(before, pickle.dumps(mind.__dict__))
        self.assertGreater(r["information_value"], 0)
        self.assertEqual(world.body, BODY)
        bill = world.pay_cognition(budget.work)
        self.assertEqual(world.body, r["body_after_computation"])
        self.assertGreater(bill["energy"]["paid"], 0)
        self.assertGreater(bill["vigilance"]["paid"], 0)
        self.assertEqual(world.t, 0)

    def test_reference_life_stays_identical_after_separate_kernel_call(self):
        from i3.lab.p2_ecologies import world_for
        from i3.modules.genome import generation_zero
        from i3.modules.mind import Mind
        from i3.runtime.life import run_life
        genome = generation_zero(901)
        spec = world_for("stable", "development", 0)
        opts = dict(keep_trace=True, observer_mind_digest=True, observer_full_competition=True)
        before = run_life(genome, spec, 17, 8, **opts)
        paid_information_value(Mind(genome, 19), branches(), CognitiveBudget(BODY, BodyLaws()))
        after = run_life(genome, spec, 17, 8, **opts)
        for key in ("trace", "evidence_head", "manifest_id", "cognitive_accounting", "actions",
                    "final_body", "outcome_model_sha256", "spatial_beliefs_sha256", "observer_full_competition"):
            self.assertEqual(before[key], after[key], key)


if __name__ == "__main__":
    unittest.main()
