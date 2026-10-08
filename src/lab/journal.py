"""Append-only hash-chained causal journal for MVP v1.2.1.

Spec: 17.4, 20.3 Stage 1, INV-22, INV-33, INV-44.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .determinism import canonical_causal_bytes, sha256_hex


GENESIS_HASH = "00" * 32


@dataclass(frozen=True, slots=True)
class JournalEntry:
    """One immutable technical-journal occurrence."""

    index: int
    event_id: str
    previous_hash: str
    event_hash: str
    causal_event: Mapping[str, object]

    def as_dict(self) -> dict[str, object]:
        return {
            "index": self.index,
            "event_id": self.event_id,
            "previous_hash": self.previous_hash,
            "event_hash": self.event_hash,
            "causal_event": dict(self.causal_event),
        }


class HashChainedJournal:
    """Append-only in-memory journal with normative SHA-256 chaining."""

    def __init__(self) -> None:
        self._entries: list[JournalEntry] = []

    @property
    def entries(self) -> tuple[JournalEntry, ...]:
        return tuple(self._entries)

    @property
    def head_hash(self) -> str:
        return self._entries[-1].event_hash if self._entries else GENESIS_HASH

    def append(
        self,
        *,
        event_id: str,
        causal_event: Mapping[str, object],
        noncausal_metadata: Mapping[str, object] | None = None,
    ) -> JournalEntry:
        """Append one causal event.

        noncausal_metadata is accepted for API separation but deliberately
        excluded from causal bytes and the hash chain.
        """

        del noncausal_metadata

        if not event_id:
            raise ValueError("event_id must not be empty")

        previous_hash = self.head_hash
        event_bytes = canonical_causal_bytes(
            {"event_id": event_id, "causal_event": causal_event}
        )
        event_hash = sha256_hex(bytes.fromhex(previous_hash) + event_bytes)

        entry = JournalEntry(
            index=len(self._entries),
            event_id=event_id,
            previous_hash=previous_hash,
            event_hash=event_hash,
            causal_event=dict(causal_event),
        )
        self._entries.append(entry)
        return entry

    def canonical_bytes(self) -> bytes:
        """Return byte-identical normalized bytes for the complete journal."""

        return b"\n".join(
            canonical_causal_bytes(entry.as_dict()) for entry in self._entries
        )

    def verify(self) -> bool:
        """Recompute the complete chain and reject any broken link or mutation."""

        previous_hash = GENESIS_HASH
        for expected_index, entry in enumerate(self._entries):
            if entry.index != expected_index:
                return False
            if entry.previous_hash != previous_hash:
                return False
            expected_hash = sha256_hex(
                bytes.fromhex(previous_hash)
                + canonical_causal_bytes(
                    {
                        "event_id": entry.event_id,
                        "causal_event": entry.causal_event,
                    }
                )
            )
            if entry.event_hash != expected_hash:
                return False
            previous_hash = expected_hash
        return True
