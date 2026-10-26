"""#557: canonical born I1 prices the old-episode lane separately.

This is a negative live-path test. A qualifying natural old recall (>32)
is not forced into the world; its existence remains unproven.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class NaturalOldEpisodeCost557(unittest.TestCase):
    def test_canonical_born_actor_has_no_free_old_source_read(self):
        with TemporaryDirectory() as folder:
            built = Path(folder) / "generated"
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                 "--output", str(built)],
                cwd=ROOT, capture_output=True, text=True, timeout=90,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            program = r"""
from pathlib import Path
from tempfile import TemporaryDirectory
from run_i1_world_preset import load_preset, _birth_parameters
from i1lab.i1_birth import birth_i1_m11, recover_i1_m11
from i1lab.i1_natural_runtime import (
    I1Runtime, _OLD_RECALL_OPERATION, _OLD_RECALL_COST_UC,
    _SLEEP_RECALL_OPERATION,
)
from i1lab.sqlite_life_store import SQLiteLifeLedger

preset,_=load_preset("empty-land")
params,_=_birth_parameters(preset)
identity="i1:557:negative-natural-old-recall"
assert _OLD_RECALL_COST_UC == 8
assert _OLD_RECALL_OPERATION != _SLEEP_RECALL_OPERATION

def factory():
    return I1Runtime(birth_life_id=identity,autonomous_mortal=True,
        m11_sqlite_custody=True,wal_path=None,
        diagnostic_sample_cost_uc=1,module_occupancy_cost_uc=1,
        **params)

def old_events(runtime):
    return [e.causal_event for e in runtime.journal.entries
            if e.causal_event.get("kind")=="i1_old_episode_paid_observation"]

with TemporaryDirectory() as folder:
    path=str(Path(folder)/"life.sqlite")
    with birth_i1_m11(db_path=path,life_id=identity,**params) as life:
        actor=life._runtime
        birth_head=actor.journal.head_hash
        cost=actor.compute_budget._config.operation_costs
        assert cost[_OLD_RECALL_OPERATION] == 8
        assert cost[_SLEEP_RECALL_OPERATION] == 1
        assert actor.memory.episode_count < 32
        result=life.run_step()
        assert result.status in ("active","dead")
        # M11 publishes a newly copied runtime only after the SQL commit.
        # The previous actor must remain untouched, not be used as evidence.
        committed=life._runtime
        assert committed is not actor
        assert actor.journal.head_hash==birth_head
        assert not old_events(committed)
        before=committed.journal.head_hash
        assert result.journal_head==before and before!=birth_head
        assert committed.journal.verify()
    audit=SQLiteLifeLedger.audit_read_only(
        path=path,expected_individual_id=identity)
    assert audit.journal_head==before
    assert audit.may_recover == (result.status=="active"), (
        audit.status, audit.pending_intent, audit.may_recover, result.status,
    )
    if result.status=="active":
        with recover_i1_m11(
            db_path=path,life_id=identity,runtime_factory=factory
        ) as restored:
            assert restored._runtime.journal.head_hash==before
            assert not old_events(restored._runtime)
print("I1_557_NEGATIVE_NATURAL_UC_M11_OK")
"""
            env = os.environ.copy()
            env["PYTHONPATH"] = os.pathsep.join(
                (str(built), str(ROOT / "src"), str(ROOT / "tools"))
            )
            run = subprocess.run(
                [sys.executable, "-c", program], cwd=ROOT,
                env=env, capture_output=True, text=True, timeout=120,
            )
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            self.assertIn("I1_557_NEGATIVE_NATURAL_UC_M11_OK", run.stdout)


if __name__ == "__main__":
    unittest.main()
