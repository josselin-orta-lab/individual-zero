"""F1L scientific transport gates, adversarial negatives, ZERO L World.step.

All simulated GitHub calls are in-memory mocks. NO real GitHub ref is created,
NO heldout individual is instantiated, NO 32-root scientific result is read.
"""
from __future__ import annotations

import ast
import base64
from hashlib import sha256
from copy import deepcopy
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from tools import stage8f1l_one_shot_reservation as R
from tools import stage8f1l_one_shot_evidence as E
from tools import stage8f1l_scientific_native as P
from tools import stage8f1l_independent_scientific_cold as Cold
from tools import stage8f1l_one_shot_cold_entry as ColdEntry

HEAD = "a" * 40
PR_HEAD = "e" * 40
REHEARSAL_ID = "404040404040"
ENV = {
    "GITHUB_REPOSITORY": R.REPO,
    "GITHUB_REF": "refs/heads/main",
    "GITHUB_EVENT_NAME": "workflow_dispatch",
    "GITHUB_RUN_ATTEMPT": "1",
    "GITHUB_RUN_ID": "505050505050",
    "GITHUB_SHA": HEAD,
    "F1L_REHEARSAL_RUN_ID": REHEARSAL_ID,
    "F1L_APPROVED_SOURCE_SHA": HEAD,
    "F1L_CONSUME_ACK": R.ACK,
    "GITHUB_TOKEN": "TEST_FAKE_NEVER_SENT",
    "F1L_PROTECTION_AUDIT_TOKEN": "ADMIN_READ_FAKE_NEVER_SENT",
}


class FakeGitHub:
    def __init__(self):
        self.commit = None
        self.claim = None
        self.calls = []
        self.bad_tree = False
        self.bad_cold = False
        self.protection = True

    def api(self, method, path, payload=None):
        self.calls.append((method, path))
        if method == "GET" and path == "/rulesets":
            return ([{"id": 123, "enforcement": "active", "target": "branch"}]
                    if self.protection else [])
        if method == "GET" and path == "/rulesets/123":
            return {
                "id": 123, "enforcement": "active", "target": "branch",
                "source_type": "Repository",
                "conditions": {"ref_name": {
                    "include": [R.CONSUMED_REF], "exclude": []}},
                "bypass_actors": [], "rules": [
                    {"type": "deletion"},
                    {"type": "non_fast_forward"},
                    {"type": "update"},
                ],
            }
        if method == "GET" and path == "/git/ref/heads/main":
            return {"object": {"sha": HEAD}}
        if method == "GET" and path == "/git/ref/heads/" + R.BRANCH:
            if self.commit is None:
                raise R.ReservationError(
                    "F1L ONE SHOT: GitHub GET returned HTTP 404")
            return {"ref": R.CONSUMED_REF,
                    "object": {"sha": self.commit}}
        if method == "GET" and path == "/git/commits/" + HEAD:
            return {"tree": {"sha": "b" * 40}}
        if method == "GET" and path == "/git/commits/" + PR_HEAD:
            return {"tree": {"sha": "0" * 40 if self.bad_tree else "b" * 40}}
        if method == "GET" and path == "/actions/runs/" + REHEARSAL_ID:
            return {
                "status": "completed", "conclusion": "success",
                "event": "pull_request", "head_sha": PR_HEAD,
                "path": R.DEV_WORKFLOW, "repository": {"full_name": R.REPO},
            }
        if (method == "GET" and path ==
                "/actions/runs/" + REHEARSAL_ID + "/jobs?per_page=100"):
            jobs = R.REQUIRED_DEV_JOBS - ({
                "f1l_full_t60_independent_python312_cold"}
                if self.bad_cold else set())
            return {"jobs": [{"name": j, "status": "completed",
                              "conclusion": "success"} for j in jobs]}
        if method == "POST" and path == "/git/blobs":
            self.claim = payload["content"].encode("utf-8")
            return {"sha": R.blob(self.claim)}
        if method == "POST" and path == "/git/trees":
            assert payload["tree"][0]["path"] == R.MARKER_PATH
            return {"sha": "c" * 40}
        if method == "POST" and path == "/git/commits":
            assert payload["parents"] == [HEAD]
            return {"sha": "d" * 40}
        if method == "POST" and path == "/git/refs":
            if self.commit is not None:
                raise R.ReservationError("F1L ONE SHOT: GitHub HTTP 422")
            assert payload["ref"] == R.CONSUMED_REF
            self.commit = payload["sha"]
            return {"ref": R.CONSUMED_REF,
                    "object": {"sha": self.commit}}
        if method == "GET" and path.startswith("/contents/" + R.MARKER_PATH):
            return {
                "sha": R.blob(self.claim), "encoding": "base64",
                "content": base64.b64encode(self.claim).decode("ascii"),
            }
        raise AssertionError("Unexpected fake API operation: " + repr((method, path)))


class F1LOneShotSafety(unittest.TestCase):
    def _authority(self, fake):
        return (
            patch.dict(os.environ, ENV, clear=True),
            patch.object(R, "_api", side_effect=fake.api),
            patch("subprocess.check_output", return_value=HEAD + "\n"),
            patch.object(R, "immutable_release_policy",
                         return_value={"enabled": True}),
        )

    def test_frozen_32_roots_and_zero_exposure(self):
        pins = R.source_blobs()
        self.assertEqual(pins["src/i3/modules/mind.py"],
                         R.ENGINE_PINS["src/i3/modules/mind.py"])
        grid = P.release_grid()  # read-only JSON, NOT a native birth
        self.assertEqual(len(grid["origins"]), 32)
        self.assertEqual([r["id"] for r in grid["origins"]], R.ROOT_IDS)
        self.assertEqual([r["seed"] for r in grid["origins"]], R.SEEDS)
        self.assertEqual(len(grid["ecologies"]), 8)
        self.assertFalse(grid["scientific_exposure_authorized"])
        self.assertEqual(grid["arms"], R.ARMS)

    def test_direct_science_world_or_producer_without_remote_ref_denied(self):
        grid = P.release_grid()
        with self.assertRaises(PermissionError):
            P._new_world(grid, grid["origins"][0], None)
        with patch.object(R, "load_receipt", return_value={"test": True}), patch.object(
                R, "verify_remote",
                side_effect=R.ReservationError("NO CLAIM")), patch.object(
                P, "_new_world",
                side_effect=AssertionError("unexpected real heldout birth")):
            with self.assertRaises(R.ReservationError):
                P.produce_release("/nonexistent/F1L_RESERVATION.json", lambda x: x)

    def test_manual_first_run_context_denies_all_variants(self):
        with patch.dict(os.environ, ENV, clear=True), patch(
                "subprocess.check_output", return_value=HEAD + "\n"):
            self.assertEqual(R.context()["head_sha"], HEAD)
            for key, value in (
                ("GITHUB_RUN_ATTEMPT", "2"),
                ("GITHUB_EVENT_NAME", "pull_request"),
                ("GITHUB_REF", "refs/heads/dev"),
                ("GITHUB_RUN_ID", ""),
                ("F1L_REHEARSAL_RUN_ID", ""),
                ("F1L_CONSUME_ACK", "NOT_CONSENTED"),
                ("F1L_APPROVED_SOURCE_SHA", "f" * 40),
            ):
                with patch.dict(os.environ, {key: value}):
                    with self.assertRaises(R.ReservationError):
                        R.context()

    def test_ruleset_exact_ref_and_no_bypass_mandatory(self):
        fake = FakeGitHub()
        with patch.dict(os.environ, ENV, clear=True), patch.object(
                R, "_api", side_effect=fake.api):
            self.assertEqual(R.protected_once_ruleset()["id"], 123)
            fake.protection = False
            with self.assertRaises(R.ReservationError):
                R.protected_once_ruleset()

    def test_release_immutability_requires_admin_read_secret(self):
        with patch.dict(os.environ, {"GITHUB_TOKEN": "fake"}, clear=True):
            with self.assertRaises(R.ReservationError):
                R.immutable_release_policy()
        with patch.dict(os.environ, {
                "F1L_PROTECTION_AUDIT_TOKEN": "fake"}, clear=True):
            with patch("tools.stage8f1l_one_shot_reservation.urlopen",
                       side_effect=RuntimeError("offline test")):
                with self.assertRaises(RuntimeError):
                    R.immutable_release_policy()

    def test_atomic_remote_first_wins_and_rejects_second_attempt(self):
        fake = FakeGitHub()
        env, api, git, policy = self._authority(fake)
        with TemporaryDirectory() as folder, env, api, git, policy:
            first = R.reserve(Path(folder) / "first.json")
            self.assertEqual(first["reservation_commit"], "d" * 40)
            self.assertEqual(R.verify_remote(first)["root_ids"], R.ROOT_IDS)
            self.assertEqual(sum(method == "POST" and path == "/git/refs"
                                 for method, path in fake.calls), 1)
            with self.assertRaises(R.ReservationError):
                R.reserve(Path(folder) / "second.json")
            self.assertEqual(sum(method == "POST" and path == "/git/refs"
                                 for method, path in fake.calls), 1)
            forged = deepcopy(first)
            forged["claim"]["seeds"][-1] += 1000
            with self.assertRaises(R.ReservationError):
                R.validate_receipt(forged)

    def test_incomplete_or_different_tree_rehearsal_does_not_consume_ref(self):
        for reason in ("bad_tree", "bad_cold"):
            fake = FakeGitHub()
            setattr(fake, reason, True)
            env, api, git, policy = self._authority(fake)
            with TemporaryDirectory() as folder, env, api, git, policy:
                with self.assertRaises(R.ReservationError):
                    R.reserve(Path(folder) / "never.json")
                self.assertEqual(fake.commit, None)
                self.assertNotIn(("POST", "/git/refs"), fake.calls)

    def test_protection_absent_fails_before_remote_reservation(self):
        fake = FakeGitHub()
        fake.protection = False
        env, api, git, policy = self._authority(fake)
        with TemporaryDirectory() as folder, env, api, git, policy:
            with self.assertRaises(R.ReservationError):
                R.reserve(Path(folder) / "never.json")
            self.assertNotIn(("POST", "/git/refs"), fake.calls)

    def test_native_start_lock_exclusive_no_second_birth(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "F1L_RESERVATION.NATIVE_START_LOCK"
            claim = {"workflow_run_id": "12", "head_sha": HEAD}
            P._first_native_start_lock(path, claim)
            self.assertTrue(path.exists())
            with self.assertRaises(FileExistsError):
                P._first_native_start_lock(path, claim)

    def test_32_case_128_original_byte_custody_without_science(self):
        # Artificial INVALID source receipts, explicitly NOT native World.step.
        with TemporaryDirectory() as folder:
            root = Path(folder)
            report = {
                "schema": P.SCHEMA, "phase": P.PHASE, "origin_count": 32,
                "origin_ids": R.ROOT_IDS, "worlds": [
                    x["id"] for x in P.release_grid()["ecologies"]],
                "rows": [],
            }
            writer = E.CaseWriter(root / "original_cases", R.ROOT_IDS)
            for origin in P.release_grid()["origins"]:
                row = {
                    "origin": origin,
                    "source": {"valid_paid_personal_source": False,
                               "source_receipt_sha256": "test-no-native"},
                    "arms": {}, "comparison": {"fixture_only": True},
                }
                row["case_sha256"] = E.digest(E.canonical(row))
                writer(row)
                report["rows"].append(row)
            receipt = {"fake": "test-only"}
            E.finalize(
                writer, report, json.loads(E.canonical(report)), root,
                receipt, reproduction_kind=
                "F1L_CANONICAL_READBACK_NO_SECOND_NATIVE")
            check = E.verify_bundle(root)
            self.assertEqual(check["original_native_gzips"], 128)
            self.assertEqual(check["heldout_native_passes"], 1)
            with self.assertRaises((KeyError, ValueError, AssertionError)):
                Cold.audit(report)  # engine-free science auditor REJECTS FAKE
            index = root / "F1L_CUSTODY_MANIFEST.json"
            tampered = json.loads(index.read_text())
            tampered["roots"][-1] = "L99"
            index.write_bytes(E.canonical(tampered))
            with self.assertRaises((ValueError, AssertionError)):
                E.verify_bundle(root)

    def test_verdict_gate_precedence_and_strict_thresholds_no_exposure(self):
        def base():
            return [{
                "root": R.ROOT_IDS[i], "ecology": "ecology" + str(i // 4),
                "source_valid": True, "continuations_complete": True,
                "arm_valid": True, "sham_neutral": True,
                "equal_t5_decision_cost": True,
                "delta_lived_ticks": 0, "pareto": "FIVE_CHANNELS_EQUAL",
            } for i in range(32)]
        rows = base()
        self.assertEqual(
            Cold._classify(rows),
            "NO_REPRODUCIBLE_LOCAL_T60_CONTENT_BODY_ADVANTAGE")
        for i in (0, 4, 8, 1, 5, 9):
            rows[i]["delta_lived_ticks"] = 2
        self.assertEqual(
            Cold._classify(rows),
            "LOCAL_T60_RECENT_PERSONAL_CONTENT_SURVIVAL_GAIN_EQUAL_DECISION_COST")
        rows[31]["delta_lived_ticks"] = -1
        self.assertEqual(
            Cold._classify(rows),
            "NO_REPRODUCIBLE_LOCAL_T60_CONTENT_BODY_ADVANTAGE")
        rows[31]["sham_neutral"] = False
        self.assertEqual(Cold._classify(rows), "INVALID_FULL_SHAM")
        rows[31]["sham_neutral"] = True
        rows[31]["equal_t5_decision_cost"] = False
        self.assertEqual(
            Cold._classify(rows), "INCONCLUSIVE_CONTENT_DECISION_COST_GATE")
        rows[31]["source_valid"] = False
        self.assertEqual(
            Cold._classify(rows), "INCONCLUSIVE_UNFUNDED_PERSONAL_SOURCE")
        pareto = base()
        for i in (0, 1, 2, 4, 5, 6, 8, 9):
            pareto[i]["pareto"] = "FULL_FIVE_CHANNEL_DOMINANCE"
        self.assertEqual(
            Cold._classify(pareto),
            "LOCAL_T60_RECENT_CONTENT_PARETO_GAIN_NO_SURVIVAL_GAIN")
        pareto[31]["pareto"] = "STALE_FIVE_CHANNEL_DOMINANCE"
        self.assertEqual(
            Cold._classify(pareto),
            "NO_REPRODUCIBLE_LOCAL_T60_CONTENT_BODY_ADVANTAGE")


    def test_cold_works_only_with_verified_immutable_release_digests(self):
        """Synthetic opaque bytes ONLY; no native seed, motor or World.step."""
        with TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "f1l-originals").mkdir()
            fake_parts = {
                root / "F1L_RESERVATION.json": b"fake-reservation",
                root / "F1L_RESERVATION.NATIVE_START_LOCK": b"fake-lock",
                root / "f1l-originals/F1L_FIRST_NATIVE.json.gz": b"fake-first",
                root / "f1l-originals/F1L_ORIGINAL_NATIVE.json.gz": b"fake-original",
                root / "f1l-originals/F1L_CANONICAL_READBACK.json.gz": b"fake-copy",
                root / "f1l-originals/F1L_ORIGINALS_128_GZIP.tar.gz": b"fake-tar",
                root / "f1l-originals/F1L_CUSTODY_MANIFEST.json": b"fake-index",
            }
            for path, data in fake_parts.items():
                path.write_bytes(data)
            receipt = {"reservation_commit": "d" * 40}
            fake_release = {
                "tag_name": ColdEntry.RAW_RELEASE_TAG, "immutable": True,
                "target_commitish": receipt["reservation_commit"],
                "assets": [
                    {"name": p.name, "size": len(raw),
                     "digest": "sha256:" + sha256(raw).hexdigest()}
                    for p, raw in fake_parts.items()
                ],
            }
            with patch.object(R, "_api", return_value=fake_release) as remote:
                verified = ColdEntry.verify_immutable_raw_release(receipt, root)
                self.assertEqual(verified["raw_assets_byte_matched"], 7)
                self.assertTrue(verified["release_immutable"])
                remote.assert_called_once_with(
                    "GET", "/releases/tags/" + ColdEntry.RAW_RELEASE_TAG)
                fake_release["assets"][1]["digest"] = "sha256:" + "0" * 64
                with self.assertRaises(ValueError):
                    ColdEntry.verify_immutable_raw_release(receipt, root)
                fake_release["assets"][1]["digest"] = (
                    "sha256:" + sha256(fake_parts[
                        root / "F1L_RESERVATION.NATIVE_START_LOCK"]).hexdigest())
                fake_release["immutable"] = False
                with self.assertRaises(ValueError):
                    ColdEntry.verify_immutable_raw_release(receipt, root)
                fake_release["immutable"] = True
                fake_release["assets"].pop()
                with self.assertRaises(ValueError):
                    ColdEntry.verify_immutable_raw_release(receipt, root)

    def test_scientific_cold_module_never_imports_native_engine(self):
        paths = [
            "tools/stage8f1l_one_shot_cold_entry.py",
            "tools/stage8f1l_independent_scientific_cold.py",
            "tools/stage8f1l_independent_paid_content_cold_audit.py",
            "tools/stage8f1k_independent_policy_value_cold_audit.py",
            "tools/stage8f1j_independent_fixed_round_cold_audit.py",
        ]
        for path in paths:
            parsed = ast.parse(Path(path).read_text())
            for node in ast.walk(parsed):
                if isinstance(node, ast.Import):
                    self.assertFalse(
                        any(alias.name.startswith("i3") for alias in node.names),
                        path + ": engine import forbidden")
                elif isinstance(node, ast.ImportFrom):
                    self.assertFalse(
                        (node.module or "").startswith("i3"),
                        path + ": engine import forbidden")



if __name__ == "__main__":
    unittest.main()
