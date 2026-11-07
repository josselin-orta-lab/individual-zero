"""Personal-effect construction: software fixtures, not scientific populations."""
from copy import deepcopy
from dataclasses import replace
from math import fsum
from pathlib import Path
import pickle
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.modules.body import (BodyLaws, CognitiveBudget, CognitiveFundingError,
                             CognitiveWork, cognitive_cost, debit_cognition)
from i3.modules.personal_outcomes import (NoPersonalSupport, PersonalOutcomes,
                                        STORE_WORK, paid_personal_information)

BODY = (40., 40., 40., 80., 40.)
MEAL = ("manger", "tok0")
REST = ("attendre", None)


def record(history, key, delta, *, laws=None):
    """Explicit synthetic paid-body pair; never an observed scientific life."""
    laws = laws or BodyLaws()
    work = CognitiveWork(cycles=5, simulated_steps=2, memory_items=3)
    funded, _ = debit_cognition(BODY, laws, work)
    after = tuple(a + d for a, d in zip(funded, delta))
    budget = CognitiveBudget(after, laws)
    history.observe(key, BODY, work, budget)
    return budget


def budget(body=BODY):
    return CognitiveBudget(body, BodyLaws())


class StationaryProjection:
    """Arithmetic-only projection; integration below uses the actual Mind."""
    gammas = (.7, .9, .99)
    proj_chunks = (1, 2, 4, 8, 16, 32, 64, 128)
    d_max = 5.

    def feats(self, body):
        return tuple((100 - x) / 100 for x in body)

    def distress(self, phi):
        return sum(phi)

    def drift(self):
        return (0.,) * 5, None

    def project(self, body, drift, budget=None):
        budget.spend(CognitiveWork(simulated_steps=len(self.proj_chunks)))
        r = -self.d_max if any(body[k] <= 0 for k in (1, 2, 3)) else -self.distress(self.feats(body))
        return [r / (1 - g) for g in self.gammas], list(body)

    def value(self, index, phi, projection):
        return projection[index]


class PersonalHistoryTests(unittest.TestCase):
    def test_empty_birth_is_unknown_not_a_zero_or_favorable_score(self):
        h, b = PersonalOutcomes(32), budget()
        with self.assertRaises(NoPersonalSupport):
            h.construct(MEAL, (("again", MEAL),), b)
        self.assertEqual(len(h._samples), 0)
        self.assertEqual(b.work.cycles, 2)  # preparation and executed empty scan

    def test_invalid_capacity_key_and_body_rejected(self):
        for value in (True, 0, -1, 513, 3.5):
            with self.assertRaises(ValueError):
                PersonalOutcomes(value)
        h = PersonalOutcomes(32)
        for key in (("unknown", None), ("manger", None), ("boire", "hidden-place"), ["boire", None]):
            with self.assertRaises(ValueError):
                h.observe(key, BODY, CognitiveWork(), budget())
        for bad in ((True, *BODY[1:]), (float("nan"), *BODY[1:]), BODY[:4]):
            with self.assertRaises(ValueError):
                h.observe(REST, bad, CognitiveWork(), budget())
        self.assertFalse(h._samples)

    def test_observed_delta_removes_only_own_decision_debit(self):
        h = PersonalOutcomes(32)
        delta = (-.5, 12., -.4, -4., 0.)
        paid = record(h, MEAL, delta)
        self.assertEqual(paid.work, STORE_WORK)
        for actual, expected in zip(h._samples[0].delta, delta):
            self.assertAlmostEqual(actual, expected)
        self.assertLess(paid.remaining[0], paid.body[0])
        # The new history-storage debit is not smuggled into the earlier outcome.
        self.assertAlmostEqual(h._samples[0].delta[0], -.5)

    def test_non_cognitive_world_laws_are_not_used_to_invent_effects(self):
        a, b = PersonalOutcomes(32), PersonalOutcomes(32)
        record(a, MEAL, (0., 4., 0., -3., 0.))
        record(b, MEAL, (0., 4., 0., -3., 0.),
               laws=replace(BodyLaws(), food_decay=8., sleep_energy_gain=99.))
        self.assertEqual(a._samples, b._samples)

    def test_unknown_token_uses_same_action_but_never_other_action(self):
        h = PersonalOutcomes(32)
        record(h, ("collecter", "tok0"), (0., 10., 0., 0., 0.))
        with self.assertRaises(NoPersonalSupport):
            h.construct(MEAL, (("again", MEAL),), budget())
        record(h, MEAL, (0., -2., 0., -3., 0.))
        unknown = ("manger", "new")
        out = h.construct(unknown, (("again", unknown),), budget())
        self.assertEqual(out[0].probe_delta[1:4], (-2., 0., -3.))

    def test_exact_key_precedes_other_token_experiences(self):
        h = PersonalOutcomes(32)
        record(h, MEAL, (0., -8., 0., 0., 0.))
        record(h, ("manger", "other"), (0., 20., 0., 0., 0.))
        out = h.construct(MEAL, (("again", MEAL),), budget())
        self.assertTrue(all(x.probe_delta[1] == -8 for x in out))

    def test_recent_window_is_chronological_not_favorable_selection(self):
        h = PersonalOutcomes(32)
        for amount in (15., 4., -6., 2.):
            record(h, MEAL, (0., amount, 0., 0., 0.))
        out = h.construct(MEAL, (("again", MEAL),), budget())
        self.assertEqual([x.probe_delta[1] for x in out], [4., -6., 2.])
        self.assertEqual([x.probability for x in out], [1 / 3] * 3)
        self.assertEqual(fsum(x.probability for x in out), 1.)

    def test_capacity_and_new_birth_do_not_inherit_experience(self):
        h = PersonalOutcomes(2)
        for amount in (1., 2., 3.):
            record(h, MEAL, (0., amount, 0., 0., 0.))
        self.assertEqual(len(h._samples), 2)
        out = h.construct(MEAL, (("again", MEAL),), budget())
        self.assertEqual([x.probe_delta[1] for x in out], [2., 3.])
        with self.assertRaises(NoPersonalSupport):
            PersonalOutcomes(2).construct(MEAL, (("again", MEAL),), budget())

    def test_single_sample_is_identical_half_mass_not_new_uncertainty(self):
        h = PersonalOutcomes(32)
        record(h, MEAL, (0., 2., 0., 0., 0.))
        out = h.construct(MEAL, (("again", MEAL),), budget())
        self.assertEqual(out[0], out[1])
        self.assertEqual(out[0].probability, .5)
        r = paid_personal_information(StationaryProjection(), h, MEAL, (("again", MEAL),), budget())
        self.assertEqual(r["information_value"], 0.)

    def test_only_the_same_key_shares_the_probe_hypothesis(self):
        h = PersonalOutcomes(32)
        for amount in (-10., 10.):
            record(h, MEAL, (0., amount, 0., 0., 0.))
        other = ("manger", "unknown")
        out = h.construct(MEAL, (("again", MEAL), ("other", other)), budget())
        for branch in out:
            self.assertEqual(dict(branch.continuations)["again"], branch.probe_delta)
            self.assertEqual(dict(branch.continuations)["other"][1], 0.)
            self.assertEqual(branch.signal, "body_only")

    def test_unfunded_storage_does_not_remember_or_evict(self):
        h = PersonalOutcomes(1)
        record(h, MEAL, (0., 2., 0., 0., 0.))
        before = tuple(h._samples)
        b = budget((0., 40., 40., 80., 40.))
        with self.assertRaises(CognitiveFundingError):
            h.observe(REST, BODY, CognitiveWork(), b)
        self.assertEqual(tuple(h._samples), before)
        self.assertEqual(b.work, CognitiveWork())

    def test_no_history_read_without_funding(self):
        h, b = PersonalOutcomes(32), budget((0., 40., 40., 80., 40.))
        with patch.object(h, "_supports", side_effect=AssertionError("unpaid read")):
            with self.assertRaises(CognitiveFundingError):
                h.construct(MEAL, (("again", MEAL),), b)
        self.assertEqual(b.work, CognitiveWork())

    def test_unknown_continuation_retains_work_and_no_partial_score(self):
        h, b = PersonalOutcomes(32), budget()
        record(h, MEAL, (0., 2., 0., 0., 0.))
        original = tuple(h._samples)
        m = StationaryProjection()
        with patch.object(m, "project", side_effect=AssertionError("partial forecast")):
            with self.assertRaises(NoPersonalSupport):
                paid_personal_information(m, h, MEAL, (("rest", REST),), b)
        # Setup plus one actually executed shared history pass. The missing
        # continuation aborts before branch construction; removed rescans are
        # not fictitiously billed.
        self.assertEqual(b.work.cycles, 2)
        self.assertEqual(b.work.simulated_steps, 0)
        self.assertEqual(tuple(h._samples), original)

    def test_decision_support_index_reuses_only_history_traversal(self):
        h = PersonalOutcomes(32)
        record(h, MEAL, (0., 2., 0., 0., 0.))
        record(h, REST, (0., -1., 0., 0., 0.))
        index = h.begin_support_index()
        b = budget()
        first_receipt, second_receipt = {}, {}
        first = h.construct(
            MEAL, (("rest", REST),), b,
            work_receipt=first_receipt, support_index=index)
        first_work = b.work
        second = h.construct(
            REST, (("meal", MEAL),), b,
            work_receipt=second_receipt, support_index=index)
        self.assertEqual(first_receipt["history_access"], "shared_scan")
        self.assertEqual(second_receipt["history_access"], "indexed_lookup")
        self.assertEqual(
            first_receipt["history_scan"],
            {"cycles": 1, "simulated_steps": 0,
             "memory_items": 18, "replays": 0})
        self.assertEqual(
            second_receipt["history_scan"],
            {"cycles": 1, "simulated_steps": 0,
             "memory_items": 4, "replays": 0})
        for actual, expected in zip(first[0].probe_delta, (0., 2., 0., 0., 0.)):
            self.assertAlmostEqual(actual, expected)
        for actual, expected in zip(second[0].probe_delta, (0., -1., 0., 0., 0.)):
            self.assertAlmostEqual(actual, expected)
        self.assertGreater(b.work.cycles, first_work.cycles)

    def test_decision_support_index_rejects_cross_owner_and_stale_history(self):
        h = PersonalOutcomes(32)
        record(h, MEAL, (0., 2., 0., 0., 0.))
        index = h.begin_support_index()
        h.construct(MEAL, (("again", MEAL),), budget(), support_index=index)

        other, other_budget = PersonalOutcomes(32), budget()
        record(other, MEAL, (0., 2., 0., 0., 0.))
        with self.assertRaises(ValueError):
            other.construct(MEAL, (("again", MEAL),), other_budget,
                            support_index=index)
        self.assertEqual(other_budget.work, CognitiveWork())

        record(h, REST, (0., -1., 0., 0., 0.))
        stale_budget = budget()
        with self.assertRaises(ValueError):
            h.construct(MEAL, (("again", MEAL),), stale_budget,
                        support_index=index)
        self.assertEqual(stale_budget.work, CognitiveWork())

    def test_death_and_mixed_learning_phase_rejected(self):
        h = PersonalOutcomes(32)
        for dead in ((40., 0., 40., 80., 40.), (40., 40., 0., 80., 40.)):
            b = budget(dead)
            with self.assertRaises(ValueError):
                h.observe(REST, BODY, CognitiveWork(), b)
            with self.assertRaises(ValueError):
                h.construct(REST, (("rest", REST),), b)
            self.assertEqual(b.work, CognitiveWork())
            with self.assertRaises(ValueError):
                h.observe(REST, dead, CognitiveWork(), budget())
        b = budget()
        b.spend(CognitiveWork(cycles=1))
        with self.assertRaises(ValueError):
            h.observe(REST, BODY, CognitiveWork(), b)
        self.assertFalse(h._samples)

    def test_forged_unaffordable_past_work_rejected_before_storage(self):
        h, b = PersonalOutcomes(32), budget()
        with self.assertRaises(CognitiveFundingError):
            h.observe(REST, BODY, CognitiveWork(cycles=100000), b)
        self.assertFalse(h._samples)
        self.assertEqual(b.work, CognitiveWork())

    def test_invalid_continuations_and_flags_do_not_read_history(self):
        h = PersonalOutcomes(32)
        for items in ((), [], (("x", MEAL), ("x", REST)), (("x",),)):
            b = budget()
            with self.assertRaises(ValueError):
                h.construct(MEAL, items, b)
            self.assertEqual(b.work, CognitiveWork())
        b = budget()
        with self.assertRaises(ValueError):
            paid_personal_information(StationaryProjection(), h, MEAL, (("x", MEAL),), b,
                                      perceive_cost=1)
        self.assertEqual(b.work, CognitiveWork())


class PersonalKernelTests(unittest.TestCase):
    def history(self, token="tok0"):
        h = PersonalOutcomes(32)
        for amount in (-10., 10.):
            record(h, ("manger", token), (0., amount, 0., 0., 0.))
        record(h, REST, (0., -1., 0., 0., 0.))
        return h

    def test_personal_branches_reach_paid_kernel_with_all_costs(self):
        h, b = self.history(), budget()
        snapshot = tuple(h._samples)
        r = paid_personal_information(StationaryProjection(), h, MEAL,
                                      (("again", MEAL), ("rest", REST)), b)
        for k, value in r["total_work"].items():
            self.assertEqual(value, getattr(b.work, k))
            self.assertEqual(value, r["construction_work"][k] + r["work"][k])
        self.assertEqual(r["forecast_start_body"], b.remaining)
        self.assertEqual(tuple(h._samples), snapshot)
        self.assertGreater(r["information_value"], 0.)
        self.assertEqual(len(r["conditional_choices"]), 2)
        self.assertTrue(all(x["signal"] == "body_only" for x in r["conditional_choices"]))

    def test_zero_perceived_kernel_cost_still_pays_constructor_and_kernel(self):
        a, b = budget(), budget()
        h = self.history()
        yes = paid_personal_information(StationaryProjection(), h, MEAL,
                                        (("again", MEAL), ("rest", REST)), a)
        no = paid_personal_information(StationaryProjection(), h, MEAL,
                                       (("again", MEAL), ("rest", REST)), b, perceive_cost=False)
        self.assertEqual(a.work, b.work)
        self.assertEqual(a.remaining, b.remaining)
        built_body, _ = debit_cognition(BODY, b.laws, CognitiveWork(**no["construction_work"]))
        self.assertEqual(no["forecast_start_body"], built_body)
        self.assertGreater(no["informed_value"], yes["informed_value"])

    def test_renaming_and_continuation_order_do_not_change_forecast(self):
        a = paid_personal_information(StationaryProjection(), self.history(), MEAL,
                                      (("again", MEAL), ("rest", REST)), budget())
        renamed = ("manger", "another-name")
        b = paid_personal_information(StationaryProjection(), self.history(renamed[1]), renamed,
                                      (("zzz", REST), ("aaa", renamed)), budget())
        for field in ("informed_value", "uninformed_value", "information_value", "total_work"):
            self.assertEqual(a[field], b[field])

    def test_saturated_bodies_do_not_reveal_sample_identity(self):
        h = PersonalOutcomes(32)
        for amount in (10., 20.):
            record(h, MEAL, (0., amount, 0., 0., 0.))
        record(h, REST, (0., -1., 0., 0., 0.))
        r = paid_personal_information(StationaryProjection(), h, MEAL,
                                      (("again", MEAL), ("rest", REST)),
                                      budget((40., 95., 40., 80., 40.)))
        self.assertEqual(len(r["conditional_choices"]), 1)
        self.assertEqual(r["information_value"], 0.)

    def test_kernel_failure_keeps_constructor_work_without_mutating_history(self):
        h, b = self.history(), budget()
        original = tuple(h._samples)
        m = StationaryProjection()
        with patch.object(m, "project", side_effect=RuntimeError("interrupted")):
            with self.assertRaises(RuntimeError):
                paid_personal_information(m, h, MEAL, (("again", MEAL),), b)
        self.assertGreater(b.work.cycles, 0)
        self.assertEqual(b.work.simulated_steps, 2)
        self.assertEqual(tuple(h._samples), original)


class PersonalRuntimeTests(unittest.TestCase):
    def test_actual_mind_world_personal_record_kernel_and_physical_settlement(self):
        from i3.lab import p2_ecologies
        from i3.modules.genome import generation_zero
        from i3.modules.mind import Mind
        from i3.modules.world import World
        for index in (0, 1):
            world = World(p2_ecologies.world_for("stable", "development", index))
            mind = Mind(generation_zero(901), 910000 + index)
            history = PersonalOutcomes(mind.m_max)
            keys = []
            # Extra personal-memory work is really executed and physically paid.
            # This short software harness is NOT a reference-parity/survival study.
            for _ in range(8):
                if world.dead:
                    break
                cap = world.capture()
                decision = CognitiveBudget(world.body, world.laws)
                action, param, work, _ = mind.decide(cap, decision)
                result = world.step(action, param, work)
                if world.dead or mind.last is None:
                    continue
                raw_key = mind.last[1]
                key = (action, raw_key[1] if action in ("manger", "collecter") else None)
                extra = CognitiveBudget(world.body, world.laws)
                history.observe(key, cap["body"], work, extra)
                paid = world.pay_cognition(extra.work)
                self.assertEqual(world.body, extra.remaining)
                self.assertEqual(tuple(paid[c]["paid"] for c in ("energy", "vigilance")),
                                 cognitive_cost(world.laws, STORE_WORK))
                keys.append(key)
                result["body"] = world.body
                mind.observe_outcome(result)
                learning = CognitiveBudget(world.body, world.laws)
                replays = mind.prepare_learning(result, learning)
                if replays is not None:
                    world.pay_cognition(learning.work)
                    result["body"] = world.body
                    self.assertEqual(mind.learn_from_outcome(result, replay_limit=replays), replays)
            self.assertTrue(keys)
            self.assertFalse(world.dead)
            original_mind, original_history = pickle.dumps(mind.__dict__), tuple(history._samples)
            before, tick = world.body, world.t
            b = CognitiveBudget(world.body, world.laws)
            r = paid_personal_information(mind, history, keys[-1], (("again", keys[-1]),), b)
            self.assertEqual(world.body, before)  # allowance alone is not settlement
            payment = world.pay_cognition(b.work)
            self.assertEqual(world.body, b.remaining)
            self.assertEqual(world.t, tick)  # no motor command from the constructor
            self.assertEqual(r["forecast_start_body"], world.body)
            self.assertEqual(pickle.dumps(mind.__dict__), original_mind)
            self.assertEqual(tuple(history._samples), original_history)
            self.assertGreater(payment["energy"]["paid"], 0.)

    def test_reference_runner_has_no_implicit_personal_history_hook(self):
        from i3.lab import p2_ecologies
        from i3.modules.genome import generation_zero
        from i3.runtime.life import run_life
        spec = p2_ecologies.world_for("stable", "development", 0)
        genome = generation_zero(901)
        a = run_life(genome, spec, 910000, 8, keep_trace=True, observer_mind_digest=True)
        with patch("i3.modules.personal_outcomes.PersonalOutcomes.observe",
                   side_effect=AssertionError("unexpected reference hook")), \
             patch("i3.modules.personal_outcomes.PersonalOutcomes.construct",
                   side_effect=AssertionError("unexpected reference hook")):
            b = run_life(genome, spec, 910000, 8, keep_trace=True, observer_mind_digest=True)
        for field in ("trace", "trace_head", "evidence_head", "cognitive_accounting",
                      "actions", "final_body", "outcome_model_sha256", "spatial_beliefs_sha256"):
            self.assertEqual(a[field], b[field], field)


if __name__ == "__main__":
    unittest.main()
