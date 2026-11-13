"""One-shot I3 native engineering cycle, no M11 or scientific birth claims."""
from dataclasses import replace
from pathlib import Path
import sqlite3
import json
import os
import subprocess
import socket
import time
from contextlib import contextmanager, closing
import sys
import tempfile
import unittest
from unittest.mock import patch

from i3.lab.dev_worlds import dev_long_corridor
from i3.modules.body import BodyLaws
from i3.modules.genome import midpoint
from i3.modules.world import World, WorldSpec
from i3.runtime.engineering_step_ledger import (
    inspect as inspect_steps, DB_NAME as STEP_DB_NAME, REMOTE_MODE,
)
from i3.runtime import engineering_rollback_witness as witness
from i3.runtime.engineering_remote_witness import RemoteEngineeringWitness
from i3.runtime.life import run_life
from i3.runtime.native_engineering_session import (
    NativeEngineeringSession, make_engineering_claim, state_hash,
)


class NativeEngineeringStepTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.genome = midpoint()
        self.seed = 7719
        self.spec = dev_long_corridor()

    def begin(self, *, index=1, spec=None, horizon=3, root=None, witness_dir=None, remote=None):
        spec = spec if spec is not None else self.spec
        root = root if root is not None else self.root
        claim = make_engineering_claim(birth_index=index, genome=self.genome,
                                       spec=spec, life_seed=self.seed)
        return NativeEngineeringSession.begin(
            root, claim, genome=self.genome, spec=spec, horizon=horizon,
            witness_directory=witness_dir, remote_witness=remote)

    def test_real_paid_motor_learning_step_and_complete_local_receipt(self):
        session = self.begin(horizon=3)
        initial_body = tuple(session.world.body)
        witnessed = []
        for tick in range(1, 4):
            event = session.step()
            witnessed.append(event)
            ledger = inspect_steps(self.root, session.claim)
            self.assertEqual(ledger["sequence"], tick)
            self.assertEqual(ledger["last_body"], list(session.world.body))
            self.assertEqual(event["receipt"]["tick"], tick)
            self.assertEqual(event["receipt"]["phase"], "POST_PAID_LEARNING")
            self.assertEqual(event["receipt"]["world_state_sha256"], state_hash(session.world))
            self.assertEqual(event["receipt"]["mind_state_sha256"], state_hash(session.mind))
            self.assertFalse(event["durable_m11"])
            self.assertFalse(event["cold_recovery_available"])
            self.assertFalse(event["scientific_world_authorized"])
            self.assertEqual(ledger["head_sha256"], event["head_sha256"])
            if event["terminal"] != "OPEN":
                break
        self.assertNotEqual(initial_body, session.world.body)
        self.assertTrue(witnessed)
        self.assertEqual(witnessed[-1]["terminal"], "CENSORED")
        with self.assertRaises(PermissionError):
            session.step()

    def test_original_reference_life_matches_native_engineering_motor_receipts(self):
        # Only existing explicitly DEVELOPMENT fixture, no old cohort index.
        control = run_life(self.genome, self.spec, self.seed, 3,
                           protocol="I3_ENGINEERING_PARITY_NO_SCIENCE",
                           keep_trace=True, decision_policy="reference")
        session = self.begin(horizon=3)
        events = [session.step() for _ in range(control["steps_lived"])]
        self.assertEqual(len(events), control["steps_lived"])
        self.assertEqual([x["action"] for x in events],
                         [x["action"] for x in control["trace"]])
        self.assertEqual([x["param"] for x in events],
                         [x["param"] for x in control["trace"]])
        self.assertEqual([x["receipt"]["body_after_paid_learning"] for x in events],
                         [x["body"] for x in control["trace"]])
        self.assertEqual(list(round(v, 6) for v in session.world.body),
                         control["final_body"])
        self.assertEqual(events[-1]["terminal"],
                         "DEAD" if control["terminal"] == "dead" else "CENSORED")

    def test_prepared_interrupted_motor_cannot_replay(self):
        session = self.begin(horizon=2)
        with patch.object(World, "step", side_effect=RuntimeError("injected motor failure")):
            with self.assertRaisesRegex(RuntimeError, "injected motor"):
                session.step()
        with self.assertRaisesRegex(PermissionError, "uncertain prepared motor"):
            inspect_steps(self.root, session.claim)
        with self.assertRaises(PermissionError):
            session.step()
        with self.assertRaises(PermissionError):
            self.begin(horizon=2)  # cannot rebirth same local index

    def test_binding_to_exact_source_world_genome_before_reservation(self):
        claim = make_engineering_claim(birth_index=4, genome=self.genome,
                                       spec=self.spec, life_seed=self.seed)
        changed = replace(self.spec, name="not-the-same-world")
        with self.assertRaises(PermissionError):
            NativeEngineeringSession.begin(
                self.root, claim, genome=self.genome, spec=changed, horizon=2)
        self.assertFalse((self.root / "i3_birth_reservations.sqlite3").exists())
        bad_genome = midpoint()
        bad_genome["genes"]["alpha"] += 0.001
        with self.assertRaises(PermissionError):
            NativeEngineeringSession.begin(
                self.root, claim, genome=bad_genome, spec=self.spec, horizon=2)
        self.assertFalse((self.root / "i3_birth_reservations.sqlite3").exists())
        with self.assertRaises(ValueError):
            NativeEngineeringSession.begin(
                self.root, claim, genome=self.genome, spec=self.spec, horizon=101)

    def test_virgin_unpaid_mind_mutation_rejected_before_prepare_or_motor(self):
        session = self.begin(horizon=3)
        session.mind.values[0][0] += 0.0001
        with patch.object(World, "step", side_effect=AssertionError(
                "virgin motor must not run")) as motor:
            with self.assertRaisesRegex(PermissionError, "unsealed native genesis"):
                session.step()
        motor.assert_not_called()
        ledger = inspect_steps(self.root, session.claim)
        self.assertEqual(ledger["sequence"], 0)
        self.assertEqual(ledger["events"], [])
        self.assertEqual(session.world.t, 0)
        with self.assertRaises(PermissionError):
            session.step()

    def test_virgin_hidden_world_mutation_rejected_before_prepare_or_motor(self):
        session = self.begin(horizon=3)
        # Hidden token-effect laws are never in the first-person capture,
        # and changing them must not bypass the native birth state pin.
        session.world.effects["forged-unobserved-token"] = (3.0, 0.0)
        with patch.object(World, "step", side_effect=AssertionError(
                "virgin motor must not run")) as motor:
            with self.assertRaisesRegex(PermissionError, "unsealed native genesis"):
                session.step()
        motor.assert_not_called()
        ledger = inspect_steps(self.root, session.claim)
        self.assertEqual(ledger["sequence"], 0)
        self.assertEqual(ledger["events"], [])
        self.assertEqual(session.world.t, 0)

    def test_reconstructed_virgin_state_also_denies_unpaid_mutation(self):
        session = self.begin(horizon=3)
        reconstructed = NativeEngineeringSession.reconstruct(
            self.root, session.claim, genome=self.genome, spec=self.spec)
        reconstructed.mind.values[0][0] += 0.0001
        with patch.object(World, "step", side_effect=AssertionError(
                "virgin motor must not run")) as motor:
            with self.assertRaisesRegex(PermissionError, "unsealed native genesis"):
                reconstructed.step()
        motor.assert_not_called()
        self.assertEqual(inspect_steps(self.root, session.claim)["sequence"], 0)

    def test_mutated_in_process_mind_state_fails_before_second_motor(self):
        session = self.begin(horizon=3)
        session.step()
        before_t = session.world.t
        session.mind.values[0][0] += 0.0001
        with self.assertRaisesRegex(PermissionError, "in-memory native state"):
            session.step()
        self.assertEqual(session.world.t, before_t)
        self.assertEqual(inspect_steps(self.root, session.claim)["sequence"], before_t)

    def test_real_physical_death_is_irreversible(self):
        terminal_spec = WorldSpec(
            name="engineering-inevitable-water-death", width=1, height=1,
            spawn=(0, 0), body=(75.0, 60.0, 0.1, 80.0, 80.0),
            laws=BodyLaws(water_decay=4.0))
        session = self.begin(spec=terminal_spec, horizon=3)
        out = session.step()
        self.assertEqual(out["terminal"], "DEAD")
        self.assertIn("zero_water", out["receipt"]["death_causes"])
        self.assertEqual(out["receipt"]["learning_paid"],
                         {"energy": 0.0, "vigilance": 0.0})
        with self.assertRaises(PermissionError):
            session.step()

    def test_deterministic_reconstruction_matches_uninterrupted_world(self):
        first = self.begin(horizon=4)
        old_receipts = [first.step()["receipt"] for _ in range(2)]
        claim = first.claim
        del first
        recovered = NativeEngineeringSession.reconstruct(
            self.root, claim, genome=self.genome, spec=self.spec)
        self.assertEqual(recovered.world.t, 2)
        self.assertEqual(recovered.head, inspect_steps(self.root, claim)["head_sha256"])
        with tempfile.TemporaryDirectory() as other:
            independent = self.begin(index=2, horizon=4, root=Path(other))
            for expected in old_receipts:
                self.assertEqual(independent.step()["receipt"], expected)
            expected_next = independent.step()
        actual_next = recovered.step()
        self.assertEqual(actual_next["receipt"], expected_next["receipt"])
        self.assertEqual(actual_next["pos"], expected_next["pos"])
        self.assertEqual(actual_next["terminal"], expected_next["terminal"])

    def test_new_python_process_reconstructs_then_commits_one_more_step(self):
        original = self.begin(horizon=4)
        original.step()
        script = '''\
from pathlib import Path
import sqlite3
import json
from i3.lab.dev_worlds import dev_long_corridor
from i3.modules.genome import midpoint
from i3.runtime.native_engineering_session import NativeEngineeringSession,make_engineering_claim
root = Path(%r)
spec,genome = dev_long_corridor(),midpoint()
claim = make_engineering_claim(birth_index=1,genome=genome,spec=spec,life_seed=7719)
reconstructed = NativeEngineeringSession.reconstruct(root,claim,genome=genome,spec=spec)
assert reconstructed.world.t == 1
print(json.dumps(reconstructed.step(),sort_keys=True))
''' % str(self.root)
        repo = Path(__file__).resolve().parents[2]
        env = dict(os.environ)
        env["PYTHONPATH"] = str(repo / "src") + os.pathsep + env.get("PYTHONPATH", "")
        done = subprocess.run([sys.executable, "-c", script], cwd=repo,
                              env=env, text=True, capture_output=True, timeout=40)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        recovered_result = json.loads(done.stdout.strip())
        self.assertEqual(recovered_result["sequence"], 2)
        self.assertEqual(inspect_steps(self.root, original.claim)["sequence"], 2)
        with self.assertRaises(PermissionError):
            original.step()  # stale owner cannot commit another motor

    def test_uncertain_or_terminal_history_is_never_reconstructed(self):
        session = self.begin(horizon=2)
        with patch.object(World, "step", side_effect=RuntimeError("crash after prepare")):
            with self.assertRaises(RuntimeError):
                session.step()
        with self.assertRaisesRegex(PermissionError, "uncertain prepared motor"):
            NativeEngineeringSession.reconstruct(
                self.root, session.claim, genome=self.genome, spec=self.spec)
        with tempfile.TemporaryDirectory() as other:
            old = self.begin(index=9, horizon=1, root=Path(other))
            self.assertEqual(old.step()["terminal"], "CENSORED")
            with self.assertRaisesRegex(PermissionError, "terminal"):
                NativeEngineeringSession.reconstruct(
                    Path(other), old.claim, genome=self.genome, spec=self.spec)

    def test_separate_witness_survives_new_process_and_binds_native_steps(self):
        with tempfile.TemporaryDirectory() as anchor_dir:
            local_witness = Path(anchor_dir)
            session = self.begin(horizon=4, witness_dir=local_witness)
            session.step()
            first = witness.verify(local_witness, self.root, session.claim)
            self.assertEqual(first["sequence"], 1)
            self.assertFalse(first["off_host_monotonic"])
            with self.assertRaisesRegex(PermissionError, "cannot be bypassed"):
                NativeEngineeringSession.reconstruct(
                    self.root, session.claim, genome=self.genome, spec=self.spec)
            script = '''from pathlib import Path
import json
from i3.lab.dev_worlds import dev_long_corridor
from i3.modules.genome import midpoint
from i3.runtime.native_engineering_session import NativeEngineeringSession,make_engineering_claim
root,external = Path(%r),Path(%r)
spec,genome = dev_long_corridor(),midpoint()
claim = make_engineering_claim(birth_index=1,genome=genome,spec=spec,life_seed=7719)
reconstructed = NativeEngineeringSession.reconstruct(root,claim,genome=genome,spec=spec,
                                                       witness_directory=external)
print(json.dumps(reconstructed.step(),sort_keys=True))
''' % (str(self.root), str(local_witness))
            repo = Path(__file__).resolve().parents[2]
            env = dict(os.environ)
            env["PYTHONPATH"] = str(repo / "src") + os.pathsep + env.get("PYTHONPATH", "")
            done = subprocess.run([sys.executable, "-c", script], cwd=repo,
                                  env=env, text=True, capture_output=True, timeout=40)
            self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
            self.assertEqual(json.loads(done.stdout)["sequence"], 2)
            self.assertEqual(witness.verify(local_witness, self.root, session.claim)["sequence"], 2)
            with self.assertRaises(PermissionError):
                session.step()  # stale original process cannot apply motor

    def test_old_complete_ledger_rejected_against_newer_separate_witness(self):
        with tempfile.TemporaryDirectory() as anchor_dir:
            session = self.begin(horizon=4, witness_dir=Path(anchor_dir))
            session.step()
            backup = self.root / "old.sqlite3"
            with sqlite3.connect(self.root / STEP_DB_NAME) as src:
                with sqlite3.connect(backup) as dst:
                    src.backup(dst)
            session.step()
            self.assertEqual(witness.verify(anchor_dir, self.root, session.claim)["sequence"], 2)
            os.replace(backup, self.root / STEP_DB_NAME)
            for ending in ("-wal", "-shm"):
                candidate = self.root / (STEP_DB_NAME + ending)
                if candidate.exists():
                    candidate.unlink()
            # The old ledger is internally consistent, but it is NOT latest.
            self.assertEqual(inspect_steps(self.root, session.claim)["sequence"], 1)
            with self.assertRaisesRegex(PermissionError, "witness rejects"):
                NativeEngineeringSession.reconstruct(
                    self.root, session.claim, genome=self.genome, spec=self.spec,
                    witness_directory=anchor_dir)

    def test_crash_before_witness_prepare_cannot_execute_native_motor(self):
        with tempfile.TemporaryDirectory() as anchor_dir:
            session = self.begin(horizon=3, witness_dir=Path(anchor_dir))
            with patch.object(witness, "prepared", side_effect=RuntimeError("witness unavailable")):
                with patch.object(World, "step", side_effect=AssertionError("motor executed")):
                    with self.assertRaisesRegex(RuntimeError, "witness unavailable"):
                        session.step()
            with self.assertRaisesRegex(PermissionError, "uncertain prepared motor"):
                NativeEngineeringSession.reconstruct(
                    self.root, session.claim, genome=self.genome, spec=self.spec,
                    witness_directory=anchor_dir)

    def test_after_seal_before_witness_commit_fails_closed(self):
        with tempfile.TemporaryDirectory() as anchor_dir:
            session = self.begin(horizon=3, witness_dir=Path(anchor_dir))
            with patch.object(witness, "committed", side_effect=RuntimeError("seal witness crash")):
                with self.assertRaisesRegex(RuntimeError, "seal witness crash"):
                    session.step()
            self.assertEqual(inspect_steps(self.root, session.claim)["sequence"], 1)
            with self.assertRaisesRegex(PermissionError, "witness rejects"):
                NativeEngineeringSession.reconstruct(
                    self.root, session.claim, genome=self.genome, spec=self.spec,
                    witness_directory=anchor_dir)

    @contextmanager
    def remote_authority(self):
        # Separate real server process and durable database, loopback test only.
        with tempfile.TemporaryDirectory() as outside:
            key = bytes(range(32))
            authority_id = "d" * 64
            with socket.socket() as sock:
                sock.bind(("127.0.0.1", 0))
                port = sock.getsockname()[1]
            repo = Path(__file__).resolve().parents[2]
            env = dict(os.environ)
            env["PYTHONPATH"] = str(repo / "src") + os.pathsep + env.get("PYTHONPATH", "")
            service = subprocess.Popen([
                sys.executable, "-m", "i3.lab.engineering_remote_authority",
                "--database", str(Path(outside)/"remote.sqlite3"),
                "--authority-id", authority_id, "--key-hex", key.hex(),
                "--port", str(port)], cwd=repo, env=env,
                stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            try:
                for _ in range(120):
                    if service.poll() is not None:
                        self.fail("remote authority quit: " + service.stderr.read().decode())
                    try:
                        with socket.create_connection(("127.0.0.1", port), .2):
                            break
                    except OSError:
                        time.sleep(.03)
                else:
                    self.fail("remote authority did not start")
                client = RemoteEngineeringWitness(
                    "http://127.0.0.1:%d" % port,
                    key=key, authority_id=authority_id,
                    allow_test_loopback_http=True, timeout=1)
                yield client, port, key, authority_id
            finally:
                service.terminate()
                service.wait(timeout=5)
                service.stderr.close()

    def test_remote_cas_native_paid_motor_and_second_process_restart(self):
        with self.remote_authority() as (remote, port, key, aid):
            session = self.begin(horizon=4, remote=remote)
            first = session.step()
            self.assertEqual(first["witness_mode"], REMOTE_MODE)
            self.assertTrue(first["remote_witness_transport"])
            self.assertFalse(first["independent_m11_antirollback"])
            script = '''from pathlib import Path
import json
from i3.lab.dev_worlds import dev_long_corridor
from i3.modules.genome import midpoint
from i3.runtime.native_engineering_session import NativeEngineeringSession,make_engineering_claim
from i3.runtime.engineering_remote_witness import RemoteEngineeringWitness
root=Path(%r)
client=RemoteEngineeringWitness("http://127.0.0.1:%d",key=bytes.fromhex(%r),
    authority_id=%r,allow_test_loopback_http=True)
spec,genome=dev_long_corridor(),midpoint()
claim=make_engineering_claim(birth_index=1,genome=genome,spec=spec,life_seed=7719)
session=NativeEngineeringSession.reconstruct(root,claim,genome=genome,spec=spec,
                                             remote_witness=client)
print(json.dumps(session.step(),sort_keys=True))
''' % (str(self.root), port, key.hex(), aid)
            repo = Path(__file__).resolve().parents[2]
            env = dict(os.environ)
            env["PYTHONPATH"] = str(repo / "src") + os.pathsep + env.get("PYTHONPATH", "")
            done = subprocess.run([sys.executable,"-c",script],cwd=repo,env=env,
                                  text=True,capture_output=True,timeout=40)
            self.assertEqual(done.returncode,0,done.stdout+done.stderr)
            self.assertEqual(json.loads(done.stdout)["sequence"],2)
            self.assertEqual(remote.verify(session.claim,inspect_steps(self.root,session.claim))["sequence"],2)
            with self.assertRaises(PermissionError):
                session.step() # stale process cannot act, even with credentials

    def test_common_local_birth_and_ledger_rollback_blocked_by_remote(self):
        with self.remote_authority() as (remote,*_):
            session = self.begin(horizon=4,remote=remote)
            session.step()
            snapshots=[]
            for name in ("i3_birth_reservations.sqlite3", STEP_DB_NAME):
                saved = self.root/("backup_"+name)
                with closing(sqlite3.connect(self.root/name)) as src:
                    with closing(sqlite3.connect(saved)) as dst:
                        src.backup(dst)
                snapshots.append((name,saved))
            session.step()
            for name,saved in snapshots:
                os.replace(saved,self.root/name)
                for suffix in ("-wal","-shm"):
                    extra=self.root/(name+suffix)
                    if extra.exists(): extra.unlink()
            old = inspect_steps(self.root,session.claim)
            self.assertEqual(old["sequence"],1)
            with self.assertRaisesRegex(PermissionError,"remote authority rejects"):
                NativeEngineeringSession.reconstruct(self.root,session.claim,
                    genome=self.genome,spec=self.spec,remote_witness=remote)
            with self.assertRaises(PermissionError):
                session.step()

    def test_remote_prepare_failure_never_executes_native_motor(self):
        with self.remote_authority() as (remote,*_):
            session = self.begin(horizon=3,remote=remote)
            with patch.object(remote,"prepared",side_effect=PermissionError("lost authority")):
                with patch.object(World,"step",side_effect=AssertionError("motor executed")):
                    with self.assertRaisesRegex(PermissionError,"lost authority"):
                        session.step()
            with self.assertRaisesRegex(PermissionError,"uncertain prepared motor"):
                NativeEngineeringSession.reconstruct(self.root,session.claim,
                    genome=self.genome,spec=self.spec,remote_witness=remote)

    def test_after_local_commit_remote_unacknowledged_stays_blocked(self):
        with self.remote_authority() as (remote,*_):
            session = self.begin(horizon=3,remote=remote)
            with patch.object(remote,"committed",side_effect=PermissionError("ack lost")):
                with self.assertRaisesRegex(PermissionError,"ack lost"):
                    session.step()
            self.assertEqual(inspect_steps(self.root,session.claim)["sequence"],1)
            with self.assertRaisesRegex(PermissionError,"remote authority rejects"):
                NativeEngineeringSession.reconstruct(self.root,session.claim,
                    genome=self.genome,spec=self.spec,remote_witness=remote)

    def test_remote_mode_is_bound_and_cannot_degrade_to_local_or_none(self):
        with self.remote_authority() as (remote,*_):
            session = self.begin(horizon=4,remote=remote)
            session.step()
            with self.assertRaisesRegex(PermissionError,"cannot be bypassed"):
                NativeEngineeringSession.reconstruct(self.root,session.claim,
                    genome=self.genome,spec=self.spec)
            with tempfile.TemporaryDirectory() as d:
                with self.assertRaisesRegex(PermissionError,"cannot be bypassed"):
                    NativeEngineeringSession.reconstruct(self.root,session.claim,
                        genome=self.genome,spec=self.spec,witness_directory=Path(d))
            with self.assertRaises(ValueError):
                NativeEngineeringSession.begin(self.root,session.claim,
                    genome=self.genome,spec=self.spec,horizon=4,
                    witness_directory=Path(self.root.parent),remote_witness=remote)

    def test_no_cross_generation_or_m11_compatibility_entrypoint(self):
        import inspect
        from i3.runtime import native_engineering_session
        source = inspect.getsource(native_engineering_session)
        for forbidden in ("i1lab", "from i2", "import i1", "pickle", "active_generation"):
            self.assertNotIn(forbidden, source)
        self.assertFalse(hasattr(NativeEngineeringSession, "resume"))
        self.assertFalse(hasattr(NativeEngineeringSession, "recover"))


if __name__ == "__main__":
    unittest.main()
