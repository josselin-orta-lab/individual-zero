"""R2.11 real-loopback mutual TLS writer/source CAS admission, software only.

All keys, CA, service and SQLite are in ONE ephemeral CI domain. No World,
scientific cohort, independently protected high-water or production M11.
"""
from contextlib import closing
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from pathlib import Path
import os
import sqlite3
import ssl
import tempfile
from threading import Thread
import unittest

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID

from i3.lab.engineering_remote_authority import serve_test_loopback
from i3.runtime.birth_reservation import make_reservation, reserve
from i3.runtime.engineering_step_ledger import (
    INTENT_SCHEMA, RECEIPT_SCHEMA, REMOTE_MODE, initialize, inspect, prepare, seal,
)
from i3.runtime.engineering_remote_witness import (
    RemoteEngineeringWitness, claim_data,
)


def _test_ca(folder, name):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    ident = x509.Name([x509.NameAttribute(
        NameOID.COMMON_NAME, name + " ephemeral test authority")])
    now = datetime.now(timezone.utc)
    cert = (
        x509.CertificateBuilder().subject_name(ident).issuer_name(ident)
        .public_key(key.public_key()).serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=10))
        .not_valid_after(now + timedelta(days=1))
        .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
        .add_extension(x509.KeyUsage(
            digital_signature=True, content_commitment=False,
            key_encipherment=False, data_encipherment=False,
            key_agreement=False, key_cert_sign=True, crl_sign=True,
            encipher_only=False, decipher_only=False), critical=True)
        .sign(key, hashes.SHA256()))
    file = folder / (name + ".ca.pem")
    file.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    return key, cert, file


def _test_leaf(folder, name, ca_key, ca_cert, *, server=False):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost" if server else name),
    ])
    now = datetime.now(timezone.utc)
    builder = (
        x509.CertificateBuilder().subject_name(subject)
        .issuer_name(ca_cert.subject).public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=10))
        .not_valid_after(now + timedelta(days=1))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None),
                       critical=True)
        .add_extension(x509.KeyUsage(
            digital_signature=True, content_commitment=False,
            key_encipherment=True, data_encipherment=False,
            key_agreement=False, key_cert_sign=False, crl_sign=False,
            encipher_only=False, decipher_only=False), critical=True)
        .add_extension(x509.ExtendedKeyUsage([
            ExtendedKeyUsageOID.SERVER_AUTH if server
            else ExtendedKeyUsageOID.CLIENT_AUTH]), critical=False))
    if server:
        builder = builder.add_extension(
            x509.SubjectAlternativeName([x509.DNSName("localhost")]),
            critical=False)
    cert = builder.sign(ca_key, hashes.SHA256())
    certfile = folder / (name + ".pem")
    keyfile = folder / (name + ".key")
    certfile.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    keyfile.write_bytes(key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption()))
    os.chmod(keyfile, 0o600)
    return certfile, keyfile, sha256(
        cert.public_bytes(serialization.Encoding.DER)).hexdigest()


class StrictMTLSWriterAdmissionTests(unittest.TestCase):
    KEY = bytes(range(32))
    AUTHORITY = "d" * 64
    SOURCE = "a" * 64

    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.db = self.root / "authority.sqlite3"
        ca_key, ca_cert, self.ca = _test_ca(self.root, "allowed")
        self.server_leaf = _test_leaf(
            self.root, "server", ca_key, ca_cert, server=True)
        self.writer_leaf = _test_leaf(
            self.root, "writer", ca_key, ca_cert)
        self.other_leaf = _test_leaf(
            self.root, "same-ca-other-writer", ca_key, ca_cert)
        other_key, other_cert, self.foreign_ca = _test_ca(
            self.root, "foreign")
        self.foreign_leaf = _test_leaf(
            self.root, "foreign-writer", other_key, other_cert)
        tls = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        tls.minimum_version = ssl.TLSVersion.TLSv1_2
        tls.verify_mode = ssl.CERT_REQUIRED
        tls.load_cert_chain(str(self.server_leaf[0]), str(self.server_leaf[1]))
        tls.load_verify_locations(cafile=str(self.ca))
        self.server_context = tls
        self.server = serve_test_loopback(
            self.db, self.AUTHORITY, self.KEY, port=0,
            test_tls_context=tls,
            expected_writer_cert_sha256=self.writer_leaf[2],
            expected_source_sha256=self.SOURCE)
        self.server.daemon_threads = True
        self.thread = Thread(target=self.server.serve_forever,
                             kwargs={"poll_interval": 0.05}, daemon=True)
        self.thread.start()
        self.addCleanup(self._close)
        self.endpoint = "https://localhost:%d" % self.server.server_port
        self.writer = self._client(self.writer_leaf)

    def _close(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)

    def _client(self, leaf=None, *, ca=None):
        ctx = ssl.create_default_context(
            purpose=ssl.Purpose.SERVER_AUTH,
            cafile=str(self.ca if ca is None else ca))
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        if leaf is not None:
            ctx.load_cert_chain(str(leaf[0]), str(leaf[1]))
        return RemoteEngineeringWitness(
            self.endpoint, key=self.KEY, authority_id=self.AUTHORITY,
            timeout=2.0, tls_context=ctx)

    def _claim(self, *, source=None, index=7):
        return make_reservation(
            birth_index=index, life_seed=79,
            source_sha256=self.SOURCE if source is None else source,
            world_sha256="b"*64, genome_sha256="c"*64)

    def _request_register(self, client, *, source=None, index=7):
        return client._request(
            "register", claim=claim_data(self._claim(source=source, index=index)),
            horizon=2, head_sha256="0"*64)

    def _counts(self):
        with closing(sqlite3.connect(self.db)) as c:
            return (c.execute("SELECT count(*) FROM histories").fetchone()[0],
                    c.execute("SELECT count(*) FROM request_nonces").fetchone()[0])

    def _local_genesis(self):
        folder = self.root / "birth"
        folder.mkdir()
        claim = self._claim()
        reserve(folder, claim)
        ledger = initialize(
            folder, claim, horizon=2,
            initial_body=[95.0, 85.0, 75.0, 65.0, 55.0],
            witness_mode=REMOTE_MODE)
        return folder, claim, ledger

    def test_real_mtls_cas_register_prepare_commit_verify_without_world(self):
        folder, claim, ledger = self._local_genesis()
        accepted = self.writer.register(claim, ledger)
        self.assertEqual(accepted["sequence"], 0)
        self.assertEqual(self.writer.verify(claim, ledger)["phase"], "COMMITTED")
        intent = {
            "schema": INTENT_SCHEMA, "tick_before": 0,
            "body_before": ledger["last_body"],
            "action": "attendre", "param": None,
            "decision_work": {"cycles": 1, "simulated_steps": 2,
                              "memory_items": 0, "replays": 0},
        }
        pending = prepare(
            folder, claim, expected_head=ledger["head_sha256"], intent=intent)
        ready = self.writer.prepared(
            folder, claim, previous_ledger=ledger, intent=intent)
        self.assertEqual(ready["phase"], "PREPARED")
        self.assertEqual(ready["pending_sequence"], 1)
        before = ledger["last_body"]
        after_motor = [before[0]-1., before[1]-.2, before[2]-.3,
                       before[3], before[4]-.2]
        after_learning = [after_motor[0]-.03, *after_motor[1:4],
                          after_motor[4]-.06]
        receipt = {
            "schema": RECEIPT_SCHEMA, "phase": "POST_PAID_LEARNING",
            "tick": 1, "action": "attendre", "param": None,
            "body_after_motor": after_motor,
            "body_after_paid_learning": after_learning,
            "decision_paid": {"energy": .1, "vigilance": .2},
            "learning_paid": {"energy": .03, "vigilance": .06},
            "death_causes": [], "world_state_sha256": "e"*64,
            "mind_state_sha256": "f"*64,
        }
        seal(folder, claim, expected_head=pending["prior_head_sha256"],
             seal_token=pending["seal_token"], receipt=receipt)
        committed = self.writer.committed(
            folder, claim, previous_ledger=ledger, intent=intent)
        self.assertEqual(committed["sequence"], 1)
        self.assertEqual(committed["phase"], "COMMITTED")
        self.assertEqual(committed["terminal"], "OPEN")
        self.assertEqual(self.writer.verify(
            claim, inspect(folder, claim))["head_sha256"], committed["head_sha256"])

    def test_same_ca_unauthorized_writer_with_same_hmac_denied_before_db(self):
        with self.assertRaises(PermissionError):
            self._request_register(self._client(self.other_leaf))
        self.assertEqual(self._counts(), (0, 0))

    def test_missing_client_certificate_denied_by_real_tls_handshake(self):
        with self.assertRaises(PermissionError):
            self._request_register(self._client())
        self.assertEqual(self._counts(), (0, 0))

    def test_foreign_ca_client_certificate_denied_by_real_tls_handshake(self):
        with self.assertRaises(PermissionError):
            self._request_register(self._client(self.foreign_leaf))
        self.assertEqual(self._counts(), (0, 0))

    def test_wrong_server_trust_ca_denied_before_db(self):
        with self.assertRaises(PermissionError):
            self._request_register(self._client(
                self.writer_leaf, ca=self.foreign_ca))
        self.assertEqual(self._counts(), (0, 0))

    def test_authorized_writer_wrong_claim_source_denied_before_db(self):
        with self.assertRaises(PermissionError):
            self._request_register(self.writer, source="f"*64)
        self.assertEqual(self._counts(), (0, 0))

    def test_unapproved_writer_denied_before_prepared_transition(self):
        folder, claim, view = self._local_genesis()
        self.writer.register(claim, view)
        previous = self._counts()
        with self.assertRaises(PermissionError):
            self._client(self.other_leaf)._request(
                "prepare", claim=claim_data(claim), sequence=1,
                previous_head_sha256=view["head_sha256"],
                intent_sha256="e"*64)
        self.assertEqual(self._counts(), previous)
        self.assertEqual(self.writer.verify(claim, view)["phase"], "COMMITTED")

    def test_incomplete_or_insecure_mtls_settings_rejected_before_db_creation(self):
        absent = self.root/"must-not-be-created.sqlite3"
        kwargs = {"port": 0, "test_tls_context": self.server_context,
                  "expected_writer_cert_sha256": self.writer_leaf[2],
                  "expected_source_sha256": self.SOURCE}
        cases = (
            {"expected_writer_cert_sha256": None},
            {"expected_source_sha256": None},
            {"expected_writer_cert_sha256": "not-a-digest"},
            {"expected_source_sha256": "not-a-digest"},
            {"test_tls_context": "not-an-ssl-context"},
            {"test_tls_context": None},
        )
        for changes in cases:
            with self.subTest(changes=changes):
                with self.assertRaises(ValueError):
                    serve_test_loopback(
                        absent, self.AUTHORITY, self.KEY,
                        **dict(kwargs, **changes))
                self.assertFalse(absent.exists())
        unverified = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        with self.assertRaises(ValueError):
            serve_test_loopback(
                absent, self.AUTHORITY, self.KEY,
                **dict(kwargs, test_tls_context=unverified))
        self.assertFalse(absent.exists())


if __name__ == "__main__":
    unittest.main()
