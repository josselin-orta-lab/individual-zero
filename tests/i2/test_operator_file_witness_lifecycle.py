"""Integration of two inert fixtures across real process exits, not M11."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from i2.modules.lifecycle_external_witness import (
    LatestWitness, WITNESS_SCHEMA, compare_audit, WitnessRefusal,
)
from i2.modules.operator_file_witness import OperatorFileWitness, UNTRUSTED_PROOF

KEY = b"test-only-custody-key-not-a-real-independent-authority"
LIFE = "life:synthetic-crash-custody"
GENESIS = "genesis:synthetic-crash-custody"

CHILD = """
import json
import os
from pathlib import Path
import sys
sys.path.insert(0, sys.argv[1])
from i2.modules.cognitive_cycle_fixture import CognitiveCycleFixture
from i2.modules.operator_file_witness import OperatorFileWitness, UNTRUSTED_PROOF
from i2.modules.lifecycle_external_witness import LatestWitness, WITNESS_SCHEMA

class NoObservation:
    def verify(self, **kwargs): raise AssertionError("no cognition")
class NoValues:
    def evaluate_batch(self, **kwargs): raise AssertionError("no valuation")
class NoCurrent:
    def verify_current(self, **kwargs): raise AssertionError("no motor review")
class NoSafety:
    def check(self, **kwargs): raise AssertionError("no safety review")
class Terminal:
    def verify_terminal(self, *, life_ref, genesis_ref, physical_step,
                        terminal_ref, evidence_ref, previous_head):
        return (life_ref == sys.argv[3] and genesis_ref == sys.argv[4]
                and physical_step == 0 and terminal_ref == "terminal:synthetic-end"
                and evidence_ref == "evidence:synthetic-end")
ports = dict(life_ref=sys.argv[3], genesis_ref=sys.argv[4],
             observation_source=NoObservation(), valuation_source=NoValues(),
             current_source=NoCurrent(), safety_source=NoSafety(),
             terminal_source=Terminal())
action = sys.argv[5]
sqlite_path = Path(sys.argv[2])
witness_path = Path(sys.argv[6])
key = bytes.fromhex(sys.argv[7])
if action == "create":
    f = CognitiveCycleFixture.create(path=sqlite_path, synthetic_uc=3, **ports)
else:
    f = CognitiveCycleFixture.reopen(path=sqlite_path, **ports)
if action == "seal" or action == "seal_and_exit":
    f.seal_terminal(physical_step=0, terminal_ref="terminal:synthetic-end",
                    evidence_ref="evidence:synthetic-end")
if action == "seal_and_exit":
    os._exit(83)
if action == "anchor" or action == "anchor_and_exit":
    report = f.audit()
    claim = LatestWitness(WITNESS_SCHEMA, report["life_ref"], report["genesis_ref"],
                          report["schema"], report["committed"], report["last_step"],
                          report["chain_head"], report["terminal_ref"],
                          report["terminal_step"], UNTRUSTED_PROOF)
    store = OperatorFileWitness(directory=witness_path, key_id="test:key", key=key)
    prior = None if claim.committed == 0 else store.read_verified_latest(
        life_ref=claim.life_ref, genesis_ref=claim.genesis_ref).proof_ref
    store.stage(claim=claim, expected_proof_ref=prior)
if action == "anchor_and_exit":
    os._exit(84)
print(json.dumps(f.audit(), sort_keys=True))
"""


class WitnessCrashBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.db = root / "cognitive.sqlite"
        self.witness_dir = root / "operator"
        self.witness_dir.mkdir(mode=0o700)
        self.store = OperatorFileWitness(
            directory=self.witness_dir, key_id="test:key", key=KEY,
        )

    def child(self, action, expect=0):
        result = subprocess.run(
            [sys.executable, "-c", CHILD, str(ROOT / "src"), str(self.db),
             LIFE, GENESIS, action, str(self.witness_dir), KEY.hex()],
            cwd=ROOT, text=True, capture_output=True, timeout=15,
        )
        self.assertEqual(result.returncode, expect, result.stderr)
        return json.loads(result.stdout) if expect == 0 else None

    def claim(self, report):
        return LatestWitness(
            WITNESS_SCHEMA, report["life_ref"], report["genesis_ref"],
            report["schema"], report["committed"], report["last_step"],
            report["chain_head"], report["terminal_ref"],
            report["terminal_step"], UNTRUSTED_PROOF,
        )

    def test_crash_after_terminal_before_witness_is_unanchored(self):
        initial = self.child("create")
        self.store.stage(claim=self.claim(initial))
        self.child("seal_and_exit", expect=83)
        committed = self.child("audit")
        self.assertTrue(committed["synthetic_terminal"])
        with self.assertRaises(WitnessRefusal) as failure:
            compare_audit(report=committed, witness=self.store)
        self.assertEqual(failure.exception.reason, "UNANCHORED")
        # A terminal SQLite file cannot be resumed or silently re-sealed.
        self.assertEqual(self.child("audit")["chain_head"], committed["chain_head"])

    def test_crash_after_anchor_and_cold_terminal_inspection(self):
        initial = self.child("create")
        genesis = self.store.stage(claim=self.claim(initial))
        self.child("seal")
        sealed = self.child("audit")
        anchored = self.store.stage(claim=self.claim(sealed),
                                    expected_proof_ref=genesis.proof_ref)
        self.assertEqual(anchored.committed, 1)
        matched = compare_audit(report=self.child("audit"), witness=self.store)
        self.assertEqual(matched.status, "MATCHED_TERMINAL_INSPECTION")
        self.assertFalse(matched.resumption_authorized)
        self.assertEqual(matched.motor_authority, "NONE")

    def test_crash_after_witness_commit_preserves_latest_head(self):
        initial = self.child("create")
        self.child("anchor_and_exit", expect=84)
        record = self.store.read_verified_latest(life_ref=LIFE, genesis_ref=GENESIS)
        self.assertEqual(record.committed, 0)
        self.assertEqual(record.chain_head, initial["chain_head"])
        self.assertEqual(compare_audit(report=self.child("audit"), witness=self.store).status,
                         "MATCHED_OPEN_INSPECTION")
        self.assertFalse(compare_audit(report=self.child("audit"), witness=self.store).resumption_authorized)

    def test_old_valid_sqlite_copy_rejected_after_terminal_witness(self):
        initial = self.child("create")
        origin = self.store.stage(claim=self.claim(initial))
        backup = Path(self.tmp.name) / "previous.sqlite"
        with sqlite3.connect(self.db) as src, sqlite3.connect(backup) as dst:
            src.backup(dst)
        self.child("seal")
        terminal = self.child("audit")
        self.store.stage(claim=self.claim(terminal),
                         expected_proof_ref=origin.proof_ref)
        # The local fixture is internally valid but older than the guard.
        self.db = backup
        with self.assertRaises(WitnessRefusal) as failure:
            compare_audit(report=self.child("audit"), witness=self.store)
        self.assertEqual(failure.exception.reason, "STALE")


if __name__ == "__main__":
    unittest.main()
