"""Stage-6 deterministic simulator-based planning.

Planning searches only over accessible SimulationState and the frozen simulator.
It never reads WorldBody, oracle, temperament, learned values, or accumulator
state. Search depth is bounded by the Stage-6 simulation horizon.

Spec: 8.11, 12.1-12.4, 20.3 Stage 6.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping

from i0.contracts import (
    Goal,
    MotiveRef,
    Option,
    OptionProposal,
    Plan,
    PlanStep,
    PredictedConsequence,
)
from i0.equipment import EquipmentPrediction, SimulationState
from i0.interfaces import PrimitiveCommand
from lab.determinism import canonical_causal_bytes, sha256_hex

from .simulator import Simulator


_PRIMITIVE_ORDER = {
    "se_deplacer": 0,
    "collecter": 1,
    "manger": 2,
    "boire": 3,
    "poser_une_pierre": 4,
    "fabriquer_outil": 5,
    "dormir": 6,
    "attendre": 7,
}
_DIRECTION_ORDER = {"north": 0, "south": 1, "east": 2, "west": 3}


@dataclass(frozen=True, slots=True)
class Stage6PlanningConfig:
    version: str
    option_ttl_steps: int
    max_depth: int
    revision_delta: float
    setpoints: Mapping[str, float]
    progressive_subgoals: bool = False
    progressive_evaluation_prefix: bool = False
    progressive_revalidate_on_new_capture: bool = False

    def validate(self) -> None:
        if not self.version:
            raise ValueError("Stage-6 planning config version must not be empty")
        if self.option_ttl_steps < 1:
            raise ValueError("option TTL must be >= 1")
        if type(self.progressive_subgoals) is not bool:
            raise ValueError('progressive_subgoals must be bool')
        if type(self.progressive_evaluation_prefix) is not bool:
            raise ValueError('progressive_evaluation_prefix must be bool')
        if type(self.progressive_revalidate_on_new_capture) is not bool:
            raise ValueError("progressive revalidation must be boolean")
        if self.progressive_revalidate_on_new_capture and not self.progressive_subgoals:
            raise ValueError("progressive revalidation requires progressive_subgoals")
        if self.progressive_evaluation_prefix and not self.progressive_subgoals:
            raise ValueError('prospective prefix requires progressive_subgoals')
        if self.max_depth < 1:
            raise ValueError("planning max depth must be >= 1")
        if self.revision_delta < 0.0:
            raise ValueError("Delta_plan must be non-negative")
        if set(self.setpoints) != {"energy", "food", "water", "integrity"}:
            raise ValueError("planning setpoints must cover the four MVP variables")


@dataclass(frozen=True, slots=True)
class PlanningSearchResult:
    status: str  # plan_found | partial_progress | incomplete_model | not_found_within_horizon
    commands: tuple[PrimitiveCommand, ...]
    predictions: tuple[EquipmentPrediction, ...]
    expanded_states: int
    unavailable_edges: int
    partial_progress: bool = False


@dataclass(frozen=True, slots=True)
class _Node:
    state: SimulationState
    commands: tuple[PrimitiveCommand, ...]
    predictions: tuple[EquipmentPrediction, ...]


class SimulatorPlanner:
    owner_id = "planning"

    def __init__(
        self,
        *,
        config: Stage6PlanningConfig,
        simulator: Simulator,
    ) -> None:
        config.validate()
        self._config = config
        self._simulator = simulator
        self._current_plan: Plan | None = None
        self._current_proposal: OptionProposal | None = None
        self._revision_required_option_ref: str | None = None
        # Read-only diagnostic of the *last actual* search, not persisted
        # cognitive state and not a second simulation.
        self._last_search_diagnostic: dict[str, object] | None = None

    @property
    def last_search_diagnostic(self) -> dict[str, object] | None:
        return (None if self._last_search_diagnostic is None
                else dict(self._last_search_diagnostic))

    def _record_search(self, result: PlanningSearchResult) -> PlanningSearchResult:
        if self._config.progressive_subgoals:
            self._last_search_diagnostic = {
                "status": result.status,
                "expanded_states": result.expanded_states,
                "unavailable_edges": result.unavailable_edges,
                "partial_progress": result.partial_progress,
            }
        return result

    def stale_partial_for_capture(self, *, t_monde: int) -> OptionProposal | None:
        """Only opt-in, physically old partial options require fresh search.

        The original time is encoded in the option's immutable expiry/TTL;
        this check never reads or guesses a physical outcome or secret state.
        """
        if not self._config.progressive_revalidate_on_new_capture:
            return None
        proposal = self._current_proposal
        if (proposal is None or proposal.option.success_condition != "step_completed"):
            return None
        authored_step = proposal.option.expires_at_step - self._config.option_ttl_steps
        return proposal if authored_step < t_monde else None

    @property
    def current_plan(self) -> Plan | None:
        return self._current_plan

    @property
    def current_proposal(self) -> OptionProposal | None:
        return self._current_proposal

    @property
    def revision_required_option_ref(self) -> str | None:
        return self._revision_required_option_ref

    def mark_plan_invalid(self, option_ref: str) -> None:
        if not option_ref:
            raise ValueError("option_ref must not be empty")
        self._revision_required_option_ref = option_ref
        self._current_plan = None
        self._current_proposal = None

    def confirm_revision_adopted(self, option_ref: str) -> None:
        if self._revision_required_option_ref == option_ref:
            self._revision_required_option_ref = None

    def invalidate_current(self) -> None:
        self._current_plan = None
        self._current_proposal = None

    @staticmethod
    def _state_key(state: SimulationState) -> str:
        return sha256_hex(canonical_causal_bytes(state.as_dict()))

    @staticmethod
    def _command_key(command: PrimitiveCommand) -> tuple[object, ...]:
        primitive_rank = _PRIMITIVE_ORDER[command.primitive]
        if command.primitive == "se_deplacer":
            return (
                primitive_rank,
                _DIRECTION_ORDER[str(command.parameters["direction"])],
            )
        if command.primitive in {"collecter", "manger"}:
            return (primitive_rank, str(command.parameters["target"]))
        return (primitive_rank,)

    @classmethod
    def candidate_commands(
        cls,
        state: SimulationState,
    ) -> tuple[PrimitiveCommand, ...]:
        commands: list[PrimitiveCommand] = []

        for neighbor in state.adjacent:
            if neighbor.passable:
                commands.append(
                    PrimitiveCommand(
                        "se_deplacer",
                        {"direction": neighbor.direction},
                    )
                )

        for resource in sorted(set(state.current_resources)):
            commands.append(
                PrimitiveCommand("collecter", {"target": resource})
            )

        for berry in ("berry_a", "berry_b"):
            if int(state.inventory.get(berry, 0)) > 0:
                commands.append(
                    PrimitiveCommand("manger", {"target": berry})
                )

        if state.current_water_source:
            commands.append(PrimitiveCommand("boire"))

        if int(state.inventory.get("stone", 0)) > 0:
            commands.append(PrimitiveCommand("poser_une_pierre"))

        if (
            int(state.inventory.get("wood", 0)) > 0
            and int(state.inventory.get("stone", 0)) > 0
        ):
            commands.append(PrimitiveCommand("fabriquer_outil"))

        commands.append(PrimitiveCommand("dormir"))
        commands.append(PrimitiveCommand("attendre"))

        return tuple(sorted(commands, key=cls._command_key))

    def search(
        self,
        *,
        initial_state: SimulationState,
        target: Callable[[SimulationState], bool],
        progress_measure: str | None = None,
    ) -> PlanningSearchResult:
        # Only a known goal measure can license an intermediate action.
        # A generic search (including shelter prediction) never fabricates
        # a partial goal from an unrelated bodily change.
        if progress_measure is not None and progress_measure not in (
            "energy", "food", "water", "integrity"
        ):
            raise ValueError("unsupported intermediate progress measure")
        self._last_search_diagnostic = None
        initial_state.validate()
        if target(initial_state):
            return self._record_search(PlanningSearchResult(
                status="plan_found",
                commands=(),
                predictions=(),
                expanded_states=0,
                unavailable_edges=0,
            ))

        queue: list[_Node] = [
            _Node(
                state=initial_state,
                commands=(),
                predictions=(),
            )
        ]
        visited = {self._state_key(initial_state)}
        expanded = 0
        unavailable = 0
        # The same bounded search may record a strictly goal-relevant
        # intermediate; goal-independent side effects are never progress.
        # Prefer measurable bodily gain over food inventory acquisition.
        candidate: tuple[tuple[PrimitiveCommand, ...],
                         tuple[EquipmentPrediction, ...]] | None = None
        candidate_rank = (0, 0.0)
        start_value = (
            float(initial_state.body[progress_measure])
            if progress_measure is not None else 0.0
        )
        start_berries = sum(
            int(initial_state.inventory.get(berry, 0))
            for berry in ("berry_a", "berry_b")
        )

        while queue:
            node = queue.pop(0)
            if len(node.commands) >= self._config.max_depth:
                continue
            expanded += 1

            for command in self.candidate_commands(node.state):
                result = self._simulator.rollout(
                    initial_state=node.state,
                    commands=(command,),
                    r_eff=1,
                    h_eff=1,
                )
                if not result.complete or not result.completed_rollouts:
                    unavailable += 1
                    continue

                rollout = result.completed_rollouts[0]
                if len(rollout.predictions) != 1:
                    unavailable += 1
                    continue
                prediction = rollout.predictions[0]
                next_state = prediction.next_state
                commands = node.commands + (command,)
                predictions = node.predictions + (prediction,)

                if target(next_state):
                    return self._record_search(PlanningSearchResult(
                        status="plan_found",
                        commands=commands,
                        predictions=predictions,
                        expanded_states=expanded,
                        unavailable_edges=unavailable,
                    ))

                if (
                    self._config.progressive_subgoals
                    and progress_measure is not None
                    and not prediction.terminal
                ):
                    bodily_gain = (
                        float(next_state.body[progress_measure]) - start_value
                    )
                    # Acquisition of edible resources is an intermediate
                    # capacity only for a *food* goal. Stock changes must
                    # never count as progress for water, energy or integrity.
                    new_berries = (
                        sum(int(next_state.inventory.get(berry, 0))
                            for berry in ("berry_a", "berry_b"))
                        - start_berries
                    ) if progress_measure == "food" else 0
                    rank = (
                        (2, bodily_gain) if bodily_gain > 0.0
                        else (1, 1.0) if new_berries > 0
                        else (0, 0.0)
                    )
                    # Stable first-in-BFS tie breaking; accumulating excess
                    # stock alone cannot win over a shorter acquisition.
                    if rank > candidate_rank:
                        candidate_rank = rank
                        candidate = (commands, predictions)

                key = self._state_key(next_state)
                if key in visited:
                    continue
                visited.add(key)
                queue.append(
                    _Node(
                        state=next_state,
                        commands=commands,
                        predictions=predictions,
                    )
                )

        if self._config.progressive_subgoals and candidate is not None:
            # Model incompleteness never authorizes a fabricated edge. Only
            # the first predicted action is offered; replan after new sensing.
            return self._record_search(PlanningSearchResult(
                status="partial_progress",
                commands=(candidate[0] if self._config.progressive_evaluation_prefix
                          else candidate[0][:1]),
                predictions=(candidate[1] if self._config.progressive_evaluation_prefix
                             else candidate[1][:1]),
                expanded_states=expanded,
                unavailable_edges=unavailable,
                partial_progress=True,
            ))
        return self._record_search(PlanningSearchResult(
            status=("incomplete_model" if unavailable > 0
                    else "not_found_within_horizon"),
            commands=(), predictions=(),
            expanded_states=expanded, unavailable_edges=unavailable,
        ))

    def plan_target(
        self,
        *,
        initial_state: SimulationState,
        target: str,
    ) -> PlanningSearchResult:
        if target == "shelter_here":
            predicate = lambda state: state.known_shelter_here
        else:
            raise ValueError(f"unsupported Stage-6 planning target: {target}")
        return self.search(initial_state=initial_state, target=predicate)

    def _goal_predicate(
        self,
        goal: Goal,
    ) -> Callable[[SimulationState], bool] | None:
        if goal.goal_type == "drink":
            threshold = float(self._config.setpoints["water"])
            return lambda state: float(state.body["water"]) >= threshold
        if goal.goal_type == "eat":
            threshold = float(self._config.setpoints["food"])
            return lambda state: float(state.body["food"]) >= threshold
        if goal.goal_type == "recover_energy":
            threshold = float(self._config.setpoints["energy"])
            return lambda state: float(state.body["energy"]) >= threshold
        if goal.goal_type == "restore_integrity":
            threshold = float(self._config.setpoints["integrity"])
            return lambda state: float(state.body["integrity"]) >= threshold
        return None

    @staticmethod
    def _predicted_consequences(
        prediction: EquipmentPrediction,
    ) -> tuple[PredictedConsequence, ...]:
        before = prediction.command
        del before  # command provenance is retained by the PlanStep itself.
        consequences: list[PredictedConsequence] = []
        for effect in prediction.effects:
            if effect.variable == "x":
                consequences.append(
                    PredictedConsequence(
                        variable="position_x",
                        value_or_delta=float(effect.after),
                        precision=0.0,
                    )
                )
            elif effect.variable == "y":
                consequences.append(
                    PredictedConsequence(
                        variable="position_y",
                        value_or_delta=float(effect.after),
                        precision=0.0,
                    )
                )
            elif effect.variable == "body" and isinstance(effect.after, Mapping):
                for name in ("energy", "food", "water", "integrity"):
                    if name in effect.after:
                        consequences.append(
                            PredictedConsequence(
                                variable=name,
                                value_or_delta=float(effect.after[name]),
                                precision=0.0,
                            )
                        )
        return tuple(consequences)

    def propose(
        self,
        *,
        goal: Goal | None,
        initial_state: SimulationState,
        st_version: str,
        retained_contribution_refs: frozenset[str],
        observation_ref_by_entity: Mapping[str, str],
        t_monde: int,
        cycle: int,
    ) -> OptionProposal | None:
        if goal is None:
            self.invalidate_current()
            if self._config.progressive_subgoals:
                self._last_search_diagnostic = {"status": "no_goal",
                    "expanded_states": 0, "unavailable_edges": 0,
                    "partial_progress": False}
            return None

        if (
            self._current_proposal is not None
            and self._current_proposal.option.goal_ref == goal.id
            and self._current_proposal.option.expires_at_step > t_monde
        ):
            if self._config.progressive_subgoals:
                self._last_search_diagnostic = {"status": "reused_cached",
                    "expanded_states": 0, "unavailable_edges": 0,
                    "partial_progress": (
                        self._current_proposal.option.success_condition
                        == "step_completed")}
            return self._current_proposal

        predicate = self._goal_predicate(goal)
        if predicate is None:
            return None

        result = self.search(
            initial_state=initial_state,
            target=predicate,
            progress_measure=(
                goal.principal_measure
                if self._config.progressive_subgoals else None
            ),
        )
        if result.status not in ("plan_found", "partial_progress") or not result.commands:
            return None

        grounding = {
            ref
            for ref in observation_ref_by_entity.values()
            if ref in retained_contribution_refs
        }
        if (
            goal.justification_ref is not None
            and goal.justification_ref in retained_contribution_refs
        ):
            grounding.add(goal.justification_ref)

        signature_tail = result.commands[-1].primitive
        suffix = (":progress:prefix" if result.partial_progress
                  and self._config.progressive_evaluation_prefix else
                  ":progress" if result.partial_progress else "")
        option_id = f"option:{goal.id}:sim:{signature_tail}{suffix}"
        plan_id = f"plan:{option_id}:v1"
        steps = tuple(
            PlanStep(
                index=index,
                command=command,
                preconditions=(),
                predicted_consequences=self._predicted_consequences(prediction),
                observation_window_steps=1,
            )
            for index, (command, prediction) in enumerate(
                zip(result.commands, result.predictions)
            )
        )
        plan = Plan(
            id=plan_id,
            option_ref=option_id,
            version="1",
            steps=steps,
            goal_ref=goal.id,
            budget_used_uc=result.expanded_states,
            status="valid",
            st_version=st_version,
        )
        option = Option(
            id=option_id,
            version="1",
            type="primitive" if len(steps) == 1 else "composite",
            learning_signature=(
                f"{goal.goal_type}:sim:{signature_tail}"
            ),
            preconditions=(),
            success_condition=("step_completed" if result.partial_progress
                               else goal.satisfaction_condition),
            failure_condition="plan_step_failed",
            invalidation_condition="goal_or_context_invalid",
            goal_ref=goal.id,
            motive_ref=MotiveRef(type="active_goal", id=goal.id),
            plan_ref=plan.id,
            founding_st_version=st_version,
            expires_at_step=t_monde + self._config.option_ttl_steps,
            provenance="planning",
            grounding_contribution_refs=tuple(sorted(grounding)),
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

    def export_causal_state(self) -> object:
        from i0.serde import encode_proposal

        return {
            "config_version": self._config.version,
            "revision_required_option_ref": self._revision_required_option_ref,
            "current_proposal": (
                None
                if self._current_proposal is None
                else encode_proposal(self._current_proposal)
            ),
        }

    def restore_causal_state(self, state: object) -> None:
        from i0.serde import decode_proposal

        if not isinstance(state, Mapping):
            raise ValueError("Stage-6 Planning state must be a mapping")
        if state.get("config_version") != self._config.version:
            raise ValueError("Stage-6 Planning config version mismatch")
        raw_revision = state.get("revision_required_option_ref")
        if raw_revision is not None and not isinstance(raw_revision, str):
            raise ValueError("invalid Stage-6 revision-required option ref")
        self._revision_required_option_ref = raw_revision
        raw = state.get("current_proposal")
        if raw is None:
            self.invalidate_current()
            return
        if not isinstance(raw, Mapping):
            raise ValueError("invalid Stage-6 Planning proposal state")
        proposal = decode_proposal(raw)
        self._current_proposal = proposal
        self._current_plan = proposal.plan
