"""No-World I3 remote authority transport and common-local-rollback tests."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from hashlib import sha256
from email.message import Message
import hmac
from pathlib import Path
import os
import secrets
import socket
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest

from i3.runtime.birth_reservation import make_reservation, reserve, DB_NAME as BIRTH_DB
from i3.runtime.engineering_step_ledger import (
    REMOTE_MODE, INTENT_SCHEMA, RECEIPT_SCHEMA, DB_NAME as LEDGER_DB,
    initialize, inspect, prepare, seal,
)
from i3.runtime.engineering_remote_witness import (
    SCHEMA, RemoteEngineeringWitness, canonical, claim_data,
)


class RemoteAuthorityEngineeringTests(unittest.TestCase):
    KEY = bytes(range(32))
    ID = "d" * 64

    @classmethod
    def setUpClass(cls):
        cls.outside = tempfile.TemporaryDirectory()
        cls.database = Path(cls.outside.name) / "remote_authority.sqlite3"
        with socket.socket() as s:
            s.bind(("127.0.0.1", 0))
            cls.port = s.getsockname()[1]
        cls.start_service()

    @classmethod
    def start_service(cls):
        env = dict(os.environ)
        # Repository uses tests/i3 and src/i3; isolated local runs use i3/.
        root = Path(__file__).resolve().parents[2]
        source = root / "src"
        if not (source / "i3" / "runtime").is_dir():
            source = Path(__file__).resolve().parents[1]
            root = source
        env["PYTHONPATH"] = str(source) + os.pathsep + env.get("PYTHONPATH", "")
        cls.service = subprocess.Popen([
            sys.executable, "-m", "i3.lab.engineering_remote_authority",
            "--database", str(cls.database), "--authority-id", cls.ID,
            "--key-hex", cls.KEY.hex(), "--port", str(cls.port),
        ], cwd=root, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        for _ in range(120):
            if cls.service.poll() is not None:
                raise RuntimeError("test service exited: " + cls.service.stderr.read().decode())
            try:
                with socket.create_connection(("127.0.0.1", cls.port), .2):
                    return
            except OSError:
                time.sleep(.03)
        raise RuntimeError("isolated service failed to start")

    @classmethod
    def stop_service(cls):
        cls.service.terminate()
        try:
            cls.service.wait(timeout=5)
        except subprocess.TimeoutExpired:
            cls.service.kill()
            cls.service.wait(timeout=5)
        cls.service.stderr.close()

    @classmethod
    def tearDownClass(cls):
        cls.stop_service()
        cls.outside.cleanup()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        idx = int(sha256(self._testMethodName.encode()).hexdigest()[:12], 16)
        self.claim = make_reservation(birth_index=idx, life_seed=55,
                                      source_sha256="a"*64,
                                      world_sha256="b"*64,
                                      genome_sha256="c"*64)
        self.client = self.make_client()
        reserve(self.root, self.claim)
        self.view = initialize(self.root, self.claim, horizon=3,
                               initial_body=[95.,85.,75.,65.,55.],
                               witness_mode=REMOTE_MODE)
        self.client.register(self.claim, self.view)

    def make_client(self, key=None, aid=None):
        return RemoteEngineeringWitness("http://127.0.0.1:%d" % self.port,
                 key=self.KEY if key is None else key,
                 authority_id=self.ID if aid is None else aid,
                 timeout=1, allow_test_loopback_http=True)

    def step(self, *, refuse_after_prepare=False, refuse_after_ledger_seal=False):
        old = inspect(self.root, self.claim)
        n = old["sequence"] + 1
        intent = {"schema": INTENT_SCHEMA, "tick_before": n - 1,
                  "body_before": old["last_body"], "action": "attendre", "param": None,
                  "decision_work": {"cycles": 1, "simulated_steps": 2,
                                    "memory_items": 0, "replays": 0}}
        p = prepare(self.root, self.claim, expected_head=old["head_sha256"], intent=intent)
        self.client.prepared(self.root, self.claim, previous_ledger=old, intent=intent)
        if refuse_after_prepare:
            return (old, intent, p)
        body = list(old["last_body"])
        after_motor = [body[0]-1.,body[1]-.2,body[2]-.3,body[3],body[4]-.2]
        after_learn = [after_motor[0]-.03,*after_motor[1:4],after_motor[4]-.06]
        receipt = {"schema": RECEIPT_SCHEMA, "phase": "POST_PAID_LEARNING", "tick": n,
                   "action": "attendre", "param": None,
                   "body_after_motor": after_motor,
                   "body_after_paid_learning": after_learn,
                   "decision_paid": {"energy": .1,"vigilance": .2},
                   "learning_paid": {"energy": .03, "vigilance": .06},
                   "death_causes": [], "world_state_sha256": "e"*64,
                   "mind_state_sha256": "f"*64}
        seal(self.root, self.claim, expected_head=p["prior_head_sha256"],
             seal_token=p["seal_token"], receipt=receipt)
        if refuse_after_ledger_seal:
            return (old, intent, p)
        return self.client.committed(self.root, self.claim,
                                     previous_ledger=old, intent=intent)

    def test_network_service_runs_in_independent_process_and_commits(self):
        self.assertNotEqual(self.service.pid, os.getpid())
        self.step()
        remote = self.client.verify(self.claim, inspect(self.root, self.claim))
        self.assertEqual(remote["sequence"], 1)
        self.assertEqual(remote["phase"], "COMMITTED")
        self.assertEqual(remote["head_sha256"], inspect(self.root,self.claim)["head_sha256"])

    def test_common_rollback_of_both_local_stores_is_caught_remotely(self):
        self.step()
        snapshots = []
        for src in (BIRTH_DB, LEDGER_DB):
            snapshot = self.root / ("old_" + src)
            with closing(sqlite3.connect(self.root/src)) as read:
                with closing(sqlite3.connect(snapshot)) as backup:
                    read.backup(backup)
            snapshots.append((src, snapshot))
        self.step()
        self.assertEqual(self.client.verify(self.claim, inspect(self.root,self.claim))["sequence"], 2)
        for name, old in snapshots:
            os.replace(old, self.root/name)
            for suffix in ("-wal","-shm"):
                extra = self.root/(name+suffix)
                if extra.exists(): extra.unlink()
        self.assertEqual(inspect(self.root,self.claim)["sequence"], 1)
        with self.assertRaisesRegex(PermissionError,"remote authority rejects"):
            self.client.verify(self.claim, inspect(self.root,self.claim))

    def test_prepared_timeout_or_crash_never_permits_replay(self):
        self.step(refuse_after_prepare=True)
        with self.assertRaisesRegex(PermissionError,"uncertain prepared motor"):
            inspect(self.root,self.claim)
        with self.assertRaises(PermissionError):
            self.client.verify(self.claim, self.view)

    def test_after_local_seal_before_remote_commit_stays_blocked(self):
        self.step(refuse_after_ledger_seal=True)
        self.assertEqual(inspect(self.root,self.claim)["sequence"],1)
        with self.assertRaisesRegex(PermissionError,"remote authority rejects"):
            self.client.verify(self.claim, inspect(self.root,self.claim))

    def test_remote_unavailable_prevents_another_motored_step(self):
        # Check service availability is not interpreted as authorization.
        self.stop_service()
        try:
            with self.assertRaisesRegex(PermissionError,"unavailable"):
                self.client.verify(self.claim, inspect(self.root,self.claim))
        finally:
            self.start_service()
        self.assertEqual(self.client.verify(self.claim, self.view)["sequence"], 0)

    def test_server_identity_persists_after_separate_process_restart(self):
        self.step()
        self.stop_service()
        self.start_service()
        self.assertEqual(self.client.verify(self.claim, inspect(self.root,self.claim))["sequence"],1)
        self.step()
        self.assertEqual(self.client.verify(self.claim,inspect(self.root,self.claim))["sequence"],2)

    def test_concurrent_prepare_is_one_shot_even_with_valid_credentials(self):
        old = inspect(self.root,self.claim)
        n = 1
        intent = {"schema":INTENT_SCHEMA,"tick_before":0,"body_before":old["last_body"],
                  "action":"attendre","param":None,"decision_work":{
                      "cycles":1,"simulated_steps":0,"memory_items":0,"replays":0}}
        prepare(self.root,self.claim,expected_head=old["head_sha256"],intent=intent)
        def attempt(_):
            try:
                return self.make_client().prepared(self.root,self.claim,
                                                    previous_ledger=old,intent=intent)
            except PermissionError:
                return None
        with ThreadPoolExecutor(max_workers=2) as pool:
            out=list(pool.map(attempt,[1,2]))
        self.assertEqual(sum(x is not None for x in out),1)
        with self.assertRaises(PermissionError):
            self.client.prepared(self.root,self.claim,previous_ledger=old,intent=intent)

    def test_wrong_key_or_authority_id_is_not_an_accepted_witness(self):
        bad=self.make_client(key=b"z"*32)
        with self.assertRaises(PermissionError):
            bad.verify(self.claim,self.view)
        different=self.make_client(aid="f"*64)
        with self.assertRaises(PermissionError):
            different.verify(self.claim,self.view)

    def test_http_rejected_without_explicit_loopback_opt_in(self):
        with self.assertRaises(ValueError):
            RemoteEngineeringWitness("http://127.0.0.1:3456",key=self.KEY,
                                     authority_id=self.ID)
        with self.assertRaises(ValueError):
            RemoteEngineeringWitness("http://example.com:3456",key=self.KEY,
                                     authority_id=self.ID,
                                     allow_test_loopback_http=True)
        with self.assertRaises(ValueError):
            RemoteEngineeringWitness("https://example.com",key=self.KEY,
                                     authority_id=self.ID)

    def test_terminal_state_cannot_be_prepared_or_re_registered(self):
        self.step();self.step();self.step()
        final = inspect(self.root,self.claim)
        self.assertEqual(final["terminal"],"CENSORED")
        self.client.verify(self.claim,final)
        with self.assertRaises(PermissionError):
            self.client.register(self.claim,final)
        with self.assertRaises(PermissionError):
            self.client._request("prepare",claim={
                "identity_sha256":self.claim.identity_sha256,
                "source_sha256":self.claim.source_sha256,
                "world_sha256":self.claim.world_sha256,
                "genome_sha256":self.claim.genome_sha256,
                "life_seed":self.claim.life_seed,
                "birth_index":self.claim.birth_index},sequence=4,
                previous_head_sha256=final["head_sha256"],intent_sha256="b"*64)


    def test_raw_http_duplicate_or_ambiguous_headers_stop_before_nonce_journal(self):
        """Even a request with a valid first HMAC must have unambiguous framing."""
        body = canonical({
            "schema": SCHEMA, "authority_id": self.ID,
            "operation": "verify", "claim": claim_data(self.claim),
        })
        with closing(sqlite3.connect(self.database)) as conn:
            before = conn.execute("SELECT COUNT(*) FROM request_nonces").fetchone()[0]

        cases = (
            ("duplicate-length", ("Content-Length", str(len(body)))),
            ("duplicate-nonce", ("X-I3-Nonce", None)),
            ("duplicate-signature", ("X-I3-Signature", None)),
            ("duplicate-type", ("Content-Type", "application/json")),
            ("transfer-encoding", ("Transfer-Encoding", "chunked")),
            ("content-encoding", ("Content-Encoding", "gzip")),
            ("expect-continue", ("Expect", "100-continue")),
            ("noncanonical-length", None),
            ("wrong-type", None),
        )
        for name, extra in cases:
            with self.subTest(case=name):
                nonce = secrets.token_hex(16)
                mac = hmac.new(
                    self.KEY, b"Q\n" + nonce.encode() + b"\n" + body,
                    sha256).hexdigest()
                headers = [
                    ("Host", "127.0.0.1"),
                    ("Content-Type", "application/json"),
                    ("Content-Length", str(len(body))),
                    ("X-I3-Nonce", nonce),
                    ("X-I3-Signature", mac),
                ]
                if name == "noncanonical-length":
                    headers[2] = ("Content-Length", "0" + str(len(body)))
                elif name == "wrong-type":
                    headers[1] = ("Content-Type", "text/plain")
                elif name == "duplicate-nonce":
                    headers.append(("X-I3-Nonce", nonce))
                elif name == "duplicate-signature":
                    headers.append(("X-I3-Signature", mac))
                elif extra is not None:
                    headers.append(extra)
                request = (b"POST /v1/command HTTP/1.1\r\n"
                           + b"".join(f"{k}: {v}\r\n".encode("ascii")
                                      for k, v in headers)
                           + b"\r\n" + body)
                with socket.create_connection(("127.0.0.1", self.port),
                                              timeout=2.0) as sock:
                    sock.settimeout(2.0)
                    sock.sendall(request)
                    with sock.makefile("rb") as incoming:
                        status = incoming.readline(512)
                self.assertIn(b" 403 ", status)
                with closing(sqlite3.connect(self.database)) as conn:
                    count = conn.execute(
                        "SELECT COUNT(*) FROM request_nonces").fetchone()[0]
                self.assertEqual(count, before,
                                 "rejected request must not journal its nonce")

    def test_client_rejects_ambiguous_http_response_before_hmac_acceptance(self):
        """No network and no motor: reject ambiguity before interpreting bytes."""
        class FakeResponse:
            status = 200

            def __init__(self, headers):
                self.headers = headers

            def __enter__(self):
                return self

            def __exit__(self, *_):
                return False

            def read(self, size):
                return b"{}"

        class FakeOpener:
            def __init__(self, response):
                self.response = response

            def open(self, *_args, **_kwargs):
                return self.response

        cases = (
            ("duplicate-signature", ("X-I3-Signature", "f"*64)),
            ("duplicate-length", ("Content-Length", "2")),
            ("duplicate-type", ("Content-Type", "application/json")),
            ("transfer-encoding", ("Transfer-Encoding", "chunked")),
            ("content-encoding", ("Content-Encoding", "gzip")),
            ("noncanonical-length", ("Content-Length", "02")),
        )
        for name, extra in cases:
            with self.subTest(case=name):
                headers = Message()
                headers.add_header("X-I3-Signature", "f"*64)
                headers.add_header("Content-Length", "2")
                headers.add_header("Content-Type", "application/json")
                if name == "noncanonical-length":
                    headers.replace_header("Content-Length", "02")
                else:
                    headers.add_header(*extra)
                self.client._opener = FakeOpener(FakeResponse(headers))
                with self.assertRaisesRegex(
                        PermissionError, "ambiguous remote authority response"):
                    self.client._request("verify", claim=claim_data(self.claim))


if __name__=="__main__":
    unittest.main()
