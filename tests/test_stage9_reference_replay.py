"""Stage-9 reference replay tests validate software identity, not science."""
from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from lab.determinism import sha256_hex
from lab.stage9_reference_replay import (
    PROTOCOL_VERSION, generate_stage9_reference_diagnostic,
)


class Stage9ReferenceReplayTests(unittest.TestCase):
    def test_short_independent_reexecution_has_identical_full_journal_and_state(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "reference.jsonl"
            result = generate_stage9_reference_diagnostic(
                steps=4, journal_path=path,
            )
            self.assertTrue(result.identical_independent_reexecution)
            self.assertEqual(result.protocol_version, PROTOCOL_VERSION)
            self.assertEqual(
                result.protocol_version,
                "stage9-extended-reference-diagnostic-v2",
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
            document = json.loads(result.to_json())
            self.assertEqual(document["journal_sha256"], result.journal_sha256)
            self.assertFalse(document["golden_stage9_frozen"])

    def test_invalid_duration_cannot_claim_extended_reference(self):
        for value in (0, -1, True, 1.5, "4", None):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    generate_stage9_reference_diagnostic(steps=value)


if __name__ == "__main__":
    unittest.main()
