from __future__ import annotations

import unittest
from dataclasses import replace

from i0.equipment import EquipmentCorpus, EquipmentCorpusExample, train_exact_transition_table
from i0.interfaces import PrimitiveCommand
from i0.modules import StaticSafetyFacts
from i0.modules.simulator import SimulatorConfig
from i0.modules.stage6_evaluator import Stage6EvaluationConfig
from i0.modules.stage6_planning import Stage6PlanningConfig
from lab.equipment_corpus import EquipmentCorpusRecorder
from lab.safety_protocol import SafetyProtocolConfig
from lab.stage4_reference_fixture import build_stage4_reference_runtime
from lab.stage6_runtime import Stage6Config, Stage6Runtime
from lab.world import Position, WorldBody, WorldLayout


def stage6_runtime(
    *,
    include_drink: bool,
    predicted_water_after: float | None = None,
) -> Stage6Runtime:
    stage4 = build_stage4_reference_runtime()
    world_config = stage4.world.config
    layout = WorldLayout(
        water_sources=frozenset({Position(2, 2)}),
    )

    training_world = WorldBody(
        config=world_config,
        layout=layout,
    )
    recorder = EquipmentCorpusRecorder(
        corpus_version="stage6-runtime-corpus-v1",
    )
    if include_drink:
        recorder.record_transition(
            world=training_world,
            t_monde=1,
            family="drinking",
            command=PrimitiveCommand("boire"),
        )
    else:
        recorder.record_transition(
            world=training_world,
            t_monde=1,
            family="wait",
            command=PrimitiveCommand("attendre"),
        )

    corpus = recorder.build()
    if include_drink and predicted_water_after is not None:
        example = corpus.examples[0]
        predicted_state = replace(
            example.observed_next_state,
            body={
                **dict(example.observed_next_state.body),
                "water": predicted_water_after,
            },
        )
        corpus = EquipmentCorpus(
            version=corpus.version,
            examples=(
                EquipmentCorpusExample(
                    family=example.family,
                    state=example.state,
                    command=example.command,
                    observed_next_state=predicted_state,
                    terminal=example.terminal,
                ),
            ),
        )

    equipment = train_exact_transition_table(
        corpus=corpus,
        equipment_version=(
            "E-v1-runtime-drink"
            if include_drink
            else "E-v1-runtime-no-drink"
        ),
    )

    return Stage6Runtime(
        world_config=world_config,
        layout=layout,
        safety_config=SafetyProtocolConfig(
            version="stage6-runtime-safety-v1",
            lethal_max=2,
            mode="campaign",
        ),
        safety_facts=StaticSafetyFacts(),
        protected_integrity_threshold=20.0,
        config=Stage6Config(
            version="stage6-runtime-test-v1",
            stage4=stage4._config,
            simulator=SimulatorConfig(
                version="stage6-runtime-simulator-v1",
                r_max=3,
                h_max=2,
            ),
            evaluation=Stage6EvaluationConfig(
                version="stage6-runtime-evaluation-v1",
                evidence_scale=10.0,
                beta=0.8,
                r_eff=3,
                h_eff=1,
            ),
            planning=Stage6PlanningConfig(
                version="stage6-runtime-planning-v1",
                option_ttl_steps=20,
                max_depth=2,
                revision_delta=0.1,
                setpoints=dict(stage4._config.value_needs.setpoints),
            ),
        ),
        equipment=equipment,
    )


class Stage6RuntimeTests(unittest.TestCase):
    def test_live_loop_uses_simulated_evidence_for_known_drink_transition(self) -> None:
        runtime = stage6_runtime(include_drink=True)

        result = runtime.run_step()

        self.assertEqual(result.execution_status, "applied")
        self.assertEqual(result.command_primitive, "boire")
        evaluations = [
            entry.causal_event
            for entry in runtime.journal.entries
            if entry.causal_event.get("kind") == "stage6_option_evaluation"
        ]
        drink = [
            event
            for event in evaluations
            if event.get("data", {}).get("simulated_value_status") == "computed"
        ]
        self.assertTrue(drink)
        self.assertTrue(
            any(event["data"]["simulated_value"] > 0.0 for event in drink)
        )
        self.assertTrue(
            all(event["data"]["r_eff"] == 3 for event in evaluations)
        )
        self.assertTrue(
            all(event["data"]["h_eff"] == 1 for event in evaluations)
        )

    def test_unseen_drink_transition_never_falls_back_to_stage4_substitution(self) -> None:
        runtime = stage6_runtime(include_drink=False)

        result = runtime.run_step()

        self.assertEqual(result.execution_status, "applied")
        self.assertEqual(result.command_primitive, "attendre")
        planning = [
            entry.causal_event
            for entry in runtime.journal.entries
            if entry.causal_event.get("kind") == "stage6_planning_result"
        ]
        self.assertTrue(planning)
        self.assertTrue(
            all(event["data"]["proposal_ref"] is None for event in planning)
        )
        self.assertFalse(
            any(
                entry.causal_event.get("kind") == "stage6_option_evaluation"
                and str(entry.causal_event.get("data", {}).get("option_ref", "")).startswith(
                    "option:"
                )
                for entry in runtime.journal.entries
            )
        )
        self.assertFalse(
            any(
                entry.causal_event.get("kind") == "competition_cycle"
                and any(
                    trace.get("evidence") not in (None, 0.0)
                    for trace in entry.causal_event.get("data", {}).get("traces", [])
                    if trace.get("option_ref") != "permanent:attendre"
                )
                for entry in runtime.journal.entries
            )
        )

    def test_lived_equipment_mismatch_emits_typed_prediction_error(self) -> None:
        runtime = stage6_runtime(
            include_drink=True,
            predicted_water_after=80.0,
        )

        first = runtime.run_step()
        self.assertEqual(first.command_primitive, "boire")

        runtime.run_step()

        errors = [
            entry.causal_event
            for entry in runtime.journal.entries
            if entry.causal_event.get("kind") == "prediction_error"
        ]
        self.assertTrue(errors)
        water = [
            event["data"]["error"]
            for event in errors
            if event["data"]["error"]["variable"] == "water"
        ]
        self.assertEqual(len(water), 1)
        self.assertEqual(water[0]["error_type"], "interoceptive")
        self.assertEqual(
            water[0]["model_target"],
            "equipment:E-v1-runtime-drink",
        )
        self.assertEqual(water[0]["predicted"], 80.0)
        self.assertEqual(water[0]["observed"], 60.0)
        self.assertEqual(water[0]["value"], 20.0)
        self.assertEqual(water[0]["nature"], "change")

    def test_equipment_is_not_a_mutable_causal_owner(self) -> None:
        runtime = stage6_runtime(include_drink=True)

        self.assertNotIn(
            "equipment",
            {owner.owner_id for owner in runtime.causal_owners},
        )


if __name__ == "__main__":
    unittest.main()
