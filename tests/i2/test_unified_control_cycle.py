"""I2 offline full-cycle + Action Control custody: no live owner or motor action."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import fields
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from i2.modules.action_control_boundary import SafetyFinding  # noqa: E402
from i2.modules.cognitive_cycle_fixture import (  # noqa: E402
    CognitiveCycleFixture, CycleReceipt, SCHEMA, _chain, _json,
    FaultInjected, CommitAcknowledgmentLost,
)
from i2.modules.action_control_custody_fixture import FaultInjected as ControlFaultInjected  # noqa: E402
from i2.modules.competition_preview import SubjectiveValuation  # noqa: E402
from i2.modules.intention_continuity import FirstPersonCapture  # noqa: E402
from i2.modules.intention_ingress import ObservationClaim  # noqa: E402

LIFE = "life:synthetic-all-in-one"
A = "affordance:collect:berry_a"
B = "affordance:eat:berry_a"
C = "affordance:drink:water"


def claim(step=3, *, life=LIFE, visible=(A, B, C), goal="goal:food"):
    return ObservationClaim(
        life, FirstPersonCapture(step, f"capture:{step}", goal, tuple(sorted(visible))),
        f"source:event:{step}", (f"evidence:{step}",),
    )


class ObservationPort:
    def __init__(self):
        self.known = set()
        self.calls = []
        self.override = None

    def add(self, c):
        self.known.add(c.digest())
        return c

    def verify(self, *, life_ref, claim, digest):
        self.calls.append((life_ref, digest))
        return (digest in self.known and life_ref == LIFE) if self.override is None else self.override


class Values:
    def __init__(self, scores=None):
        self.scores = {B: 5} if scores is None else scores
        self.calls = []
        self.throw = False

    def evaluate_batch(self, *, frame, receipts):
        self.calls.append((frame.frame_ref, len(receipts)))
        if self.throw:
            raise ValueError("subjective synthetic source unavailable")
        return tuple(SubjectiveValuation(c.candidate_ref, r.ref,
                                        f"value:source:{i}", self.scores.get(c.semantic_ref, 0))
                     for i, (c, r) in enumerate(zip(frame.candidates, receipts)))


class Current:
    def __init__(self):
        self.calls = []
        self.result = True
        self.fail_after_first = False

    def verify_current(self, *, life_ref, frame, advice):
        self.calls.append((life_ref, frame.capture_ref, advice.status))
        if self.fail_after_first and len(self.calls) > 1:
            return False
        return self.result


class Safety:
    def __init__(self, veto=False):
        self.veto = veto
        self.calls = []
        self.mutate = None
        self.throw = False

    def check(self, *, life_ref, frame, candidate_ref, control_receipt_ref):
        self.calls.append((life_ref, frame.capture_ref, candidate_ref, control_receipt_ref))
        if self.throw:
            raise ValueError("synthetic safety unavailable")
        result = SafetyFinding(life_ref, frame.frame_ref, frame.capture_ref,
                               candidate_ref, control_receipt_ref, self.veto,
                               "source:simulated-safety")
        return result if self.mutate is None else self.mutate(result)


class Terminal:
    def verify_terminal(self, **kwargs):
        return True


class UnifiedCognitionAndControl(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db = Path(self.temp.name) / "cycle.sqlite"
        self.source = ObservationPort()
        self.values = Values()
        self.current = Current()
        self.safety = Safety()

    def make(self, capacity=20):
        params = dict(path=self.db, life_ref=LIFE, synthetic_uc=capacity,
                      observation_source=self.source, valuation_source=self.values)
        params.update(current_source=self.current, safety_source=self.safety,
                      genesis_ref="genesis:unified-control", terminal_source=Terminal())
        return CognitiveCycleFixture.create(**params)

    def reopen(self):
        params = dict(path=self.db, life_ref=LIFE,
                      observation_source=self.source, valuation_source=self.values)
        params.update(current_source=self.current, safety_source=self.safety,
                      genesis_ref="genesis:unified-control", terminal_source=Terminal())
        return CognitiveCycleFixture.reopen(**params)

    def first(self, instance, *, at=3, visible=(A,B,C), fault=None):
        c = self.source.add(claim(at, visible=visible))
        return instance.open(claim=c, semantic_ref=A,
                             evidence_ref=f"evidence:{at}", ttl_steps=12,
                             _fault_at=fault)

    def event(self):
        with sqlite3.connect(self.db) as conn:
            body = conn.execute("SELECT event_json FROM events WHERE seq=1").fetchone()[0]
        return json.loads(body)

    def tamper(self, change):
        with sqlite3.connect(self.db) as conn:
            body, previous = conn.execute(
                "SELECT event_json,previous_hash FROM events WHERE seq=1").fetchone()
            record = json.loads(body)
            change(record)
            new_text = _json(record)
            head = _chain(previous, new_text, schema=SCHEMA)
            conn.execute("UPDATE events SET event_json=?,event_hash=? WHERE seq=1",
                         (new_text, head))
            conn.execute("UPDATE account SET chain_head=? WHERE id=1", (head,))

    def test_single_commit_bills_intent_competition_and_control(self):
        f = self.make()
        r = self.first(f)
        self.assertEqual((r.intake_uc,r.competition_uc,r.control_uc), (1,3,1))
        self.assertEqual(r.competition_status,"ADVISORY_ONLY")
        self.assertEqual(r.control_status,"REVIEWED_NOT_ADMITTED")
        self.assertEqual(r.motor_authority,"NONE")
        self.assertEqual(r.control_suggested_candidate_ref,r.suggested_candidate_ref)
        self.assertTrue(r.control_receipt_ref.startswith("synthetic:control:"))
        self.assertEqual(f.audit()["remaining_synthetic_uc"],15)
        self.assertEqual(f.audit()["committed"],1)
        self.assertTrue(f.audit()["control_review_included"])
        self.assertEqual(f.audit()["schema"], SCHEMA)
        self.assertEqual(len(self.current.calls),2)
        self.assertEqual(len(self.safety.calls),1)
        self.assertEqual(self.event()["control_review"]["motor_authority"],"NONE")
        self.assertEqual(f.lookup(capture_ref="capture:3"),r)

    def test_three_stages_pay_from_same_account_and_end_below_budget(self):
        f = self.make(capacity=10)
        first = self.first(f)
        c4 = self.source.add(claim(4))
        second = f.observe(claim=c4)
        self.assertEqual((first.control_uc,second.control_uc),(1,1))
        self.assertEqual(f.audit()["remaining_synthetic_uc"],0)
        self.assertEqual(f.audit()["committed"],2)
        self.assertNotEqual(first.control_receipt_ref, second.control_receipt_ref)

    def test_exact_budget_funds_control_and_never_produces_motor(self):
        f = self.make(capacity=5)
        r = self.first(f)
        self.assertEqual((r.intake_uc,r.competition_uc,r.control_uc),(1,3,1))
        self.assertEqual(f.audit()["remaining_synthetic_uc"],0)
        forbidden = {"command","dispatch","execute","admit","admit_motor","birth","world"}
        self.assertFalse(any(hasattr(f,n) for n in forbidden))
        self.assertFalse(forbidden.intersection({fld.name for fld in fields(CycleReceipt)}))

    def test_control_unfunded_after_complete_competition_no_partial_charge(self):
        f = self.make(capacity=4)
        r = self.first(f)
        self.assertEqual((r.intake_uc,r.competition_uc,r.control_uc),(1,3,0))
        self.assertEqual(r.control_status,"UNFUNDED")
        self.assertIsNone(r.control_suggested_candidate_ref)
        self.assertIsNone(r.control_receipt_ref)
        self.assertEqual(len(self.safety.calls),0)
        self.assertEqual(f.audit()["remaining_synthetic_uc"],0)

    def test_competition_unfunded_never_charges_control(self):
        f = self.make(capacity=2)
        r = self.first(f)
        self.assertEqual((r.competition_status,r.control_status),("UNFUNDED","NO_ADVICE"))
        self.assertEqual((r.intake_uc,r.competition_uc,r.control_uc),(1,0,0))
        self.assertEqual(len(self.safety.calls),0)
        self.assertEqual(f.audit()["remaining_synthetic_uc"],1)

    def test_no_candidates_and_no_advice_do_not_call_veto(self):
        f = self.make(capacity=5)
        c = self.source.add(claim(3,visible=()))
        r = f.observe(claim=c)
        self.assertEqual((r.competition_status,r.control_status),("NO_CANDIDATES","NO_ADVICE"))
        self.assertEqual((r.intake_uc,r.competition_uc,r.control_uc),(1,0,0))
        self.assertEqual(len(self.safety.calls),0)

    def test_equal_valuations_do_not_call_veto(self):
        self.values.scores = {A:4,B:4}
        f = self.make(capacity=8)
        r = self.first(f)
        self.assertEqual((r.competition_status,r.control_status),("AMBIGUOUS","NO_ADVICE"))
        self.assertEqual((r.intake_uc,r.competition_uc,r.control_uc),(1,3,0))
        self.assertEqual(len(self.safety.calls),0)

    def test_negative_values_do_not_create_motor_or_review_debit(self):
        self.values.scores = {}
        f = self.make(capacity=8)
        r = self.first(f)
        self.assertEqual(r.control_status,"NO_ADVICE")
        self.assertEqual(r.control_uc,0)
        self.assertIsNone(r.control_receipt_ref)

    def test_independent_veto_always_masks_candidate(self):
        self.safety.veto = True
        f = self.make()
        r = self.first(f)
        self.assertEqual(r.control_status,"VETOED")
        self.assertIsNone(r.control_suggested_candidate_ref)
        self.assertEqual(r.control_uc,1)
        self.assertEqual(r.motor_authority,"NONE")
        self.assertEqual(self.event()["control_review"]["suggested_candidate_ref"],None)
        self.assertEqual(len(self.safety.calls),1)

    def test_intention_policy_rejected_pays_only_intake_and_no_review(self):
        f = self.make(capacity=10)
        first = self.first(f)
        c4 = self.source.add(claim(4))
        r = f.open(claim=c4,semantic_ref=A,evidence_ref="evidence:4",ttl_steps=3)
        self.assertEqual(r.intention_kind,"policy_rejected")
        self.assertIsNone(r.control_status)
        self.assertEqual((r.intake_uc,r.competition_uc,r.control_uc),(1,0,0))
        self.assertIsNone(r.control_suggested_candidate_ref)
        self.assertEqual(self.event()["control_uc"],first.control_uc)
        self.assertEqual(f.audit()["remaining_synthetic_uc"],4)

    def test_control_mode_exhausted_intention_refuses_before_any_publication(self):
        f = self.make(capacity=0)
        with self.assertRaises(ValueError):
            self.first(f)
        self.assertEqual(f.audit()["remaining_synthetic_uc"], 0)
        self.assertEqual(f.audit()["committed"], 0)
        self.assertEqual(self.current.calls, [])
        self.assertEqual(self.safety.calls, [])

    def test_reopen_requires_same_mode_and_external_ports(self):
        f = self.make()
        self.first(f)
        again = self.reopen()
        self.assertEqual(again.audit()["committed"],1)
        self.assertEqual(again.lookup(capture_ref="capture:3"),f.lookup(capture_ref="capture:3"))

    def test_missing_current_or_safety_port_fails_before_creating_db(self):
        bad = (dict(current_source=object()),
               dict(safety_source=object()),
               dict(terminal_source=object()))
        for override in bad:
            with self.subTest(override=override):
                params=dict(path=self.db, life_ref=LIFE,synthetic_uc=9,
                            observation_source=self.source,valuation_source=self.values,
                            current_source=self.current,safety_source=self.safety,
                            genesis_ref="genesis:unified-control",terminal_source=Terminal())
                params.update(override)
                with self.assertRaises(ValueError): CognitiveCycleFixture.create(**params)
                self.assertFalse(self.db.exists())

    def test_false_current_source_blocks_entire_cycle(self):
        self.current.result = False
        f = self.make()
        with self.assertRaises(ValueError):self.first(f)
        self.assertEqual(f.audit()["committed"],0)
        self.assertEqual(f.audit()["remaining_synthetic_uc"],20)
        self.assertEqual(self.safety.calls,[])

    def test_lost_current_after_veto_rolls_back_every_debit(self):
        self.current.fail_after_first = True
        f = self.make()
        with self.assertRaises(ValueError):self.first(f)
        self.assertEqual(f.audit()["remaining_synthetic_uc"],20)
        self.assertEqual(f.audit()["committed"],0)
        self.assertEqual(len(self.safety.calls),1)

    def test_truthy_nonbool_source_cannot_grant_context(self):
        self.current.result=1
        f = self.make()
        with self.assertRaises(ValueError):self.first(f)
        self.assertEqual(f.audit()["committed"],0)

    def test_observation_attestation_rejection_blocks_control_and_intake(self):
        f=self.make()
        with self.assertRaises(ValueError):
            f.open(claim=claim(3),semantic_ref=A,evidence_ref="evidence:3",ttl_steps=8)
        self.assertEqual(f.audit()["committed"],0)
        self.assertEqual(self.safety.calls,[])

    def test_foreign_life_rejected_even_if_observation_port_whitelists(self):
        f=self.make()
        bad=self.source.add(claim(3,life="life:other"))
        with self.assertRaises(ValueError):
            f.open(claim=bad,semantic_ref=A,evidence_ref="evidence:3",ttl_steps=8)
        self.assertEqual(f.audit()["committed"],0)

    def test_safety_source_failure_rolls_back_intent_and_competition(self):
        self.safety.throw=True
        f=self.make()
        with self.assertRaises(ValueError):self.first(f)
        self.assertEqual(f.audit()["committed"],0)
        self.assertEqual(f.audit()["remaining_synthetic_uc"],20)

    def test_forged_veto_identity_or_receipt_ref_is_refused(self):
        from dataclasses import replace
        transforms=(lambda x:replace(x,life_ref="life:alien"),
                    lambda x:replace(x,frame_ref="frame:i2:alien"),
                    lambda x:replace(x,capture_ref="capture:alien"),
                    lambda x:replace(x,candidate_ref="candidate:i2:alien"),
                    lambda x:replace(x,control_receipt_ref="fake:receipt"),
                    lambda x:replace(x,veto=1),
                    lambda x:replace(x,evidence_ref="bad evidence"))
        for mutation in transforms:
            with self.subTest(mutation=mutation):
                self.safety.mutate=mutation
                f=self.make()
                with self.assertRaises(ValueError):self.first(f)
                self.assertEqual(f.audit()["committed"],0)
                self.db.unlink()

    def test_injected_failures_before_commit_rollback_all_three_stages(self):
        for fault in ("after_intake_debit","after_intention","after_competition_debit",
                      "after_control_debit","after_safety","before_commit"):
            with self.subTest(fault=fault):
                f=self.make()
                with self.assertRaises((FaultInjected,ControlFaultInjected)):self.first(f,fault=fault)
                self.assertEqual((f.audit()["remaining_synthetic_uc"],f.audit()["committed"]),(20,0))
                self.assertIsNone(f.lookup(capture_ref="capture:3"))
                self.db.unlink()

    def test_lost_ack_after_commit_is_resolved_without_any_new_port_call(self):
        f=self.make()
        with self.assertRaises(CommitAcknowledgmentLost):self.first(f,fault="after_commit")
        old=(len(self.source.calls),len(self.values.calls),len(self.current.calls),len(self.safety.calls))
        ack=self.reopen().lookup(capture_ref="capture:3")
        self.assertEqual((ack.intake_uc,ack.competition_uc,ack.control_uc),(1,3,1))
        self.assertEqual((len(self.source.calls),len(self.values.calls),len(self.current.calls),len(self.safety.calls)),old)
        with self.assertRaises(ValueError):self.first(f)
        self.assertEqual(f.audit()["remaining_synthetic_uc"],15)

    def test_cross_instance_same_capture_charged_only_once(self):
        f=self.make()
        g=self.reopen()
        obs=self.source.add(claim(3))
        def attempt(instance):
            try:
                return instance.open(claim=obs,semantic_ref=A,evidence_ref="evidence:3",ttl_steps=12).control_status
            except ValueError:
                return "REPLAY_REJECTED"
        with ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(attempt,(f,g)))
        self.assertCountEqual(results,["REVIEWED_NOT_ADMITTED","REPLAY_REJECTED"])
        self.assertEqual(f.audit()["committed"],1)
        self.assertEqual(f.audit()["remaining_synthetic_uc"],15)

    def test_stale_capture_after_newer_one_refused_without_debit(self):
        f=self.make(capacity=12)
        self.first(f,at=4)
        obs=self.source.add(claim(3))
        with self.assertRaises(ValueError):
            f.open(claim=obs,semantic_ref=A,evidence_ref="evidence:3",ttl_steps=12)
        self.assertEqual(f.audit()["remaining_synthetic_uc"],7)

    def test_tampered_control_debit_detected_even_with_recomputed_hashes(self):
        f=self.make()
        self.first(f)
        self.tamper(lambda v:v.__setitem__("control_uc",0))
        with self.assertRaises(ValueError):f.audit()

    def test_tampered_safety_veto_detected_even_with_recomputed_hashes(self):
        f=self.make()
        self.first(f)
        self.tamper(lambda v:v["safety_finding"].__setitem__("veto",True))
        with self.assertRaises(ValueError):f.audit()

    def test_tampered_control_receipt_ref_detected_even_with_recomputed_hashes(self):
        f=self.make()
        self.first(f)
        self.tamper(lambda v:v["control_receipt"].__setitem__("ref","bad:receipt"))
        with self.assertRaises(ValueError):f.audit()

    def test_tampered_control_cost_type_detected_even_with_recomputed_hashes(self):
        f=self.make()
        self.first(f)
        self.tamper(lambda v:v.__setitem__("control_uc",True))
        with self.assertRaises(ValueError):f.audit()

    def test_tampered_review_motor_authority_detected_even_with_recomputed_hashes(self):
        f=self.make()
        self.first(f)
        self.tamper(lambda v:v["control_review"].__setitem__("motor_authority","ALLOWED"))
        with self.assertRaises(ValueError):f.audit()

    def test_tampered_account_balance_detected(self):
        f=self.make()
        self.first(f)
        with sqlite3.connect(self.db) as conn:
            conn.execute("UPDATE account SET remaining_uc=remaining_uc+1 WHERE id=1")
        with self.assertRaises(ValueError):f.audit()

    def test_audit_never_contacts_external_current_safety_or_values(self):
        f=self.make()
        self.first(f)
        prior=(len(self.source.calls),len(self.values.calls),len(self.current.calls),len(self.safety.calls))
        reopened=self.reopen()
        reopened.audit()
        reopened.lookup(capture_ref="capture:3")
        self.assertEqual(prior,(len(self.source.calls),len(self.values.calls),len(self.current.calls),len(self.safety.calls)))


if __name__ == "__main__":
    unittest.main()
