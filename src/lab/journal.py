"""Append-only hash-chained causal journal for MVP v1.2.1.

Spec: 17.4, 20.3 Stage 1, INV-22, INV-33, INV-44.
"""

from __future__ import annotations

from copy import deepcopy
import json
import os
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
        self._wal_fd: int | None = None
        self._wal_faulted = False
        self._entries: list[JournalEntry] = []
        # Non-causal lookup index. The append order and canonical bytes remain
        # exactly those of _entries.
        self._by_id: dict[str, JournalEntry] = {}

    def enable_durable_wal(self, *, path: str) -> None:
        """Birth-only append-before-ack fsync journal, never life restoration.

        A new exclusive file is required; an existing life cannot be resumed
        or overwritten. The parent directory is fsynced for creation safety.
        """
        if (type(path) is not str or not os.path.isabs(path) or not path
                or self._entries or self._wal_fd is not None or self._wal_faulted):
            raise ValueError("WAL must be enabled on a fresh journal with an absolute path")
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        fd = os.open(path, flags, 0o600)
        try:
            directory = os.open(os.path.dirname(path), os.O_RDONLY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
        except BaseException:
            os.close(fd)
            self._wal_faulted = True
            raise
        self._wal_fd = fd

    @property
    def durable_wal_enabled(self) -> bool:
        return self._wal_fd is not None and not self._wal_faulted

    @staticmethod
    def audit_durable_wal(path: str) -> dict[str, object]:
        """Verify a complete durable file offline; never resurrect an individual.

        A torn last record or any rewritten, duplicated or reordered event
        fails closed. Only an attestation is returned, not a runnable journal.
        """
        if type(path) is not str or not os.path.isabs(path):
            raise ValueError("offline WAL audit requires an absolute path")
        with open(path, "rb") as stream:
            contents = stream.read()
        if contents and not contents.endswith(b"\n"):
            raise ValueError("unterminated durable journal record")
        replay = HashChainedJournal()
        for raw in contents.splitlines():
            if not raw:
                raise ValueError("empty durable journal record")
            try:
                payload = json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as error:
                raise ValueError("invalid durable journal JSON") from error
            if (type(payload) is not dict or set(payload) != {
                "index", "event_id", "previous_hash", "event_hash", "causal_event",
            } or type(payload["index"]) is not int
                    or type(payload["event_id"]) is not str
                    or type(payload["causal_event"]) is not dict
                    or canonical_causal_bytes(payload) != raw):
                raise ValueError("noncanonical durable journal record")
            if (payload["index"] != len(replay.entries)
                    or payload["previous_hash"] != replay.head_hash):
                raise ValueError("durable journal occurrence order or chain broken")
            reconstructed = replay.append(
                event_id=payload["event_id"],
                causal_event=payload["causal_event"],
            )
            if reconstructed.event_hash != payload["event_hash"]:
                raise ValueError("durable journal entry hash mismatch")
        if not replay.verify():
            raise ValueError("durable journal internal consistency failed")
        return {"verified_entries": len(replay.entries), "head_hash": replay.head_hash}

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
        # The durable receipt becomes visible in memory only AFTER write+fsync.
        # An I/O fault permanently poisons this life rather than rolling back
        # a potentially partially persisted physical history.
        if self._wal_faulted:
            raise RuntimeError("durable journal has suffered an unrecoverable I/O error")
        if self._wal_fd is not None:
            record = canonical_causal_bytes(entry.as_dict()) + b"\n"
            try:
                sent = 0
                while sent != len(record):
                    written = os.write(self._wal_fd, record[sent:])
                    if written <= 0:
                        raise OSError("durable journal write made no progress")
                    sent += written
                os.fsync(self._wal_fd)
            except BaseException:
                self._wal_faulted = True
                raise
        self._entries.append(entry)
        self._by_id[event_id] = entry
        return entry

    def canonical_bytes(self) -> bytes:
        """Return byte-identical normalized bytes for the complete journal."""

        return b"\n".join(
            canonical_causal_bytes(entry.as_dict()) for entry in self._entries
        )

    def verify(self) -> bool:
        """Recompute the complete chain and reject any broken link or mutation."""

        if self._wal_faulted:
            return False
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
