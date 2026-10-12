"""Read-only SQLite journal auditing must reject noninteger record ordinals.

SQLite stores the authoritative row index as INTEGER, but a forged canonical
record can encode Boolean true as its JSON index. Python considers True == 1:
comparison alone is not an integrity check. The SHA-256 occurrence digest
intentionally excludes the transport index, so the adversarial record retains
a cryptographically coherent entire causal chain.
"""
from __future__ import annotations

import json
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
import unittest

from lab.determinism import canonical_causal_bytes
from lab.journal import GENESIS_HASH, HashChainedJournal
from lab.sqlite_life_store import RecoveryBlocked, SQLiteLifeLedger


IDENTITY = "i0:sqlite:strict-record-index"


def current_state():
    return {
        "individual_id": IDENTITY,
        "world": {"physical_step": 0},
        "scheduler": {"t_monde": 0},
        "owners": {"metacognition_health": {"cycle": 0}},
    }


class StrictOccurrenceIndexTests(unittest.TestCase):
    def test_rehashed_canonical_boolean_index_cannot_pass_readonly_audit(self):
        with TemporaryDirectory() as directory:
            path = str(Path(directory) / "strict-index.db")
            journal = HashChainedJournal()
            rows = [
                journal.append(
                    event_id=f"event:{index}",
                    causal_event={"kind": "test_causal_receipt", "t_monde": index},
                ).as_dict()
                for index in (0, 1)
            ]
            with SQLiteLifeLedger.birth(
                path=path, individual_id=IDENTITY, initial_state=current_state(),
            ) as store:
                store.begin_intent(expected_generation=0, intent_ref="step:1")
                store.commit_generation(
                    expected_generation=0, expected_head=GENESIS_HASH,
                    intent_ref="step:1", current_state=current_state(), events=rows,
                )
            good = SQLiteLifeLedger.audit_read_only(
                path=path, expected_individual_id=IDENTITY,
            )
            self.assertEqual(good.journal_count, 2)
            self.assertEqual(good.journal_head, journal.head_hash)

            with sqlite3.connect(path) as connection:
                record = connection.execute(
                    "SELECT canonical_bytes, event_hash FROM causal_occurrence WHERE idx=1"
                ).fetchone()
                self.assertIsNotNone(record)
                canonical_record = json.loads(record[0])
                self.assertEqual(canonical_record["index"], 1)
                canonical_record["index"] = True
                forged = canonical_causal_bytes(canonical_record)
                # All SHA links remain valid: only the unhashed transport index
                # changes from numeric 1 to JSON true. This must not pass M-19.
                connection.execute(
                    "UPDATE causal_occurrence SET canonical_bytes=? WHERE idx=1",
                    (forged,),
                )
                self.assertEqual(
                    connection.execute(
                        "SELECT event_hash FROM causal_occurrence WHERE idx=1"
                    ).fetchone()[0],
                    record[1],
                )

            with self.assertRaisesRegex(RecoveryBlocked, "canonical|index"):
                SQLiteLifeLedger.audit_read_only(
                    path=path, expected_individual_id=IDENTITY,
                )


if __name__ == "__main__":
    unittest.main()
