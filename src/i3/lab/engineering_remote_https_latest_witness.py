"""Read-only HTTPS latest signed witness fetch for I3 R2.7 engineering.

A pinned TLS endpoint and authentic Ed25519 receipt are NOT a protected
monotonic high-water or independent M11 operator. No retries, caching, hidden
Worlds, signing keys, or native motor/recovery authority exist here.
"""
from __future__ import annotations

import http.client
from pathlib import Path
import re
import ssl
from urllib.parse import urlsplit

from i3.lab.engineering_remote_signed_checkpoint_receipt import (
    verify_signed_checkpoint_receipt,
)

PATH = "/v1/i3/receipt/latest"
MAX_BYTES = 8192
_CONTENT_LENGTH = re.compile(r"[1-9][0-9]{0,4}\Z")
_HOST_LABEL = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\Z")


class PinnedHTTPSLatestWitness:
    """Fetch exactly one latest Ed25519 receipt over CA-verified HTTPS.

    The TLS CA, expected DNS/port, Ed25519 key, issuer and source pins must
    originate from an operator outside the rollback domain. This module
    cannot verify that organizational property and never claims independent
    M11 attestation. It is not a network server or a motor gate by itself.
    """

    def __init__(self, endpoint: str, *, ca_file: Path,
                 trusted_public_key: bytes, authority_id: str,
                 source_sha256: str, key_id: str, timeout: float = 3.0):
        if type(endpoint) is not str or not endpoint.isascii():
            raise PermissionError("HTTPS latest witness endpoint must be canonical ASCII")
        try:
            url = urlsplit(endpoint)
            host, port = url.hostname, url.port
        except ValueError as exc:
            raise PermissionError("invalid HTTPS witness endpoint") from exc
        if (url.scheme != "https" or not host or not port
                or url.username is not None or url.password is not None
                or url.query or url.fragment or url.path != PATH
                or endpoint != f"https://{host}:{port}{PATH}"
                or any(_HOST_LABEL.fullmatch(label) is None
                       for label in host.split("."))):
            raise PermissionError(
                "explicit canonical https://DNS:port/v1/i3/receipt/latest required")
        if (type(timeout) not in (float, int)
                or not 0 < timeout <= 10):
            raise PermissionError("positive bounded socket timeout required")
        try:
            ca = Path(ca_file)
        except (TypeError, ValueError) as exc:
            raise PermissionError("external CA bundle file required") from exc
        if (ca.is_symlink() or ca.parent.is_symlink() or not ca.is_file()):
            raise PermissionError("existing nonsymlink CA bundle required")
        try:
            context = ssl.create_default_context(
                purpose=ssl.Purpose.SERVER_AUTH, cafile=str(ca))
        except (OSError, ssl.SSLError, ValueError) as exc:
            raise PermissionError("CA trust bundle invalid: fail closed") from exc
        if not context.check_hostname or context.verify_mode != ssl.CERT_REQUIRED:
            raise PermissionError("verified TLS hostname/certificate required")
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        # Verify pin shape immediately (without accepting self-declared trust).
        if (type(trusted_public_key) is not bytes
                or len(trusted_public_key) != 32):
            raise PermissionError("explicit pinned Ed25519 public key required")
        self._host = host
        self._port = port
        self._timeout = timeout
        self._context = context
        self._pins = {
            "trusted_public_key": trusted_public_key,
            "expected_authority_id": authority_id,
            "expected_source_sha256": source_sha256,
            "expected_key_id": key_id,
        }

    def fetch_required_latest(self) -> bytes:
        """One authenticated bounded GET; STOP on any response ambiguity.

        The endpoint may still serve a genuine *old* signed receipt if its
        operator or storage is rolled back. R2.6 must compare it against its
        independently retained expectations, never use this as motor GO.
        """
        conn = http.client.HTTPSConnection(
            self._host, self._port, timeout=self._timeout,
            context=self._context)
        try:
            conn.request(
                "GET", PATH, headers={"Accept": "application/octet-stream",
                                      "Cache-Control": "no-store",
                                      "Pragma": "no-cache"})
            response = conn.getresponse()
            if response.status != 200:
                raise PermissionError("latest witness HTTP status not 200: STOP")
            headers = response.headers
            lengths = headers.get_all("Content-Length", [])
            if (len(lengths) != 1
                    or type(lengths[0]) is not str
                    or _CONTENT_LENGTH.fullmatch(lengths[0]) is None):
                raise PermissionError(
                    "latest witness requires one canonical Content-Length")
            length = int(lengths[0])
            if length > MAX_BYTES:
                raise PermissionError("latest witness receipt exceeds size cap")
            if (response.getheader("Content-Type") != "application/octet-stream"
                    or response.getheader("Cache-Control") != "no-store"
                    or response.getheader("Content-Encoding") not in (None, "identity")
                    or response.getheader("Transfer-Encoding") is not None
                    or response.getheader("Location") is not None):
                raise PermissionError("latest witness HTTP headers are ambiguous")
            body = response.read(length + 1)
            if type(body) is not bytes or len(body) != length:
                raise PermissionError("latest witness body truncated or exceeded cap")
            # Application-layer verification is essential in addition to TLS.
            # An authentic signature does NOT establish remote freshness.
            verify_signed_checkpoint_receipt(body, **self._pins)
            return body
        except PermissionError:
            raise
        except (OSError, http.client.HTTPException, EOFError) as exc:
            raise PermissionError("latest witness HTTPS unavailable: STOP") from exc
        finally:
            conn.close()


__all__ = ["PATH", "MAX_BYTES", "PinnedHTTPSLatestWitness"]
