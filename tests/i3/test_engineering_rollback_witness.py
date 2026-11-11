"""Engineering-only local witness checks. No organism, World or science run."""
from contextlib import closing
from pathlib import Path
import os
import sqlite3
import tempfile
import unittest

from i3.runtime.birth_reservation import make_reservation, reserve
from i3.runtime import engineering_step_ledger as ledger
from i3.runtime import engineering_rollback_witness as anchor


class SeparateLocalRollbackWitnessTest(unittest.TestCase):
    def setUp(self):
        self.ctx = tempfile.TemporaryDirectory()
        self.addCleanup(self.ctx.cleanup)
        self.dir = Path(self.ctx.name)
        self.life = self.dir / "life"
        self.witness = self.dir / "witness"
        self.life.mkdir()
        self.witness.mkdir()
        self.claim = make_reservation(
            birth_index=11, life_seed=231,
            source_sha256="a"*64, world_sha256="b"*64,
            genome_sha256="c"*64)
        reserve(self.life, self.claim)
        self.genesis = ledger.initialize(
            self.life, self.claim, horizon=3,
            initial_body=[95., 85., 75., 65., 55.], witness_mode=ledger.ANCHOR_MODE)
        self.first = anchor.register(self.witness, self.life, self.claim, self.genesis)

    def make_intent(self, view):
        return {"schema": ledger.INTENT_SCHEMA, "tick_before": view["sequence"],
                "body_before": view["last_body"], "action": "attendre", "param": None,
                "decision_work": {"cycles": 3, "simulated_steps": 4,
                                  "memory_items": 11, "replays": 0}}

    def make_receipt(self, view):
        before = view["last_body"]
        motor = [before[0]-1.0, before[1]-1.0, before[2]-1.0,
                 before[3], before[4]-1.0]
        final = [motor[0]-0.02, *motor[1:4], motor[4]-0.05]
        return {"schema": ledger.RECEIPT_SCHEMA,
                "phase": "POST_PAID_LEARNING", "tick": view["sequence"] + 1,
                "action": "attendre", "param": None,
                "body_after_motor": motor, "body_after_paid_learning": final,
                "decision_paid": {"energy": 0.06, "vigilance": 0.15},
                "learning_paid": {"energy": 0.02, "vigilance": 0.05},
                "death_causes": [], "world_state_sha256": "d"*64,
                "mind_state_sha256": "e"*64}

    def prepare(self):
        view = ledger.inspect(self.life, self.claim)
        intent = self.make_intent(view)
        p = ledger.prepare(self.life, self.claim,
                           expected_head=view["head_sha256"], intent=intent)
        anchor.prepared(self.witness, self.life, self.claim,
                        previous_ledger=view, intent=intent)
        return view, intent, p

    def commit(self, view, intent, token):
        ledger.seal(self.life, self.claim, expected_head=view["head_sha256"],
                    seal_token=token["seal_token"], receipt=self.make_receipt(view))
        return anchor.committed(self.witness, self.life, self.claim,
                                previous_ledger=view, intent=intent)

    def test_register_then_both_phases_advance_identically(self):
        self.assertEqual(self.first["sequence"], 0)
        self.assertFalse(self.first["durable_m11"])
        before, intent, token = self.prepare()
        with self.assertRaisesRegex(PermissionError, "witness rejects"):
            anchor.verify(self.witness, self.life, self.claim, before)
        final = self.commit(before, intent, token)
        view = ledger.inspect(self.life, self.claim)
        self.assertEqual(final["sequence"], 1)
        self.assertEqual(anchor.verify(self.witness, self.life, self.claim, view)["head_sha256"],
                         view["head_sha256"])
        self.assertEqual(view["witness_mode"], ledger.ANCHOR_MODE)

    def test_ledger_prepare_without_witness_never_continues(self):
        view = ledger.inspect(self.life, self.claim)
        ledger.prepare(self.life, self.claim, expected_head=view["head_sha256"],
                       intent=self.make_intent(view))
        with self.assertRaises(PermissionError):
            ledger.inspect(self.life, self.claim)
        with self.assertRaises(PermissionError):
            anchor.verify(self.witness, self.life, self.claim)

    def test_crash_after_witness_prepare_and_before_seal_remains_uncertain(self):
        view, intent, token = self.prepare()
        with self.assertRaises(PermissionError):
            anchor.verify(self.witness, self.life, self.claim)
        with self.assertRaises(PermissionError):
            anchor.prepared(self.witness, self.life, self.claim,
                            previous_ledger=view, intent=intent)
        self.assertEqual(ledger.inspect_pending(self.life, self.claim)["prepared"]["seq"], 1)

    def test_sealed_ledger_but_witness_pending_refuses_reconstruction(self):
        view, intent, p = self.prepare()
        ledger.seal(self.life, self.claim, expected_head=view["head_sha256"],
                    seal_token=p["seal_token"], receipt=self.make_receipt(view))
        with self.assertRaises(PermissionError):
            anchor.verify(self.witness, self.life, self.claim)
        # Explicitly do not auto-promote a previously prepared witness after a crash.

    def test_rollback_of_only_ledger_is_detected(self):
        first, intent1, p1 = self.prepare()
        self.commit(first, intent1, p1)
        checkpoint = self.dir / "old-ledger.sqlite3"
        # SQLite hot backup is a coherent snapshot of committed data only.
        with closing(sqlite3.connect(self.life / ledger.DB_NAME)) as src:
            with closing(sqlite3.connect(checkpoint)) as dst:
                src.backup(dst)
        second, intent2, p2 = self.prepare()
        self.commit(second, intent2, p2)
        self.assertEqual(anchor.verify(self.witness, self.life, self.claim)["sequence"], 2)
        # An adversary can restore a consistent OLD *ledger* file, not witness.
        os.replace(checkpoint, self.life / ledger.DB_NAME)
        for suffix in ("-wal", "-shm"):
            path = self.life / (ledger.DB_NAME+suffix)
            if path.exists():
                path.unlink()
        self.assertEqual(ledger.inspect(self.life, self.claim)["sequence"], 1)
        with self.assertRaisesRegex(PermissionError, "witness rejects"):
            anchor.verify(self.witness, self.life, self.claim)

    def test_both_local_files_rolled_back_together_are_not_protected(self):
        """Negative capability test: no independent off-host monotonic authority."""
        first, intent1, p1 = self.prepare()
        self.commit(first, intent1, p1)
        old_life = self.dir / "old-life.sqlite3"
        old_witness = self.dir / "old-witness.sqlite3"
        for source, target in ((self.life / ledger.DB_NAME, old_life),
                               (self.witness / anchor.DB_NAME, old_witness)):
            with closing(sqlite3.connect(source)) as src:
                with closing(sqlite3.connect(target)) as dst:
                    src.backup(dst)
        second, intent2, p2 = self.prepare()
        self.commit(second, intent2, p2)
        self.assertEqual(anchor.verify(self.witness, self.life, self.claim)["sequence"], 2)
        for copy, path in ((old_life, self.life / ledger.DB_NAME),
                           (old_witness, self.witness / anchor.DB_NAME)):
            os.replace(copy, path)
            for suffix in ("-wal", "-shm"):
                companion = path.with_name(path.name + suffix)
                if companion.exists():
                    companion.unlink()
        # It is deliberately impossible for two mutually rolled-back local
        # databases to prove that they once held a later valid state.
        self.assertEqual(anchor.verify(self.witness, self.life, self.claim)["sequence"], 1)

    def test_witness_cannot_share_directory_and_foreign_db_fails(self):
        with self.assertRaises(PermissionError):
            anchor.validate_location(self.life, self.life)
        with self.assertRaises(PermissionError):
            anchor.register(self.witness, self.life, self.claim, self.genesis)
        with closing(sqlite3.connect(self.witness / anchor.DB_NAME)) as conn:
            conn.execute("PRAGMA application_id=41")
        with self.assertRaises(PermissionError):
            anchor.verify(self.witness, self.life, self.claim)


if __name__ == "__main__":
    unittest.main()
