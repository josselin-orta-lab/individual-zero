"""Real process-kill crash matrix for the coordinated Stage11 SQLite path.

Parent NEVER rebuilds a prior generation after a killed child. A fully
committed current generation can be cold-reconstructed with the same factory;
uncommitted intent fences must halt. This uses real physics, not toy states.
"""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

import pytest

from lab.m11_transactional_mortal import M11TransactionalMortal
from lab.sqlite_life_store import SQLiteLifeLedger, RecoveryBlocked
from lab.stage11_reference_fixture import build_stage11_reference_runtime


INDIVIDUAL = "m11:hard-crash:stage11"
POINTS = (
    "after_intent", "before_private_execution",
    "after_private_execution", "before_sql_commit",
    "after_sql_commit", "after_publication",
)
_SCRIPT = r"""
import os
import sys
from lab.m11_transactional_mortal import M11TransactionalMortal
from lab.stage11_reference_fixture import build_stage11_reference_runtime

dbpath, crash_point, terminal = sys.argv[1:]
runtime = build_stage11_reference_runtime(
    autonomous_mortal=True, enable_geography=True,
)
if terminal == "death":
    center = runtime.world.position
    for dx, dy in ((0,0),(1,0),(-1,0),(0,1),(0,-1)):
        cell = {"x": center.x + dx, "y": center.y + dy}
        runtime.world.apply_scenario_event(
            "set_lethal_zone", {"position": cell, "active": True},
        )
with M11TransactionalMortal.birth(
    db_path=dbpath, runtime=runtime,
    individual_id="m11:hard-crash:stage11",
) as life:
    def hard_exit(point):
        if point == crash_point:
            os._exit(76)
    life.run_step(test_fault=hard_exit)
    raise AssertionError("fault not reached")
"""


def factory():
    return build_stage11_reference_runtime(
        autonomous_mortal=True, enable_geography=True)


@pytest.mark.parametrize("point", POINTS)
def test_actual_os_exit_survives_only_atomic_committed_current(point):
    with TemporaryDirectory() as directory:
        path = str(Path(directory) / "one-life.db")
        child = subprocess.run(
            [sys.executable, "-c", _SCRIPT, path, point, "normal"],
            capture_output=True, text=True, timeout=50,
        )
        assert child.returncode == 76, child.stderr
        receipt = SQLiteLifeLedger.audit_read_only(
            path=path, expected_individual_id=INDIVIDUAL)
        if point in {"after_sql_commit", "after_publication"}:
            assert receipt.generation == 1
            assert receipt.pending_intent is False
            assert receipt.may_recover is True
            with M11TransactionalMortal.cold_recover(
                db_path=path, individual_id=INDIVIDUAL,
                runtime_factory=factory,
            ) as life:
                assert life.inspect()["world_step"] == 1
                next_step = life.run_step()
                assert next_step.generation == 2
                assert next_step.world_step == 2
        else:
            assert receipt.generation == 0
            assert receipt.pending_intent is True
            assert receipt.may_recover is False
            with pytest.raises(RecoveryBlocked):
                M11TransactionalMortal.cold_recover(
                    db_path=path, individual_id=INDIVIDUAL,
                    runtime_factory=factory,
                )


def test_fatal_committed_death_never_reopens_as_active_after_hard_exit():
    with TemporaryDirectory() as directory:
        path = str(Path(directory) / "one-life.db")
        child = subprocess.run(
            [sys.executable, "-c", _SCRIPT, path, "after_sql_commit", "death"],
            capture_output=True, text=True, timeout=50,
        )
        assert child.returncode == 76, child.stderr
        receipt = SQLiteLifeLedger.audit_read_only(
            path=path, expected_individual_id=INDIVIDUAL)
        assert receipt.generation == 1
        assert receipt.status == "dead"
        assert not receipt.may_recover
        with pytest.raises(RecoveryBlocked):
            M11TransactionalMortal.cold_recover(
                db_path=path, individual_id=INDIVIDUAL,
                runtime_factory=factory,
            )
