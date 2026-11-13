"""Engineering-only R2.4 pinned CAS boundary and remote-store rollback faults.

A volatile Python pin is a TEST DOUBLE, NOT an independent trusted M11 anchor.
Every World instantiated here is a local, unregistered engineering-only World.
"""
from contextlib import closing
from pathlib import Path
from unittest.mock import patch
import os
import socket
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest

from i3.lab.dev_worlds import dev_long_corridor
from i3.modules.genome import midpoint
from i3.modules.world import World
from i3.runtime.birth_reservation import DB_NAME as BIRTH_DB
from i3.runtime.engineering_step_ledger import (
    DB_NAME as LEDGER_DB, inspect as inspect_steps,
)
from i3.runtime.engineering_remote_witness import RemoteEngineeringWitness
from i3.runtime.native_engineering_session import (
    NativeEngineeringSession, make_engineering_claim,
)


class VolatileTestOnlyPin:
    """In-memory same-process high-water oracle, never a durable authority."""

    def __init__(self):
        self.records = {}

    @staticmethod
    def _state(out):
        if (out["phase"] != "COMMITTED" or
                out["pending_sequence"] is not None or
                out["pending_intent_sha256"] is not None):
            raise PermissionError("test anchor refuses incomplete remote state")
        return (out["sequence"], out["head_sha256"], out["terminal"])

    @staticmethod
    def _key(out):
        return (out["authority_id"], out["identity_sha256"])

    def publish(self, out):
        key = self._key(out)
        value = self._state(out)
        prior = self.records.get(key)
        if prior is None:
            if value[0] != 0 or value[2] != "OPEN":
                raise PermissionError("test pin requires exact first genesis")
        else:
            if (prior[2] != "OPEN" or
                    (value[0] != prior[0] and value[0] != prior[0]+1) or
                    (value[0] == prior[0] and value != prior)):
                raise PermissionError("test pin cannot reset or fork a committed head")
        self.records[key] = value

    def assert_current(self, out):
        key = self._key(out)
        if self.records.get(key) != self._state(out):
            raise PermissionError("external committed high-water mismatch")


class PinnedRemoteCASFaultTests(unittest.TestCase):
    KEY = bytes(range(32))
    AUTHORITY_ID = "d" * 64

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "local"
        self.root.mkdir()
        self.remote_root = Path(self.tmp.name) / "authority"
        self.remote_root.mkdir()
        self.remote_db = self.remote_root / "authority.sqlite3"
        self.genome = midpoint()
        self.spec = dev_long_corridor()
        self.claim = make_engineering_claim(
            birth_index=31, genome=self.genome, spec=self.spec, life_seed=7719)
        self.pin = VolatileTestOnlyPin()
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            self.port = sock.getsockname()[1]
        self.service = None
        self.start()
        self.client = RemoteEngineeringWitness(
            "http://127.0.0.1:%d" % self.port,
            key=self.KEY, authority_id=self.AUTHORITY_ID,
            allow_test_loopback_http=True, timeout=1, commit_anchor=self.pin)

    def tearDown(self):
        self.stop()

    def start(self):
        repo = Path(__file__).resolve().parents[2]
        env = dict(os.environ)
        env["PYTHONPATH"] = str(repo / "src") + os.pathsep + env.get("PYTHONPATH", "")
        self.service = subprocess.Popen([
            sys.executable, "-m", "i3.lab.engineering_remote_authority",
            "--database", str(self.remote_db),
            "--authority-id", self.AUTHORITY_ID,
            "--key-hex", self.KEY.hex(), "--port", str(self.port),
        ], cwd=repo, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        for _ in range(120):
            if self.service.poll() is not None:
                raise RuntimeError("test-only service quit: " +
                                   self.service.stderr.read().decode())
            try:
                with socket.create_connection(("127.0.0.1", self.port), .2):
                    return
            except OSError:
                time.sleep(.03)
        raise RuntimeError("test-only authority failed to start")

    def stop(self):
        if self.service is not None:
            if self.service.poll() is None:
                self.service.terminate()
                self.service.wait(timeout=5)
            self.service.stderr.close()
            self.service = None

    def begin(self):
        return NativeEngineeringSession.begin(
            self.root, self.claim, genome=self.genome, spec=self.spec,
            horizon=4, remote_witness=self.client)

    @staticmethod
    def snapshot(src, dst):
        with closing(sqlite3.connect(src)) as original:
            with closing(sqlite3.connect(dst)) as target:
                original.backup(target)

    @staticmethod
    def restore(src, snapshot):
        os.replace(snapshot, src)
        for ext in ("-wal", "-shm"):
            extra = Path(str(src) + ext)
            if extra.exists():
                extra.unlink()

    def test_normal_native_two_steps_pin_and_same_identity_cold_rebuild(self):
        session = self.begin()
        self.assertEqual(self.pin.records[
            (self.AUTHORITY_ID, self.claim.identity_sha256)][0], 0)
        steps = [session.step(), session.step()]
        self.assertEqual([row["sequence"] for row in steps], [1, 2])
        self.assertTrue(all(row["receipt"]["phase"] == "POST_PAID_LEARNING"
                            for row in steps))
        self.assertTrue(all(row["independent_m11_antirollback"] is False
                            for row in steps))
        pin = self.pin.records[(self.AUTHORITY_ID, self.claim.identity_sha256)]
        self.assertEqual(pin[0], 2)
        self.assertEqual(pin[1], steps[-1]["head_sha256"])
        rebuilt = NativeEngineeringSession.reconstruct(
            self.root, self.claim, genome=self.genome, spec=self.spec,
            remote_witness=self.client)
        self.assertEqual(rebuilt.world.t, 2)
        self.assertEqual(self.client.verify(
            self.claim, inspect_steps(self.root, self.claim))["sequence"], 2)
        self.assertEqual(rebuilt.step()["sequence"], 3)

    def test_both_local_stores_and_remote_db_rollback_denied_by_retained_test_pin(self):
        session = self.begin()
        session.step()
        older = {}
        for src in (self.root / BIRTH_DB, self.root / LEDGER_DB, self.remote_db):
            backup = src.with_name("old_" + src.name)
            self.snapshot(src, backup)
            older[src] = backup
        session.step()
        self.assertEqual(self.pin.records[
            (self.AUTHORITY_ID, self.claim.identity_sha256)][0], 2)
        self.stop()
        for src, backup in older.items():
            self.restore(src, backup)
        self.start()
        self.assertEqual(inspect_steps(self.root, self.claim)["sequence"], 1)
        # The remote server's new process ALSO thinks the old source is valid.
        # Only the separately retained test pin prevents replay here.
        with patch.object(World, "step",
                          side_effect=AssertionError("must not replay motor")):
            with self.assertRaisesRegex(PermissionError,
                                        "external committed high-water mismatch"):
                NativeEngineeringSession.reconstruct(
                    self.root, self.claim, genome=self.genome, spec=self.spec,
                    remote_witness=self.client)
        # Never interpret this in-memory control as off-host anti-rollback.
        self.assertEqual(self.pin.records[
            (self.AUTHORITY_ID, self.claim.identity_sha256)][0], 2)

    def test_complete_rollback_including_volatile_pin_is_not_independent_m11(self):
        # An attacker controlling every state-bearing object can restore a
        # coherent older version of the *pin*, too. This EXPECTED ACCEPTANCE
        # is the explicit release-blocking negative control, not a security
        # PASS and not an authorized scientific World.
        session = self.begin()
        session.step()
        pinned_before = dict(self.pin.records)
        older = {}
        for src in (self.root / BIRTH_DB, self.root / LEDGER_DB, self.remote_db):
            backup = src.with_name("old_" + src.name)
            self.snapshot(src, backup)
            older[src] = backup
        original_second = session.step()
        self.assertEqual(original_second["sequence"], 2)
        self.stop()
        for src, backup in older.items():
            self.restore(src, backup)
        self.pin.records = pinned_before  # deliberate compromised test pin
        self.start()
        old_ledger = inspect_steps(self.root, self.claim)
        self.assertEqual(old_ledger["sequence"], 1)
        self.assertEqual(self.client.verify(self.claim, old_ledger)["sequence"], 1)
        resumed = NativeEngineeringSession.reconstruct(
            self.root, self.claim, genome=self.genome, spec=self.spec,
            remote_witness=self.client)
        self.assertEqual(resumed.world.t, 1)
        # A second *synthetic test* motor is accepted under a full coordinated
        # rollback. A real external motor cannot be repeated safely this way.
        replayed = resumed.step()
        self.assertEqual(replayed["sequence"], 2)
        self.assertFalse(replayed["independent_m11_antirollback"])

    def test_after_remote_commit_before_anchor_publish_failure_is_stop(self):
        session = self.begin()
        original_publish = self.pin.publish
        def fail_after_accepted_remote_commit(out):
            if out["sequence"] > 0:
                raise PermissionError("independent test pin unavailable")
            original_publish(out)
        original_world_step = World.step
        executed = []
        def counted_step(world, *args, **kwargs):
            executed.append(True)
            return original_world_step(world, *args, **kwargs)
        with patch.object(self.pin, "publish", side_effect=fail_after_accepted_remote_commit):
            with patch.object(World, "step", counted_step):
                with self.assertRaisesRegex(
                        PermissionError, "independent test pin unavailable"):
                    session.step()
        self.assertEqual(len(executed), 1)
        self.assertEqual(inspect_steps(self.root, self.claim)["sequence"], 1)
        with patch.object(World, "step",
                          side_effect=AssertionError("uncertain motor replayed")):
            with self.assertRaisesRegex(PermissionError,
                                        "external committed high-water mismatch"):
                NativeEngineeringSession.reconstruct(
                    self.root, self.claim, genome=self.genome, spec=self.spec,
                    remote_witness=self.client)
        with self.assertRaisesRegex(PermissionError, "failed or terminal"):
            session.step()

    def test_pin_unavailable_pre_motor_stops_before_physical_world_step(self):
        session = self.begin()
        with patch.object(self.pin, "assert_current",
                          side_effect=PermissionError("no independent test pin")):
            with patch.object(World, "step",
                              side_effect=AssertionError("unexpected World motor")):
                with self.assertRaisesRegex(PermissionError, "no independent test pin"):
                    session.step()
        self.assertEqual(inspect_steps(self.root, self.claim)["sequence"], 0)
        with self.assertRaisesRegex(PermissionError, "failed or terminal"):
            session.step()

    def test_pin_shape_and_unpinned_mode_never_claim_release(self):
        with self.assertRaisesRegex(ValueError, "assert_current and publish"):
            RemoteEngineeringWitness(
                "http://127.0.0.1:%d" % self.port,
                key=self.KEY, authority_id=self.AUTHORITY_ID,
                allow_test_loopback_http=True, commit_anchor=object())
        client = RemoteEngineeringWitness(
            "http://127.0.0.1:%d" % self.port,
            key=self.KEY, authority_id=self.AUTHORITY_ID,
            allow_test_loopback_http=True)
        self.assertIsNone(client._commit_anchor)
        self.assertFalse(hasattr(client, "independent_m11_antirollback"))


if __name__ == "__main__":
    unittest.main()
