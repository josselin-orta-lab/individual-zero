"""Software-only native trace hashing and two-currency funding checks.

Traces here are wholly fabricated, with no World/Mind invocation, birth or
source timestamp. They exercise math, not scientific authenticity or physics.
"""
from __future__ import annotations

import ast
from copy import deepcopy
from hashlib import sha256
import inspect
import json
from pathlib import Path
import runpy
import unittest
from unittest.mock import patch

from i3.lab import stage6_light_trace_funding_preflight as v

_native_case = runpy.run_path(str(Path(__file__).with_name(
    'test_stage6_light_native_custody_preflight.py')))['native_case']
_source = runpy.run_path(str(Path(__file__).with_name(
    'test_stage6_light_native_custody_preflight.py')))['_source']


def fabricated_traced_life():
    """400 entirely invented funded steps, not a physical life."""
    source_pin, _ = _source()
    identity, life = _native_case(0, 0, 'shared', 0, 'stable', 0, source_pin)
    rates = {
        'version': 'i3-body-laws-v2',
        'energy_per_cycle': 0.02, 'energy_per_simulated_step': 0.002,
        'energy_per_memory_item': 0.0002, 'energy_per_replay': 0.005,
        'vigilance_per_cycle': 0.05, 'vigilance_per_simulated_step': 0.002,
        'vigilance_per_replay': 0.01,
    }
    life['manifest']['world']['laws'] = rates
    life['manifest']['world_sha256'] = v.custody._digest(life['manifest']['world'])
    identity['world_sha256'] = life['manifest']['world_sha256']
    life['manifest_id'] = v.custody._digest(life['manifest'])
    work = {'cycles': 1, 'simulated_steps': 0, 'memory_items': 0, 'replays': 0}
    empty = {name: 0 for name in work}
    one_bill = {c: {'requested': amount, 'paid': amount, 'unpaid': 0.0}
                for c, amount in (('energy', 0.02), ('vigilance', 0.05))}
    no_bill = {c: {'requested': 0.0, 'paid': 0.0, 'unpaid': 0.0}
               for c in ('energy', 'vigilance')}
    trace_head = sha256(json.dumps([life['genome'], life['world'], life['life_seed'],
                                    life['horizon']], separators=(',', ':')).encode()).hexdigest()
    evidence_head = life['manifest_id']
    before = [60.0] * 5
    trace = []
    for t in range(1, 401):
        after = before[:]
        after[0] -= 0.02
        after[4] -= 0.05
        phase = {
            'decision': {'work': deepcopy(work), 'accounting': deepcopy(one_bill),
                         'body_before': before[:], 'body_after_debit': after[:]},
            'learning': {'work': deepcopy(empty), 'accounting': deepcopy(no_bill),
                         'body_before': after[:], 'body_after_debit': after[:]},
        }
        base = {'t': t, 'action': None, 'param': None, 'option': None,
                'body': after[:], 'pos': [0, 0], 'dead': []}
        trace_head = sha256((trace_head + json.dumps(base, separators=(',', ':'),
                                                    sort_keys=True)).encode()).hexdigest()
        evidence_head = v.custody._digest({
            'previous': evidence_head, 'record': base,
            'work': work, 'accounting': one_bill, 'funding_phases': phase})
        trace.append({**base, 'cognitive_work': deepcopy(work),
                      'cognitive_accounting': deepcopy(one_bill),
                      'funding_phases': phase,
                      'info': {'not_evidence': 'arbitrary observer-only text'}})
        before = after[:]
    totals = {c: {'requested': amount * 400, 'paid': amount * 400, 'unpaid': 0.0}
              for c, amount in (('energy', 0.02), ('vigilance', 0.05))}
    life['cognitive_accounting'] = {
        'schema': 'i3-cognitive-funding/v2', 'status': 'SETTLED_FOR_DECLARED_WORK',
        'totals': totals, 'shortfall_steps': 0, 'pending_replays': 0,
        'pending_energy': 0.0, 'pending_vigilance': 0.0,
        'learning_updates': 0, 'replays_executed': 0, 'inactive_steps': 400,
    }
    life['trace'] = trace
    life['trace_head'] = trace_head
    life['evidence_head'] = v.custody._digest({
        'previous': evidence_head, 'terminal': life['terminal'],
        'accounting': life['cognitive_accounting']})
    life['actions'] = {'physical_inactivity': 400}
    life['drinks'] = life['meals'] = 0
    life['first_drink_step'] = None
    life['final_body'] = [round(x, 6) for x in before]
    return identity, life, source_pin


class NativeTraceFundingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = fabricated_traced_life()

    def audit(self, identity=None, life=None, source_pin=None):
        iid, original, pin = deepcopy(self.baseline)
        return v.inspect_traced_life(
            identity if identity is not None else iid,
            life if life is not None else original,
            expected_protocol='FAKE_NATIVE_SHAPE_NOT_APPROVED',
            source_pin=source_pin or pin, source_head='c'*40)

    def negative(self, operation):
        iid, life, pin = deepcopy(self.baseline)
        operation(iid, life)
        with self.assertRaises((ValueError, PermissionError)):
            self.audit(iid, life, pin)

    def test_source_parity_with_fabricated_full_trace_without_world(self):
        result = self.audit()
        self.assertEqual(result['trace_steps_checked'], 400)
        self.assertEqual(result['status'], 'SUPPLIED_TRACE_TWO_CURRENCY_CHAIN_MATCH_NOT_ATTESTED')
        self.assertTrue(result['trace_head_recomputed'])
        self.assertTrue(result['funding_evidence_head_recomputed'])
        for key in ('trace_info_cryptographically_authenticated',
                    'motor_decision_causality_or_world_physics_replayed',
                    'independent_original_source_and_time_attested',
                    'owner_authorization'):
            self.assertIs(result[key], False)
        self.assertEqual(result['new_lives_created'], 0)
        self.assertEqual(result['new_worlds_opened'], 0)

    def test_missing_or_truncated_trace_fails_closed(self):
        self.negative(lambda i, x: x.pop('trace'))
        self.negative(lambda i, x: x['trace'].pop())

    def test_reordered_trace_or_missing_funding_phase_denied(self):
        self.negative(lambda i, x: x['trace'][1].update({'t': 1}))
        self.negative(lambda i, x: x['trace'][1]['funding_phases'].pop('learning'))

    def test_changed_trace_body_position_or_action_denied(self):
        self.negative(lambda i, x: x['trace'][10]['body'].__setitem__(1, 52.0))
        self.negative(lambda i, x: x['trace'][20]['pos'].__setitem__(0, 99))
        self.negative(lambda i, x: x['trace'][15].update({'action': 'attendre'}))

    def test_cognitive_work_and_currency_cost_forgery_denied(self):
        self.negative(lambda i, x: x['trace'][5]['cognitive_work'].__setitem__('cycles', 0))
        self.negative(lambda i, x: x['trace'][9]['funding_phases']['decision']['accounting']['vigilance'].__setitem__('paid', 0.0))
        self.negative(lambda i, x: x['trace'][15]['funding_phases']['decision']['work'].__setitem__('cycles', 2))
        self.negative(lambda i, x: x['trace'][25]['funding_phases']['learning']['body_after_debit'].__setitem__(1, 4.0))
        self.negative(lambda i, x: x['trace'][99]['cognitive_accounting']['energy'].__setitem__('paid', 0.0))

    def test_terminal_evidence_or_genome_forgery_denied(self):
        self.negative(lambda i, x: x.update({'trace_head': '0'*64}))
        self.negative(lambda i, x: x.update({'evidence_head': '0'*64}))
        self.negative(lambda i, x: x['manifest']['genome']['genes'].__setitem__('beta_u', 1.5))

    def test_life_aggregate_and_final_state_forgery_denied(self):
        self.negative(lambda i, x: x['cognitive_accounting']['totals']['energy'].__setitem__('paid', 1.0))
        self.negative(lambda i, x: x['actions'].__setitem__('physical_inactivity', 399))
        self.negative(lambda i, x: x['final_body'].__setitem__(0, 0.0))
        self.negative(lambda i, x: x.update({'first_drink_step': 14}))

    def test_uncommitted_trace_info_must_never_be_used_as_evidence(self):
        iid, life, pin = deepcopy(self.baseline)
        life['trace'][5]['info'] = {'changed_after_hash': 'not authenticated'}
        result = self.audit(iid, life, pin)
        self.assertIs(result['trace_info_cryptographically_authenticated'], False)

    def test_refuse_unfunded_or_extra_schema_fields(self):
        self.negative(lambda i, x: x['trace'][5]['funding_phases']['decision']['accounting']['energy'].__setitem__('unpaid', .1))
        self.negative(lambda i, x: x['trace'][5].update({'oracle': 'hidden-world'}))
        self.negative(lambda i, x: x['trace'][5]['funding_phases']['decision']['body_before'].__setitem__(0, float('nan')))

    def test_inert_method_and_no_live_surface(self):
        with patch.object(v.custody, '_assert_inert', side_effect=PermissionError):
            with self.assertRaises(PermissionError):
                self.audit()
        for f in (v.run_life, v.open_world, v.authorize_science):
            with self.assertRaises(PermissionError):
                f()
        src = inspect.getsource(v)
        names = []
        for node in ast.walk(ast.parse(src)):
            if isinstance(node, ast.Import):
                names.extend(a.name for a in node.names)
            elif isinstance(node, ast.ImportFrom):
                names.append(node.module or '')
        self.assertFalse(any(n.startswith(('i3.modules', 'i3.runtime')) for n in names))


if __name__ == '__main__':
    unittest.main()
