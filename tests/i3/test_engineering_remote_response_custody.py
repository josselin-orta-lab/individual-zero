"""Signed remote witness response strictness, no World or scientific births.

The forged signatures use a fixed unit-test HMAC key. These tests exercise
client-side protocol parsing; they do NOT represent off-host authentication.
"""
from hashlib import sha256
import hmac
from unittest.mock import patch
import unittest

from i3.runtime.engineering_remote_witness import (
    SCHEMA, RemoteEngineeringWitness, canonical,
)


class FakeHTTPResponse:
    """Minimal detached HTTP 200 test response, never contacts a service."""

    status = 200

    def __init__(self, payload, signature):
        self.payload = payload
        self.headers = {"X-I3-Signature": signature}

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self, max_bytes):
        return self.payload[:max_bytes]


class SignedResponseCustodyTests(unittest.TestCase):
    KEY = bytes(range(32))
    AUTHORITY = "d" * 64
    CLAIM = "a" * 64
    HEAD = "b" * 64
    INTENT = "c" * 64
    NONCE = "1" * 32

    def setUp(self):
        self.client = RemoteEngineeringWitness(
            "http://127.0.0.1:34719", key=self.KEY,
            authority_id=self.AUTHORITY, allow_test_loopback_http=True)

    def state(self, **changes):
        value = {
            "schema": SCHEMA,
            "authority_id": self.AUTHORITY,
            "identity_sha256": self.CLAIM,
            "sequence": 0,
            "head_sha256": self.HEAD,
            "phase": "COMMITTED",
            "terminal": "OPEN",
            "pending_sequence": None,
            "pending_intent_sha256": None,
        }
        value.update(changes)
        return value

    def receive(self, state, *, request_nonce=None, response_nonce=None):
        nonce = self.NONCE if request_nonce is None else request_nonce
        signed_for = nonce if response_nonce is None else response_nonce
        payload = canonical(state)
        mac = hmac.new(
            self.KEY, b"R\n" + signed_for.encode("ascii") +
            b"\n200\n" + payload, sha256).hexdigest()
        response = FakeHTTPResponse(payload, mac)
        with patch("i3.runtime.engineering_remote_witness.secrets.token_hex",
                   return_value=nonce):
            with patch.object(self.client._opener, "open", return_value=response) as call:
                value = self.client._request(
                    "verify", claim={"identity_sha256": self.CLAIM})
        self.assertEqual(call.call_count, 1)
        return value

    def test_canonical_committed_and_prepared_signed_responses_are_accepted(self):
        committed = self.state()
        self.assertEqual(self.receive(committed), committed)
        prepared = self.state(
            phase="PREPARED", pending_sequence=1,
            pending_intent_sha256=self.INTENT)
        self.assertEqual(self.receive(prepared), prepared)

    def test_signed_committed_phase_cannot_carry_any_pending_work(self):
        cases = (
            {"pending_sequence": 1},
            {"pending_intent_sha256": self.INTENT},
            {"pending_sequence": True},
            {"pending_sequence": 0, "pending_intent_sha256": self.INTENT},
        )
        for changes in cases:
            with self.subTest(changes=changes):
                with self.assertRaisesRegex(
                        PermissionError, "response cannot establish custody"):
                    self.receive(self.state(**changes))

    def test_signed_prepared_phase_requires_consistent_exact_pending_shape(self):
        good = self.state(
            phase="PREPARED", pending_sequence=1,
            pending_intent_sha256=self.INTENT)
        invalid = (
            {"terminal": "DEAD"},
            {"terminal": "CENSORED"},
            {"pending_sequence": None},
            {"pending_sequence": True},  # bool compares equal to 1 in Python
            {"pending_sequence": 2},
            {"pending_sequence": 0},
            {"pending_intent_sha256": None},
            {"pending_intent_sha256": "not-a-hash"},
        )
        for changes in invalid:
            with self.subTest(changes=changes):
                with self.assertRaisesRegex(
                        PermissionError, "response cannot establish custody"):
                    self.receive(dict(good, **changes))

    def test_signed_old_response_cannot_be_replayed_with_new_request_nonce(self):
        self.assertEqual(self.receive(self.state(), request_nonce="1" * 32),
                         self.state())
        # Even with an unchanged body/authority ID and valid old HMAC, the
        # next independently minted nonce must invalidate the old answer.
        with self.assertRaisesRegex(
                PermissionError, "response authentication failed"):
            self.receive(self.state(), request_nonce="2" * 32,
                         response_nonce="1" * 32)

    def test_signed_foreign_authority_and_malformed_state_fail_closed(self):
        with self.assertRaisesRegex(
                PermissionError, "response cannot establish custody"):
            self.receive(self.state(authority_id="f" * 64))
        with self.assertRaisesRegex(
                PermissionError, "response cannot establish custody"):
            self.receive(self.state(sequence=True))
        with self.assertRaisesRegex(
                PermissionError, "response cannot establish custody"):
            self.receive(self.state(terminal="ALIVE"))


if __name__ == "__main__":
    unittest.main()
