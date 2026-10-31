"""Synthetic SQLite ACID fixture only: no I2 birth, M11, or Scheduler ledger."""
from dataclasses import replace
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import copy
import json
import sqlite3
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from i2.modules.intention_continuity import FirstPersonCapture  # noqa: E402
from i2.modules.intention_ingress import ObservationClaim, INTAKE_UC  # noqa: E402
from i2.modules.intention_atomic_fixture import (  # noqa: E402
    AtomicIntentionFixture, FaultInjected, CommitAcknowledgmentLost, SCHEMA, _chain, _canonical,
)

LIFE = "life:synthetic-i2"
SEM = "affordance:berry_a"
GOAL = "goal:food"


def claim(step, *, life=LIFE, visible=True, goal=GOAL, contradicted=False,
          ref=None, evidence="evidence:lived"):
    return ObservationClaim(
        life_ref=life,
        source_event_ref=f"source:synthetic:{step}",
        subjective_evidence_refs=(evidence,),
        capture=FirstPersonCapture(
            step=step, ref=ref or f"capture:{step}", goal_ref=goal,
            accessible_semantics=(SEM,) if visible else (),
            contradicted_semantics=(SEM,) if contradicted else (),
        ),
    )


class FakeSource:
    """Allowlist fixture only. Neither an I2 M11 nor an authenticated port."""
    def __init__(self):
        self.allowed = set()
        self.calls = []
        self.override = None

    def allow(self, c):
        self.allowed.add(c.digest())
        return c

    def verify(self, *, life_ref, claim, digest):
        self.calls.append((life_ref, digest))
        return digest in self.allowed if self.override is None else self.override


class TestAtomicIntentionFixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db = Path(self.temp.name) / "synthetic.db"
        self.src = FakeSource()
        self.store = AtomicIntentionFixture.create(
            path=self.db, life_ref=LIFE, synthetic_uc=6, observation_authority=self.src,
        )

    def open(self, step=3, **kw):
        c = self.src.allow(claim(step, **kw))
        return self.store.open(claim=c, semantic_ref=SEM,
                               evidence_ref="evidence:lived", ttl_steps=8)

    def test_empty_fixture_is_not_living_engine(self):
        x = self.store.audit()
        self.assertEqual(x["schema"], SCHEMA)
        self.assertEqual(x["committed"], 0)
        self.assertEqual(x["remaining_synthetic_uc"], 6)
        self.assertIsNone(x["intention"])
        for key in ("m11_authenticated", "real_scheduler_uc", "motor_authority"):
            self.assertIs(x[key], False)
        for method in ("birth", "run_step", "cold_recover", "admit_motor", "world"):
            self.assertFalse(hasattr(self.store, method))

    def test_open_is_one_atomic_charge_and_semantic_change(self):
        a = self.open()
        self.assertEqual(a.kind, "opened")
        self.assertEqual(a.units, INTAKE_UC)
        self.assertEqual(self.store.audit()["committed"], 1)
        self.assertEqual(self.store.audit()["remaining_synthetic_uc"], 5)
        self.assertEqual(self.store.audit()["intention"]["semantic_ref"], SEM)
        self.assertEqual(self.store.lookup(capture_ref="capture:3"), a)
        self.assertNotIn("command", str(self.store.audit()))

    def test_reopen_replays_exact_owner_state_from_sqlite(self):
        self.open()
        self.store.observe(claim=self.src.allow(claim(4, visible=False)))
        prior = self.store.audit()
        new = AtomicIntentionFixture.reopen(
            path=self.db, life_ref=LIFE, observation_authority=self.src,
        )
        self.assertEqual(new.audit(), prior)
        self.assertEqual(new.audit()["intention"]["status"], "suspended")
        r = new.observe(claim=self.src.allow(claim(5)))
        self.assertEqual(r.kind, "resumed")
        self.assertEqual(self.store.audit()["intention"]["status"], "active")

    def test_expiration_is_replayed_and_persisted(self):
        c = self.src.allow(claim(3))
        self.store.open(claim=c, semantic_ref=SEM, evidence_ref="evidence:lived", ttl_steps=2)
        r = self.store.observe(claim=self.src.allow(claim(6)))
        self.assertEqual(r.kind, "expired")
        self.assertIsNone(self.store.audit()["intention"])
        self.assertIsNone(AtomicIntentionFixture.reopen(
            path=self.db, life_ref=LIFE, observation_authority=self.src).audit()["intention"])

    def test_rejection_by_source_is_free_and_does_not_publish(self):
        c = claim(3)
        with self.assertRaises(ValueError):
            self.store.open(claim=c, semantic_ref=SEM,
                            evidence_ref="evidence:lived", ttl_steps=3)
        self.assertEqual(self.store.audit()["committed"], 0)
        self.assertEqual(self.store.audit()["remaining_synthetic_uc"], 6)

    def test_source_must_return_exact_true(self):
        self.src.override = 1
        with self.assertRaises(ValueError):
            self.store.observe(claim=claim(3))
        self.assertEqual(self.store.audit()["committed"], 0)

    def test_foreign_life_never_charged_even_if_source_accepts(self):
        c = self.src.allow(claim(3, life="life:alien"))
        with self.assertRaises(ValueError):
            self.store.observe(claim=c)
        self.assertEqual(self.src.calls, [])
        self.assertEqual(self.store.audit()["committed"], 0)

    def test_open_refuses_evidence_not_present_in_personal_claim(self):
        c = self.src.allow(claim(3))
        with self.assertRaises(ValueError):
            self.store.open(claim=c, semantic_ref=SEM,
                            evidence_ref="evidence:oracle", ttl_steps=3)
        self.assertEqual(self.src.calls, [])
        self.assertEqual(self.store.audit()["remaining_synthetic_uc"], 6)

    def test_invalid_request_is_free_preflight(self):
        c = self.src.allow(claim(3))
        for ttl in (0, -1, True, 65, 1.0):
            with self.subTest(ttl=ttl), self.assertRaises(ValueError):
                self.store.open(claim=c, semantic_ref=SEM,
                                evidence_ref="evidence:lived", ttl_steps=ttl)
        self.assertEqual(self.store.audit()["committed"], 0)
        self.assertEqual(self.src.calls, [])

    def test_policy_rejection_is_charged_once_without_owner_change(self):
        self.open()
        current = self.store.audit()["intention"]
        c = self.src.allow(claim(4))
        paid = self.store.open(claim=c, semantic_ref=SEM,
                               evidence_ref="evidence:lived", ttl_steps=4)
        self.assertEqual(paid.kind, "policy_rejected")
        self.assertEqual(self.store.audit()["remaining_synthetic_uc"], 4)
        self.assertEqual(self.store.audit()["intention"], current)
        with self.assertRaises(ValueError):
            self.store.observe(claim=c)
        self.assertEqual(self.store.audit()["remaining_synthetic_uc"], 4)
        # A later, genuinely different capture remains allowed.
        r = self.store.observe(claim=self.src.allow(claim(5)))
        self.assertEqual(r.kind, "retained")

    def test_one_commit_per_capture_no_double_spend_across_instances(self):
        self.open()
        second = AtomicIntentionFixture.reopen(
            path=self.db, life_ref=LIFE, observation_authority=self.src,
        )
        c = self.src.allow(claim(3))
        with self.assertRaises(ValueError):
            second.observe(claim=c)
        with self.assertRaises(ValueError):
            self.store.observe(claim=self.src.allow(claim(2)))
        with self.assertRaises(ValueError):
            self.store.observe(claim=self.src.allow(claim(4, ref="capture:3")))
        self.assertEqual(self.store.audit()["remaining_synthetic_uc"], 5)

    def test_digest_conflict_changes_content_and_is_not_replayable(self):
        self.open()
        other = replace(claim(3), source_event_ref="source:different")
        self.assertNotEqual(other.digest(), claim(3).digest())
        with self.assertRaises(ValueError):
            self.store.observe(claim=self.src.allow(other))
        self.assertEqual(self.store.audit()["committed"], 1)

    def test_synthetic_uc_exhaustion_rolls_back(self):
        self.open()
        for step in range(4, 9):
            self.store.observe(claim=self.src.allow(claim(step)))
        self.assertEqual(self.store.audit()["remaining_synthetic_uc"], 0)
        before = copy.deepcopy(self.store.audit())
        with self.assertRaises(ValueError):
            self.store.observe(claim=self.src.allow(claim(9)))
        self.assertEqual(self.store.audit(), before)

    def test_injected_failures_rollback_real_sqlite_debit_and_owner(self):
        for point in ("after_debit", "after_policy", "before_commit"):
            with self.subTest(point=point):
                c = self.src.allow(claim(3))
                with self.assertRaises(FaultInjected):
                    self.store.open(claim=c, semantic_ref=SEM,
                                    evidence_ref="evidence:lived", ttl_steps=4,
                                    _fault_at=point)
                restarted = AtomicIntentionFixture.reopen(
                    path=self.db, life_ref=LIFE, observation_authority=self.src,
                )
                self.assertEqual(restarted.audit()["committed"], 0)
                self.assertEqual(restarted.audit()["remaining_synthetic_uc"], 6)
                self.assertIsNone(restarted.lookup(capture_ref="capture:3"))
        self.assertEqual(self.open().kind, "opened")
        self.assertEqual(self.store.audit()["remaining_synthetic_uc"], 5)

    def test_post_commit_ack_loss_does_not_retry_charged_work(self):
        c = self.src.allow(claim(3))
        with self.assertRaises(CommitAcknowledgmentLost):
            self.store.open(claim=c, semantic_ref=SEM,
                            evidence_ref="evidence:lived", ttl_steps=8,
                            _fault_at="after_commit")
        restarted = AtomicIntentionFixture.reopen(
            path=self.db, life_ref=LIFE, observation_authority=self.src,
        )
        original = restarted.lookup(capture_ref=c.capture.ref)
        self.assertEqual(original.kind, "opened")
        self.assertEqual(restarted.audit()["remaining_synthetic_uc"], 5)
        with self.assertRaises(ValueError):
            restarted.open(claim=c, semantic_ref=SEM,
                           evidence_ref="evidence:lived", ttl_steps=8)
        self.assertEqual(restarted.lookup(capture_ref=c.capture.ref), original)

    def test_event_chain_corruption_refuses_reopen(self):
        self.open()
        with sqlite3.connect(self.db) as db:
            db.execute("UPDATE events SET event_hash=? WHERE seq=1", ("0" * 64,))
        with self.assertRaises(ValueError):
            AtomicIntentionFixture.reopen(path=self.db, life_ref=LIFE,
                                         observation_authority=self.src)

    def test_account_owner_tamper_refuses_reopen(self):
        self.open()
        with sqlite3.connect(self.db) as db:
            db.execute("UPDATE account SET owner_json=?", (json.dumps({"command": "eat"}),))
        with self.assertRaises(ValueError):
            self.store.audit()

    def test_event_content_tamper_rejects_even_if_sqlite_crc_valid(self):
        self.open()
        with sqlite3.connect(self.db) as db:
            event = json.loads(db.execute("SELECT event_json FROM events").fetchone()[0])
            event["owner_snapshot"]["current"]["accumulator"] = 10
            db.execute("UPDATE events SET event_json=?", (json.dumps(event),))
        with self.assertRaises(ValueError):
            self.store.audit()

    def test_missing_database_does_not_create_new_life_or_fixture(self):
        missing = Path(self.temp.name) / "missing.db"
        with self.assertRaises(ValueError):
            AtomicIntentionFixture.reopen(path=missing, life_ref=LIFE,
                                         observation_authority=self.src)
        self.assertFalse(missing.exists())

    def test_reopen_rejects_foreign_identity(self):
        with self.assertRaises(ValueError):
            AtomicIntentionFixture.reopen(path=self.db, life_ref="life:foreign",
                                         observation_authority=self.src)

    def test_existing_file_cannot_be_reinitialized_as_new_identity(self):
        before = self.store.audit()
        with self.assertRaises(FileExistsError):
            AtomicIntentionFixture.create(path=self.db, life_ref="life:new",
                                          synthetic_uc=999, observation_authority=self.src)
        self.assertEqual(self.store.audit(), before)

    def test_concurrent_requests_for_one_capture_commit_once(self):
        c = self.src.allow(claim(3))
        other = AtomicIntentionFixture.reopen(
            path=self.db, life_ref=LIFE, observation_authority=self.src,
        )
        def run(obj):
            try:
                return obj.open(claim=c, semantic_ref=SEM,
                                evidence_ref="evidence:lived", ttl_steps=8)
            except ValueError:
                return None
        with ThreadPoolExecutor(max_workers=2) as pool:
            result = list(pool.map(run, (self.store, other)))
        self.assertEqual(sum(x is not None for x in result), 1)
        self.assertEqual(self.store.audit()["remaining_synthetic_uc"], 5)
        self.assertEqual(self.store.audit()["committed"], 1)

    def test_replayed_owner_rejects_even_rehashed_corrupt_log(self):
        self.open()
        with sqlite3.connect(self.db) as db:
            raw = db.execute("SELECT event_json, previous_hash FROM events WHERE seq=1").fetchone()
            event = json.loads(raw[0])
            event["owner_snapshot"]["current"]["status"] = "suspended"
            rewritten = _canonical(event)
            new_hash = _chain(raw[1], rewritten)
            db.execute("UPDATE events SET event_json=?,event_hash=? WHERE seq=1",
                       (rewritten, new_hash))
            db.execute("UPDATE account SET chain_head=? WHERE id=1", (new_hash,))
        with self.assertRaisesRegex(ValueError, "policy replay"):
            self.store.audit()

    def test_local_hash_chain_is_not_external_m11_authenticity(self):
        self.open()
        a = self.store.audit()
        self.assertEqual(len(a["chain_head"]), 64)
        self.assertFalse(a["m11_authenticated"])
        self.assertFalse(a["real_scheduler_uc"])
        self.assertNotIn("signature", a)
        self.assertNotIn("command", str(a))


if __name__ == "__main__":
    unittest.main()
