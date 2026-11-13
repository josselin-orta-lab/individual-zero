"""R2.8 engineering-only nonce-bound online signed-witness HTTPS reader.

Proves possession of the pinned online reply key *for a fresh challenge*, NOT
monotonic storage custody, witness operator independence, source admission,
native motor recovery, or physical World truth. All release gates remain STOP.
"""
from __future__ import annotations

import base64
import binascii
import http.client
import json
import re
import secrets

from i3.lab.engineering_remote_https_latest_witness import (
    PATH as LEGACY_PATH, PinnedHTTPSLatestWitness,
)
from i3.lab.engineering_remote_signed_checkpoint_receipt import (
    verify_signed_checkpoint_receipt,
)
from i3.runtime.engineering_remote_witness import canonical

PATH = "/v1/i3/receipt/challenge"
REQUEST_SCHEMA = "i3-online-challenge-witness-request/v1"
RESPONSE_SCHEMA = "i3-online-challenge-witness-response/v1"
DOMAIN = b"I3-R28-ONLINE-WITNESS/v1\0"
MAX_RESPONSE_BYTES = 16384
_MAX_RECEIPT_BYTES = 8192
_NONCE = re.compile(r"[0-9a-f]{32}\Z")
_KEY_ID = re.compile(r"[a-z0-9][a-z0-9._-]{0,63}\Z")
_LENGTH = re.compile(r"[1-9][0-9]{0,4}\Z")
_RESPONSE_KEYS = {
    "schema", "nonce", "responder_key_id", "signed_receipt_b64",
    "signature_b64",
}


def _no_duplicate_pairs(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError("duplicate JSON response field")
        obj[key] = value
    return obj


def _decode_canonical_base64(value: str, expected_size: int | None = None) -> bytes:
    if type(value) is not str:
        raise ValueError("base64 signature/receipt must be a string")
    try:
        decoded = base64.b64decode(value, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise ValueError("noncanonical base64 response field") from exc
    if (base64.b64encode(decoded).decode("ascii") != value
            or (expected_size is not None and len(decoded) != expected_size)):
        raise ValueError("noncanonical base64 length/padding")
    return decoded


class PinnedHTTPSChallengedWitness(PinnedHTTPSLatestWitness):
    """A strict, one-request, separately responder-signed read-only probe.

    This is NOT a network publisher. A malicious or rolled-back *live* signer
    may sign a stale valid receipt for the new nonce; R2.6 and independent
    protected high-water custody remain necessary.
    """

    def __init__(self, endpoint: str, *, ca_file, trusted_public_key: bytes,
                 authority_id: str, source_sha256: str, key_id: str,
                 responder_public_key: bytes, responder_key_id: str,
                 timeout: float = 3.0):
        if type(endpoint) is not str or not endpoint.endswith(PATH):
            raise PermissionError("exact online witness challenge path required")
        # Reuse R2.7 CA/hostname/port validation. Any extra path, query,
        # fragment, userinfo, origin ambiguity or HTTP URL is still rejected.
        base = endpoint[:-len(PATH)]
        super().__init__(
            base + LEGACY_PATH, ca_file=ca_file,
            trusted_public_key=trusted_public_key,
            authority_id=authority_id, source_sha256=source_sha256,
            key_id=key_id, timeout=timeout)
        if (type(responder_public_key) is not bytes
                or len(responder_public_key) != 32
                or type(responder_key_id) is not str
                or _KEY_ID.fullmatch(responder_key_id) is None):
            raise PermissionError("explicit pinned online responder key/identity required")
        self._responder_key = responder_public_key
        self._responder_key_id = responder_key_id

    def fetch_required_latest(self) -> bytes:
        """One authenticated POST for a fresh nonce, return exact issuer bytes.

        Does not retry, fall back or authorize any native motor or World.
        """
        nonce = secrets.token_hex(16)
        if type(nonce) is not str or _NONCE.fullmatch(nonce) is None:
            raise PermissionError("cryptographic request nonce unavailable: STOP")
        request_bytes = canonical({"schema": REQUEST_SCHEMA, "nonce": nonce})
        conn = http.client.HTTPSConnection(
            self._host, self._port, timeout=self._timeout,
            context=self._context)
        try:
            conn.request(
                "POST", PATH, body=request_bytes,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Cache-Control": "no-store",
                    "Pragma": "no-cache",
                })
            response = conn.getresponse()
            if response.status != 200:
                raise PermissionError("online witness challenge HTTP status not 200: STOP")
            headers = response.headers
            lengths = headers.get_all("Content-Length", [])
            if (len(lengths) != 1
                    or type(lengths[0]) is not str
                    or _LENGTH.fullmatch(lengths[0]) is None
                    or int(lengths[0]) > MAX_RESPONSE_BYTES):
                raise PermissionError("online witness response needs exact bounded length")
            if (response.getheader("Content-Type") != "application/json"
                    or response.getheader("Cache-Control") != "no-store"
                    or response.getheader("Content-Encoding") not in (None, "identity")
                    or response.getheader("Transfer-Encoding") is not None
                    or response.getheader("Location") is not None):
                raise PermissionError("online witness response has unsafe HTTP headers")
            body = response.read(int(lengths[0]) + 1)
            if type(body) is not bytes or len(body) != int(lengths[0]):
                raise PermissionError("online witness truncated/oversized response")
            try:
                result = json.loads(body, object_pairs_hook=_no_duplicate_pairs)
                if (type(result) is not dict
                        or set(result) != _RESPONSE_KEYS
                        or canonical(result) != body
                        or result["schema"] != RESPONSE_SCHEMA
                        or result["nonce"] != nonce
                        or result["responder_key_id"] != self._responder_key_id):
                    raise ValueError("wrong/noncanonical responder or fresh nonce")
                signature = _decode_canonical_base64(
                    result["signature_b64"], expected_size=64)
                receipt = _decode_canonical_base64(result["signed_receipt_b64"])
                if not 0 < len(receipt) <= _MAX_RECEIPT_BYTES:
                    raise ValueError("signed issuer receipt too large/empty")
                signed = DOMAIN + canonical({
                    "schema": RESPONSE_SCHEMA, "nonce": nonce,
                    "responder_key_id": self._responder_key_id,
                    "signed_receipt_b64": result["signed_receipt_b64"],
                })
                try:
                    from cryptography.exceptions import InvalidSignature
                    from cryptography.hazmat.primitives.asymmetric.ed25519 import (
                        Ed25519PublicKey,
                    )
                except ImportError as exc:
                    raise PermissionError(
                        "online responder Ed25519 dependency unavailable: STOP") from exc
                try:
                    Ed25519PublicKey.from_public_bytes(
                        self._responder_key).verify(signature, signed)
                except (InvalidSignature, ValueError) as exc:
                    raise PermissionError("online responder signature invalid: STOP") from exc
                verify_signed_checkpoint_receipt(receipt, **self._pins)
                return receipt
            except (ValueError, TypeError, KeyError, UnicodeError) as exc:
                raise PermissionError("online witness reply malformed/freshness failed: STOP") from exc
        except PermissionError:
            raise
        except (OSError, http.client.HTTPException, EOFError) as exc:
            raise PermissionError("online witness HTTPS unavailable: STOP") from exc
        finally:
            conn.close()


__all__ = [
    "PATH", "REQUEST_SCHEMA", "RESPONSE_SCHEMA", "DOMAIN",
    "PinnedHTTPSChallengedWitness",
]
