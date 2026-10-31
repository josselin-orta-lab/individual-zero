"""Research-only I2 intention owner; never an action or an authenticated life.

This isolated, deterministic policy persists *semantic* intent across supplied
first-person captures. The caller must independently authenticate observations,
UC charges and any future M11 snapshot. A nonempty work_ref is a correlation
handle, NOT proof of payment. Nothing here chooses or admits motor commands.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from hashlib import sha256
from typing import Mapping

POLICY = "i2-semantic-intention-proposal-v1"
_STATES = frozenset({"active", "suspended"})
_FIELDS = frozenset({"policy", "last_step", "last_capture_ref", "current"})
_RECORD_FIELDS = frozenset({
    "ref", "semantic_ref", "goal_ref", "origin_capture_ref", "origin_evidence_ref",
    "created_step", "last_checked_step", "last_capture_ref", "expires_at_step",
    "status",
})


def _ref(value: object, field: str) -> str:
    if (type(value) is not str or not 1 <= len(value) <= 256
            or not value.isascii() or any(ord(ch) < 33 or ord(ch) > 126 for ch in value)):
        raise ValueError(f"invalid {field}")
    return value


def _step(value: object, name: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(f"invalid {name}")
    return value


def _intention_ref(capture_ref: str, goal_ref: str, semantic_ref: str, evidence_ref: str) -> str:
    raw = "\x1f".join((POLICY, capture_ref, goal_ref, semantic_ref, evidence_ref))
    return "intent:i2:" + sha256(raw.encode("ascii")).hexdigest()


def _semantics(values: object, name: str) -> tuple[str, ...]:
    if (type(values) is not tuple or len(values) > 64
            or any(_ref(value, name) != value for value in values)
            or values != tuple(sorted(set(values)))):
        raise ValueError(f"invalid canonical {name}")
    return values


@dataclass(frozen=True, slots=True)
class FirstPersonCapture:
    """A *caller-asserted* subjective projection, not verified world truth."""

    step: int
    ref: str
    goal_ref: str | None
    accessible_semantics: tuple[str, ...]
    contradicted_semantics: tuple[str, ...] = ()

    def validate(self) -> None:
        _step(self.step, "capture step")
        _ref(self.ref, "capture ref")
        if self.goal_ref is not None:
            _ref(self.goal_ref, "goal ref")
        a = _semantics(self.accessible_semantics, "accessible semantics")
        b = _semantics(self.contradicted_semantics, "contradicted semantics")
        if set(a).intersection(b):
            raise ValueError("affordance simultaneously accessible and contradicted")


@dataclass(frozen=True, slots=True)
class SemanticIntention:
    """No option ID, accumulator, command, threshold or motor authority."""

    ref: str
    semantic_ref: str
    goal_ref: str
    origin_capture_ref: str
    origin_evidence_ref: str
    created_step: int
    last_checked_step: int
    last_capture_ref: str
    expires_at_step: int
    status: str

    def validate(self) -> None:
        for field in ("ref", "semantic_ref", "goal_ref", "origin_capture_ref",
                      "origin_evidence_ref", "last_capture_ref"):
            _ref(getattr(self, field), field)
        created = _step(self.created_step, "created step")
        checked = _step(self.last_checked_step, "checked step")
        expiry = _step(self.expires_at_step, "expiry step")
        if (checked < created or expiry <= checked or expiry - created > 64
                or type(self.status) is not str or self.status not in _STATES
                or self.ref != _intention_ref(self.origin_capture_ref, self.goal_ref,
                                              self.semantic_ref, self.origin_evidence_ref)):
            raise ValueError("invalid intention timeline or status")


@dataclass(frozen=True, slots=True)
class IntentionTransition:
    kind: str
    step: int
    capture_ref: str
    intention_ref: str | None
    work_ref: str


class IntentionContinuity:
    """One-slot source-only owner, with no birth or motor dispatch interface.

    One charged cognitive update is *asserted* per distinct capture. No owner
    authenticates work_ref: an integrating runtime MUST validate real UC debit
    and first-person evidence before calling. This is not M11 recovery.
    """

    def __init__(self) -> None:
        self._current: SemanticIntention | None = None
        self._last_step = -1
        self._last_capture_ref: str | None = None

    @property
    def current(self) -> SemanticIntention | None:
        return self._current

    def _fresh(self, capture: FirstPersonCapture, work_ref: str) -> None:
        if type(capture) is not FirstPersonCapture:
            raise ValueError("first-person capture required")
        capture.validate()
        _ref(work_ref, "UC work correlation ref")
        if capture.step <= self._last_step or capture.ref == self._last_capture_ref:
            raise ValueError("stale or repeated capture")

    def _clock(self, capture: FirstPersonCapture) -> None:
        self._last_step = capture.step
        self._last_capture_ref = capture.ref

    def open(
        self, *, capture: FirstPersonCapture, semantic_ref: str,
        evidence_ref: str, ttl_steps: int, work_ref: str,
    ) -> IntentionTransition:
        self._fresh(capture, work_ref)
        semantic = _ref(semantic_ref, "semantic ref")
        evidence = _ref(evidence_ref, "personally observed evidence ref")
        if type(ttl_steps) is not int or not 1 <= ttl_steps <= 64:
            raise ValueError("TTL must be a bounded positive physical duration")
        if self._current is not None:
            raise ValueError("active/suspended intention cannot be overwritten")
        if capture.goal_ref is None or semantic not in capture.accessible_semantics:
            raise ValueError("intent must arise from currently observed affordance and goal")
        # An ID is bound to exact observed provenance, not a wall-clock UUID,
        # a motor option ID or a transplanted prior individual's memory.
        ref = _intention_ref(capture.ref, capture.goal_ref, semantic, evidence)
        candidate = SemanticIntention(
            ref=ref, semantic_ref=semantic, goal_ref=capture.goal_ref,
            origin_capture_ref=capture.ref, origin_evidence_ref=evidence,
            created_step=capture.step, last_checked_step=capture.step,
            last_capture_ref=capture.ref, expires_at_step=capture.step + ttl_steps,
            status="active",
        )
        candidate.validate()
        self._current = candidate
        self._clock(capture)
        return IntentionTransition("opened", capture.step, capture.ref, ref, work_ref)

    def observe(self, *, capture: FirstPersonCapture, work_ref: str) -> IntentionTransition:
        self._fresh(capture, work_ref)
        previous = self._current
        current = previous
        kind = "idle"
        if previous is not None:
            if capture.step >= previous.expires_at_step:
                current, kind = None, "expired"
            elif capture.goal_ref != previous.goal_ref:
                current, kind = None, "goal_changed"
            elif previous.semantic_ref in capture.contradicted_semantics:
                current, kind = None, "contradicted"
            else:
                active = previous.semantic_ref in capture.accessible_semantics
                status = "active" if active else "suspended"
                kind = ("resumed" if active and previous.status == "suspended"
                        else "suspended" if not active and previous.status == "active"
                        else "retained" if active else "still_suspended")
                current = replace(previous, status=status,
                                  last_checked_step=capture.step,
                                  last_capture_ref=capture.ref)
                current.validate()
        self._current = current
        self._clock(capture)
        return IntentionTransition(
            kind, capture.step, capture.ref,
            None if previous is None else previous.ref, work_ref,
        )

    def export_state(self) -> dict[str, object]:
        """Plain-data serialization, NOT an M11-signed recovery image."""
        record = self._current
        return {
            "policy": POLICY, "last_step": self._last_step,
            "last_capture_ref": self._last_capture_ref,
            "current": None if record is None else {
                field: getattr(record, field) for field in sorted(_RECORD_FIELDS)
            },
        }

    @classmethod
    def from_untrusted_snapshot(cls, snapshot: Mapping[str, object]) -> IntentionContinuity:
        """Parse atomically, fail closed; caller MUST authenticate M11 externally."""
        if type(snapshot) is not dict or set(snapshot) != _FIELDS or snapshot["policy"] != POLICY:
            raise ValueError("unexpected intention snapshot fields or policy")
        step = snapshot["last_step"]
        if type(step) is not int or step < -1:
            raise ValueError("invalid owner step")
        capture_ref = snapshot["last_capture_ref"]
        if (step == -1) != (capture_ref is None):
            raise ValueError("invalid empty owner clock")
        if capture_ref is not None:
            _ref(capture_ref, "owner capture ref")
        raw = snapshot["current"]
        record = None
        if raw is not None:
            if type(raw) is not dict or set(raw) != _RECORD_FIELDS:
                raise ValueError("unexpected intention fields")
            record = SemanticIntention(**raw)
            record.validate()
            if record.last_checked_step != step or record.last_capture_ref != capture_ref:
                raise ValueError("owner and intention timelines disagree")
        result = cls()
        result._last_step = step
        result._last_capture_ref = capture_ref
        result._current = record
        return result