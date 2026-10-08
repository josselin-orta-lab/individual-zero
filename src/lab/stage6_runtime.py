"""Integrated Stage-6 runtime: live simulated evidence over Stage 4.

Stage 6 keeps the completed Stage-4 loop and replaces only the evidence source
used by Competition. Every candidate in a cycle is evaluated from the same
accessible SimulationState and the same effective (R_eff, H_eff) budget.

The greedy E-0 planner is intentionally retained in this first Stage-6
sub-gate. Simulator-based multi-step planning replaces it in the next sub-gate.

Spec: 8.5, 8.11, 12.1-12.5, 20.3 Stage 6, DC-01.
"""

from __future__ import annotations

from dataclasses import dataclass

from i0.equipment import EquipmentModel
from i0.modules import StaticSafetyFacts
from i0.modules.simulator import Simulator, SimulatorConfig, state_from_capture
from i0.modules.stage6_evaluator import (
    Stage6EvaluationConfig,
    Stage6OptionEvaluator,
)
from i0.modules.stage6_planning import (
    SimulatorPlanner,
    Stage6PlanningConfig,
)

from .safety_protocol import SafetyProtocolConfig
from .stage4_runtime import Stage4Config, Stage4Runtime
from .world import WorldLayout, WorldPhysicsConfig


@dataclass(frozen=True, slots=True)
class Stage6Config:
    version: str
    stage4: Stage4Config
    simulator: SimulatorConfig
    evaluation: Stage6EvaluationConfig
    planning: Stage6PlanningConfig

    def validate(self) -> None:
        if not self.version:
            raise ValueError("Stage 6 config version must not be empty")
        self.stage4.validate()
        self.simulator.validate()
        self.evaluation.validate()
        self.planning.validate()
        if self.evaluation.r_eff > self.simulator.r_max:
            raise ValueError("R_eff must not exceed R_max")
        if self.evaluation.h_eff > self.simulator.h_max:
            raise ValueError("H_eff must not exceed H_max")
        if self.planning.max_depth > self.simulator.h_max:
            raise ValueError("planning max_depth must not exceed H_max")


class Stage6Runtime(Stage4Runtime):
    """Stage-4 loop with typed E_a^sim evidence from frozen equipment."""

    individual_id = "i0-stage6"

    def __init__(
        self,
        *,
        world_config: WorldPhysicsConfig,
        layout: WorldLayout,
        safety_config: SafetyProtocolConfig,
        safety_facts: StaticSafetyFacts,
        protected_integrity_threshold: float,
        config: Stage6Config,
        equipment: EquipmentModel,
    ) -> None:
        config.validate()
        self._stage6_config = config
        self.equipment = equipment
        self.simulator = Simulator(
            config=config.simulator,
            equipment=equipment,
        )
        self.option_evaluator = Stage6OptionEvaluator(
            config=config.evaluation,
            simulator=self.simulator,
            needs_config=config.stage4.value_needs,
        )

        super().__init__(
            world_config=world_config,
            layout=layout,
            safety_config=safety_config,
            safety_facts=safety_facts,
            protected_integrity_threshold=protected_integrity_threshold,
            config=config.stage4,
        )
        self.planning = SimulatorPlanner(
            config=config.planning,
            simulator=self.simulator,
        )

    @property
    def stage6_config(self) -> Stage6Config:
        return self._stage6_config

    @property
    def equipment_version(self) -> str:
        return self.equipment.version

    def _propose_for_cycle(
        self,
        *,
        capture,
        goal_for_planning,
        st_before_cycle,
        cycle: int,
    ):
        initial_state = state_from_capture(
            capture=capture,
            is_night=self.world.is_night(capture.t_monde),
        )
        proposal = self.planning.propose(
            goal=goal_for_planning,
            initial_state=initial_state,
            st_version=st_before_cycle.version,
            retained_contribution_refs=frozenset(
                element.contribution_ref
                for element in st_before_cycle.competitive
            ),
            observation_ref_by_entity=(
                self.stage3.perception.observation_ref_by_entity
            ),
            t_monde=capture.t_monde,
            cycle=cycle,
        )
        self._write(
            kind="stage6_planning_result",
            cycle=cycle,
            data={
                "goal_ref": goal_for_planning.id,
                "proposal_ref": (
                    None if proposal is None else proposal.option.id
                ),
                "equipment_version": self.equipment.version,
                "planning_version": self._stage6_config.planning.version,
            },
        )
        return proposal

    def _evaluate_competition_cycle(
        self,
        *,
        capture,
        cycle: int,
    ):
        initial_state = state_from_capture(
            capture=capture,
            is_night=self.world.is_night(capture.t_monde),
        )

        evidence_inputs = {}
        for proposal in self.competition.candidate_proposals:
            supplied = self.option_evaluator.evaluate(
                proposal=proposal,
                initial_state=initial_state,
                cycle=cycle,
                t_monde=capture.t_monde,
            )
            evidence_inputs[proposal.option.id] = supplied
            evaluation = supplied.evaluation
            self._write(
                kind="stage6_option_evaluation",
                cycle=cycle,
                data={
                    "option_ref": proposal.option.id,
                    "status": evaluation.status,
                    "simulated_value_status": (
                        evaluation.simulated_value_status
                    ),
                    "simulated_value": evaluation.simulated_value,
                    "evidence": supplied.evidence,
                    "equipment_version": self.equipment.version,
                    "r_eff": self._stage6_config.evaluation.r_eff,
                    "h_eff": self._stage6_config.evaluation.h_eff,
                },
            )

        return self.competition.evaluate(
            cycle=cycle,
            t_monde=capture.t_monde,
            evidence_inputs=evidence_inputs,
        )
