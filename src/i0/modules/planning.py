"""Minimal Stage-4 greedy E-0 planner.

The planner reads only cognitive state supplied to it: active goal, founding
S_t version, current perceived position, and Perception's last-known symbolic
entity map. It never reads the world or oracle.

Spec: 8.11, 20.4 Stage 4.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from i0.contracts import (
    Goal,
    MotiveRef,
    Option,
    OptionProposal,
    Plan,
    PlanStep,
    PredictedConsequence,
)
from i0.interfaces import PrimitiveCommand
from i0.modules.perception import PerceivedEntity
from i0.serde import decode_proposal, encode_proposal


@dataclass(frozen=True, slots=True)
class PlanningConfig:
    version: str
    option_ttl_steps: int

    def validate(self) -> None:
        if not self.version:
            raise ValueError("planning config version must not be empty")
        if self.option_ttl_steps < 1:
            raise ValueError("option TTL must be >= 1")


class GreedyPlannerE0:
    owner_id = "planning"

    def __init__(self, config: PlanningConfig) -> None:
        config.validate()
        self._config = config
        self._current_plan: Plan | None = None
        self._current_proposal: OptionProposal | None = None

    @property
    def current_plan(self) -> Plan | None:
        return self._current_plan

    @property
    def current_proposal(self) -> OptionProposal | None:
        return self._current_proposal

    def invalidate_current(self) -> None:
        self._current_plan = None
        self._current_proposal = None

    @staticmethod
    def _movement_steps(
        *,
        start: tuple[int, int],
        target: tuple[int, int],
    ) -> list[PrimitiveCommand]:
        x, y = start
        tx, ty = target
        commands: list[PrimitiveCommand] = []
        while x < tx:
            commands.append(PrimitiveCommand("se_deplacer", {"direction": "east"}))
            x += 1
        while x > tx:
            commands.append(PrimitiveCommand("se_deplacer", {"direction": "west"}))
            x -= 1
        while y < ty:
            commands.append(PrimitiveCommand("se_deplacer", {"direction": "south"}))
            y += 1
        while y > ty:
            commands.append(PrimitiveCommand("se_deplacer", {"direction": "north"}))
            y -= 1
        return commands

    @staticmethod
    def _nearest(
        entities: Mapping[str, PerceivedEntity],
        *,
        types: set[str],
        position: tuple[int, int],
    ) -> PerceivedEntity | None:
        candidates = [
            entity
            for entity in entities.values()
            if entity.entity_type in types
        ]
        if not candidates:
            return None
        x, y = position
        candidates.sort(
            key=lambda entity: (
                abs(entity.x - x) + abs(entity.y - y),
                entity.entity_type,
                entity.entity_id,
            )
        )
        return candidates[0]

    def propose(
        self,
        *,
        goal: Goal | None,
        st_version: str,
        position: tuple[int, int],
        known_entities: Mapping[str, PerceivedEntity],
        observation_ref_by_entity: Mapping[str, str],
        retained_contribution_refs: frozenset[str],
        t_monde: int,
        cycle: int,
    ) -> OptionProposal | None:
        if goal is None:
            self.invalidate_current()
            return None

        if (
            self._current_proposal is not None
            and self._current_proposal.option.goal_ref == goal.id
            and self._current_proposal.option.expires_at_step > t_monde
        ):
            return self._current_proposal

        commands: list[PrimitiveCommand] = []
        target_key = goal.target
        grounding_refs: list[str] = []
        if (
            goal.justification_ref is not None
            and goal.justification_ref in retained_contribution_refs
        ):
            grounding_refs.append(goal.justification_ref)

        if goal.goal_type == "drink":
            target = self._nearest(
                known_entities,
                types={"water_source"},
                position=position,
            )
            if target is None:
                return None
            commands.extend(
                self._movement_steps(
                    start=position,
                    target=(target.x, target.y),
                )
            )
            target_ref = observation_ref_by_entity.get(target.entity_id)
            if target_ref is None or target_ref not in retained_contribution_refs:
                return None
            grounding_refs.append(target_ref)
            commands.append(PrimitiveCommand("boire"))
            target_key = target.entity_id

        elif goal.goal_type == "eat":
            target = self._nearest(
                known_entities,
                types={"berry_a", "berry_b"},
                position=position,
            )
            if target is None:
                return None
            commands.extend(
                self._movement_steps(
                    start=position,
                    target=(target.x, target.y),
                )
            )
            target_ref = observation_ref_by_entity.get(target.entity_id)
            if target_ref is None or target_ref not in retained_contribution_refs:
                return None
            grounding_refs.append(target_ref)
            commands.append(
                PrimitiveCommand("collecter", {"target": target.entity_type})
            )
            commands.append(
                PrimitiveCommand("manger", {"target": target.entity_type})
            )
            target_key = target.entity_id

        elif goal.goal_type == "recover_energy":
            commands.append(PrimitiveCommand("dormir"))

        elif goal.goal_type == "restore_integrity":
            shelter = self._nearest(
                known_entities,
                types={"shelter"},
                position=position,
            )
            if shelter is not None:
                commands.extend(
                    self._movement_steps(
                        start=position,
                        target=(shelter.x, shelter.y),
                    )
                )
            commands.append(PrimitiveCommand("attendre"))
            target_key = shelter.entity_id if shelter is not None else "rest"

        else:
            return None

        option_id = f"option:{goal.id}:{target_key}"
        plan_id = f"plan:{option_id}:v1"
        predicted_steps: list[PlanStep] = []
        predicted_x, predicted_y = position
        for index, command in enumerate(commands):
            consequences: tuple[PredictedConsequence, ...] = ()
            if command.primitive == "se_deplacer":
                direction = str(command.parameters["direction"])
                if direction == "east":
                    predicted_x += 1
                elif direction == "west":
                    predicted_x -= 1
                elif direction == "south":
                    predicted_y += 1
                elif direction == "north":
                    predicted_y -= 1
                consequences = (
                    PredictedConsequence(
                        variable="position_x",
                        value_or_delta=float(predicted_x),
                        precision=0.0,
                    ),
                    PredictedConsequence(
                        variable="position_y",
                        value_or_delta=float(predicted_y),
                        precision=0.0,
                    ),
                )
            predicted_steps.append(
                PlanStep(
                    index=index,
                    command=command,
                    preconditions=(),
                    predicted_consequences=consequences,
                    observation_window_steps=1,
                )
            )
        steps = tuple(predicted_steps)
        plan = Plan(
            id=plan_id,
            option_ref=option_id,
            version="1",
            steps=steps,
            goal_ref=goal.id,
            budget_used_uc=len(steps),
            status="valid",
            st_version=st_version,
        )
        option = Option(
            id=option_id,
            version="1",
            type="primitive" if len(steps) == 1 else "composite",
            learning_signature=(
                f"{goal.goal_type}:{target_key}:{commands[-1].primitive}"
            ),
            preconditions=(),
            success_condition=goal.satisfaction_condition,
            failure_condition="plan_step_failed",
            invalidation_condition="goal_or_target_invalid",
            goal_ref=goal.id,
            motive_ref=MotiveRef(type="active_goal", id=goal.id),
            plan_ref=plan_id,
            founding_st_version=st_version,
            expires_at_step=t_monde + self._config.option_ttl_steps,
            provenance="planning",
            grounding_contribution_refs=tuple(sorted(set(grounding_refs))),
            state="proposed",
        )
        proposal = OptionProposal(
            option=option,
            plan=plan,
            preliminary_admissibility=None,
        )
        proposal.validate()
        self._current_plan = plan
        self._current_proposal = proposal
        return proposal

    def first_command(self, proposal: OptionProposal) -> PrimitiveCommand:
        if proposal.plan is None or not proposal.plan.steps:
            raise ValueError("proposal has no executable plan")
        return proposal.plan.steps[0].command

    def export_causal_state(self) -> object:
        return {
            "config_version": self._config.version,
            "current_proposal": (
                None
                if self._current_proposal is None
                else encode_proposal(self._current_proposal)
            ),
        }

    def restore_causal_state(self, state: object) -> None:
        if not isinstance(state, Mapping):
            raise ValueError("Planning state must be a mapping")
        if state.get("config_version") != self._config.version:
            raise ValueError("Planning config version mismatch")
        raw = state.get("current_proposal")
        if raw is None:
            self.invalidate_current()
            return
        if not isinstance(raw, Mapping):
            raise ValueError("invalid Planning proposal state")
        proposal = decode_proposal(raw)
        self._current_proposal = proposal
        self._current_plan = proposal.plan
