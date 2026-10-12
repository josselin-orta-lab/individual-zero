"""M-11 opt-in current-owner image custody, not full runtime restart proof."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest

from lab.determinism import (
    RandomStreamRegistry, canonical_causal_bytes, sha256_hex,
)
from lab.journal import GENESIS_HASH, HashChainedJournal
from lab.sqlite_current_envelope import registered_current_metadata
from lab.sqlite_life_store import RecoveryBlocked, SQLiteLifeLedger
from lab.sqlite_runtime_custody import capture_registered_current_state
from lab.stage4_reference_fixture import build_stage4_reference_runtime
from lab.stage10_reference_fixture import build_stage10_reference_runtime
from lab.stage11_reference_fixture import build_stage11_reference_runtime


IDENTITY = "i0:m11:registered-custody:fixture"


def capture(runtime, *, expected_owner_ids=None):
    return capture_registered_current_state(
        runtime, individual_id=IDENTITY, expected_owner_ids=expected_owner_ids,
    )


class SQLiteOwnerCustodyTests(unittest.TestCase):
    def test_stage4_stage10_stage11_all_registered_owners_are_captured(self):
        builders = (
            build_stage4_reference_runtime,
            build_stage10_reference_runtime,
            build_stage11_reference_runtime,
        )
        for builder in builders:
            with self.subTest(builder=builder.__name__):
                runtime = builder(autonomous_mortal=True)
                original_world = deepcopy(runtime.world.export_causal_state())
                original_clock = deepcopy(runtime.scheduler.export_causal_state())
                original_head = runtime.journal.head_hash
                expected = sorted(owner.owner_id for owner in runtime.causal_owners)
                state = capture(runtime)
                self.assertEqual(state["owner_ids"], expected)
                self.assertEqual(state["world"], original_world)
                self.assertEqual(state["scheduler"], original_clock)
                self.assertEqual(state["journal"], {"count": 0, "head": GENESIS_HASH})
                self.assertEqual(state["lifecycle"], "active")
                self.assertEqual(
                    len(state["owners"]), len(expected) - 2,
                )
                self.assertEqual(runtime.world.export_causal_state(), original_world)
                self.assertEqual(runtime.scheduler.export_causal_state(), original_clock)
                self.assertEqual(runtime.journal.head_hash, original_head)
                self.assertIsNotNone(registered_current_metadata(state))

    def test_stage12_metacognition_and_sleep_are_one_registered_owner(self):
        # Reuse the established versioned live Stage12 constructor, not a
        # second independent set of components or independent Oracle/Bench.
        from test_stage12_mortal_runtime import stage12_runtime
        with TemporaryDirectory() as directory:
            runtime = stage12_runtime(str(Path(directory) / "stage12.jsonl"))
            image = capture(runtime)
            self.assertEqual(image["owner_ids"].count("metacognition_health"), 1)
            metacognition = image["owners"]["metacognition_health"]
            self.assertEqual(
                metacognition["schema"], "stage12-metacognition-sleep-custody-v1",
            )
            self.assertIn("prior_metacognition_and_sleep", metacognition)
            self.assertIn("lived_detectors", metacognition)
            self.assertIn("exploration", image["owners"])
            self.assertIn("individual.slow_history", image["owners"])
            self.assertEqual(runtime.journal.head_hash, GENESIS_HASH)

    def test_reject_nonmortal_open_step_duplicate_and_missing_owner(self):
        legacy = build_stage4_reference_runtime()
        with self.assertRaisesRegex(RuntimeError, "mortal"):
            capture(legacy)
        runtime = build_stage4_reference_runtime(autonomous_mortal=True)
        identities = tuple(sorted(owner.owner_id for owner in runtime.causal_owners))
        with self.assertRaisesRegex(ValueError, "roster changed"):
            capture(runtime, expected_owner_ids=identities[:-1])
        altered = SimpleNamespace(
            stage3=runtime.stage3, world=runtime.world,
            scheduler=runtime.scheduler, journal=runtime.journal,
            causal_owners=(*runtime.causal_owners, runtime.world),
        )
        with self.assertRaisesRegex(ValueError, "duplicated"):
            capture(altered)
        runtime.stage3.substrate.open_step()
        with self.assertRaisesRegex(RuntimeError, "quiescent"):
            capture(runtime)

    def test_rng_registry_state_is_complete_and_not_consumed(self):
        runtime = build_stage4_reference_runtime(autonomous_mortal=True)
        rng = RandomStreamRegistry(campaign_seed="m11-static-seed")
        stream = rng.stream("competition")
        stream.random()
        frozen = stream.getstate()
        attached = SimpleNamespace(
            stage3=runtime.stage3, world=runtime.world,
            scheduler=runtime.scheduler, journal=runtime.journal,
            causal_owners=(*runtime.causal_owners, rng),
        )
        image = capture(attached)
        self.assertEqual(image["rng_owner_ids"], ["scheduler.random_streams"])
        self.assertEqual(
            image["owners"]["scheduler.random_streams"], rng.export_causal_state(),
        )
        self.assertEqual(stream.getstate(), frozen)
        with self.assertRaisesRegex(ValueError, "RNG"):
            broken = deepcopy(image)
            broken["rng_owner_ids"] = []
            registered_current_metadata(broken)

    def test_strict_genesis_and_monotone_roster_are_pinned(self):
        runtime = build_stage4_reference_runtime(autonomous_mortal=True)
        first = capture(runtime)
        with TemporaryDirectory() as directory:
            path = str(Path(directory) / "life.db")
            with SQLiteLifeLedger.birth(
                path=path, individual_id=IDENTITY, initial_state=first,
            ) as ledger:
                self.assertTrue(ledger.audit().may_recover)
                self.assertEqual(ledger.audit().journal_count, 0)
                ledger.begin_intent(expected_generation=0, intent_ref="metadata:1")
                j = HashChainedJournal()
                row = j.append(event_id="metadata:1", causal_event={
                    "kind": "test_causal_receipt", "t_monde": 0,
                }).as_dict()
                second = deepcopy(first)
                second["journal"] = {"count": 1, "head": row["event_hash"]}
                ledger.commit_generation(
                    expected_generation=0, expected_head=GENESIS_HASH,
                    intent_ref="metadata:1", current_state=second,
                    events=[row], status="active",
                )
                self.assertEqual(ledger.audit().generation, 1)
                ledger.begin_intent(expected_generation=1, intent_ref="metadata:2")
                forged = deepcopy(second)
                original = forged["owner_ids"]
                forged["owner_ids"] = sorted(original + ["surprise-owner"])
                forged["owners"]["surprise-owner"] = {"state": "unregistered"}
                forged["owner_roster_hash"] = sha256_hex(canonical_causal_bytes(
                    forged["owner_ids"],
                ))
                with self.assertRaisesRegex(ValueError, "roster changed"):
                    ledger.commit_generation(
                        expected_generation=1, expected_head=row["event_hash"],
                        intent_ref="metadata:2", current_state=forged, events=[],
                    )
            receipt = SQLiteLifeLedger.audit_read_only(
                path=path, expected_individual_id=IDENTITY,
            )
            self.assertEqual(receipt.generation, 1)
            self.assertTrue(receipt.pending_intent)
            self.assertFalse(receipt.may_recover)

    def test_strict_sqlite_current_image_rejects_rehashed_false_anchor(self):
        runtime = build_stage4_reference_runtime(autonomous_mortal=True)
        original = capture(runtime)
        with TemporaryDirectory() as directory:
            path = str(Path(directory) / "life.db")
            with SQLiteLifeLedger.birth(
                path=path, individual_id=IDENTITY, initial_state=original,
            ):
                pass
            changed = deepcopy(original)
            changed["journal"]["count"] = 1
            payload = canonical_causal_bytes(changed)
            with sqlite3.connect(path) as database:
                database.execute(
                    "UPDATE life_current SET state_bytes=?, state_hash=? WHERE slot=1",
                    (payload, sha256_hex(payload)),
                )
            with self.assertRaisesRegex(RecoveryBlocked, "anchor"):
                SQLiteLifeLedger.audit_read_only(
                    path=path, expected_individual_id=IDENTITY,
                )

    def test_strict_birth_refuses_stale_genesis_anchor(self):
        runtime = build_stage4_reference_runtime(autonomous_mortal=True)
        original = capture(runtime)
        with TemporaryDirectory() as directory:
            forged = deepcopy(original)
            forged["journal"]["head"] = "f" * 64
            path = str(Path(directory) / "no-birth.db")
            with self.assertRaisesRegex(ValueError, "birth custody"):
                SQLiteLifeLedger.birth(
                    path=path, individual_id=IDENTITY, initial_state=forged,
                )
            self.assertFalse(Path(path).exists())


    def test_strict_roster_cannot_be_silently_downgraded_by_rehashed_state(self):
        runtime = build_stage4_reference_runtime(autonomous_mortal=True)
        original = capture(runtime)
        with TemporaryDirectory() as directory:
            path = str(Path(directory) / "life.db")
            with SQLiteLifeLedger.birth(
                path=path, individual_id=IDENTITY, initial_state=original,
            ):
                pass
            legacy_shape = {
                key: deepcopy(original[key])
                for key in ("individual_id", "world", "scheduler", "owners")
            }
            payload = canonical_causal_bytes(legacy_shape)
            with sqlite3.connect(path) as database:
                pinned = database.execute(
                    "SELECT registered_roster_hash FROM life_current WHERE slot=1"
                ).fetchone()[0]
                self.assertEqual(pinned, original["owner_roster_hash"])
                database.execute(
                    "UPDATE life_current SET state_bytes=?, state_hash=? WHERE slot=1",
                    (payload, sha256_hex(payload)),
                )
            # The new state checksum and canonical bytes are valid. The
            # separately pinned lifetime contract must still catch removal
            # of the former strict roster from the sole-current-state image.
            with self.assertRaisesRegex(RecoveryBlocked, "contract downgrade"):
                SQLiteLifeLedger.audit_read_only(
                    path=path, expected_individual_id=IDENTITY,
                )

    def test_operator_cli_discloses_registered_roster_without_recovery_claim(self):
        runtime = build_stage4_reference_runtime(autonomous_mortal=True)
        image = capture(runtime)
        with TemporaryDirectory() as directory:
            path = str(Path(directory) / "life.db")
            with SQLiteLifeLedger.birth(
                path=path, individual_id=IDENTITY, initial_state=image,
            ):
                proc = subprocess.run(
                    [sys.executable, "scripts/audit_i0_sqlite.py",
                     "--db", path, "--identity", IDENTITY,
                     "--expect-generation", "0", "--expect-head", GENESIS_HASH],
                    capture_output=True, text=True, timeout=25,
                )
                self.assertEqual(proc.returncode, 0, proc.stderr)
                report = json.loads(proc.stdout)
                self.assertEqual(
                    report["registered_owner_roster_hash"],
                    image["owner_roster_hash"],
                )
                self.assertFalse(report["runtime_recovery_certified"])
                self.assertEqual(report["claim"],
                    "internal_consistency_only_not_independent_physical_truth")


if __name__ == "__main__":
    unittest.main()
