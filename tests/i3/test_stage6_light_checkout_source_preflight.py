"""Read-only Git/source integrity tests. All byte contents are artificial.

The tests create temporary Git checkouts. They never import I3 biology,
construct a World, allocate a study seed, or execute a life.
"""
from __future__ import annotations

import ast
from copy import deepcopy
from hashlib import sha256
import inspect
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from i3.lab import stage6_light_checkout_source_preflight as v


def git(root: Path, *args: str) -> str:
    proc = subprocess.run(("git", "-C", str(root), *args),
                          capture_output=True, text=True, check=True)
    return proc.stdout.strip()


def denied_method() -> dict:
    return {
        "schema": "i3-stage6-light-method-preauth/v1",
        "protocol_id": "I3_STAGE6_LIGHT_METHOD_V1",
        "status": "METHOD_FIXED_PREAUTH_NOT_EXECUTABLE",
        "phase": "design_only", "scientific_verdict": "NOT_ISSUED",
        "authorization": {**{k: False for k in v.DENIED},
                          **{k: None for k in v.UNASSIGNED}},
        "custody": {
            "scientific_worlds_and_lives_now_allowed": False,
            "rehearsal_worlds_and_lives_now_allowed": False,
            "per_generation_selection_requires_separate_adr0017_acceptance": True,
        },
    }


class Stage6LightCheckoutSourceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="i3-stage6-fake-git-")
        self.root = Path(self.tmp.name)
        git(self.root, "init", "-q")
        git(self.root, "config", "user.name", "Stage6 fixture, not author")
        git(self.root, "config", "user.email", "fixture@example.invalid")
        self.src = self.root / "src/i3"
        (self.src / "lab").mkdir(parents=True)
        (self.src / "modules").mkdir()
        (self.src / "lab/alpha.py").write_bytes(b"# toy: no World\nx = 2\n")
        (self.src / "modules/beta.py").write_bytes(b"# toy: no Mind\ny = 'abc'\n")
        self.method = self.root / "method.json"
        self.method.write_text(json.dumps(denied_method(), sort_keys=True), encoding="utf-8")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "toy committed bytes, not scientific history")
        self.head = git(self.root, "rev-parse", "HEAD")
        self.files = {p.relative_to(self.src).as_posix(): sha256(p.read_bytes()).hexdigest()
                      for p in sorted(self.src.rglob("*.py"))}
        self.pin = v._canonical_digest(self.files)
        self.method_pin = sha256(self.method.read_bytes()).hexdigest()
        self.claim = {"files": dict(self.files), "sha256": self.pin,
                      "git_head": self.head, "working_tree_dirty": False}

    def tearDown(self):
        self.tmp.cleanup()

    def check(self, *, claim=None, head=None, pin=None, method_pin=None,
              method=None):
        return v.verify_checkout_source(
            checkout_root=self.root,
            source_record=self.claim if claim is None else claim,
            expected_git_head=self.head if head is None else head,
            expected_source_sha256=self.pin if pin is None else pin,
            expected_method_sha256=self.method_pin if method_pin is None else method_pin,
            method_path=self.method if method is None else method,
        )

    def test_committed_toy_tree_with_external_sha_pins_passes_without_world(self):
        result = self.check()
        self.assertEqual(result["status"], "CHECKOUT_BYTES_MATCH_EXTERNAL_PINS_PREAUTH_ONLY")
        self.assertEqual(result["source_file_count"], 2)
        self.assertEqual(result["git_head"], self.head)
        self.assertEqual(result["source_sha256"], self.pin)
        self.assertTrue(result["source_bytes_against_checkout_verified"])
        self.assertTrue(result["git_head_tree_bytes_verified"])
        self.assertFalse(result["external_pre_execution_timestamp_attested"])
        self.assertFalse(result["source_or_method_independently_authenticated"])
        self.assertFalse(result["owner_authorization"])
        self.assertEqual((result["worlds_opened"], result["lives_executed"]), (0, 0))
        self.assertEqual(result["scientific_verdict"], "NOT_ISSUED")

    def test_no_biology_or_cli_imports_and_all_launch_methods_refuse(self):
        text = Path(inspect.getfile(v)).read_text(encoding="utf-8")
        imports = []
        for node in ast.walk(ast.parse(text)):
            if isinstance(node, ast.Import):
                imports += [alias.name for alias in node.names]
            if isinstance(node, ast.ImportFrom):
                imports.append(node.module)
        self.assertFalse(any(n and (n == "i3" or n.startswith("i3.")) for n in imports))
        self.assertNotIn("if __name__", text)
        for method in (v.run_life, v.open_world, v.authorize_science):
            with self.assertRaises(PermissionError):
                method("fake-life", owner_token="fake")

    def test_external_source_pin_is_mandatory_and_not_taken_from_the_claim(self):
        with self.assertRaises(ValueError):
            self.check(pin="a" * 64)
        with self.assertRaises(ValueError):
            self.check(head="b" * 40)
        with self.assertRaises(ValueError):
            self.check(pin="bad")
        with self.assertRaises(ValueError):
            self.check(head="not-a-commit")
        claim = deepcopy(self.claim)
        claim["working_tree_dirty"] = True
        with self.assertRaises(ValueError):
            self.check(claim=claim)

    def test_dirty_checkout_rejected_even_if_snapshot_matches_original_bytes(self):
        (self.src / "modules/beta.py").write_bytes(b"y = 'tampered'\n")
        with self.assertRaises(ValueError):
            self.check()

    def test_untracked_python_and_non_python_files_refused(self):
        extra = self.src / "lab/new.py"
        extra.write_text("# untracked fake\n")
        with self.assertRaises(ValueError):
            self.check()
        extra.unlink()
        (self.root / "UNTRACKED.txt").write_text("fake")
        with self.assertRaises(ValueError):
            self.check()

    def test_modified_bytes_with_assume_unchanged_are_still_caught(self):
        src = self.src / "lab/alpha.py"
        git(self.root, "update-index", "--assume-unchanged", "src/i3/lab/alpha.py")
        src.write_text("x = 999\n")
        with self.assertRaises(ValueError):
            self.check()

    def test_head_commit_mismatch_or_ref_change_is_rejected(self):
        self.assertNotEqual(self.head, "c" * 40)
        with self.assertRaises(ValueError):
            self.check(head="c" * 40)
        git(self.root, "commit", "--allow-empty", "-qm", "a fake second commit")
        with self.assertRaises(ValueError):
            self.check()

    def test_method_content_pin_and_all_denials_are_mandatory(self):
        changed = denied_method()
        changed["authorization"]["worlds_allowed"] = True
        self.method.write_text(json.dumps(changed, sort_keys=True))
        with self.assertRaises(PermissionError):
            self.check()
        method_pin = sha256(self.method.read_bytes()).hexdigest()
        with self.assertRaises(PermissionError):
            self.check(method_pin=method_pin)
        changed["authorization"]["worlds_allowed"] = False
        changed["authorization"]["assigned_world_seeds"] = [123]
        self.method.write_text(json.dumps(changed, sort_keys=True))
        with self.assertRaises(PermissionError):
            self.check(method_pin=sha256(self.method.read_bytes()).hexdigest())

    def test_source_manifest_must_cover_every_python_path_exactly_once(self):
        claim = deepcopy(self.claim)
        del claim["files"]["modules/beta.py"]
        claim["sha256"] = v._canonical_digest(claim["files"])
        with self.assertRaises(ValueError):
            self.check(claim=claim, pin=claim["sha256"])
        claim = deepcopy(self.claim)
        claim["files"]["../../escaped.py"] = "a" * 64
        claim["sha256"] = v._canonical_digest(claim["files"])
        with self.assertRaises(ValueError):
            self.check(claim=claim, pin=claim["sha256"])
        claim = deepcopy(self.claim)
        claim["files"][".hidden.py"] = "a" * 64
        claim["sha256"] = v._canonical_digest(claim["files"])
        with self.assertRaises(ValueError):
            self.check(claim=claim, pin=claim["sha256"])

    def test_fake_self_consistent_hashes_cannot_replace_committed_bytes(self):
        claim = deepcopy(self.claim)
        claim["files"]["lab/alpha.py"] = "0" * 64
        claim["sha256"] = v._canonical_digest(claim["files"])
        with self.assertRaises(ValueError):
            self.check(claim=claim, pin=claim["sha256"])

    def test_source_symlink_rejected_even_when_tracked_and_pinned(self):
        (self.src / "modules/beta.py").unlink()
        (self.src / "modules/beta.py").symlink_to("../lab/alpha.py")
        git(self.root, "add", "-A")
        git(self.root, "commit", "-qm", "new symlink in fake repo")
        files = dict(self.files)
        files["modules/beta.py"] = sha256((self.src / "modules/beta.py").read_bytes()).hexdigest()
        claim = {"files": files, "sha256": v._canonical_digest(files),
                 "git_head": git(self.root, "rev-parse", "HEAD"),
                 "working_tree_dirty": False}
        with self.assertRaises(ValueError):
            self.check(claim=claim, head=claim["git_head"], pin=claim["sha256"])

    def test_absent_git_root_or_missing_source_fails(self):
        with self.assertRaises(ValueError):
            v.verify_checkout_source(
                checkout_root=self.src, source_record=self.claim,
                expected_git_head=self.head, expected_source_sha256=self.pin,
                expected_method_sha256=self.method_pin, method_path=self.method)
        (self.src / "modules/beta.py").unlink()
        with self.assertRaises(ValueError):
            self.check()


if __name__ == "__main__":
    unittest.main()
