"""One-shot *engineering* integration of native I3 Mind/World with step custody.

Creates a fresh local **test-only** World and Mind (P1.3 reference), never a
registered birth or scientific cohort. A committed receipt proves that this
in-process path actually called the native physics and paid learning. It does
NOT persist the full mutable organism or authenticate source bytes. Source-
pinned deterministic *detached replay* can reconstruct a previously fully
sealed engineering history in a new process, but is NOT M11 or independently
anchored anti-rollback. Unsealed actions always poison continuation.

This intentionally duplicates the small reference step sequence from life.py
rather than changing that historically pinned experimental runner.
"""
from __future__ import annotations

from collections import deque
from dataclasses import fields, is_dataclass
from hashlib import sha256
import json
from math import isfinite
from pathlib import Path
import random

from i3.modules.body import CognitiveBudget, CognitiveWork
from i3.modules.genome import digest as genome_digest, validate as validate_genome
from i3.modules.mind import EffectsModel, Mind
from i3.modules.world import World, WorldSpec
from i3.runtime.birth_reservation import Reservation, reserve
from i3.runtime.engineering_step_ledger import (
    INTENT_SCHEMA, RECEIPT_SCHEMA, ANCHOR_MODE, LEGACY_MODE, REMOTE_MODE,
    initialize, inspect, prepare, seal,
)
from i3.runtime import engineering_rollback_witness as witness
from i3.runtime.engineering_remote_witness import RemoteEngineeringWitness
from i3.runtime.provenance import digest, source_snapshot, world_snapshot


STATUS = "I3_NATIVE_ENGINEERING_ONE_SHOT_NO_COLD_RECOVERY"


def _stable(value):
    """Typed, deterministic *fingerprint* of current in-memory I3 state.

    Not a restorable codec, a source attestation or an anti-rollback anchor.
    Refuse unknown objects rather than hash reprs containing process addresses.
    """
    if value is None or type(value) in (bool, int, str):
        return value
    if type(value) is float:
        if not isfinite(value):
            raise ValueError("non-finite native state")
        return value
    if isinstance(value, random.Random):
        return {"type": "random.Random", "state": _stable(value.getstate())}
    if type(value) in (tuple, list):
        return {"type": type(value).__name__, "items": [_stable(v) for v in value]}
    if isinstance(value, deque):
        return {"type": "deque", "maxlen": value.maxlen,
                "items": [_stable(v) for v in value]}
    if type(value) in (set, frozenset):
        items = [_stable(v) for v in value]
        return {"type": type(value).__name__, "items": sorted(items, key=_json)}
    if isinstance(value, dict):
        items = [[_stable(k), _stable(v)] for k, v in value.items()]
        items.sort(key=lambda pair: _json(pair[0]))
        return {"type": "mapping", "items": items}
    if is_dataclass(value) and not isinstance(value, type):
        if not type(value).__module__.startswith("i3.modules."):
            raise TypeError("foreign state dataclass")
        return {"type": type(value).__module__ + "." + type(value).__name__,
                "fields": {f.name: _stable(getattr(value, f.name))
                           for f in fields(value)}}
    if type(value) in (World, Mind, EffectsModel):
        return {"type": type(value).__module__ + "." + type(value).__name__,
                "fields": {k: _stable(v) for k, v in sorted(vars(value).items())}}
    raise TypeError("unsupported native state: " + type(value).__name__)


def _json(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False)


def state_hash(value: World | Mind) -> str:
    """Observer-only checksum; never read by the organism or action control."""
    if type(value) not in (World, Mind):
        raise TypeError("only exact reference World/Mind may be fingerprinted")
    return sha256(_json(_stable(value)).encode("utf-8")).hexdigest()


def make_engineering_claim(*, birth_index: int, genome: dict,
                           spec: WorldSpec, life_seed: int) -> Reservation:
    """Bind a *local engineering* slot to current source and proposed inputs."""
    if type(spec) is not WorldSpec:
        raise TypeError("exact native WorldSpec required")
    validate_genome(genome)
    from i3.runtime.birth_reservation import make_reservation
    return make_reservation(birth_index=birth_index, life_seed=life_seed,
                            source_sha256=source_snapshot()["sha256"],
                            world_sha256=digest(world_snapshot(spec)),
                            genome_sha256=genome_digest(genome))


def _native_decide(world: World, mind: Mind):
    """Reproduce the original P1.3 decision from first-person capture only."""
    capture = world.capture()
    budget = CognitiveBudget(world.body, world.laws)
    action, param, work, _info = mind.decide(capture, budget)
    if work != budget.work:
        raise ValueError("Mind decision work differs from the native allowance")
    intent = {"schema": INTENT_SCHEMA, "tick_before": world.t,
              "body_before": list(world.body), "action": action, "param": param,
              "decision_work": {name: getattr(work, name)
                  for name in ("cycles", "simulated_steps", "memory_items", "replays")}}
    return action, param, work, intent


def _native_outcome(world: World, mind: Mind, action, param,
                    work: CognitiveWork) -> dict:
    """Apply exactly one native motor plus the already prepaid learning path.

    Only the caller that has durably PREPARED an intent may use this as a
    *new* action. Read-only reconstruction replays it on a detached World.
    """
    outcome = world.step(action, param, work)
    motor_body = list(outcome["body"])
    paid_learning = {"energy": 0.0, "vigilance": 0.0}
    if not outcome["dead"] and mind.last is not None:
        learning = CognitiveBudget(outcome["body"], world.laws)
        mind.observe_outcome(outcome)
        replay_limit = mind.prepare_learning(outcome, learning)
        if replay_limit is not None:
            audit = world.pay_cognition(learning.work)
            outcome["body"] = world.body
            replays = mind.learn_from_outcome(
                outcome, replay_limit=replay_limit)
            if replays != replay_limit:
                raise RuntimeError("executed replays differ from prepaid replay count")
            paid_learning = {key: audit[key]["paid"]
                             for key in ("energy", "vigilance")}
    return {"schema": RECEIPT_SCHEMA, "phase": "POST_PAID_LEARNING",
            "tick": world.t, "action": action, "param": param,
            "body_after_motor": motor_body,
            "body_after_paid_learning": list(world.body),
            "decision_paid": {key: outcome["cognitive_accounting"][key]["paid"]
                              for key in ("energy", "vigilance")},
            "learning_paid": paid_learning,
            "death_causes": list(outcome["dead"]),
            "world_state_sha256": state_hash(world),
            "mind_state_sha256": state_hash(mind)}


class NativeEngineeringSession:
    """An in-process reference session, optionally rebuilt by verified replay."""

    def __init__(self, directory: Path, claim: Reservation, *, horizon: int,
                 world: World, mind: Mind, head: str,
                 witness_directory: Path | None = None,
                 remote_witness: RemoteEngineeringWitness | None = None):
        self.directory = Path(directory)
        self.claim = claim
        self.horizon = horizon
        self.world = world
        self.mind = mind
        self.head = head
        # Sequence zero has no sealed receipt to compare against. Pin the
        # complete native state produced by this construction before its
        # first paid motor; this is process-local, not independent M11 custody.
        self._virgin_world_sha256 = state_hash(world)
        self._virgin_mind_sha256 = state_hash(mind)
        self.witness_directory = (None if witness_directory is None
                                  else Path(witness_directory))
        self.remote_witness = remote_witness
        self._stopped = False

    @classmethod
    def begin(cls, directory: Path, claim: Reservation, *, genome: dict,
              spec: WorldSpec, horizon: int,
              witness_directory: Path | None = None,
              remote_witness: RemoteEngineeringWitness | None = None) -> NativeEngineeringSession:
        """Consume a fresh, source-matched engineering slot, never a cohort."""
        if type(claim) is not Reservation or type(spec) is not WorldSpec:
            raise TypeError("exact I3 engineering claim and WorldSpec required")
        if type(horizon) is not int or not 1 <= horizon <= 100:
            raise ValueError("engineering-only horizon must be 1..100")
        if claim != make_engineering_claim(birth_index=claim.birth_index,
                genome=genome, spec=spec, life_seed=claim.life_seed):
            raise PermissionError("engineering claim does not match current source/world/genome")
        world = World(spec)
        mind = Mind(genome, claim.life_seed)
        if world.dead:
            raise PermissionError("initial I3 body is already dead")
        # Verify the full state is representable before consuming a slot.
        state_hash(world)
        state_hash(mind)
        if remote_witness is not None:
            if type(remote_witness) is not RemoteEngineeringWitness or witness_directory is not None:
                raise ValueError("remote and local witness modes must be exclusive")
            if claim.life_seed > 2**63 - 1:
                raise ValueError("remote authority cannot persist this life seed")
        if witness_directory is not None:
            # SQLite witness seeds must fit the signed 64-bit integer column.
            if claim.life_seed > 2**63 - 1:
                raise ValueError("local witness cannot persist this life seed")
            # Preflight the separate local witness before consuming a birth slot.
            witness.validate_location(witness_directory, directory)
        reserve(directory, claim)  # durable one-shot local reservation
        view = initialize(directory, claim, horizon=horizon,
                          initial_body=world.body,
                          witness_mode=(REMOTE_MODE if remote_witness is not None
                                        else ANCHOR_MODE if witness_directory is not None
                                        else LEGACY_MODE))
        if witness_directory is not None:
            # A failure here leaves an unusable birth slot, never a hidden life.
            witness.register(witness_directory, directory, claim, view)
        if remote_witness is not None:
            # Fail-closed incomplete genesis, never an implicit local fallback.
            remote_witness.register(claim, view)
        return cls(directory, claim, horizon=horizon, world=world,
                   mind=mind, head=view["head_sha256"],
                   witness_directory=witness_directory,
                   remote_witness=remote_witness)

    @classmethod
    def reconstruct(cls, directory: Path, claim: Reservation, *, genome: dict,
                    spec: WorldSpec,
                    witness_directory: Path | None = None,
                    remote_witness: RemoteEngineeringWitness | None = None) -> NativeEngineeringSession:
        """Cold read + source-pinned *detached deterministic replay*.

        Never replays a PREPARED/uncertain motor, a dead/censored life, or an
        external action. All old actions are recomputed on a fresh, isolated
        local World, and every decision, payment and post-learning state must
        match the sealed original before a new motor can be authorized.
        This is NOT externally anchored M11 or production anti-rollback.
        """
        if type(claim) is not Reservation or type(spec) is not WorldSpec:
            raise TypeError("exact I3 engineering claim and WorldSpec required")
        if claim != make_engineering_claim(birth_index=claim.birth_index,
                genome=genome, spec=spec, life_seed=claim.life_seed):
            raise PermissionError("current source/world/genome differs from sealed life")
        view = inspect(directory, claim)  # rejects incomplete or corrupt ledger
        if remote_witness is not None and (type(remote_witness) is not RemoteEngineeringWitness
                                           or witness_directory is not None):
            raise ValueError("remote and local witness modes must be exclusive")
        mode = (REMOTE_MODE if remote_witness is not None else
                ANCHOR_MODE if witness_directory is not None else LEGACY_MODE)
        if view["witness_mode"] != mode:
            raise PermissionError("registered engineering witness cannot be bypassed")
        if witness_directory is not None:
            witness.verify(witness_directory, directory, claim, view)
        if remote_witness is not None:
            remote_witness.verify(claim, view)
        if view["terminal"] != "OPEN":
            raise PermissionError("cannot reconstruct or resume a terminal I3 life")
        world, mind = World(spec), Mind(genome, claim.life_seed)
        if world.dead or view["horizon"] > 100:
            raise PermissionError("invalid native engineering genesis or horizon")
        for event in view["events"]:
            action, param, work, intent = _native_decide(world, mind)
            if intent != event["intent"]:
                raise PermissionError("historical native choice/work is not reproducible")
            actual = _native_outcome(world, mind, action, param, work)
            if actual != event["receipt"]:
                raise PermissionError("historical native outcome/cost/state differs")
        if (world.t != view["sequence"]
                or list(world.body) != view["last_body"]):
            raise PermissionError("reconstructed native state differs from custody")
        # No restore fallback or source-independent lineage import.
        if witness_directory is not None:
            # Revalidate after deterministic replay, before new motor authority.
            witness.verify(witness_directory, directory, claim)
        if remote_witness is not None:
            remote_witness.verify(claim, inspect(directory, claim))
        return cls(directory, claim, horizon=view["horizon"],
                   world=world, mind=mind, head=view["head_sha256"],
                   witness_directory=witness_directory,
                   remote_witness=remote_witness)

    def step(self) -> dict:
        """One genuine native paid step, ledger PREPARE *before* World.step.

        Any exception irrevocably stops this process-local attempt; only an
        entirely sealed, independently verified chain may be reconstructed.
        """
        if self._stopped:
            raise PermissionError("failed or terminal native engineering session")
        try:
            view = inspect(self.directory, self.claim)
            mode = (REMOTE_MODE if self.remote_witness is not None else
                    ANCHOR_MODE if self.witness_directory is not None
                    else LEGACY_MODE)
            if view["witness_mode"] != mode:
                raise PermissionError("native witness mode changed or omitted")
            if self.witness_directory is not None:
                witness.verify(self.witness_directory, self.directory, self.claim, view)
            if self.remote_witness is not None:
                self.remote_witness.verify(self.claim, view)
            if (view["head_sha256"] != self.head or view["terminal"] != "OPEN"
                    or view["sequence"] != self.world.t
                    or view["last_body"] != list(self.world.body)):
                raise PermissionError("native state and custody have diverged")
            if view["events"]:
                last = view["events"][-1]["receipt"]
                if (last["world_state_sha256"] != state_hash(self.world)
                        or last["mind_state_sha256"] != state_hash(self.mind)):
                    raise PermissionError("in-memory native state changed after sealing")
            elif (self._virgin_world_sha256 != state_hash(self.world)
                  or self._virgin_mind_sha256 != state_hash(self.mind)):
                # Neither body nor tick detects a changed hidden environment
                # or unpaid learned value before the first sealed receipt.
                raise PermissionError(
                    "unsealed native genesis state changed before first motor")
            action, param, work, intent = _native_decide(self.world, self.mind)
            prepared = prepare(self.directory, self.claim,
                               expected_head=self.head, intent=intent)
            if self.witness_directory is not None:
                # Witness PREPARED is durable BEFORE executing a new motor.
                witness.prepared(self.witness_directory, self.directory,
                                 self.claim, previous_ledger=view, intent=intent)
            if self.remote_witness is not None:
                # Signed network acknowledgement BEFORE executing the motor.
                self.remote_witness.prepared(self.directory, self.claim,
                                             previous_ledger=view, intent=intent)
            # The sole *new* World.step happens after durable PREPARED in both stores.
            receipt = _native_outcome(self.world, self.mind, action, param, work)
            sealed = seal(self.directory, self.claim,
                          expected_head=prepared["prior_head_sha256"],
                          seal_token=prepared["seal_token"], receipt=receipt)
            if self.witness_directory is not None:
                witness.committed(self.witness_directory, self.directory,
                                   self.claim, previous_ledger=view, intent=intent)
            if self.remote_witness is not None:
                self.remote_witness.committed(self.directory, self.claim,
                                              previous_ledger=view, intent=intent)
            self.head = sealed["head_sha256"]
            if sealed["terminal"] != "OPEN":
                self._stopped = True
            return {"schema": "i3-native-engineering-step/v1", "status": STATUS,
                    "action": action, "param": param, "receipt": receipt,
                    "pos": list(self.world.pos), "sequence": sealed["sequence"],
                    "head_sha256": self.head, "terminal": sealed["terminal"],
                    "durable_m11": False, "cold_recovery_available": False,
                    "witness_mode": mode,
                    "remote_witness_transport": self.remote_witness is not None,
                    "independent_m11_antirollback": False,
                    "scientific_world_authorized": False}
        except BaseException:
            self._stopped = True
            raise
