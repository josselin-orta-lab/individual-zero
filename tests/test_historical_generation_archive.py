"""Pure falsification tests for the I2 read-only historical archive guard."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("check_i2_archive", ROOT / "tools/check_i2_archive.py")
guard = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(guard)


class I2ArchiveGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((ROOT / guard.MANIFEST).read_text(encoding="utf-8"))
        cls.registry = json.loads((ROOT / "config/engine-registry.json").read_text(encoding="utf-8"))
        cls.contract = json.loads((ROOT / "src/i2/engine.json").read_text(encoding="utf-8"))

    def originals(self):
        return {path: sha for path, sha, _ in guard.FROZEN.values()}

    def assess(self, manifest=None, registry=None, contract=None, observed=None):
        return guard.assess(
            self.manifest if manifest is None else manifest,
            self.registry if registry is None else registry,
            self.contract if contract is None else contract,
            self.originals() if observed is None else observed,
        )

    def test_original_pins_and_no_engine_promotion(self):
        self.assertEqual(self.assess(), [])

    def test_changed_source_tree_fails_closed(self):
        observed = self.originals()
        observed["src/i2"] = "0" * 40
        self.assertTrue(any("historical tree changed" in x for x in self.assess(observed=observed)))
        observed = self.originals()
        observed.pop("tests/i2")
        self.assertTrue(any("tests/i2" in x for x in self.assess(observed=observed)))

    def test_manifest_cannot_be_rewritten_to_match_modified_tree(self):
        modified = json.loads(json.dumps(self.manifest))
        modified["source"]["git_tree_sha"] = "0" * 40
        self.assertTrue(any("manifest pin differs" in x for x in self.assess(manifest=modified)))

    def test_registration_and_implicit_birth_are_rejected(self):
        registry = json.loads(json.dumps(self.registry))
        registry["generations"]["I2"] = {"role": "active"}
        self.assertTrue(any("registered" in x for x in self.assess(registry=registry)))
        contract = json.loads(json.dumps(self.contract))
        contract["entrypoints"]["runtime"] = "i2.fake"
        self.assertTrue(any("entrypoints" in x for x in self.assess(contract=contract)))

    def test_changed_archive_authority_is_rejected(self):
        manifest = json.loads(json.dumps(self.manifest))
        manifest["executable_activation"] = "ALLOWED"
        self.assertTrue(any("activation" in x for x in self.assess(manifest=manifest)))
        manifest = json.loads(json.dumps(self.manifest))
        manifest["baseline_main_commit"] = "0" * 40
        self.assertTrue(any("baseline" in x for x in self.assess(manifest=manifest)))


if __name__ == "__main__":
    unittest.main()
