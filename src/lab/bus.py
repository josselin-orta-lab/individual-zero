"""Validated in-memory message bus for normative Stage 1.

The bus owns only transport state. It validates and orders messages but does not
interpret cognitive content or mutate component state.

Spec: 2.2, 3.3, 4.3-4.4, DC-11, INV-35, INV-51.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from .contracts import ContractViolation, OntologyRegistry, SchemaRegistry
from .determinism import deterministic_id
from .journal import HashChainedJournal


@dataclass(frozen=True, slots=True)
class BufferedMessage:
    producer: str
    local_sequence: int
    schema_name: str
    schema_version: str
    payload: Mapping[str, object]
    semantic_terms: tuple[str, ...]


class ProducerBuffer:
    """Local phase buffer owned by exactly one producer."""

    def __init__(self, producer: str) -> None:
        if not producer:
            raise ValueError("producer must not be empty")
        self._producer = producer
        self._next_sequence = 0
        self._messages: list[BufferedMessage] = []

    @property
    def producer(self) -> str:
        return self._producer

    def publish(
        self,
        *,
        schema_name: str,
        schema_version: str,
        payload: Mapping[str, object],
        semantic_terms: Sequence[str] = (),
    ) -> BufferedMessage:
        message = BufferedMessage(
            producer=self._producer,
            local_sequence=self._next_sequence,
            schema_name=schema_name,
            schema_version=schema_version,
            payload=dict(payload),
            semantic_terms=tuple(semantic_terms),
        )
        self._next_sequence += 1
        self._messages.append(message)
        return message

    def drain(self) -> tuple[BufferedMessage, ...]:
        messages = tuple(self._messages)
        self._messages.clear()
        return messages


@dataclass(frozen=True, slots=True)
class ValidatedMessage:
    id: str
    producer: str
    local_sequence: int
    schema_name: str
    schema_version: str
    payload: Mapping[str, object]
    semantic_terms: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "producer": self.producer,
            "local_sequence": self.local_sequence,
            "schema_name": self.schema_name,
            "schema_version": self.schema_version,
            "payload": dict(self.payload),
            "semantic_terms": list(self.semantic_terms),
        }


@dataclass(frozen=True, slots=True)
class AdmissionResult:
    accepted: bool
    message: ValidatedMessage | None
    violation: ContractViolation | None


class InMemoryBus:
    """Single in-memory bus with canonical pouring and deterministic rejection."""

    def __init__(
        self,
        *,
        schemas: SchemaRegistry,
        ontology: OntologyRegistry,
        producer_order: Sequence[str],
        journal: HashChainedJournal,
    ) -> None:
        if not producer_order:
            raise ValueError("producer_order must not be empty")
        if len(producer_order) != len(set(producer_order)):
            raise ValueError("producer_order must contain unique producer ids")

        self._schemas = schemas
        self._ontology = ontology
        self._producer_order = tuple(producer_order)
        self._producer_rank = {
            producer: rank
            for rank, producer in enumerate(self._producer_order)
        }
        self._journal = journal
        self._available: list[ValidatedMessage] = []
        self._event_sequence = 0

    @property
    def available(self) -> tuple[ValidatedMessage, ...]:
        return tuple(self._available)

    @property
    def owner_id(self) -> str:
        return "bus.transport"

    def export_causal_state(self) -> object:
        return {
            "available": [message.as_dict() for message in self._available],
        }

    def restore_causal_state(self, state: object) -> None:
        if not isinstance(state, Mapping):
            raise ValueError("bus causal state must be a mapping")
        raw_messages = state.get("available")
        if not isinstance(raw_messages, list):
            raise ValueError("bus available state must be a list")

        restored: list[ValidatedMessage] = []
        for raw in raw_messages:
            if not isinstance(raw, Mapping):
                raise ValueError("invalid validated message state")
            payload = raw.get("payload")
            terms = raw.get("semantic_terms")
            if not isinstance(payload, Mapping) or not isinstance(terms, list):
                raise ValueError("invalid validated message payload state")
            restored.append(
                ValidatedMessage(
                    id=str(raw["id"]),
                    producer=str(raw["producer"]),
                    local_sequence=int(raw["local_sequence"]),
                    schema_name=str(raw["schema_name"]),
                    schema_version=str(raw["schema_version"]),
                    payload=dict(payload),
                    semantic_terms=tuple(str(term) for term in terms),
                )
            )
        self._available = restored

    def _journal_event(
        self,
        *,
        kind: str,
        t_monde: int,
        cycle: int,
        attempt_ref: str,
        data: Mapping[str, object],
    ) -> None:
        event_id = deterministic_id(
            "journal-event-v1",
            "bus",
            t_monde,
            cycle,
            attempt_ref,
            self._event_sequence,
        )
        self._event_sequence += 1
        self._journal.append(
            event_id=event_id,
            causal_event={
                "emitter": "bus",
                "kind": kind,
                "t_monde": t_monde,
                "cycle": cycle,
                "attempt_ref": attempt_ref,
                "data": dict(data),
            },
        )

    def pour(
        self,
        *,
        buffers: Sequence[ProducerBuffer],
        t_monde: int,
        cycle: int,
        attempt_ref: str,
    ) -> tuple[AdmissionResult, ...]:
        if t_monde < 0 or cycle < 0:
            raise ValueError("t_monde and cycle must be non-negative")
        if not attempt_ref:
            raise ValueError("attempt_ref must not be empty")

        seen_buffers: set[str] = set()
        pending: list[BufferedMessage] = []

        for buffer in buffers:
            producer = buffer.producer
            if producer in seen_buffers:
                raise ValueError(f"duplicate producer buffer: {producer}")
            seen_buffers.add(producer)
            if producer not in self._producer_rank:
                raise ContractViolation(
                    "unknown_producer",
                    f"producer absent from canonical order: {producer}",
                )
            pending.extend(buffer.drain())

        pending.sort(
            key=lambda message: (
                self._producer_rank[message.producer],
                message.local_sequence,
            )
        )

        results: list[AdmissionResult] = []
        for message in pending:
            try:
                causal_payload = self._schemas.validate_message(
                    schema_name=message.schema_name,
                    schema_version=message.schema_version,
                    payload=message.payload,
                )
                self._ontology.require_all(message.semantic_terms)

                message_id = deterministic_id(
                    "bus-message-v1",
                    message.producer,
                    t_monde,
                    cycle,
                    attempt_ref,
                    message.local_sequence,
                    message.schema_name,
                    message.schema_version,
                    causal_payload,
                    message.semantic_terms,
                )
                validated = ValidatedMessage(
                    id=message_id,
                    producer=message.producer,
                    local_sequence=message.local_sequence,
                    schema_name=message.schema_name,
                    schema_version=message.schema_version,
                    payload=causal_payload,
                    semantic_terms=message.semantic_terms,
                )
                self._available.append(validated)
                self._journal_event(
                    kind="bus_message_admitted",
                    t_monde=t_monde,
                    cycle=cycle,
                    attempt_ref=attempt_ref,
                    data={"message": validated.as_dict()},
                )
                results.append(
                    AdmissionResult(
                        accepted=True,
                        message=validated,
                        violation=None,
                    )
                )
            except ContractViolation as violation:
                self._journal_event(
                    kind="bus_message_rejected",
                    t_monde=t_monde,
                    cycle=cycle,
                    attempt_ref=attempt_ref,
                    data={
                        "producer": message.producer,
                        "local_sequence": message.local_sequence,
                        "schema_name": message.schema_name,
                        "schema_version": message.schema_version,
                        "violation": violation.as_dict(),
                    },
                )
                results.append(
                    AdmissionResult(
                        accepted=False,
                        message=None,
                        violation=violation,
                    )
                )

        return tuple(results)

    def drain_available(self) -> tuple[ValidatedMessage, ...]:
        messages = tuple(self._available)
        self._available.clear()
        return messages
