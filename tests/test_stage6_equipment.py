from __future__ import annotations

import unittest

from i0.equipment import (
    EquipmentCorpus,
    EquipmentCorpusExample,
    SimulationNeighbor,
    SimulationState,
    train_exact_transition_table,
)
from i0.interfaces import PrimitiveCommand
from i0.modules.simulator import Simulator, SimulatorConfig


def state(*, x: int = 2, passable_east: bool = True) -> SimulationState:
    return SimulationState(
        schema_version="stage6-test-state-v1",
        x=x,
        y=2,
        body={
            "energy": 50.0,
            "food": 60.0,
            "water": 60.0,
            "integrity": 100.0,
        },
        inventory={
            "berry_a": 0,
            "berry_b": 0,
            "wood": 0,
            "stone": 0,
            "tool": 0,
        },
        current_water_source=False,
        current_resources=(),
        adjacent=(
            SimulationNeighbor(
                direction="east",
                x=x + 1,
                y=2,
                passable=passable_east,
                water_source=False,
                resources=(),
                creature=False,
            ),
        ),
        known_shelter_here=False,
        is_night=False,
    )


def corpus() -> EquipmentCorpus:
    before = state(x=2)
    after = state(x=3)
    return EquipmentCorpus(
        version="stage6-test-corpus-v1",
        examples=(
            EquipmentCorpusExample(
                family="free_movement",
                state=before,
                command=PrimitiveCommand(
                    "se_deplacer",
                    {"direction": "east"},
                ),
                observed_next_state=after,
                terminal=False,
            ),
        ),
    )


class EquipmentContractTests(unittest.TestCase):
    def test_training_produces_deterministic_immutable_artifact(self) -> None:
        first = train_exact_transition_table(
            corpus=corpus(),
            equipment_version="E-v1-test",
        )
        second = train_exact_transition_table(
            corpus=corpus(),
            equipment_version="E-v1-test",
        )

        self.assertEqual(first.artifact_digest, second.artifact_digest)
        self.assertEqual(first.version, "E-v1-test")

    def test_known_input_predicts_exact_recorded_transition(self) -> None:
        model = train_exact_transition_table(
            corpus=corpus(),
            equipment_version="E-v1-test",
        )
        prediction = model.predict(
            state=state(x=2),
            command=PrimitiveCommand(
                "se_deplacer",
                {"direction": "east"},
            ),
        )

        self.assertEqual(prediction.next_state.x, 3)
        self.assertEqual(prediction.confidence, 1.0)
        self.assertEqual(prediction.horizon, 1)

    def test_unseen_input_is_unavailable_not_extrapolated(self) -> None:
        model = train_exact_transition_table(
            corpus=corpus(),
            equipment_version="E-v1-test",
        )

        with self.assertRaises(LookupError):
            model.predict(
                state=state(x=4),
                command=PrimitiveCommand(
                    "se_deplacer",
                    {"direction": "east"},
                ),
            )

    def test_conflicting_same_accessible_input_is_rejected(self) -> None:
        base = corpus().examples[0]
        conflicting = EquipmentCorpusExample(
            family="free_movement",
            state=base.state,
            command=base.command,
            observed_next_state=state(x=2),
            terminal=False,
        )
        bad = EquipmentCorpus(
            version="bad-corpus",
            examples=(base, conflicting),
        )

        with self.assertRaisesRegex(ValueError, "conflicting"):
            train_exact_transition_table(
                corpus=bad,
                equipment_version="E-v1-test",
            )


class SimulatorTests(unittest.TestCase):
    def simulator(self) -> Simulator:
        return Simulator(
            config=SimulatorConfig(
                version="sim-test-v1",
                r_max=4,
                h_max=3,
            ),
            equipment=train_exact_transition_table(
                corpus=corpus(),
                equipment_version="E-v1-test",
            ),
        )

    def test_deterministic_rollouts_are_not_repeated(self) -> None:
        result = self.simulator().rollout(
            initial_state=state(x=2),
            commands=(
                PrimitiveCommand("se_deplacer", {"direction": "east"}),
            ),
            r_eff=4,
            h_eff=1,
        )

        self.assertTrue(result.complete)
        self.assertEqual(result.requested_rollouts, 4)
        self.assertEqual(result.effective_rollouts, 1)
        self.assertEqual(len(result.completed_rollouts), 1)

    def test_partial_unseen_rollout_is_explicitly_unavailable(self) -> None:
        result = self.simulator().rollout(
            initial_state=state(x=2),
            commands=(
                PrimitiveCommand("se_deplacer", {"direction": "east"}),
                PrimitiveCommand("se_deplacer", {"direction": "east"}),
            ),
            r_eff=2,
            h_eff=2,
        )

        self.assertFalse(result.complete)
        self.assertEqual(result.reason, "equipment_input_unseen")
        self.assertEqual(result.completed_rollouts, ())
        self.assertIsNotNone(result.partial_rollout)
        self.assertEqual(result.partial_rollout.horizon_reached, 1)

    def test_budget_bounds_are_enforced(self) -> None:
        simulator = self.simulator()
        with self.assertRaises(ValueError):
            simulator.rollout(
                initial_state=state(),
                commands=(PrimitiveCommand("attendre"),),
                r_eff=5,
                h_eff=1,
            )


if __name__ == "__main__":
    unittest.main()
