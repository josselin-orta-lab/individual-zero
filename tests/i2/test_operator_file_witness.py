"""Adversarial tests for operator-only file custody. NOT M11 or real signing."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import multiprocessing
import os
import tempfile
import unittest

from i2.modules.lifecycle_external_witness import LatestWitness, WITNESS_SCHEMA, LIFECYCLE_SCHEMA, ZERO_HASH
from i2.modules.operator_file_witness import (
    OperatorFileWitness, WitnessStoreError, UNTRUSTED_PROOF,
)

KEY = b"operator-test-key-only-not-production" * 2
LIFE = "life:synthetic-file-custody"
GENESIS = "genesis:synthetic-file-custody"


def claim(seq, *, terminal=False, genesis=GENESIS, head=None):
    return LatestWitness(
        WITNESS_SCHEMA, LIFE, genesis, LIFECYCLE_SCHEMA, seq,
        seq - 1, ZERO_HASH if seq == 0 else (head or ("%064x" % seq)),
        "terminal:synthetic" if terminal else None,
        seq - 1 if terminal else None, UNTRUSTED_PROOF,
    )


def concurrent_writer(directory, first_proof, head, queue):
    store = OperatorFileWitness(directory=Path(directory), key_id="operator:test", key=KEY)
    try:
        store.stage(claim=claim(1, head=head), expected_proof_ref=first_proof)
        queue.put("COMMITTED")
    except WitnessStoreError:
        queue.put("REFUSED")


class FileWitnessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name) / "witness"
        self.dir.mkdir(mode=0o700)
        self.store = OperatorFileWitness(directory=self.dir, key_id="operator:test", key=KEY)

    def genesis(self):
        return self.store.stage(claim=claim(0))

    def test_cold_restart_and_terminal_absorbs(self):
        origin = self.genesis()
        end = self.store.stage(claim=claim(1, terminal=True),
                               expected_proof_ref=origin.proof_ref)
        fresh = OperatorFileWitness(directory=self.dir, key_id="operator:test", key=KEY)
        self.assertEqual(fresh.read_verified_latest(life_ref=LIFE, genesis_ref=GENESIS), end)
        with self.assertRaisesRegex(WitnessStoreError, "terminal"):
            fresh.stage(claim=claim(2), expected_proof_ref=end.proof_ref)

    def test_missing_genesis_wrong_key_and_torn_log_fail_closed(self):
        with self.assertRaises(WitnessStoreError):
            self.store.read_verified_latest(life_ref=LIFE, genesis_ref=GENESIS)
        self.genesis()
        alien = OperatorFileWitness(directory=self.dir, key_id="operator:test", key=b"x" * 32)
        with self.assertRaises(WitnessStoreError):
            alien.read_verified_latest(life_ref=LIFE, genesis_ref=GENESIS)
        with open(self.dir / "heads.jsonl", "ab") as f:
            f.write(b"{broken")
        with self.assertRaisesRegex(WitnessStoreError, "torn"):
            self.store.read_verified_latest(life_ref=LIFE, genesis_ref=GENESIS)

    def test_genesis_conflict_duplicate_ack_and_stale_writer(self):
        first = self.genesis()
        with self.assertRaises(WitnessStoreError):
            self.store.stage(claim=claim(0))
        with self.assertRaises(WitnessStoreError):
            self.store.stage(claim=claim(1, genesis="genesis:other"),
                             expected_proof_ref=first.proof_ref)
        step = self.store.stage(claim=claim(1), expected_proof_ref=first.proof_ref)
        with self.assertRaises(WitnessStoreError):
            self.store.stage(claim=claim(1, head="e" * 64),
                             expected_proof_ref=first.proof_ref)
        self.assertEqual(self.store.read_verified_latest(life_ref=LIFE, genesis_ref=GENESIS), step)

    def test_untrusted_claim_is_not_a_signed_latest_proof(self):
        self.genesis()
        with self.assertRaises(ValueError):
            self.store.stage(claim=replace(claim(1), proof_ref="hmac-sha256:fake"))
        with self.assertRaises(WitnessStoreError):
            self.store.read_verified_latest(life_ref=LIFE, genesis_ref="genesis:other")

    def test_two_processes_one_winner_on_same_prior_head(self):
        first = self.genesis()
        context = multiprocessing.get_context("spawn")
        queue = context.Queue()
        writers = [
            context.Process(target=concurrent_writer,
                            args=(str(self.dir), first.proof_ref, char * 64, queue))
            for char in ("a", "b")
        ]
        for p in writers:
            p.start()
        for p in writers:
            p.join(15)
            self.assertEqual(p.exitcode, 0)
        self.assertEqual(sorted(queue.get(timeout=5) for _ in writers),
                         ["COMMITTED", "REFUSED"])
        latest = self.store.read_verified_latest(life_ref=LIFE, genesis_ref=GENESIS)
        self.assertEqual(latest.committed, 1)
        self.assertIn(latest.chain_head, ("a" * 64, "b" * 64))

    def test_complete_directory_rollback_remains_undetectable_here(self):
        """Explicit negative boundary: no independent latest-generation anchor."""
        first = self.genesis()
        copy = self.dir / "old-copy"
        # Snapshot only the data file, outside the canonical store path.
        old = (self.dir / "heads.jsonl").read_bytes()
        self.store.stage(claim=claim(1), expected_proof_ref=first.proof_ref)
        (self.dir / "heads.jsonl").write_bytes(old)
        rolled_back = self.store.read_verified_latest(life_ref=LIFE, genesis_ref=GENESIS)
        self.assertEqual(rolled_back.committed, 0)  # NOT anti-rollback proof


if __name__ == "__main__":
    unittest.main()
