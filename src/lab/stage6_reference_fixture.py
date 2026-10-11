"""Stage-6 deterministic compatibility fixture.

The fixture exercises live simulator-based planning and E_a^sim for one full
300-step day. Its equipment is an exact software-reference table trained only
on the accessible states required by this controlled trajectory.

These values are compatibility fixtures, not campaign calibration.

Spec: 12, 20.3 Stage 6.
"""

from __future__ import annotations

from i0.equipment import train_exact_transition_table
from i0.interfaces import PrimitiveCommand
from i0.modules import StaticSafetyFacts
from i0.modules.simulator import SimulatorConfig
from i0.modules.stage6_evaluator import Stage6EvaluationConfig
from i0.modules.stage6_planning import Stage6PlanningConfig

from .equipment_corpus import EquipmentCorpusRecorder
from .safety_protocol import SafetyProtocolConfig
from .stage4_reference_fixture import build_stage4_reference_runtime
from .stage6_runtime import Stage6Config, Stage6Runtime
from .world import Position, WorldBody, WorldLayout


def build_stage6_reference_runtime(*, autonomous_mortal: bool = False) -> Stage6Runtime:
    stage4 = build_stage4_reference_runtime(autonomous_mortal=autonomous_mortal)
    world_config = stage4.world.config
    layout = WorldLayout(
        water_sources=frozenset({Position(2, 2)}),
    )

    training_world = WorldBody(
        config=world_config,
        layout=layout,
    )
    recorder = EquipmentCorpusRecorder(
        corpus_version="stage6-runtime-reference-corpus-v1",
    )

    # Initial thirsty state: waiting is known but carries no homeostatic gain.
    recorder.record_transition(
        world=training_world,
        t_monde=1,
        family="wait",
        command=PrimitiveCommand("attendre"),
    )

    # The one useful transition at birth.
    recorder.record_transition(
        world=training_world,
        t_monde=2,
        family="drinking",
        command=PrimitiveCommand("boire"),
    )

    # Stable post-drink state in daytime and nighttime contexts.
    recorder.record_transition(
        world=training_world,
        t_monde=3,
        family="wait",
        command=PrimitiveCommand("attendre"),
    )
    recorder.record_transition(
        world=training_world,
        t_monde=201,
        family="wait",
        command=PrimitiveCommand("attendre"),
    )

    equipment = train_exact_transition_table(
        corpus=recorder.build(),
        equipment_version="E-v1-stage6-reference",
    )

    return Stage6Runtime(
        world_config=world_config,
        layout=layout,
        safety_config=SafetyProtocolConfig(
            version="stage6-reference-safety-v1",
            lethal_max=2,
            mode="campaign",
        ),
        safety_facts=StaticSafetyFacts(),
        protected_integrity_threshold=20.0,
        config=Stage6Config(
            version="stage6-reference-v1",
            stage4=stage4._config,
            simulator=SimulatorConfig(
                version="stage6-reference-simulator-v1",
                r_max=3,
                h_max=2,
            ),
            evaluation=Stage6EvaluationConfig(
                version="stage6-reference-evaluation-v1",
                evidence_scale=10.0,
                beta=0.8,
                r_eff=3,
                h_eff=1,
            ),
            planning=Stage6PlanningConfig(
                version="stage6-reference-planning-v1",
                option_ttl_steps=20,
                max_depth=2,
                revision_delta=0.1,
                setpoints=dict(stage4._config.value_needs.setpoints),
            ),
        ),
        equipment=equipment,
        autonomous_mortal=autonomous_mortal,
    )
