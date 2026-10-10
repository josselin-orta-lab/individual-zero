"""Journal views and isolated evaluation trace for MVP v1.2.1.

The technical journal remains the single append-only causal trace. The
autobiographical view is a deterministic projection authorized only through
AutoSegmentCommit records. Evaluation data is stored separately.

Spec: 17.4-17.5, DC-09, INV-02, INV-27, INV-44, INV-49.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from .determinism import deterministic_id
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
            if "attempt_ref" in fields:
                raise ValueError("attempt_ref is never autobiographically visible")

    def allows(self, event: JournalEntry) -> bool:
        kind = event.causal_event.get("kind")
        return isinstance(kind, str) and kind in self.allowed_fields_by_kind

    def project(self, event: JournalEntry) -> dict[str, object]:
        kind = event.causal_event.get("kind")
        if not isinstance(kind, str) or kind not in self.allowed_fields_by_kind:
            raise ValueError("event kind is not autobiographically allowed")
        projected = {"event_id": event.event_id, "kind": kind}
        for field in self.allowed_fields_by_kind[kind]:
            if field in event.causal_event:
                projected[field] = event.causal_event[field]
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
        self._commit_sequence += 1
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
            if not isinstance(version, str) or not isinstance(refs, list):
                raise ValueError("malformed AutoSegmentCommit in technical journal")
            policy = policies.get(version)
            if policy is None:
                raise ValueError(
                    f"missing autobiographical policy version: {version}"
                )
            policy.validate()

            for event_ref in refs:
                if not isinstance(event_ref, str):
                    raise ValueError("AutoSegmentCommit references invalid event id")
                source = self._journal.get(event_ref)
                if source is None:
                    raise ValueError("AutoSegmentCommit references unknown event")
                projected.append(policy.project(source))

        return tuple(projected)


@dataclass(frozen=True, slots=True)
class EvaluationRecord:
    sequence: int
    kind: str
    data: Mapping[str, object]


class EvaluationTrace:
    """Separate bench/operator trace, never part of individual causal state."""

    def __init__(self) -> None:
        self._records: list[EvaluationRecord] = []

    @property
    def records(self) -> tuple[EvaluationRecord, ...]:
        return tuple(self._records)

    def append(self, *, kind: str, data: Mapping[str, object]) -> EvaluationRecord:
        if not kind:
            raise ValueError("evaluation record kind must not be empty")
        record = EvaluationRecord(
            sequence=len(self._records),
            kind=kind,
            data=dict(data),
        )
        self._records.append(record)
        return record
