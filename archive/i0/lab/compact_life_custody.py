"""Bounded in-memory custody replacing historical technical event retention.

These are runtime-to-cognition interfaces, not a complete life journal:
- only authorized, physically accepted lived events reach Memory;
- only typed, causally ordered online owner updates remain until the Stage-10
  consolidation publisher confirms that they were consumed;
- no event history, oracle, WorldBody snapshot, rollback or persisted replay.

The existing runtime is migrated to these interfaces in later PRs, only after
consumer parity is demonstrated. Capacity exhaustion must stop and report,
never silently discard a lived event or a post-cut learning update.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Mapping, Sequence

from .determinism import canonical_causal_bytes, sha256_hex
from .journal_views import AutobiographicalPolicy
from .epistemic_guard import project_lived_field


@dataclass(frozen=True, slots=True)
class FrozenOnlineUpdate:
    """Copy of an already-published online owner update, not a new observation."""

    owner_id: str
    event_id: str
    t_monde: int
    kind: str
    payload: Mapping[str, object]


@dataclass(frozen=True, slots=True)
class FrozenDeltaWindow:
    cut_world_step: int
    last_sequence: int
    updates: tuple[FrozenOnlineUpdate, ...]
    digest: str


class BoundedLivedStream:
    """Delivery queue of only lived and policy-authorized step events.

    The physical dispatcher must invoke commit_step only AFTER a nonterminal
    world transition is accepted. There is no technical journal lookup here.
    """

    def __init__(
        self, *, policy: AutobiographicalPolicy, max_pending_events: int,
    ) -> None:
        policy.validate()
        if type(max_pending_events) is not int or max_pending_events < 2:
            raise ValueError("lived queue capacity must be at least two")
        self._policy = policy
        self._limit = max_pending_events
        self._pending: list[dict[str, object]] = []
        self._last_step = 0
        self._terminal = False

    @property
    def pending_count(self) -> int:
        return len(self._pending)

    @property
    def last_step(self) -> int:
        return self._last_step

    def commit_step(
        self,
        *, t_monde: int, attempt_ref: str,
        experienced: Sequence[tuple[str, Mapping[str, object]]],
    ) -> None:
        if self._terminal:
            raise RuntimeError("terminal life cannot publish lived events")
        if type(t_monde) is not int or t_monde != self._last_step + 1:
            raise ValueError("lived steps must be strictly consecutive")
        if type(attempt_ref) is not str or not attempt_ref:
            raise ValueError("lived step requires its actual attempt reference")

        committed: list[dict[str, object]] = []
        seen_ids: set[str] = set()
        observed_kinds: list[str] = []
        for event_id, source in experienced:
            if type(event_id) is not str or not event_id or event_id in seen_ids:
                raise ValueError("invalid or duplicate lived event reference")
            seen_ids.add(event_id)
            if not isinstance(source, Mapping):
                raise ValueError("lived source must be an event mapping")
            kind = source.get("kind")
            if type(kind) is not str or kind not in self._policy.allowed_fields_by_kind:
                raise ValueError("non-autobiographical event cannot enter Memory")
            if source.get("t_monde") != t_monde or source.get("attempt_ref") != attempt_ref:
                raise ValueError("lived event is not from this committed world step")
            observed_kinds.append(kind)
            projected: dict[str, object] = {"event_id": event_id, "kind": kind}
            for field in self._policy.allowed_fields_by_kind[kind]:
                if field != "event_id" and field in source:
                    projected[field] = project_lived_field(
                        kind=kind, field=field, value=source[field],
                    )
            # Reject non-causal objects before modifying queue or cursor.
            canonical_causal_bytes(projected)
            committed.append(projected)

        if (observed_kinds.count("command_experienced") != 1
                or observed_kinds.count("world_transition_experienced") != 1):
            raise ValueError("exactly one real command and world result required")
        if len(self._pending) + len(committed) > self._limit:
            raise RuntimeError("lived events not yet consumed; no silent eviction")
        self._pending.extend(committed)
        self._last_step = t_monde

    def drain_for_memory(self) -> tuple[dict[str, object], ...]:
        """Hand over owned projections; no complete-life archive retained."""
        if self._terminal:
            raise RuntimeError("no postmortem cognitive consumption")
        result = deepcopy(tuple(self._pending))
        self._pending.clear()
        return result

    def seal_terminal(self) -> None:
        """No new memories or later consolidation after this individual's death."""
        self._terminal = True
        self._pending.clear()


# Emitter-to-owner mapping mirrors the *existing* Stage-10 published update
# semantics; arbitrary Lab metrics, hidden truth, or trial events are rejected.
_ONLINE_OWNER_KINDS = {
    "value_needs": frozenset({"td_update_published"}),
    "metacognition_health": frozenset({"kappa_update_published"}),
    "perception": frozenset({"perceptual_precision_update_published"}),
    "causal_model": frozenset({
        "causal_inference_status_published",
        "causal_safety_status_published",
        "causal_prediction_corrections_published",
    }),
}
_STAGE4_OWNER_KINDS = {
    ("stage4-runtime", "kappa_update_published"): "metacognition_health",
    ("stage4-runtime", "causal_inference_status_published"): "causal_model",
    ("stage4-runtime", "causal_safety_status_published"): "causal_model",
    ("stage4-runtime", "causal_prediction_corrections_published"): "causal_model",
}


class BoundedPostCutDeltas:
    """Only temporary, verified-local online updates for a private Stage-10 rebase.

    A freeze is a consistency token. Publishing a prepared consolidation
    requires confirmation that no new owner update arrived meanwhile. Nothing
    here restores committed cognition or creates a learned event.
    """

    def __init__(self, *, max_pending_updates: int) -> None:
        if type(max_pending_updates) is not int or max_pending_updates < 1:
            raise ValueError("post-cut capacity must be positive")
        self._limit = max_pending_updates
        self._cut_step: int | None = None
        self._last_t: int | None = None
        self._sequence = 0
        self._updates: list[FrozenOnlineUpdate] = []
        self._seen: set[str] = set()
        self._terminal = False

    @property
    def pending_count(self) -> int:
        return len(self._updates)

    def begin_cut(self, *, world_step: int) -> None:
        if self._terminal:
            raise RuntimeError("terminal life cannot begin consolidation")
        if self._cut_step is not None or self._updates:
            raise RuntimeError("previous cut has not been committed")
        if type(world_step) is not int or world_step < 1:
            raise ValueError("invalid physical consolidation cut")
        self._cut_step = world_step
        self._last_t = world_step
        self._sequence += 1

    def append_published_update(
        self,
        *, emitter: str, kind: str, event_id: str,
        t_monde: int, payload: Mapping[str, object],
    ) -> None:
        if self._terminal:
            raise RuntimeError("terminal life cannot learn")
        if self._cut_step is None:
            raise RuntimeError("online delta needs an active cut")
        if type(t_monde) is not int or t_monde < self._last_t:
            raise ValueError("post-cut update would violate causal ordering")
        if type(event_id) is not str or not event_id or event_id in self._seen:
            raise ValueError("duplicate or invalid post-cut update")
        owner = _STAGE4_OWNER_KINDS.get((emitter, kind))
        if owner is None and kind in _ONLINE_OWNER_KINDS.get(emitter, frozenset()):
            owner = emitter
        if owner is None or not isinstance(payload, Mapping):
            raise ValueError("unrecognized online owner update")
        if len(self._updates) >= self._limit:
            raise RuntimeError("unconsumed online deltas; no silent loss")

        copied = deepcopy(dict(payload))
        canonical_causal_bytes(copied)
        new = FrozenOnlineUpdate(
            owner_id=owner, event_id=event_id, t_monde=t_monde,
            kind=kind, payload=copied,
        )
        self._updates.append(new)
        self._seen.add(event_id)
        self._last_t = t_monde
        self._sequence += 1

    def freeze(self) -> FrozenDeltaWindow:
        if self._terminal or self._cut_step is None:
            raise RuntimeError("no active consolidation cut")
        copied = deepcopy(tuple(self._updates))
        digest = sha256_hex(canonical_causal_bytes({
            "cut": self._cut_step,
            "sequence": self._sequence,
            "updates": [
                {
                    "owner": item.owner_id, "id": item.event_id,
                    "t_monde": item.t_monde, "kind": item.kind,
                    "payload": item.payload,
                }
                for item in copied
            ],
        }))
        return FrozenDeltaWindow(
            cut_world_step=self._cut_step,
            last_sequence=self._sequence,
            updates=copied, digest=digest,
        )

    def acknowledge_published(self, frozen: FrozenDeltaWindow) -> None:
        """Discard only AFTER owner commit; reject stale private candidates."""
        if frozen != self.freeze():
            raise ValueError("post-cut learning changed during private rebase")
        self._updates.clear()
        self._seen.clear()
        self._cut_step = None
        self._last_t = None

    def seal_terminal(self) -> None:
        self._terminal = True
        self._updates.clear()
        self._seen.clear()
        self._cut_step = None
        self._last_t = None
