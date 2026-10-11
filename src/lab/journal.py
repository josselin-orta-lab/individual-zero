"""Append-only hash-chained causal journal for MVP v1.2.1.

Spec: 17.4, 20.3 Stage 1, INV-22, INV-33, INV-44.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Mapping
from unicodedata import normalize

from .determinism import canonical_causal_bytes, sha256_hex


GENESIS_HASH = "00" * 32


class _DetachedCausalEvent(Mapping[str, object]):
    """Read-only technical view whose nested reads never alias journal state."""

    __slots__ = ("__contents",)

    def __init__(self, source: Mapping[str, object]) -> None:
        self.__contents = deepcopy(dict(source))

    def __getitem__(self, key: str) -> object:
        return deepcopy(self.__contents[key])

    def __iter__(self):
        return iter(self.__contents)

    def __len__(self) -> int:
        return len(self.__contents)

    def copy(self) -> dict[str, object]:
        """Compatibility helper: like dict.copy(), without leaking aliases."""
        return dict(self)

    def __repr__(self) -> str:
        return repr(dict(self))


@dataclass(frozen=True, slots=True)
class JournalEntry:
    """One immutable technical-journal occurrence."""

    index: int
    event_id: str
    previous_hash: str
    event_hash: str
    causal_event: Mapping[str, object]

    def __post_init__(self) -> None:
        object.__setattr__(self, "causal_event", _DetachedCausalEvent(self.causal_event))

    def as_dict(self) -> dict[str, object]:
        return {
            "index": self.index,
            "event_id": self.event_id,
            "previous_hash": self.previous_hash,
            "event_hash": self.event_hash,
            # An exported document must not alias the hash-chained record.
            "causal_event": dict(self.causal_event),
        }


class HashChainedJournal:
    """Append-only in-memory journal with normative SHA-256 chaining."""

    def __init__(self) -> None:
        self._entries: list[JournalEntry] = []
        # Non-causal lookup index. The append order and canonical bytes remain
        # exactly those of _entries.
        self._by_id: dict[str, JournalEntry] = {}
        # A fatal result is recorded before its one terminal step closure.
        # No other event may intervene and nothing may follow that closure.
        # This is a forward-only runtime guard, never a replacement for the
        # independent auditor's checks on potentially forged export bytes.
        self._pending_death_closure: tuple[int, str] | None = None
        self._death_sealed = False

    @property
    def entries(self) -> tuple[JournalEntry, ...]:
        return tuple(self._entries)

    def get(self, event_id: str) -> JournalEntry | None:
        return self._by_id.get(event_id)

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

        if not isinstance(event_id, str) or not event_id:
            raise ValueError("event_id must be a nonempty string")
        # INV-49: an occurrence has one immutable identity, including after
        # repeated attempts/rollbacks. Otherwise _by_id silently loses the
        # first occurrence while the hash-chained journal still contains it.
        if normalize("NFC", event_id) != event_id:
            raise ValueError("journal event_id must be NFC-normalized")
        if event_id in self._by_id:
            raise ValueError("duplicate technical journal event_id")
        if self._death_sealed:
            raise RuntimeError("terminal journal is sealed after death")
        # A malformed physical closure is not an opportunity to inject a new
        # cognitive event between death and final technical step closure.
        kind = causal_event.get("kind")
        pending = self._pending_death_closure
        if pending is not None:
            closure = causal_event.get("data")
            if not (
                kind == "step_closed"
                and causal_event.get("t_monde") == pending[0]
                and causal_event.get("attempt_ref") == pending[1]
                and isinstance(closure, Mapping)
                and closure.get("outcome") == "dead"
                and closure.get("applied_command_count") == 1
                and closure.get("world_advance_count") == 1
            ):
                raise RuntimeError("terminal death requires its unique technical closure")
        elif kind == "individual_death_confirmed":
            if (
                type(causal_event.get("t_monde")) is not int
                or causal_event["t_monde"] < 1
                or not isinstance(causal_event.get("attempt_ref"), str)
                or not causal_event["attempt_ref"]
            ):
                raise ValueError("terminal death needs a valid world attempt")

        # Own the complete nested payload, not just the outer dictionary.
        # Canonicalize exactly the copy retained in the append-only chain:
        # subsequent caller mutations cannot alter an already hashed event.
        retained_event = deepcopy(dict(causal_event))
        previous_hash = self.head_hash
        event_bytes = canonical_causal_bytes(
            {"event_id": event_id, "causal_event": retained_event}
        )
        event_hash = sha256_hex(bytes.fromhex(previous_hash) + event_bytes)

        entry = JournalEntry(
            index=len(self._entries),
            event_id=event_id,
            previous_hash=previous_hash,
            event_hash=event_hash,
            causal_event=retained_event,
        )
        self._entries.append(entry)
        self._by_id[event_id] = entry
        if kind == "individual_death_confirmed":
            self._pending_death_closure = (
                retained_event["t_monde"], retained_event["attempt_ref"],
            )
        elif pending is not None:
            self._pending_death_closure = None
            self._death_sealed = True
        return entry

    def canonical_bytes(self) -> bytes:
        """Return byte-identical normalized bytes for the complete journal."""

        return b"\n".join(
            canonical_causal_bytes(entry.as_dict()) for entry in self._entries
        )

    def verify(self) -> bool:
        """Recompute the complete chain and reject any broken link or mutation."""

        previous_hash = GENESIS_HASH
        seen_ids: set[str] = set()
        if len(self._by_id) != len(self._entries):
            return False
        for expected_index, entry in enumerate(self._entries):
            if (
                entry.index != expected_index
                or not isinstance(entry.event_id, str)
                or not entry.event_id
                or normalize("NFC", entry.event_id) != entry.event_id
                or entry.event_id in seen_ids
                or self._by_id.get(entry.event_id) is not entry
            ):
                return False
            seen_ids.add(entry.event_id)
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
