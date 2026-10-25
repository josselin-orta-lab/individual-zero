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
    from .world import Command, command_digest

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

    # Receipt identity and its declared content must agree with the actual
    # Stage2 Action Control serializer. A copied digest / primitive on a
    # synthetic command event is not evidence of the emitted command.
    parameters = c.get("parameters")
    if (not isinstance(parameters, Mapping)
            or deterministic_id(
                "journal-event-v1", "action_control", t_monde,
                attempt_ref, digest, "send",
            ) != command_ref):
        return old
    try:
        if command_digest(Command(primitive, dict(parameters))) != digest:
            return old
    except (TypeError, ValueError, KeyError):
        return old

    captures = []
    admissions = []
    # Bounded per-attempt reverse scan avoids an unpaid full journal read.
    # Any overflow denies only the new projection, never the physical action.
    inspected = 0
    for entry in journal.iter_entries_reversed():
        # Post-command receipts are not part of this attempt's admission
        # prefix. They must not exhaust the bounded provenance budget.
        if entry.index >= command.index:
            continue
        inspected += 1
        if inspected > 4096:
            return old
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


def attested_postwake_perceptual_body(
    *, journal, t_monde: int, attempt_ref: str,
    command_ref: str, physical_ref: str,
) -> dict[str, object] | None:
    """DORMANT L1 gate: only an actual *perceived* body after a wake.

    The Stage10 wake/reduced receipts authorize the *context* of the new
    capture but never become autobiographical payload themselves. This
    returns a candidate for future versioned DC-09 consideration, NOT a
    memory, session, goal, motor authorization or learned sleep value.
    There is no reader or production caller until #495 activation.
    """
    from collections.abc import Mapping

    # Verify the full original Stage3/Action Control/physical command chain
    # first, including a captured body exactly equal to the physical
    # pre-action body. An after-admission perturbation fails closed.
    if policy_for_proven_prebody_transition(
        journal=journal, t_monde=t_monde, attempt_ref=attempt_ref,
        command_ref=command_ref, physical_ref=physical_ref,
    ) is not LIVED_PREBODY_POLICY:
        return None
    command = journal.get(command_ref)
    physical = journal.get(physical_ref)
    if command is None or physical is None:
        return None
    selected: dict[str, list] = {
        "stage10_reduced_capture": [],
        "stage10_sleep_woke": [],
        "perceptual_capture": [],
    }
    inspected = 0
    for entry in journal.iter_entries_reversed():
        if entry.index >= command.index:
            continue
        inspected += 1
        if inspected > 4096:
            return None
        event = entry.causal_event
        step = event.get("t_monde")
        if type(step) is int and step < t_monde:
            break
        if step != t_monde or event.get("attempt_ref") != attempt_ref:
            return None
        kind = event.get("kind")
        if kind in selected:
            expected = (
                "stage3-runtime" if kind == "perceptual_capture"
                else "stage4-runtime"
            )
            if event.get("emitter") != expected:
                return None
            selected[kind].append(entry)
    if any(len(group) != 1 for group in selected.values()):
        return None
    reduced = selected["stage10_reduced_capture"][0]
    wake = selected["stage10_sleep_woke"][0]
    capture = selected["perceptual_capture"][0]
    if not (
        reduced.index < wake.index < capture.index
        < command.index < physical.index
    ):
        return None
    reduced_data = reduced.causal_event.get("data")
    captured = capture.causal_event.get("data")
    if (not isinstance(reduced_data, Mapping)
            or reduced_data.get("full_cognitive_perception") is not False
            or not isinstance(captured, Mapping)
            or captured.get("dual_scope_capture_schema")
                != "stage12-dual-scope-body-cue-v1"
            or captured.get("capture_t_monde") != t_monde):
        return None
    position = captured.get("position")
    body = captured.get("dual_scope_visible_body")
    if (not isinstance(position, Mapping)
            or set(position) != {"x", "y"}
            or any(type(position[k]) is not int for k in ("x", "y"))
            or not isinstance(body, Mapping)):
        return None
    # The prebody selector has already verified all four bodily components,
    # their finiteness and physical concordance. Do not export the hidden
    # wake reason, sleep-state owner or raw technical payload.
    return {
        "source_event_ref": capture.event_id,
        "t_monde": t_monde,
        "position": {k: position[k] for k in ("x", "y")},
        "body_perceived": {
            k: float(body[k])
            for k in ("energy", "food", "water", "integrity")
        },
    }


def candidate_versioned_waking_perception(
    *, journal, t_monde: int, attempt_ref: str,
    command_ref: str, physical_ref: str,
) -> dict[str, object] | None:
    """DORMANT: a versioned, strictly perceptual candidate; never DC-09 output.

    A caller may inspect this only after an actual physical transition.
    It does not publish an event, mutate an owner, or label the elapsed sleep
    interval as remembered. Every returned field is either a stable source
    reference or part of the authenticated first-person sensory capture.
    """
    from math import isfinite

    candidate = attested_postwake_perceptual_body(
        journal=journal, t_monde=t_monde, attempt_ref=attempt_ref,
        command_ref=command_ref, physical_ref=physical_ref,
    )
    if candidate is None:
        return None
    if set(candidate) != {
        "source_event_ref", "t_monde", "position", "body_perceived",
    }:
        return None
    source = candidate["source_event_ref"]
    position = candidate["position"]
    body = candidate["body_perceived"]
    keys = ("energy", "food", "water", "integrity")
    if (type(source) is not str or not source
            or type(candidate["t_monde"]) is not int
            or candidate["t_monde"] != t_monde
            or not isinstance(position, dict)
            or set(position) != {"x", "y"}
            or any(type(position[k]) is not int for k in ("x", "y"))
            or not isinstance(body, dict) or set(body) != set(keys)
            or any(type(body[k]) not in (int, float)
                   or not isfinite(body[k]) or not 0 <= body[k] <= 100
                   for k in keys)):
        return None
    return {
        "schema": "i1-perceived-waking-body-candidate-v1",
        "source_event_ref": source,
        "t_monde": t_monde,
        "position": {k: int(position[k]) for k in ("x", "y")},
        "body_perceived": {k: float(body[k]) for k in keys},
    }


# DORMANT: not registered with JournalViews, Memory or natural I1 birth.
# This policy describes only fields already present in the first-person
# sensory capture. It intentionally does not authorize Stage10 wake labels.
DORMANT_WAKING_BODY_POLICY = AutobiographicalPolicy(
    version="i1-first-person-waking-body-v1",
    allowed_fields_by_kind={
        "waking_body_perceived": (
            "t_monde", "position", "body_perceived",
        ),
    },
)
