"""I1-only bounded Stage10 fragments from genuinely charged autobiographical replay.

No journal, WorldBody, Oracle or active owner is available here. The caller
provides exactly one previously verified event per P-42 episode_replay debit.
The former paid buffer is bounded independently of the lifetime/history size.
"""
from __future__ import annotations

from copy import deepcopy
from math import isfinite
from typing import Mapping

from .action_fragments import closed_action_fragments
from .memory import same_lived_command_parameters
from lab.determinism import canonical_causal_bytes, sha256_hex

MAX_PAID_SOURCES = 32
MAX_COMMITTED_FRAGMENTS = 16
CHANNELS = ("energy", "food", "water", "integrity")
SCHEMA = "i1-stage10-observed-action-fragments-v1"
_EFFECT_TYPES = {
    "movement": str, "ate": str, "rest": str, "drank": bool,
    "tool_crafted": bool, "shelter_formed": bool,
    "placed_stone_count": int,
}


def _body(value):
    if (type(value) is not dict or set(value) != set(CHANNELS)
            or any(type(value[k]) not in (int, float)
                   or not isfinite(value[k]) or not 0 <= value[k] <= 100
                   for k in CHANNELS)):
        return None
    return {k: float(value[k]) for k in CHANNELS}


def _effects(value):
    if type(value) is not dict:
        return None
    detached = {}
    for key, val in value.items():
        if key == "collected":
            if (type(val) is not dict or set(val) != {"kind", "quantity"}
                    or type(val["kind"]) is not str or not val["kind"]
                    or type(val["quantity"]) is not int
                    or val["quantity"] < 0):
                return None
            detached[key] = {"kind": val["kind"], "quantity": val["quantity"]}
        elif (key not in _EFFECT_TYPES
              or type(val) is not _EFFECT_TYPES[key]
              or key == "placed_stone_count" and val < 0):
            # Scenario and hazard effects may be autobiographically visible
            # but need not fit this narrow factual summary vocabulary.
            # Retain the lived body delta without inventing their meaning.
            return {}
        else:
            detached[key] = val
    return detached


def _valid_event(event):
    if (type(event) is not dict or type(event.get("event_id")) is not str
            or not event["event_id"] or type(event.get("t_monde")) is not int
            or event["t_monde"] < 1):
        return False
    if event.get("kind") == "command_experienced":
        if (set(event) != {"event_id", "kind", "t_monde", "primitive", "parameters"}
                or type(event["primitive"]) is not str
                or not event["primitive"] or type(event["parameters"]) is not dict):
            return False
    elif event.get("kind") == "world_transition_experienced":
        if (set(event) not in (
                {"event_id", "kind", "t_monde", "position_after",
                 "body_after", "effects"},
                {"event_id", "kind", "t_monde", "position_after",
                 "body_before", "body_after", "effects"})
                or type(event["position_after"]) is not dict
                or set(event["position_after"]) != {"x", "y"}
                or any(type(event["position_after"][k]) is not int
                       for k in ("x", "y"))
                or _body(event["body_after"]) is None
                or "body_before" in event and _body(event["body_before"]) is None
                or _effects(event["effects"]) is None):
            return False
    else:
        return False
    try:
        canonical_causal_bytes(event)
    except (ValueError, TypeError):
        return False
    return True


def _source_valid(row, *, before_step=None):
    if (type(row) is not dict
            or set(row) != {"episode_ref", "event_offset",
                            "event_ref", "projection_digest", "event"}
            or type(row["episode_ref"]) is not str or not row["episode_ref"]
            or type(row["event_offset"]) is not int or row["event_offset"] < 0
            or type(row["event_ref"]) is not str or not row["event_ref"]
            or type(row["projection_digest"]) is not str
            or len(row["projection_digest"]) != 64
            or not _valid_event(row["event"])):
        return False
    event = row["event"]
    return (
        row["event_ref"] == event["event_id"]
        and sha256_hex(canonical_causal_bytes(event)) == row["projection_digest"]
        and (before_step is None or event["t_monde"] < before_step)
    )


def validate_paid_sources(rows, *, before_step=None):
    if type(rows) is not list or len(rows) > MAX_PAID_SOURCES:
        return False
    seen_ids, seen_offsets = set(), set()
    for row in rows:
        if not _source_valid(row, before_step=before_step):
            return False
        identity = (row["episode_ref"], row["event_offset"])
        if row["event_ref"] in seen_ids or identity in seen_offsets:
            return False
        seen_ids.add(row["event_ref"])
        seen_offsets.add(identity)
    return rows == sorted(
        rows, key=lambda row: (row["event"]["t_monde"], row["event_ref"])
    )


def record_paid_source(rows, *, episode_ref, event_offset, event,
                       before_step):
    """Retain a fixed-size subset of exact source events AFTER their debit.

    All other event kinds, obsolete schema variants and absent source offsets
    remain unknown rather than being promoted into facts. This does not read
    additional episodes or invent uncharged cross-step evidence.
    """
    if (not validate_paid_sources(rows, before_step=before_step)
            or type(episode_ref) is not str or not episode_ref
            or type(before_step) is not int or before_step < 1):
        raise ValueError("invalid private charged action replay custody")
    if type(event_offset) is not int or event_offset < 0 or not _valid_event(event):
        return rows
    if event["t_monde"] >= before_step:
        raise ValueError("post-cut source cannot enter private replay")
    new = {
        "episode_ref": episode_ref, "event_offset": event_offset,
        "event_ref": event["event_id"], "event": deepcopy(event),
        "projection_digest": sha256_hex(canonical_causal_bytes(event)),
    }
    if (any(row["event_ref"] == new["event_ref"]
            or (row["episode_ref"], row["event_offset"])
               == (episode_ref, event_offset) for row in rows)):
        raise ValueError("duplicate charged action source")
    combined = sorted(
        [*rows, new], key=lambda row: (
            row["event"]["t_monde"], row["event_ref"],
        )
    )[-MAX_PAID_SOURCES:]
    if not validate_paid_sources(combined, before_step=before_step):
        raise ValueError("invalid bounded charged replay result")
    return combined


def _new_fragments(rows, *, cut_step):
    """No cross-episode same-step inference without authenticated order."""
    per_step = {}
    for row in rows:
        event = row["event"]
        key = (row["episode_ref"], event["t_monde"])
        pair = per_step.setdefault(key, {"command": [], "transition": []})
        target = ("command" if event["kind"] == "command_experienced"
                  else "transition")
        pair[target].append(row)
    witnesses = []
    for (ep, step), pair in sorted(per_step.items(), key=lambda x: x[0][1]):
        if len(pair["command"]) != 1 or len(pair["transition"]) != 1:
            continue
        command, transition = pair["command"][0], pair["transition"][0]
        if command["event_offset"] >= transition["event_offset"]:
            continue
        cmd, physical = command["event"], transition["event"]
        body_before = (_body(physical["body_before"])
                       if "body_before" in physical else None)
        after = _body(physical["body_after"])
        witnesses.append({
            "step": step,
            "primitive": cmd["primitive"],
            "parameters": deepcopy(cmd["parameters"]),
            "position_after": deepcopy(physical["position_after"]),
            "source_event_refs": [cmd["event_id"], physical["event_id"]],
            "source_episode_refs": [ep],
            "body_before": body_before, "body_after": after,
            "observed_effects": _effects(physical["effects"]),
            "causal_attribution": False, "decision_evidence": False,
        })
    # The shared generic grouping function rejects duplicated world steps,
    # including two independent episodes that claim a physical action at once.
    result = []
    for item in closed_action_fragments(
            witnesses, max_fragments=MAX_COMMITTED_FRAGMENTS, max_steps=16):
        row = {
            **item,
            "schema": SCHEMA,
            "verification_status": "observed_not_verified",
            "consolidation_cut_step": cut_step,
        }
        # Hash complete detached observation, not a fictional semantic goal.
        row["id"] = "lived-fragment:" + sha256_hex(
            canonical_causal_bytes(row)
        )[:28]
        result.append(row)
    return result


def _published_row_valid(row):
    required = {
        "id", "schema", "verification_status", "consolidation_cut_step",
        "primitive", "parameters", "site_after", "first_step", "last_step",
        "observed_steps", "source_event_refs", "source_episode_refs",
        "body_before", "body_after", "observed_total_body_delta",
        "observed_effects_by_step", "complete_subjective_session",
        "causal_attribution", "decision_evidence",
    }
    if (type(row) is not dict or set(row) != required
            or row["schema"] != SCHEMA
            or row["verification_status"] != "observed_not_verified"
            or type(row["consolidation_cut_step"]) is not int
            or type(row["first_step"]) is not int
            or type(row["last_step"]) is not int
            or not 1 <= row["first_step"] <= row["last_step"]
                   < row["consolidation_cut_step"]
            or type(row["observed_steps"]) is not int
            or not 1 <= row["observed_steps"] <= 16
            or row["last_step"] - row["first_step"] + 1 != row["observed_steps"]
            or type(row["primitive"]) is not str or not row["primitive"]
            or type(row["parameters"]) is not dict
            or type(row["site_after"]) is not dict
            or set(row["site_after"]) != {"x", "y"}
            or any(type(row["site_after"][k]) is not int for k in ("x", "y"))
            or type(row["source_event_refs"]) is not list
            or len(row["source_event_refs"]) != row["observed_steps"] * 2
            or len(set(row["source_event_refs"])) != len(row["source_event_refs"])
            or any(type(ref) is not str or not ref for ref in row["source_event_refs"])
            or type(row["source_episode_refs"]) is not list
            or not row["source_episode_refs"]
            or len(set(row["source_episode_refs"])) != len(row["source_episode_refs"])
            or any(type(ref) is not str or not ref for ref in row["source_episode_refs"])
            or _body(row["body_after"]) is None
            or row["body_before"] is not None and _body(row["body_before"]) is None
            or type(row["observed_effects_by_step"]) is not list
            or len(row["observed_effects_by_step"]) != row["observed_steps"]
            or any(_effects(effect) is None for effect in row["observed_effects_by_step"])
            or row["complete_subjective_session"] is not False
            or row["causal_attribution"] is not False
            or row["decision_evidence"] is not False):
        return False
    before, delta = row["body_before"], row["observed_total_body_delta"]
    if before is None:
        if delta is not None:
            return False
    elif (type(delta) is not dict or set(delta) != set(CHANNELS)
          or any(type(delta[k]) not in (int, float) or not isfinite(delta[k])
                 or abs(delta[k] - (
                     row["body_after"][k] - before[k])) > 1e-9
                 for k in CHANNELS)):
        return False
    try:
        payload = {key: value for key, value in row.items() if key != "id"}
        return row["id"] == "lived-fragment:" + sha256_hex(
            canonical_causal_bytes(payload))[:28]
    except (TypeError, ValueError):
        return False


def validate_published_fragments(rows):
    if type(rows) is not list or len(rows) > MAX_COMMITTED_FRAGMENTS:
        return False
    seen_events, seen_ids = set(), set()
    for row in rows:
        if not _published_row_valid(row):
            return False
        refs = set(row["source_event_refs"])
        if row["id"] in seen_ids or seen_events.intersection(refs):
            return False
        seen_ids.add(row["id"])
        seen_events.update(refs)
    return rows == sorted(
        rows, key=lambda row: (
            row["last_step"], row["first_step"], row["id"],
        )
    )


def merge_paid_fragments(rows, previous, *, cut_step):
    """Bounded sixth-pass assembly, only from prior paid replay receipts."""
    if (type(cut_step) is not int or cut_step < 1
            or not validate_paid_sources(rows, before_step=cut_step)
            or not validate_published_fragments(previous)
            or any(item["consolidation_cut_step"] >= cut_step
                   for item in previous)):
        raise ValueError("unverified paid source or persisted fragment")
    new = _new_fragments(rows, cut_step=cut_step)
    if not new:
        return deepcopy(previous)
    combined = [*deepcopy(previous), *new]
    # Repeated source evidence must never count as a new experience. An
    # identical replay is also rejected rather than counted twice.
    refs = [ref for item in combined for ref in item["source_event_refs"]]
    if len(refs) != len(set(refs)):
        raise ValueError("repeated fragment source across consolidation cuts")
    combined.sort(key=lambda row: (
        row["last_step"], row["first_step"], row["id"],
    ))
    result = combined[-MAX_COMMITTED_FRAGMENTS:]
    if not validate_published_fragments(result):
        raise ValueError("published fragment shape or identity mismatch")
    return result
