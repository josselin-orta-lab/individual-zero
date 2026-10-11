"""Authorized autobiographical journal views for MVP v1.3.1.

The complete technical journal remains I0's append-only causal trace.
Autobiographical knowledge is projected only via explicit AutoSegmentCommit.
Scientific EvaluationTrace is loaded lazily from an external-only module.

Spec: 17.4-17.5, DC-09, INV-02, INV-27, INV-44, INV-49.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from .determinism import deterministic_id
from .epistemic_guard import project_lived_field, validate_lived_field_name
from .journal import HashChainedJournal, JournalEntry


@dataclass(frozen=True, slots=True)
class AutobiographicalPolicy:
    """Versioned allowlist and projection fields for perceptible event kinds."""

    version: str
    allowed_fields_by_kind: Mapping[str, tuple[str, ...]]

    def validate(self) -> None:
        if not self.version:
            raise ValueError("autobiographical policy version must not be empty")
        for kind, fields in self.allowed_fields_by_kind.items():
            if not kind:
                raise ValueError("autobiographical event kind must not be empty")
            if len(fields) != len(set(fields)):
                raise ValueError(f"duplicate projection field for kind {kind!r}")
            for field in fields:
                validate_lived_field_name(field)

    def allows(self, event: JournalEntry) -> bool:
        kind = event.causal_event.get("kind")
        return isinstance(kind, str) and kind in self.allowed_fields_by_kind

    def project(self, event: JournalEntry) -> dict[str, object]:
        kind = event.causal_event.get("kind")
        if not isinstance(kind, str) or kind not in self.allowed_fields_by_kind:
            raise ValueError("event kind is not autobiographically allowed")
        projected = {"event_id": event.event_id, "kind": kind}
        for field in self.allowed_fields_by_kind[kind]:
            # The technical occurrence identity belongs to JournalEntry,
            # not to any producer-supplied field within the causal payload.
            if field == "event_id":
                continue
            if field in event.causal_event:
                projected[field] = project_lived_field(
                    kind=kind, field=field, value=event.causal_event[field],
                )
        return projected


@dataclass(frozen=True, slots=True)
class AutoSegmentCommit:
    event_id: str
    t_monde: int
    attempt_ref: str
    event_refs: tuple[str, ...]
    filter_version: str


class JournalViews:
    """Read projections over one immutable technical journal."""

    def __init__(self, *, journal: HashChainedJournal) -> None:
        self._journal = journal
        self._commit_event_ids = [
            entry.event_id
            for entry in journal.entries
            if entry.causal_event.get("kind") == "auto_segment_commit"
        ]
        self._commit_sequence = len(self._commit_event_ids)

    def technical(self) -> tuple[JournalEntry, ...]:
        return self._journal.entries

    def commit_autobiographical(
        self,
        *,
        t_monde: int,
        attempt_ref: str,
        event_refs: Sequence[str],
        policy: AutobiographicalPolicy,
    ) -> AutoSegmentCommit:
        policy.validate()
        if t_monde < 0:
            raise ValueError("t_monde must be non-negative")
        if not attempt_ref:
            raise ValueError("attempt_ref must not be empty")
        if len(event_refs) != len(set(event_refs)):
            raise ValueError("AutoSegmentCommit event references must be unique")

        validated: list[str] = []
        for event_ref in event_refs:
            entry = self._journal.get(event_ref)
            if entry is None:
                raise ValueError(f"unknown technical event reference: {event_ref}")
            entry_attempt = entry.causal_event.get("attempt_ref")
            if entry_attempt != attempt_ref:
                raise ValueError("autobiographical commit cannot cross attempts")
            if not policy.allows(entry):
                raise ValueError(
                    f"technical event kind is not autobiographically allowed: "
                    f"{entry.causal_event.get('kind')!r}"
                )
            if entry.causal_event.get("t_monde") != t_monde:
                raise ValueError("autobiographical source world step mismatch")
            # Check the entire authorized nested projection before publishing
            # the append-only commitment, not only at the next Memory read.
            policy.project(entry)
            validated.append(event_ref)

        commit_event_id = deterministic_id(
            "journal-event-v1",
            "autobiographical-view",
            t_monde,
            attempt_ref,
            self._commit_sequence,
            tuple(validated),
            policy.version,
        )
        self._journal.append(
            event_id=commit_event_id,
            causal_event={
                "emitter": "journal",
                "kind": "auto_segment_commit",
                "t_monde": t_monde,
                "attempt_ref": attempt_ref,
                "event_refs": validated,
                "filter_version": policy.version,
            },
        )
        self._commit_sequence += 1
        self._commit_event_ids.append(commit_event_id)
        return AutoSegmentCommit(
            event_id=commit_event_id,
            t_monde=t_monde,
            attempt_ref=attempt_ref,
            event_refs=tuple(validated),
            filter_version=policy.version,
        )

    def autobiographical(
        self,
        *,
        policies: Mapping[str, AutobiographicalPolicy],
    ) -> tuple[dict[str, object], ...]:
        projected: list[dict[str, object]] = []

        for commit_event_id in self._commit_event_ids:
            entry = self._journal.get(commit_event_id)
            if entry is None:
                raise ValueError("autobiographical commit index references unknown event")

            version = entry.causal_event.get("filter_version")
            refs = entry.causal_event.get("event_refs")
            attempt = entry.causal_event.get("attempt_ref")
            t_monde = entry.causal_event.get("t_monde")
            if (
                entry.causal_event.get("kind") != "auto_segment_commit"
                or not isinstance(version, str)
                or not isinstance(attempt, str) or not attempt
                or type(t_monde) is not int
                or not isinstance(refs, list)
                or any(not isinstance(ref, str) for ref in refs)
                or len(refs) != len(set(refs))
            ):
                raise ValueError("malformed AutoSegmentCommit in technical journal")
            policy = policies.get(version)
            if policy is None:
                raise ValueError(
                    f"missing autobiographical policy version: {version}"
                )
            policy.validate()

            for event_ref in refs:
                source = self._journal.get(event_ref)
                if source is None or source.index >= entry.index:
                    raise ValueError("AutoSegmentCommit references missing/future event")
                if (
                    source.causal_event.get("attempt_ref") != attempt
                    or source.causal_event.get("t_monde") != t_monde
                    or not policy.allows(source)
                ):
                    raise ValueError("illegal autobiographical source provenance")
                projected.append(policy.project(source))

        return tuple(projected)



def __getattr__(name: str):
    """Backward-compatible lazy scientific facade, never eagerly loaded by I0."""
    if name in {"EvaluationTrace", "EvaluationRecord"}:
        from .evaluation_trace import EvaluationTrace, EvaluationRecord

        return {
            "EvaluationTrace": EvaluationTrace,
            "EvaluationRecord": EvaluationRecord,
        }[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return sorted(set(globals()) | {"EvaluationTrace", "EvaluationRecord"})
