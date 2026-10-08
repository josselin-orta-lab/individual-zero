from __future__ import annotations

from pathlib import Path
import unittest

from lab.bench import EvaluationBench
from lab.journal_views import EvaluationTrace
from lab.oracle import OracleAccessDenied, OracleCapability, create_oracle
from lab.world import BodyState, Position, ToolRecipe, BerryEffect, WorldBody, WorldLayout, WorldPhysicsConfig


def world() -> WorldBody:
    config = WorldPhysicsConfig(
        version="oracle-test-v1",
        width=32,
        height=32,
        day_steps=300,
        night_steps=100,
        night_start_step=200,
        initial_body=BodyState(50.0, 60.0, 60.0, 100.0),
        initial_position=Position(2, 2),
        food_decay_per_step=0.0,
        water_decay_per_step=0.0,
        action_energy_costs={
            "se_deplacer": 0.0,
            "collecter": 0.0,
            "manger": 0.0,
            "boire": 0.0,
            "poser_une_pierre": 0.0,
            "fabriquer_outil": 0.0,
            "dormir": 0.0,
            "attendre": 0.0,
        },
        sleep_energy_gain=0.0,
        rest_integrity_gain=0.0,
        drink_water_gain=1.0,
        berry_effects={
            "berry_a": BerryEffect(1.0, 0.0),
            "berry_b": BerryEffect(1.0, -1.0),
        },
        creature_damage=1.0,
        tool_recipe=ToolRecipe(1, 1, 2),
    )
    return WorldBody(
        config=config,
        layout=WorldLayout(oracle_canary="ORACLE_ONLY_CANARY"),
    )


class OracleBoundaryTests(unittest.TestCase):
    def test_invalid_capability_cannot_read_oracle(self) -> None:
        instance = world()
        oracle, _ = create_oracle(instance)

        with self.assertRaises(OracleAccessDenied):
            oracle.read_ground_truth(OracleCapability(object()))

    def test_bench_can_read_ground_truth_and_canary(self) -> None:
        instance = world()
        oracle, capability = create_oracle(instance)
        trace = EvaluationTrace()
        bench = EvaluationBench(
            oracle=oracle,
            capability=capability,
            trace=trace,
        )

        truth = bench.oracle_truth()

        self.assertEqual(truth["oracle_canary"], "ORACLE_ONLY_CANARY")
        self.assertEqual(trace.records[-1].kind, "oracle_read")

    def test_oracle_canary_is_not_in_world_causal_state(self) -> None:
        state = world().export_causal_state()

        self.assertNotIn("oracle_canary", state)

    def test_i0_package_has_no_oracle_or_bench_dependency(self) -> None:
        root = Path(__file__).resolve().parents[1] / "src" / "i0"
        forbidden = (
            "lab.oracle",
            "EvaluationBench",
            "EvaluationTrace",
            "oracle_truth",
        )

        offenders: list[str] = []
        for path in root.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            if any(token in text for token in forbidden):
                offenders.append(str(path.relative_to(root)))

        self.assertEqual(offenders, [])

    def test_evaluation_metrics_are_external(self) -> None:
        instance = world()
        oracle, capability = create_oracle(instance)
        trace = EvaluationTrace()
        bench = EvaluationBench(
            oracle=oracle,
            capability=capability,
            trace=trace,
        )

        bench.count_lethal_transition(data={"t_monde": 1})
        bench.count_lethal_rollback(data={"t_monde": 1})

        self.assertEqual(bench.metrics.lethal_transitions, 1)
        self.assertEqual(bench.metrics.lethal_rollbacks, 1)
        self.assertEqual(len(trace.records), 2)


if __name__ == "__main__":
    unittest.main()
