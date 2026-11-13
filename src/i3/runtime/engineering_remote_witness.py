"""Network CAS witness client for I3 *engineering-only* native sessions.

An authority must be independently owned/deployed to protect against a common
rollback of local files. This module cannot attest deployment independence,
external motor exactly-once semantics, identity ownership or scientific GO.
No automatic retries: an ambiguous response must stop the acting process.
"""
from __future__ import annotations

from hashlib import sha256
import hmac
import json
import re
import secrets
import ssl
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPSHandler, HTTPHandler, HTTPRedirectHandler, Request, build_opener

from i3.runtime.birth_reservation import Reservation
from i3.runtime.engineering_step_ledger import REMOTE_MODE, inspect_pending

SCHEMA = "i3-engineering-remote-monotonic/v1"
HEX = re.compile(r"[0-9a-f]{64}\Z")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def intent_digest(identity: str, seq: int, previous: str, intent: dict) -> str:
    return sha256(canonical({"schema": SCHEMA, "identity": identity,
                             "sequence": seq, "previous": previous,
                             "intent": intent})).hexdigest()


def claim_data(claim: Reservation) -> dict:
    if type(claim) is not Reservation:
        raise TypeError("typed I3 engineering reservation required")
    return {"identity_sha256": claim.identity_sha256,
            "source_sha256": claim.source_sha256,
            "world_sha256": claim.world_sha256,
            "genome_sha256": claim.genome_sha256,
            "life_seed": claim.life_seed, "birth_index": claim.birth_index}


class _NeverRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise PermissionError("remote authority redirects are forbidden")


class RemoteEngineeringWitness:
    """Authenticated CAS to a separately deployed append-only authority.

    HTTPS is mandatory except explicitly opted-in 127.0.0.1 unit tests.
    HMAC authenticates protocol messages *only if the shared key stays secret*;
    an operator controlling both client code/key and local stores is NOT covered.
    """

    def __init__(self, base_url: str, *, key: bytes, authority_id: str,
                 timeout: float = 3.0, allow_test_loopback_http: bool = False,
                 tls_context: ssl.SSLContext | None = None,
                 commit_anchor=None):
        if type(base_url) is not str or type(key) is not bytes or len(key) < 32:
            raise ValueError("remote URL and >=32-byte authentication key required")
        if type(authority_id) is not str or not HEX.fullmatch(authority_id):
            raise ValueError("exact remote authority identifier required")
        if type(timeout) not in (float, int) or not 0 < timeout <= 30:
            raise ValueError("bounded remote timeout required")
        url = urlsplit(base_url)
        if (not url.hostname or not url.port or url.username or url.password
                or url.path not in ("", "/") or url.query or url.fragment):
            raise ValueError("remote URL must be an origin with an explicit port")
        if url.scheme != "https":
            if not (allow_test_loopback_http is True and url.scheme == "http"
                    and url.hostname == "127.0.0.1"):
                raise ValueError("HTTPS mandatory outside explicit loopback test")
        if tls_context is not None:
            if not isinstance(tls_context, ssl.SSLContext):
                raise ValueError("real TLS context required")
            if url.scheme != "https":
                raise ValueError("TLS context cannot secure loopback HTTP")
            # HTTPSHandler accepts arbitrary caller contexts. An unverified
            # context otherwise silently removes peer-certificate / hostname
            # checks despite the HTTPS URL. Refuse it BEFORE network or motor.
            if (tls_context.verify_mode != ssl.CERT_REQUIRED
                    or tls_context.check_hostname is not True
                    or tls_context.minimum_version < ssl.TLSVersion.TLSv1_2):
                raise ValueError(
                    "TLS CAS writer requires certificate and hostname verification"
                    " with TLS >= 1.2")
        self._origin = base_url.rstrip("/")
        self._key = key
        self.authority_id = authority_id
        self._timeout = timeout
        self._opener = build_opener(_NeverRedirect(), HTTPSHandler(context=tls_context),
                                    HTTPHandler())
        # Optional operator-supplied COMMITTED high-water pin. It is NOT an
        # attested off-host M11 anchor merely because it implements this API.
        # Any unavailable/untrusted anchor must fail closed, not be bypassed.
        if commit_anchor is not None and (
                not callable(getattr(commit_anchor, "assert_current", None))
                or not callable(getattr(commit_anchor, "publish", None))):
            raise ValueError("committed anchor needs assert_current and publish")
        self._commit_anchor = commit_anchor

    def _request(self, operation: str, **fields) -> dict:
        if operation not in {"register", "verify", "prepare", "commit"}:
            raise ValueError("unrecognized authority operation")
        data = canonical({"schema": SCHEMA, "authority_id": self.authority_id,
                          "operation": operation, **fields})
        if len(data) > 8192:
            raise PermissionError("oversized authority request")
        nonce = secrets.token_hex(16)
        signature = hmac.new(self._key, b"Q\n" + nonce.encode() + b"\n" + data,
                             sha256).hexdigest()
        req = Request(self._origin + "/v1/command", data=data, method="POST",
                      headers={"Content-Type": "application/json",
                               "X-I3-Nonce": nonce, "X-I3-Signature": signature})
        try:
            with self._opener.open(req, timeout=self._timeout) as resp:
                code = resp.status
                answer = resp.read(8193)
                received = resp.headers.get("X-I3-Signature", "")
        except (URLError, HTTPError, TimeoutError, OSError) as exc:
            raise PermissionError("remote authority unavailable/rejected: fail closed") from exc
        if code != 200 or len(answer) > 8192 or not HEX.fullmatch(received):
            raise PermissionError("unsigned or invalid remote authority response")
        expected = hmac.new(self._key, b"R\n" + nonce.encode() + b"\n" +
                            str(code).encode() + b"\n" + answer, sha256).hexdigest()
        if not hmac.compare_digest(expected, received):
            raise PermissionError("remote authority response authentication failed")
        try:
            data = json.loads(answer)
            if canonical(data) != answer or type(data) is not dict or set(data) != {
                    "schema", "authority_id", "identity_sha256", "sequence",
                    "head_sha256", "phase", "terminal", "pending_sequence",
                    "pending_intent_sha256"}:
                raise ValueError("wrong response schema")
            if data["schema"] != SCHEMA or data["authority_id"] != self.authority_id:
                raise ValueError("wrong authority")
            if (type(data["sequence"]) is not int or data["sequence"] < 0
                    or type(data["identity_sha256"]) is not str
                    or not HEX.fullmatch(data["identity_sha256"])
                    or type(data["head_sha256"]) is not str
                    or not HEX.fullmatch(data["head_sha256"])
                    or data["phase"] not in ("COMMITTED", "PREPARED")
                    or data["terminal"] not in ("OPEN", "DEAD", "CENSORED")):
                raise ValueError("bad response values")
            # A valid HMAC is not permission to accept a logically impossible
            # custody state. In particular bool is an int subclass in Python,
            # so exact pending-sequence typing is required before any motor.
            if data["phase"] == "COMMITTED":
                if (data["pending_sequence"] is not None
                        or data["pending_intent_sha256"] is not None):
                    raise ValueError("COMMITTED response has pending work")
            elif (data["terminal"] != "OPEN"
                  or type(data["pending_sequence"]) is not int
                  or data["pending_sequence"] != data["sequence"] + 1
                  or type(data["pending_intent_sha256"]) is not str
                  or not HEX.fullmatch(data["pending_intent_sha256"])):
                raise ValueError("invalid PREPARED response state")
            return data
        except (ValueError, TypeError) as exc:
            raise PermissionError("remote response cannot establish custody") from exc

    def register(self, claim: Reservation, ledger: dict) -> dict:
        if (ledger["witness_mode"] != REMOTE_MODE or ledger["sequence"] != 0
                or ledger["terminal"] != "OPEN" or ledger["prepared"] is not None
                or ledger["identity_sha256"] != claim.identity_sha256):
            raise PermissionError("remote birth registration requires empty exact ledger")
        out = self._request("register", claim=claim_data(claim),
                            horizon=ledger["horizon"], head_sha256=ledger["head_sha256"])
        self._check(out, claim, ledger)
        if self._commit_anchor is not None:
            self._commit_anchor.publish(out)  # reject failed/ambiguous genesis
        return out

    def verify(self, claim: Reservation, ledger: dict) -> dict:
        if ledger["witness_mode"] != REMOTE_MODE or ledger["prepared"] is not None:
            raise PermissionError("remote mode or stable ledger required")
        out = self._request("verify", claim=claim_data(claim))
        self._check(out, claim, ledger)
        if self._commit_anchor is not None:
            self._commit_anchor.assert_current(out)
        return out

    @staticmethod
    def _check(out: dict, claim: Reservation, ledger: dict) -> None:
        if (out["identity_sha256"] != claim.identity_sha256
                or out["sequence"] != ledger["sequence"]
                or out["head_sha256"] != ledger["head_sha256"]
                or out["terminal"] != ledger["terminal"]
                or out["phase"] != "COMMITTED"
                or out["pending_sequence"] is not None
                or out["pending_intent_sha256"] is not None):
            raise PermissionError("remote authority rejects stale or incomplete ledger")

    def prepared(self, directory, claim: Reservation, *, previous_ledger: dict,
                 intent: dict) -> dict:
        pending = inspect_pending(directory, claim)
        if (pending["witness_mode"] != REMOTE_MODE
                or pending["head_sha256"] != previous_ledger["head_sha256"]
                or pending["sequence"] != previous_ledger["sequence"]
                or pending["prepared"] is None
                or pending["prepared"]["seq"] != pending["sequence"] + 1
                or pending["prepared"]["intent"] != intent):
            raise PermissionError("remote PREPARED must follow exact ledger PREPARED")
        # Re-check an authenticated remote COMMITTED head against the
        # independently retained pin before asking permission for a motor.
        # The previous local receipt alone is not a trusted remote witness.
        # This extra read is an engineering transport/host cost.
        if self._commit_anchor is not None:
            self.verify(claim, previous_ledger)
        n = pending["prepared"]["seq"]
        d = intent_digest(claim.identity_sha256, n, pending["head_sha256"], intent)
        out = self._request("prepare", claim=claim_data(claim), sequence=n,
                            previous_head_sha256=pending["head_sha256"],
                            intent_sha256=d)
        if (out["identity_sha256"] != claim.identity_sha256 or out["phase"] != "PREPARED"
                or out["sequence"] != previous_ledger["sequence"]
                or out["head_sha256"] != previous_ledger["head_sha256"]
                or out["pending_sequence"] != n or out["pending_intent_sha256"] != d):
            raise PermissionError("authority did not acknowledge exact PREPARED")
        return out

    def committed(self, directory, claim: Reservation, *, previous_ledger: dict,
                  intent: dict) -> dict:
        from i3.runtime.engineering_step_ledger import inspect
        ledger = inspect(directory, claim)
        if (ledger["witness_mode"] != REMOTE_MODE
                or ledger["sequence"] != previous_ledger["sequence"] + 1
                or ledger["events"][-1]["intent"] != intent):
            raise PermissionError("local paid event not committed before remote acknowledgement")
        n = ledger["sequence"]
        d = intent_digest(claim.identity_sha256, n, previous_ledger["head_sha256"], intent)
        out = self._request("commit", claim=claim_data(claim), sequence=n,
                            previous_head_sha256=previous_ledger["head_sha256"],
                            intent_sha256=d, head_sha256=ledger["head_sha256"],
                            terminal=ledger["terminal"])
        self._check(out, claim, ledger)
        if self._commit_anchor is not None:
            self._commit_anchor.publish(out)
        return out
