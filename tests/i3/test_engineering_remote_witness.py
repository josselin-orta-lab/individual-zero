"""No-World I3 remote authority transport and common-local-rollback tests."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from hashlib import sha256
from pathlib import Path
import os
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
from i3.runtime.engineering_remote_witness import RemoteEngineeringWitness


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
        root = Path(__file__).resolve().parents[1]
        env["PYTHONPATH"] = str(root) + os.pathsep + env.get("PYTHONPATH", "")
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


if __name__=="__main__":
    unittest.main()
