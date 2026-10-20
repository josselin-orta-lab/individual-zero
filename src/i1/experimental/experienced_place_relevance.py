"""I1 opt-in, stateless Stage8 relevance of personally experienced places.

Stage8 may consider a PLACE where this individual physically executed boire
and subsequently observed a strictly positive bodily water delta. The place
itself, or a movement toward it, is not predicted to replenish water. The
entity-type label alone never receives value.

There is no mutable evidence owner here. The ONLY accumulated training state
remains I1LivedWaterOwner, already registered in current-generation M11
custody. The evaluator derives a bounded, uncertain signal on each current
first-person cognitive cycle. It does not alter Q, TD, Planning, Competition,
motor commands, death, or resource physics.

Research-only: ordinary birth_i1 and birth_i1_m11 never enable this adapter.
"""
from __future__ import annotations

from dataclasses import replace
from math import isfinite

from i1.modules.competition import OptionEvidenceInput

CONTRACT = "i1-experienced-place-stage8-native-opt-in-v1"
MAX_RELEVANCE = 0.45
RELEVANCE_WATER_GATE = 30.0


def experienced_site_relevance(
    *, observed_gain: float, current_water: float,
    confidence: float, observed_hops: int,
) -> float:
    """Bound a prior bodily association, never predict a future water gain."""
    quantities = (observed_gain, current_water, confidence)
    if (
        any(type(x) not in (int, float) or not isfinite(x) for x in quantities)
        or not 0 < observed_gain <= 100
        or not 0 <= current_water <= 100
        or not 0 < confidence <= 1
        or type(observed_hops) is not int
        or not 1 <= observed_hops <= 8
    ):
        raise ValueError("nonphysical first-person water/place relevance input")
    if current_water > RELEVANCE_WATER_GATE:
        return 0.0
    deficit = 100.0 - current_water
    fractional_prior_relief = min(observed_gain, deficit) / deficit
    observed_route_uncertainty = 1.0 / (1.0 + 0.1 * (observed_hops - 1))
    return min(
        MAX_RELEVANCE,
        fractional_prior_relief * confidence * observed_route_uncertainty,
    )


def personally_supported_site_gain(owner, *, site: tuple[int, int],
                                  life_id: str) -> float | None:
    """Derive a site-specific association exclusively from M11-owned state."""
    if (
        type(site) is not tuple or len(site) != 2
        or any(type(x) is not int for x in site)
        or type(life_id) is not str or not life_id.startswith("i1:")
        or owner.life_id != life_id
        or type(owner.enabled) is not bool
    ):
        raise ValueError("water evidence is not owned by this mortal I1")
    if not owner.enabled:
        return None
    gains: list[float] = []
    for row in owner.examples:
        if (
            type(row) is not dict
            or type(row.get("source_position")) is not list
            or len(row["source_position"]) != 2
            or any(type(x) is not int for x in row["source_position"])
            or type(row.get("delta_water")) not in (int, float)
            or not isfinite(row["delta_water"])
            or not 0 < row["delta_water"] <= 100
            or type(row.get("sent_world_step")) is not int
            or type(row.get("observed_world_step")) is not int
            or row["observed_world_step"] != row["sent_world_step"] + 1
        ):
            raise ValueError("invalid positive source evidence from water owner")
        if tuple(row["source_position"]) == site:
            gains.append(float(row["delta_water"]))
    return None if not gains else max(gains)


class I1ExperiencedPlaceStage8:
    """Pure derived evaluation around real Stage8; no independent mutable owner.

    This wrapper is assembled at a fresh opt-in mortal birth from the exact
    owner roster that M11 restores. Because it owns no accumulators or Q
    state, a cold factory reconstructs it with the current owner instead
    of importing a stale Python object.
    """

    def __init__(self, *, underlying, actor) -> None:
        if underlying is None or actor is None:
            raise ValueError("native site relevance needs Stage8 and I1 owner")
        self._underlying = underlying
        self._actor = actor

    def __getattr__(self, key):
        if key.startswith("__"):
            raise AttributeError(key)
        underlying = vars(self).get("_underlying")
        if underlying is None:
            raise AttributeError(key)
        return getattr(underlying, key)

    def evaluate(self, *, proposal, **kwargs):
        # Always call the genuinely charged/evaluated Stage8 path first.
        baseline = self._underlying.evaluate(proposal=proposal, **kwargs)
        option = proposal.option
        if (
            option.provenance != "memory"
            or option.motive_ref.type != "place_memory"
            or option.goal_ref is not None
            or baseline.evidence is None
            or baseline.evaluation.status != "evaluated"
        ):
            return baseline

        actor = self._actor
        goal = actor.goal_manager.active_goal
        if (
            goal is None or goal.goal_type != "drink"
            or type(goal.id) is not str
            or not goal.id.startswith("goal:drink:")
        ):
            return baseline
        geo = actor.exploration.geographic
        target = None if geo is None else geo.place_for(option)
        if (
            target is None or target.source_t_monde != kwargs["t_monde"]
            or target.origin == target.observed_position
            or not 0 < target.confidence <= 1
            or not 2 <= len(target.visited_path) <= 9
        ):
            return baseline

        # Only the authorized bodily Perception frozen at step opening.
        seen = actor._stage11_prospective_capture
        if (
            type(seen) is not tuple or len(seen) != 3
            or seen[0] != kwargs["t_monde"]
            or seen[1] != target.origin
            or type(seen[2]) not in (int, float)
            or not isfinite(seen[2])
            or not 0 <= seen[2] <= 100
        ):
            raise RuntimeError("expired or unowned frozen body observation")
        site = tuple(target.observed_position)
        gain = personally_supported_site_gain(
            actor._water_learner, site=site, life_id=actor._i1_personal_id,
        )
        if gain is None:
            return baseline
        value = experienced_site_relevance(
            observed_gain=gain, current_water=seen[2],
            confidence=target.confidence,
            observed_hops=len(target.visited_path) - 1,
        )
        if value == 0:
            return baseline
        signal = f"i1:personally-relieved-water:{site[0]}:{site[1]}"
        if signal in baseline.evaluation.signal_ids:
            raise RuntimeError("previously admitted site evidence counted twice")
        enhanced = OptionEvidenceInput(
            evaluation=replace(
                baseline.evaluation,
                signal_ids=tuple(baseline.evaluation.signal_ids) + (signal,),
                producers=tuple(dict.fromkeys(
                    tuple(baseline.evaluation.producers)
                    + ("i1:conditional-lived-site-relevance",)
                )),
            ),
            evidence=max(-1.0, min(1.0, baseline.evidence + value)),
        )
        enhanced.validate()
        return enhanced
