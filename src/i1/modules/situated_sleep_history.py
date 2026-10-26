"""Observer-only, situated sleep history from an already UC-paid h projection.

#473: This module owns neither memory nor a safety/value/motor judgment.
The caller must have obtained a validated, bounded SlowHistory projection
after the independent P-43 charge. No WorldBody, Oracle or journal scan here.
"""
from __future__ import annotations

from copy import deepcopy

from .memory import same_lived_command_parameters
from .paid_action_consolidation import CHANNELS, validate_published_fragments
from .sleep_competition import _sleep_site_ref

SCHEMA = "i1-situated-observed-sleep-history-v1"


def describe_situated_sleep_history(
    *, published_fragments: list[dict[str, object]],
    current_site: tuple[int, int], before_step: int,
) -> dict[str, object]:
    """Describe personally witnessed sleep here/elsewhere; never predict it.

    'Not observed here' means only absent from the bounded, published h view.
    The signs count *fragments*, not distinct admissions, causal benefits,
    independent sleep sessions, expected rewards or probable safety.
    """
    current_ref = _sleep_site_ref(current_site)
    if (type(before_step) is not int or before_step < 1
            or not validate_published_fragments(published_fragments)):
        raise ValueError("invalid situated h read or world step")
    # A valid retained h fragment can still be from a future publication
    # relative to this current option. That must never be read retroactively.
    if any(row["consolidation_cut_step"] > before_step
           or row["last_step"] >= before_step for row in published_fragments):
        raise ValueError("situated sleep history crosses publication cut")

    groups: dict[tuple[int, int], list[dict[str, object]]] = {}
    for fragment in published_fragments:
        if (fragment["primitive"] != "dormir"
                or not same_lived_command_parameters(
                    fragment["parameters"], {},
                )):
            continue
        site = (fragment["site_after"]["x"], fragment["site_after"]["y"])
        _sleep_site_ref(site)  # Reject malformed physical site, do not repair.
        groups.setdefault(site, []).append(fragment)

    sites = []
    for site in sorted(groups):
        rows = groups[site]  # Already ordered by h's authenticated chronology.
        signs = {
            channel: {"positive": 0, "negative": 0, "zero": 0, "unknown": 0}
            for channel in CHANNELS
        }
        experiences = []
        for row in rows:
            delta = row["observed_total_body_delta"]
            for channel in CHANNELS:
                sign = ("unknown" if delta is None else
                        "positive" if delta[channel] > 0 else
                        "negative" if delta[channel] < 0 else "zero")
                signs[channel][sign] += 1
            experiences.append({
                "fragment_id": row["id"],
                "first_step": row["first_step"],
                "last_step": row["last_step"],
                "observed_steps": row["observed_steps"],
                "source_event_refs": list(row["source_event_refs"]),
                "source_episode_refs": list(row["source_episode_refs"]),
                "observed_body_before": deepcopy(row["body_before"]),
                "observed_body_after": deepcopy(row["body_after"]),
                "observed_total_body_delta": deepcopy(delta),
                "verification_status": row["verification_status"],
            })
        sites.append({
            "site_ref": _sleep_site_ref(site),
            "site": [site[0], site[1]],
            "is_current_site": site == current_site,
            "fragment_count": len(rows),
            "observed_steps": sum(row["observed_steps"] for row in rows),
            "first_observed_step": rows[0]["first_step"],
            "last_observed_step": rows[-1]["last_step"],
            "observed_full_energy_before_count": sum(
                row["body_before"] is not None
                and row["body_before"]["energy"] == 100
                for row in rows
            ),
            "sign_counts_by_fragment": {
                channel: {
                    **counts,
                    "contradictory": (
                        counts["positive"] > 0 and counts["negative"] > 0
                    ),
                }
                for channel, counts in signs.items()
            },
            "experiences": experiences,
        })

    same = next((x for x in sites if x["is_current_site"]), None)
    total = sum(site["fragment_count"] for site in sites)
    return {
        "schema": SCHEMA,
        "primitive": "dormir",
        "parameters": {},
        "current_site_ref": current_ref,
        "current_site": [current_site[0], current_site[1]],
        "current_site_record_status": (
            "observed_in_bounded_h" if same is not None
            else "not_observed_in_bounded_h"
        ),
        "same_site_fragment_count": 0 if same is None else same["fragment_count"],
        "other_site_fragment_count": total - (
            0 if same is None else same["fragment_count"]
        ),
        "historical_site_count": len(sites),
        "historical_fragment_count": total,
        "site_observations": sites,
        "complete_subjective_session_proven": False,
        "causal_attribution": False,
        "decision_evidence": False,
        "expected_consequence": None,
        "site_safety_inferred": False,
        "motor_permission": False,
    }
