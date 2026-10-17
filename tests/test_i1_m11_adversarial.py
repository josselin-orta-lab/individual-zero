"""Adversarial M11 tests of the CURRENT autonomous I1, without old cohorts.

These checks test actual durable-intent/COMMIT boundaries, full current-state
authentication and irreversible death. Tampering occurs only in deliberately
invalid test fixtures; it never supplies experience or knowledge to a life.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_i1_fork import generate


class NaturalI1M11AdversarialTests(unittest.TestCase):
    def test_current_commit_faults_terminal_identity_and_owner_custody(self):
        with TemporaryDirectory(prefix="i1-m11-adversarial-") as home:
            output = Path(home) / "generated"
            generate(output)
            code = r"""
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
import sqlite3

from i1lab.i1_birth import birth_i1_m11, recover_i1_m11
from i1lab.i1_natural_runtime import I1Runtime
from i1lab.m11_transactional_mortal import _runtime_image
from i1lab.sqlite_life_store import SQLiteLifeLedger, RecoveryBlocked
from i1lab.stage11_reference_fixture import build_stage11_reference_runtime
from i1lab.stage10_reference_fixture import build_stage10_reference_runtime
from i1lab.world import BodyState
from i1.modules.stage12_detectors import Stage12DetectionPolicy

base = build_stage11_reference_runtime(autonomous_mortal=True)
sleep = build_stage10_reference_runtime(autonomous_mortal=True)
stage10 = replace(sleep._stage10_config, stage9=base._stage11_config.stage9)
detector = Stage12DetectionPolicy(
    version="i1-m11-native-adversarial-v1", window=12,
    stagnation_steps=3, stagnation_tolerance=0.05,
    loop_repetitions=2, loop_max_period=2,
    entropy_min_samples=3, entropy_warning_fraction=0.25,
    bias_min_outcomes_each=2, attribution_bias_threshold=0.75)
params = dict(
    world_config=base.world.config, layout=base.world._layout,
    safety_config=base.stage3.substrate.safety._config,
    safety_facts=base._canonical_safety._innate,
    protected_integrity_threshold=(
        base.stage3.control._config.protected_integrity_threshold),
    stage11_config=base._stage11_config, stage10_config=stage10,
    equipment=base.equipment, detector_policy=detector,
    diagnostic_sample_cost_uc=1, module_occupancy_cost_uc=1)

def factory(life_id, *, world_config=None):
    args = dict(params)
    if world_config is not None:
        args["world_config"] = world_config
    return I1Runtime(
        birth_life_id=life_id, autonomous_mortal=True,
        m11_sqlite_custody=True, wal_path=None, **args)

def birth(path, life_id, *, world_config=None):
    args = dict(params)
    if world_config is not None:
        args["world_config"] = world_config
    return birth_i1_m11(db_path=path, life_id=life_id, **args)

class Injected(RuntimeError):
    pass

with TemporaryDirectory(prefix="i1-current-m11-faults-") as folder:
    root = Path(folder)
    life_id = "i1:m11:native:faults"
    with birth(str(root / "continuous.sqlite"), life_id) as normal:
        first = normal.run_step()
        second = normal.run_step()
        assert first.status == second.status == "active"
        assert first.generation == 1 and second.generation == 2
        assert first.world_step == 1 and second.world_step == 2

    for checkpoint in ("before_sql_commit", "after_sql_commit",
                       "after_publication"):
        db_path = str(root / (checkpoint + ".sqlite"))
        with birth(db_path, life_id) as interrupted:
            def inject(stage):
                if stage == checkpoint:
                    raise Injected("simulated M11 interruption at " + stage)
            try:
                interrupted.run_step(test_fault=inject)
            except Injected:
                pass
            else:
                raise AssertionError("M11 did not inject " + checkpoint)
            try:
                interrupted.run_step()
            except RecoveryBlocked:
                pass
            else:
                raise AssertionError("poisoned coordinator continued " + checkpoint)

        receipt = SQLiteLifeLedger.audit_read_only(
            path=db_path, expected_individual_id=life_id)
        if checkpoint == "before_sql_commit":
            assert receipt.generation == 0, receipt
            assert receipt.pending_intent and not receipt.may_recover, receipt
            try:
                with recover_i1_m11(
                    db_path=db_path, life_id=life_id,
                    runtime_factory=lambda: factory(life_id)):
                    pass
            except RecoveryBlocked:
                pass
            else:
                raise AssertionError("unresolved intent resumed previous generation")
        else:
            # COMMIT is durable. Recover the EXACT latest active generation;
            # never replay the previous command or restore an older snapshot.
            assert receipt.generation == 1, receipt
            assert receipt.may_recover and not receipt.pending_intent, receipt
            assert receipt.journal_head == first.journal_head, receipt
            with recover_i1_m11(
                db_path=db_path, life_id=life_id,
                runtime_factory=lambda: factory(life_id),
            ) as resumed:
                published = resumed.inspect()
                assert published["generation"] == 1
                assert published["world_step"] == 1
                next_step = resumed.run_step()
                assert next_step.generation == 2
                assert next_step.world_step == 2
                assert next_step.journal_head == second.journal_head
                assert next_step.status == "active"

    # A fully canonical SQLite image still requires independent, frozen
    # owner custody; rewriting the roster hash without the image is rejected.
    base_path = str(root / "continuous.sqlite")
    with sqlite3.connect(base_path) as db:
        db.execute(
            "UPDATE life_current SET registered_roster_hash=? WHERE slot=1",
            ("0" * 64,),
        )
    try:
        SQLiteLifeLedger.audit_read_only(
            path=base_path, expected_individual_id=life_id)
    except RecoveryBlocked:
        pass
    else:
        raise AssertionError("tampered SQLite owner roster was accepted")

    # A syntactically valid extra lived form that is NOT in slow history must
    # be rejected, including before the first real consolidation publication.
    actor = factory(life_id)
    form = {
        "episode_ref": "unauthorized-episode",
        "event_ref": "unauthorized-world-event",
        "event_kind": "world_transition_experienced",
        "projection_digest": "a" * 64,
        "verification_status": "observed_not_verified",
        "lived_observation": {
            "position": [0, 0],
            "body": {"energy": 25.0, "food": 25.0,
                     "water": 25.0, "integrity": 25.0},
        },
    }
    actor._i1_active_owner_views["perception"]._active_observations = [form]
    try:
        _runtime_image(actor, individual_id=life_id)
    except RecoveryBlocked:
        pass
    else:
        raise AssertionError("unpublished active perception evidence was accepted")

    # The physical body dies once. SQLite marks the identity terminal, then
    # refuses both additional live steps and a cold-start resurrection.
    deceased = "i1:m11:native:terminal"
    depleted = replace(
        params["world_config"],
        initial_body=BodyState(
            energy=40.0, food=0.0, water=0.0, integrity=0.25),
    )
    dead_db = str(root / "terminal.sqlite")
    with birth(dead_db, deceased, world_config=depleted) as dying:
        last = dying.run_step()
        assert last.status == "dead", last
        try:
            dying.run_step()
        except RecoveryBlocked:
            pass
        else:
            raise AssertionError("terminal individual resumed physically")
    terminal = SQLiteLifeLedger.audit_read_only(
        path=dead_db, expected_individual_id=deceased)
    assert terminal.status == "dead" and not terminal.may_recover, terminal
    try:
        with recover_i1_m11(
            db_path=dead_db, life_id=deceased,
            runtime_factory=lambda: factory(deceased, world_config=depleted)):
            pass
    except RecoveryBlocked:
        pass
    else:
        raise AssertionError("dead I1 was resurrected from SQLite")

print("I1_NATIVE_M11_ADVERSARIAL_OK")
"""
            proc = subprocess.run(
                [sys.executable, "-c", code],
                env={"PYTHONPATH": str(output) + ":" + str(ROOT / "src")},
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("I1_NATIVE_M11_ADVERSARIAL_OK", proc.stdout)


if __name__ == "__main__":
    unittest.main()
