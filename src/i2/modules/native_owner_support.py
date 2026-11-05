"""Pure body and reflex helpers consumed by the SAME existing I2 SQLite owner.

Never a second persistent world, scheduler, motor authority, or independent
M11 witness. Inputs come only from the owner's committed current body and
immutable genesis traits; hidden action effects are supplied only after
admission to the existing transaction.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from math import isfinite

from i2.modules.native_body_contract import Body
from i2.modules.native_birth_temperament import BirthTemperament, declared_temperament
from i2.modules.native_physiological_needs import assess_needs
from i2.modules.intention_ingress import ObservationClaim
from i2.modules.unstable_world_reappraisal_contract import SurvivalReflexSnapshot

VERSION = "i2-native-integrated-physical-observation-v1"


def _json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                      allow_nan=False)


def saved_body(raw: str) -> Body:
    if type(raw) is not str:
        raise ValueError("native committed body required")
    data = json.loads(raw)
    if (type(data) is not dict or
            set(data) != {"energy", "food", "water", "integrity"}):
        raise ValueError("four exact current body channels required")
    body = Body(*(float(data[k]) for k in ("energy", "food", "water", "integrity")))
    if raw != _json(data):
        raise ValueError("noncanonical committed body")
    return body


def saved_traits(raw: str) -> BirthTemperament:
    if type(raw) is not str:
        raise ValueError("immutable birth temperament required")
    data = json.loads(raw)
    traits = declared_temperament(data)
    if raw != _json(data):
        raise ValueError("noncanonical birth temperament")
    return traits


def genesis_binding(body_json: str, traits_json: str) -> str:
    saved_body(body_json)
    saved_traits(traits_json)
    return sha256(_json([VERSION, body_json, traits_json]).encode("ascii")).hexdigest()[:24]


def current_evidence(body: Body, traits: BirthTemperament) -> tuple[str, ...]:
    """First-person current signals; no hidden payoff or future outcome."""
    needs = assess_needs(body, traits)
    return tuple([
        "evidence:i2:native:physiology:" + VERSION,
        "evidence:i2:native:energy:" + format(body.energy, ".6f"),
        "evidence:i2:native:food:" + format(body.food, ".6f"),
        "evidence:i2:native:water:" + format(body.water, ".6f"),
        "evidence:i2:native:integrity:" + format(body.integrity, ".6f"),
        "evidence:i2:native:leading_need:" + (needs.leading_need or "none"),
        "evidence:i2:native:birth_traits:" +
        sha256(_json(traits.as_dict()).encode("ascii")).hexdigest()[:24],
    ])


def native_scores(scores: dict[str, int], body: Body,
                  traits: BirthTemperament, *, collect: str, eat: str,
                  drink: str) -> dict[str, int]:
    """A small declared innate drive on top of learned chosen-outcome scores.

    DRINK responds to real water deficit, EAT to real food deficit;
    exploration changes COLLECT's subjective ranking. No learning outcome
    is fabricated, and the trait cannot order a motor action.
    """
    needs = assess_needs(body, traits)
    adjustments = {
        drink: round(8 * needs.pressures["water"]),
        eat: round(8 * needs.pressures["food"]),
        collect: round(4 * needs.pressures["food"] +
                       2 * traits.exploration),
    }
    return {k: int(v + adjustments.get(k, 0)) for k, v in scores.items()}


@dataclass(frozen=True, slots=True)
class NativeCaptureReflex:
    """Innate current-body danger report, not learned and not motor-owning."""
    claim: ObservationClaim
    body: Body
    traits: BirthTemperament

    def __post_init__(self) -> None:
        self.claim.validate()
        if not set(current_evidence(self.body, self.traits)).issubset(
                self.claim.subjective_evidence_refs):
            raise ValueError("native reflex not bound to observed current body")

    @property
    def evidence_ref(self) -> str:
        return current_evidence(self.body, self.traits)[1]

    @property
    def state(self) -> str:
        needs = assess_needs(self.body, self.traits)
        if any(getattr(self.body, key) <= 2 for key in
               ("food", "water", "integrity")):
            return "PREEMPT"
        if needs.immediate_danger:
            return "CONSTRAIN"
        return "NO_PREEMPTION"

    def snapshot(self) -> SurvivalReflexSnapshot:
        return SurvivalReflexSnapshot(
            self.claim.life_ref, self.claim.capture.ref, self.claim.digest(),
            self.evidence_ref, self.state)

    def verify_survival_reflex(self, *, claim: ObservationClaim,
                               snapshot: SurvivalReflexSnapshot) -> bool:
        return claim == self.claim and snapshot == self.snapshot()
