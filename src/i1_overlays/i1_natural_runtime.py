"""Canonical living I1 without A2.38/A2.39 H1/H2 ablation policies.

The historical experimental classes remain available by explicit import for
reproducing the original studies. This default actor inherits the general
perception/needs/planning/Competition/Stage9/Action Control substrate, the
first-person D1 capabilities and the default #229 food affordance, without
inheriting either scripted A2.38 H1/H2 review or A2.39 food-first H2.

Sleep and starvation physics are installed by the isolated I1 generator's
common mortal Stage11SleepRuntime birth path. No motor bypass or artificial
prebirth experience is introduced here.
"""
from __future__ import annotations

from .i1_d2_runtime import I1WaterPrudentRuntime
from dataclasses import replace
from .determinism import canonical_causal_bytes, sha256_hex
from i1.modules.geographic_exploration import GeographicExplorationConfig

# Historical arms remain available explicitly from the independent
# I1A238ExperimentalRuntime / I1A239ExperimentalRuntime classes. They are
# intentionally not accepted by the canonical runtime's constructor.
_ABLATION_SETTINGS = frozenset({
    "i1_a238_alternate_need",
    "i1_a238_bounded_move",
    "i1_a238_need_review_uc",
    "i1_a238_move_review_uc",
    "i1_a238_max_move_reviews",
    "i1_a239_food_first_risk",
    "i1_a239_strict_unknown",
    "i1_a239_d2_uc",
    "i1_a239_risk_uc",
    "i1_a239_max_commitments",
})


class I1Runtime(I1WaterPrudentRuntime):
    """Default I1 actor. H1/H2 are not part of its inheritance graph."""

    individual_id = "i1-natural-default-v1"

    def __init__(self, **kwargs):
        # Version the prospective I1 configuration instead of modifying the
        # canonical reference fixture or copying A2.38 researcher switches.
        cfg = kwargs.get("stage11_config")
        if cfg is None:
            raise ValueError("natural I1 birth requires an explicit Stage11 config")
        if cfg.geographic is None:
            geographic = GeographicExplorationConfig(
                version="i1-firstperson-frontier-v1",
                novelty_weight=0.15, max_distinct_sites=1024,
                max_targets_per_cycle=1,
                observe_routes=False, refresh_surveys=False,
            )
            cfg = replace(
                cfg, version=cfg.version + "+i1-firstperson-frontier-v1",
                geographic=geographic, intrinsic_weight=min(cfg.intrinsic_weight, 0.35),
                local_threat_alerts=True,
                geographic_capacity_guard_enabled=True,
            )
        kwargs["stage11_config"] = cfg
        # First-person proximal action agency, never a claim that a distal
        # outcome was necessarily caused by the individual's intention.
        kwargs["subjective_goal_agency"] = True
        kwargs["dual_scope_agency"] = True
        kwargs["spatial_goal_progress"] = True
        unexpected = sorted(_ABLATION_SETTINGS.intersection(kwargs))
        if unexpected:
            raise ValueError(
                "H1/H2 settings are restricted to historical experimental "
                "runtimes, not the default I1: " + ", ".join(unexpected)
            )
        # No opt-out in the canonical actor: a sensed, UC-priced unknown
        # action may be CONSIDERED, never forced or deemed safe. For
        # experimental ablations use the frozen descendant/runtime class.
        if kwargs.get("i1_unknown_action_enabled", True) is not True:
            raise ValueError("default I1 requires uncertain-action consideration")
        kwargs["i1_unknown_action_enabled"] = True
        # Ordinary embodied water experience is useful without any external
        # pre-trained visible-delta corpus or D2/H2 movement permission.
        if kwargs.get("i1_water_probe_enabled", True) is not True:
            raise ValueError("default I1 requires first-person water probing")
        if kwargs.get("i1_water_learning_enabled", True) is not True:
            raise ValueError("default I1 requires first-person water learning")
        kwargs["i1_water_probe_enabled"] = True
        kwargs["i1_water_learning_enabled"] = True
        kwargs["i1_d2_prudence"] = False
        super().__init__(**kwargs)

    def _propose_for_cycle(
        self, *, capture, goal_for_planning, st_before_cycle, cycle,
    ):
        proposal = super()._propose_for_cycle(
            capture=capture, goal_for_planning=goal_for_planning,
            st_before_cycle=st_before_cycle, cycle=cycle,
        )
        if proposal is not None or goal_for_planning is None:
            return proposal
        if (self.goal_manager.active_goal is None
                or self.goal_manager.active_goal.id != goal_for_planning.id):
            return proposal
        # Native GoalManager failure accounting instead of H1's specialist
        # arm. Genuine unchanged first-person context is required; an
        # unmodelled effect is not misrepresented as a successful action.
        context = sha256_hex(canonical_causal_bytes({
            "goal": goal_for_planning.goal_type,
            "target": goal_for_planning.target,
            "position": [capture.x, capture.y],
            "body": dict(capture.body),
            "inventory": dict(capture.inventory),
            "current_resources": list(capture.current_resources),
            "current_water_source": capture.current_water_source,
            "adjacent": [
                [cell.direction, cell.passable, cell.water_source,
                 list(cell.resources)]
                for cell in capture.adjacent
            ],
        }))
        # This is a GoalManager operation, charged to the existing canonical
        # goal arbitration budget instead of minting a new H1 UC entitlement.
        if not self._charge(module="goal_manager", operation="goal_arbitrate"):
            return proposal
        released = self.goal_manager.note_non_plannable(
            material_context_hash=context, t_monde=capture.t_monde
        )
        self._write(kind="i1_goal_unavailable_reconsidered", cycle=cycle, data={
            "goal_ref": goal_for_planning.id,
            "perceived_context_sha256": context,
            "goal_released": released,
            "new_goal_forced": False,
            "success_inferred": False,
        })
        if released:
            self.planning.invalidate_current()
            self.competition.prune_invalid(
                active_goal_id=None, t_monde=capture.t_monde
            )
        return proposal
