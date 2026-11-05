"""Development-only falsifiers for v2 payment, inactivity and same-step replay."""
from copy import deepcopy
from dataclasses import asdict, replace
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'src'))
from i3.modules.body import (BodyLaws, CognitiveBudget, CognitiveFundingError,
                            CognitiveWork, cognitive_cost, debit_cognition, transition)
from i3.modules.genome import midpoint, generation_zero
from i3.modules.mind import Mind
from i3.modules.world import World
from i3.lab.dev_worlds import dev_open_field, dev_long_corridor
from i3.runtime.life import run_life


class AllowanceTests(unittest.TestCase):
    def test_exact_boundary_can_be_paid_once(self):
        budget = CognitiveBudget((.02, 50., 50., 100., .05), BodyLaws())
        budget.spend(CognitiveWork(cycles=1))
        self.assertEqual((budget.remaining[0], budget.remaining[4]), (0., 0.))
        before = (budget.work, budget.remaining)
        self.assertFalse(budget.try_spend(CognitiveWork(cycles=1)))
        self.assertEqual((budget.work, budget.remaining), before)

    def test_failed_reservation_is_atomic(self):
        budget = CognitiveBudget((1., 50., 50., 100., 1.), BodyLaws())
        with self.assertRaises(CognitiveFundingError):
            budget.spend(CognitiveWork(simulated_steps=1000))
        self.assertEqual(budget.work, CognitiveWork())
        self.assertEqual(budget.remaining, budget.body)

    def test_mixed_work_reconciles_with_one_strict_debit(self):
        budget = CognitiveBudget((4., 50., 50., 100., 5.), BodyLaws())
        for work in (CognitiveWork(cycles=2), CognitiveWork(memory_items=30),
                     CognitiveWork(simulated_steps=50, replays=4)):
            budget.spend(work)
        self.assertEqual(budget.work, CognitiveWork(2, 50, 30, 4))
        body, audit = debit_cognition(budget.body, budget.laws, budget.work)
        self.assertEqual(body, budget.remaining)
        self.assertTrue(all(bill['paid'] == bill['requested'] for bill in audit.values()))

    def test_no_silent_reuse_of_v1_physics(self):
        with self.assertRaises(ValueError):
            CognitiveBudget((50.,)*5, replace(BodyLaws(), version='i3-body-laws-v1'))

    def test_invalid_laws_and_limits_fail_before_use(self):
        for laws in (replace(BodyLaws(), water_decay=-1),
                     replace(BodyLaws(), sleep_food_cost_per_energy=0),
                     replace(BodyLaws(), energy_per_cycle=float('nan'))):
            with self.subTest(laws=laws), self.assertRaises(ValueError):
                CognitiveBudget((50.,)*5, laws)
        with self.assertRaises(ValueError):
            CognitiveBudget((-1., 50., 50., 50., 50.), BodyLaws())


class StrictPhysicsTests(unittest.TestCase):
    def test_future_sleep_cannot_finance_current_decision(self):
        with self.assertRaises(CognitiveFundingError):
            transition((.01, 50., 50., 100., 50.), 'dormir', BodyLaws(),
                       CognitiveWork(cycles=1))

    def test_motor_cannot_spend_cognitive_reservation(self):
        with self.assertRaises(CognitiveFundingError):
            transition((2., 50., 50., 100., 50.), 'se_deplacer', BodyLaws(),
                       CognitiveWork(cycles=1))

    def test_quiescence_is_not_sleep_or_free_chosen_wait(self):
        body = (0., 50., 50., 90., 0.)
        after, death = transition(body, None, BodyLaws(), CognitiveWork())
        self.assertEqual(death, ())
        self.assertEqual(after, (0., 49.8, 49.6, 90., 0.))
        with self.assertRaises(CognitiveFundingError):
            transition(body, 'attendre', BodyLaws(), CognitiveWork())

    def test_invalid_request_cannot_apply_scheduled_changes(self):
        spec = dev_open_field()
        source = next(iter(spec.water))
        spec.changes = ((1, 'water_stock', source, 0),)
        for action, param, work in [('bogus', None, CognitiveWork()),
                                    ('se_deplacer', 'bad', CognitiveWork()),
                                    ('manger', 'missing', CognitiveWork()),
                                    ('attendre', None, CognitiveWork(cycles=100000)),
                                    (None, 'not-null', CognitiveWork())]:
            world = World(spec)
            before = deepcopy(world.__dict__)
            with self.subTest(action=action), self.assertRaises((ValueError, KeyError)):
                world.step(action, param, work)
            self.assertEqual(world.__dict__, before)

    def test_failed_postpayment_preserves_world(self):
        world = World(dev_open_field())
        before = deepcopy(world.__dict__)
        with self.assertRaises(CognitiveFundingError):
            world.pay_cognition(CognitiveWork(cycles=100000))
        self.assertEqual(world.__dict__, before)

    def test_death_at_birth_is_not_reversible(self):
        spec = replace(dev_open_field(), body=(50., 50., 0., 100., 50.))
        world = World(spec)
        with self.assertRaises(RuntimeError):
            world.step('dormir', None, CognitiveWork())
        with self.assertRaises(RuntimeError):
            world.pay_cognition(CognitiveWork())
        result = run_life(midpoint(), spec, 0, 20)
        self.assertEqual(result['steps_lived'], 0)
        self.assertEqual(result['terminal'], 'dead')
        self.assertEqual(result['cognitive_accounting']['learning_updates'], 0)


class FundedMindTests(unittest.TestCase):
    def test_unfunded_capture_is_not_processed(self):
        spec = replace(dev_open_field(), body=(0., 50., 50., 100., 0.))
        world, mind = World(spec), Mind(midpoint(), 0)
        rng_before = mind.rng.getstate()
        budget = CognitiveBudget(world.body, world.laws)
        with patch.object(mind, 'perceive', side_effect=AssertionError('unfunded perception')):
            action, param, work, info = mind.decide(world.capture(), budget)
        self.assertIsNone(action)
        self.assertEqual(work, CognitiveWork())
        self.assertEqual(mind.map, {})
        self.assertEqual(mind.rng.getstate(), rng_before)

    def test_unfunded_projection_is_not_executed(self):
        mind = Mind(midpoint(), 0)
        budget = CognitiveBudget((.001, 50., 50., 100., .001), BodyLaws())
        with patch.object(mind, 'feats', side_effect=AssertionError('unfunded projection')):
            with self.assertRaises(CognitiveFundingError):
                mind.project((50.,)*5, mind.drift(), budget)
        self.assertEqual(budget.work, CognitiveWork())

    def test_partial_simulation_stays_paid_but_has_no_score(self):
        mind = Mind(midpoint(), 0)
        budget = CognitiveBudget((.002, 50., 50., 100., .002), BodyLaws())
        with self.assertRaises(CognitiveFundingError):
            mind.simulate((50.,)*5, [('attendre',)], 1, budget)
        self.assertEqual(budget.work.simulated_steps, 1)
        self.assertEqual(budget.remaining[0], 0.)

    def test_unaffordable_learning_changes_neither_effects_nor_memories(self):
        mind = Mind(midpoint(), 0)
        body = (.001, 50., 50., 100., .001)
        mind.last = (body, ('attendre',), 'attendre', None)
        budget = CognitiveBudget(body, BodyLaws())
        self.assertIsNone(mind.prepare_learning({'body': body, 'dead': ()}, budget))
        self.assertEqual(budget.work, CognitiveWork())
        self.assertEqual(mind.effects.stats, {})
        self.assertFalse(mind.buffer)

    def test_exhaustion_advances_passive_time_without_forced_recovery(self):
        spec = replace(dev_open_field(), body=(0., 50., 1., 100., 0.))
        result = run_life(midpoint(), spec, 0, 20, keep_trace=True)
        self.assertEqual(result['terminal'], 'dead')
        self.assertEqual(result['death_causes'], ['zero_water'])
        self.assertEqual(result['steps_lived'], 3)
        self.assertEqual(result['actions'], {'physical_inactivity': 3})
        self.assertTrue(all(row['action'] is None for row in result['trace']))
        self.assertEqual(result['cognitive_accounting']['totals']['energy']['paid'], 0.)

    def test_mismatched_allowance_is_not_accepted(self):
        world, mind = World(dev_open_field()), Mind(midpoint(), 0)
        with self.assertRaises(ValueError):
            mind.decide(world.capture(), CognitiveBudget((1.,)*5, world.laws))


# This controlled policy is ONLY a unit fixture for the terminal billing path.
def paid_sleep(mind, cap, budget):
    budget.spend(CognitiveWork(cycles=3))
    mind.last = (cap['body'], ('dormir',), 'dormir', None)
    return 'dormir', None, budget.work, {'option': 'unit-prepaid-sleep'}


class ReplayAndEvidenceTests(unittest.TestCase):
    def test_last_observed_sleep_is_settled_on_that_step(self):
        with patch.object(Mind, 'decide', paid_sleep):
            result = run_life(midpoint(), dev_open_field(), 0, 1, keep_trace=True)
        audit = result['cognitive_accounting']
        self.assertEqual(audit['status'], 'SETTLED_FOR_DECLARED_WORK')
        self.assertEqual(audit['replays_executed'], 1)
        self.assertEqual(audit['pending_replays'], 0)
        self.assertEqual(audit['pending_energy'], 0.)
        row = result['trace'][0]
        self.assertEqual(row['funding_phases']['learning']['work']['replays'], 1)
        self.assertGreater(row['funding_phases']['learning']['accounting']['energy']['paid'], 0.)

    def test_terminal_sleep_performs_no_postmortem_learning(self):
        spec = replace(dev_open_field(), body=(50., 50., .3, 100., 50.))
        with patch.object(Mind, 'decide', paid_sleep), \
             patch.object(Mind, 'learn_from_outcome', side_effect=AssertionError('postmortem')):
            result = run_life(midpoint(), spec, 0, 1, keep_trace=True)
        self.assertEqual(result['terminal'], 'dead')
        self.assertEqual(result['cognitive_accounting']['replays_executed'], 0)
        self.assertEqual(result['trace'][0]['funding_phases']['learning']['work'], asdict(CognitiveWork()))

    def test_replay_count_is_bounded_before_updates(self):
        mind = Mind(midpoint(), 0)
        body = (.077, 50., 50., 100., 1.)
        mind.last = (body, ('dormir',), 'dormir', None)
        mind.buffer.extend((0., (50.,)*5, (50.,)*5, False) for _ in range(10))
        budget = CognitiveBudget(body, BodyLaws())
        count = mind.prepare_learning({'body': body, 'dead': ()}, budget)
        self.assertEqual(count, 0)  # Base 0.0742 fits; one replay does not.
        self.assertEqual(budget.work.replays, 0)
        self.assertGreater(budget.remaining[0], 0.)

    def test_development_evidence_has_exact_phase_conservation_and_replay(self):
        for seed in (2, 9):
            for factory in (dev_open_field, dev_long_corridor):
                a = run_life(generation_zero(seed), factory(), 4, 100, keep_trace=True)
                b = run_life(generation_zero(seed), factory(), 4, 100)
                self.assertEqual(a['trace_head'], b['trace_head'])
                self.assertEqual(a['evidence_head'], b['evidence_head'])
                audit = a['cognitive_accounting']
                self.assertEqual(audit['shortfall_steps'], 0)
                self.assertEqual(audit['pending_replays'], 0)
                replay_count = 0
                for row in a['trace']:
                    for phase in row['funding_phases'].values():
                        work = CognitiveWork(**phase['work'])
                        costs = cognitive_cost(factory().laws, work)
                        replay_count += work.replays
                        for channel, idx, cost in zip(('energy', 'vigilance'), (0, 4), costs):
                            bill = phase['accounting'][channel]
                            self.assertEqual(bill, {'requested': cost, 'paid': cost, 'unpaid': 0.})
                            self.assertAlmostEqual(phase['body_before'][idx] -
                                                   phase['body_after_debit'][idx], cost, places=12)
                self.assertEqual(replay_count, audit['replays_executed'])
                for channel in ('energy', 'vigilance'):
                    paid = sum(r['cognitive_accounting'][channel]['paid'] for r in a['trace'])
                    self.assertAlmostEqual(paid, audit['totals'][channel]['paid'], places=12)


if __name__ == '__main__':
    unittest.main()
