"""Opt-in M-11 physical/cognitive coordinator for a *single* active process.

The world, Scheduler and cognition execute on a DETACHED candidate first.
The candidate is not observable through this owner until the canonical
journal suffix and complete registered owner state share one SQLite COMMIT.
The only publication is a pointer swap to the committed candidate.

This is a development integration gate, NOT yet a cold-start Stage10/11
recovery certification. Failures permanently poison this coordinator;
pending/uncertain identities are NEVER restored as earlier lives.
"""
from __future__ import annotations

from copy import deepcopy
from collections.abc import Mapping
from dataclasses import dataclass, fields, is_dataclass
from types import MappingProxyType
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Callable

from .determinism import canonical_causal_bytes, sha256_hex
from .journal import GENESIS_HASH
from .mortal_execution import MortalStatus
from .sqlite_life_store import SQLiteLifeLedger, RecoveryBlocked
from .sqlite_runtime_custody import capture_registered_current_state


def _copy_private_runtime(runtime: Any) -> Any:
    """Clone registered runtime with frozen mapping proxies shared read-only.

    `mappingproxy` is not pickleable/copyable on supported Python versions;
    frozen S_t snapshots contain recursive proxies and are immutable views.
    Sharing those proxy objects is safe because they contain frozen values,
    while every mutable runtime owner is cloned by deepcopy.
    """
    proxies: dict[int, object] = {}
    visited: set[int] = set()

    def collect(value: object) -> None:
        marker = id(value)
        if marker in visited:
            return
        visited.add(marker)
        if isinstance(value, MappingProxyType):
            proxies[marker] = value
            return
        if value is None or isinstance(value, (str, bytes, int, float, bool, complex)):
            return
        if isinstance(value, dict):
            for key, item in value.items():
                collect(key)
                collect(item)
        elif isinstance(value, (list, tuple, set, frozenset)):
            for item in value:
                collect(item)
        else:
            mod = type(value).__module__
            if not (mod.startswith("i0.") or mod.startswith("lab.")):
                return
            own = getattr(value, "__dict__", None)
            if isinstance(own, dict):
                for item in own.values():
                    collect(item)
            for base in type(value).__mro__:
                slots = getattr(base, "__slots__", ())
                if isinstance(slots, str):
                    slots = (slots,)
                for slot in slots:
                    if slot not in {"__dict__", "__weakref__"}:
                        try:
                            collect(object.__getattribute__(value, slot))
                        except AttributeError:
                            continue

    collect(runtime)
    return deepcopy(runtime, proxies)


def _decode_canonical(value: Any) -> Any:
    """Decode only I0's canonical lossless float wrapper.

    SQLite validates the original byte sequence and hash chain first. The
    decoded value is re-encoded byte-identically before any cold state owner
    receives it, rejecting ambiguous/noncanonical data.
    """
    if isinstance(value, dict):
        if set(value) == {"$f64"} and isinstance(value["$f64"], str):
            try:
                decoded = float.fromhex(value["$f64"])
            except ValueError as exc:
                raise RecoveryBlocked("invalid canonical IEEE-754 encoding") from exc
            if canonical_causal_bytes(decoded) != canonical_causal_bytes(value):
                raise RecoveryBlocked("noncanonical float encoding")
            return decoded
        return {k: _decode_canonical(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_decode_canonical(v) for v in value]
    return value


_PHYSICAL_MUTABLE = frozenset({
    "_position", "_body", "_inventory", "_resources",
    "_obstacles", "_water_sources", "_creatures", "_danger_zones",
    "_lethal_zones", "_shelters", "_placed_stones",
    "_action_failure_schedules", "_action_failure_indices",
})


def _contract_value(value: Any) -> Any:
    """A lossless, ordering-independent representation of constructor inputs.

    Never use repr() for a durable fingerprint: mapping/set representations
    and custom objects may differ across fresh processes or Python versions.
    Unsupported configuration types fail closed rather than being ignored.
    """
    if value is None or type(value) in (str, bool, int, float):
        return value
    if is_dataclass(value) and not isinstance(value, type):
        return {
            "$dataclass": type(value).__module__ + "." + type(value).__qualname__,
            "fields": {
                f.name: _contract_value(getattr(value, f.name))
                for f in fields(value)
            },
        }
    if isinstance(value, Mapping):
        if any(type(key) is not str for key in value):
            raise RecoveryBlocked("runtime contract requires string mapping keys")
        return {key: _contract_value(item) for key, item in value.items()}
    if isinstance(value, (set, frozenset)):
        items = [_contract_value(item) for item in value]
        return {
            "$collection": type(value).__name__,
            "items": sorted(items, key=canonical_causal_bytes),
        }
    if isinstance(value, (tuple, list)):
        return {
            "$collection": type(value).__name__,
            "items": [_contract_value(item) for item in value],
        }
    raise RecoveryBlocked(
        "unsupported runtime constructor configuration: "
        + type(value).__module__ + "." + type(value).__qualname__
    )


def _runtime_contract(runtime: Any) -> str:
    """Pin actual constructor values, never unstable Python repr strings."""
    configuration = (
        "m11-structured-constructor-contract-v2",
        type(runtime).__module__, type(runtime).__qualname__,
        runtime._config, runtime.world.config,
        getattr(runtime, "_stage11_config", None),
        getattr(runtime, "_stage10_config", None),
        getattr(runtime, "_m11_sqlite_custody", False),
        getattr(runtime, "_stage12_detector_policy", None),
        getattr(runtime, "_stage12_alert_policy", None),
        getattr(runtime, "_stage12_diagnostic_cost_uc", None),
        getattr(runtime, "_stage12_occupancy_cost_uc", None),
        getattr(runtime.world, "_layout", None),
    )
    return sha256_hex(canonical_causal_bytes(_contract_value(configuration)))


def _runtime_image(runtime: Any, *, individual_id: str) -> dict[str, Any]:
    image = capture_registered_current_state(
        runtime, individual_id=individual_id)
    substrate = runtime.stage3.substrate
    image["runtime_local"] = {
        "schema": "m11-quiescent-runtime-locals-v1",
        "runtime_contract": _runtime_contract(runtime),
        "runtime_self_id": str(runtime.individual_id),
        "scheduler_journal_sequence": runtime.scheduler._journal_sequence,
        "stage3_event_sequence": runtime.stage3._event_sequence,
        "stage4_event_sequence": runtime._event_sequence,
        "bus_event_sequence": runtime.bus._event_sequence,
        "autobiographical_commit_sequence": substrate.views._commit_sequence,
        "stage11_modulation_signals": dict(getattr(
            runtime, "_stage11_modulation_signals", {})),
    }
    return image


def _install_trusted_current_on_fresh(
    runtime: Any, image: dict[str, Any], journal_bytes: bytes,
) -> None:
    """Initialize a never-used runtime from one SQLite-validated current slot.

    This is NOT WorldBody.restore_causal_state on an existing mortal life.
    A private, newly constructed WorldBody parses the complete state first;
    only then are its physical value fields installed in an untouched birth
    instance. No previously committed live world is ever rolled backwards.
    """
    from .world import WorldBody
    from .journal_views import JournalViews

    original = _runtime_image(runtime, individual_id=image["individual_id"])
    if (original["journal"]["count"] != 0
            or original["scheduler"]["t_monde"] != 0
            or runtime.stage3.substrate.mortal_status is not MortalStatus.ACTIVE):
        raise RecoveryBlocked("cold reconstruction requires a never-executed mortal birth")
    if original["owner_ids"] != image["owner_ids"]:
        raise RecoveryBlocked("configured causal owner roster is not the stored roster")
    local = image.get("runtime_local")
    if (not isinstance(local, dict)
            or set(local) != set(original["runtime_local"])
            or local["schema"] != "m11-quiescent-runtime-locals-v1"
            or local["runtime_contract"] != original["runtime_local"]["runtime_contract"]
            or local["runtime_self_id"] != original["runtime_local"]["runtime_self_id"]):
        raise RecoveryBlocked("incompatible or incomplete runtime cold-restoration contract")
    for item in ("scheduler_journal_sequence", "stage3_event_sequence",
                 "stage4_event_sequence", "bus_event_sequence",
                 "autobiographical_commit_sequence"):
        if type(local[item]) is not int or local[item] < 0:
            raise RecoveryBlocked("invalid runtime event counter")
    if (not isinstance(local["stage11_modulation_signals"], dict)
            or any(type(v) is not bool for v in local["stage11_modulation_signals"].values())):
        raise RecoveryBlocked("invalid modulation signal state")

    # Restore causal occurrences, NOT physical command effects. The storage
    # auditor has already checked their exact canonical bytes and SHA links.
    for raw in journal_bytes.split(b"\n"):
        entry = _decode_canonical(json.loads(raw))
        if canonical_causal_bytes(entry) != raw:
            raise RecoveryBlocked("cold journal has noncanonical encoding")
        if (not isinstance(entry, dict)
                or not isinstance(entry.get("causal_event"), dict)):
            raise RecoveryBlocked("malformed trusted journal event")
        runtime.journal.append(
            event_id=entry["event_id"],
            causal_event=entry["causal_event"],
        )
        if runtime.journal.entries[-1].as_dict() != entry:
            raise RecoveryBlocked("cold journal differs from durable occurrence")
    if (runtime.journal.head_hash != image["journal"]["head"]
            or len(runtime.journal.entries) != image["journal"]["count"]):
        raise RecoveryBlocked("cold journal does not match current SQL generation")

    # Build a detached, unpublished *new* world. The original public-world
    # restore prohibition on `runtime.world` is never disabled or bypassed.
    staging = WorldBody(config=runtime.world.config, layout=runtime.world._layout)
    staging.restore_causal_state(image["world"])
    if staging.export_causal_state() != image["world"]:
        raise RecoveryBlocked("cold physical image differs from current SQL state")
    current = dict(runtime.world.__dict__)
    for name in _PHYSICAL_MUTABLE:
        current[name] = deepcopy(getattr(staging, name))
    runtime.world.__dict__ = current
    runtime.scheduler.restore_causal_state(image["scheduler"])
    runtime.scheduler._journal_sequence = local["scheduler_journal_sequence"]
    current_owner_ids = {o.owner_id: o for o in runtime.causal_owners}
    for key, value in image["owners"].items():
        owner = current_owner_ids[key]
        owner.restore_causal_state(deepcopy(value))
    # Complete ledger bytes correspond to the current *generation*, not any
    # selected historical snapshot. The new world has never executed a step.
    boundary = runtime.stage3.substrate._mortal_boundary
    if boundary is None or boundary.last_world_step != 0:
        raise RecoveryBlocked("missing fresh mortal execution boundary")
    boundary._last_world_step = image["scheduler"]["t_monde"]
    runtime.stage3._event_sequence = local["stage3_event_sequence"]
    runtime._event_sequence = local["stage4_event_sequence"]
    runtime.bus._event_sequence = local["bus_event_sequence"]
    runtime.stage3.substrate.views._commit_event_ids = [
        row.event_id for row in runtime.journal.entries
        if row.causal_event.get("kind") == "auto_segment_commit"
    ]
    runtime.stage3.substrate.views._commit_sequence = local[
        "autobiographical_commit_sequence"]
    if (runtime.stage3.substrate.views._commit_sequence !=
            len(runtime.stage3.substrate.views._commit_event_ids)):
        raise RecoveryBlocked("invalid restored autobiographical sequence")
    if hasattr(runtime, "_stage11_modulation_signals"):
        runtime._stage11_modulation_signals = dict(
            local["stage11_modulation_signals"])
    if canonical_causal_bytes(_runtime_image(
        runtime, individual_id=image["individual_id"]
    )) != canonical_causal_bytes(image):
        raise RecoveryBlocked("cold reconstructed world/owners do not match committed state")


@dataclass(frozen=True, slots=True)
class TransactionalStepReceipt:
    generation: int
    world_step: int
    status: str
    journal_count: int
    journal_head: str
    outcome: str


class M11TransactionalMortal:
    """The *single* official world owner for an opted-in mortal execution.

    The original runtime provided at birth remains private and cannot be
    published to consumers as a life. This class does not expose it.
    """

    def __init__(self, *, runtime: Any, ledger: SQLiteLifeLedger,
                 individual_id: str) -> None:
        self._runtime = runtime
        self._ledger = ledger
        self.individual_id = individual_id
        self._stopped = False

    @classmethod
    def birth(cls, *, db_path: str, runtime: Any,
              individual_id: str) -> "M11TransactionalMortal":
        if not isinstance(db_path, str) or not os.path.isabs(db_path):
            raise ValueError("M-11 requires a new absolute database path")
        # Stage12 currently has a separate durable event owner. Until that
        # owner joins this same transaction, its runtime must not accidentally
        # be treated as covered by a Stage10/11 SQLite custody receipt.
        from .stage10_runtime import Stage10Runtime
        from .stage11_runtime import Stage11Runtime
        from .stage12_runtime import Stage12Runtime
        if (type(runtime) not in (Stage10Runtime, Stage11Runtime)
                and not (type(runtime) is Stage12Runtime
                         and getattr(runtime, "_m11_sqlite_custody", False) is True)):
            raise RecoveryBlocked("unsupported runtime: additional mutable/WAL owners not coordinated")
        if (runtime.stage3.substrate._mortal_boundary is None
                or runtime.stage3.substrate.mortal_status is not MortalStatus.ACTIVE
                or runtime.scheduler.t_monde != 0
                or runtime.journal.entries
                or runtime.stage3.substrate.bench is not None
                or runtime.stage3.substrate.evaluation_trace is not None
                or runtime.stage3.substrate._operator_frame_sink is not None
                or runtime.journal.durable_wal_enabled):
            raise ValueError("M-11 requires a fresh, standalone mortal runtime without side effects")
        # Acquire exclusive ownership of a DETACHED candidate. Keeping the
        # caller's original runtime dispatchable would give one life two
        # physical authorities, bypassing the SQLite transaction boundary.
        private = _copy_private_runtime(runtime)
        state = _runtime_image(private, individual_id=individual_id)
        ledger = SQLiteLifeLedger.birth(
            path=db_path, individual_id=individual_id, initial_state=state)
        try:
            runtime.stage3.substrate._mortal_boundary.halt(failed_step=1)
        except BaseException:
            ledger.close()
            raise
        return cls(runtime=private, ledger=ledger, individual_id=individual_id)

    @classmethod
    def cold_recover(cls, *, db_path: str, individual_id: str,
                     runtime_factory: Callable[[], Any]) -> "M11TransactionalMortal":
        """Resume only the *current*, nonterminal, wholly committed generation.

        No physical command is replayed. Factory must build exactly the same
        never-run autonomous runtime configuration as at original birth.
        Incomplete, terminal, or mismatched owner graphs fail permanently.
        """
        ledger = SQLiteLifeLedger.open_existing(
            path=db_path, expected_individual_id=individual_id)
        try:
            raw = ledger.recover_current_bytes(
                expected_individual_id=individual_id)
            image = _decode_canonical(json.loads(raw))
            if canonical_causal_bytes(image) != raw:
                raise RecoveryBlocked("cold state bytes are not canonical")
            if not isinstance(image, dict) or image.get("lifecycle") != "active":
                raise RecoveryBlocked("no active current generation to rehydrate")
            journal = ledger.export_canonical_journal()
            if not journal:
                # Zero-genesis state is allowed, with no past command.
                if ledger.audit().generation != 0:
                    raise RecoveryBlocked("non-genesis current state lacks canonical events")
                runtime = runtime_factory()
                from .stage10_runtime import Stage10Runtime
                from .stage11_runtime import Stage11Runtime
                from .stage12_runtime import Stage12Runtime
                if (type(runtime) not in (Stage10Runtime, Stage11Runtime)
                        and not (type(runtime) is Stage12Runtime
                                 and getattr(runtime, "_m11_sqlite_custody", False) is True)):
                    raise RecoveryBlocked("cold factory exposes uncoordinated runtime")
                if _runtime_image(runtime, individual_id=individual_id) != image:
                    raise RecoveryBlocked("genesis factory does not match anchored state")
            else:
                runtime = runtime_factory()
                from .stage10_runtime import Stage10Runtime
                from .stage11_runtime import Stage11Runtime
                from .stage12_runtime import Stage12Runtime
                if (type(runtime) not in (Stage10Runtime, Stage11Runtime)
                        and not (type(runtime) is Stage12Runtime
                                 and getattr(runtime, "_m11_sqlite_custody", False) is True)):
                    raise RecoveryBlocked("cold factory exposes uncoordinated runtime")
                _install_trusted_current_on_fresh(runtime, image, journal)
            private = _copy_private_runtime(runtime)
            expected = canonical_causal_bytes(image)
            detached = _runtime_image(private, individual_id=individual_id)
            if canonical_causal_bytes(detached) != expected:
                changed = [
                    name for name in image
                    if canonical_causal_bytes(detached.get(name)) != canonical_causal_bytes(image[name])
                ]
                if "owners" in changed:
                    changed.extend(
                        "owner:" + name for name in image["owners"]
                        if canonical_causal_bytes(detached["owners"].get(name))
                        != canonical_causal_bytes(image["owners"][name])
                    )
                if "runtime_local" in changed:
                    changed.extend(
                        "runtime_local:" + name for name in image["runtime_local"]
                        if canonical_causal_bytes(detached["runtime_local"].get(name))
                        != canonical_causal_bytes(image["runtime_local"][name])
                    )
                raise RecoveryBlocked(
                    "detached cold runtime differs before sealing external factory: "
                    + ", ".join(changed[:12]))
            # No duplicate active authority can escape through a factory.
            runtime.stage3.substrate._mortal_boundary.halt(
                failed_step=max(1, runtime.scheduler.t_monde))
            detached_after_halt = _runtime_image(private, individual_id=individual_id)
            if canonical_causal_bytes(detached_after_halt) != expected:
                changed = [
                    name for name in image
                    if canonical_causal_bytes(detached_after_halt.get(name))
                    != canonical_causal_bytes(image[name])
                ]
                raise RecoveryBlocked(
                    "external factory quarantine changed owned cold runtime: "
                    + ", ".join(changed))
            return cls(runtime=private, ledger=ledger, individual_id=individual_id)
        except BaseException:
            ledger.close()
            raise

    def inspect(self) -> dict[str, object]:
        """No mutable runtime owner is ever returned to a caller."""
        receipt = self._ledger.audit()
        return {
            "individual_id": receipt.individual_id,
            "generation": receipt.generation,
            "status": receipt.status,
            "journal_count": receipt.journal_count,
            "journal_head": receipt.journal_head,
            "pending_intent": receipt.pending_intent,
            "world_step": self._runtime.scheduler.t_monde,
        }

    def close(self) -> None:
        self._stopped = True
        self._ledger.close()

    def __enter__(self) -> "M11TransactionalMortal":
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    def run_step(self, *,
                 test_fault: Callable[[str], None] | None = None
                 ) -> TransactionalStepReceipt:
        if self._stopped:
            raise RecoveryBlocked("transactional life is no longer dispatchable")
        base = self._ledger.audit()
        if not base.may_recover:
            raise RecoveryBlocked("terminal or uncertain current generation")
        if self._runtime.stage3.substrate.mortal_status is not MortalStatus.ACTIVE:
            raise RecoveryBlocked("current runtime has already stopped")
        old_state = _runtime_image(self._runtime, individual_id=self.individual_id)
        if (base.state_hash != sha256_hex(canonical_causal_bytes(old_state))
                or base.journal_head != self._runtime.journal.head_hash
                or base.journal_count != len(self._runtime.journal.entries)):
            self._stopped = True
            raise RecoveryBlocked("unsanctioned mutation of published world or owners")
        # Fence durable BEFORE copying, executing or publishing ANY world step.
        intent = f"m11:world:{base.generation + 1}:{base.journal_head[:16]}"
        try:
            self._ledger.begin_intent(
                expected_generation=base.generation, intent_ref=intent)
            if test_fault:
                test_fault("after_intent")
            candidate = _copy_private_runtime(self._runtime)
            # Absolute prohibition on running private frames with Oracle,
            # Bench, a duplicate WAL owner, or an operator callback.
            if (candidate.stage3.substrate.bench is not None
                    or candidate.journal.durable_wal_enabled
                    or candidate.stage3.substrate._operator_frame_sink is not None):
                raise RecoveryBlocked("unsafe external side effect in private candidate")
            if test_fault:
                test_fault("before_private_execution")
            if getattr(candidate, "_m11_sqlite_custody", False):
                candidate._m11_step_capability = True
                try:
                    outcome = candidate.run_step()
                finally:
                    candidate._m11_step_capability = False
            else:
                outcome = candidate.run_step()
            if test_fault:
                test_fault("after_private_execution")
            # A live owner MUST NOT have observed the candidate's private effects.
            if _runtime_image(self._runtime, individual_id=self.individual_id) != old_state:
                raise RecoveryBlocked("candidate mutated previously published owner")
            status = candidate.stage3.substrate.mortal_status
            lifecycle = (
                "dead" if status is MortalStatus.DEAD
                else "active" if status is MortalStatus.ACTIVE
                else "technical_halt"
            )
            if lifecycle == "technical_halt":
                raise RecoveryBlocked("uncertain private execution cannot commit")
            proposed = _runtime_image(candidate, individual_id=self.individual_id)
            if proposed["owner_ids"] != old_state["owner_ids"]:
                raise RecoveryBlocked("private candidate lost a causal owner")
            if proposed.get("lifecycle") != lifecycle:
                raise RecoveryBlocked("candidate lifecycle and registered image diverged")
            events = [
                event.as_dict()
                for event in candidate.journal.entries[base.journal_count:]
            ]
            if not events:
                raise RecoveryBlocked("generation missing canonical journal occurrences")
            if test_fault:
                test_fault("before_sql_commit")
            committed = self._ledger.commit_generation(
                expected_generation=base.generation,
                expected_head=base.journal_head,
                intent_ref=intent,
                current_state=proposed,
                events=events,
                status=lifecycle,
            )
            if test_fault:
                test_fault("after_sql_commit")
            # ONE official publication of every state owner after durable
            # commit. No WorldBody.apply or command replay on the old runtime.
            self._runtime = candidate
            if test_fault:
                test_fault("after_publication")
            return TransactionalStepReceipt(
                generation=committed.generation,
                world_step=candidate.scheduler.t_monde,
                status=lifecycle,
                journal_count=committed.journal_count,
                journal_head=committed.journal_head,
                outcome=outcome.execution_status,
            )
        except BaseException:
            self._stopped = True
            # Deliberately never roll back a committed effect or continue from
            # an uncertain transaction. The db is auditable after reopen.
            raise
