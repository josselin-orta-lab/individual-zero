from __future__ import annotations

import unittest
from copy import deepcopy

from lab.compute_budget import ComputeBudgetConfig, CycleComputeBudget
from lab.determinism import canonical_causal_bytes
from lab.journal import HashChainedJournal
from lab.snapshots import SnapshotManager, SnapshotType


class ComputeBudgetTests(unittest.TestCase):
    def config(self) -> ComputeBudgetConfig:
        return ComputeBudgetConfig(
            version="fixture-v1",
            cycle_ceiling=10,
            module_envelopes={
                "worker": 6,
                "control": 4,
            },
            protected_modules=frozenset({"control"}),
            protected_capacity=3,
            operation_costs={
                "small": 2,
                "large": 5,
            },
        )

    def test_cycle_budget_renews_without_carryover(self) -> None:
        budget = CycleComputeBudget(config=self.config())
        budget.open_cycle(1)
        self.assertTrue(budget.charge(module="worker", operation="small").accepted)
        self.assertEqual(budget.consumed_cycle_uc, 2)

        budget.open_cycle(2)

        self.assertEqual(budget.consumed_cycle_uc, 0)
        self.assertEqual(budget.consumed_module_uc("worker"), 0)

    def test_module_envelope_is_never_borrowed(self) -> None:
        budget = CycleComputeBudget(config=self.config())
        budget.open_cycle(1)
        self.assertTrue(budget.charge(module="worker", operation="large").accepted)

        rejected = budget.charge(module="worker", operation="small")

        self.assertFalse(rejected.accepted)
        self.assertEqual(rejected.reason, "module_envelope")
        self.assertEqual(budget.consumed_cycle_uc, 5)
        self.assertEqual(budget.consumed_module_uc("worker"), 5)

    def test_protected_capacity_is_preserved_for_control(self) -> None:
        budget = CycleComputeBudget(config=self.config())
        budget.open_cycle(1)
        self.assertTrue(budget.charge(module="worker", operation="large").accepted)

        rejected = budget.charge(module="worker", operation="small")

        self.assertFalse(rejected.accepted)
        self.assertEqual(rejected.reason, "module_envelope")

        accepted_control = budget.charge(module="control", operation="small")
        self.assertTrue(accepted_control.accepted)
        self.assertEqual(budget.consumed_cycle_uc, 7)

    def test_ordinary_work_cannot_consume_protected_capacity(self) -> None:
        config = ComputeBudgetConfig(
            version="fixture-protected-v1",
            cycle_ceiling=10,
            module_envelopes={"worker": 10, "control": 4},
            protected_modules=frozenset({"control"}),
            protected_capacity=3,
            operation_costs={"large": 5, "small": 2},
        )
        budget = CycleComputeBudget(config=config)
        budget.open_cycle(1)

        self.assertTrue(budget.charge(module="worker", operation="large").accepted)
        self.assertTrue(budget.charge(module="worker", operation="small").accepted)
        rejected = budget.charge(module="worker", operation="small")

        self.assertFalse(rejected.accepted)
        self.assertEqual(rejected.reason, "protected_capacity")
        self.assertEqual(budget.consumed_cycle_uc, 7)

        control = budget.charge(module="control", operation="small")
        self.assertTrue(control.accepted)
        self.assertEqual(budget.consumed_cycle_uc, 9)

    def test_global_ceiling_is_never_exceeded(self) -> None:
        config = ComputeBudgetConfig(
            version="fixture-v2",
            cycle_ceiling=6,
            module_envelopes={"control": 10},
            protected_modules=frozenset({"control"}),
            protected_capacity=2,
            operation_costs={"large": 5, "small": 2},
        )
        budget = CycleComputeBudget(config=config)
        budget.open_cycle(1)
        self.assertTrue(budget.charge(module="control", operation="large").accepted)

        rejected = budget.charge(module="control", operation="small")

        self.assertFalse(rejected.accepted)
        self.assertEqual(rejected.reason, "cycle_ceiling")
        self.assertEqual(budget.consumed_cycle_uc, 5)

    def test_refused_work_does_not_consume_uc(self) -> None:
        budget = CycleComputeBudget(config=self.config())
        budget.open_cycle(1)

        first = budget.charge(module="worker", operation="large")
        second = budget.charge(module="worker", operation="large")

        self.assertTrue(first.accepted)
        self.assertFalse(second.accepted)
        self.assertEqual(budget.consumed_cycle_uc, 5)

    def test_scheduler_capacity_quote_is_pure_and_matches_real_charges(self):
        budget = CycleComputeBudget(config=self.config())
        control = CycleComputeBudget(config=self.config())
        for owner in (budget, control):
            owner.open_cycle(2)
            self.assertTrue(
                owner.charge(module="worker", operation="small").accepted,
            )
        before = budget.export_causal_state()
        first = budget.quote_operations(
            module="worker", operations=("small", "small"),
        )
        self.assertEqual((first.required_uc, first.available_uc), (4, 4))
        self.assertTrue(first.affordable)
        second = budget.quote_operations(
            module="worker", operations=("small", "large"),
        )
        self.assertEqual(second.required_uc, 7)
        self.assertFalse(second.affordable)
        self.assertEqual(budget.export_causal_state(), before)
        for owner in (budget, control):
            self.assertTrue(
                owner.charge(module="worker", operation="small").accepted,
            )
            self.assertTrue(
                owner.charge(module="worker", operation="small").accepted,
            )
        self.assertEqual(
            budget.export_causal_state(), control.export_causal_state(),
        )
        self.assertEqual(
            budget.quote_operations(
                module="worker", operations=("small",),
            ).available_uc, 0,
        )

    def test_scheduler_capacity_quote_preserves_protected_reservation(self):
        config = ComputeBudgetConfig(
            version="quote-protected-v1", cycle_ceiling=10,
            module_envelopes={"worker": 10, "control": 4},
            protected_modules=frozenset({"control"}),
            protected_capacity=3,
            operation_costs={"large": 5, "small": 2},
        )
        budget = CycleComputeBudget(config=config)
        budget.open_cycle(1)
        self.assertTrue(
            budget.charge(module="worker", operation="large").accepted,
        )
        before = budget.export_causal_state()
        denied = budget.quote_operations(
            module="worker", operations=("small", "small"),
        )
        self.assertEqual(denied.available_uc, 2)
        self.assertEqual(denied.required_uc, 4)
        self.assertFalse(denied.affordable)
        allowed = budget.quote_operations(
            module="control", operations=("small", "small"),
        )
        self.assertEqual(allowed.available_uc, 4)
        self.assertTrue(allowed.affordable)
        self.assertEqual(before, budget.export_causal_state())
        self.assertEqual(
            budget.charge(module="worker", operation="small").accepted,
            True,
        )
        self.assertFalse(
            budget.charge(module="worker", operation="small").accepted,
        )
        self.assertTrue(
            budget.charge(module="control", operation="small").accepted,
        )

    def test_scheduler_capacity_quote_rejects_invalid_or_unopened_inputs(self):
        budget = CycleComputeBudget(config=self.config())
        with self.assertRaises(RuntimeError):
            budget.quote_operations(
                module="worker", operations=("small",),
            )
        budget.open_cycle(1)
        original = budget.export_causal_state()
        for module, operations in (
            ("missing", ("small",)),
            ("worker", ()),
            ("worker", ("missing",)),
            ("worker", ("small", 1)),
            ("worker", ["small"]),
            ("worker", "small"),
            (True, ("small",)),
        ):
            with self.subTest(module=module, operations=operations):
                with self.assertRaises(ValueError):
                    budget.quote_operations(
                        module=module, operations=operations,
                    )
                self.assertEqual(
                    budget.export_causal_state(), original,
                )

    @staticmethod
    def protected_snapshot_config() -> ComputeBudgetConfig:
        return ComputeBudgetConfig(
            version="stage11-scheduler-restore-unit-v1",
            cycle_ceiling=10,
            module_envelopes={"worker": 10, "control": 4},
            protected_modules=frozenset({"control"}),
            protected_capacity=3,
            operation_costs={
                "small": 2, "large": 5, "one": 1, "zero": 0,
            },
        )

    def test_invalid_snapshot_uc_ledgers_reject_without_mutating_owner(self):
        config = self.protected_snapshot_config()
        budget = CycleComputeBudget(config=config)
        budget.open_cycle(7)
        self.assertTrue(budget.charge(
            module="worker", operation="large",
        ).accepted)
        self.assertTrue(budget.charge(
            module="control", operation="small",
        ).accepted)
        before = deepcopy(budget.export_causal_state())
        before_bytes = canonical_causal_bytes(before)
        initial_quote = budget.quote_operations(
            module="worker", operations=("small",),
        )
        invalid = []

        def alter(label, change):
            candidate = deepcopy(before)
            change(candidate)
            invalid.append((label, candidate))

        alter("wrong_version",
              lambda s: s.update(config_version="unknown"))
        alter("missing_schema_field",
              lambda s: s.pop("consumed_by_module"))
        alter("extra_schema_field",
              lambda s: s.update(unregistered_counter=1))
        alter("cycle_boolean", lambda s: s.update(cycle=True))
        alter("cycle_fractional", lambda s: s.update(cycle=7.5))
        alter("cycle_text", lambda s: s.update(cycle="7"))
        alter("cycle_zero", lambda s: s.update(cycle=0))
        alter("cycle_negative", lambda s: s.update(cycle=-1))
        alter("cycle_none_with_spending",
              lambda s: s.update(cycle=None))
        alter("cycle_none_with_zero_module_entry",
              lambda s: s.update(
                  cycle=None, consumed_cycle_uc=0,
                  consumed_by_module={"worker": 0},
              ))
        alter("cycle_none_with_zero_total_nonempty_modules",
              lambda s: s.update(
                  cycle=None, consumed_cycle_uc=0,
                  consumed_by_module={"control": 0},
              ))
        alter("consumed_cycle_boolean",
              lambda s: s.update(consumed_cycle_uc=True))
        alter("consumed_cycle_float",
              lambda s: s.update(consumed_cycle_uc=7.0))
        alter("consumed_cycle_text",
              lambda s: s.update(consumed_cycle_uc="7"))
        alter("consumed_cycle_negative",
              lambda s: s.update(consumed_cycle_uc=-1))
        alter("modules_not_mapping",
              lambda s: s.update(consumed_by_module=[("worker", 5)]))
        alter("module_boolean",
              lambda s: s["consumed_by_module"].update(control=True))
        alter("module_float",
              lambda s: s["consumed_by_module"].update(control=2.0))
        alter("module_text",
              lambda s: s["consumed_by_module"].update(control="2"))
        alter("module_negative",
              lambda s: s["consumed_by_module"].update(control=-2))
        alter("late_bad_module_boolean",
              lambda s: s.update(consumed_by_module={
                  "worker": 5, "control": False,
              }))
        alter("unknown_module",
              lambda s: s["consumed_by_module"].update(other=0))
        alter("nonstr_module_key",
              lambda s: s["consumed_by_module"].update({42: 0}))
        alter("excess_control_envelope",
              lambda s: s.update(
                  consumed_cycle_uc=10,
                  consumed_by_module={"worker": 5, "control": 5},
              ))
        alter("excess_global_ceiling",
              lambda s: s.update(
                  consumed_cycle_uc=11,
                  consumed_by_module={"worker": 7, "control": 4},
              ))
        alter("total_mismatch",
              lambda s: s.update(consumed_cycle_uc=8))
        alter("ordinary_steals_safety_reserve",
              lambda s: s.update(
                  consumed_cycle_uc=10,
                  consumed_by_module={"worker": 8, "control": 2},
              ))

        for label, bad in invalid:
            with self.subTest(label=label):
                with self.assertRaises(ValueError):
                    budget.restore_causal_state(bad)
                self.assertEqual(budget.export_causal_state(), before)
                self.assertEqual(
                    canonical_causal_bytes(budget.export_causal_state()),
                    before_bytes,
                )
                self.assertEqual(
                    budget.quote_operations(
                        module="worker", operations=("small",),
                    ),
                    initial_quote,
                )

        # A legal restore and ordinary work remain possible after every
        # rejected candidate; no attempt silently borrowed protected UC.
        budget.restore_causal_state(deepcopy(before))
        self.assertTrue(budget.charge(
            module="worker", operation="small",
        ).accepted)
        self.assertEqual(budget.consumed_cycle_uc, 9)
        self.assertEqual(budget.consumed_module_uc("worker"), 7)
        self.assertEqual(budget.consumed_module_uc("control"), 2)

    def test_all_legitimate_budget_owner_states_roundtrip_exactly(self):
        config = self.protected_snapshot_config()
        situations = []

        unopened = CycleComputeBudget(config=config)
        situations.append(("unopened", unopened))
        empty = CycleComputeBudget(config=config)
        empty.open_cycle(1)
        situations.append(("open_empty", empty))
        free = CycleComputeBudget(config=config)
        free.open_cycle(2)
        self.assertTrue(free.charge(
            module="worker", operation="zero",
        ).accepted)
        situations.append(("zero_cost_with_zero_entry", free))
        shared = CycleComputeBudget(config=config)
        shared.open_cycle(3)
        for module, operation in (
            ("worker", "large"), ("worker", "small"),
            ("control", "small"), ("control", "one"),
        ):
            self.assertTrue(shared.charge(
                module=module, operation=operation,
            ).accepted)
        self.assertEqual(shared.consumed_cycle_uc, 10)
        situations.append(("ordinary_seven_protected_three", shared))
        protected = CycleComputeBudget(config=config)
        protected.open_cycle(4)
        self.assertTrue(protected.charge(
            module="control", operation="small",
        ).accepted)
        self.assertTrue(protected.charge(
            module="control", operation="small",
        ).accepted)
        situations.append(("protected_only", protected))

        for label, source in situations:
            with self.subTest(label=label):
                state = deepcopy(source.export_causal_state())
                encoded = canonical_causal_bytes(state)
                independent = CycleComputeBudget(config=config)
                independent.open_cycle(42)
                self.assertTrue(independent.charge(
                    module="control", operation="one",
                ).accepted)
                independent.restore_causal_state(deepcopy(state))
                self.assertEqual(independent.export_causal_state(), state)
                self.assertEqual(
                    canonical_causal_bytes(independent.export_causal_state()),
                    encoded,
                )
                if source.cycle is None:
                    with self.assertRaises(RuntimeError):
                        independent.charge(
                            module="worker", operation="small",
                        )
                    continue
                self.assertEqual(
                    independent.quote_operations(
                        module="worker", operations=("small",),
                    ),
                    source.quote_operations(
                        module="worker", operations=("small",),
                    ),
                )
                self.assertEqual(
                    independent.charge(
                        module="worker", operation="small",
                    ),
                    source.charge(
                        module="worker", operation="small",
                    ),
                )
                self.assertEqual(
                    independent.export_causal_state(),
                    source.export_causal_state(),
                )

    def test_snapshot_manager_restore_keeps_budget_and_journal_deterministic(self):
        config = self.protected_snapshot_config()

        def replay_once():
            journal = HashChainedJournal()
            manager = SnapshotManager(journal=journal)
            budget = CycleComputeBudget(config=config)
            budget.open_cycle(4)
            self.assertTrue(budget.charge(
                module="worker", operation="large",
            ).accepted)
            saved = deepcopy(budget.export_causal_state())
            record = manager.take(
                snapshot_type=SnapshotType.PERIODIC,
                individual_id="i0-uc-owner-snapshot-unit",
                t_monde=4, cycle=0, attempt_ref=None,
                owners=(budget,),
                versions={"scheduler": config.version},
            )
            self.assertTrue(manager.verify(record.id))
            budget.open_cycle(5)
            self.assertTrue(budget.charge(
                module="control", operation="small",
            ).accepted)
            manager.restore(record.id, owners=(budget,))
            self.assertEqual(budget.export_causal_state(), saved)
            self.assertTrue(manager.verify(record.id))
            self.assertTrue(journal.verify())
            self.assertEqual(
                [e.causal_event["kind"] for e in journal.entries],
                ["snapshot_taken", "snapshot_restored"],
            )
            return (
                record,
                canonical_causal_bytes(budget.export_causal_state()),
                journal.canonical_bytes(),
                journal.head_hash,
            )

        self.assertEqual(replay_once(), replay_once())

    def test_verified_snapshot_with_incompatible_uc_reserve_rejects_atomically(self):
        # Deliberately malformed version discipline for this synthetic unit:
        # a snapshot is hash-valid, but the receiving owner protects more UC
        # than the writer did while accidentally reusing the version string.
        strict_config = self.protected_snapshot_config()
        loose_config = ComputeBudgetConfig(
            version=strict_config.version, cycle_ceiling=10,
            module_envelopes={"worker": 10, "control": 4},
            protected_modules=frozenset({"control"}),
            protected_capacity=1,
            operation_costs=strict_config.operation_costs,
        )
        journal = HashChainedJournal()
        manager = SnapshotManager(journal=journal)
        source = CycleComputeBudget(config=loose_config)
        source.open_cycle(1)
        for operation in ("large", "small", "small"):
            self.assertTrue(source.charge(
                module="worker", operation=operation,
            ).accepted)
        self.assertEqual(source.consumed_module_uc("worker"), 9)
        record = manager.take(
            snapshot_type=SnapshotType.PERIODIC,
            individual_id="i0-misversioned-UC-snapshot-unit",
            t_monde=1, cycle=0, attempt_ref=None,
            owners=(source,),
            versions={"scheduler": strict_config.version},
        )
        target = CycleComputeBudget(config=strict_config)
        target.open_cycle(4)
        self.assertTrue(target.charge(
            module="control", operation="small",
        ).accepted)
        before = target.export_causal_state()
        journal_before = journal.canonical_bytes()
        with self.assertRaisesRegex(ValueError, "protected reserve"):
            manager.restore(record.id, owners=(target,))
        self.assertEqual(target.export_causal_state(), before)
        self.assertEqual(journal.canonical_bytes(), journal_before)
        self.assertTrue(journal.verify())
        self.assertTrue(manager.verify(record.id))

    def test_budget_state_is_snapshot_restorable(self) -> None:
        budget = CycleComputeBudget(config=self.config())
        budget.open_cycle(4)
        budget.charge(module="worker", operation="small")
        state = budget.export_causal_state()

        budget.open_cycle(5)
        budget.restore_causal_state(state)

        self.assertEqual(budget.cycle, 4)
        self.assertEqual(budget.consumed_cycle_uc, 2)
        self.assertEqual(budget.consumed_module_uc("worker"), 2)

    def test_overconsuming_stub_can_be_stopped_without_blocking_cycle(self) -> None:
        budget = CycleComputeBudget(config=self.config())
        budget.open_cycle(1)

        operations_completed = 0
        for _ in range(10):
            charge = budget.charge(module="worker", operation="small")
            if not charge.accepted:
                break
            operations_completed += 1

        self.assertEqual(operations_completed, 3)
        self.assertLessEqual(budget.consumed_cycle_uc, self.config().cycle_ceiling)

    def test_budget_never_uses_machine_time(self) -> None:
        budget_a = CycleComputeBudget(config=self.config())
        budget_b = CycleComputeBudget(config=self.config())
        budget_a.open_cycle(1)
        budget_b.open_cycle(1)

        for _ in range(2):
            budget_a.charge(module="worker", operation="small")
            budget_b.charge(module="worker", operation="small")

        self.assertEqual(
            budget_a.export_causal_state(),
            budget_b.export_causal_state(),
        )


if __name__ == "__main__":
    unittest.main()
