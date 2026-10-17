from __future__ import annotations

import unittest
from copy import deepcopy
from decimal import Decimal
from fractions import Fraction
from math import inf, nan
from dataclasses import replace
from types import MappingProxyType

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

    def test_open_cycle_only_accepts_exact_positive_int_before_reset(self):
        budget = CycleComputeBudget(config=self.config())
        budget.open_cycle(4)
        self.assertTrue(budget.charge(
            module="worker", operation="small",
        ).accepted)
        original = budget.export_causal_state()
        original_bytes = canonical_causal_bytes(original)
        quote = budget.quote_operations(
            module="worker", operations=("small",),
        )

        invalid_cycles = (
            True, False, 0, -1, 0.0, 1.0, 1.25, -0.5,
            nan, inf, -inf, Decimal("2"), Fraction(3, 2),
            "5", None, [], {}, (5,),
        )
        for value in invalid_cycles:
            with self.subTest(value=repr(value)):
                with self.assertRaises(ValueError):
                    budget.open_cycle(value)
                self.assertEqual(budget.export_causal_state(), original)
                self.assertEqual(
                    canonical_causal_bytes(budget.export_causal_state()),
                    original_bytes,
                )
                self.assertEqual(
                    budget.quote_operations(
                        module="worker", operations=("small",),
                    ),
                    quote,
                )
        # A rejected open never resets the current ledger. Only a
        # legitimate next cycle may renew the envelope.
        self.assertEqual(budget.cycle, 4)
        self.assertTrue(budget.charge(
            module="worker", operation="small",
        ).accepted)
        self.assertEqual(budget.consumed_cycle_uc, 4)
        budget.open_cycle(5)
        self.assertEqual(budget.cycle, 5)
        self.assertEqual(budget.consumed_cycle_uc, 0)
        self.assertEqual(budget.consumed_module_uc("worker"), 0)

    def test_charge_count_rejects_noncanonical_numeric_types_atomically(self):
        budget = CycleComputeBudget(config=self.config())
        budget.open_cycle(3)
        self.assertTrue(budget.charge(
            module="worker", operation="small",
        ).accepted)
        before = budget.export_causal_state()
        before_bytes = canonical_causal_bytes(before)
        expected_quote = budget.quote_operations(
            module="worker", operations=("small",),
        )
        invalid_counts = (
            True, False, -1, -3, 0.0, 1.0, 1.5, -0.1,
            nan, inf, -inf, Decimal("1"), Decimal("1.5"),
            Fraction(1, 2), "2", None, [], {}, (2,),
        )
        for value in invalid_counts:
            with self.subTest(value=repr(value)):
                with self.assertRaises(ValueError):
                    budget.charge(
                        module="worker", operation="small", count=value,
                    )
                self.assertEqual(budget.export_causal_state(), before)
                self.assertEqual(
                    canonical_causal_bytes(budget.export_causal_state()),
                    before_bytes,
                )
                self.assertEqual(
                    budget.quote_operations(
                        module="worker", operations=("small",),
                    ),
                    expected_quote,
                )
        # Invalid calls have not consumed, reserved or silently rounded UC.
        receipt = budget.charge(module="worker", operation="small")
        self.assertTrue(receipt.accepted)
        self.assertIs(type(receipt.requested_uc), int)
        self.assertEqual(receipt.requested_uc, 2)
        self.assertEqual(budget.consumed_cycle_uc, 4)

    def test_charge_identifiers_fail_cleanly_without_mutating_uc(self):
        budget = CycleComputeBudget(config=self.config())
        # Keep the original missing-open-cycle contract, even if the
        # request itself contains malformed identifiers or count.
        with self.assertRaises(RuntimeError):
            budget.charge(module=[], operation=[], count=1.5)
        budget.open_cycle(1)
        original = budget.export_causal_state()
        encoded = canonical_causal_bytes(original)
        invalid_requests = (
            ([], "small"), ({}, "small"), (True, "small"),
            (None, "small"), (1, "small"), ("missing", "small"),
            ("worker", []), ("worker", {}), ("worker", True),
            ("worker", None), ("worker", 1), ("worker", "missing"),
        )
        for module, operation in invalid_requests:
            with self.subTest(module=repr(module), operation=repr(operation)):
                with self.assertRaises(ValueError):
                    budget.charge(
                        module=module, operation=operation, count=1,
                    )
                self.assertEqual(
                    canonical_causal_bytes(budget.export_causal_state()),
                    encoded,
                )
                self.assertEqual(budget.export_causal_state(), original)
        self.assertTrue(budget.charge(
            module="worker", operation="small",
        ).accepted)

    def test_integer_counts_and_snapshot_replay_preserve_old_uc_semantics(self):
        config = self.protected_snapshot_config()

        def one_independent_run():
            budget = CycleComputeBudget(config=config)
            journal = HashChainedJournal()
            manager = SnapshotManager(journal=journal)
            budget.open_cycle(2)
            zero_count = budget.charge(
                module="worker", operation="small", count=0,
            )
            double_count = budget.charge(
                module="worker", operation="small", count=2,
            )
            zero_cost = budget.charge(
                module="control", operation="zero", count=2,
            )
            default_count = budget.charge(
                module="control", operation="one",
            )
            self.assertEqual(
                (zero_count.accepted, zero_count.requested_uc), (True, 0),
            )
            self.assertEqual(
                (double_count.accepted, double_count.requested_uc), (True, 4),
            )
            self.assertEqual(
                (zero_cost.accepted, zero_cost.requested_uc), (True, 0),
            )
            self.assertEqual(
                (default_count.accepted, default_count.requested_uc), (True, 1),
            )
            self.assertEqual(
                budget.export_causal_state()["consumed_by_module"],
                {"control": 1, "worker": 4},
            )
            self.assertEqual(budget.consumed_cycle_uc, 5)
            before_refusal = canonical_causal_bytes(
                budget.export_causal_state()
            )
            unaffordable = budget.charge(
                module="worker", operation="large",
            )
            self.assertEqual(
                (unaffordable.accepted, unaffordable.reason),
                (False, "protected_capacity"),
            )
            self.assertEqual(
                canonical_causal_bytes(budget.export_causal_state()),
                before_refusal,
            )

            state_at_capture = deepcopy(budget.export_causal_state())
            record = manager.take(
                snapshot_type=SnapshotType.PERIODIC,
                individual_id="i0-stage11-canonical-count-snapshot-unit",
                t_monde=2, cycle=0, attempt_ref=None,
                owners=(budget,),
                versions={"scheduler": config.version},
            )
            self.assertTrue(manager.verify(record.id))
            budget.open_cycle(3)
            self.assertTrue(budget.charge(
                module="control", operation="small",
            ).accepted)
            manager.restore(record.id, owners=(budget,))
            self.assertEqual(budget.export_causal_state(), state_at_capture)
            self.assertEqual(
                canonical_causal_bytes(budget.export_causal_state()),
                canonical_causal_bytes(state_at_capture),
            )
            self.assertTrue(manager.verify(record.id))
            self.assertTrue(journal.verify())
            self.assertEqual(
                [event.causal_event["kind"] for event in journal.entries],
                ["snapshot_taken", "snapshot_restored"],
            )
            return (
                (zero_count, double_count, zero_cost, default_count, unaffordable),
                record,
                canonical_causal_bytes(budget.export_causal_state()),
                journal.canonical_bytes(),
                journal.head_hash,
            )

        self.assertEqual(one_independent_run(), one_independent_run())

    def test_versioned_config_rejects_noncanonical_uc_values_and_types(self):
        base = self.config()
        invalid = []

        def broken(label, **changes):
            invalid.append((label, replace(base, **changes)))

        for label, value in (
            ("bool_true", True), ("bool_false", False), ("float_integer", 10.0),
            ("float_fraction", 10.5), ("nan", nan), ("inf", inf),
            ("negative_inf", -inf), ("decimal", Decimal("10")),
            ("fraction", Fraction(1, 2)), ("text", "10"),
            ("none", None), ("list", [10]), ("negative", -1),
        ):
            broken("cycle_ceiling_" + label, cycle_ceiling=value)
            broken("protected_capacity_" + label, protected_capacity=value)
            broken("module_envelope_" + label, module_envelopes={
                "worker": value, "control": 4,
            })
            broken("operation_cost_" + label, operation_costs={
                "small": value, "large": 5,
            })
        broken("reserve_exceeds_ceiling", protected_capacity=11)
        broken("empty_version", version="")
        for label, value in (
            ("bool", True), ("integer", 1), ("none", None),
            ("list", ["v1"]), ("tuple", ("v1",)),
        ):
            broken("version_" + label, version=value)

        for label, value in (
            ("none", None), ("list", [("worker", 6)]),
            ("empty_dict", {}), ("text", "worker"),
            ("nonstring_module_key", {1: 6, "control": 4}),
            ("bool_module_key", {True: 6, "control": 4}),
            ("empty_module_key", {"": 6, "control": 4}),
            ("negative_envelope", {"worker": -1, "control": 4}),
            ("missing_protected_module", {"worker": 6}),
        ):
            broken("envelopes_" + label, module_envelopes=value)
        for label, value in (
            ("none", None), ("list", [("small", 2)]),
            ("empty_dict", {}), ("text", "small"),
            ("nonstring_cost_key", {1: 2, "large": 5}),
            ("bool_cost_key", {True: 2, "large": 5}),
            ("empty_cost_key", {"": 2, "large": 5}),
            ("negative_cost", {"small": -1, "large": 5}),
        ):
            broken("costs_" + label, operation_costs=value)
        for label, value in (
            ("mutable_set", {"control"}),
            ("list", ["control"]), ("tuple", ("control",)),
            ("none", None), ("text", "control"),
            ("bool_module", frozenset({True})),
            ("numeric_module", frozenset({1})),
            ("empty_module", frozenset({""})),
            ("unregistered_module", frozenset({"unknown"})),
        ):
            broken("protected_members_" + label, protected_modules=value)

        # The constructor itself must fail before any owner can be opened.
        # Neither an annotation nor a frozen dataclass coerces invalid data.
        for label, config in invalid:
            with self.subTest(label=label):
                with self.assertRaises(ValueError):
                    config.validate()
                with self.assertRaises(ValueError):
                    CycleComputeBudget(config=config)

        # Repeated validation of the original valid input is unchanged.
        for _ in range(2):
            base.validate()
        owner = CycleComputeBudget(config=base)
        owner.open_cycle(1)
        receipt = owner.charge(module="worker", operation="small")
        self.assertTrue(receipt.accepted)
        self.assertIs(type(receipt.requested_uc), int)
        self.assertEqual(receipt.requested_uc, 2)

    def test_immutable_mapping_and_zero_uc_config_stay_valid(self):
        standard = self.config()
        immutable_mapping_config = replace(
            standard, version="fixture-mappingproxy-v1",
            module_envelopes=MappingProxyType(dict(standard.module_envelopes)),
            operation_costs=MappingProxyType(dict(standard.operation_costs)),
        )
        zero_config = ComputeBudgetConfig(
            version="fixture-zero-uc-v1", cycle_ceiling=0,
            module_envelopes={"worker": 0},
            protected_modules=frozenset(),
            protected_capacity=0,
            operation_costs={"zero": 0},
        )
        multiple_protected = ComputeBudgetConfig(
            version="fixture-two-protected-v1", cycle_ceiling=10,
            module_envelopes={"worker": 7, "control": 4, "gatekeeper": 3},
            protected_modules=frozenset({"control", "gatekeeper"}),
            protected_capacity=3,
            operation_costs={"small": 2, "one": 1, "zero": 0},
        )
        no_protected = ComputeBudgetConfig(
            version="fixture-no-protected-v1", cycle_ceiling=10,
            module_envelopes={"worker": 10},
            protected_modules=frozenset(), protected_capacity=0,
            operation_costs={"small": 2, "zero": 0},
        )

        for config, module, operation in (
            (standard, "worker", "small"),
            (immutable_mapping_config, "worker", "small"),
            (zero_config, "worker", "zero"),
            (multiple_protected, "control", "one"),
            (no_protected, "worker", "small"),
        ):
            with self.subTest(version=config.version):
                original_envelopes = dict(config.module_envelopes)
                original_costs = dict(config.operation_costs)
                config.validate()
                config.validate()
                self.assertEqual(dict(config.module_envelopes), original_envelopes)
                self.assertEqual(dict(config.operation_costs), original_costs)

                def independent():
                    journal = HashChainedJournal()
                    manager = SnapshotManager(journal=journal)
                    budget = CycleComputeBudget(config=config)
                    budget.open_cycle(1)
                    first = budget.charge(
                        module=module, operation=operation, count=1,
                    )
                    self.assertTrue(first.accepted)
                    self.assertIs(type(first.requested_uc), int)
                    expected = config.operation_costs[operation]
                    self.assertEqual(first.requested_uc, expected)
                    owner = deepcopy(budget.export_causal_state())
                    snapshot = manager.take(
                        snapshot_type=SnapshotType.PERIODIC,
                        individual_id="i0-stage11-uc-config-validation-v1",
                        t_monde=1, cycle=0, attempt_ref=None,
                        owners=(budget,),
                        versions={"scheduler": config.version},
                    )
                    self.assertTrue(manager.verify(snapshot.id))
                    budget.open_cycle(2)
                    budget.charge(module=module, operation=operation)
                    manager.restore(snapshot.id, owners=(budget,))
                    self.assertEqual(budget.export_causal_state(), owner)
                    self.assertTrue(manager.verify(snapshot.id))
                    self.assertTrue(journal.verify())
                    self.assertEqual(
                        [e.causal_event["kind"] for e in journal.entries],
                        ["snapshot_taken", "snapshot_restored"],
                    )
                    return (
                        first, snapshot, canonical_causal_bytes(owner),
                        journal.canonical_bytes(), journal.head_hash,
                    )
                self.assertEqual(independent(), independent())

    def test_invalid_nan_budget_config_never_reaches_a_scheduler_owner(self):
        config = replace(self.config(), operation_costs={
            "small": nan, "large": 5,
        })
        with self.assertRaises(ValueError):
            config.validate()
        with self.assertRaises(ValueError):
            CycleComputeBudget(config=config)
        # Verify the same operation on a valid declared config remains
        # an integer-valued UC charge and has exact deterministic state.
        owner = CycleComputeBudget(config=self.config())
        owner.open_cycle(1)
        recorded = owner.charge(module="worker", operation="small")
        self.assertEqual(recorded.requested_uc, 2)
        self.assertEqual(recorded.consumed_cycle_uc, 2)
        self.assertIs(type(recorded.requested_uc), int)
        self.assertEqual(
            canonical_causal_bytes(owner.export_causal_state()),
            canonical_causal_bytes({
                "config_version": "fixture-v1",
                "cycle": 1,
                "consumed_cycle_uc": 2,
                "consumed_by_module": {"worker": 2},
            }),
        )

    def test_scheduler_owner_detaches_caller_owned_uc_mappings(self):
        source_envelopes = {"worker": 7, "control": 3}
        source_costs = {"small": 2, "zero": 0}
        config = ComputeBudgetConfig(
            version="stage11-uc-mapping-ownership-unit-v1",
            cycle_ceiling=10,
            module_envelopes=source_envelopes,
            protected_modules=frozenset({"control"}),
            protected_capacity=3,
            operation_costs=source_costs,
        )
        owner = CycleComputeBudget(config=config)
        owner.open_cycle(1)
        baseline_quote = owner.quote_operations(
            module="worker", operations=("small", "small"),
        )
        self.assertEqual(
            (baseline_quote.required_uc, baseline_quote.available_uc),
            (4, 7),
        )
        original = owner.export_causal_state()
        original_bytes = canonical_causal_bytes(original)

        # The producer, NOT the owner, mutates aliased dicts after init.
        # A public owner must not silently accept altered/free P-43 prices.
        source_envelopes["worker"] = 0
        source_envelopes["unregistered"] = 500
        source_costs["small"] = 0
        source_costs["zero"] = 9
        source_costs["unregistered"] = 0
        source_envelopes.clear()
        source_costs.clear()

        self.assertEqual(owner.export_causal_state(), original)
        self.assertEqual(
            canonical_causal_bytes(owner.export_causal_state()),
            original_bytes,
        )
        self.assertEqual(
            owner.quote_operations(
                module="worker", operations=("small", "small"),
            ),
            baseline_quote,
        )
        self.assertEqual(
            owner.charge(
                module="worker", operation="small", count=2,
            ).requested_uc,
            4,
        )
        self.assertEqual(owner.consumed_module_uc("worker"), 4)
        self.assertEqual(owner.consumed_cycle_uc, 4)
        with self.assertRaises(ValueError):
            owner.charge(module="worker", operation="unregistered")
        with self.assertRaises(ValueError):
            owner.charge(module="unregistered", operation="small")
        with self.assertRaises(ValueError):
            owner.quote_operations(
                module="worker", operations=("unregistered",),
            )
        self.assertEqual(owner.consumed_cycle_uc, 4)
        rejected = owner.charge(
            module="worker", operation="small", count=2,
        )
        self.assertFalse(rejected.accepted)
        # The original worker envelope is 7 UC, so the first refusal
        # remains module_envelope; later source mutation cannot alter it.
        self.assertEqual(rejected.reason, "module_envelope")
        self.assertEqual(owner.consumed_cycle_uc, 4)
        bad = deepcopy(owner.export_causal_state())
        bad["consumed_cycle_uc"] = 8
        bad["consumed_by_module"] = {"worker": 8}
        previous = canonical_causal_bytes(owner.export_causal_state())
        with self.assertRaises(ValueError):
            owner.restore_causal_state(bad)
        self.assertEqual(
            canonical_causal_bytes(owner.export_causal_state()), previous,
        )
        # A zero-cost operation remains zero; the producer's later
        # replacement of that cost with 9 cannot make it expensive.
        free = owner.charge(module="worker", operation="zero")
        self.assertTrue(free.accepted)
        self.assertEqual(free.requested_uc, 0)

    def test_mappingproxy_producer_mutation_keeps_guarded_snapshot_replay(self):
        def independent():
            envelope_source = {"worker": 7, "control": 3}
            operation_source = {"small": 2, "zero": 0}
            config = ComputeBudgetConfig(
                version="stage11-uc-mapping-ownership-guarded-v1",
                cycle_ceiling=10,
                module_envelopes=MappingProxyType(envelope_source),
                protected_modules=frozenset({"control"}),
                protected_capacity=3,
                operation_costs=MappingProxyType(operation_source),
                cycle_occurrence_guard=True,
            )
            budget = CycleComputeBudget(config=config)
            journal = HashChainedJournal()
            manager = SnapshotManager(journal=journal)
            budget.open_cycle(1, occurrence=(1, "first-attempt", 1))
            first = budget.charge(module="worker", operation="small")
            self.assertEqual((first.accepted, first.requested_uc), (True, 2))
            saved = deepcopy(budget.export_causal_state())
            snapshot = manager.take(
                snapshot_type=SnapshotType.PERIODIC,
                individual_id="i0-uc-owner-custody-v1", t_monde=1,
                cycle=0, attempt_ref=None, owners=(budget,),
                versions={"scheduler": config.version},
            )
            self.assertTrue(manager.verify(snapshot.id))

            envelope_source["worker"] = 0
            operation_source["small"] = 0
            operation_source["zero"] = 500
            envelope_source.clear()
            operation_source.clear()

            quoted = budget.quote_operations(
                module="worker", operations=("small",),
            )
            self.assertEqual(
                (quoted.required_uc, quoted.available_uc), (2, 5),
            )
            budget.open_cycle(1, occurrence=(2, "next-step-attempt", 1))
            second = budget.charge(module="worker", operation="small")
            self.assertEqual((second.accepted, second.requested_uc), (True, 2))
            manager.restore(snapshot.id, owners=(budget,))
            self.assertEqual(budget.export_causal_state(), saved)
            with self.assertRaises(RuntimeError):
                budget.open_cycle(1, occurrence=(1, "first-attempt", 1))
            self.assertEqual(budget.export_causal_state(), saved)
            self.assertTrue(manager.verify(snapshot.id))
            self.assertTrue(journal.verify())
            return (
                first, second, snapshot.id, snapshot.sha256,
                canonical_causal_bytes(budget.export_causal_state()),
                journal.canonical_bytes(), journal.head_hash,
            )
        self.assertEqual(independent(), independent())

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
