"""Stage-9 raw artifact custody fixtures are synthetic, never heldout results."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from lab.stage9_heldout_artifact_custody import (
    INDEX_VERSION, audit_heldout_raw_artifacts, load_raw_artifact_index,
)
from lab.stage9_scientific_preregistration import validate_registration
from tests.test_stage9_scientific_assessment import make_report, sealed
from tests.test_stage9_scientific_preregistration import example_draft


def _prepared(root: Path):
    registration = example_draft()
    report = make_report(registration, candidates=20)
    index_runs = []
    first_paths = None
    for i, run in enumerate(report["runs"]):
        name = f"run{i}"
        folder = root / name
        folder.mkdir()
        journal = f"synthetic journal bytes {i}\n".encode()
        state = f"synthetic causal state bytes {i}\n".encode()
        files = {
            "journal_path": (f"{name}/original.jsonl", journal),
            "replay_journal_path": (f"{name}/replay.jsonl", journal),
            "causal_state_path": (f"{name}/state.json", state),
            "replay_causal_state_path": (f"{name}/replay-state.json", state),
        }
        row = {"world_id": run["world_id"], "seed": run["seed"]}
        for key, (relative, payload) in files.items():
            (root / relative).write_bytes(payload)
            row[key] = relative
        run["journal_sha256"] = sha256(journal).hexdigest()
        run["replay_journal_sha256"] = sha256(journal).hexdigest()
        run["causal_state_sha256"] = sha256(state).hexdigest()
        run["replay_causal_state_sha256"] = sha256(state).hexdigest()
        index_runs.append(row)
        if first_paths is None:
            first_paths = dict(row)
    report = sealed(report)
    index = {
        "protocol_version": INDEX_VERSION,
        "registration_digest": validate_registration(registration),
        "evidence_sha256": report["evidence_sha256"],
        "runs": index_runs,
    }
    return registration, report, index


class Stage9RawArtifactCustodyTests(unittest.TestCase):
    def test_real_bytes_match_declared_digests_but_are_not_scientific_proof(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            registration, report, index = _prepared(root)
            result = audit_heldout_raw_artifacts(
                registration=registration, evidence=report,
                index=index, artifact_root=root,
            )
            self.assertEqual(result["runs_checked"], 4)
            self.assertEqual(result["raw_files_checked"], 16)
            self.assertTrue(result["original_replay_bytes_identical"])
            self.assertGreater(result["total_bytes_checked"], 0)
            self.assertEqual(len(result["index_sha256"]), 64)
            self.assertIsNone(result["scientific_verdict"])
            self.assertFalse(result["golden_stage9_frozen"])
            self.assertTrue(result["outstanding"])
            self.assertNotEqual(result["provisional_metric_assessment"], "accepted")

    def test_tampering_with_actual_journal_or_replay_fails(self):
        for key in ("journal_path", "replay_journal_path",
                    "causal_state_path", "replay_causal_state_path"):
            with self.subTest(key=key):
                with TemporaryDirectory() as folder:
                    root = Path(folder)
                    reg, evidence, index = _prepared(root)
                    path = root / index["runs"][0][key]
                    path.write_bytes(path.read_bytes() + b"forged")
                    with self.assertRaisesRegex(ValueError, "raw artifact digest"):
                        audit_heldout_raw_artifacts(
                            registration=reg, evidence=evidence,
                            index=index, artifact_root=root,
                        )

    def test_empty_reported_journal_is_not_accepted_as_execution(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            reg, evidence, index = _prepared(root)
            reported = deepcopy(evidence)
            empty_sha = sha256(b"").hexdigest()
            reported["runs"][0]["journal_sha256"] = empty_sha
            reported["runs"][0]["replay_journal_sha256"] = empty_sha
            reported = sealed(reported)
            index["evidence_sha256"] = reported["evidence_sha256"]
            for key in ("journal_path", "replay_journal_path"):
                (root / index["runs"][0][key]).write_bytes(b"")
            with self.assertRaisesRegex(ValueError, "empty raw artifact"):
                audit_heldout_raw_artifacts(
                    registration=reg, evidence=reported,
                    index=index, artifact_root=root,
                )

    def test_digest_can_not_be_forged_in_report_or_index(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            reg, evidence, index = _prepared(root)
            changed = deepcopy(evidence)
            changed["runs"][0]["journal_sha256"] = "f" * 64
            changed["runs"][0]["replay_journal_sha256"] = "f" * 64
            changed = sealed(changed)
            index["evidence_sha256"] = changed["evidence_sha256"]
            with self.assertRaisesRegex(ValueError, "raw artifact digest"):
                audit_heldout_raw_artifacts(
                    registration=reg, evidence=changed,
                    index=index, artifact_root=root,
                )
            index["evidence_sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "not bound"):
                audit_heldout_raw_artifacts(
                    registration=reg, evidence=evidence,
                    index=index, artifact_root=root,
                )

    def test_missing_or_duplicate_run_index_is_rejected(self):
        for modification in ("missing", "duplicate", "foreign"):
            with self.subTest(modification=modification):
                with TemporaryDirectory() as folder:
                    root = Path(folder)
                    reg, evidence, index = _prepared(root)
                    if modification == "missing":
                        index["runs"].pop()
                    elif modification == "duplicate":
                        index["runs"][1] = deepcopy(index["runs"][0])
                    else:
                        index["runs"][0]["world_id"] = "unregistered-world"
                    with self.assertRaises(ValueError):
                        audit_heldout_raw_artifacts(
                            registration=reg, evidence=evidence,
                            index=index, artifact_root=root,
                        )

    def test_same_raw_file_cannot_masquerade_as_independent_replay(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            reg, evidence, index = _prepared(root)
            index["runs"][0]["replay_journal_path"] = (
                index["runs"][0]["journal_path"]
            )
            with self.assertRaisesRegex(ValueError, "reused"):
                audit_heldout_raw_artifacts(
                    registration=reg, evidence=evidence,
                    index=index, artifact_root=root,
                )

    def test_hardlinked_original_and_replay_are_rejected(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            reg, evidence, index = _prepared(root)
            first = root / index["runs"][0]["journal_path"]
            replay = root / index["runs"][0]["replay_journal_path"]
            replay.unlink()
            os.link(first, replay)
            with self.assertRaisesRegex(ValueError, "reused"):
                audit_heldout_raw_artifacts(
                    registration=reg, evidence=evidence,
                    index=index, artifact_root=root,
                )

    def test_path_escape_and_symlink_do_not_access_outside_file(self):
        for scenario in ("traversal", "symlink"):
            with self.subTest(scenario=scenario):
                with TemporaryDirectory() as folder:
                    root = Path(folder)
                    reg, evidence, index = _prepared(root)
                    original = root / index["runs"][0]["journal_path"]
                    if scenario == "traversal":
                        index["runs"][0]["journal_path"] = "../../outside"
                    else:
                        link = root / "shortcut.jsonl"
                        link.symlink_to(original)
                        index["runs"][0]["journal_path"] = link.name
                    with self.assertRaisesRegex(ValueError, "traversal|symlink"):
                        audit_heldout_raw_artifacts(
                            registration=reg, evidence=evidence,
                            index=index, artifact_root=root,
                        )

    def test_ambiguous_json_and_invalid_schema_fail_closed(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            reg, evidence, index = _prepared(root)
            manifest = root / "index.json"
            manifest.write_text('{"protocol_version":"a","protocol_version":"b"}')
            with self.assertRaisesRegex(ValueError, "duplicate"):
                load_raw_artifact_index(manifest)
            manifest.write_text('{"runs":[NaN]}')
            with self.assertRaisesRegex(ValueError, "non-finite"):
                load_raw_artifact_index(manifest)
            index["protocol_version"] = "obsolete"
            with self.assertRaisesRegex(ValueError, "schema"):
                audit_heldout_raw_artifacts(
                    registration=reg, evidence=evidence,
                    index=index, artifact_root=root,
                )


if __name__ == "__main__":
    unittest.main()
