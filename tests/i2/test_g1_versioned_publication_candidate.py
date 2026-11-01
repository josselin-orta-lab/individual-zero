"""G1/R1 reviewer-only SQLite reference: keep two FULL state revisions in ONE owner.

Falsifiable question: after a private COMMIT, can a reader still obtain the
exact older, externally attested full state following a cold reopen?
This is NOT a living I2 owner, M11 attestation, external signer or motor/physics.
`verified=True` and `Anchor` are deliberately injected trust ASSUMPTIONS.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

ZERO = "0" * 64
GENESIS = {"energy": 4, "inventory": 0, "uc": 40,
           "memory_version": 0, "observed_result": None, "terminal": False}


class Refusal(ValueError):
    """Do not guess the public body revision or retry a pending step."""


@dataclass(frozen=True)
class Anchor:
    revision: int
    digest: str
    terminal: bool


def _serialize(state: dict) -> str:
    if (type(state) is not dict or state.keys() != GENESIS.keys() or
            any(type(state[k]) is not int or state[k] < 0 for k in
                ("energy", "inventory", "uc", "memory_version")) or
            type(state["terminal"]) is not bool):
        raise Refusal("invalid complete owner state")
    if state["observed_result"] not in (None, "benefit", "harm", "death"):
        raise Refusal("invalid outcome")
    if state["terminal"] and state["observed_result"] != "death":
        raise Refusal("inconsistent terminal")
    return json.dumps(state, sort_keys=True, separators=(",", ":"))


def _digest(parent: str, revision: int, raw: str) -> str:
    return sha256(f"{parent}:{revision}:{raw}".encode()).hexdigest()


class VersionedOwnerCandidate:
    """Test-only one-transaction state history; no WorldBody transitions."""

    def __init__(self, path: Path, *, create: bool = False):
        self.db = sqlite3.connect(path)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=FULL")
        self._same_process_pending: int | None = None
        if create:
            self.db.executescript("""
                CREATE TABLE versions (
                  revision INTEGER PRIMARY KEY,
                  digest TEXT UNIQUE NOT NULL,
                  parent TEXT NOT NULL,
                  state TEXT NOT NULL);
                CREATE TABLE attempt (
                  id INTEGER PRIMARY KEY CHECK(id=1), pending INTEGER);
                INSERT INTO attempt VALUES(1,NULL);
            """)
            raw = _serialize(GENESIS)
            self.db.execute("INSERT INTO versions VALUES(0,?,?,?)",
                            (_digest(ZERO, 0, raw), ZERO, raw))
            self.db.commit()

    def close(self) -> None:
        self.db.close()

    def genesis_anchor(self) -> Anchor:
        return Anchor(0, self.db.execute(
            "SELECT digest FROM versions WHERE revision=0").fetchone()[0], False)

    def pending(self) -> int | None:
        return self.db.execute("SELECT pending FROM attempt WHERE id=1").fetchone()[0]

    def public(self, anchor: Anchor, *, verified: bool) -> dict:
        if verified is not True:
            raise Refusal("missing independently verified fresh head")
        if type(anchor.revision) is not int or anchor.revision < 0:
            raise Refusal("invalid anchor")
        parent = ZERO
        state = None
        digest = None
        for i in range(anchor.revision + 1):
            row = self.db.execute(
                "SELECT digest,parent,state FROM versions WHERE revision=?", (i,)
            ).fetchone()
            if row is None:
                raise Refusal("attested revision absent from local owner")
            digest, predecessor, raw = row
            try:
                state = json.loads(raw)
                if (_serialize(state) != raw or predecessor != parent or
                        digest != _digest(parent, i, raw)):
                    raise Refusal("inconsistent local owner history")
            except (ValueError, TypeError) as error:
                raise Refusal("invalid state history") from error
            parent = digest
        if digest != anchor.digest or state["terminal"] != anchor.terminal:
            raise Refusal("owner disagrees with external anchor")
        return state

    def stage(self, anchor: Anchor, body: dict, *, fail_before_commit=False) -> Anchor:
        """All state fields + pending flag in the SAME SQLite COMMIT."""
        try:
            self.db.execute("BEGIN IMMEDIATE")
            previous = self.public(anchor, verified=True)
            if anchor.terminal or previous["terminal"]:
                raise Refusal("terminal state is absorbing")
            if self.pending() is not None:
                raise Refusal("unresolved prior private attempt")
            latest = self.db.execute("SELECT MAX(revision) FROM versions").fetchone()[0]
            if latest != anchor.revision:
                raise Refusal("private or forked successor already exists")
            raw = _serialize(body)
            if body["uc"] > previous["uc"]:
                raise Refusal("UC refund forbidden")
            revision = latest + 1
            head = _digest(anchor.digest, revision, raw)
            self.db.execute("INSERT INTO versions VALUES(?,?,?,?)",
                            (revision, head, anchor.digest, raw))
            self.db.execute("UPDATE attempt SET pending=? WHERE id=1", (revision,))
            if fail_before_commit:
                raise RuntimeError("injected failure before local COMMIT")
            self.db.commit()
        except BaseException:
            self.db.rollback()
            raise
        self._same_process_pending = revision
        return Anchor(revision, head, body["terminal"])

    def acknowledge_mock_cas(self, new_anchor: Anchor, *, received: bool) -> None:
        """Only an explicit same-process hypothetical CAS ACK can clear pending.

        Crash/lost ACK leaves pending indefinitely; no recovery API exists.
        This does NOT authenticate that acknowledgment in a real trust domain.
        """
        if not received or self._same_process_pending != new_anchor.revision:
            raise Refusal("uncertain CAS: no resumption")
        if self.pending() != new_anchor.revision:
            raise Refusal("pending attempt mismatch")
        self.public(new_anchor, verified=True)
        self.db.execute("UPDATE attempt SET pending=NULL WHERE id=1")
        self.db.commit()
        self._same_process_pending = None


def snapshot(*, result="benefit", terminal=False) -> dict:
    return {"energy": 0 if terminal else 3, "inventory": 1,
            "uc": 36, "memory_version": 0,
            "observed_result": result, "terminal": terminal}


class G1RetainedRevisionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "single-owner.sqlite"
        self.owner = VersionedOwnerCandidate(self.path, create=True)
        self.addCleanup(lambda: self.owner.close())
        self.g0 = self.owner.genesis_anchor()

    def cold_reopen(self):
        self.owner.close()
        self.owner = VersionedOwnerCandidate(self.path)

    def test_c5_old_full_state_retrievable_after_private_commit_and_cold_reopen(self):
        new = self.owner.stage(self.g0, snapshot())
        self.cold_reopen()
        self.assertEqual(self.owner.public(self.g0, verified=True), GENESIS)
        self.assertEqual(self.owner.pending(), 1)
        # The candidate anchor `new` is NOT automatically trusted. An
        # external CAS was NOT called, so do not publish the private state.
        self.assertEqual(new.revision, 1)
        self.assertIsNone(self.owner.public(self.g0, verified=True)["observed_result"])

    def test_c7_public_new_state_only_after_hypothetical_cas_ack(self):
        candidate = self.owner.stage(self.g0, snapshot())
        self.assertEqual(self.owner.public(self.g0, verified=True), GENESIS)
        # This explicit ACK is a test input, NOT a real M11 signature or CAS.
        self.owner.acknowledge_mock_cas(candidate, received=True)
        self.cold_reopen()
        self.assertIsNone(self.owner.pending())
        self.assertEqual(self.owner.public(candidate, verified=True), snapshot())
        # The full historical snapshot remains retained but is no longer
        # permitted as input for a new step once the external head advanced.
        with self.assertRaises(Refusal):
            self.owner.stage(self.g0, snapshot())

    def test_c4_before_commit_rollback_and_c8_lost_ack_fail_closed(self):
        with self.assertRaisesRegex(RuntimeError, "injected failure"):
            self.owner.stage(self.g0, snapshot(), fail_before_commit=True)
        self.cold_reopen()
        self.assertIsNone(self.owner.pending())
        with self.assertRaisesRegex(Refusal, "absent"):
            self.owner.public(Anchor(1, "a" * 64, False), verified=True)
        new = self.owner.stage(self.g0, snapshot())
        self.cold_reopen()
        with self.assertRaisesRegex(Refusal, "uncertain CAS"):
            self.owner.acknowledge_mock_cas(new, received=True)
        with self.assertRaisesRegex(Refusal, "unresolved prior private"):
            self.owner.stage(new, snapshot())

    def test_c6_bad_anchor_or_lost_history_refuses_publication(self):
        self.owner.stage(self.g0, snapshot())
        with self.assertRaisesRegex(Refusal, "fresh head"):
            self.owner.public(self.g0, verified=False)
        with self.assertRaisesRegex(Refusal, "disagrees"):
            self.owner.public(Anchor(0, "f" * 64, False), verified=True)
        self.owner.db.execute("DELETE FROM versions WHERE revision=0")
        self.owner.db.commit()
        with self.assertRaisesRegex(Refusal, "absent"):
            self.owner.public(self.g0, verified=True)

    def test_c10_external_terminal_anchor_blocks_old_copy_but_local_fake_does_not(self):
        old_copy = Path(self.temp.name) / "old-copy.sqlite"
        with sqlite3.connect(old_copy) as dest:
            self.owner.db.backup(dest)
        new = self.owner.stage(self.g0, snapshot(result="death", terminal=True))
        self.owner.acknowledge_mock_cas(new, received=True)
        with self.assertRaisesRegex(Refusal, "terminal"):
            self.owner.stage(new, snapshot())
        restored = VersionedOwnerCandidate(old_copy)
        try:
            with self.assertRaisesRegex(Refusal, "absent"):
                restored.public(new, verified=True)
            # Negative case: forged same-domain old anchor makes dead life look alive.
            self.assertFalse(restored.public(self.g0, verified=True)["terminal"])
        finally:
            restored.close()


if __name__ == "__main__":
    unittest.main()
