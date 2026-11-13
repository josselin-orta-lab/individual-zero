"""R2.7 no-World HTTPS fault matrix with REAL loopback TLS and ephemeral CA.

The server and signer live in this same test process. Passing these checks
must never be called independently attested M11 or live motor recovery.
"""
from contextlib import closing
from datetime import datetime, timedelta, timezone
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

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, rsa
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID

from i3.lab.engineering_remote_authority import AuthorityStore
from i3.lab.engineering_remote_checkpoint_publisher import (
    TestOnlyCheckpointPublisher,
)
from i3.lab.engineering_remote_https_latest_witness import (
    PATH, MAX_BYTES, PinnedHTTPSLatestWitness,
)
from i3.lab.engineering_remote_recovery_reconciliation import (
    reconcile_required_witness,
)
from i3.runtime.birth_reservation import make_reservation
from i3.runtime.engineering_remote_witness import (
    SCHEMA as REQUEST_SCHEMA, canonical, claim_data,
)


def _test_ca_and_tls_cert(folder: Path, prefix: str):
    """Generate loopback-only CA and TLS certificate; never a deployed key."""
    root_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    leaf_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    now = datetime.now(timezone.utc)
    root_name = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, prefix+" ephemeral test CA"),
    ])
    leaf_name = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
    ])
    ca = (x509.CertificateBuilder()
          .subject_name(root_name).issuer_name(root_name)
          .public_key(root_key.public_key()).serial_number(x509.random_serial_number())
          .not_valid_before(now - timedelta(minutes=10))
          .not_valid_after(now + timedelta(days=1))
          .add_extension(x509.BasicConstraints(ca=True, path_length=0),
                         critical=True)
          .add_extension(x509.KeyUsage(
              digital_signature=True, content_commitment=False,
              key_encipherment=False, data_encipherment=False,
              key_agreement=False, key_cert_sign=True, crl_sign=True,
              encipher_only=False, decipher_only=False), critical=True)
          .sign(root_key, hashes.SHA256()))
    leaf = (x509.CertificateBuilder()
            .subject_name(leaf_name).issuer_name(root_name)
            .public_key(leaf_key.public_key()).serial_number(x509.random_serial_number())
            .not_valid_before(now - timedelta(minutes=10))
            .not_valid_after(now + timedelta(days=1))
            .add_extension(x509.BasicConstraints(ca=False, path_length=None),
                           critical=True)
            .add_extension(x509.SubjectAlternativeName([x509.DNSName("localhost")]),
                           critical=False)
            .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]),
                           critical=False)
            .sign(root_key, hashes.SHA256()))
    ca_file = folder/(prefix+".ca.pem")
    cert_file = folder/(prefix+".leaf.pem")
    key_file = folder/(prefix+".leaf.key")
    ca_file.write_bytes(ca.public_bytes(serialization.Encoding.PEM))
    cert_file.write_bytes(leaf.public_bytes(serialization.Encoding.PEM))
    key_file.write_bytes(leaf_key.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption()))
    os.chmod(key_file, 0o600)
    return ca_file, cert_file, key_file


class _FixtureHTTPSHandler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        return

    def do_GET(self):
        server = self.server
        server.requests += 1
        server.last_path = self.path
        server.last_request_headers = dict(self.headers)
        if server.mode == "drop":
            self.connection.shutdown(socket.SHUT_RDWR)
            self.connection.close()
            return
        if server.mode == "redirect":
            self.send_response(302)
            self.send_header("Location", "https://other.example.test/")
            self.end_headers()
            return
        if server.mode == "status503":
            self.send_response(503)
            self.end_headers()
            return
        if server.mode == "status404":
            self.send_response(404)
            self.end_headers()
            return
        if self.path != PATH:
            self.send_response(404)
            self.end_headers()
            return
        data = server.latest
        if server.mode == "oversize":
            data = b"x" * (MAX_BYTES + 1)
        declared_length = (
            len(data) + 1 if server.mode == "truncated" else len(data))
        self.send_response(200)
        self.send_header(
            "Content-Type",
            "text/plain" if server.mode == "wrongtype"
            else "application/octet-stream")
        if server.mode != "missingcache":
            self.send_header(
                "Cache-Control",
                "public, max-age=3600" if server.mode == "cacheable"
                else "no-store")
        if server.mode == "gzip":
            self.send_header("Content-Encoding", "gzip")
        if server.mode == "chunked":
            self.send_header("Transfer-Encoding", "chunked")
        if server.mode != "nolength":
            self.send_header(
                "Content-Length",
                "000"+str(declared_length) if server.mode == "badlength"
                else str(declared_length))
            if server.mode == "duplength":
                self.send_header("Content-Length", str(declared_length))
        self.end_headers()
        self.wfile.write(data)
        self.wfile.flush()


class HTTPSLatestWitnessFaultTests(unittest.TestCase):
    AUTHORITY = "d" * 64
    SOURCE = "a" * 64
    KEY_ID = "test-r27-https"

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        folder = Path(tmp.name)
        self.auth_path = folder/"authority.sqlite3"
        self.pub_path = folder/"publisher.sqlite3"
        self.authority = AuthorityStore(self.auth_path, self.AUTHORITY)
        self.signer = ed25519.Ed25519PrivateKey.generate()
        self.public = self.signer.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        self.publisher = TestOnlyCheckpointPublisher(
            self.pub_path, self.auth_path, authority_id=self.AUTHORITY,
            source_sha256=self.SOURCE, key_id=self.KEY_ID,
            trusted_public_key=self.public, sign=self.signer.sign)
        self.claim = claim_data(make_reservation(
            birth_index=501, life_seed=99, source_sha256=self.SOURCE,
            world_sha256="b"*64, genome_sha256="c"*64))
        self.count = 0
        self.send("register", horizon=2, head_sha256="0"*64)
        self.first = self.publisher.publish("0"*64)

        self.ca_file, cert_file, key_file = _test_ca_and_tls_cert(folder, "trusted")
        self.foreign_ca, _, _ = _test_ca_and_tls_cert(folder, "foreign")
        server = ThreadingHTTPServer(("127.0.0.1", 0), _FixtureHTTPSHandler)
        server.daemon_threads = True
        server.mode = "success"
        server.latest = self.first
        server.requests = 0
        server.last_path = None
        server.last_request_headers = None
        tls = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        tls.minimum_version = ssl.TLSVersion.TLSv1_2
        tls.load_cert_chain(str(cert_file), str(key_file))
        server.socket = tls.wrap_socket(server.socket, server_side=True)
        thread = Thread(target=server.serve_forever,
                        kwargs={"poll_interval": 0.05}, daemon=True)
        thread.start()
        self.server = server
        self.addCleanup(self._shutdown, server, thread)
        self.endpoint = f"https://localhost:{server.server_port}{PATH}"

    @staticmethod
    def _shutdown(server, thread):
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)

    def send(self, operation, **fields):
        self.count += 1
        return self.authority.apply(
            {"schema": REQUEST_SCHEMA, "authority_id": self.AUTHORITY,
             "operation": operation, "claim": self.claim, **fields},
            request_nonce=f"{self.count:032x}")

    def reader(self, **changes):
        options = dict(
            endpoint=self.endpoint, ca_file=self.ca_file,
            authority_id=self.AUTHORITY, source_sha256=self.SOURCE,
            key_id=self.KEY_ID, trusted_public_key=self.public, timeout=2)
        options.update(changes)
        endpoint = options.pop("endpoint")
        return PinnedHTTPSLatestWitness(endpoint, **options)

    def reconcile(self, reader=None):
        current = self.reader() if reader is None else reader
        return reconcile_required_witness(
            self.auth_path, self.pub_path,
            authority_id=self.AUTHORITY, source_sha256=self.SOURCE,
            key_id=self.KEY_ID, trusted_public_key=self.public,
            target_identity_sha256=self.claim["identity_sha256"],
            fetch_required_latest=current.fetch_required_latest)

    def backup(self, path, suffix):
        backup = path.with_name(path.stem+"."+suffix+".sqlite3")
        with closing(sqlite3.connect(path)) as src:
            with closing(sqlite3.connect(backup)) as dst:
                src.backup(dst)
        return backup

    @staticmethod
    def restore(path, backup):
        os.replace(backup, path)
        for extension in ("-wal", "-shm"):
            sidecar = Path(str(path)+extension)
            if sidecar.exists():
                sidecar.unlink()

    def test_real_loopback_tls_ca_hostname_and_signed_readonly_reconciliation(self):
        reader = self.reader()
        with patch("i3.modules.world.World.__init__",
                   side_effect=AssertionError("World forbidden")):
            self.assertEqual(reader.fetch_required_latest(), self.first)
            state = self.reconcile(reader)
        self.assertEqual(state["result"], "READ_ONLY_MATCH_NO_MOTOR_AUTHORITY")
        self.assertFalse(state["motor_authority"])
        self.assertFalse(state["scientific_world_authorized"])
        self.assertFalse(state["independent_m11_attested"])
        self.assertEqual(self.server.last_path, PATH)
        self.assertEqual(self.server.last_request_headers.get("Cache-Control"),
                         "no-store")
        self.assertEqual(self.server.requests, 2)

    def test_untrusted_ca_or_hostname_mismatch_rejected_by_real_tls(self):
        with self.assertRaises(PermissionError):
            self.reader(ca_file=self.foreign_ca).fetch_required_latest()
        wrong_host = self.endpoint.replace("localhost", "127.0.0.1")
        with self.assertRaises(PermissionError):
            self.reader(endpoint=wrong_host).fetch_required_latest()

    def test_insecure_or_ambiguous_endpoint_ca_timeout_and_key_refused(self):
        bad_endpoints = (
            self.endpoint.replace("https:", "http:"),
            self.endpoint+"?query=1", self.endpoint+"#fragment",
            self.endpoint.replace("/v1/i3/receipt/latest", "/"),
            self.endpoint.replace("localhost", "user@localhost"),
            "https://localhost"+PATH,
            self.endpoint.replace("localhost", "local_host"),
        )
        for url in bad_endpoints:
            with self.subTest(url=url):
                with self.assertRaises(PermissionError):
                    self.reader(endpoint=url)
        with self.assertRaises(PermissionError):
            self.reader(ca_file=self.ca_file.parent/"missing.ca.pem")
        with self.assertRaises(PermissionError):
            self.reader(timeout=False)
        with self.assertRaises(PermissionError):
            self.reader(trusted_public_key=b"x"*31)

    def test_http_status_and_redirect_never_retried(self):
        for mode in ("redirect", "status503", "status404"):
            with self.subTest(mode=mode):
                self.server.mode = mode
                before = self.server.requests
                with self.assertRaises(PermissionError):
                    self.reader().fetch_required_latest()
                self.assertEqual(self.server.requests, before+1)

    def test_missing_bad_or_duplicate_content_length_fails_closed(self):
        for mode in ("nolength", "badlength", "duplength", "truncated"):
            with self.subTest(mode=mode):
                self.server.mode = mode
                before = self.server.requests
                with self.assertRaises(PermissionError):
                    self.reader().fetch_required_latest()
                self.assertEqual(self.server.requests, before+1)

    def test_oversized_type_cache_encoding_and_transfer_rejected(self):
        for mode in ("oversize", "wrongtype", "missingcache",
                     "cacheable", "gzip", "chunked"):
            with self.subTest(mode=mode):
                self.server.mode = mode
                before = self.server.requests
                with self.assertRaises(PermissionError):
                    self.reader().fetch_required_latest()
                self.assertEqual(self.server.requests, before+1)

    def test_dropped_tls_connection_is_stop_without_retry_or_fallback(self):
        self.server.mode = "drop"
        with self.assertRaisesRegex(PermissionError, "STOP"):
            self.reconcile()
        self.assertEqual(self.server.requests, 1)
        self.assertEqual(self.publisher.latest(), self.first)

    def test_signed_but_stale_https_response_rejected_by_local_highwater(self):
        self.send("verify")
        newer = self.publisher.publish(sha256(self.first).hexdigest())
        self.assertNotEqual(newer, self.first)
        self.assertEqual(self.reader().fetch_required_latest(), self.first)
        with self.assertRaisesRegex(PermissionError, "publisher differs"):
            self.reconcile()
        self.server.latest = newer
        self.assertEqual(self.reconcile()["publication_index"], 2)

    def test_signed_payload_tamper_or_foreign_key_denied_despite_valid_tls(self):
        changed = json.loads(self.first)
        changed["payload"]["source_sha256"] = "f"*64
        self.server.latest = canonical(changed)
        with self.assertRaises(PermissionError):
            self.reader().fetch_required_latest()
        self.server.latest = self.first
        alien_key = ed25519.Ed25519PrivateKey.generate()
        alien_pub = alien_key.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        with self.assertRaises(PermissionError):
            self.reader(trusted_public_key=alien_pub).fetch_required_latest()

    def test_valid_tls_and_valid_old_signature_after_all_domain_rollback_is_negative(self):
        old_authority = self.backup(self.auth_path, "old")
        old_publisher = self.backup(self.pub_path, "old")
        self.send("verify")
        newer = self.publisher.publish(sha256(self.first).hexdigest())
        self.server.latest = newer
        self.assertEqual(self.reconcile()["publication_index"], 2)
        self.restore(self.auth_path, old_authority)
        self.restore(self.pub_path, old_publisher)
        self.server.latest = self.first
        # Deliberately accepted: a real TLS handshake and a real signed old
        # receipt cannot detect a co-rollback of the *server's* high-water.
        # This must remain the negative FAIL_INDEPENDENT_M11.
        restored = self.reconcile()
        self.assertEqual(restored["publication_index"], 1)
        self.assertFalse(restored["motor_authority"])
        self.assertFalse(restored["independent_m11_attested"])


if __name__ == "__main__":
    unittest.main()
