"""Synthetic-only file custody tests; no heldout science or Golden evidence."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from lab.stage9_registered_manifest_custody import (
    INDEX_VERSION, audit_registered_manifest_files, load_manifest_index,
)
from lab.stage9_scientific_preregistration import validate_registration
from tests.test_stage9_scientific_preregistration import example_draft


def _fixture(root: Path) -> tuple[dict[str, object], dict[str, object]]:
    draft = example_draft()
    files: dict[str, dict[str, str]] = {
        "frozen_manifests": {},
        "calibration_worlds": {},
        "holdout_worlds": {},
    }
    groups = (
        ("frozen_manifests", (
            ("world_generator", "world_generator_sha256"),
            ("equipment", "equipment_sha256"),
            ("parameter_registry", "parameter_registry_sha256"),
            ("ontology", "ontology_sha256"),
        )),
        ("calibration_worlds", tuple(
            (world, world) for world in draft["calibration_world_ids"]
        )),
        ("holdout_worlds", tuple(
            (world, world) for world in draft["holdout_world_ids"]
        )),
    )
    for group, labels in groups:
        (root / group).mkdir()
        for label, _ in labels:
            name = label.replace(":", "_") + ".manifest"
            relative = f"{group}/{name}"
            payload = (
                f"SYNTHETIC MANIFEST, NOT A REAL EXPERIMENT\n"
                f"group={group}\nlabel={label}\n"
            ).encode("utf-8")
            (root / relative).write_bytes(payload)
            digest = sha256(payload).hexdigest()
            files[group][label] = relative
            if group == "frozen_manifests":
                fields = {
                    "world_generator": "world_generator_sha256",
                    "equipment": "equipment_sha256",
                    "parameter_registry": "parameter_registry_sha256",
                    "ontology": "ontology_sha256",
                }
                draft[fields[label]] = digest
            elif group == "calibration_worlds":
                draft["calibration_world_sha256"][label] = digest
            else:
                draft["holdout_world_sha256"][label] = digest
    index = {
        "protocol_version": INDEX_VERSION,
        "registration_digest": validate_registration(draft),
        **files,
    }
    return draft, index


def _audit(
    root: Path, draft: dict[str, object], index: dict[str, object],
) -> dict[str, object]:
    return audit_registered_manifest_files(
        registration=draft, index=index, artifact_root=root,
    )


class Stage9RegisteredManifestCustodyTests(unittest.TestCase):
    def test_all_registered_manifest_bytes_verified_without_scientific_verdict(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            draft, index = _fixture(root)
            result = _audit(root, draft, index)
            self.assertEqual(result["frozen_manifests_checked"], 4)
            self.assertEqual(result["calibration_worlds_checked"], 1)
            self.assertEqual(result["holdout_worlds_checked"], 2)
            self.assertEqual(result["total_manifest_files_checked"], 7)
            self.assertGreater(result["total_manifest_bytes_checked"], 0)
            self.assertEqual(result["registration_digest"], validate_registration(draft))
            self.assertFalse(result["physical_world_semantics_attested"])
            self.assertFalse(result["world_generation_independence_attested"])
            self.assertFalse(result["heldout_seed_custody_attested"])
            self.assertFalse(result["golden_stage9_frozen"])
            self.assertIsNone(result["scientific_verdict"])
            self.assertTrue(result["outstanding"])

    def test_manifest_bytes_cannot_be_forged_or_substituted(self):
        for role, name in (
            ("frozen_manifests", "ontology"),
            ("frozen_manifests", "equipment"),
            ("calibration_worlds", "calibration:1"),
            ("holdout_worlds", "holdout:null"),
        ):
            with self.subTest(group=role, manifest=name):
                with TemporaryDirectory() as folder:
                    root = Path(folder)
                    draft, index = _fixture(root)
                    path = root / index[role][name]
                    path.write_bytes(path.read_bytes() + b"late forensic alteration")
                    with self.assertRaisesRegex(ValueError, "manifest digest mismatch"):
                        _audit(root, draft, index)

    def test_missing_empty_and_reused_manifest_files_fail_closed(self):
        for kind in ("missing", "empty", "duplicate_path", "hardlink"):
            with self.subTest(kind=kind):
                with TemporaryDirectory() as folder:
                    root = Path(folder)
                    draft, index = _fixture(root)
                    original = root / index["frozen_manifests"]["equipment"]
                    replacement = root / index["frozen_manifests"]["ontology"]
                    if kind == "missing":
                        original.unlink()
                        expected = "missing physical manifest file"
                    elif kind == "empty":
                        original.write_bytes(b"")
                        expected = "empty physical manifest"
                    elif kind == "duplicate_path":
                        index["frozen_manifests"]["equipment"] = index[
                            "frozen_manifests"
                        ]["ontology"]
                        expected = "physical manifest reused"
                    else:
                        original.unlink()
                        os.link(replacement, original)
                        expected = "physical manifest reused"
                    with self.assertRaisesRegex(ValueError, expected):
                        _audit(root, draft, index)

    def test_path_escape_and_symlink_aliases_fail(self):
        for kind in ("parent", "absolute", "dot", "symlink_file", "symlink_dir"):
            with self.subTest(kind=kind):
                with TemporaryDirectory() as folder:
                    root = Path(folder)
                    draft, index = _fixture(root)
                    source = index["frozen_manifests"]["equipment"]
                    original = root / source
                    if kind == "parent":
                        index["frozen_manifests"]["equipment"] = "../elsewhere"
                    elif kind == "absolute":
                        index["frozen_manifests"]["equipment"] = str(original)
                    elif kind == "dot":
                        index["frozen_manifests"]["equipment"] = (
                            "frozen_manifests/./equipment.manifest"
                        )
                    elif kind == "symlink_file":
                        other = root / "equipment.link"
                        other.symlink_to(original)
                        index["frozen_manifests"]["equipment"] = other.name
                    else:
                        (root / "linked").symlink_to(
                            root / "frozen_manifests", target_is_directory=True,
                        )
                        index["frozen_manifests"]["equipment"] = (
                            "linked/equipment.manifest"
                        )
                    with self.assertRaisesRegex(
                        ValueError, "traversal-free|relative|symlinks",
                    ):
                        _audit(root, draft, index)

    def test_symlinked_custody_root_is_rejected(self):
        with TemporaryDirectory() as folder:
            root = Path(folder) / "real"
            root.mkdir()
            draft, index = _fixture(root)
            alias = root.parent / "alias"
            alias.symlink_to(root, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "root may not be a symlink"):
                _audit(alias, draft, index)

    def test_index_requires_exact_worlds_roles_and_digest(self):
        edits = (
            ("missing_holdout", lambda i: i["holdout_worlds"].pop("holdout:null")),
            ("extra_calibration", lambda i: i["calibration_worlds"].update({
                "synthetic:foreign": i["calibration_worlds"]["calibration:1"],
            })),
            ("missing_equipment", lambda i: i["frozen_manifests"].pop("equipment")),
            ("unexpected_index_key", lambda i: i.update({"approved": True})),
            ("wrong_version", lambda i: i.update({"protocol_version": "future"})),
            ("wrong_binding", lambda i: i.update({"registration_digest": "0" * 64})),
        )
        for scenario, edit in edits:
            with self.subTest(scenario=scenario):
                with TemporaryDirectory() as folder:
                    root = Path(folder)
                    draft, baseline = _fixture(root)
                    index = deepcopy(baseline)
                    edit(index)
                    with self.assertRaises(ValueError):
                        _audit(root, draft, index)

    def test_index_json_rejects_ambiguity_and_nonfinite_constants(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "index.json"
            for contents, error in (
                ('{"protocol_version":"a","protocol_version":"b"}',
                 "duplicate heldout evidence JSON key"),
                ('{"protocol_version":NaN}', "non-finite heldout JSON constant"),
                ('[]', "physical manifest index must be a JSON object"),
            ):
                with self.subTest(contents=contents):
                    path.write_text(contents, encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, error):
                        load_manifest_index(path)

    def test_registration_digest_changes_cannot_launder_old_manifest_index(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            draft, index = _fixture(root)
            draft["steps_per_run"] += 1
            with self.assertRaisesRegex(ValueError, "differs from registration"):
                _audit(root, draft, index)

    def test_synthetic_example_remains_unregistered(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            draft, index = _fixture(root)
            path = root / "index.json"
            path.write_text(json.dumps(index), encoding="utf-8")
            loaded = load_manifest_index(path)
            self.assertEqual(_audit(root, draft, loaded)["scientific_verdict"], None)


if __name__ == "__main__":
    unittest.main()
