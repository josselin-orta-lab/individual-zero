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
        super().__init__(**kwargs)
