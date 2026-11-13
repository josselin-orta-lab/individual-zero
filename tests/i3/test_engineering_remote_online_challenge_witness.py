"""R2.8 real loopback TLS + independent-in-test Ed25519 challenge signer.

A live key response to a nonce is not proof of non-rewindable server state.
Both local SQLite stores and the TLS responder share one test worker.
"""
import base64
from contextlib import closing
from hashlib import sha256
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import socket
import sqlite3
import ssl
import tempfile
from threading import Thread
import unittest
from unittest.mock import patch

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from i3.lab.engineering_remote_authority import AuthorityStore
from i3.lab.engineering_remote_checkpoint_publisher import (
    TestOnlyCheckpointPublisher,
)
from i3.lab.engineering_remote_online_challenge_witness import (
    DOMAIN, PATH, REQUEST_SCHEMA, RESPONSE_SCHEMA,
    PinnedHTTPSChallengedWitness,
)
from i3.lab.engineering_remote_recovery_reconciliation import (
    reconcile_required_witness,
)
from i3.runtime.birth_reservation import make_reservation
from i3.runtime.engineering_remote_witness import (
    SCHEMA as CAS_SCHEMA, canonical, claim_data,
)
from test_engineering_remote_https_latest_witness import _test_ca_and_tls_cert


class _ChallengeTLSHandler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        return

    def do_POST(self):
        server = self.server
        server.requests += 1
        server.paths.append(self.path)
        server.last_headers = dict(self.headers)
        if server.mode == "drop":
            self.connection.shutdown(socket.SHUT_RDWR)
            self.connection.close()
            return
        if server.mode in ("redirect", "unavailable"):
            self.send_response(302 if server.mode == "redirect" else 503)
            if server.mode == "redirect":
                self.send_header("Location", "https://untrusted.invalid/")
            self.end_headers()
            return
        if self.path != PATH:
            self.send_error(404)
            return
        size = int(self.headers.get("Content-Length", "0"))
        request_raw = self.rfile.read(size)
        server.last_request = request_raw
        try:
            request = json.loads(request_raw)
            if (type(request) is not dict
                    or set(request) != {"schema", "nonce"}
                    or request["schema"] != REQUEST_SCHEMA
                    or canonical(request) != request_raw):
                self.send_error(400)
                return
        except (TypeError, ValueError, KeyError):
            self.send_error(400)
            return
        server.nonces.append(request["nonce"])
        if server.mode == "replay":
            response_bytes = server.recorded_reply
        else:
            nonce = ("f"*32 if server.mode == "wrong_nonce"
                     else request["nonce"])
            receipt = server.latest
            if server.mode == "bad_issuer":
                tampered = json.loads(receipt)
                tampered["payload"]["source_sha256"] = "f"*64
                receipt = canonical(tampered)
            unsigned = {
                "schema": RESPONSE_SCHEMA, "nonce": nonce,
                "responder_key_id": (
                    "other-online-key" if server.mode == "foreign_id"
                    else server.responder_key_id),
                "signed_receipt_b64": base64.b64encode(receipt).decode("ascii"),
            }
            signer = (server.foreign_signer if server.mode == "foreign_key"
                      else server.responder_signer)
            signature = signer.sign(DOMAIN + canonical(unsigned))
            response = dict(
                unsigned, signature_b64=base64.b64encode(
                    signature).decode("ascii"))
            response_bytes = canonical(response)
            if server.mode == "bad_base64":
                response["signature_b64"] = "*"*88
                response_bytes = canonical(response)
            elif server.mode == "bad_signature":
                response["signature_b64"] = base64.b64encode(
                    b"\x00" * 64).decode("ascii")
                response_bytes = canonical(response)
            elif server.mode == "duplicate_field":
                response_bytes = (
                    b'{"schema":"x","schema":"x"}')
            elif server.mode == "noncanonical":
                response_bytes += b"\n"
            server.recorded_reply = response_bytes
        server.last_response = response_bytes
        if server.mode == "oversize":
            response_bytes = b"x" * 16385
        self.send_response(200)
        self.send_header(
            "Content-Type", "text/plain" if server.mode == "wrong_type"
            else "application/json")
        if server.mode != "missing_cache":
            self.send_header(
                "Cache-Control", "public" if server.mode == "cacheable"
                else "no-store")
        if server.mode == "gzip":
            self.send_header("Content-Encoding", "gzip")
        if server.mode == "chunked":
            self.send_header("Transfer-Encoding", "chunked")
        if server.mode != "no_length":
            length = (len(response_bytes)+1 if server.mode == "truncated"
                      else len(response_bytes))
            self.send_header(
                "Content-Length", "00"+str(length)
                if server.mode == "bad_length" else str(length))
            if server.mode == "duplicate_length":
                self.send_header("Content-Length", str(length))
        self.end_headers()
        self.wfile.write(response_bytes)
        self.wfile.flush()


class OnlineWitnessChallengeTests(unittest.TestCase):
    AUTHORITY = "d" * 64
    SOURCE = "a" * 64
    ISSUER_ID = "r28-test-issuer"
    RESPONDER_ID = "r28-test-online-responder"

    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        self.authority_db = root / "authority.sqlite3"
        self.publisher_db = root / "publisher.sqlite3"
        self.auth = AuthorityStore(self.authority_db, self.AUTHORITY)
        self.issuer = Ed25519PrivateKey.generate()
        self.responder = Ed25519PrivateKey.generate()
        self.foreign = Ed25519PrivateKey.generate()
        self.issuer_pub = self.issuer.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        self.responder_pub = self.responder.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        self.pub = TestOnlyCheckpointPublisher(
            self.publisher_db, self.authority_db,
            authority_id=self.AUTHORITY, source_sha256=self.SOURCE,
            key_id=self.ISSUER_ID, trusted_public_key=self.issuer_pub,
            sign=self.issuer.sign)
        self.claim = claim_data(make_reservation(
            birth_index=901, life_seed=778, source_sha256=self.SOURCE,
            world_sha256="b"*64, genome_sha256="c"*64))
        self.nonce = 0
        self.send("register", horizon=3, head_sha256="0"*64)
        self.first = self.pub.publish("0"*64)

        self.ca, cert, key = _test_ca_and_tls_cert(root, "r28")
        self.wrong_ca, _, _ = _test_ca_and_tls_cert(root, "r28-wrong")
        server = ThreadingHTTPServer(("127.0.0.1", 0), _ChallengeTLSHandler)
        server.daemon_threads = True
        server.mode = "success"
        server.latest = self.first
        server.responder_signer = self.responder
        server.foreign_signer = self.foreign
        server.responder_key_id = self.RESPONDER_ID
        server.requests = 0
        server.nonces = []
        server.paths = []
        server.recorded_reply = b""
        server.last_headers = None
        server.last_response = None
        server.last_request = None
        tls = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        tls.minimum_version = ssl.TLSVersion.TLSv1_2
        tls.load_cert_chain(str(cert), str(key))
        server.socket = tls.wrap_socket(server.socket, server_side=True)
        thread = Thread(target=server.serve_forever,
                        kwargs={"poll_interval": 0.05}, daemon=True)
        thread.start()
        self.server = server
        self.addCleanup(self._close, server, thread)
        self.endpoint = f"https://localhost:{server.server_port}{PATH}"

    @staticmethod
    def _close(server, thread):
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)

    def send(self, operation, **kwargs):
        self.nonce += 1
        return self.auth.apply({
            "schema": CAS_SCHEMA, "authority_id": self.AUTHORITY,
            "operation": operation, "claim": self.claim, **kwargs,
        }, request_nonce=f"{self.nonce:032x}")

    def reader(self, **changes):
        options = dict(
            endpoint=self.endpoint, ca_file=self.ca,
            trusted_public_key=self.issuer_pub,
            authority_id=self.AUTHORITY, source_sha256=self.SOURCE,
            key_id=self.ISSUER_ID,
            responder_public_key=self.responder_pub,
            responder_key_id=self.RESPONDER_ID, timeout=2.0)
        options.update(changes)
        return PinnedHTTPSChallengedWitness(**options)

    def reconcile(self, reader=None):
        reader = self.reader() if reader is None else reader
        return reconcile_required_witness(
            self.authority_db, self.publisher_db,
            authority_id=self.AUTHORITY, source_sha256=self.SOURCE,
            key_id=self.ISSUER_ID, trusted_public_key=self.issuer_pub,
            target_identity_sha256=self.claim["identity_sha256"],
            fetch_required_latest=reader.fetch_required_latest)

    def advance(self):
        self.send("verify")
        return self.pub.publish(sha256(self.first).hexdigest())

    def backup(self, path, label):
        target = path.with_name(path.stem+"."+label+".sqlite3")
        with closing(sqlite3.connect(path)) as src:
            with closing(sqlite3.connect(target)) as dest:
                src.backup(dest)
        return target

    @staticmethod
    def restore(path, old):
        os.replace(old, path)
        for suffix in ("-wal", "-shm"):
            sidecar = Path(str(path)+suffix)
            if sidecar.exists():
                sidecar.unlink()

    def test_real_tls_live_nonce_and_readonly_r26_consistency(self):
        reader = self.reader()
        with patch("i3.modules.world.World.__init__",
                   side_effect=AssertionError("World construction forbidden")):
            self.assertEqual(reader.fetch_required_latest(), self.first)
            self.assertEqual(reader.fetch_required_latest(), self.first)
            state = self.reconcile(reader)
        self.assertEqual(state["result"], "READ_ONLY_MATCH_NO_MOTOR_AUTHORITY")
        self.assertFalse(state["motor_authority"])
        self.assertFalse(state["scientific_world_authorized"])
        self.assertFalse(state["independent_m11_attested"])
        self.assertEqual(len(self.server.nonces), 3)
        self.assertEqual(len(set(self.server.nonces)), 3)
        self.assertTrue(all(path == PATH for path in self.server.paths))
        self.assertEqual(self.server.last_headers["Content-Type"],
                         "application/json")

    def test_captured_full_response_replay_cannot_answer_fresh_nonce(self):
        self.assertEqual(self.reader().fetch_required_latest(), self.first)
        old = self.server.recorded_reply
        self.server.mode = "replay"
        before = self.server.requests
        with self.assertRaisesRegex(PermissionError, "freshness"):
            self.reader().fetch_required_latest()
        self.assertEqual(self.server.requests, before+1)
        self.assertEqual(self.server.recorded_reply, old)
        self.assertNotEqual(self.server.nonces[-1], self.server.nonces[-2])

    def test_wrong_signed_nonce_rejected_even_with_correct_responder_key(self):
        self.server.mode = "wrong_nonce"
        with self.assertRaisesRegex(PermissionError, "freshness"):
            self.reader().fetch_required_latest()

    def test_foreign_responder_signer_id_and_public_pin_rejected(self):
        for mode in ("foreign_key", "foreign_id"):
            with self.subTest(mode=mode):
                self.server.mode = mode
                with self.assertRaises(PermissionError):
                    self.reader().fetch_required_latest()
        self.server.mode = "success"
        with self.assertRaises(PermissionError):
            self.reader(responder_public_key=b"x"*32).fetch_required_latest()
        with self.assertRaises(PermissionError):
            self.reader(responder_key_id="wrong").fetch_required_latest()

    def test_responder_signs_mutated_issuer_receipt_still_denied(self):
        self.server.mode = "bad_issuer"
        with self.assertRaises(PermissionError):
            self.reader().fetch_required_latest()

    def test_tls_foreign_ca_and_hostname_denied(self):
        with self.assertRaises(PermissionError):
            self.reader(ca_file=self.wrong_ca).fetch_required_latest()
        with self.assertRaises(PermissionError):
            self.reader(endpoint=self.endpoint.replace(
                "localhost", "127.0.0.1")).fetch_required_latest()

    def test_endpoint_and_pins_invalid_are_rejected_before_network(self):
        bad = (self.endpoint.replace("https:", "http:"),
               self.endpoint+"?x=1", self.endpoint+"#fragment",
               self.endpoint.replace("/v1/i3/receipt/challenge", "/"),
               self.endpoint.replace("localhost", "user@localhost"))
        for endpoint in bad:
            with self.subTest(endpoint=endpoint):
                with self.assertRaises(PermissionError):
                    self.reader(endpoint=endpoint)
        with self.assertRaises(PermissionError):
            self.reader(responder_public_key=b"x"*31)
        with self.assertRaises(PermissionError):
            self.reader(ca_file=self.ca.parent/"missing.ca.pem")

    def test_status_redirect_and_connection_loss_stop_once(self):
        for mode in ("redirect", "unavailable", "drop"):
            with self.subTest(mode=mode):
                self.server.mode = mode
                before = self.server.requests
                with self.assertRaises(PermissionError):
                    self.reader().fetch_required_latest()
                self.assertEqual(self.server.requests, before+1)

    def test_bad_http_length_cache_type_encoding_denied(self):
        for mode in ("no_length", "bad_length", "duplicate_length",
                     "truncated", "oversize", "wrong_type", "missing_cache",
                     "cacheable", "gzip", "chunked"):
            with self.subTest(mode=mode):
                self.server.mode = mode
                before = self.server.requests
                with self.assertRaises(PermissionError):
                    self.reader().fetch_required_latest()
                self.assertEqual(self.server.requests, before+1)

    def test_duplicate_noncanonical_json_and_corrupted_signature_denied(self):
        for mode in ("duplicate_field", "noncanonical",
                     "bad_base64", "bad_signature"):
            with self.subTest(mode=mode):
                self.server.mode = mode
                with self.assertRaises(PermissionError):
                    self.reader().fetch_required_latest()

    def test_invalid_random_source_stops_before_network_send(self):
        before = self.server.requests
        with patch(
                "i3.lab.engineering_remote_online_challenge_witness.secrets.token_hex",
                return_value="invalid nonce"):
            with self.assertRaisesRegex(PermissionError, "nonce unavailable"):
                self.reader().fetch_required_latest()
        self.assertEqual(self.server.requests, before)

    def test_new_challenge_can_authenticate_old_receipt_but_r26_denies_stale(self):
        newer = self.advance()
        self.assertNotEqual(newer, self.first)
        self.assertEqual(self.reader().fetch_required_latest(), self.first)
        with self.assertRaisesRegex(PermissionError, "publisher differs"):
            self.reconcile()
        self.server.latest = newer
        self.assertEqual(self.reconcile()["publication_index"], 2)

    def test_rollback_both_databases_and_server_under_fresh_challenge_negative(self):
        old_auth = self.backup(self.authority_db, "old")
        old_pub = self.backup(self.publisher_db, "old")
        newer = self.advance()
        self.server.latest = newer
        newer_read = self.reconcile()
        self.assertEqual(newer_read["publication_index"], 2)
        recent_nonce = self.server.nonces[-1]
        self.restore(self.authority_db, old_auth)
        self.restore(self.publisher_db, old_pub)
        self.server.latest = self.first
        # The online test key is still live and signs the NEW nonce over the
        # OLD valid receipt: even challenge-response cannot detect rollback.
        state = self.reconcile()
        self.assertEqual(state["publication_index"], 1)
        self.assertNotEqual(self.server.nonces[-1], recent_nonce)
        self.assertFalse(state["motor_authority"])
        self.assertFalse(state["independent_m11_attested"])


if __name__ == "__main__":
    unittest.main()
