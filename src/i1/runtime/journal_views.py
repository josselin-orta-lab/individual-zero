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
from .epistemic_guard import (
    project_lived_field, validate_lived_kind_fields,
)
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
            validate_lived_kind_fields(kind, fields)
            if len(fields) != len(set(fields)):
                raise ValueError(f"duplicate projection field for kind {kind!r}")

    def allows(self, event: JournalEntry) -> bool:
        kind = event.causal_event.get("kind")
        return isinstance(kind, str) and kind in self.allowed_fields_by_kind

    def project(self, event: JournalEntry) -> dict[str, object]:
        # Also protect direct policy.project callers, not only the
        # JournalViews commit/read entrypoints which validate policies.
        self.validate()
        return self._project_validated(event)

    def _project_validated(self, event: JournalEntry) -> dict[str, object]:
        """Internal fast path: caller validated this exact policy already.

        No exemption from the event-kind or lived-field epistemic guards.
        Direct callers must keep using project(), which always validates.
        """
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
        self._i1_prebody_birth_enabled = False
        # Rehydrate in journal order without materializing the complete
        # technical history. The reverse iterator is read-only and covers
        # every original occurrence; only committed autobiographical IDs
        # are retained, in their original chronological order.
        self._commit_event_ids = [
            entry.event_id
            for entry in journal.iter_entries_reversed()
            if entry.causal_event.get("kind") == "auto_segment_commit"
        ]
        self._commit_event_ids.reverse()
        self._commit_sequence = len(self._commit_event_ids)
        self._committed_source_refs: set[str] = set()
        self._source_commit_id: dict[str, str] = {}
        for commit_id in self._commit_event_ids:
            entry = journal.get(commit_id)
            refs = None if entry is None else entry.causal_event.get("event_refs")
            if (type(refs) is not list
                    or any(type(ref) is not str or not ref for ref in refs)
                    or len(refs) != len(set(refs))
                    or any(ref in self._committed_source_refs for ref in refs)):
                raise ValueError("invalid or duplicated historical autobiography custody")
            self._committed_source_refs.update(refs)
            for ref in refs:
                self._source_commit_id[ref] = commit_id

    def enable_i1_prebody_at_birth(self) -> None:
        """Enable the canonical I1 DC-09 selection only on a pristine birth."""
        if (self._i1_prebody_birth_enabled
                or self._journal.entry_count != 0
                or self._commit_sequence != 0):
            raise RuntimeError("I1 prebody DC-09 requires one fresh birth")
        self._i1_prebody_birth_enabled = True

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
        # The physical transition already exists in the append-only journal.
        # Only the canonical born I1 enables this versioned post-action gate.
        # A reduced sleep continuation has no full Stage3 bodily capture and
        # therefore retains the historical projection automatically.
        if (self._i1_prebody_birth_enabled
                and policy.version == "stage7-autobio-v1"
                and len(event_refs) >= 2):
            from .i1_natural_prebody_policy import (
                policy_for_proven_prebody_transition,
            )
            policy = policy_for_proven_prebody_transition(
                journal=self._journal, t_monde=t_monde,
                attempt_ref=attempt_ref, command_ref=event_refs[-2],
                physical_ref=event_refs[-1],
            )
        # Birth-gated I1-only post-physical sensory event. It is authored
        # here, not by Memory, only if the one captured waking body matched
        # the applied physical prebody AND same-attempt Stage10 wake receipts.
        # A bare technical wake label is not an autobiographical source.
        if (self._i1_prebody_birth_enabled
                and policy.version == "i1-lived-body-before-v1"
                and len(event_refs) >= 2):
            from .i1_natural_prebody_policy import (
                candidate_versioned_waking_perception,
                LIVED_WAKING_BODY_POLICY,
            )
            cue = candidate_versioned_waking_perception(
                journal=self._journal, t_monde=t_monde,
                attempt_ref=attempt_ref, command_ref=event_refs[-2],
                physical_ref=event_refs[-1],
            )
            if cue is not None:
                cue_ref = deterministic_id(
                    "journal-event-v1", "i1-first-person-wake",
                    t_monde, attempt_ref,
                    cue["source_event_ref"], event_refs[-1],
                )
                self._journal.append(
                    event_id=cue_ref,
                    causal_event={
                        "kind": "waking_body_perceived",
                        "emitter": "i1-first-person-wake",
                        "t_monde": t_monde,
                        "attempt_ref": attempt_ref,
                        "position": dict(cue["position"]),
                        "body_perceived": dict(cue["body_perceived"]),
                    },
                )
                event_refs = tuple(event_refs) + (cue_ref,)
                policy = LIVED_WAKING_BODY_POLICY
        policy.validate()
        if t_monde < 0:
            raise ValueError("t_monde must be non-negative")
        if not attempt_ref:
            raise ValueError("attempt_ref must not be empty")
        if len(event_refs) != len(set(event_refs)):
            raise ValueError("AutoSegmentCommit event references must be unique")

        if any(ref in self._committed_source_refs for ref in event_refs):
            raise ValueError("autobiographical event already committed")
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
            if entry.causal_event.get("kind") == "waking_body_perceived":
                # Never let a custom policy commit a forged sensory event.
                # Require the unique produced event as the final source,
                # and independently re-check the capture and physical chain.
                from .i1_natural_prebody_policy import (
                    candidate_versioned_waking_perception,
                    LIVED_WAKING_BODY_POLICY,
                )
                if (policy.version != LIVED_WAKING_BODY_POLICY.version
                        or event_ref != event_refs[-1]
                        or len(event_refs) < 3):
                    raise ValueError("unproven waking cue commit")
                original_command, original_physical = (
                    event_refs[-3], event_refs[-2])
                cue = candidate_versioned_waking_perception(
                    journal=self._journal, t_monde=t_monde,
                    attempt_ref=attempt_ref,
                    command_ref=original_command,
                    physical_ref=original_physical,
                )
                if (cue is None
                        or event_ref != deterministic_id(
                            "journal-event-v1", "i1-first-person-wake",
                            t_monde, attempt_ref,
                            cue["source_event_ref"], original_physical)
                        or entry.causal_event.get("emitter")
                           != "i1-first-person-wake"
                        or entry.causal_event.get("position")
                           != cue["position"]
                        or entry.causal_event.get("body_perceived")
                           != cue["body_perceived"]):
                    raise ValueError("forged waking cue provenance")
            # Check the entire authorized nested projection before publishing
            # the append-only commitment, not only at the next Memory read.
            if type(policy) is AutobiographicalPolicy:
                policy._project_validated(entry)
            else:
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
        self._committed_source_refs.update(validated)
        for ref in validated:
            self._source_commit_id[ref] = commit_event_id
        return AutoSegmentCommit(
            event_id=commit_event_id,
            t_monde=t_monde,
            attempt_ref=attempt_ref,
            event_refs=tuple(validated),
            filter_version=policy.version,
        )

    def selected_committed_autobiography(
        self, *, policies: Mapping[str, AutobiographicalPolicy],
        selected_event_refs: frozenset[str],
        max_verified_sources: int = 4096,
    ) -> tuple[dict[str, object], ...]:
        """Bounded *scoped* DC-09 projection of committed source identities.

        This validates every source in each touched commitment, but unlike
        autobiographical() does NOT audit unrelated historical commitments.
        The selecting Memory owner and its caller must pay UC separately;
        possession of a source ref grants no cognitive or motor permission.
        """
        if (type(max_verified_sources) is not int
                or not 1 <= max_verified_sources <= 4096):
            raise ValueError("invalid scoped DC-09 source verification limit")
        if (type(selected_event_refs) is not frozenset
                or len(selected_event_refs) > min(64, max_verified_sources)
                or any(type(ref) is not str or not ref
                       for ref in selected_event_refs)):
            raise ValueError("invalid bounded selected autobiographical refs")
        if not selected_event_refs:
            return ()
        commit_ids = set()
        for ref in selected_event_refs:
            commit_id = self._source_commit_id.get(ref)
            if commit_id is None:
                raise ValueError("uncommitted autobiographical source")
            commit_ids.add(commit_id)
        if len(commit_ids) > 64:
            raise ValueError("too many selected autobiographical commits")
        projected = []
        touched = []
        validated_policies = set()
        source_count = 0
        for commit_id in commit_ids:
            entry = self._journal.get(commit_id)
            if entry is None:
                raise ValueError("missing autobiographical commitment")
            kind = entry.causal_event.get("kind")
            version = entry.causal_event.get("filter_version")
            refs = entry.causal_event.get("event_refs")
            attempt = entry.causal_event.get("attempt_ref")
            t_monde = entry.causal_event.get("t_monde")
            if (kind != "auto_segment_commit"
                    or type(version) is not str
                    or type(attempt) is not str or not attempt
                    or type(t_monde) is not int
                    or type(refs) is not list
                    or any(type(ref) is not str or not ref for ref in refs)
                    or len(set(refs)) != len(refs)
                    or len(refs) > 64):
                raise ValueError("malformed touched autobiographical commitment")
            policy = policies.get(version)
            if policy is None:
                raise ValueError("missing touched autobiographical policy")
            if version not in validated_policies or type(policy) is not AutobiographicalPolicy:
                policy.validate()
                validated_policies.add(version)
            source_count += len(refs)
            if source_count > max_verified_sources:
                raise ValueError("bounded autobiographical scan exhausted")
            local = []
            for ref in refs:
                source = self._journal.get(ref)
                if (self._source_commit_id.get(ref) != commit_id
                        or source is None or source.index >= entry.index
                        or source.causal_event.get("attempt_ref") != attempt
                        or source.causal_event.get("t_monde") != t_monde
                        or not policy.allows(source)):
                    raise ValueError("invalid touched first-person provenance")
                # Check nested DC-09 projection on *every* source of a
                # touched commitment, including unselected ones. This does
                # not change the global-audit historical reader contract.
                lived = (
                    policy._project_validated(source)
                    if type(policy) is AutobiographicalPolicy
                    else policy.project(source)
                )
                if ref in selected_event_refs:
                    local.append(((entry.index, source.index), lived))
            touched.extend(local)
        # Match the historical chronological commitment/source projection.
        touched.sort(key=lambda row: row[0])
        return tuple(row for _, row in touched)

    def autobiographical(
        self,
        *,
        policies: Mapping[str, AutobiographicalPolicy],
        selected_event_refs: frozenset[str] | None = None,
    ) -> tuple[dict[str, object], ...]:
        if selected_event_refs is not None and (
                type(selected_event_refs) is not frozenset
                or any(type(ref) is not str or not ref
                       for ref in selected_event_refs)):
            raise ValueError("invalid scoped autobiographical refs")
        projected: list[dict[str, object]] = []
        # Exact built-in immutable policies can be validated once per read;
        # custom policy subclasses keep their original validation cadence.
        validated_versions: set[str] = set()

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
            if type(policy) is AutobiographicalPolicy:
                if version not in validated_versions:
                    policy.validate()
                    validated_versions.add(version)
            else:
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
                if (selected_event_refs is None
                        or event_ref in selected_event_refs):
                    projected.append(
                        policy._project_validated(source)
                        if type(policy) is AutobiographicalPolicy
                        else policy.project(source)
                    )

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
