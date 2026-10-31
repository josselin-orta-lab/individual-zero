"""Inert Action Control-boundary tests: synthetic sources, no birth or motor."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import fields, replace
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from i2.modules.option_reconstruction import CandidateFrame, SemanticCandidate, _bound_id  # noqa: E402
from i2.modules.competition_preview import CompetitionAdvice, SubjectiveValuation  # noqa: E402
from i2.modules.action_control_boundary import (  # noqa: E402
    ActionControlBoundary, ControlReceipt, SafetyFinding, ControlReview,
    CONTROL_OPERATION, CONTROL_UC,
)

LIFE = "life:i2-test"
SEMANTICS = tuple(sorted(("affordance:collect:berry_a", "affordance:eat:berry_a",
                          "affordance:drink:water")))
DIGEST = "a" * 64


def frame(step=3, *, life=LIFE, semantics=SEMANTICS, tagged=False, capture_ref=None):
    candidates = tuple(SemanticCandidate(
        _bound_id("candidate", life, DIGEST, semantic), semantic,
        "intent:i2:" + "f" * 64 if tagged and semantic == semantics[0] else None,
    ) for semantic in semantics)
    return CandidateFrame(
        frame_ref="frame:i2:" + f"{step:064x}", life_ref=life,
        capture_ref=capture_ref or f"capture:{step}", physical_step=step,
        claim_digest=DIGEST, work_correlation_ref=f"correlation:{step}",
        candidates=candidates,
    )


def advice(f, *, scores=None, status=None):
    scores = scores if scores is not None else {SEMANTICS[1]: 4}
    names = tuple(item.candidate_ref for item in f.candidates)
    if not names:
        return CompetitionAdvice(f.frame_ref, f.capture_ref, f.physical_step,
                                 "NO_CANDIDATES", None, (), (), ())
    receipts = tuple(f"comp-receipt:{i + 1}:{f.physical_step}" for i in range(len(names)))
    values = tuple(SubjectiveValuation(n, r, f"subjective:{i + 1}", scores.get(c.semantic_ref, 0))
                   for i, (c, n, r) in enumerate(zip(f.candidates, names, receipts)))
    best = max(v.value for v in values)
    leaders = [v.candidate_ref for v in values if v.value == best]
    decided = "NO_POSITIVE_EVIDENCE" if best <= 0 else "AMBIGUOUS" if len(leaders) != 1 else "ADVISORY_ONLY"
    chosen = leaders[0] if decided == "ADVISORY_ONLY" else None
    return CompetitionAdvice(f.frame_ref, f.capture_ref, f.physical_step,
                             status or decided, chosen, names, receipts, values)


class SyntheticCurrent:
    """Configured test source, not a physical/M11 authority."""

    def __init__(self):
        self.calls = []
        self.overrule = True

    def verify_current(self, *, life_ref, frame, advice):
        self.calls.append((life_ref, frame.frame_ref, advice.frame_ref))
        return self.overrule


class SyntheticDebit:
    """A toy balance, NOT a Scheduler or durable UC ledger."""

    def __init__(self, balance=12):
        self.balance = balance
        self.calls = []
        self.n = 0
        self.tamper = None
        self.throw = False

    def debit(self, *, life_ref, frame_ref, capture_ref, claim_digest,
              candidate_ref, operation, units):
        self.calls.append((life_ref, frame_ref, capture_ref, claim_digest, candidate_ref, operation, units))
        if self.balance < units:
            return None
        self.balance -= units
        self.n += 1
        if self.throw:
            raise RuntimeError("uncertain external debit")
        r = ControlReceipt(f"control-receipt:{self.n}", life_ref, frame_ref, capture_ref,
                           claim_digest, candidate_ref, operation, units)
        return self.tamper(r) if self.tamper else r


class SyntheticSafety:
    """Toy veto for software wiring, cannot admit a motor command."""

    def __init__(self, veto=False):
        self.calls = []
        self.veto = veto
        self.tamper = None
        self.throw = False

    def check(self, *, life_ref, frame, candidate_ref, control_receipt_ref):
        self.calls.append((life_ref, frame.frame_ref, candidate_ref, control_receipt_ref))
        if self.throw:
            raise RuntimeError("safety authority unavailable")
        f = SafetyFinding(life_ref, frame.frame_ref, frame.capture_ref,
                          candidate_ref, control_receipt_ref, self.veto, "safety:claimed-test-finding")
        return self.tamper(f) if self.tamper else f


def setup(*, balance=12, veto=False):
    current, ledger, safety = SyntheticCurrent(), SyntheticDebit(balance), SyntheticSafety(veto)
    gate = ActionControlBoundary(life_ref=LIFE, current_authority=current,
                                 ledger=ledger, safety_authority=safety)
    return gate, current, ledger, safety


class TestActionControlBoundary(unittest.TestCase):
    def test_all_authority_ports_required_and_no_motor_port(self):
        c, u, s = SyntheticCurrent(), SyntheticDebit(), SyntheticSafety()
        for x, y, z in ((None, u, s), (c, None, s), (c, u, None)):
            with self.subTest(ports=(x,y,z)), self.assertRaises(ValueError):
                ActionControlBoundary(life_ref=LIFE, current_authority=x,
                                      ledger=y, safety_authority=z)
        gate, *_ = setup()
        for name in ("birth", "run_step", "dispatch", "command", "execute",
                     "admit", "admit_motor", "apply_world", "cold_recover"):
            self.assertFalse(hasattr(gate, name))
        forbidden = {"command", "action", "admission", "approved", "winner", "execute", "uc_balance"}
        self.assertFalse(forbidden & {f.name for f in fields(ControlReview)})

    def test_unique_fully_evaluated_candidate_is_reviewed_not_admitted(self):
        gate, current, ledger, safety = setup()
        f = frame()
        a = advice(f)
        r = gate.review(frame=f, advice=a)
        self.assertEqual(r.status, "REVIEWED_NOT_ADMITTED")
        self.assertEqual(r.suggested_candidate_ref, a.suggested_candidate_ref)
        self.assertEqual(r.motor_authority, "NONE")
        self.assertEqual(ledger.balance, 11)
        self.assertEqual((len(current.calls), len(ledger.calls), len(safety.calls)), (1,1,1))
        self.assertEqual(ledger.calls[0][-2:], (CONTROL_OPERATION, CONTROL_UC))
        self.assertEqual(r.control_receipt_ref, safety.calls[0][-1])

    def test_independent_safety_veto_masks_candidate(self):
        gate, _, ledger, safety = setup(veto=True)
        r = gate.review(frame=frame(), advice=advice(frame()))
        self.assertEqual(r.status, "VETOED")
        self.assertIsNone(r.suggested_candidate_ref)
        self.assertEqual(r.motor_authority, "NONE")
        self.assertEqual(ledger.balance, 11)
        self.assertEqual(len(safety.calls), 1)

    def test_ambiguous_frame_never_reaches_debit_or_safety(self):
        f = frame()
        gate, source, ledger, safety = setup()
        a = advice(f, scores={SEMANTICS[0]: 4, SEMANTICS[1]: 4})
        self.assertEqual(a.status, "AMBIGUOUS")
        r = gate.review(frame=f, advice=a)
        self.assertEqual(r.status, "NO_ADVICE")
        self.assertIsNone(r.suggested_candidate_ref)
        self.assertEqual((len(source.calls), ledger.calls, safety.calls), (1, [], []))

    def test_nonpositive_frame_is_never_reviewed_for_motor(self):
        f = frame()
        gate, _, ledger, safety = setup()
        r = gate.review(frame=f, advice=advice(f, scores={}))
        self.assertEqual(r.status, "NO_ADVICE")
        self.assertEqual(ledger.calls, [])
        self.assertEqual(safety.calls, [])

    def test_unfunded_competition_never_creates_safety_review(self):
        f = frame()
        a = CompetitionAdvice(f.frame_ref, f.capture_ref, f.physical_step,
                              "UNFUNDED", None, (), (), ())
        gate, _, ledger, safety = setup()
        self.assertEqual(gate.review(frame=f, advice=a).status, "NO_ADVICE")
        self.assertEqual(ledger.calls, [])
        self.assertEqual(safety.calls, [])

    def test_empty_frame_requires_no_safety_work(self):
        f = frame(semantics=())
        gate, _, ledger, safety = setup()
        self.assertEqual(gate.review(frame=f, advice=advice(f)).status, "NO_ADVICE")
        self.assertEqual(ledger.calls, [])
        self.assertEqual(safety.calls, [])

    def test_missing_control_uc_never_queries_safety(self):
        f = frame()
        gate, _, ledger, safety = setup(balance=0)
        r = gate.review(frame=f, advice=advice(f))
        self.assertEqual(r.status, "UNFUNDED")
        self.assertEqual(r.motor_authority, "NONE")
        self.assertEqual(ledger.balance, 0)
        self.assertEqual(safety.calls, [])

    def test_unattested_current_capture_rejected_before_spend(self):
        f = frame()
        gate, source, ledger, safety = setup()
        source.overrule = False
        with self.assertRaises(ValueError): gate.review(frame=f, advice=advice(f))
        self.assertEqual(ledger.calls, [])
        self.assertEqual(safety.calls, [])

    def test_truthy_nonboolean_current_attestation_rejected(self):
        for value in (1, "true", [], None):
            with self.subTest(value=value):
                f = frame()
                gate, source, ledger, _ = setup()
                source.overrule = value
                with self.assertRaises(ValueError): gate.review(frame=f, advice=advice(f))
                self.assertEqual(ledger.calls, [])

    def test_foreign_life_denied_before_authority_invocation(self):
        f = frame(life="life:foreign")
        gate, source, ledger, safety = setup()
        with self.assertRaises(ValueError): gate.review(frame=f, advice=advice(f))
        self.assertEqual((source.calls, ledger.calls, safety.calls), ([], [], []))

    def test_forged_recommended_candidate_without_winning_value_refused(self):
        f = frame()
        a = advice(f)
        forged = replace(a, suggested_candidate_ref=f.candidates[0].candidate_ref)
        gate, source, ledger, _ = setup()
        with self.assertRaises(ValueError): gate.review(frame=f, advice=forged)
        self.assertEqual((source.calls, ledger.calls), ([], []))

    def test_foreign_candidate_and_frame_mismatch_refused(self):
        f = frame()
        a = advice(f)
        variants = (replace(a, frame_ref="frame:i2:foreign"),
                    replace(a, capture_ref="capture:foreign"),
                    replace(a, physical_step=f.physical_step + 1),
                    replace(a, suggested_candidate_ref="candidate:i2:foreign"))
        for bad in variants:
            with self.subTest(bad=bad):
                gate, _, ledger, _ = setup()
                with self.assertRaises(ValueError): gate.review(frame=f, advice=bad)
                self.assertEqual(ledger.calls, [])

    def test_partial_competition_evaluation_never_reaches_safety(self):
        f = frame(); a = advice(f)
        variants = (replace(a, evaluated_candidate_refs=a.evaluated_candidate_refs[:-1]),
                    replace(a, receipt_refs=a.receipt_refs[:-1]),
                    replace(a, valuation_records=a.valuation_records[:-1]))
        for bad in variants:
            with self.subTest(bad=bad):
                gate, source, ledger, _ = setup()
                with self.assertRaises(ValueError): gate.review(frame=f, advice=bad)
                self.assertEqual((source.calls, ledger.calls), ([], []))

    def test_duplicate_or_misaligned_competition_receipts_refused(self):
        f = frame(); a = advice(f)
        variants = (
            replace(a, receipt_refs=(a.receipt_refs[0], a.receipt_refs[0], a.receipt_refs[2])),
            replace(a, valuation_records=(replace(a.valuation_records[0], receipt_ref="receipt:wrong"),)
                    + a.valuation_records[1:]),
            replace(a, valuation_records=list(a.valuation_records)),
        )
        for bad in variants:
            with self.subTest(bad=bad):
                gate, source, ledger, _ = setup()
                with self.assertRaises(ValueError): gate.review(frame=f, advice=bad)
                self.assertEqual((source.calls, ledger.calls), ([], []))

    def test_forged_status_tie_and_nonpositive_value_refused(self):
        f = frame(); a = advice(f)
        variants = (replace(a, status="AMBIGUOUS", suggested_candidate_ref=None),
                    replace(a, status="NO_POSITIVE_EVIDENCE", suggested_candidate_ref=None),
                    replace(a, status="MADE_UP"),
                    replace(a, status="UNFUNDED", suggested_candidate_ref=None))
        for bad in variants:
            with self.subTest(bad=bad):
                gate, source, ledger, _ = setup()
                with self.assertRaises(ValueError): gate.review(frame=f, advice=bad)
                self.assertEqual((source.calls, ledger.calls), ([], []))

    def test_invalid_competition_value_bound_and_wrong_semantic(self):
        f = frame(); a = advice(f)
        variants = (replace(a.valuation_records[0], value=True),
                    replace(a.valuation_records[0], value=1025),
                    replace(a.valuation_records[0], candidate_ref="candidate:alien"))
        for v in variants:
            with self.subTest(v=v):
                gate, source, ledger, _ = setup()
                bad=replace(a, valuation_records=(v,)+a.valuation_records[1:])
                with self.assertRaises(ValueError): gate.review(frame=f, advice=bad)
                self.assertEqual((source.calls, ledger.calls), ([], []))

    def test_malformed_frame_rejected_before_port(self):
        f=frame(); a=advice(f)
        bad = replace(f, candidates=f.candidates[::-1])
        gate, source, ledger, _ = setup()
        with self.assertRaises(ValueError): gate.review(frame=bad, advice=a)
        self.assertEqual((source.calls, ledger.calls), ([], []))

    def test_stale_step_and_replayed_frame_never_recharge(self):
        gate, _, ledger, _ = setup()
        f=frame(4);gate.review(frame=f, advice=advice(f))
        with self.assertRaises(ValueError): gate.review(frame=f, advice=advice(f))
        older=frame(3)
        with self.assertRaises(ValueError): gate.review(frame=older, advice=advice(older))
        self.assertEqual(len(ledger.calls), 1)

    def test_same_capture_different_frame_ref_is_refused(self):
        gate, _, ledger, _ = setup()
        f = frame()
        gate.review(frame=f, advice=advice(f))
        mutated = replace(f, frame_ref="frame:i2:" + "f" * 64)
        with self.assertRaises(ValueError):gate.review(frame=mutated, advice=advice(mutated))
        self.assertEqual(len(ledger.calls), 1)

    def test_second_frame_new_step_requires_new_control_uc(self):
        gate, _, ledger, _ = setup()
        f3, f4 = frame(3), frame(4)
        gate.review(frame=f3, advice=advice(f3))
        gate.review(frame=f4, advice=advice(f4))
        self.assertEqual(ledger.balance, 10)
        self.assertEqual(len(ledger.calls), 2)

    def test_after_uncertain_charge_attempt_cannot_retry_locally(self):
        gate, _, ledger, safety = setup()
        ledger.throw = True
        f=frame()
        with self.assertRaises(RuntimeError): gate.review(frame=f, advice=advice(f))
        with self.assertRaises(ValueError): gate.review(frame=f, advice=advice(f))
        self.assertEqual(ledger.balance, 11)
        self.assertEqual(safety.calls, [])

    def test_receipt_mismatch_refuses_before_safety_with_no_refund_claim(self):
        changes=(lambda r: replace(r, life_ref="life:foreign"),
                 lambda r: replace(r, frame_ref="frame:i2:foreign"),
                 lambda r: replace(r, capture_ref="capture:wrong"),
                 lambda r: replace(r, claim_digest="c"*64),
                 lambda r: replace(r, candidate_ref="candidate:i2:wrong"),
                 lambda r: replace(r, operation="incorrect"),
                 lambda r: replace(r, units=2),
                 lambda r: replace(r, units=True),
                 lambda r: replace(r, ref="has space"))
        for change in changes:
            with self.subTest(change=change):
                gate, _, ledger, safety = setup()
                ledger.tamper=change
                f=frame()
                with self.assertRaises(ValueError): gate.review(frame=f, advice=advice(f))
                self.assertEqual(safety.calls, [])
                self.assertEqual(ledger.balance, 11)

    def test_forged_safety_result_refused_after_paid_review(self):
        changes=(lambda s: replace(s, life_ref="life:foreign"),
                 lambda s: replace(s, frame_ref="frame:i2:wrong"),
                 lambda s: replace(s, capture_ref="capture:wrong"),
                 lambda s: replace(s, candidate_ref="candidate:wrong"),
                 lambda s: replace(s, control_receipt_ref="control:wrong"),
                 lambda s: replace(s, veto=1),
                 lambda s: replace(s, evidence_ref="not valid"))
        for change in changes:
            with self.subTest(change=change):
                gate, _, ledger, safety = setup()
                safety.tamper=change
                f=frame()
                with self.assertRaises(ValueError): gate.review(frame=f, advice=advice(f))
                self.assertEqual(ledger.balance, 11)

    def test_safety_exception_after_charge_never_allows_free_retry(self):
        gate, _, ledger, safety = setup()
        safety.throw=True
        f=frame()
        with self.assertRaises(RuntimeError): gate.review(frame=f, advice=advice(f))
        with self.assertRaises(ValueError): gate.review(frame=f, advice=advice(f))
        self.assertEqual(ledger.balance, 11)

    def test_reused_control_receipt_across_frames_refused(self):
        gate, _, ledger, safety = setup()
        f=frame(3); gate.review(frame=f, advice=advice(f))
        ledger.tamper=lambda r: replace(r, ref="control-receipt:1")
        new=frame(4)
        with self.assertRaises(ValueError): gate.review(frame=new, advice=advice(new))
        self.assertEqual(len(safety.calls),1)

    def test_intention_tag_never_changes_review_outcome(self):
        states=[]
        for tagged in (False, True):
            gate, _, ledger, safety = setup()
            f=frame(tagged=tagged)
            r=gate.review(frame=f, advice=advice(f))
            states.append((r.status,r.suggested_candidate_ref,ledger.balance,len(safety.calls)))
        self.assertEqual(states[0],states[1])

    def test_two_concurrent_calls_only_one_can_review(self):
        gate, _, ledger, _=setup()
        f=frame();a=advice(f)
        def attempt(_):
            try:return gate.review(frame=f, advice=a).status
            except ValueError:return "REPLAY_REFUSED"
        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes=list(pool.map(attempt,(0,1)))
        self.assertCountEqual(outcomes,["REVIEWED_NOT_ADMITTED","REPLAY_REFUSED"])
        self.assertEqual(len(ledger.calls),1)

    def test_no_command_and_all_review_variants_are_motor_none(self):
        variants=[]
        for veto,balance,scores in ((True,12,None),(False,12,None),(False,0,None),
                                    (False,12,{})):
            gate,_,_,_=setup(veto=veto,balance=balance)
            f=frame(); r=gate.review(frame=f,advice=advice(f,scores=scores))
            variants.append(r)
        for result in variants:
            self.assertEqual(result.motor_authority,"NONE")
            self.assertFalse(hasattr(result,"command"))
            self.assertFalse(hasattr(result,"admission"))


if __name__ == "__main__":
    unittest.main()
