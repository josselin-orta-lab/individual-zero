from __future__ import annotations

import unittest

from lab.compute_budget import ComputeBudgetConfig
from lab.replay import compare_causal_state, verify_reexecution
from lab.stage1_runtime import ScriptedStage1Runtime


def fixture_budget_config() -> ComputeBudgetConfig:
    return ComputeBudgetConfig(
        version="stage1-test-v1",
        cycle_ceiling=100,
        module_envelopes={"stage1_fixture": 100},
        protected_modules=frozenset({"stage1_fixture"}),
        protected_capacity=10,
        operation_costs={"fixture_op": 1},
    )


class ReplayVerificationTests(unittest.TestCase):
    def test_equal_causal_states_compare_identically(self) -> None:
        result = compare_causal_state(
            {"world": 3, "state": [1, 2]},
            {"state": [1, 2], "world": 3},
        )

        self.assertTrue(result.identical)
        self.assertEqual(result.reference_sha256, result.replay_sha256)
        result.require_identical()

    def test_divergence_is_reported(self) -> None:
        result = compare_causal_state(
            {"world": 3},
            {"world": 4},
        )

        self.assertFalse(result.identical)
        self.assertNotEqual(result.reference_sha256, result.replay_sha256)
        with self.assertRaises(AssertionError):
            result.require_identical()

    def test_independent_stage1_reexecution_is_identical(self) -> None:
        def execute():
            runtime = ScriptedStage1Runtime(campaign_seed=71, budget_config=fixture_budget_config())
            for _ in range(4):
                runtime.run_step(cycle=1)
            return runtime.causal_fingerprint()

        result = verify_reexecution(
            execute_reference=execute,
            execute_replay=execute,
        )

        self.assertTrue(result.identical)
        result.require_identical()


if __name__ == "__main__":
    unittest.main()
