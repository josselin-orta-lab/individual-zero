from __future__ import annotations

import unittest

from lab.compute_budget import ComputeBudgetConfig, CycleComputeBudget


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
