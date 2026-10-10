"""Development-only operator integration on synthetic seeded worlds (not held-out)."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

from lab.stage9_heldout_runner import (
    ANNOTATIONS_VERSION, GENERATOR_VERSION, RELEASE_VERSION, WORLD_VERSION,
    _json_file, execute_campaign, package_evidence,
)
from lab.stage9_scientific_preregistration import validate_registration
from tests.test_stage9_heldout_runner import _components, _generator, _plain, _write
from tests.test_stage9_scientific_preregistration import example_draft


class Stage9HeldoutOperatorIntegrationTests(unittest.TestCase):

    def test_four_cell_dry_rehearsal_with_real_runtime(self):
        reference, params, equipment = _components()
        registered = example_draft()
        registered["holdout_seeds"] = [41, 42]
        registered["calibration_seeds"] = [13, 14]
        registered["world_generator_version"] = _generator().version
        with TemporaryDirectory() as directory:
            root = Path(directory)
            custody = root / "original-manifests"
            files = {
                "frozen/generator.json": {
                    "protocol_version": GENERATOR_VERSION,
                    "generation": _plain(_generator()),
                },
                "frozen/parameters.json": params,
                "frozen/equipment.json": equipment,
                "frozen/ontology.json": {
                    "protocol_version": "stage9-heldout-ontology-v1",
                    "version": "development-only",
                },
            }
            physics = reference.world.config.as_dict()
            physical_worlds = [
                ("holdout:positive", physics, "positive"),
                ("holdout:null", dict(physics, version="dev-null-physics",
                                      drink_water_gain=0.0), "null"),
                ("calibration:1", dict(physics, version="dev-calibration-physics"),
                 "calibration"),
            ]
            for world, world_physics, filename in physical_worlds:
                files["worlds/" + filename + ".json"] = {
                    "protocol_version": WORLD_VERSION,
                    "world_id": world, "physics": world_physics,
                    "scenario": {
                        "id": filename + "-synthetic",
                        "version": "development-v1",
                        "events": [],
                    },
                }
            digests = {}
            for name, document in files.items():
                path = custody / name
                _write(path, document)
                digests[name] = sha256(path.read_bytes()).hexdigest()
            registered.update({
                "world_generator_sha256": digests["frozen/generator.json"],
                "parameter_registry_sha256": digests["frozen/parameters.json"],
                "equipment_sha256": digests["frozen/equipment.json"],
                "ontology_sha256": digests["frozen/ontology.json"],
                "holdout_world_sha256": {
                    "holdout:positive": digests["worlds/positive.json"],
                    "holdout:null": digests["worlds/null.json"],
                },
                "calibration_world_sha256": {
                    "calibration:1": digests["worlds/calibration.json"],
                },
                "steps_per_run": 3,
            })
            reg_digest = validate_registration(registered)
            reg_path = root / "registration.json"
            _write(reg_path, registered)
            index_path = root / "index.json"
            _write(index_path, {
                "protocol_version": "stage9-registered-physical-manifest-index-v1",
                "registration_digest": reg_digest,
                "frozen_manifests": {
                    "world_generator": "frozen/generator.json",
                    "parameter_registry": "frozen/parameters.json",
                    "equipment": "frozen/equipment.json",
                    "ontology": "frozen/ontology.json",
                },
                "calibration_worlds": {
                    "calibration:1": "worlds/calibration.json",
                },
                "holdout_worlds": {
                    "holdout:positive": "worlds/positive.json",
                    "holdout:null": "worlds/null.json",
                },
            })
            fake_commit = "b" * 40
            release_path = root / "operator-release.json"
            _write(release_path, {
                "protocol_version": RELEASE_VERSION,
                "registration_digest": reg_digest,
                "frozen_implementation_commit": registered[
                    "frozen_implementation_commit"
                ],
                "registration_commit": fake_commit,
                "authorization": "GO",
                "research_owner": "synthetic-test",
                "custodian": "synthetic-test",
                "operator": "synthetic-test",
                "independent_evaluator": "synthetic-test",
                "approval_evidence_ref": "synthetic-test-not-a-signature",
                "independent_timestamp_ref": "synthetic-test-not-a-timestamp",
            })
            raw = root / "raw"
            args = dict(
                repository=root, registration_path=reg_path,
                registration_commit=fake_commit,
                manifest_index_path=index_path, manifest_root=custody,
                release_path=release_path, output_root=raw,
            )
            # Replace ONLY the real Git seal/witness preflight; this is a
            # synthetic rehearsal with no real signed approval or secrets.
            with patch(
                "lab.stage9_heldout_runner._check_preregistration",
                return_value={"worktree_status": "synthetic-dev-only"},
            ):
                receipt = execute_campaign(**args)
                self.assertEqual(receipt["run_count"], 4)
                self.assertFalse(receipt["independent_execution_attested"])
                self.assertFalse(receipt["golden_stage9_frozen"])
                archive = _json_file(raw / "operator-run-index.json")
                self.assertEqual(len(archive["runs"]), 4)
                for row in archive["runs"]:
                    for key in (
                        "journal_path", "replay_journal_path",
                        "causal_state_path", "replay_causal_state_path",
                    ):
                        self.assertTrue((raw / row[key]).is_file())
                    self.assertEqual(
                        (raw / row["journal_path"]).read_bytes(),
                        (raw / row["replay_journal_path"]).read_bytes(),
                    )
                with self.assertRaisesRegex(ValueError, "already exists"):
                    execute_campaign(**args)

            annotations = root / "bench-annotations.json"
            _write(annotations, {
                "protocol_version": ANNOTATIONS_VERSION,
                "registration_digest": reg_digest,
                "runs": [
                    {"world_id": w, "seed": s,
                     "known_cause_cases": [],
                     "naturally_acquired_false_candidates": []}
                    for w in registered["holdout_world_ids"]
                    for s in registered["holdout_seeds"]
                ],
            })
            result = package_evidence(
                registration_path=reg_path, runs_root=raw,
                annotations_path=annotations,
                evidence_path=root / "evidence.json",
                raw_index_path=root / "raw-index.json",
            )
            self.assertEqual(result["assessment"], "not_evaluable")
            self.assertFalse(result["golden_stage9_frozen"])

    def test_no_go_does_not_expose_physical_worlds(self):
        registered = example_draft()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "registration.json"
            _write(path, registered)
            release = root / "release.json"
            _write(release, {"authorization": "NO-GO"})
            with patch(
                "lab.stage9_heldout_runner._check_preregistration",
                return_value={"worktree_status": "synthetic-dev-only"},
            ):
                with self.assertRaisesRegex(ValueError, "fields"):
                    execute_campaign(
                        repository=root, registration_path=path,
                        registration_commit="b" * 40,
                        manifest_index_path=root / "missing-index.json",
                        manifest_root=root / "missing-secret-worlds",
                        release_path=release, output_root=root / "uncreated-raw",
                    )
            self.assertFalse((root / "uncreated-raw").exists())


if __name__ == "__main__":
    unittest.main()
