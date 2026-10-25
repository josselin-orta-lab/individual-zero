"""Bounded, descriptive contiguous fragments from already-owned lived action witnesses.

The caller must have obtained witnesses through a UC-paid, closed, committed
first-person Memory projection. This pure view has no memory, motor or value owner.
"""
from __future__ import annotations

from copy import deepcopy
from math import isfinite

CHANNELS = ("energy", "food", "water", "integrity")


def closed_action_fragments(witnesses, *, max_fragments=16, max_steps=16):
    """Group contiguous exact-action witnesses without inferring sleep sessions.

    Missing or conflicting first-person body evidence yields an unknown total.
    Time gaps, place changes, command changes and discontinuous physical
    states break fragments. A fragment reports observed steps, not admission
    count, physiological causality, benefit, or an inferred future outcome.
    """
    if (type(max_fragments) is not int or not 1 <= max_fragments <= 16
            or type(max_steps) is not int or not 1 <= max_steps <= 16):
        raise ValueError("invalid bounded lived fragment limits")
    from .memory import same_lived_command_parameters

    def valid(row):
        if (type(row) is not dict or type(row.get("step")) is not int
                or row["step"] < 1 or type(row.get("primitive")) is not str
                or not row["primitive"] or type(row.get("parameters")) is not dict
                or type(row.get("position_after")) is not dict
                or set(row["position_after"]) != {"x", "y"}
                or any(type(row["position_after"][k]) is not int for k in ("x", "y"))
                or type(row.get("source_event_refs")) not in (list, tuple)
                or len(row["source_event_refs"]) != 2
                or any(type(ref) is not str or not ref for ref in row["source_event_refs"])
                or row["source_event_refs"][0] == row["source_event_refs"][1]
                or row.get("causal_attribution") is not False
                or row.get("decision_evidence") is not False):
            return False
        for name in ("body_before", "body_after"):
            body = row.get(name)
            if body is not None and (
                type(body) is not dict or set(body) != set(CHANNELS)
                or any(type(body[k]) not in (int, float)
                       or not isfinite(body[k]) or not 0 <= body[k] <= 100
                       for k in CHANNELS)
            ):
                return False
        return row.get("body_after") is not None

    groups = []
    current = []
    seen_steps = set()
    seen_refs = set()
    for row in sorted(witnesses, key=lambda x: x["step"] if type(x) is dict and type(x.get("step")) is int else -1):
        if not valid(row):
            if current:
                groups.append(current)
                current = []
            continue
        refs = row["source_event_refs"]
        if (row["step"] in seen_steps or any(ref in seen_refs for ref in refs)):
            # Fail closed on ambiguous source identity, including a duplicate
            # that would otherwise bridge two different physical fragments.
            return ()
        seen_steps.add(row["step"])
        seen_refs.update(refs)
        previous = current[-1] if current else None
        joined = (
            previous is not None
            and row["step"] == previous["step"] + 1
            and row["primitive"] == previous["primitive"]
            and same_lived_command_parameters(row["parameters"], previous["parameters"])
            and row["position_after"] == previous["position_after"]
            and len(current) < max_steps
            and previous["body_after"] is not None
            and row["body_before"] is not None
            and all(previous["body_after"][k] == row["body_before"][k]
                    for k in CHANNELS)
        )
        if current and not joined:
            groups.append(current)
            current = []
        current.append(row)
    if current:
        groups.append(current)
    result = []
    for group in groups[-max_fragments:]:
        first, last = group[0], group[-1]
        # Without a first-person BEFORE value for the first transition, a
        # total difference is unknowable even when all later steps are closed.
        before = first["body_before"]
        after = last["body_after"]
        result.append({
            "primitive": first["primitive"],
            "parameters": deepcopy(first["parameters"]),
            "site_after": deepcopy(first["position_after"]),
            "first_step": first["step"],
            "last_step": last["step"],
            "observed_steps": len(group),
            "source_event_refs": tuple(ref for row in group
                                       for ref in row["source_event_refs"]),
            "source_episode_refs": tuple(dict.fromkeys(
                ref for row in group
                for ref in row.get("source_episode_refs", ())
            )),
            "body_before": deepcopy(before),
            "body_after": deepcopy(after),
            "observed_total_body_delta": (
                None if before is None else
                {key: after[key] - before[key] for key in CHANNELS}
            ),
            "observed_effects_by_step": tuple(
                deepcopy(row.get("observed_effects")) for row in group
            ),
            "complete_subjective_session": False,
            "causal_attribution": False,
            "decision_evidence": False,
        })
    return tuple(result)
