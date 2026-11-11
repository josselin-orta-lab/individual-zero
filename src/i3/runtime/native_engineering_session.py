"""One-shot *engineering* integration of native I3 Mind/World with step custody.

Creates a fresh local **test-only** World and Mind (P1.3 reference), never a
registered birth or scientific cohort. A committed receipt proves that this
in-process path actually called the native physics and paid learning. It does
NOT persist/reconstruct the full mutable organism, authenticate source bytes,
or permit cold continuation. Failure at any stage poisons the session.

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
    INTENT_SCHEMA, RECEIPT_SCHEMA, initialize, inspect, prepare, seal,
)
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


class NativeEngineeringSession:
    """Ephemeral, one-process-only native reference session, no restart API."""

    def __init__(self, directory: Path, claim: Reservation, *, horizon: int,
                 world: World, mind: Mind, head: str):
        self.directory = Path(directory)
        self.claim = claim
        self.horizon = horizon
        self.world = world
        self.mind = mind
        self.head = head
        self._stopped = False

    @classmethod
    def begin(cls, directory: Path, claim: Reservation, *, genome: dict,
              spec: WorldSpec, horizon: int) -> NativeEngineeringSession:
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
        reserve(directory, claim)  # durable one-shot local reservation
        view = initialize(directory, claim, horizon=horizon,
                          initial_body=world.body)
        return cls(directory, claim, horizon=horizon, world=world,
                   mind=mind, head=view["head_sha256"])

    def step(self) -> dict:
        """One genuine native paid step, ledger PREPARE *before* World.step.

        An exception never permits the same in-memory session to try again,
        including when the action may have been executed but the seal failed.
        """
        if self._stopped:
            raise PermissionError("failed or terminal native engineering session")
        try:
            view = inspect(self.directory, self.claim)
            if (view["head_sha256"] != self.head or view["terminal"] != "OPEN"
                    or view["sequence"] != self.world.t
                    or view["last_body"] != list(self.world.body)):
                raise PermissionError("native state and custody have diverged")
            if view["events"]:
                last = view["events"][-1]["receipt"]
                if (last["world_state_sha256"] != state_hash(self.world)
                        or last["mind_state_sha256"] != state_hash(self.mind)):
                    raise PermissionError("in-memory native state changed after sealing")

            capture = self.world.capture()  # sole input to Mind
            budget = CognitiveBudget(self.world.body, self.world.laws)
            action, param, work, _info = self.mind.decide(capture, budget)
            if work != budget.work:
                raise ValueError("Mind decision work differs from the native allowance")
            before = list(self.world.body)
            intent = {"schema": INTENT_SCHEMA, "tick_before": self.world.t,
                      "body_before": before, "action": action, "param": param,
                      "decision_work": {name: getattr(work, name)
                          for name in ("cycles", "simulated_steps", "memory_items", "replays")}}
            prepared = prepare(self.directory, self.claim,
                               expected_head=self.head, intent=intent)
            # No external motor selector: one original native action only.
            outcome = self.world.step(action, param, work)
            motor_body = list(outcome["body"])
            paid_learning = {"energy": 0.0, "vigilance": 0.0}
            if not outcome["dead"] and self.mind.last is not None:
                learning = CognitiveBudget(outcome["body"], self.world.laws)
                self.mind.observe_outcome(outcome)
                replay_limit = self.mind.prepare_learning(outcome, learning)
                if replay_limit is not None:
                    audit = self.world.pay_cognition(learning.work)
                    outcome["body"] = self.world.body
                    replays = self.mind.learn_from_outcome(
                        outcome, replay_limit=replay_limit)
                    if replays != replay_limit:
                        raise RuntimeError("executed replays differ from prepaid replay count")
                    paid_learning = {key: audit[key]["paid"]
                                     for key in ("energy", "vigilance")}
            receipt = {"schema": RECEIPT_SCHEMA, "phase": "POST_PAID_LEARNING",
                       "tick": self.world.t, "action": action, "param": param,
                       "body_after_motor": motor_body,
                       "body_after_paid_learning": list(self.world.body),
                       "decision_paid": {key: outcome["cognitive_accounting"][key]["paid"]
                                         for key in ("energy", "vigilance")},
                       "learning_paid": paid_learning,
                       "death_causes": list(outcome["dead"]),
                       "world_state_sha256": state_hash(self.world),
                       "mind_state_sha256": state_hash(self.mind)}
            sealed = seal(self.directory, self.claim,
                          expected_head=prepared["prior_head_sha256"],
                          seal_token=prepared["seal_token"], receipt=receipt)
            self.head = sealed["head_sha256"]
            if sealed["terminal"] != "OPEN":
                self._stopped = True
            return {"schema": "i3-native-engineering-step/v1", "status": STATUS,
                    "action": action, "param": param, "receipt": receipt,
                    "pos": list(self.world.pos), "sequence": sealed["sequence"],
                    "head_sha256": self.head, "terminal": sealed["terminal"],
                    "durable_m11": False, "cold_recovery_available": False,
                    "scientific_world_authorized": False}
        except BaseException:
            self._stopped = True
            raise
