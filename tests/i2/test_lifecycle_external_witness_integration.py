"""Read-only witness comparison against the actual synthetic v3 SQLite owner.

GitHub CI uses real I2 types. Witness below is not an M11 service.
"""
from __future__ import annotations

from pathlib import Path
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from i2.modules.cognitive_cycle_fixture import CognitiveCycleFixture, LIFECYCLE_SCHEMA  # noqa: E402
from i2.modules.lifecycle_external_witness import (  # noqa: E402
    LatestWitness, WITNESS_SCHEMA, compare_audit, verify_fixture,
)

LIFE = "life:synthetic-anchor-integration"
GENESIS = "genesis:synthetic-anchor-integration"


class EmptySource:
    def verify(self, *, life_ref, claim, digest):
        raise AssertionError("no cognition allowed in this test")


class EmptyValues:
    def evaluate_batch(self, *, frame, receipts):
        raise AssertionError("no valuation allowed in this test")


class Current:
    def verify_current(self, *, life_ref, frame, advice):
        raise AssertionError("no Action Control activity")


class Safety:
    def check(self, *, life_ref, frame, candidate_ref, control_receipt_ref):
        raise AssertionError("no safety review activity")


class Terminal:
    def __init__(self):
        self.calls = 0

    def verify_terminal(self, *, life_ref, genesis_ref, physical_step,
                        terminal_ref, evidence_ref, previous_head):
        self.calls += 1
        return (life_ref == LIFE and genesis_ref == GENESIS and physical_step == 0
                and terminal_ref.startswith("terminal:") and
                evidence_ref == "evidence:synthetic-term")


def checkpoint(snapshot):
    return LatestWitness(
        WITNESS_SCHEMA, snapshot["life_ref"], snapshot["genesis_ref"],
        snapshot["schema"], snapshot["committed"], snapshot["last_step"],
        snapshot["chain_head"], snapshot["terminal_ref"],
        snapshot["terminal_step"], "proof:external-test-only",
    )


class Witness:
    """In-memory latest-anchor test double; no signing, no durability."""
    def __init__(self, record):
        self.record = record
        self.calls = []

    def read_latest(self, *, life_ref, genesis_ref):
        self.calls.append("read")
        return self.record

    def verify_latest(self, *, record):
        self.calls.append("verify")
        return record is self.record


class SQLiteWitnessIntegration(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.path = Path(self.t.name) / "v3.sqlite"
        self.terminal = Terminal()
        self.ports = dict(
            life_ref=LIFE, genesis_ref=GENESIS,
            observation_source=EmptySource(), valuation_source=EmptyValues(),
            current_source=Current(), safety_source=Safety(),
            terminal_source=self.terminal,
        )

    def create(self, path=None):
        return CognitiveCycleFixture.create(path=path or self.path,
                                            synthetic_uc=4, **self.ports)

    def reopen(self, path=None):
        return CognitiveCycleFixture.reopen(path=path or self.path, **self.ports)

    def seal(self, fixture, ref="terminal:death-A"):
        return fixture.seal_terminal(physical_step=0, terminal_ref=ref,
                                     evidence_ref="evidence:synthetic-term")

    def test_real_v3_schema_is_bound_to_witness_contract(self):
        self.assertEqual(LIFECYCLE_SCHEMA, "i2-unified-cognitive-lifecycle-fixture-v3")

    def test_exact_empty_v3_inspection_remains_nonmotor(self):
        f = self.create()
        anchor = Witness(checkpoint(f.audit()))
        result = verify_fixture(fixture=f, witness=anchor)
        self.assertEqual(result.status, "MATCHED_OPEN_INSPECTION")
        self.assertEqual(result.motor_authority, "NONE")
        self.assertFalse(result.resumption_authorized)
        self.assertEqual(anchor.calls, ["read", "verify"])

    def test_terminal_v3_cold_reopen_matches_independent_latest(self):
        f = self.create()
        self.seal(f)
        anchor = Witness(checkpoint(f.audit()))
        frozen = self.reopen()
        result = verify_fixture(fixture=frozen, witness=anchor)
        self.assertEqual(result.status, "MATCHED_TERMINAL_INSPECTION")
        self.assertEqual(result.terminal_ref, "terminal:death-A")
        self.assertFalse(result.resumption_authorized)
        self.assertEqual(self.terminal.calls, 1)

    def test_old_sqlite_backup_after_terminal_is_rejected(self):
        f = self.create()
        stale = Path(self.t.name) / "stale.sqlite"
        with sqlite3.connect(str(self.path)) as src, sqlite3.connect(str(stale)) as dst:
            src.backup(dst)
        # Local audit of the old file still passes. The external latest differs.
        old = self.reopen(stale)
        self.assertEqual(old.audit()["committed"], 0)
        self.seal(f)
        anchor = Witness(checkpoint(f.audit()))
        with self.assertRaisesRegex(ValueError, "stale local copy"):
            verify_fixture(fixture=old, witness=anchor)
        self.assertEqual(anchor.calls, ["read", "verify"])

    def test_different_terminal_branch_same_seq_is_rejected(self):
        original = self.create()
        clonepath = Path(self.t.name) / "fork.sqlite"
        with sqlite3.connect(str(self.path)) as src, sqlite3.connect(str(clonepath)) as dst:
            src.backup(dst)
        fork = self.reopen(clonepath)
        self.seal(original, ref="terminal:A")
        self.seal(fork, ref="terminal:B")
        self.assertEqual(original.audit()["committed"], fork.audit()["committed"])
        anchor = Witness(checkpoint(original.audit()))
        with self.assertRaisesRegex(ValueError, "fork"):
            verify_fixture(fixture=fork, witness=anchor)

    def test_unanchored_post_commit_extension_is_rejected(self):
        f = self.create()
        old_anchor = Witness(checkpoint(f.audit()))
        self.seal(f)
        with self.assertRaisesRegex(ValueError, "unanchored local extension"):
            verify_fixture(fixture=f, witness=old_anchor)

    def test_witness_unavailable_is_fail_closed_not_a_local_fallback(self):
        f = self.create()
        with self.assertRaisesRegex(ValueError, "mandatory"):
            verify_fixture(fixture=f, witness=None)

    def test_altered_sqlite_fails_local_audit_before_witness_contact(self):
        f = self.create()
        anchor = Witness(checkpoint(f.audit()))
        with sqlite3.connect(str(self.path)) as c:
            c.execute("UPDATE account SET chain_head=? WHERE id=1", ("e" * 64,))
        with self.assertRaises(ValueError):
            verify_fixture(fixture=f, witness=anchor)
        self.assertEqual(anchor.calls, [])

    def test_wrong_fixture_schema_refuses_witness_proof(self):
        legacy = Path(self.t.name) / "old-v1.sqlite"
        v1 = CognitiveCycleFixture.create(path=legacy, life_ref=LIFE,
                    synthetic_uc=4, observation_source=EmptySource(),
                    valuation_source=EmptyValues())
        with self.assertRaisesRegex(ValueError, "exact I2 synthetic v3"):
            verify_fixture(fixture=v1, witness=Witness(checkpoint(self.create().audit())))


    def cold_audit_in_separate_process(self, path):
        """Audit an existing SQLite snapshot in a separate Python process.

        The test still uses synthetic ports and proves no remote custody.
        Crucially, neither an in-memory owner nor a preloaded journal can
        provide the child's result: it must reopen the database on disk.
        """
        child = """
import json
from pathlib import Path
import sys
sys.path.insert(0, sys.argv[1])
from i2.modules.cognitive_cycle_fixture import CognitiveCycleFixture

class UnusedObservation:
    def verify(self, **kwargs):
        raise AssertionError("cold audit must not read perception")
class UnusedValues:
    def evaluate_batch(self, **kwargs):
        raise AssertionError("cold audit must not recompute external values")
class UnusedCurrent:
    def verify_current(self, **kwargs):
        raise AssertionError("cold audit must not review a motor action")
class UnusedSafety:
    def check(self, **kwargs):
        raise AssertionError("cold audit must not inspect safety source")
class UnusedTerminal:
    def verify_terminal(self, **kwargs):
        raise AssertionError("cold audit must not attest a new terminal")
fixture = CognitiveCycleFixture.reopen(
    path=Path(sys.argv[2]), life_ref=sys.argv[3],
    genesis_ref=sys.argv[4], observation_source=UnusedObservation(),
    valuation_source=UnusedValues(), current_source=UnusedCurrent(),
    safety_source=UnusedSafety(), terminal_source=UnusedTerminal(),
)
print(json.dumps(fixture.audit(), sort_keys=True))
"""
        result = subprocess.run(
            [sys.executable, "-c", child, str(ROOT / "src"), str(path),
             LIFE, GENESIS],
            cwd=ROOT, capture_output=True, text=True, timeout=15, check=True,
        )
        return json.loads(result.stdout)

    def test_stale_backup_rejected_after_cold_process_audit(self):
        fixture = self.create()
        old_path = Path(self.t.name) / "old-cold.sqlite"
        with sqlite3.connect(str(self.path)) as src, sqlite3.connect(str(old_path)) as dst:
            src.backup(dst)
        self.seal(fixture)
        latest = self.cold_audit_in_separate_process(self.path)
        stale = self.cold_audit_in_separate_process(old_path)
        self.assertEqual(latest["committed"], 1)
        self.assertEqual(stale["committed"], 0)
        with self.assertRaisesRegex(ValueError, "stale local copy"):
            compare_audit(report=stale, witness=Witness(checkpoint(latest)))

    def test_cold_process_fork_and_unanchored_extension_fail_closed(self):
        original = self.create()
        fork_path = Path(self.t.name) / "cold-fork.sqlite"
        with sqlite3.connect(str(self.path)) as src, sqlite3.connect(str(fork_path)) as dst:
            src.backup(dst)
        fork = self.reopen(fork_path)
        self.seal(original, ref="terminal:cold-A")
        self.seal(fork, ref="terminal:cold-B")
        a = self.cold_audit_in_separate_process(self.path)
        b = self.cold_audit_in_separate_process(fork_path)
        self.assertEqual(a["committed"], b["committed"])
        self.assertNotEqual(a["chain_head"], b["chain_head"])
        with self.assertRaisesRegex(ValueError, "fork"):
            compare_audit(report=b, witness=Witness(checkpoint(a)))
        genesis_only = dict(a, committed=0, last_step=-1,
                            chain_head="0" * 64, synthetic_terminal=False,
                            terminal_ref=None, terminal_step=None)
        with self.assertRaisesRegex(ValueError, "unanchored local extension"):
            compare_audit(report=a, witness=Witness(checkpoint(genesis_only)))


if __name__ == "__main__":
    unittest.main()
