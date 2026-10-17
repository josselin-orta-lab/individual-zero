"""Independent audit of the *external* Stage12 operator's causal controls.

A valid hash chain proves tamper evidence relative to its trusted tail, not
that the reported operator policy or its stop sequence is coherent. This
module reconstructs the versioned console state from event records without
importing I0 cognition, MortalWorldBoundary, WorldBody, Oracle or Bench.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json

from .independent_journal_audit import audit_export_bytes


_CONTROL_KINDS = frozenset({
    "operator_console_configured",
    "operator_step_cap_set",
    "experiment_stopped",
})
_NAMESPACE = "stage12-external-operator-event-v1"


@dataclass(frozen=True, slots=True)
class Stage12OperatorControlAudit:
    head_hash: str
    occurrences: int
    configured: bool
    mode: str | None
    policy_version: str | None
    maximum_world_steps: int | None
    cap_changes: int
    operator_events: int
    last_closed_step: int
    experiment_stopped: bool
    stop_reason: str | None

    def as_dict(self) -> dict[str, object]:
        return {
            "schema": "stage12-independent-operator-control-audit-v1",
            "head_hash": self.head_hash,
            "occurrences": self.occurrences,
            "configured": self.configured,
            "mode": self.mode,
            "policy_version": self.policy_version,
            "maximum_world_steps": self.maximum_world_steps,
            "cap_changes": self.cap_changes,
            "operator_events": self.operator_events,
            "last_closed_step": self.last_closed_step,
            "experiment_stopped": self.experiment_stopped,
            "stop_reason": self.stop_reason,
            "operator_intent_independently_verified": False,
        }


def _independent_event_id(
    version: str, world_step: int, kind: str, ordinal: int,
) -> str:
    """Independent reproduction of the normative deterministic ID payload.

    The arguments are only canonical strings and integers. The full export
    has already passed strict Unicode, JSON byte canonicality and hash-chain
    verification by audit_export_bytes().
    """
    payload = [_NAMESPACE, version, world_step, kind, ordinal]
    canonical = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return sha256(canonical).hexdigest()


def audit_stage12_operator_control(
    content: bytes, *, expected_head: str | None = None,
    expected_count: int | None = None,
) -> Stage12OperatorControlAudit:
    base = audit_export_bytes(
        content, expected_head=expected_head, expected_count=expected_count,
    )
    configured = stopped = inside_step = False
    mode: str | None = None
    version: str | None = None
    cap: int | None = None
    cap_changes = events_seen = last_closed = 0
    stop_reason: str | None = None

    for line in content.split(b"\n"):
        row = json.loads(line)
        event = row["causal_event"]
        kind = event["kind"]
        if stopped:
            raise ValueError("causal event occurred after operator stop")
        if kind == "step_opened":
            if inside_step:
                raise ValueError("nested physical attempt during operator audit")
            inside_step = True
            t = event["t_monde"]
            if cap is not None and t > cap:
                raise ValueError("physical step opened beyond the operator's cap")
        elif kind == "step_closed":
            if not inside_step:
                raise ValueError("physical closure without prior attempt")
            inside_step = False
            last_closed = event["t_monde"]

        if kind not in _CONTROL_KINDS:
            if event.get("emitter") == "operator_console":
                raise ValueError("unversioned external operator event")
            continue

        data = event.get("data")
        t = event.get("t_monde")
        if (inside_step or event.get("emitter") != "operator_console"
                or "attempt_ref" in event
                or type(t) is not int or t != last_closed
                or type(data) is not dict):
            raise ValueError("operator control must be at the closed step boundary")

        if kind == "operator_console_configured":
            if configured or events_seen != 0 or set(data) != {
                "mode", "policy_version",
            }:
                raise ValueError("duplicate or invalid operator configuration")
            new_mode, new_version = data["mode"], data["policy_version"]
            if (new_mode not in ("diagnostic", "campaign")
                    or type(new_version) is not str or not new_version.strip()):
                raise ValueError("invalid external operator policy")
            mode, version, configured = new_mode, new_version, True
        elif not configured:
            raise ValueError("operator action has no earlier configuration")
        elif kind == "operator_step_cap_set":
            if set(data) != {"maximum_world_steps", "previous_cap", "policy_version"}:
                raise ValueError("invalid operator step-cap receipt")
            requested = data["maximum_world_steps"]
            if (data["policy_version"] != version
                    or type(requested) is not int or requested < 1
                    or requested < t
                    or data["previous_cap"] != cap
                    or (cap is not None and requested > cap)):
                raise ValueError("operator step cap was raised, forged or set in the past")
            cap = requested
            cap_changes += 1
        elif kind == "experiment_stopped":
            if set(data) != {
                "reason", "policy_version", "mode", "maximum_world_steps",
                "world_rewound", "physical_death",
            }:
                raise ValueError("invalid external terminal stop receipt")
            reason = data["reason"]
            if (type(reason) is not str or not reason.strip()
                    or data["policy_version"] != version
                    or data["mode"] != mode
                    or data["maximum_world_steps"] != cap
                    or data["world_rewound"] is not False
                    or data["physical_death"] is not False):
                raise ValueError("external terminal stop conflicts with operator state")
            if reason == "world_step_cap_reached" and (
                cap is None or cap != t
            ):
                raise ValueError("cap-reached operator stop has an incorrect world step")
            if reason == "campaign_safety_block" and mode != "campaign":
                raise ValueError("campaign safety stop has an incorrect operator mode")
            stop_reason, stopped = reason, True

        # Control event identity includes policy, step, type, and strictly
        # contiguous ordinal, making omitted/reordered control receipts
        # detectable even when an attacker recomputes the entire hash chain.
        if version is None or row["event_id"] != _independent_event_id(
            version, t, kind, events_seen,
        ):
            raise ValueError("operator control identity or sequence was forged")
        events_seen += 1

    return Stage12OperatorControlAudit(
        head_hash=base.head_hash, occurrences=base.occurrences,
        configured=configured, mode=mode, policy_version=version,
        maximum_world_steps=cap, cap_changes=cap_changes,
        operator_events=events_seen, last_closed_step=last_closed,
        experiment_stopped=stopped, stop_reason=stop_reason,
    )
