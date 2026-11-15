"""No-World tests of one-shot Stage6 custody and artifact receipt semantics."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from i3.lab import stage6_light_native_gsr_transport as S
from i3.lab import stage6_light_one_shot_receipts as R

HEAD = "a1b2c3d4e5f60718293a4b5c6d7e8f9012345678"
SOURCE = "5a56a9e52d4d2909bf2dfa64a4ec0066e0b3e814da25fd4df70ee56cc180edbf"


def fixture(version, seed):
    return {
        "schema": "i3-stage6-rehearsal-receipt/v1",
        "status": "ENGINEERING_FULL_GSR_REHEARSAL_NO_SCIENCE",
        "python_version": version, "source_git_head": HEAD,
        "source_files_sha256": SOURCE,
        "allocation_sha256": seed * 64,
        "last_chain_sha256": "c"*64,
        "lives_archived": 11520, "planned_worlds": 288,
        "phase_count": 9, "archive_sha256": "d"*64,
        "reduction_sha256": "e"*64, "science_admission": False,
        "no_retry": True, "workflow_run_id": 1729,
        "job_name": "engineering-" + version,
    }


class OneShotRehearsalReceiptTests(unittest.TestCase):
    def test_only_311_and_312_source_exact_frozen_receipts_can_join(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp)/"a.json", Path(tmp)/"b.json"
            a.write_text(json.dumps(fixture("3.11", "a")))
            b.write_text(json.dumps(fixture("3.12", "b")))
            combined = R.combine_rehearsal_receipts(str(a), str(b))
            self.assertEqual(set(combined), {"3.11", "3.12"})
            self.assertEqual(combined["3.12"]["lives_archived"], 11520)
            broken = fixture("3.12", "b")
            broken["source_git_head"] = "0"*40
            b.write_text(json.dumps(broken))
            with self.assertRaises(PermissionError):
                R.combine_rehearsal_receipts(str(a), str(b))

    def test_phase_hash_chain_verifies_all_nine_in_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            chain, previous = [], None
            for i, name in enumerate(S.PHASES):
                row = {"ordinal": i, "phase": name,
                       "payload_sha256": ("e"*63)+str(i),
                       "previous_sha256": previous}
                row["chain_sha256"] = S._sha(row)
                previous = row["chain_sha256"]
                chain.append(row)
            (root/"PHASES.jsonl").write_text(
                "".join(json.dumps(r)+"\n" for r in chain))
            R._phase_check(root, previous)
            altered = deepcopy(chain)
            altered[5]["phase"] = "R_FINAL"
            (root/"PHASES.jsonl").write_text(
                "".join(json.dumps(r)+"\n" for r in altered))
            with self.assertRaises(ValueError):
                R._phase_check(root, previous)
            (root/"PHASES.jsonl").write_text(
                "".join(json.dumps(r)+"\n" for r in chain[:8]))
            with self.assertRaises(ValueError):
                R._phase_check(root, previous)

if __name__ == "__main__":
    unittest.main()
