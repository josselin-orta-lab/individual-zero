"""Stage-9 reference replay tests validate software identity, not science."""
from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from lab.determinism import canonical_causal_bytes, sha256_hex
from lab.stage9_canonical_journal_audit import audit_raw_causal_journal
from lab.stage9_reference_replay import (
    PROTOCOL_VERSION, generate_stage9_reference_diagnostic,
)


class Stage9ReferenceReplayTests(unittest.TestCase):
    def test_short_independent_reexecution_has_identical_full_journal_and_state(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "reference.jsonl"
            state_path = Path(folder) / "causal-state.json"
            result = generate_stage9_reference_diagnostic(
                steps=4, journal_path=path, causal_state_path=state_path,
            )
            self.assertTrue(result.identical_independent_reexecution)
            self.assertEqual(result.protocol_version, PROTOCOL_VERSION)
            self.assertEqual(
                result.protocol_version,
                "stage9-extended-reference-diagnostic-v3",
            )
            self.assertEqual(result.steps, 4)
            self.assertEqual(result.classification, "diagnostic_only")
            self.assertIsNone(result.scientific_verdict)
            self.assertFalse(result.golden_stage9_frozen)
            self.assertGreater(result.causal_owners, 0)
            self.assertEqual(len(result.causal_state_sha256), 64)
            self.assertEqual(len(result.journal_head), 64)
            payload = path.read_bytes()
            self.assertGreater(len(payload), 0)
            self.assertEqual(result.journal_bytes, len(payload))
            self.assertEqual(result.journal_sha256, sha256_hex(payload))
            independent = audit_raw_causal_journal(
                path, physical_observation_refs=set(),
            )
            self.assertGreater(independent["journal_events_checked"], 0)
            self.assertEqual(independent["journal_head_hash"], result.journal_head)
            self.assertFalse(independent["physical_truth_attested"])
            self.assertFalse(independent["memory_episode_closure_attested"])
            state_bytes = state_path.read_bytes()
            self.assertGreater(len(state_bytes), 0)
            self.assertEqual(result.causal_state_sha256, sha256_hex(state_bytes))
            canonical_state = json.loads(state_bytes)
            self.assertEqual(state_bytes, canonical_causal_bytes(canonical_state))
            self.assertEqual(len(canonical_state), result.causal_owners)
            self.assertIn("causal_model", canonical_state)
            document = json.loads(result.to_json())
            self.assertEqual(document["journal_sha256"], result.journal_sha256)
            self.assertFalse(document["golden_stage9_frozen"])

    def test_archiving_state_does_not_change_reference_metrics(self):
        with TemporaryDirectory() as folder:
            state_path = Path(folder) / "causal-state.json"
            baseline = generate_stage9_reference_diagnostic(steps=3)
            archived = generate_stage9_reference_diagnostic(
                steps=3, causal_state_path=state_path,
            )
            self.assertEqual(baseline, archived)
            self.assertEqual(
                sha256_hex(state_path.read_bytes()), archived.causal_state_sha256,
            )
            # Deliberate tampering is not erased by parsing and rendering:
            # the archived bytes, not just reported JSON values, are bound.
            with state_path.open("ab") as stream:
                stream.write(b"\n")
            self.assertNotEqual(
                sha256_hex(state_path.read_bytes()), archived.causal_state_sha256,
            )

    def test_invalid_duration_cannot_claim_extended_reference(self):
        for value in (0, -1, True, 1.5, "4", None):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    generate_stage9_reference_diagnostic(steps=value)


if __name__ == "__main__":
    unittest.main()
