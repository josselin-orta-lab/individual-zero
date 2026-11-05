"""One-shot G1-LAB v1-r1: pure, local, source-bound need/aversion valuations.

This is an EXPLICITLY RESEARCHER-WRITTEN scoring hypothesis for a non-living
disposable lab.  It neither implements natural hunger nor grants M11, action
or birth authority. No second state owner: all previous outcomes are supplied
only from the same already-committed SQLite lab history.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json

from i2.modules.competition_preview import (
    CompetitionReceipt, MAX_VALUE_MAGNITUDE, SubjectiveValuation, _frame,
)
from i2.modules.intention_ingress import ObservationClaim
from i2.modules.intention_continuity import _ref

ARMS = ("full", "need_off", "aversion_off", "fixed")
NUTRIENT_GAIN = 8
AVERSION_SIGNALS = (0, 4)
ENERGIES = (17, 60)
BASE_PRIORS = {
    "affordance:collect:berry_a": 3,
    "affordance:eat:berry_a": 4,
    "affordance:drink:water": 1,
}
EAT = "affordance:eat:berry_a"
PROTOCOL_BLOB = "a279067fbfd21f02ee4aa7854509c19f12cfbb62"


@dataclass(frozen=True, slots=True)
class PersonalFoodOutcome:
    """One chosen action, first visible only AFTER its committed effect."""

    life_ref: str
    capture_ref: str
    chosen_action_ref: str
    observed_step: int
    evidence_ref: str
    nutrition_gain: int
    aversive_signal: int

    def validate(self) -> None:
        for name in ("life_ref", "capture_ref", "chosen_action_ref",
                     "evidence_ref"):
            _ref(getattr(self, name), name)
        if (type(self.observed_step) is not int or self.observed_step < 0 or
                type(self.nutrition_gain) is not int or
                type(self.aversive_signal) is not int or
                self.chosen_action_ref not in BASE_PRIORS or
                self.nutrition_gain not in (0, NUTRIENT_GAIN) or
                self.aversive_signal not in AVERSION_SIGNALS or
                (self.chosen_action_ref != EAT and
                 (self.nutrition_gain != 0 or self.aversive_signal != 0)) or
                (self.chosen_action_ref == EAT and
                 self.nutrition_gain != NUTRIENT_GAIN)):
            raise ValueError("not a valid personally chosen laboratory outcome")


def need_aversion_scores(
    *, claim: ObservationClaim, results: tuple[PersonalFoodOutcome, ...],
    previous_energy: int, arm: str,
) -> dict[str, int]:
    """Only past chosen results and the PREVIOUS energy may influence scores.

    These are engineered scores, not inferred biological preferences. No
    unchosen counterfactual, hidden world/sensory law, time bonus or same-step
    consequence may enter. Old negative memories remain in the outcome log
    even if the latest event changes the currently used estimate.
    """
    if type(claim) is not ObservationClaim:
        raise ValueError("exact first-person claim required")
    claim.validate()
    if (arm not in ARMS or type(previous_energy) is not int or
            not 0 < previous_energy <= 100 or
            type(results) is not tuple or len(results) > 8 or
            f"evidence:lab:body-energy:{previous_energy}"
            not in claim.subjective_evidence_refs):
        raise ValueError("no permitted prior-committed body evidence")
    observed: dict[str, tuple[int, int]] = {}
    seen_ref: set[str] = set()
    seen_capture: set[str] = set()
    last_step = -1
    for result in results:
        if type(result) is not PersonalFoodOutcome:
            raise ValueError("exact personal result required")
        result.validate()
        if (result.life_ref != claim.life_ref or
                result.capture_ref == claim.capture.ref or
                result.capture_ref in seen_capture or
                result.evidence_ref in seen_ref or
                result.evidence_ref not in claim.subjective_evidence_refs or
                result.observed_step <= last_step or
                result.observed_step >= claim.capture.step):
            raise ValueError("future, unobserved, duplicated or foreign food evidence")
        last_step = result.observed_step
        seen_capture.add(result.capture_ref)
        seen_ref.add(result.evidence_ref)
        observed[result.chosen_action_ref] = (
            result.nutrition_gain, result.aversive_signal,
        )
    if arm == "fixed":
        return dict(BASE_PRIORS)
    deficit = 100 - previous_energy
    values: dict[str, int] = {}
    for action, prior in BASE_PRIORS.items():
        nutrition, aversion = observed.get(action, (0, 0))
        need = (deficit * nutrition) // 100 if arm != "need_off" else 0
        cost = aversion if arm != "aversion_off" else 0
        score = prior + need - cost
        if abs(score) > MAX_VALUE_MAGNITUDE:
            raise ValueError("score exceeds already bounded paid Competition")
        values[action] = score
    return values


class NeedAversionValuation:
    """Paid Competition source for the ONE approved non-living laboratory."""

    def __init__(self, *, claim: ObservationClaim,
                 results: tuple[PersonalFoodOutcome, ...],
                 previous_energy: int, arm: str) -> None:
        self.claim = claim
        self.results = results
        self.previous_energy = previous_energy
        self.arm = arm

    def evaluate_batch(
        self, *, frame: object, receipts: tuple[CompetitionReceipt, ...],
    ) -> tuple[SubjectiveValuation, ...]:
        frame = _frame(frame)
        if (frame.life_ref != self.claim.life_ref or
                frame.capture_ref != self.claim.capture.ref or
                frame.physical_step != self.claim.capture.step or
                frame.claim_digest != self.claim.digest() or
                type(receipts) is not tuple or
                len(receipts) != len(frame.candidates)):
            raise ValueError("valuation not bound to paid personal frame")
        scores = need_aversion_scores(
            claim=self.claim, results=self.results,
            previous_energy=self.previous_energy, arm=self.arm,
        )
        result_refs = [asdict(r) for r in self.results]
        valued = []
        for candidate, receipt in zip(frame.candidates, receipts):
            if type(receipt) is not CompetitionReceipt:
                raise ValueError("exact paid receipt required")
            receipt.validate()
            if (receipt.life_ref != frame.life_ref or
                    receipt.frame_ref != frame.frame_ref or
                    receipt.claim_digest != frame.claim_digest or
                    receipt.candidate_ref != candidate.candidate_ref or
                    candidate.semantic_ref not in scores):
                raise ValueError("foreign, missing or unbound paid evidence")
            score = scores[candidate.semantic_ref]
            sealed = json.dumps(
                [frame.claim_digest, receipt.ref, candidate.candidate_ref,
                 candidate.semantic_ref, score, self.previous_energy,
                 self.arm, result_refs],
                sort_keys=True, separators=(",", ":"), ensure_ascii=True,
            ).encode("ascii")
            valued.append(SubjectiveValuation(
                candidate.candidate_ref, receipt.ref,
                "chosen:synthetic:" + sha256(sealed).hexdigest(), score,
            ))
        return tuple(valued)
