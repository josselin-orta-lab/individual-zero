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
from .observed_frontier_routing import GeographicTransitTarget
from .spatial_memory import SpatialReturnTarget, LivedSiteReturnTarget
from .simulator import Simulator
from .stage6_planning import SimulatorPlanner


def _perceptually_grounded_step(*, target, initial_state, simulator):
    """Common local-simulator validation for ordinary and transit proposals."""
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
    # Frozen E-v1 is an exact corpus table: an unseen input is UNKNOWN, not
    # evidence that a physically perceived adjacent step cannot be attempted.
    # As at Stage 9, a local one-step exploratory plan may remain indeterminate
    # without inventing numeric predicted consequences. A conflicting learned
    # causal correction, invalid rollout or other model failure is NOT ignored.
    if not predicted.complete:
        if predicted.reason != "equipment_input_unseen":
            return None
        consequences = ()
    else:
        if len(predicted.completed_rollouts) != 1:
            return None
        predictions = predicted.completed_rollouts[0].predictions
        if (len(predictions) != 1
            or (predictions[0].next_state.x, predictions[0].next_state.y)
            != target.destination):
            return None
        consequences = SimulatorPlanner._predicted_consequences(predictions[0])
        # The exact Equipment corpus records only *changed* dimensions.
        # A north/south move may predict y alone, not a redundant x value.
        # Require an explicit correct forecast of the changed axis and reject
        # any contradictory forecast of the stationary axis. Never fabricate
        # that stationary-axis numeric consequence just to satisfy P-47.
        expected = {
            "position_x": target.destination[0],
            "position_y": target.destination[1],
        }
        predicted_positions = {
            consequence.variable: consequence.value_or_delta
            for consequence in consequences
            if consequence.variable in expected
        }
        changed_axis = (
            "position_y" if target.direction in ("north", "south")
            else "position_x"
        )
        if (
            predicted_positions.get(changed_axis) != expected[changed_axis]
            or any(value != expected[name]
                   for name, value in predicted_positions.items())
        ):
            return None
    return consequences


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
    consequences = _perceptually_grounded_step(
        target=target, initial_state=initial_state, simulator=simulator,
    )
    if consequences is None:
        return None
    command = PrimitiveCommand(
        "se_deplacer", {"direction": target.direction},
    )
    option_id = (
        f"option:geographic:{target.ref}"
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
    proposal = OptionProposal(
        option=option, plan=plan,
        preliminary_admissibility=(
            "indeterminate" if not consequences else None
        ),
    )
    proposal.validate()
    return proposal


def propose_geographic_transit(
    *, target: GeographicTransitTarget, initial_state: SimulationState,
    simulator: Simulator, st_version: str, t_monde: int, ttl_steps: int,
) -> OptionProposal | None:
    """One real adjacent transit hop toward a physically witnessed frontier.

    Transit is NOT a fresh geographic visit and is never dispatched here.
    Ordinary Competition and canonical Action Control keep their authority.
    """
    target.validate()
    initial_state.validate()
    if (not st_version or type(t_monde) is not int or t_monde < 1
        or type(ttl_steps) is not int or ttl_steps < 1
        or target.source_t_monde != t_monde
        or target.origin != (initial_state.x, initial_state.y)):
        return None
    consequences = _perceptually_grounded_step(
        target=target, initial_state=initial_state, simulator=simulator,
    )
    if consequences is None:
        return None
    option_id = f"option:geographic:{target.ref}"
    plan_id = f"plan:{option_id}:v1"
    plan = Plan(
        id=plan_id, option_ref=option_id, version="1",
        steps=(PlanStep(
            index=0, command=PrimitiveCommand(
                "se_deplacer", {"direction": target.direction},
            ),
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
            f"geographic_transit:{target.observed_frontier[0]}:"
            f"{target.observed_frontier[1]}:via:"
            f"{target.destination[0]}:{target.destination[1]}"
        ),
        preconditions=("adjacent_passable",),
        success_condition="target_position_observed",
        failure_condition="target_position_not_observed",
        invalidation_condition="route_objective_visited_or_context_changed",
        motive_ref=MotiveRef(type="cible_exploration", id=target.ref),
        founding_st_version=st_version,
        expires_at_step=t_monde + ttl_steps,
        provenance="exploration", goal_ref=None,
        plan_ref=plan_id, state="proposed",
    )
    result = OptionProposal(
        option=option, plan=plan,
        preliminary_admissibility=(
            "indeterminate" if not consequences else None
        ),
    )
    result.validate()
    return result

def propose_spatial_return(
    *, target: SpatialReturnTarget, initial_state: SimulationState,
    simulator: Simulator, st_version: str, t_monde: int, ttl_steps: int,
    goal_ref: str,
) -> OptionProposal | None:
    """A single validated hop toward a remembered place, not a compulsory act."""
    target.validate()
    initial_state.validate()
    if (not goal_ref or not st_version or type(t_monde) is not int
        or t_monde < 1 or type(ttl_steps) is not int or ttl_steps < 1
        or target.source_t_monde != t_monde
        or target.origin != (initial_state.x, initial_state.y)):
        return None
    effects = _perceptually_grounded_step(
        target=target, initial_state=initial_state, simulator=simulator,
    )
    if effects is None:
        return None
    option_id = f"option:place-memory:{target.ref}"
    plan_id = f"plan:{option_id}:v1"
    plan = Plan(
        id=plan_id, option_ref=option_id, version="1",
        steps=(PlanStep(index=0, command=PrimitiveCommand(
            "se_deplacer", {"direction": target.direction}),
            preconditions=("adjacent_passable",),
            predicted_consequences=effects,
            observation_window_steps=1),),
        goal_ref=goal_ref, budget_used_uc=1, status="valid",
        st_version=st_version,
    )
    option = Option(
        id=option_id, version="1", type="primitive",
        learning_signature=(f"memory_place_return:{target.entity_id}"),
        preconditions=("adjacent_passable",),
        success_condition="target_position_observed",
        failure_condition="target_position_not_observed",
        invalidation_condition="observed_entity_place_or_goal_changed",
        motive_ref=MotiveRef(type="place_memory", id=target.ref),
        founding_st_version=st_version,
        expires_at_step=t_monde + ttl_steps,
        provenance="memory", goal_ref=goal_ref, plan_ref=plan_id,
        state="proposed",
    )
    proposal = OptionProposal(
        option=option, plan=plan,
        preliminary_admissibility=("indeterminate" if not effects else None),
    )
    proposal.validate()
    return proposal

def propose_lived_site_return(
    *, target: LivedSiteReturnTarget, initial_state: SimulationState,
    simulator: Simulator, st_version: str, t_monde: int, ttl_steps: int,
) -> OptionProposal | None:
    """One ordinary option toward a personally experienced site, never an entity.

    A bodily association is contextual, not a predicted benefit or a command.
    Stage8 reads the separately authenticated Exploration owner to assess its
    relevance. GoalManager is not bypassed by an artificial objective.
    """
    target.validate()
    initial_state.validate()
    if (not st_version or type(t_monde) is not int or t_monde < 1
        or type(ttl_steps) is not int or ttl_steps < 1
        or target.source_t_monde != t_monde
        or target.origin != (initial_state.x, initial_state.y)):
        return None
    effects = _perceptually_grounded_step(
        target=target, initial_state=initial_state, simulator=simulator,
    )
    if effects is None:
        return None
    option_id = f"option:lived-site:{target.ref}"
    plan_id = f"plan:{option_id}:v1"
    plan = Plan(
        id=plan_id, option_ref=option_id, version="1",
        steps=(PlanStep(
            index=0, command=PrimitiveCommand(
                "se_deplacer", {"direction": target.direction}),
            preconditions=("adjacent_passable",),
            predicted_consequences=effects, observation_window_steps=1,
        ),),
        goal_ref=None, budget_used_uc=1, status="valid",
        st_version=st_version,
    )
    option = Option(
        id=option_id, version="1", type="primitive",
        learning_signature=(
            f"lived_site_return:{target.observed_position[0]}:"
            f"{target.observed_position[1]}"
        ),
        preconditions=("adjacent_passable",),
        success_condition="target_position_observed",
        failure_condition="target_position_not_observed",
        invalidation_condition="lived_site_or_context_changed",
        motive_ref=MotiveRef(type="lived_site", id=target.ref),
        founding_st_version=st_version, expires_at_step=t_monde+ttl_steps,
        provenance="memory", goal_ref=None, plan_ref=plan_id,
        state="proposed",
    )
    proposal = OptionProposal(
        option=option, plan=plan,
        preliminary_admissibility=("indeterminate" if not effects else None),
    )
    proposal.validate()
    return proposal
