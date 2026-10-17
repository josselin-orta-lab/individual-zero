"""Adversarial canonical-source audit for pre-action spatial perception.

Rehash tampering while preserving structural journal integrity, then require
semantic rejection. Uses a live integrated Stage12 WorldBody autonomous life.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from lab.determinism import canonical_causal_bytes
from lab.independent_journal_audit import audit_export_bytes
from lab.journal import GENESIS_HASH
from lab.stage12_spatial_cue_audit import audit_spatial_visible_cues
from test_stage12_goal_agency_runtime import opt_in_runtime


def rechain(rows):
    previous = GENESIS_HASH
    for n, row in enumerate(rows):
        row["index"] = n
        row["previous_hash"] = previous
        previous = sha256(bytes.fromhex(previous) + canonical_causal_bytes({
            "event_id": row["event_id"], "causal_event": row["causal_event"],
        })).hexdigest()
        row["event_hash"] = previous
    return b"\n".join(canonical_causal_bytes(r) for r in rows)


class SpatialCueProvenanceAuditTests(unittest.TestCase):
    def test_live_perception_has_four_legal_neighbors(self):
        with TemporaryDirectory() as root:
            life = opt_in_runtime(str(Path(root) / "life.wal"), join=True)
            for _ in range(4):
                self.assertEqual(life.run_step().execution_status, "applied")
            raw = life.journal.canonical_bytes()
            report = audit_spatial_visible_cues(
                raw, expected_head=life.journal.head_hash,
                expected_count=len(life.journal.entries),
            )
            self.assertEqual(report.legal_adjacent_receipts, 4)
            self.assertEqual(report.passable_cells + report.nonpassable_cells, 16)
            self.assertFalse(report.as_dict()["first_person_world_judgement_proven"])

    def test_rehashed_wrong_neighbor_direction_is_rejected(self):
        with TemporaryDirectory() as root:
            life = opt_in_runtime(str(Path(root) / "life.wal"), join=True)
            for _ in range(3):
                self.assertEqual(life.run_step().execution_status, "applied")
            rows = [json.loads(line) for line in life.journal.canonical_bytes().splitlines()]
            target = next(row["causal_event"]["data"] for row in rows
                          if row["causal_event"]["kind"] == "perceptual_capture")
            target["agency_visible_adjacent"][0]["direction"] = "east"
            forged = rechain(rows)
            self.assertEqual(audit_export_bytes(forged).world_steps_closed, 3)
            with self.assertRaisesRegex(ValueError, "duplicate or unknown|incompatible"):
                audit_spatial_visible_cues(forged)

    def test_rehashed_missing_adjacent_is_rejected(self):
        with TemporaryDirectory() as root:
            life = opt_in_runtime(str(Path(root) / "life.wal"), join=True)
            for _ in range(2):
                self.assertEqual(life.run_step().execution_status, "applied")
            rows = [json.loads(line) for line in life.journal.canonical_bytes().splitlines()]
            target = next(row["causal_event"]["data"] for row in rows
                          if row["causal_event"]["kind"] == "perceptual_capture")
            del target["agency_visible_adjacent"]
            forged = rechain(rows)
            self.assertEqual(audit_export_bytes(forged).world_steps_closed, 2)
            with self.assertRaisesRegex(ValueError, "missing adjacent cue"):
                audit_spatial_visible_cues(forged)


if __name__ == "__main__":
    unittest.main()
