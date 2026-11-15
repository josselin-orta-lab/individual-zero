"""Offline-only negative provenance tests, with generated throwaway TEST keys.

These signatures are created after the fabricated receipts are assembled.
They are not witnesses to any actual i3 life, seed allocation or first exposure.
"""
from __future__ import annotations

import ast
import base64
from copy import deepcopy
from hashlib import sha256
import inspect
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from i3.lab import stage6_light_signed_custody_preflight as v


def _hash(data: bytes) -> str:
    return sha256(data).hexdigest()


def _signed(payload: dict, key: Ed25519PrivateKey, domain: bytes,
            key_id: str) -> bytes:
    signed = v._canonical({"schema": v.SCHEMA, "payload": payload})
    sig = key.sign(domain + signed)
    return v._canonical({
        "schema": v.SCHEMA, "payload": payload,
        "signature": {"algorithm": "Ed25519", "key_id": key_id,
                      "value": base64.b64encode(sig).decode("ascii")},
    })


class Stage6SignedCustodyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="i3-stage6-fake-signed-")
        self.addCleanup(self.tmp.cleanup)
        self.method = Path(self.tmp.name) / "METHOD.json"
        self.method_data = {
            "schema": "i3-stage6-light-method-preauth/v1",
            "protocol_id": v.PROTOCOL,
            "status": "METHOD_FIXED_PREAUTH_NOT_EXECUTABLE",
            "phase": "design_only", "scientific_verdict": "NOT_ISSUED",
            "authorization": {
                **{name: False for name in v._DENIED},
                **{name: None for name in v._UNASSIGNED},
            },
            "custody": {
                "scientific_worlds_and_lives_now_allowed": False,
                "rehearsal_worlds_and_lives_now_allowed": False,
                "per_generation_selection_requires_separate_adr0017_acceptance": True,
            },
        }
        self.method.write_bytes(v._canonical(self.method_data))
        self.witness_private = Ed25519PrivateKey.generate()
        self.publisher_private = Ed25519PrivateKey.generate()
        def public(key):
            return key.public_key().public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw)
        self.witness_pub = public(self.witness_private)
        self.publisher_pub = public(self.publisher_private)
        self.pins = {
            "trusted_witness_public_key": self.witness_pub,
            "trusted_publisher_public_key": self.publisher_pub,
            "witness_key_id": "external-witness-test",
            "publisher_key_id": "run-publisher-test",
            "expected_run_id": _hash(b"fixture-run-identifier-not-a-study"),
            "expected_method_sha256": _hash(self.method.read_bytes()),
            "expected_source_sha256": _hash(b"invented-source-not-executed"),
            "expected_transport_sha256": _hash(b"invented-transport-not-executed"),
            "expected_allocation_sha256": _hash(b"no real allocations"),
            "expected_seed_commitment_sha256": _hash(b"invented seed root, no real seeds"),
        }
        self.precommit_payload = {
            "kind": "PRECOMMIT", "protocol_id": v.PROTOCOL,
            "run_id": self.pins["expected_run_id"],
            "method_sha256": self.pins["expected_method_sha256"],
            "source_sha256": self.pins["expected_source_sha256"],
            "transport_sha256": self.pins["expected_transport_sha256"],
            "allocation_sha256": self.pins["expected_allocation_sha256"],
            "seed_commitment_sha256": self.pins["expected_seed_commitment_sha256"],
            "witness_key_id": self.pins["witness_key_id"],
            "publisher_key_id": self.pins["publisher_key_id"],
        }
        self.precommit = self.seal_precommit()
        self.events = self.build_phases()

    def seal_precommit(self, *, payload=None, key=None):
        return _signed(
            self.precommit_payload if payload is None else payload,
            self.witness_private if key is None else key,
            v.ANCHOR_DOMAIN, self.pins["witness_key_id"])

    def seal_phase(self, payload, *, key=None):
        return _signed(payload,
                       self.publisher_private if key is None else key,
                       v.EVENT_DOMAIN, self.pins["publisher_key_id"])

    def build_phases(self, *, precommit=None):
        anchor = _hash(self.precommit if precommit is None else precommit)
        previous_raw_sha = anchor
        input_sha = self.pins["expected_seed_commitment_sha256"]
        phases = []
        for ordinal, phase in enumerate(v.PHASES, 1):
            artifact = _hash(f"INVENTED fake {ordinal} {phase}".encode())
            item = {
                "kind": "PHASE", "protocol_id": v.PROTOCOL,
                "run_id": self.pins["expected_run_id"],
                "phase": phase, "ordinal": ordinal,
                "precommit_sha256": anchor,
                "previous_receipt_sha256": previous_raw_sha,
                "input_artifact_sha256": input_sha,
                "artifact_sha256": artifact,
            }
            raw = self.seal_phase(item)
            phases.append(raw)
            previous_raw_sha = _hash(raw)
            input_sha = artifact
        return phases

    def audit(self, events=None, *, precommit=None, **changes):
        precommit = self.precommit if precommit is None else precommit
        events = self.events if events is None else events
        supplied = {**self.pins, **changes,
                    "retained_precommit_sha256": _hash(precommit),
                    "retained_latest_sha256": _hash(events[-1]) if events else _hash(precommit)}
        # Don't overwrite explicit high-water pin overrides.
        supplied.update({k: val for k, val in changes.items()})
        with patch.object(v, "METHOD", self.method):
            return v.inspect_signed_custody_prefix(precommit, events, **supplied)

    def re_sign_event(self, number, *, fields):
        events = self.events[:]
        item = json.loads(events[number])["payload"]
        item.update(fields)
        events[number] = self.seal_phase(item)
        return events

    def test_full_9_phase_signed_chain_is_not_proof_of_real_exposure(self):
        receipt = self.audit()
        self.assertEqual(receipt["phases_verified"], 9)
        self.assertEqual(receipt["phase_prefix"], list(v.PHASES))
        self.assertTrue(receipt["complete_declared_phase_chain"])
        for field in ("historical_first_exposure_time_attested",
                      "source_executed_and_seed_sampling_attested",
                      "true_original_gsr_order_attested",
                      "independent_original_archive_custody_attested",
                      "owner_authorization"):
            self.assertIs(receipt[field], False)
        self.assertEqual(receipt["science_verdict"], "NOT_ISSUED")
        self.assertEqual(receipt["new_worlds_opened"], 0)
        self.assertEqual(receipt["new_lives_created"], 0)

    def test_signed_precommit_only_and_prefix_never_authorize(self):
        self.assertEqual(self.audit([])["phases_verified"], 0)
        self.assertFalse(self.audit([])["complete_declared_phase_chain"])
        for n in (1, 2, 3, 5, 8):
            item = self.audit(self.events[:n])
            self.assertEqual(item["phases_verified"], n)
            self.assertFalse(item["complete_declared_phase_chain"])
            self.assertIs(item["owner_authorization"], False)

    def test_witness_signature_must_verify_independent_pinned_key(self):
        wrong = self.seal_precommit(key=self.publisher_private)
        with self.assertRaises(PermissionError):
            self.audit(self.build_phases(precommit=wrong), precommit=wrong)
        with self.assertRaises(PermissionError):
            self.audit(trusted_witness_public_key=self.publisher_pub)

    def test_publisher_signature_must_verify(self):
        altered = self.events[:]
        obj = json.loads(altered[0])
        obj["signature"]["value"] = base64.b64encode(bytes(64)).decode()
        altered[0] = v._canonical(obj)
        with self.assertRaises(PermissionError):
            self.audit(altered)

    def test_source_and_allocation_cannot_be_changed_postcommit(self):
        for key in ("expected_source_sha256", "expected_transport_sha256",
                    "expected_allocation_sha256", "expected_seed_commitment_sha256",
                    "expected_run_id"):
            with self.subTest(key=key), self.assertRaises(PermissionError):
                self.audit(**{key: _hash(b"different runtime or seeds")})

    def test_retained_anchor_and_latest_high_water_are_mandatory(self):
        with self.assertRaises(PermissionError):
            self.audit(retained_precommit_sha256=_hash(b"different precommit"))
        with self.assertRaises(PermissionError):
            self.audit(retained_latest_sha256=_hash(self.events[0]))
        with self.assertRaises(PermissionError):
            self.audit(retained_latest_sha256=None)

    def test_wrong_phase_order_or_bool_ordinal_rejected_even_if_signed(self):
        for index, change in ((0, {"phase": "SELECT_G1"}),
                              (0, {"ordinal": True}),
                              (3, {"phase": "G2"}),
                              (2, {"ordinal": 0})):
            with self.subTest(index=index, change=change):
                with self.assertRaises(PermissionError):
                    self.audit(self.re_sign_event(index, fields=change))

    def test_forged_previous_receipt_or_artifact_dependency_rejected(self):
        for key in ("previous_receipt_sha256", "input_artifact_sha256",
                    "precommit_sha256"):
            with self.subTest(key=key), self.assertRaises(PermissionError):
                self.audit(self.re_sign_event(1, fields={key: _hash(b"forged link")}))

    def test_duplicate_artifact_and_extra_phase_rejected(self):
        duplicated = json.loads(self.events[0])["payload"]["artifact_sha256"]
        with self.assertRaises(PermissionError):
            self.audit(self.re_sign_event(1, fields={"artifact_sha256": duplicated}))
        with self.assertRaises(PermissionError):
            self.audit(self.events + [self.events[-1]])

    def test_duplicate_json_keys_noncanonical_and_oversize_fails_closed(self):
        raw = self.precommit.replace(b'"kind":"PRECOMMIT"',
                                     b'"kind":"PRECOMMIT","kind":"PRECOMMIT"')
        with self.assertRaises(PermissionError):
            self.audit([], precommit=raw)
        with self.assertRaises(PermissionError):
            self.audit([], precommit=b"\n" + self.precommit)
        with self.assertRaises(PermissionError):
            self.audit([], precommit=b"{" + b" " * 4098 + b"}")

    def test_missing_or_identical_pinned_operator_keys_rejected(self):
        for change in (
            {"trusted_publisher_public_key": self.witness_pub},
            {"publisher_key_id": self.pins["witness_key_id"]},
            {"trusted_witness_public_key": b""},
            {"publisher_key_id": "unsafe/remote"},
        ):
            with self.subTest(change=change), self.assertRaises(PermissionError):
                self.audit(**change)

    def test_local_method_requires_byte_pin_and_deny_all(self):
        with patch.object(v, "METHOD", self.method):
            v._assert_denied_method(self.pins["expected_method_sha256"])
            with self.assertRaises(PermissionError):
                v._assert_denied_method(_hash(b"unknown method"))
            self.method_data["authorization"]["auto_start_allowed"] = True
            self.method.write_bytes(v._canonical(self.method_data))
            with self.assertRaises(PermissionError):
                v._assert_denied_method(_hash(self.method.read_bytes()))

    def test_checkout_method_if_available_is_still_deny_all(self):
        # Local development can execute only the focused mock fixture. In CI,
        # the original repository method MUST also satisfy the true guard.
        if not v.METHOD.is_file():
            self.skipTest("full repository method absent from isolated local test")
        real_pin = _hash(v.METHOD.read_bytes())
        v._assert_denied_method(real_pin)

    def test_no_world_imports_network_signing_or_executable_surface(self):
        src = inspect.getsource(v)
        imports = []
        for node in ast.walk(ast.parse(src)):
            if isinstance(node, ast.Import):
                imports.extend(a.name for a in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.append(node.module or "")
        self.assertFalse(any(name.startswith(("i3.runtime", "i3.modules"))
                             for name in imports))
        for func in (v.run_life, v.open_world, v.authorize_science):
            with self.assertRaises(PermissionError):
                func()


if __name__ == "__main__":
    unittest.main()
