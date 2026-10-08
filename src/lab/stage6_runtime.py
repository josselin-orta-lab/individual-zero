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

from i0.contracts import PredictionError
from i0.equipment import EquipmentModel
from i0.modules import Admissibility, PreparedCommand, StaticSafetyFacts
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
        self._revision_initial_state = None
        self._revision_capture = None
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

    def _handle_agency_comparison(
        self,
        *,
        capture,
        comparison,
    ) -> None:
        engaged_plan_failed = (
            comparison.status == "nonconforming"
            and comparison.option_ref is not None
            and self.competition.is_engaged(comparison.option_ref)
        )
        if engaged_plan_failed:
            # DC-17: the realization failed, not the pursued option or goal.
            self._write(
                kind="agency_comparison",
                data=self._comparison_as_dict(comparison),
            )
            option_ref = str(comparison.option_ref)
            self.planning.mark_plan_invalid(option_ref)
            self.stage3.control.clear_option_step(option_ref)
            self._write(
                kind="plan_revision_requested",
                data={
                    "option_ref": option_ref,
                    "reason": "failed_step",
                    "active_goal_ref": (
                        None
                        if self.goal_manager.active_goal is None
                        else self.goal_manager.active_goal.id
                    ),
                },
            )
        else:
            super()._handle_agency_comparison(
                capture=capture,
                comparison=comparison,
            )

        for index, effect in enumerate(comparison.effects):
            status = effect.get("status")
            if status not in {"nonconforming", "expected_effect_missing"}:
                continue

            variable = str(effect.get("variable", "unspecified"))
            predicted_raw = effect.get("predicted")
            observed_raw = effect.get("observed")
            precision_raw = effect.get("precision")
            predicted = (
                None if predicted_raw is None else float(predicted_raw)
            )
            observed = (
                None if observed_raw is None else float(observed_raw)
            )
            precision = (
                None if precision_raw is None else float(precision_raw)
            )
            magnitude = (
                None
                if predicted is None or observed is None
                else abs(observed - predicted)
            )
            error_type = (
                "interoceptive"
                if variable in {"energy", "food", "water", "integrity"}
                else "action"
            )
            error = PredictionError(
                error_type=error_type,
                source="agency_comparator",
                model_target=f"equipment:{self.equipment.version}",
                variable=variable,
                predicted=predicted,
                observed=observed,
                value=magnitude,
                precision=precision,
                nature="change",
                t_monde=capture.t_monde,
                episode_ref=None,
            )
            error.validate()
            self._write(
                kind="prediction_error",
                data={
                    "index": index,
                    "option_ref": comparison.option_ref,
                    "sent_t_monde": comparison.sent_t_monde,
                    "error": error.as_dict(),
                },
            )

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
        self._revision_initial_state = initial_state
        self._revision_capture = capture
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

    def _first_step_admissible(self, proposal) -> bool:
        if proposal.plan is None or not proposal.plan.steps:
            return False
        if self._revision_capture is None:
            return False
        step = proposal.plan.steps[0]
        prepared = PreparedCommand(
            command=step.command,
            source="decision",
            option_ref=proposal.option.id,
            st_version_ref=proposal.option.founding_st_version,
            grounding_contribution_refs=(
                proposal.option.grounding_contribution_refs
            ),
            predicted_consequences=step.predicted_consequences,
            observation_window_steps=step.observation_window_steps,
        )
        status = self.stage3.control.verifier_admissibilite(
            capture=self._revision_capture,
            prepared=prepared,
        )
        return status is not Admissibility.INADMISSIBLE

    def _compare_revision_value(
        self,
        *,
        before,
        after,
        cycle: int,
        t_monde: int,
    ):
        state = self._revision_initial_state
        if state is None:
            return None
        return self.option_evaluator.compare_revised_plans(
            old_proposal=before,
            new_proposal=after,
            initial_state=state,
            delta_plan=self._stage6_config.planning.revision_delta,
            cycle=cycle,
            t_monde=t_monde,
        )

    def _register_option_proposal(
        self,
        *,
        proposal,
        active_goal_id: str | None,
        t_monde: int,
        cycle: int,
    ) -> bool:
        before = self.competition.proposal_for(proposal.option.id)
        material = (
            before is not None
            and self.competition.material_plan_change(before, proposal)
        )
        engaged = self.competition.is_engaged(proposal.option.id)

        if material and engaged:
            invalid_revision = (
                self.planning.revision_required_option_ref
                == proposal.option.id
            )
            comparison = (
                None
                if invalid_revision
                else self._compare_revision_value(
                    before=before,
                    after=proposal,
                    cycle=cycle,
                    t_monde=t_monde,
                )
            )
            value_revision = (
                comparison is not None
                and comparison.status == "improved"
            )
            if not invalid_revision and not value_revision:
                self._write(
                    kind="revised_plan_rejected",
                    cycle=cycle,
                    data={
                        "option_ref": proposal.option.id,
                        "reason": (
                            "comparison_unavailable"
                            if comparison is None
                            or comparison.status == "unavailable"
                            else "delta_plan_not_reached"
                        ),
                        "old_value": (
                            None if comparison is None else comparison.old_value
                        ),
                        "new_value": (
                            None if comparison is None else comparison.new_value
                        ),
                        "delta": (
                            None if comparison is None else comparison.delta
                        ),
                        "delta_plan": self._stage6_config.planning.revision_delta,
                        "r_eff": (
                            None if comparison is None else comparison.r_eff
                        ),
                        "h_eff": (
                            None if comparison is None else comparison.h_eff
                        ),
                    },
                )
                return False
            if not self._first_step_admissible(proposal):
                self._write(
                    kind="revised_plan_rejected",
                    cycle=cycle,
                    data={
                        "option_ref": proposal.option.id,
                        "reason": "first_step_inadmissible",
                    },
                )
                return False

        registered = super()._register_option_proposal(
            proposal=proposal,
            active_goal_id=active_goal_id,
            t_monde=t_monde,
            cycle=cycle,
        )
        if not registered or before is None or not material:
            return registered

        if engaged:
            self.stage3.control.clear_option_step(proposal.option.id)
            self.planning.confirm_revision_adopted(proposal.option.id)
            self._write(
                kind="revised_plan_adopted",
                cycle=cycle,
                data={
                    "option_ref": proposal.option.id,
                    "goal_ref": proposal.option.goal_ref,
                    "motive_ref": {
                        "type": proposal.option.motive_ref.type,
                        "id": proposal.option.motive_ref.id,
                    },
                    "reason": (
                        "invalid_active_plan"
                        if invalid_revision
                        else "value_improvement"
                    ),
                    "delta_plan": self._stage6_config.planning.revision_delta,
                },
            )
        else:
            self._write(
                kind="nonengaged_plan_replaced",
                cycle=cycle,
                data={
                    "option_ref": proposal.option.id,
                    "accumulator_after": self.competition.accumulator_for(
                        proposal.option.id
                    ),
                },
            )
        return registered

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
