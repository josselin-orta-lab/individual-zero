"""One-shot I3 native engineering cycle, no M11 or scientific birth claims."""
from dataclasses import replace
from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from i3.lab.dev_worlds import dev_long_corridor
from i3.modules.body import BodyLaws
from i3.modules.genome import midpoint
from i3.modules.world import World, WorldSpec
from i3.runtime.engineering_step_ledger import inspect as inspect_steps
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

    def begin(self, *, index=1, spec=None, horizon=3, root=None):
        spec = spec if spec is not None else self.spec
        root = root if root is not None else self.root
        claim = make_engineering_claim(birth_index=index, genome=self.genome,
                                       spec=spec, life_seed=self.seed)
        return NativeEngineeringSession.begin(
            root, claim, genome=self.genome, spec=spec, horizon=horizon)

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
