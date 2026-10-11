"""Prospective, public Stage-11 software checks for Scheduler occurrence custody.

Opt-in tests only; the negative direct-owner legacy diagnostic remains in
test_stage11_cycle_occurrence_custody.py and must not be misreported as fixed
for the default behavior. No scientific held-out or historical Golden claim.
"""
from copy import deepcopy
from dataclasses import replace
from unittest import TestCase

from lab.compute_budget import ComputeBudgetConfig, CycleComputeBudget
from lab.determinism import canonical_causal_bytes, sha256_hex
from lab.journal import HashChainedJournal
from lab.snapshots import SnapshotManager, SnapshotType
from lab.stage1_runtime import ScriptedStage1Runtime
from lab.stage11_routed_junction_probe import build_public_route_runtime


def guarded_config() -> ComputeBudgetConfig:
    return ComputeBudgetConfig(
        version="stage11-cycle-occurrence-custody-guard-dev-v1",
        cycle_ceiling=8,
        module_envelopes={"worker": 8, "control": 2},
        protected_modules=frozenset({"control"}),
        protected_capacity=2,
        operation_costs={"small": 2, "one": 1, "zero": 0},
        cycle_occurrence_guard=True,
    )


class Stage11CycleOccurrenceGuardTests(TestCase):
    def test_guarded_owner_requires_valid_context_and_denies_duplicate(self):
        owner = CycleComputeBudget(config=guarded_config())
        before = owner.export_causal_state()
        self.assertIsNone(before["active_occurrence"])
        bad = (
            None, (), (1,), (1, "first"), (1, "first", 2),
            (True, "first", 1), (0, "first", 1),
            (1, "", 1), (1, 5, 1), (1, "first", True),
            [1, "first", 1], (1, "first", 1.0),
        )
        for occurrence in bad:
            with self.subTest(occurrence=repr(occurrence)):
                with self.assertRaises(ValueError):
                    owner.open_cycle(1, occurrence=occurrence)
                self.assertEqual(owner.export_causal_state(), before)

        owner.open_cycle(1, occurrence=(1, "first-attempt", 1))
        receipt = owner.charge(module="worker", operation="small")
        self.assertTrue(receipt.accepted)
        self.assertEqual(receipt.requested_uc, 2)
        charged = deepcopy(owner.export_causal_state())
        charged_bytes = canonical_causal_bytes(charged)
        with self.assertRaisesRegex(RuntimeError, "already opened"):
            owner.open_cycle(1, occurrence=(1, "first-attempt", 1))
        self.assertEqual(owner.export_causal_state(), charged)
        self.assertEqual(canonical_causal_bytes(owner.export_causal_state()), charged_bytes)
        self.assertEqual(owner.consumed_cycle_uc, 2)

        # Different cognitive cycle, same world step/attempt: renewed UC.
        owner.open_cycle(2, occurrence=(1, "first-attempt", 2))
        self.assertTrue(owner.charge(module="worker", operation="small").accepted)
        self.assertEqual(owner.consumed_cycle_uc, 2)

        # Next *physical* step legitimately starts again at numeric cycle 1.
        owner.open_cycle(1, occurrence=(2, "next-world-step", 1))
        self.assertEqual(owner.consumed_cycle_uc, 0)
        self.assertTrue(owner.charge(module="worker", operation="small").accepted)
        # Same physical step/cycle, but new rollback attempt is distinct.
        owner.open_cycle(1, occurrence=(2, "rollback-attempt-1", 1))
        self.assertEqual(owner.consumed_cycle_uc, 0)

    def test_guarded_restore_rejects_invalid_occurrence_without_partial_write(self):
        owner = CycleComputeBudget(config=guarded_config())
        owner.open_cycle(1, occurrence=(3, "accepted-attempt", 1))
        self.assertTrue(owner.charge(module="worker", operation="small").accepted)
        before = deepcopy(owner.export_causal_state())
        original_bytes = canonical_causal_bytes(before)

        invalid = []
        def malformed(label, occurrence):
            candidate = deepcopy(before)
            candidate["active_occurrence"] = occurrence
            invalid.append((label, candidate))

        malformed("missing", None)
        malformed("bad_type", [3, "accepted-attempt", 1])
        malformed("unexpected_key", {
            "t_monde": 3, "attempt_ref": "accepted-attempt", "cycle": 1,
            "extra": True,
        })
        malformed("boolean_world_step", {
            "t_monde": True, "attempt_ref": "accepted-attempt", "cycle": 1,
        })
        malformed("wrong_cycle", {
            "t_monde": 3, "attempt_ref": "accepted-attempt", "cycle": 2,
        })
        malformed("empty_attempt", {
            "t_monde": 3, "attempt_ref": "", "cycle": 1,
        })
        missing_key = deepcopy(before)
        del missing_key["active_occurrence"]
        invalid.append(("missing_schema", missing_key))
        for name, candidate in invalid:
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    owner.restore_causal_state(candidate)
                self.assertEqual(owner.export_causal_state(), before)
                self.assertEqual(
                    canonical_causal_bytes(owner.export_causal_state()), original_bytes,
                )

        # Legacy snapshot schema cannot silently restore into a guarded owner.
        unguarded_config = replace(
            guarded_config(), version="legacy-separate-v1",
            cycle_occurrence_guard=False,
        )
        legacy = CycleComputeBudget(config=unguarded_config)
        legacy.open_cycle(1)
        with self.assertRaises(ValueError):
            owner.restore_causal_state(legacy.export_causal_state())
        self.assertEqual(owner.export_causal_state(), before)

        # Restore a valid owner state, then deny re-opening that same identity.
        owner.open_cycle(1, occurrence=(4, "later", 1))
        owner.restore_causal_state(deepcopy(before))
        self.assertEqual(owner.export_causal_state(), before)
        with self.assertRaisesRegex(RuntimeError, "already opened"):
            owner.open_cycle(1, occurrence=(3, "accepted-attempt", 1))
        self.assertEqual(owner.export_causal_state(), before)

    def test_guarded_snapshot_manager_exactly_restores_occurrence(self):
        def run_once():
            owner = CycleComputeBudget(config=guarded_config())
            journal = HashChainedJournal()
            manager = SnapshotManager(journal=journal)
            owner.open_cycle(1, occurrence=(2, "attempt-2", 1))
            self.assertTrue(owner.charge(
                module="worker", operation="small",
            ).accepted)
            frozen = deepcopy(owner.export_causal_state())
            record = manager.take(
                snapshot_type=SnapshotType.PERIODIC,
                individual_id="i0-uc-occurrence-public-v1",
                t_monde=2, cycle=0, attempt_ref=None,
                owners=(owner,),
                versions={"budget": guarded_config().version},
            )
            self.assertTrue(manager.verify(record.id))
            owner.open_cycle(1, occurrence=(3, "attempt-3", 1))
            self.assertTrue(owner.charge(
                module="control", operation="one",
            ).accepted)
            manager.restore(record.id, owners=(owner,))
            self.assertEqual(owner.export_causal_state(), frozen)
            with self.assertRaises(RuntimeError):
                owner.open_cycle(1, occurrence=(2, "attempt-2", 1))
            self.assertEqual(owner.export_causal_state(), frozen)
            self.assertTrue(manager.verify(record.id))
            self.assertTrue(journal.verify())
            self.assertEqual(
                [e.causal_event["kind"] for e in journal.entries],
                ["snapshot_taken", "snapshot_restored"],
            )
            return (
                record.id, record.sha256,
                canonical_causal_bytes(owner.export_causal_state()),
                journal.canonical_bytes(), journal.head_hash,
            )
        self.assertEqual(run_once(), run_once())

    def test_guarded_stage1_reuses_cycle_one_across_physical_steps_and_replay(self):
        def run_once():
            runtime = ScriptedStage1Runtime(
                campaign_seed=213, budget_config=guarded_config(),
            )
            runtime.run_step(cycle=1)
            first = runtime.compute_budget.export_causal_state()
            self.assertEqual(
                (first["active_occurrence"]["t_monde"],
                 first["active_occurrence"]["cycle"]), (1, 1),
            )
            snapshot = runtime.take_snapshot(
                snapshot_type=SnapshotType.PERIODIC,
            )
            self.assertTrue(runtime.snapshots.verify(snapshot.id))
            initial = runtime.causal_fingerprint()
            runtime.run_step(cycle=1)
            second = runtime.compute_budget.export_causal_state()
            self.assertEqual(
                (second["active_occurrence"]["t_monde"],
                 second["active_occurrence"]["cycle"]), (2, 1),
            )
            self.assertNotEqual(
                first["active_occurrence"]["attempt_ref"],
                second["active_occurrence"]["attempt_ref"],
            )
            expected = runtime.causal_fingerprint()
            runtime.restore(snapshot.id)
            self.assertEqual(runtime.causal_fingerprint(), initial)
            runtime.run_step(cycle=1)
            self.assertEqual(runtime.causal_fingerprint(), expected)
            self.assertTrue(runtime.journal.verify())
            return (
                snapshot.id, snapshot.sha256,
                runtime.journal.canonical_bytes(), runtime.journal.head_hash,
            )
        self.assertEqual(run_once(), run_once())

    def test_stage11_public_opt_in_is_versioned_and_independently_replayable(self):
        def run_once(guard):
            runtime = build_public_route_runtime(
                layout_variant="junction_open", planning_uc=4,
                exploration_uc=4, survey_refresh=True,
                cycle_occurrence_guard=guard,
            )
            self.assertEqual(
                runtime._config.compute_budget.cycle_occurrence_guard, guard,
            )
            manager = runtime.stage3.substrate.snapshots
            actions, captures = [], []
            for step in range(1, 6):
                output = runtime.run_step()
                actions.append((
                    output.execution_status, output.command_primitive,
                    output.option_ref, output.source,
                ))
                if step in (4, 5):
                    record = manager.take(
                        snapshot_type=SnapshotType.PERIODIC,
                        individual_id=runtime.individual_id,
                        t_monde=step, cycle=0, attempt_ref=None,
                        owners=runtime.causal_owners,
                        versions={"stage11": runtime._stage11_config.version},
                    )
                    self.assertTrue(manager.verify(record.id))
                    captures.append((record.id, record.sha256))
                state = runtime.compute_budget.export_causal_state()
                if guard:
                    self.assertIsNotNone(state["active_occurrence"])
                    self.assertEqual(state["active_occurrence"]["t_monde"], step)
                    self.assertEqual(
                        state["active_occurrence"]["cycle"], runtime.compute_budget.cycle,
                    )
                else:
                    self.assertNotIn("active_occurrence", state)
            self.assertTrue(runtime.journal.verify())
            return (
                runtime._stage11_config.version,
                runtime._config.compute_budget.version,
                tuple(actions), tuple(captures),
                sha256_hex(runtime.journal.canonical_bytes()),
                sha256_hex(canonical_causal_bytes({
                    owner.owner_id: owner.export_causal_state()
                    for owner in runtime.causal_owners
                })),
            )

        unguarded = run_once(False)
        guarded = run_once(True)
        self.assertEqual(run_once(False), unguarded)
        self.assertEqual(run_once(True), guarded)
        self.assertNotEqual(unguarded[:2], guarded[:2])
        self.assertEqual(unguarded[2], guarded[2])
        self.assertNotEqual(unguarded[4], guarded[4])
        for invalid_flag in (None, 1, 0, "true"):
            with self.subTest(flag=invalid_flag), self.assertRaises(ValueError):
                build_public_route_runtime(
                    cycle_occurrence_guard=invalid_flag,
                )
        for invalid_flag in (None, 1, "yes"):
            with self.subTest(config_flag=invalid_flag), self.assertRaises(ValueError):
                replace(
                    guarded_config(), cycle_occurrence_guard=invalid_flag,
                ).validate()
