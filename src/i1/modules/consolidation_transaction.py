"""Stage-10 private consolidation transactions, MVP 15.6 / INV-23,24,47.

Contracts only: actual six cognitive passes, owner rebase, UC accounting and
coordinated publication are NOT supplied here. No method writes active h/Q/κ,
perceptual precision, causal rules, or the journal. The original episode data
are frozen, not merely the identifiers pointing into mutable Memory.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Callable, Mapping
from unicodedata import normalize

from lab.determinism import canonical_causal_bytes, sha256_hex

PASSES = (
    "episode_selection", "interleaved_replay", "hypothesis_extraction",
    "procedural_compilation", "kappa_recalibration", "index_maintenance",
)


def _identifier(value: object) -> bool:
    return type(value) is str and bool(value.strip()) and normalize("NFC", value) == value


def _json_tree(value: object) -> None:
    """Restrict frozen workspace data to portable, unambiguous causal trees."""
    if value is None or type(value) in (str, bool, int, float):
        canonical_causal_bytes(value)
        if type(value) is str and normalize("NFC", value) != value:
            raise ValueError("non-NFC causal string")
        return
    if type(value) is list:
        for item in value:
            _json_tree(item)
        return
    if type(value) is dict:
        for key, item in value.items():
            if not _identifier(key):
                raise ValueError("causal dictionary keys must be nonempty NFC strings")
            _json_tree(item)
        return
    raise ValueError("workspace must be an exact JSON-compatible causal tree")


def _owned(value: object) -> object:
    _json_tree(value)
    return deepcopy(value)


def _digest(value: object) -> str:
    return sha256_hex(canonical_causal_bytes(value))


@dataclass(frozen=True, slots=True)
class ConsolidationCut:
    world_step: int
    journal_index: int
    journal_event_id: str
    journal_hash: str
    history_version: str

    def validate(self) -> None:
        if type(self.world_step) is not int or self.world_step < 1:
            raise ValueError("invalid causal cut world step")
        if type(self.journal_index) is not int or self.journal_index < 0:
            raise ValueError("cut needs a nonnegative append-only journal index")
        if not _identifier(self.journal_event_id) or not _identifier(self.history_version):
            raise ValueError("cut requires journal identity and slow-history version")
        if (type(self.journal_hash) is not str or len(self.journal_hash) != 64
                or any(ch not in "0123456789abcdef" for ch in self.journal_hash)):
            raise ValueError("cut requires the journal's lowercase SHA-256 head")

    def as_dict(self) -> dict[str, object]:
        self.validate()
        return {
            "world_step": self.world_step,
            "journal_index": self.journal_index,
            "journal_event_id": self.journal_event_id,
            "journal_hash": self.journal_hash,
            "history_version": self.history_version,
        }


@dataclass(frozen=True, slots=True)
class PassCheckpoint:
    name: str
    candidate: object
    digest: str


@dataclass(frozen=True, slots=True)
class ConsolidationCommitReceipt:
    """A *claim* by the future scheduler, not a journal verification service."""
    consolidation_id: str
    source_history_version: str
    new_history_version: str
    candidate_digest: str
    journal_commit_index: int
    journal_commit_event_id: str

    def validate(self) -> None:
        if not all(_identifier(v) for v in (
            self.consolidation_id, self.source_history_version,
            self.new_history_version, self.journal_commit_event_id,
        )):
            raise ValueError("commit receipt identity missing")
        if self.source_history_version == self.new_history_version:
            raise ValueError("coordinated commit must publish a new history version")
        if (type(self.journal_commit_index) is not int or self.journal_commit_index < 0
                or type(self.candidate_digest) is not str
                or len(self.candidate_digest) != 64
                or any(ch not in "0123456789abcdef" for ch in self.candidate_digest)):
            raise ValueError("invalid commit index or candidate digest")


class ConsolidationTransaction:
    """One complete frozen input, private sequential checkpoints and resume."""

    schema = "stage10-consolidation-transaction-v2"

    def __init__(
        self, *, consolidation_id: str, cut: ConsolidationCut,
        episode_refs: tuple[str, ...], episode_payloads: Mapping[str, object],
        history_candidate: object,
    ) -> None:
        cut.validate()
        if not _identifier(consolidation_id):
            raise ValueError("stable consolidation identifier required")
        if (type(episode_refs) is not tuple
                or any(not _identifier(ref) for ref in episode_refs)
                or len(set(episode_refs)) != len(episode_refs)):
            raise ValueError("frozen batch needs unique episode references")
        if (not isinstance(episode_payloads, Mapping)
                or set(episode_payloads) != set(episode_refs)):
            raise ValueError("batch contents must match frozen references exactly")
        frozen: dict[str, object] = {}
        for ref in episode_refs:
            payload = _owned(episode_payloads[ref])
            if (type(payload) is not dict or payload.get("id") != ref
                    or type(payload.get("end_t_monde")) is not int
                    or payload["end_t_monde"] >= cut.world_step):
                raise ValueError("episode payload must match identity and predate cut")
            frozen[ref] = payload
        self.id = consolidation_id
        self.cut = cut
        self._batch = episode_refs
        self._frozen_episodes = frozen
        self._initial = _owned(history_candidate)
        # Clone only the already validated private JSON tree.
        self._candidate = deepcopy(self._initial)
        self._candidate_digest_cached = _digest(self._initial)
        self._checkpoints: list[PassCheckpoint] = []
        self._status = "active"
        self._batch_digest = _digest({"refs": list(self._batch), "episodes": frozen})
        self._seed_digest = _digest({
            "schema": self.schema, "id": self.id, "cut": self.cut.as_dict(),
            "batch_digest": self._batch_digest, "initial_digest": self._candidate_digest_cached,
        })

    @property
    def batch(self) -> tuple[str, ...]:
        return self._batch

    def frozen_episodes_copy(self) -> dict[str, object]:
        return deepcopy(self._frozen_episodes)

    def frozen_episode_subset_copy(self, refs: tuple[str, ...]) -> dict[str, object]:
        """Detach only the priced unit's required autobiography, not all Memory.

        The pass runner must charge before using this operation. A missing
        reference cannot be silently replaced with a WorldBody oracle read.
        """
        if type(refs) is not tuple or len(set(refs)) != len(refs):
            raise ValueError("invalid frozen episode unit reference set")
        try:
            return deepcopy({ref: self._frozen_episodes[ref] for ref in refs})
        except KeyError as exc:
            raise ValueError("episode absent from cut-point batch") from exc

    @property
    def batch_digest(self) -> str:
        return self._batch_digest

    @property
    def status(self) -> str:
        return self._status

    @property
    def cursor(self) -> int:
        return len(self._checkpoints)

    @property
    def completed_passes(self) -> tuple[str, ...]:
        return tuple(point.name for point in self._checkpoints)

    @property
    def candidate_digest(self) -> str:
        # Updated only at a validated candidate replacement.
        return self._candidate_digest_cached

    def candidate_copy(self) -> object:
        return deepcopy(self._candidate)

    def interrupt(self) -> None:
        if self._status != "active":
            raise ValueError("only an active transaction can be interrupted")
        # Current candidate is already a private copy of the latest
        # validated checkpoint; unfinished runner work lives elsewhere.
        # Suspending does not replace the checkpoint candidate.
        self._status = "suspended"

    def resume(self) -> None:
        if self._status != "suspended":
            raise ValueError("only a suspended transaction may resume")
        self._status = "active"

    def _point_digest(self, *, name: str, candidate: object) -> str:
        prior = self._checkpoints[-1].digest if self._checkpoints else self._seed_digest
        return _digest({"prior_digest": prior, "pass": name, "candidate": candidate})

    def run_pass(
        self, *, name: str,
        executor: Callable[[object, tuple[str, ...], ConsolidationCut], object],
        validator: Callable[[object], bool],
    ) -> None:
        if self._status != "active" or self.cursor == len(PASSES):
            raise ValueError("transaction inactive or already complete")
        if name != PASSES[self.cursor]:
            raise ValueError("passes must run in normative order")
        # The executor cannot obtain a reference to the private candidate.
        result = executor(deepcopy(self._candidate), self._batch, self.cut)
        candidate = _owned(result)
        # Guard against mutation by even the validator supplied by an owner.
        if validator(deepcopy(candidate)) is not True:
            raise ValueError("private pass failed technical validation")
        digest = self._point_digest(name=name, candidate=candidate)
        candidate_digest = _digest(candidate)
        self._checkpoints.append(PassCheckpoint(name, deepcopy(candidate), digest))
        self._candidate = candidate
        self._candidate_digest_cached = candidate_digest

    def validated_candidate(self, *, validator: Callable[[object], bool]) -> object:
        if self._status != "active" or self.cursor != len(PASSES):
            raise ValueError("all six passes must complete before publication")
        candidate = deepcopy(self._candidate)
        if validator(deepcopy(candidate)) is not True:
            raise ValueError("completed private history failed validation")
        return candidate

    def export_causal_state(self) -> dict[str, object]:
        return deepcopy({
            "schema": self.schema, "id": self.id, "cut": self.cut.as_dict(),
            "batch": list(self._batch), "frozen_episodes": self._frozen_episodes,
            "batch_digest": self._batch_digest, "initial": self._initial,
            "checkpoints": [{
                "name": cp.name, "candidate": cp.candidate, "digest": cp.digest,
            } for cp in self._checkpoints],
            "candidate": self._candidate, "status": self._status,
        })

    @classmethod
    def restore(cls, state: Mapping[str, object]) -> "ConsolidationTransaction":
        if (not isinstance(state, Mapping) or set(state) != {
            "schema", "id", "cut", "batch", "frozen_episodes", "batch_digest",
            "initial", "checkpoints", "candidate", "status",
        } or state.get("schema") != cls.schema):
            raise ValueError("incompatible consolidation snapshot")
        raw_cut = state["cut"]
        if not isinstance(raw_cut, Mapping) or set(raw_cut) != {
            "world_step", "journal_index", "journal_event_id", "journal_hash", "history_version",
        }:
            raise ValueError("invalid consolidation cut snapshot")
        cut = ConsolidationCut(**raw_cut)
        raw_batch = state["batch"]
        if type(raw_batch) is not list:
            raise ValueError("invalid frozen batch snapshot")
        restored = cls(
            consolidation_id=state["id"], cut=cut,
            episode_refs=tuple(raw_batch), episode_payloads=state["frozen_episodes"],
            history_candidate=state["initial"],
        )
        if state["batch_digest"] != restored._batch_digest:
            raise ValueError("frozen batch hash mismatch")
        points = state["checkpoints"]
        if type(points) is not list or len(points) > len(PASSES):
            raise ValueError("invalid consolidation cursor")
        for index, point in enumerate(points):
            if (not isinstance(point, Mapping) or set(point) != {
                "name", "candidate", "digest",
            } or point["name"] != PASSES[index]):
                raise ValueError("invalid checkpoint chronology")
            candidate = _owned(point["candidate"])
            digest = restored._point_digest(name=point["name"], candidate=candidate)
            if point["digest"] != digest:
                raise ValueError("checkpoint chain digest mismatch")
            restored._checkpoints.append(PassCheckpoint(point["name"], candidate, digest))
        status = state["status"]
        if status not in ("active", "suspended"):
            raise ValueError("invalid consolidation transaction status")
        expected = restored._checkpoints[-1].candidate if restored._checkpoints else restored._initial
        if canonical_causal_bytes(state["candidate"]) != canonical_causal_bytes(expected):
            raise ValueError("candidate differs from last validated checkpoint")
        restored._candidate = deepcopy(expected)
        restored._candidate_digest_cached = _digest(restored._candidate)
        restored._status = status
        return restored


class ConsolidationSlot:
    """Single pending transaction (INV-47), snapshot-able without owner overlap."""

    schema = "stage10-consolidation-slot-v1"
    owner_id = "consolidation"

    def __init__(self) -> None:
        self._current: ConsolidationTransaction | None = None

    @property
    def current(self) -> ConsolidationTransaction | None:
        return self._current

    def begin(self, transaction: ConsolidationTransaction) -> None:
        if self._current is not None:
            raise ValueError("suspended/active consolidation must take priority")
        if transaction.status != "active" or transaction.cursor:
            raise ValueError("only a fresh consolidation can begin")
        self._current = transaction

    def resume(self) -> ConsolidationTransaction:
        if self._current is None:
            raise ValueError("no suspended consolidation")
        self._current.resume()
        return self._current

    def acknowledge_coordinated_commit(self, receipt: ConsolidationCommitReceipt) -> None:
        """Release a completed transaction only on a matching scheduler receipt.

        The scheduler MUST ensure the receipt actually comes from an atomic
        journaled publication; this component cannot certify that itself.
        """
        receipt.validate()
        tx = self._current
        if tx is None or tx.id != receipt.consolidation_id:
            raise ValueError("no matching transaction")
        if tx.status != "active" or tx.cursor != len(PASSES):
            raise ValueError("cannot acknowledge incomplete consolidation")
        if (receipt.source_history_version != tx.cut.history_version
                or receipt.candidate_digest != tx.candidate_digest
                or receipt.journal_commit_index <= tx.cut.journal_index):
            raise ValueError("incompatible scheduler publication receipt")
        self._current = None

    def export_causal_state(self) -> dict[str, object]:
        return {"schema": self.schema, "current": (
            None if self._current is None else self._current.export_causal_state()
        )}

    def restore_causal_state(self, state: object) -> None:
        if not isinstance(state, Mapping) or set(state) != {"schema", "current"} or state["schema"] != self.schema:
            raise ValueError("incompatible consolidation slot snapshot")
        raw = state["current"]
        restored = None if raw is None else ConsolidationTransaction.restore(raw)
        self._current = restored
