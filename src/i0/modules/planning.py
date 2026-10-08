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
)
from i0.interfaces import PrimitiveCommand
from i0.modules.perception import PerceivedEntity


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

    @property
    def current_plan(self) -> Plan | None:
        return self._current_plan

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
        t_monde: int,
        cycle: int,
    ) -> OptionProposal | None:
        if goal is None:
            return None

        commands: list[PrimitiveCommand] = []
        target_key = goal.target

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

        option_id = (
            f"option:{goal.id}:{target_key}:{st_version}:{t_monde}:{cycle}"
        )
        plan_id = f"plan:{option_id}:v1"
        steps = tuple(
            PlanStep(
                index=index,
                command=command,
                preconditions=(),
                predicted_consequences=(),
                observation_window_steps=1,
            )
            for index, command in enumerate(commands)
        )
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
            state="proposed",
        )
        proposal = OptionProposal(
            option=option,
            plan=plan,
            preliminary_admissibility=None,
        )
        proposal.validate()
        self._current_plan = plan
        return proposal

    def first_command(self, proposal: OptionProposal) -> PrimitiveCommand:
        if proposal.plan is None or not proposal.plan.steps:
            raise ValueError("proposal has no executable plan")
        return proposal.plan.steps[0].command

    def export_causal_state(self) -> object:
        plan = self._current_plan
        return {
            "config_version": self._config.version,
            "current_plan": None if plan is None else {
                "id": plan.id,
                "option_ref": plan.option_ref,
                "version": plan.version,
                "steps": [
                    {
                        "index": step.index,
                        "command": step.command.as_dict(),
                        "preconditions": list(step.preconditions),
                        "observation_window_steps": step.observation_window_steps,
                    }
                    for step in plan.steps
                ],
                "goal_ref": plan.goal_ref,
                "budget_used_uc": plan.budget_used_uc,
                "status": plan.status,
                "st_version": plan.st_version,
            },
        }
