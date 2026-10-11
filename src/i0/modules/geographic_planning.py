"""Stage-11 Planning adapter for an Exploration-designated adjacent frontier.

No target invention, no hidden map, no direct action sender. Every proposed
motion is validated by an actual bounded Simulator rollout from the single
Perception-derived SimulationState. Action Control retains the last veto.
"""
from __future__ import annotations

from i0.contracts import MotiveRef, Option, OptionProposal, Plan, PlanStep
from i0.equipment import SimulationState
from i0.interfaces import PrimitiveCommand

from .geographic_exploration import GeographicTarget
from .simulator import Simulator
from .stage6_planning import SimulatorPlanner


def propose_geographic_frontier(
    *, target: GeographicTarget, initial_state: SimulationState,
    simulator: Simulator, st_version: str, t_monde: int, ttl_steps: int,
) -> OptionProposal | None:
    target.validate()
    initial_state.validate()
    if (not st_version or type(t_monde) is not int or t_monde < 1
        or type(ttl_steps) is not int or ttl_steps < 1
        or target.source_t_monde != t_monde
        or target.origin != (initial_state.x, initial_state.y)):
        return None
    matching = [
        cell for cell in initial_state.adjacent
        if cell.direction == target.direction
    ]
    if (len(matching) != 1 or matching[0].passable is not True
        or matching[0].creature is True
        or (matching[0].x, matching[0].y) != target.destination):
        return None
    command = PrimitiveCommand(
        "se_deplacer", {"direction": target.direction},
    )
    predicted = simulator.rollout(
        initial_state=initial_state, commands=(command,), r_eff=1, h_eff=1,
    )
    if not predicted.complete or len(predicted.completed_rollouts) != 1:
        return None
    predictions = predicted.completed_rollouts[0].predictions
    if (len(predictions) != 1
        or (predictions[0].next_state.x, predictions[0].next_state.y)
        != target.destination):
        return None
    consequences = SimulatorPlanner._predicted_consequences(predictions[0])
    if not {"position_x", "position_y"}.issubset({
        consequence.variable for consequence in consequences
    }):
        return None
    option_id = (
        f"option:geographic:{target.ref}:t{target.source_t_monde}"
    )
    plan_id = f"plan:{option_id}:v1"
    plan = Plan(
        id=plan_id, option_ref=option_id, version="1",
        steps=(PlanStep(
            index=0, command=command,
            preconditions=("adjacent_passable",),
            predicted_consequences=consequences,
            observation_window_steps=1,
        ),),
        goal_ref=None, budget_used_uc=1, status="valid",
        st_version=st_version,
    )
    option = Option(
        id=option_id, version="1", type="primitive",
        learning_signature=(
            f"geographic_frontier:{target.destination[0]}:{target.destination[1]}"
        ),
        preconditions=("adjacent_passable",),
        success_condition="target_position_observed",
        failure_condition="target_position_not_observed",
        invalidation_condition="target_visited_or_context_changed",
        motive_ref=MotiveRef(type="cible_exploration", id=target.ref),
        founding_st_version=st_version,
        expires_at_step=t_monde + ttl_steps,
        provenance="exploration", goal_ref=None,
        plan_ref=plan_id,
        state="proposed",
    )
    proposal = OptionProposal(option=option, plan=plan)
    proposal.validate()
    return proposal
