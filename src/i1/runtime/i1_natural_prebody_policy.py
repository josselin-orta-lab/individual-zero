"""Explicit, currently DORMANT I1-only DC-09 pre-action body policy.

Do not register for a natural birth without tested M11 replay compatibility
and a paid owner-side read. Historical Stage2/Stage7 policy versions remain
unchanged. Physical pre-action values enter Memory only through committed,
version-matched JournalViews projections, never through technical journals.
"""
from __future__ import annotations

from .journal_views import AutobiographicalPolicy
from .stage7_runtime import STAGE7_AUTOBIOGRAPHICAL_POLICY

LIVED_PREBODY_POLICY = AutobiographicalPolicy(
    version="i1-lived-body-before-v1",
    allowed_fields_by_kind={
        kind: (
            tuple(fields[:fields.index("body_after")])
            + ("body_before",)
            + tuple(fields[fields.index("body_after"):])
            if kind == "world_transition_experienced" else tuple(fields)
        )
        for kind, fields in
        STAGE7_AUTOBIOGRAPHICAL_POLICY.allowed_fields_by_kind.items()
    },
)
LIVED_PREBODY_POLICY.validate()

def captured_prebody_matches_transition(
    *, captured_body: object, physical_body_before: object,
) -> bool:
    """Fail closed when a physical pre-action state was not itself perceived.

    This pure gate authorizes no journal read and never changes a motor
    command. A scenario applied after admission may make the physical state
    differ from the pre-decision capture: that state must NOT be described
    as the body's earlier first-person perception.
    """
    from collections.abc import Mapping
    from math import isfinite

    keys = frozenset(("energy", "food", "water", "integrity"))
    if (not isinstance(captured_body, Mapping)
            or not isinstance(physical_body_before, Mapping)
            or set(captured_body) != keys
            or set(physical_body_before) != keys):
        return False
    for name in keys:
        a = captured_body[name]
        b = physical_body_before[name]
        if (type(a) not in (int, float) or type(b) not in (int, float)
                or not isfinite(a) or not isfinite(b)
                or not 0 <= a <= 100 or not 0 <= b <= 100
                or float(a) != float(b)):
            return False
    return True

def policy_for_proven_prebody_transition(
    *, journal, t_monde: int, attempt_ref: str,
    command_ref: str, physical_ref: str,
) -> AutobiographicalPolicy:
    """Select a DC-09 policy from already committed physical journal receipts.

    This pure, currently UNWIRED admission gate reads no WorldBody, Oracle,
    current Memory state or hidden post-action telemetry. A new-policy
    projection is eligible only if one first-person capture, one admission
    and the actually sent/physically applied command share the exact
    attempt, source identity, and causal ordering. Otherwise the historical
    policy is retained, never a fabricated bodily recollection.
    """
    from collections.abc import Mapping
    from .determinism import deterministic_id

    old = STAGE7_AUTOBIOGRAPHICAL_POLICY
    if (type(t_monde) is not int or t_monde < 1
            or any(type(ref) is not str or not ref
                   for ref in (attempt_ref, command_ref, physical_ref))):
        return old
    command = journal.get(command_ref)
    physical = journal.get(physical_ref)
    if command is None or physical is None:
        return old
    c, p = command.causal_event, physical.causal_event
    if (command.index >= physical.index
            or c.get("kind") != "command_experienced"
            or c.get("emitter") != "action_control"
            or p.get("kind") != "world_transition_experienced"
            or p.get("emitter") != "world_and_body"
            or any(event.get("t_monde") != t_monde
                   or event.get("attempt_ref") != attempt_ref
                   for event in (c, p))):
        return old
    digest = c.get("command_hash")
    primitive = c.get("primitive")
    if (type(digest) is not str or len(digest) != 64
            or type(primitive) is not str or not primitive
            or deterministic_id(
                "journal-event-v1", "world", t_monde,
                attempt_ref, digest, "transition",
            ) != physical_ref):
        return old

    captures = []
    admissions = []
    # Bounded per-attempt reverse scan avoids an unpaid full journal read.
    # Any overflow denies only the new projection, never the physical action.
    for inspected, entry in enumerate(journal.iter_entries_reversed(), 1):
        if inspected > 4096:
            return old
        if entry.index >= command.index:
            continue
        e = entry.causal_event
        step = e.get("t_monde")
        if type(step) is int and step < t_monde:
            break
        if step != t_monde or e.get("attempt_ref") != attempt_ref:
            return old
        if e.get("kind") == "perceptual_capture":
            if e.get("emitter") != "stage3-runtime":
                return old
            captures.append(entry)
        elif e.get("kind") == "command_admitted":
            if e.get("emitter") != "stage3-runtime":
                return old
            admissions.append(entry)
    if len(captures) != 1 or len(admissions) != 1:
        return old
    capture, admitted = captures[0], admissions[0]
    if not capture.index < admitted.index < command.index < physical.index:
        return old
    captured = capture.causal_event.get("data")
    admission = admitted.causal_event.get("data")
    if (not isinstance(captured, Mapping)
            or captured.get("capture_t_monde") != t_monde
            or captured.get("dual_scope_capture_schema")
                != "stage12-dual-scope-body-cue-v1"
            or not isinstance(admission, Mapping)
            or admission.get("command_hash") != digest
            or admission.get("primitive") != primitive):
        return old
    if not captured_prebody_matches_transition(
        captured_body=captured.get("dual_scope_visible_body"),
        physical_body_before=p.get("body_before"),
    ):
        return old
    return LIVED_PREBODY_POLICY
