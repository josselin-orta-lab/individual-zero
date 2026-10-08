from __future__ import annotations

import unittest

from i0.equipment import train_exact_transition_table
from i0.interfaces import PrimitiveCommand
from i0.modules.simulator import Simulator, SimulatorConfig
from i0.modules.stage6_planning import (
    SimulatorPlanner,
    Stage6PlanningConfig,
)
from lab.equipment_corpus import EquipmentCorpusRecorder
from lab.stage4_reference_fixture import build_stage4_reference_runtime
from lab.world import WorldBody, WorldLayout


def shelter_planner():
    stage4 = build_stage4_reference_runtime()
    world = WorldBody(
        config=stage4.world.config,
        layout=WorldLayout(),
    )
    world._inventory["stone"] = 4  # controlled offline corpus fixture only

    recorder = EquipmentCorpusRecorder(
        corpus_version="stage6-shelter-corpus-v1",
    )
    examples = []
    for step in range(1, 5):
        examples.append(
            recorder.record_transition(
                world=world,
                t_monde=step,
                family="stone_placement",
                command=PrimitiveCommand("poser_une_pierre"),
            )
        )

    equipment = train_exact_transition_table(
        corpus=recorder.build(),
        equipment_version="E-v1-shelter-test",
    )
    simulator = Simulator(
        config=SimulatorConfig(
            version="stage6-shelter-sim-v1",
            r_max=1,
            h_max=4,
        ),
        equipment=equipment,
    )
    planner = SimulatorPlanner(
        config=Stage6PlanningConfig(
            version="stage6-shelter-plan-v1",
            option_ttl_steps=20,
            max_depth=4,
            revision_delta=0.1,
            setpoints=dict(stage4._config.value_needs.setpoints),
        ),
        simulator=simulator,
    )
    return planner, examples[0].state


class Stage6PlanningTests(unittest.TestCase):
    def test_shelter_plan_is_found_under_fixed_horizon(self) -> None:
        planner, initial_state = shelter_planner()

        result = planner.plan_target(
            initial_state=initial_state,
            target="shelter_here",
        )

        self.assertEqual(result.status, "plan_found")
        self.assertEqual(
            [command.primitive for command in result.commands],
            ["poser_une_pierre"] * 4,
        )
        self.assertEqual(len(result.predictions), 4)
        self.assertTrue(result.predictions[-1].next_state.known_shelter_here)
        self.assertLessEqual(result.expanded_states, 4)

    def test_missing_final_transition_is_reported_as_incomplete_model(self) -> None:
        stage4 = build_stage4_reference_runtime()
        world = WorldBody(
            config=stage4.world.config,
            layout=WorldLayout(),
        )
        world._inventory["stone"] = 4
        recorder = EquipmentCorpusRecorder(
            corpus_version="stage6-incomplete-shelter-v1",
        )
        for step in range(1, 4):
            recorder.record_transition(
                world=world,
                t_monde=step,
                family="stone_placement",
                command=PrimitiveCommand("poser_une_pierre"),
            )
        equipment = train_exact_transition_table(
            corpus=recorder.build(),
            equipment_version="E-v1-incomplete-shelter",
        )
        planner = SimulatorPlanner(
            config=Stage6PlanningConfig(
                version="stage6-incomplete-plan-v1",
                option_ttl_steps=20,
                max_depth=4,
                setpoints=dict(stage4._config.value_needs.setpoints),
            ),
            simulator=Simulator(
                config=SimulatorConfig(
                    version="stage6-incomplete-sim-v1",
                    r_max=1,
                    h_max=4,
                ),
                equipment=equipment,
            ),
        )

        result = planner.plan_target(
            initial_state=recorder.build().examples[0].state,
            target="shelter_here",
        )

        self.assertEqual(result.status, "incomplete_model")
        self.assertGreater(result.unavailable_edges, 0)


if __name__ == "__main__":
    unittest.main()
