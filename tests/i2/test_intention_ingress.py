"""Boundary contract tests with deliberately synthetic port substitutes.

A synthetic port is NOT an M11 source, a real Scheduler UC ledger or a life.
"""
from dataclasses import replace, fields
from pathlib import Path
import copy
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from i2.modules.intention_continuity import FirstPersonCapture  # noqa: E402
from i2.modules.intention_ingress import (  # noqa: E402
    ObservationClaim, UCReceipt, IntentionIngress, INTAKE_OPERATION, INTAKE_UC,
)

LIFE = 'life:synthetic-one'
SEM = 'affordance:berry_a'
GOAL = 'goal:food'


def claim(step, *, life=LIFE, semantic=SEM, visible=True,
          contradicted=False, goal=GOAL, evidence='evidence:lived'):
    return ObservationClaim(
        life_ref=life,
        capture=FirstPersonCapture(
            step=step, ref=f'capture:{step}', goal_ref=goal,
            accessible_semantics=(semantic,) if visible else (),
            contradicted_semantics=(semantic,) if contradicted else (),
        ),
        source_event_ref=f'source:physical:{step}',
        subjective_evidence_refs=(evidence,),
    )


class SyntheticObservationPort:
    """Unprivileged test fake, not a provenance attester."""
    def __init__(self):
        self.allowed = set()
        self.calls = []
        self.override = None

    def admit_for_test(self, value):
        self.allowed.add(value.digest())

    def verify(self, *, life_ref, claim, digest):
        self.calls.append((life_ref, digest))
        if self.override is not None:
            return self.override
        return digest in self.allowed


class SyntheticDebitPort:
    """Finite in-memory mock; no UC deducted from a living scheduler."""
    def __init__(self, balance=8):
        self.balance = balance
        self.calls = []
        self.issued = []
        self.override = None

    def debit(self, *, life_ref, capture_ref, claim_digest, operation, units):
        self.calls.append((life_ref, capture_ref, claim_digest, operation, units))
        if units > self.balance:
            return None
        self.balance -= units
        receipt = UCReceipt(
            ref=f'synthetic-charge:{len(self.issued) + 1}',
            life_ref=life_ref, capture_ref=capture_ref, claim_digest=claim_digest,
            operation=operation, units=units,
        )
        self.issued.append(receipt)
        return self.override(receipt) if self.override is not None else receipt


def setup(balance=8):
    source = SyntheticObservationPort()
    budget = SyntheticDebitPort(balance)
    gateway = IntentionIngress(life_ref=LIFE, observation_authority=source,
                               uc_authority=budget)
    return gateway, source, budget


def opened():
    gate, source, budget = setup()
    a = claim(3)
    source.admit_for_test(a)
    event = gate.open(claim=a, semantic_ref=SEM, evidence_ref='evidence:lived', ttl_steps=8)
    assert event.kind == 'opened'
    return gate, source, budget


class TestIntentionIngress(unittest.TestCase):
    def test_no_default_authority_or_birth_port(self):
        for src, uc in ((None, SyntheticDebitPort()), (SyntheticObservationPort(), None)):
            with self.assertRaises(ValueError):
                IntentionIngress(life_ref=LIFE, observation_authority=src, uc_authority=uc)
        gate, _, _ = setup()
        for forbidden in ('birth', 'run_step', 'dispatch', 'admit_motor', 'command', 'winner'):
            self.assertFalse(hasattr(gate, forbidden))

    def test_open_bound_to_capture_evidence_and_paid_external_receipt(self):
        gate, src, uc = opened()
        self.assertEqual(gate.current.goal_ref, GOAL)
        self.assertEqual(gate.current.origin_evidence_ref, 'evidence:lived')
        self.assertEqual(gate.current.created_step, 3)
        self.assertEqual(len(src.calls), 1)
        self.assertEqual(uc.balance, 7)
        self.assertEqual(uc.calls[0][3:], (INTAKE_OPERATION, INTAKE_UC))
        self.assertEqual(uc.calls[0][2], claim(3).digest())
        self.assertNotIn('accumulator', gate.inspect_proposal_state()['current'])

    def test_observe_retains_suspends_and_resumes_without_motor(self):
        gate, src, uc = opened()
        for step, visible, expected in ((4, True, 'retained'), (5, False, 'suspended'),
                                         (6, False, 'still_suspended'), (7, True, 'resumed')):
            c = claim(step, visible=visible)
            src.admit_for_test(c)
            t = gate.observe(claim=c)
            self.assertEqual(t.kind, expected)
            self.assertEqual(t.work_ref, uc.issued[-1].ref)
        self.assertEqual(uc.balance, 3)
        self.assertEqual(gate.current.created_step, 3)
        self.assertEqual(gate.current.last_checked_step, 7)

    def test_claim_digest_exactly_binds_capture_and_evidence(self):
        c = claim(3)
        variants = (
            replace(c, life_ref='life:other'),
            replace(c, source_event_ref='source:alternate'),
            replace(c, subjective_evidence_refs=('evidence:changed',)),
            replace(c, capture=replace(c.capture, goal_ref='goal:thirst')),
            replace(c, capture=replace(c.capture, accessible_semantics=())),
            replace(c, capture=replace(c.capture, ref='capture:other')),
        )
        for v in variants:
            with self.subTest(v=v):
                self.assertNotEqual(v.digest(), c.digest())

    def test_source_port_rejects_unattested_frames_before_debit(self):
        gate, src, uc = setup()
        with self.assertRaises(ValueError):
            gate.open(claim=claim(3),semantic_ref=SEM,evidence_ref='evidence:lived',ttl_steps=5)
        self.assertEqual(uc.calls, [])
        self.assertIsNone(gate.current)
        self.assertEqual(src.calls[0][1], claim(3).digest())

    def test_truthy_nonboolean_source_decision_rejected(self):
        gate, src, uc = setup()
        src.override = 1
        with self.assertRaises(ValueError):
            gate.observe(claim=claim(3))
        self.assertEqual(uc.calls, [])

    def test_foreign_life_rejected_before_source_or_charge(self):
        gate, src, uc = setup()
        c = claim(3,life='life:other')
        src.admit_for_test(c)
        with self.assertRaises(ValueError):
            gate.observe(claim=c)
        self.assertEqual(src.calls, [])
        self.assertEqual(uc.calls, [])

    def test_origin_evidence_must_be_in_claim_before_port_use(self):
        gate, src, uc = setup()
        c = claim(3)
        src.admit_for_test(c)
        with self.assertRaises(ValueError):
            gate.open(claim=c,semantic_ref=SEM,evidence_ref='evidence:unseen',ttl_steps=5)
        self.assertEqual(src.calls, [])
        self.assertEqual(uc.calls, [])

    def test_invalid_claim_canonicality_rejected_pre_admission(self):
        gate, src, uc = setup()
        variants = (
            replace(claim(3), subjective_evidence_refs=('z', 'a')),
            replace(claim(3), subjective_evidence_refs=()),
            replace(claim(3), subjective_evidence_refs=('a', 'a')),
            replace(claim(3), capture=replace(claim(3).capture, step=True)),
            replace(claim(3), capture=replace(claim(3).capture, accessible_semantics=('z','a'))),
        )
        for v in variants:
            with self.subTest(v=v), self.assertRaises(ValueError):
                gate.observe(claim=v)
        self.assertEqual(src.calls, [])
        self.assertEqual(uc.calls, [])

    def test_insufficient_uc_fail_closed_and_no_owner_mutation(self):
        gate, src, uc = setup(balance=0)
        c=claim(3)
        src.admit_for_test(c)
        before=copy.deepcopy(gate.inspect_proposal_state())
        with self.assertRaises(ValueError):
            gate.open(claim=c,semantic_ref=SEM,evidence_ref='evidence:lived',ttl_steps=5)
        self.assertEqual(uc.balance,0)
        self.assertEqual(gate.inspect_proposal_state(),before)

    def test_receipt_must_bind_all_fields(self):
        mutations = (
            lambda r: replace(r, life_ref='life:other'),
            lambda r: replace(r, capture_ref='capture:other'),
            lambda r: replace(r, claim_digest='0'*64),
            lambda r: replace(r, operation='wrong_operation'),
            lambda r: replace(r, units=2),
            lambda r: replace(r, units=True),
            lambda r: replace(r, ref='bad ref'),
        )
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                gate, src, uc = setup()
                c=claim(3)
                src.admit_for_test(c)
                uc.override=mutate
                before=gate.inspect_proposal_state()
                with self.assertRaises(ValueError):
                    gate.observe(claim=c)
                self.assertEqual(gate.inspect_proposal_state(),before)

    def test_missing_uc_receipt_refuses(self):
        gate, src, uc=setup()
        c=claim(3)
        src.admit_for_test(c)
        uc.override=lambda r: False
        with self.assertRaises(ValueError):
            gate.observe(claim=c)
        self.assertIsNone(gate.current)

    def test_reused_uc_receipt_never_applies_second_consultation(self):
        gate, src, uc=opened()
        c=claim(4)
        src.admit_for_test(c)
        uc.override=lambda r: replace(r,ref=uc.issued[0].ref)
        before=copy.deepcopy(gate.inspect_proposal_state())
        with self.assertRaises(ValueError):
            gate.observe(claim=c)
        self.assertEqual(gate.inspect_proposal_state(),before)

    def test_same_capture_replay_is_rejected_before_second_charge(self):
        gate, src, uc = opened()
        before=len(uc.calls)
        with self.assertRaises(ValueError):
            gate.observe(claim=claim(3))
        self.assertEqual(len(uc.calls), before)

    def test_past_capture_ref_reuse_after_later_step_rejected(self):
        gate, src, uc = opened()
        second = claim(4)
        src.admit_for_test(second)
        gate.observe(claim=second)
        bad = replace(claim(5), capture=replace(claim(5).capture, ref='capture:3'))
        src.admit_for_test(bad)
        with self.assertRaises(ValueError):
            gate.observe(claim=bad)
        self.assertEqual(len(uc.calls),2)

    def test_invalid_open_attempt_is_paid_once_even_if_owner_refuses(self):
        gate, src, uc = opened()
        c=claim(4)
        src.admit_for_test(c)
        with self.assertRaises(ValueError):
            gate.open(claim=c,semantic_ref=SEM,evidence_ref='evidence:lived',ttl_steps=3)
        self.assertEqual(uc.balance,6)
        self.assertEqual(gate.current.last_checked_step,3)
        with self.assertRaises(ValueError):
            gate.open(claim=c,semantic_ref=SEM,evidence_ref='evidence:lived',ttl_steps=3)
        self.assertEqual(uc.balance,6)

    def test_bad_ttl_and_semantic_are_free_syntactic_preflight(self):
        gate, src, uc=setup()
        c=claim(3)
        src.admit_for_test(c)
        for ttl, sem in ((0,SEM),(True,SEM),(5,'bad ref')):
            with self.subTest(ttl=ttl,sem=sem),self.assertRaises(ValueError):
                gate.open(claim=c,semantic_ref=sem,evidence_ref='evidence:lived',ttl_steps=ttl)
        self.assertEqual(uc.calls,[])

    def test_no_birth_engine_m11_recovery_or_motor_state(self):
        gate, src, uc=opened()
        s=gate.inspect_proposal_state()
        self.assertEqual(set(s),{'policy','last_step','last_capture_ref','current'})
        for field in ('command','winner','accumulator','threshold','motor','option_ref','admission'):
            self.assertNotIn(field,repr(s))
        self.assertFalse(hasattr(gate,'cold_recover'))
        self.assertFalse(hasattr(gate,'step'))
        self.assertFalse(hasattr(gate,'world'))

    def test_no_individual_can_be_inferred_from_synthetic_port(self):
        gate, src, uc=opened()
        self.assertEqual(gate.current.origin_capture_ref,'capture:3')
        self.assertNotIn('m11',gate.inspect_proposal_state())
        self.assertFalse(hasattr(gate, 'birth'))

if __name__=='__main__':
    unittest.main()