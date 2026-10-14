"""GA-SPATIAL-01 stateless first-person spatial cue policy (NOT a producer).

Action Control remains sole owner of eventual subjective judgement. This pure
policy has no access to outcome, P-47, WorldBody, Oracle, Bench or causal logs.
The caller must separately prove command admission/execution, life identity,
and pre-action intent. A policy return is NOT an admissible Stage12 pair.
"""
from __future__ import annotations

from dataclasses import dataclass

from i0.interfaces import PrimitiveCommand
from .perception import PerceptualCapture


DIRECTIONS = {"north": (0, -1), "south": (0, 1),
              "east": (1, 0), "west": (-1, 0)}
POLICY_VERSION = "stage12-goal-spatial-subjective-cue-v1"


@dataclass(frozen=True, slots=True)
class SpatialAgencyCue:
    """A bounded subjective judgement candidate, not causal physical truth."""

    agency: str
    reason: str
    policy_version: str = POLICY_VERSION


def evaluate_spatial_goal_cue(
    *, pre: PerceptualCapture, post: PerceptualCapture,
    command: PrimitiveCommand, target_x: int, target_y: int,
    target_kind: str, admitted_and_executed: bool,
) -> SpatialAgencyCue:
    """Interpret a witnessed *goal-relevant* spatial movement.

    This function does not compute goal success/failure or compare predictions.
    A nearby obstacle alone, or no spatial progress alone, never proves world.
    Target must have been directly perceived as a resource/water source before
    the action. Returns unknown on ambiguity; caller controls UC and custody.
    """
    unknown = SpatialAgencyCue("unknown", "insufficient_spatial_agency_cues")
    if (type(pre) is not PerceptualCapture
            or type(post) is not PerceptualCapture
            or type(target_x) is not int or type(target_y) is not int
            or type(admitted_and_executed) is not bool
            or type(target_kind) is not str):
        raise ValueError("invalid candidate lived spatial cues")
    if (not admitted_and_executed or post.t_monde != pre.t_monde + 1
            or command.primitive != "se_deplacer"):
        return unknown
    direction = command.parameters.get("direction")
    if direction not in DIRECTIONS:
        return unknown
    dx, dy = DIRECTIONS[direction]
    attempted = (pre.x + dx, pre.y + dy)
    target = (target_x, target_y)
    cell = [c for c in pre.adjacent
            if c.direction == direction and (c.x, c.y) == attempted]
    # Target cue and attempted cell MUST coincide for this v1 local policy.
    # Targets on distant or unrelated cells cannot explain an obstruction.
    if len(cell) != 1 or target != attempted:
        return unknown
    observed = cell[0]
    if target_kind == "water":
        relevant = observed.water_source
    elif target_kind in ("berry_a", "berry_b"):
        relevant = target_kind in observed.resources
    else:
        return unknown
    if not relevant:
        return unknown
    before = (pre.x, pre.y)
    after = (post.x, post.y)
    if (not observed.passable and after == before):
        return SpatialAgencyCue(
            "world", "witnessed_goal_relevant_blocked_direction")
    if (observed.passable and
            after == (pre.x + dx, pre.y + dy)):
        return SpatialAgencyCue(
            "self", "witnessed_goal_relevant_efferent_displacement")
    return unknown
