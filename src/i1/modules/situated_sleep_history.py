"""Observer-only sleep view of the shared situated action history (#555).

Preserve the existing sleep journal schema, source references, ordering,
and sleep-site identifiers. The common core reads only a previously UC-paid
and bounded SlowHistory projection, and never supplies motor authority.
"""
from __future__ import annotations

from .situated_action_history import describe_situated_action_history
from .sleep_competition import _sleep_site_ref

SCHEMA = "i1-situated-observed-sleep-history-v1"


def describe_situated_sleep_history(
    *, published_fragments: list[dict[str, object]],
    current_site: tuple[int, int], before_step: int,
) -> dict[str, object]:
    """Maintain the existing sleep-specific output using the generic core."""
    summary = describe_situated_action_history(
        published_fragments=published_fragments,
        current_site=current_site,
        before_step=before_step,
        primitive="dormir",
        parameters={},
    )
    summary["schema"] = SCHEMA
    summary["current_site_ref"] = _sleep_site_ref(current_site)
    for row in summary["site_observations"]:
        row["site_ref"] = _sleep_site_ref(tuple(row["site"]))
    # A replacement key at the same position preserves the old journal
    # object field order as well as content and semantics.
    return {
        ("complete_subjective_session_proven"
         if key == "independent_action_session_proven" else key): value
        for key, value in summary.items()
    }
