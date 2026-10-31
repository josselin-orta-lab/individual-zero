"""Offline I2 unified cycle tests; all identities, values and UC are synthetic."""
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
from i2.modules.intention_continuity import FirstPersonCapture  # noqa: E402
from i2.modules.intention_ingress import ObservationClaim  # noqa: E402
from i2.modules.competition_preview import SubjectiveValuation  # noqa: E402
from i2.modules.cognitive_cycle_fixture import (  # noqa: E402
    CognitiveCycleFixture, CycleReceipt, FaultInjected, CommitAcknowledgmentLost,
    _chain, _json, SCHEMA,
)

LIFE = "life:synthetic-cycle"
A = "affordance:collect:berry_a"
B = "affordance:eat:berry_a"
C = "affordance:drink:water"


def claim(step=3, *, life=LIFE, visible=(A, B, C), goal="goal:hunger",
          conflict=(), ref=None):
    return ObservationClaim(
        life_ref=life, source_event_ref=f"source:synthetic:{step}",
        subjective_evidence_refs=(f"evidence:{step}",),
        capture=FirstPersonCapture(
            step, ref or f"capture:{step}", goal,
            tuple(sorted(visible)), tuple(sorted(conflict)),
        ),
    )


class SyntheticObservations:
    def __init__(self):
        self.allowed = set()
        self.calls = 0
        self.override = None

    def add(self, value):
        self.allowed.add(value.digest())
        return value

    def verify(self, *, life_ref, claim, digest):
        self.calls += 1
        if self.override is not None:
            return self.override
        return life_ref == LIFE and digest in self.allowed and digest == claim.digest()


class SyntheticValues:
    def __init__(self, scores=None):
        self.scores = scores if scores is not None else {A: 2, B: 9, C: 1}
        self.calls = 0
        self.fault = False
        self.tamper = None

    def evaluate_batch(self, *, frame, receipts):
        self.calls += 1
        if self.fault:
            raise RuntimeError("synthetic evidence port failed")
        result = tuple(
            SubjectiveValuation(
                candidate_ref=c.candidate_ref, receipt_ref=r.ref,
                evidence_ref=f"value:synthetic:{c.semantic_ref}",
                value=self.scores.get(c.semantic_ref, 0),
            ) for c, r in zip(frame.candidates, receipts)
        )
        return self.tamper(result) if self.tamper else result


class CycleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "one-synthetic-cycle.sqlite"
        self.source = SyntheticObservations()
        self.values = SyntheticValues()

    def fixture(self, budget=12):
        return CognitiveCycleFixture.create(
            path=self.path, life_ref=LIFE, synthetic_uc=budget,
            observation_source=self.source, valuation_source=self.values,
        )

    def first(self, fixture, *, at=3, _fault_at=None, semantic_ref=A, visible=(A, B, C)):
        obs = self.source.add(claim(at, visible=visible))
        return fixture.open(claim=obs, semantic_ref=semantic_ref,
                            evidence_ref=f"evidence:{at}", ttl_steps=12,
                            _fault_at=_fault_at)

    def test_empty_fixture_not_a_birth_and_never_motor(self):
        f = self.fixture()
        self.assertEqual(f.audit()["committed"], 0)
        self.assertEqual(f.audit()["remaining_synthetic_uc"], 12)
        self.assertFalse(f.audit()["m11_authenticated"])
        self.assertFalse(f.audit()["scheduler_uc_authenticated"])
        self.assertEqual(f.audit()["motor_authority"], "NONE")
        for method in ("birth", "run_step", "dispatch", "admit_motor", "execute", "cold_recover"):
            self.assertFalse(hasattr(f, method))
        self.assertFalse({"command", "winner", "admission", "motor_option"} &
                         {i.name for i in fields(CycleReceipt)})

    def test_both_injected_sources_required(self):
        with self.assertRaises(ValueError):
            CognitiveCycleFixture(path=self.path, life_ref=LIFE,
                                  observation_source=None, valuation_source=self.values)
        with self.assertRaises(ValueError):
            CognitiveCycleFixture(path=self.path, life_ref=LIFE,
                                  observation_source=self.source, valuation_source=None)

    def test_full_cycle_one_commit_debits_owner_and_all_candidates(self):
        f = self.fixture()
        receipt = self.first(f)
        self.assertEqual((receipt.intake_uc, receipt.competition_uc), (1, 3))
        self.assertEqual(receipt.competition_status, "ADVISORY_ONLY")
        self.assertEqual(receipt.intention_kind, "opened")
        self.assertIsNotNone(receipt.suggested_candidate_ref)
        self.assertEqual(receipt.motor_authority, "NONE")
        report = f.audit()
        self.assertEqual((report["remaining_synthetic_uc"], report["committed"]), (8, 1))
        self.assertEqual(report["intention"]["status"], "active")
        self.assertEqual(f.lookup(capture_ref="capture:3"), receipt)

    def test_reopen_is_readonly_verification_not_life_recovery(self):
        f = self.fixture()
        original = self.first(f)
        src_calls, value_calls = self.source.calls, self.values.calls
        inspected = CognitiveCycleFixture.reopen(
            path=self.path, life_ref=LIFE,
            observation_source=self.source, valuation_source=self.values,
        )
        self.assertEqual(inspected.lookup(capture_ref=original.capture_ref), original)
        self.assertEqual(inspected.audit()["chain_head"], original.chain_head)
        self.assertEqual((self.source.calls, self.values.calls), (src_calls, value_calls))
        self.assertEqual(inspected.audit()["motor_authority"], "NONE")

    def test_intention_suspend_resume_keeps_semantics_not_candidate(self):
        f = self.fixture(budget=16)
        initial = self.first(f)
        c4 = self.source.add(claim(4, visible=(B, C)))
        suspended = f.observe(claim=c4)
        self.assertEqual(suspended.intention_kind, "suspended")
        self.assertEqual(suspended.competition_uc, 2)
        self.assertEqual(f.audit()["intention"]["status"], "suspended")
        c5 = self.source.add(claim(5, visible=(A, B)))
        resumed = f.observe(claim=c5)
        self.assertEqual(resumed.intention_kind, "resumed")
        self.assertEqual(resumed.competition_uc, 2)
        self.assertNotEqual(initial.suggested_candidate_ref, resumed.suggested_candidate_ref)
        self.assertEqual(f.audit()["intention"]["status"], "active")
        self.assertEqual(f.audit()["remaining_synthetic_uc"], 16 - 4 - 3 - 3)

    def test_first_capture_not_currently_visible_cannot_be_opened(self):
        f = self.fixture()
        result = self.first(f, semantic_ref=A, visible=(B, C))
        self.assertEqual(result.intention_kind, "policy_rejected")
        self.assertEqual(result.competition_status, "POLICY_REJECTED")
        self.assertEqual((result.intake_uc, result.competition_uc), (1, 0))
        self.assertIsNone(f.audit()["intention"])
        self.assertEqual(self.values.calls, 0)
        self.assertEqual(f.audit()["remaining_synthetic_uc"], 11)
        with self.assertRaises(ValueError):
            self.first(f, semantic_ref=A, visible=(B, C))
        self.assertEqual(f.audit()["committed"], 1)

    def test_failed_second_open_charges_only_intention_and_keeps_previous(self):
        f = self.fixture()
        first = self.first(f)
        current = f.audit()["intention"]
        second = self.first(f, at=4)
        self.assertEqual(second.competition_status, "POLICY_REJECTED")
        self.assertEqual(second.intake_uc, 1)
        self.assertEqual(f.audit()["intention"], current)
        self.assertEqual(f.audit()["remaining_synthetic_uc"], 7)
        self.assertNotEqual(first.capture_ref, second.capture_ref)

    def test_zero_uc_refuses_before_consultation_and_publishing(self):
        f = self.fixture(budget=0)
        with self.assertRaises(ValueError):
            self.first(f)
        self.assertEqual(f.audit()["committed"], 0)
        self.assertEqual(self.values.calls, 0)

    def test_one_uc_can_publish_intention_but_not_unpaid_competition(self):
        f = self.fixture(budget=1)
        r = self.first(f)
        self.assertEqual((r.intake_uc, r.competition_uc), (1, 0))
        self.assertEqual(r.competition_status, "UNFUNDED")
        self.assertIsNone(r.suggested_candidate_ref)
        self.assertEqual(self.values.calls, 0)
        self.assertIsNotNone(f.audit()["intention"])
        self.assertEqual(f.audit()["remaining_synthetic_uc"], 0)

    def test_partial_competition_budget_never_allocates_one_candidate(self):
        f = self.fixture(budget=3)
        r = self.first(f)
        self.assertEqual((r.intake_uc, r.competition_uc), (1, 0))
        self.assertEqual(r.competition_status, "UNFUNDED")
        self.assertEqual(f.audit()["remaining_synthetic_uc"], 2)
        self.assertEqual(self.values.calls, 0)

    def test_exact_total_budget_pays_all(self):
        f = self.fixture(budget=4)
        r = self.first(f)
        self.assertEqual(r.competition_uc, 3)
        self.assertEqual(f.audit()["remaining_synthetic_uc"], 0)

    def test_no_candidates_debits_only_intention(self):
        f = self.fixture(budget=1)
        c = self.source.add(claim(3, visible=()))
        r = f.observe(claim=c)
        self.assertEqual(r.intention_kind, "idle")
        self.assertEqual(r.competition_status, "NO_CANDIDATES")
        self.assertEqual((r.intake_uc, r.competition_uc), (1, 0))
        self.assertEqual(self.values.calls, 0)

    def test_equal_or_nonpositive_values_do_not_force_selection(self):
        for scores, status in (({A: 5, B: 5, C: 0}, "AMBIGUOUS"),
                               ({A: 0, B: -1, C: 0}, "NO_POSITIVE_EVIDENCE")):
            with self.subTest(status=status):
                self.values.scores = scores
                f = self.fixture()
                r = self.first(f)
                self.assertEqual(r.competition_status, status)
                self.assertIsNone(r.suggested_candidate_ref)
                self.path.unlink()
                # SQLite WAL files and readers must not be kept between subcases.

    def test_intention_context_does_not_create_bonus(self):
        f = self.fixture()
        r = self.first(f)
        self.assertEqual(r.competition_status, "ADVISORY_ONLY")
        with sqlite3.connect(self.path) as conn:
            (raw,) = conn.execute("SELECT event_json FROM events WHERE seq=1").fetchone()
        data = json.loads(raw)
        candidates = data["frame"]["candidates"]
        self.assertEqual(len(candidates), 3)
        self.assertEqual(len([c for c in candidates if c["intention_ref"]]), 1)
        winner = next(c["candidate_ref"] for c in candidates if c["semantic_ref"] == B)
        self.assertEqual(r.suggested_candidate_ref, winner)

    def test_replays_and_stale_captures_refuse_before_competition(self):
        f = self.fixture(budget=12)
        self.first(f)
        for c in (claim(3), claim(2), claim(4, ref="capture:3")):
            self.source.add(c)
            with self.subTest(c=c), self.assertRaises(ValueError):
                f.observe(claim=c)
        self.assertEqual(f.audit()["remaining_synthetic_uc"], 8)
        self.assertEqual(self.values.calls, 1)

    def test_foreign_claim_and_unattested_claim_refuse(self):
        f = self.fixture()
        with self.assertRaises(ValueError):
            f.observe(claim=claim(3, life="life:forged"))
        with self.assertRaises(ValueError):
            f.observe(claim=claim(3))
        self.assertEqual(f.audit()["committed"], 0)
        self.assertEqual(self.values.calls, 0)

    def test_nonboolean_authority_does_not_authorize(self):
        f = self.fixture()
        c = self.source.add(claim())
        self.source.override = 1
        with self.assertRaises(ValueError):
            f.observe(claim=c)
        self.assertEqual(f.audit()["committed"], 0)

    def test_observation_origin_evidence_is_required_before_source_access(self):
        f = self.fixture()
        c = self.source.add(claim())
        with self.assertRaises(ValueError):
            f.open(claim=c, semantic_ref=A, evidence_ref="evidence:forged", ttl_steps=3)
        self.assertEqual(self.source.calls, 0)
        self.assertEqual(f.audit()["committed"], 0)

    def test_bad_valuation_or_exception_rolls_back_entire_cycle(self):
        for flaw in ("exception", "partial", "wrong_receipt", "bool_value"):
            with self.subTest(flaw=flaw):
                f = self.fixture()
                if flaw == "exception":
                    self.values.fault = True
                elif flaw == "partial":
                    self.values.tamper = lambda vals: vals[:-1]
                elif flaw == "wrong_receipt":
                    self.values.tamper = lambda vals: tuple(replace(x, receipt_ref="fake:receipt") for x in vals)
                else:
                    self.values.tamper = lambda vals: tuple(replace(x, value=True) for x in vals)
                with self.assertRaises((ValueError, RuntimeError)):
                    self.first(f)
                self.assertEqual(f.audit()["committed"], 0)
                self.assertEqual(f.audit()["remaining_synthetic_uc"], 12)
                self.values.fault = False
                self.values.tamper = None
                self.path.unlink()

    def test_faults_before_commit_never_charge_or_publish(self):
        for point in ("after_intake_debit", "after_intention",
                      "after_competition_debit", "before_commit"):
            with self.subTest(point=point):
                f = self.fixture()
                with self.assertRaises(FaultInjected):
                    self.first(f, _fault_at=point)
                self.assertEqual(f.audit()["committed"], 0)
                self.assertEqual(f.audit()["remaining_synthetic_uc"], 12)
                self.assertIsNone(f.lookup(capture_ref="capture:3"))
                self.path.unlink()

    def test_after_commit_lost_ack_resolved_without_second_evaluation(self):
        f = self.fixture()
        with self.assertRaises(CommitAcknowledgmentLost):
            self.first(f, _fault_at="after_commit")
        calls = self.values.calls
        recovered = f.lookup(capture_ref="capture:3")
        self.assertEqual(recovered.competition_uc, 3)
        self.assertEqual(recovered.intake_uc, 1)
        self.assertEqual(f.audit()["remaining_synthetic_uc"], 8)
        with self.assertRaises(ValueError):
            self.first(f)
        self.assertEqual(self.values.calls, calls)
        reopened = CognitiveCycleFixture.reopen(
            path=self.path, life_ref=LIFE,
            observation_source=self.source, valuation_source=self.values)
        self.assertEqual(reopened.lookup(capture_ref="capture:3"), recovered)

    def test_concurrent_two_sessions_charge_only_once(self):
        f = self.fixture()
        second = CognitiveCycleFixture.reopen(
            path=self.path, life_ref=LIFE,
            observation_source=self.source, valuation_source=self.values)
        c = self.source.add(claim())
        def run(obj):
            try:
                return obj.open(claim=c, semantic_ref=A,
                                evidence_ref="evidence:3", ttl_steps=4)
            except ValueError:
                return "REJECTED"
        with ThreadPoolExecutor(max_workers=2) as pool:
            out = list(pool.map(run, (f, second)))
        self.assertEqual(sum(isinstance(r, CycleReceipt) for r in out), 1)
        self.assertEqual(out.count("REJECTED"), 1)
        self.assertEqual(f.audit()["committed"], 1)
        self.assertEqual(f.audit()["remaining_synthetic_uc"], 8)

    def test_reopen_rejects_foreign_life_and_symlink(self):
        self.fixture()
        with self.assertRaises(ValueError):
            CognitiveCycleFixture.reopen(path=self.path, life_ref="life:other",
                                         observation_source=self.source,
                                         valuation_source=self.values)
        link = Path(self.tmp.name) / "shortcut.sqlite"
        link.symlink_to(self.path)
        with self.assertRaises(ValueError):
            CognitiveCycleFixture.reopen(path=link, life_ref=LIFE,
                                         observation_source=self.source,
                                         valuation_source=self.values)

    def test_bad_sqlite_account_or_owner_detected(self):
        f = self.fixture()
        self.first(f)
        with sqlite3.connect(self.path) as c:
            c.execute("UPDATE account SET remaining_uc=remaining_uc+1")
        with self.assertRaises(ValueError):
            f.audit()

    def test_mutated_event_detected_with_recalculated_chain(self):
        f = self.fixture()
        self.first(f)
        with sqlite3.connect(self.path) as c:
            text, old = c.execute("SELECT event_json,previous_hash FROM events WHERE seq=1").fetchone()
            data = json.loads(text)
            data["competition_uc"] = 0
            new_text = _json(data)
            next_hash = _chain(old, new_text)
            c.execute("UPDATE events SET event_json=?, event_hash=? WHERE seq=1", (new_text, next_hash))
            c.execute("UPDATE account SET chain_head=? WHERE id=1", (next_hash,))
        with self.assertRaises(ValueError):
            f.audit()

    def test_untouched_event_json_is_canonical_and_bound_to_source(self):
        f = self.fixture()
        self.first(f)
        with sqlite3.connect(self.path) as c:
            raw, digest = c.execute("SELECT event_json,claim_digest FROM events WHERE seq=1").fetchone()
        d = json.loads(raw)
        self.assertEqual(raw, _json(d))
        self.assertEqual(digest, d["claim_digest"])
        self.assertEqual(d["intake_uc"] + d["competition_uc"], 4)
        self.assertEqual(d["seq"], 1)
        self.assertEqual(d["owner_snapshot"]["current"], f.audit()["intention"])
        self.assertEqual(d["owner_snapshot"]["last_step"], 3)

    def test_audit_replays_without_reauthenticating_external_source(self):
        f = self.fixture()
        self.first(f)
        self.source.override = False
        self.values.fault = True
        # A replayable local hash is NOT independent proof of a lived source.
        report = f.audit()
        self.assertEqual(report["committed"], 1)
        self.assertFalse(report["m11_authenticated"])
        self.assertFalse(report["scheduler_uc_authenticated"])

    def test_goal_change_expires_context_but_never_suppresses_visible_candidates(self):
        f = self.fixture(budget=8)
        self.first(f)
        changed = self.source.add(claim(4, visible=(B, C), goal="goal:thirst"))
        receipt = f.observe(claim=changed)
        self.assertEqual(receipt.intention_kind, "goal_changed")
        self.assertEqual(receipt.competition_uc, 2)
        self.assertIsNone(f.audit()["intention"])
        with sqlite3.connect(self.path) as db:
            (event_raw,) = db.execute("SELECT event_json FROM events WHERE seq=2").fetchone()
        event = json.loads(event_raw)
        self.assertEqual({c["semantic_ref"] for c in event["frame"]["candidates"]}, {B, C})
        self.assertTrue(all(c["intention_ref"] is None for c in event["frame"]["candidates"]))

    def test_unsupported_fault_and_invalid_request_never_create_file(self):
        f = self.fixture()
        c = self.source.add(claim())
        with self.assertRaises(ValueError):
            f.observe(claim=c, _fault_at="m11_power_loss")
        with self.assertRaises(ValueError):
            f.open(claim=c, semantic_ref=A, evidence_ref="evidence:3", ttl_steps=True)
        self.assertEqual(f.audit()["committed"], 0)


if __name__ == "__main__":
    unittest.main()
