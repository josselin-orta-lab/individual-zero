"""Offline SQLite competition custody tests, never an I2 life or M11."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import fields, replace
import json
from pathlib import Path
import sqlite3
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from i2.modules.intention_continuity import FirstPersonCapture, IntentionContinuity  # noqa: E402
from i2.modules.intention_ingress import ObservationClaim  # noqa: E402
from i2.modules.option_reconstruction import reconstruct_candidates, CandidateFrame  # noqa: E402
from i2.modules.competition_preview import SubjectiveValuation, veto_preview, CompetitionAdvice  # noqa: E402
from i2.modules.competition_transaction_fixture import (  # noqa: E402
    CompetitionTransactionFixture, FixtureAdviceReceipt, FaultInjected,
    CommitAcknowledgmentLost, _chain, _canonical,
)

LIFE = "synthetic:test-one"
A = "offer:explore"
B = "offer:eat"
C = "offer:rest"


def frame(step=3, *, visible=(A, B, C), life=LIFE, intent=None):
    cap = FirstPersonCapture(step, f"capture:{step}", "goal:need", tuple(sorted(visible)))
    claim = ObservationClaim(life, cap, f"source:{step}", (f"evidence:{step}",))
    owner = IntentionContinuity()
    if intent is None:
        t = owner.observe(capture=cap, work_ref=f"work:{step}")
    else:
        t = owner.open(capture=cap, semantic_ref=intent, evidence_ref=f"evidence:{step}",
                       ttl_steps=4, work_ref=f"work:{step}")
    return reconstruct_candidates(claim=claim, transition=t, current=owner.current)


def ref_for_sem(candidate_frame, semantic):
    return next(c.candidate_ref for c in candidate_frame.candidates
                if c.semantic_ref == semantic)


class MockSource:
    def __init__(self):
        self.accept = True
        self.calls = []
    def verify(self, *, life_ref, frame):
        self.calls.append((life_ref, frame.frame_ref))
        return self.accept


class MockEvidence:
    def __init__(self, scores=None):
        self.scores = scores or {A: 3, B: 6, C: 1}
        self.calls = []
        self.fail = False
        self.mutate = None
    def evaluate_batch(self, *, frame, receipts):
        self.calls.append(frame.frame_ref)
        if self.fail:
            raise ValueError("synthetic observation unavailable")
        val = tuple(SubjectiveValuation(
            candidate_ref=r.candidate_ref, receipt_ref=r.ref,
            evidence_ref="mock:subjective:" + str(i),
            value=self.scores.get(c.semantic_ref, 0),
        ) for i, (r, c) in enumerate(zip(receipts, frame.candidates)))
        return self.mutate(val) if self.mutate else val


class TestCompetitionTransactionFixture(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "competition.sqlite"
        self.source = MockSource()
        self.evidence = MockEvidence()

    def create(self, uc=9, *, life=LIFE):
        return CompetitionTransactionFixture.create(path=self.path, life_ref=life,
            synthetic_uc=uc, frame_source=self.source, evidence_source=self.evidence)

    def reopen(self, *, life=LIFE):
        return CompetitionTransactionFixture.reopen(path=self.path, life_ref=life,
            frame_source=self.source, evidence_source=self.evidence)

    def test_fresh_fixture_really_empty_and_inert(self):
        fixture = self.create(uc=7)
        result = fixture.audit()
        self.assertEqual(result["remaining_synthetic_uc"], 7)
        self.assertEqual(result["record_count"], 0)
        self.assertEqual(result["last_step"], -1)
        self.assertFalse(result["m11_authenticated"])
        self.assertFalse(result["scheduler_uc_authenticated"])
        self.assertEqual(result["motor_authority"], "NONE")
        for key in ("birth", "run_step", "action_control", "command", "dispatch", "m11", "recover_life"):
            self.assertFalse(hasattr(fixture, key), key)

    def test_funded_frame_debits_same_transaction_as_advice(self):
        fixture = self.create()
        out = fixture.review(frame=frame())
        self.assertEqual(out.status, "ADVISORY_ONLY")
        self.assertEqual(out.units_spent, 3)
        self.assertEqual(out.motor_authority, "NONE")
        self.assertEqual(out.suggested_candidate_ref, ref_for_sem(frame(), B))
        self.assertEqual(fixture.audit()["remaining_synthetic_uc"], 6)
        self.assertEqual(self.reopen().lookup(capture_ref="capture:3"), out)
        self.assertFalse({"command", "admit", "execute", "action"} &
                         {x.name for x in fields(FixtureAdviceReceipt)})

    def test_reopen_preserves_custody_not_life(self):
        self.create().review(frame=frame(3))
        other = self.reopen()
        self.assertEqual(other.review(frame=frame(4)).seq, 2)
        self.assertEqual(other.audit()["remaining_synthetic_uc"], 3)
        self.assertEqual(other.audit()["record_count"], 2)

    def test_too_many_candidates_unfunded_consumes_frame_without_debit(self):
        fixture = self.create(uc=2)
        receipt = fixture.review(frame=frame(3))
        self.assertEqual(receipt.status, "UNFUNDED")
        self.assertEqual(receipt.units_spent, 0)
        self.assertIsNone(receipt.suggested_candidate_ref)
        self.assertEqual(self.evidence.calls, [])
        self.assertEqual(self.reopen().audit()["remaining_synthetic_uc"], 2)
        with self.assertRaises(ValueError):
            self.reopen().review(frame=frame(3))
        self.assertEqual(self.reopen().review(frame=frame(4, visible=(A, B))).units_spent, 2)

    def test_zero_candidates_no_debit_but_persisted(self):
        fixture = self.create(0)
        out = fixture.review(frame=frame(3, visible=()))
        self.assertEqual(out.status, "NO_CANDIDATES")
        self.assertEqual(out.units_spent, 0)
        self.assertEqual(fixture.audit()["record_count"], 1)
        self.assertEqual(self.evidence.calls, [])

    def test_equal_best_abstains_without_executable_result(self):
        self.evidence.scores = {A: 4, B: 4, C: 0}
        fixture = self.create()
        out = fixture.review(frame=frame())
        self.assertEqual(out.status, "AMBIGUOUS")
        self.assertIsNone(out.suggested_candidate_ref)
        self.assertEqual(out.motor_authority, "NONE")
        self.assertEqual(fixture.audit()["remaining_synthetic_uc"], 6)

    def test_nonpositive_scores_abstain_with_paid_full_frame(self):
        self.evidence.scores = {A: -1, B: 0, C: -2}
        out = self.create().review(frame=frame())
        self.assertEqual(out.status, "NO_POSITIVE_EVIDENCE")
        self.assertIsNone(out.suggested_candidate_ref)
        self.assertEqual(out.units_spent, 3)

    def test_intention_tag_is_neutral_to_advice(self):
        first = self.create().review(frame=frame(3, intent=A))
        second = self.reopen().review(frame=frame(4))
        self.assertEqual(first.status, second.status)
        self.assertEqual(first.units_spent, second.units_spent)
        self.assertEqual(first.suggested_candidate_ref, ref_for_sem(frame(3), B))
        self.assertEqual(second.suggested_candidate_ref, ref_for_sem(frame(4), B))

    def test_non_food_winner_by_synthetic_scores(self):
        self.evidence.scores = {A: 8, B: 0, C: 1}
        out = self.create().review(frame=frame(3))
        self.assertEqual(out.suggested_candidate_ref, ref_for_sem(frame(), A))

    def test_rejected_source_before_any_ledger_or_evaluation(self):
        fixture = self.create()
        self.source.accept = False
        with self.assertRaises(ValueError):
            fixture.review(frame=frame())
        self.assertEqual(fixture.audit()["remaining_synthetic_uc"], 9)
        self.assertEqual(self.evidence.calls, [])

    def test_foreign_life_refused_before_source(self):
        fixture = self.create()
        with self.assertRaises(ValueError):
            fixture.review(frame=frame(life="other:life"))
        self.assertEqual(self.source.calls, [])
        self.assertEqual(fixture.audit()["record_count"], 0)

    def test_repeated_capture_after_restart_cannot_charge_again(self):
        self.create().review(frame=frame(3))
        fixture = self.reopen()
        for bad in (frame(3), frame(2), frame(4)):
            if bad.physical_step == 4:
                bad = replace(bad, capture_ref="capture:3")
            with self.subTest(bad=bad.frame_ref), self.assertRaises(ValueError):
                fixture.review(frame=bad)
        self.assertEqual(fixture.audit()["remaining_synthetic_uc"], 6)

    def test_precommit_faults_rollback_balance_and_advice(self):
        for fault in ("after_debit", "after_evidence", "before_commit"):
            with self.subTest(fault=fault):
                if self.path.exists():
                    self.path.unlink()
                    for sidecar in (str(self.path)+"-wal", str(self.path)+"-shm"):
                        p = Path(sidecar)
                        if p.exists():
                            p.unlink()
                fixture = self.create()
                with self.assertRaises(FaultInjected):
                    fixture.review(frame=frame(), _fault_at=fault)
                self.assertEqual(fixture.audit()["record_count"], 0)
                self.assertEqual(fixture.audit()["remaining_synthetic_uc"], 9)
                self.assertIsNone(self.reopen().lookup(capture_ref="capture:3"))

    def test_lost_commit_acknowledgment_is_resolved_by_read_only_lookup(self):
        fixture = self.create()
        with self.assertRaises(CommitAcknowledgmentLost):
            fixture.review(frame=frame(), _fault_at="after_commit")
        recovered = self.reopen().lookup(capture_ref="capture:3")
        self.assertEqual(recovered.units_spent, 3)
        self.assertEqual(self.reopen().audit()["record_count"], 1)
        with self.assertRaises(ValueError):
            self.reopen().review(frame=frame())
        self.assertEqual(self.reopen().audit()["remaining_synthetic_uc"], 6)

    def test_bad_evidence_rolls_back_even_if_debit_was_calculated(self):
        fixture = self.create()
        self.evidence.fail = True
        with self.assertRaises(ValueError):
            fixture.review(frame=frame())
        self.assertEqual(fixture.audit()["remaining_synthetic_uc"], 9)
        self.assertEqual(fixture.audit()["record_count"], 0)

    def test_malformed_value_or_reordered_value_refuses_atomically(self):
        fixture = self.create()
        self.evidence.mutate = lambda vals: tuple(replace(v, receipt_ref="forged:uc") for v in vals)
        with self.assertRaises(ValueError):
            fixture.review(frame=frame())
        self.assertEqual(fixture.audit()["record_count"], 0)
        self.assertEqual(fixture.audit()["remaining_synthetic_uc"], 9)
        self.evidence.mutate = None
        self.assertEqual(fixture.review(frame=frame()).units_spent, 3)

    def test_bad_frame_fails_before_source_and_charge(self):
        fixture = self.create()
        original = frame()
        bad = replace(original, candidates=original.candidates[::-1])
        with self.assertRaises(ValueError):
            fixture.review(frame=bad)
        self.assertEqual(self.source.calls, [])
        self.assertEqual(fixture.audit()["remaining_synthetic_uc"], 9)

    def test_wrong_life_cannot_reopen_readonly(self):
        self.create().review(frame=frame(3))
        with self.assertRaises(ValueError):
            self.reopen(life="other:life")
        self.assertEqual(self.reopen().audit()["record_count"], 1)

    def test_cannot_recreate_over_database(self):
        self.create()
        with self.assertRaises(FileExistsError):
            self.create()
        self.assertEqual(self.reopen().audit()["remaining_synthetic_uc"], 9)

    def test_corruption_of_stored_event_is_detected(self):
        self.create().review(frame=frame())
        conn = sqlite3.connect(self.path)
        conn.execute("UPDATE events SET event_json='{}' WHERE seq=1")
        conn.commit();conn.close()
        with self.assertRaises(ValueError):
            self.reopen()

    def test_modified_balance_without_event_is_detected(self):
        self.create().review(frame=frame())
        conn = sqlite3.connect(self.path)
        conn.execute("UPDATE account SET remaining_uc=remaining_uc+1")
        conn.commit();conn.close()
        with self.assertRaises(ValueError):
            self.reopen()

    def test_modified_rehashed_value_cannot_change_published_decision_only(self):
        self.create().review(frame=frame())
        conn = sqlite3.connect(self.path)
        before = conn.execute("SELECT event_json FROM events WHERE seq=1").fetchone()[0]
        obj = json.loads(before)
        obj["suggested_candidate_ref"] = ref_for_sem(frame(), A)
        text = _canonical(obj)
        conn.execute("UPDATE events SET event_json=?, event_hash=? WHERE seq=1",
                     (text, _chain("0"*64, text)))
        conn.execute("UPDATE account SET chain_head=?", (_chain("0"*64,text),))
        conn.commit();conn.close()
        with self.assertRaises(ValueError):
            self.reopen()

    def test_partial_rewrite_with_valid_hash_still_replays_values_and_cost(self):
        self.create().review(frame=frame())
        conn = sqlite3.connect(self.path)
        obj = json.loads(conn.execute("SELECT event_json FROM events").fetchone()[0])
        obj["units_spent"] = 1
        txt = _canonical(obj)
        chain = _chain("0"*64, txt)
        conn.execute("UPDATE events SET event_json=?, event_hash=?", (txt,chain))
        conn.execute("UPDATE account SET chain_head=?", (chain,))
        conn.commit();conn.close()
        with self.assertRaises(ValueError):
            self.reopen()

    def test_parallel_sessions_one_capture_one_charge(self):
        first = self.create()
        second = self.reopen()
        f = frame()
        def attempt(x):
            try:
                return x.review(frame=f).status
            except ValueError:
                return "REPLAY_REJECTED"
        with ThreadPoolExecutor(max_workers=2) as pool:
            result = list(pool.map(attempt, (first,second)))
        self.assertCountEqual(result, ["ADVISORY_ONLY", "REPLAY_REJECTED"])
        self.assertEqual(self.reopen().audit()["remaining_synthetic_uc"], 6)
        self.assertEqual(self.reopen().audit()["record_count"], 1)

    def test_source_ports_required_and_never_m11(self):
        with self.assertRaises(ValueError):
            CompetitionTransactionFixture(path=self.path, life_ref=LIFE,
                frame_source=None, evidence_source=self.evidence)
        with self.assertRaises(ValueError):
            CompetitionTransactionFixture(path=self.path, life_ref=LIFE,
                frame_source=self.source, evidence_source=None)
        self.assertFalse(hasattr(self.create(), "cold_recover"))


if __name__ == "__main__":
    unittest.main()
