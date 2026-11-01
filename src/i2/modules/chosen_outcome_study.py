"""G2-only, pure observational chosen-outcome valuation study.

Unlike matched-pair H2 this uses only the last *actually observed chosen-arm*
consequence. This is NOT an I2 learning owner, persisted H2 state, a causal
contrast, an M11 attester, motor policy or living WorldBody. Its injected
source is a synthetic research port. Competition still pays the entire frame.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Protocol

from .competition_preview import (
    CompetitionReceipt, SubjectiveValuation, MAX_VALUE_MAGNITUDE, _frame,
)
from .intention_continuity import _ref
from .intention_ingress import ObservationClaim

MAX_RECORDED_CHOICES = 64
OUTCOME_LIMIT = 200
FIXED_SCORE_OFFSET = 4  # preregistered toy-domain choice, not physiological value


@dataclass(frozen=True, slots=True)
class ObservedChosenResult:
    """One admitted-by-controller action and its later recorded result."""

    life_ref: str
    issue_capture_ref: str
    chosen_action_ref: str
    observed_step: int
    evidence_ref: str
    observed_net: int

    def validate(self) -> None:
        for name in ("life_ref", "issue_capture_ref", "chosen_action_ref",
                     "evidence_ref"):
            _ref(getattr(self, name), name)
        if type(self.observed_step) is not int or self.observed_step < 0:
            raise ValueError("invalid observed physical step")
        if type(self.observed_net) is not int or abs(self.observed_net) > OUTCOME_LIMIT:
            raise ValueError("invalid chosen outcome magnitude")


class ChosenResultEvidence(Protocol):
    """Research test double only, never an independently trusted witness."""

    def verify_chosen_result(self, *, result: ObservedChosenResult) -> bool: ...


def observed_chosen_scores(
    *, claim: ObservationClaim, results: tuple[ObservedChosenResult, ...],
    source: ChosenResultEvidence, priors: dict[str, int],
) -> dict[str, int]:
    """No counterfactual, no unseen world state, no same-step consequence.

    Last observed score is an intentionally crude recency heuristic for
    reversible environments, NOT a calibrated H2 estimate. The fixed prior
    and offset must be reported as intervention assumptions. Recompute from
    the exact test evidence for every capture; store NO new owner state.
    """
    if type(claim) is not ObservationClaim:
        raise ValueError("exact personal capture required")
    claim.validate()
    if (type(results) is not tuple or len(results) > MAX_RECORDED_CHOICES
            or type(priors) is not dict):
        raise ValueError("bounded observations and fixed priors required")
    if not callable(getattr(source, "verify_chosen_result", None)):
        raise ValueError("chosen-outcome evidence source required")
    scores = {}
    for semantic, prior in priors.items():
        _ref(semantic, "prior semantic")
        if type(prior) is not int or abs(prior) > MAX_VALUE_MAGNITUDE:
            raise ValueError("invalid fixed prior")
        scores[semantic] = prior

    last_step = -1
    captures = set()
    evidence_refs = set()
    for result in results:
        if type(result) is not ObservedChosenResult:
            raise ValueError("exact observed chosen result required")
        result.validate()
        if (result.life_ref != claim.life_ref or
                result.observed_step <= last_step or
                result.observed_step >= claim.capture.step or
                result.issue_capture_ref == claim.capture.ref or
                result.issue_capture_ref in captures or
                result.evidence_ref in evidence_refs):
            raise ValueError("stale, future, duplicated or foreign chosen evidence")
        if result.chosen_action_ref not in scores:
            raise ValueError("chosen action is absent from fixed priors")
        if source.verify_chosen_result(result=result) is not True:
            raise ValueError("chosen outcome was not actually observed")
        last_step = result.observed_step
        captures.add(result.issue_capture_ref)
        evidence_refs.add(result.evidence_ref)
        score = result.observed_net + FIXED_SCORE_OFFSET
        if abs(score) > MAX_VALUE_MAGNITUDE:
            raise ValueError("chosen-outcome score overflows Competition bounds")
        scores[result.chosen_action_ref] = score
    return scores


class ChosenOutcomeValuationStudy:
    """Inject a past-only synthetic readout into existing *paid* Competition.

    No internal memory or motor dispatch. The research controller owns the
    test evidence; a living I2 would need a separately reviewed atomic owner.
    """

    def __init__(
        self, *, claim: ObservationClaim,
        results: tuple[ObservedChosenResult, ...],
        source: ChosenResultEvidence, priors: dict[str, int],
    ) -> None:
        self.claim = claim
        self.results = results
        self.source = source
        self.priors = dict(priors)

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
            raise ValueError("paid batch does not match current observation")
        values = observed_chosen_scores(
            claim=self.claim, results=self.results,
            source=self.source, priors=self.priors,
        )
        output = []
        for candidate, receipt in zip(frame.candidates, receipts):
            if type(receipt) is not CompetitionReceipt:
                raise ValueError("exact paid receipt required")
            receipt.validate()
            if (receipt.life_ref != frame.life_ref or
                    receipt.frame_ref != frame.frame_ref or
                    receipt.claim_digest != frame.claim_digest or
                    receipt.candidate_ref != candidate.candidate_ref):
                raise ValueError("foreign or unbound paid candidate receipt")
            if candidate.semantic_ref not in values:
                raise ValueError("missing fixed candidate prior")
            bound = json.dumps(
                [frame.claim_digest, candidate.candidate_ref, receipt.ref,
                 candidate.semantic_ref, values[candidate.semantic_ref],
                 [r.evidence_ref for r in self.results]],
                separators=(",", ":"), ensure_ascii=True,
            ).encode("ascii")
            output.append(SubjectiveValuation(
                candidate.candidate_ref, receipt.ref,
                "chosen:synthetic:" + sha256(bound).hexdigest(),
                values[candidate.semantic_ref],
            ))
        return tuple(output)
