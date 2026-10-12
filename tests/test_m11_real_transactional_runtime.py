"""Integration-level private staging of real autonomous mortal Stage 11.

These tests deliberately use the full reference cognitive runtime, not a
fake SQLite state, a guessed journal suffix, or an Oracle/Bench mock.
"""
from __future__ import annotations

import os
import json
import subprocess
import sys
from tempfile import TemporaryDirectory
from pathlib import Path

import pytest

from lab.sqlite_life_store import RecoveryBlocked, SQLiteLifeLedger
from lab.sqlite_runtime_custody import capture_registered_current_state
from lab.stage11_reference_fixture import build_stage11_reference_runtime
from lab.m11_transactional_mortal import M11TransactionalMortal

IDENTITY = "m11:real-world:development-instance"


def fresh():
    return build_stage11_reference_runtime(
        autonomous_mortal=True, enable_geography=True,
    )


def test_runtime_contract_is_stable_across_equivalent_constructor_mappings():
    """Cold-start identity is semantic, never dict iteration or object repr."""
    from dataclasses import replace
    from lab.m11_transactional_mortal import _runtime_contract

    original, rebuilt = fresh(), fresh()
    assert _runtime_contract(original) == _runtime_contract(rebuilt)
    modulation = rebuilt._stage11_config.modulation
    reordered = {
        key: dict(reversed(list(values.items())))
        for key, values in reversed(list(modulation.multipliers.items()))
    }
    rebuilt._stage11_config = replace(
        rebuilt._stage11_config,
        modulation=replace(modulation, multipliers=reordered),
    )
    assert _runtime_contract(original) == _runtime_contract(rebuilt)

    rebuilt._stage11_config = replace(
        rebuilt._stage11_config,
        intrinsic_weight=rebuilt._stage11_config.intrinsic_weight + 0.25,
    )
    assert _runtime_contract(original) != _runtime_contract(rebuilt)


def test_live_stage11_is_prepared_then_atomically_published():
    initial = fresh()
    original = capture_registered_current_state(initial, individual_id=IDENTITY)
    with TemporaryDirectory() as temp:
        path = str(Path(temp) / "life.sqlite")
        with M11TransactionalMortal.birth(
            db_path=path, runtime=initial, individual_id=IDENTITY,
        ) as life:
            assert life.inspect()["generation"] == 0
            # The supplied object is quarantined at birth: only the private
            # committed coordinator can dispatch another physical command.
            with pytest.raises(RuntimeError):
                initial.run_step()
            first = life.run_step()
            assert first.generation == 1
            assert first.status == "active"
            assert first.world_step == 1
            assert life.inspect()["journal_count"] > 0
            assert first.journal_head == life.inspect()["journal_head"]
            second = life.run_step()
            assert second.generation == 2
            assert second.world_step == 2
            assert second.journal_count > first.journal_count
            assert life._runtime.stage3.substrate.bench is None
            assert life._runtime.stage3.substrate.evaluation_trace is None
        # The externally retained runtime is halted, without any physical
        # transition or cognition after transfer to the sole SQLite owner.
        assert initial.stage3.substrate.mortal_status.value == "technical_halt"
        assert initial.world.export_causal_state() == original["world"]
        assert initial.journal.head_hash == original["journal"]["head"]
        with SQLiteLifeLedger.open_existing(
            path=path, expected_individual_id=IDENTITY,
        ) as stored:
            receipt = stored.audit()
            assert receipt.generation == 2
            assert receipt.journal_count == second.journal_count
            assert receipt.journal_head == second.journal_head
            assert receipt.pending_intent is False
            assert stored.export_canonical_journal()


def test_after_intent_failure_never_recovers_previous_active_generation():
    with TemporaryDirectory() as temp:
        path = str(Path(temp) / "life.sqlite")
        with M11TransactionalMortal.birth(
            db_path=path, runtime=fresh(), individual_id=IDENTITY,
        ) as life:
            def fault(point):
                if point == "after_intent":
                    raise RuntimeError("injected intent boundary failure")
            with pytest.raises(RuntimeError, match="injected intent"):
                life.run_step(test_fault=fault)
            with pytest.raises(RecoveryBlocked):
                life.run_step()
        with SQLiteLifeLedger.open_existing(
            path=path, expected_individual_id=IDENTITY,
        ) as stored:
            assert stored.audit().pending_intent is True
            with pytest.raises(RecoveryBlocked):
                stored.recover_current_bytes(expected_individual_id=IDENTITY)
            sealed = stored.seal_uncertain()
            assert sealed.status == "technical_halt"
            assert not sealed.may_recover


def test_after_committed_generation_fault_never_retries_in_process():
    with TemporaryDirectory() as temp:
        path = str(Path(temp) / "life.sqlite")
        with M11TransactionalMortal.birth(
            db_path=path, runtime=fresh(), individual_id=IDENTITY,
        ) as life:
            def fault(point):
                if point == "after_sql_commit":
                    raise RuntimeError("post-commit publication interruption")
            with pytest.raises(RuntimeError, match="post-commit"):
                life.run_step(test_fault=fault)
            with pytest.raises(RecoveryBlocked):
                life.run_step()
        with SQLiteLifeLedger.open_existing(
            path=path, expected_individual_id=IDENTITY,
        ) as stored:
            assert stored.audit().pending_intent is False
            assert stored.audit().generation == 1
            assert stored.audit().may_recover is True
            # Runtime cold-restoration is a separate gate; do not select
            # an older generation or dispatch a command without it.


def test_cold_recovery_of_current_stage11_generation_does_not_replay_physics():
    with TemporaryDirectory() as temp:
        path = str(Path(temp) / "life.sqlite")
        with M11TransactionalMortal.birth(
            db_path=path, runtime=fresh(), individual_id=IDENTITY,
        ) as life:
            first = life.run_step()
            assert first.generation == 1
            before = life.inspect()
        with M11TransactionalMortal.cold_recover(
            db_path=path, individual_id=IDENTITY, runtime_factory=fresh,
        ) as life:
            after = life.inspect()
            assert after["generation"] == before["generation"]
            assert after["journal_head"] == before["journal_head"]
            assert after["world_step"] == before["world_step"]
            continued = life.run_step()
            assert continued.world_step == before["world_step"] + 1
            assert continued.generation == before["generation"] + 1
            assert continued.journal_count > before["journal_count"]
        # A new process never reselects generation 0 or duplicates step 1.
        with SQLiteLifeLedger.open_existing(
            path=path, expected_individual_id=IDENTITY,
        ) as ledger:
            assert ledger.audit().generation == 2


def test_cold_recovery_refuses_unresolved_intent_even_with_factory():
    with TemporaryDirectory() as temp:
        path = str(Path(temp) / "life.sqlite")
        with M11TransactionalMortal.birth(
            db_path=path, runtime=fresh(), individual_id=IDENTITY,
        ) as life:
            def fault(point):
                if point == "after_intent":
                    raise RuntimeError("interrupted")
            with pytest.raises(RuntimeError, match="interrupted"):
                life.run_step(test_fault=fault)
        with pytest.raises(RecoveryBlocked):
            M11TransactionalMortal.cold_recover(
                db_path=path, individual_id=IDENTITY, runtime_factory=fresh,
            )


def test_cold_recovery_uses_current_generation_after_prepublication_crash():
    with TemporaryDirectory() as temp:
        path = str(Path(temp) / "life.sqlite")
        with M11TransactionalMortal.birth(
            db_path=path, runtime=fresh(), individual_id=IDENTITY,
        ) as life:
            def fault(point):
                if point == "after_sql_commit":
                    raise RuntimeError("published only in SQLite")
            with pytest.raises(RuntimeError):
                life.run_step(test_fault=fault)
        with M11TransactionalMortal.cold_recover(
            db_path=path, individual_id=IDENTITY, runtime_factory=fresh,
        ) as life:
            assert life.inspect()["generation"] == 1
            assert life.inspect()["world_step"] == 1
            next_step = life.run_step()
            assert next_step.world_step == 2
            assert next_step.generation == 2


def test_cold_start_and_uninterrupted_stage11_agree_across_real_steps():
    """No physical command replay: compare distinct deterministic lives only."""
    with TemporaryDirectory() as tmp:
        steady_path = str(Path(tmp) / "steady.db")
        restored_path = str(Path(tmp) / "restored.db")
        with M11TransactionalMortal.birth(
            db_path=steady_path, runtime=fresh(), individual_id=IDENTITY,
        ) as uninterrupted:
            stable = [uninterrupted.run_step() for _ in range(5)]
        with M11TransactionalMortal.birth(
            db_path=restored_path, runtime=fresh(), individual_id=IDENTITY,
        ) as initial:
            one = initial.run_step()
        partial = [one]
        for _ in range(4):
            with M11TransactionalMortal.cold_recover(
                db_path=restored_path, individual_id=IDENTITY,
                runtime_factory=fresh,
            ) as recovered:
                partial.append(recovered.run_step())
        if [(r.world_step, r.journal_head, r.journal_count)
                for r in stable] != [(r.world_step, r.journal_head, r.journal_count)
                for r in partial]:
            with SQLiteLifeLedger.open_existing(
                path=steady_path, expected_individual_id=IDENTITY,
            ) as a, SQLiteLifeLedger.open_existing(
                path=restored_path, expected_individual_id=IDENTITY,
            ) as b:
                aa = a.export_canonical_journal().split(bytes([10]))
                bb = b.export_canonical_journal().split(bytes([10]))
                divergence = next(
                    (i for i, (x, y) in enumerate(zip(aa, bb)) if x != y),
                    min(len(aa), len(bb)),
                )
                left = json.loads(aa[divergence]) if divergence < len(aa) else None
                right = json.loads(bb[divergence]) if divergence < len(bb) else None
                raise AssertionError(("first cold divergence", divergence,
                                      left, right))
        assert [(r.world_step, r.journal_head, r.journal_count)
                for r in stable] == [
                    (r.world_step, r.journal_head, r.journal_count)
                    for r in partial]
        with SQLiteLifeLedger.open_existing(
            path=steady_path, expected_individual_id=IDENTITY,
        ) as a, SQLiteLifeLedger.open_existing(
            path=restored_path, expected_individual_id=IDENTITY,
        ) as b:
            assert a.export_canonical_journal() == b.export_canonical_journal()
            assert a.recover_current_bytes(
                expected_individual_id=IDENTITY
            ) == b.recover_current_bytes(
                expected_individual_id=IDENTITY
            )


def test_stage10_cognition_and_sleep_owners_share_sqlite_generation():
    from lab.stage10_reference_fixture import build_stage10_reference_runtime
    builder = lambda: build_stage10_reference_runtime(
        autonomous_mortal=True, start_fatigued=True,
    )
    with TemporaryDirectory() as temp:
        path = str(Path(temp) / "sleeping-life.db")
        with M11TransactionalMortal.birth(
            db_path=path, runtime=builder(), individual_id=IDENTITY,
        ) as first:
            step = first.run_step()
            assert step.world_step == 1
            assert step.generation == 1
        with M11TransactionalMortal.cold_recover(
            db_path=path, individual_id=IDENTITY,
            runtime_factory=builder,
        ) as resumed:
            second = resumed.run_step()
            assert second.generation == 2
            assert second.world_step == 2
            assert resumed.inspect()["journal_head"] == second.journal_head
        with SQLiteLifeLedger.open_existing(
            path=path, expected_individual_id=IDENTITY,
        ) as ledger:
            assert ledger.audit().registered_roster_hash is not None
            assert ledger.audit().generation == 2


def test_uncoordinated_runtime_type_fails_closed_before_birth():
    from lab.stage4_reference_fixture import build_stage4_reference_runtime
    with TemporaryDirectory() as tmp:
        path = str(Path(tmp) / "uncoordinated.sqlite")
        with pytest.raises(RecoveryBlocked, match="uncoordinated|unsupported"):
            M11TransactionalMortal.birth(
                db_path=path,
                runtime=build_stage4_reference_runtime(autonomous_mortal=True),
                individual_id=IDENTITY,
            )
        assert not Path(path).exists()
