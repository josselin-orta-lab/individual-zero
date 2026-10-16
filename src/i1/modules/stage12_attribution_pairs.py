"""GA-06: one canonical Metacognition owner joins independent lived sources.

This is a bounded *candidate* ledger, not another cognitive owner, evaluator,
Oracle or source of subjective labels. All references are to separate original
source receipts whose semantic linkage an external auditor must reproduce.
"""
from __future__ import annotations

from dataclasses import dataclass

PAIR_VERSION = "stage12-goal-outcome-agency-pair-v1"


def _ref(value: object) -> bool:
    return type(value) is str and bool(value.strip())


@dataclass(frozen=True, slots=True)
class LivedAttributionPair:
    pair_ref: str
    life_id: str
    intent_ref: str
    goal_followup_ref: str
    agency_assessment_ref: str
    agency_judgement_ref: str
    observed_world_step: int
    outcome: str
    agency: str
    version: str = PAIR_VERSION

    def validate(self) -> None:
        if (self.version != PAIR_VERSION
                or not all(_ref(v) for v in (
                    self.pair_ref, self.life_id, self.intent_ref,
                    self.goal_followup_ref, self.agency_assessment_ref,
                    self.agency_judgement_ref,
                ))
                or len({
                    self.pair_ref, self.goal_followup_ref, self.agency_judgement_ref,
                }) != 3
                or type(self.observed_world_step) is not int
                or self.observed_world_step < 2
                or self.outcome not in ("success", "failure")
                or self.agency not in ("self", "world")):
            raise ValueError("unverifiable first-person outcome/agency pair")

    def as_dict(self) -> dict[str, object]:
        return {k: getattr(self, k) for k in self.__dataclass_fields__}

    @classmethod
    def from_dict(cls, state: object) -> "LivedAttributionPair":
        if type(state) is not dict or set(state) != set(cls.__dataclass_fields__):
            raise ValueError("invalid immutable attribution pair image")
        value = cls(**state)
        value.validate()
        return value


class Stage12AttributionPairs:
    """Versioned queue of one pending lived pair and committed unique refs."""

    schema = PAIR_VERSION

    def __init__(self) -> None:
        self._pending: LivedAttributionPair | None = None
        self._seen_pair_refs: set[str] = set()
        self._seen_intents: set[str] = set()
        self._seen_judgements: set[str] = set()
        self._last_observed_world_step = 0

    @property
    def pending(self) -> LivedAttributionPair | None:
        return self._pending

    def admit(self, value: LivedAttributionPair) -> None:
        if type(value) is not LivedAttributionPair:
            raise TypeError("canonical lived attribution pair required")
        value.validate()
        if (self._pending is not None
                or value.observed_world_step <= self._last_observed_world_step
                or value.pair_ref in self._seen_pair_refs
                or value.intent_ref in self._seen_intents
                or value.agency_judgement_ref in self._seen_judgements):
            raise ValueError("duplicate, overlapping or stale lived attribution pair")
        self._pending = value
        self._seen_pair_refs.add(value.pair_ref)
        self._seen_intents.add(value.intent_ref)
        self._seen_judgements.add(value.agency_judgement_ref)
        self._last_observed_world_step = value.observed_world_step

    def consume(self, *, diagnostic_world_step: int) -> LivedAttributionPair | None:
        """A pair is usable precisely in the NEXT paid diagnostic sample.

        Missed/denied diagnostics consume but never duplicate or backdate the
        sample. Caller records an explicit suppression receipt if unavailable.
        """
        if type(diagnostic_world_step) is not int or diagnostic_world_step < 1:
            raise ValueError("invalid attribution diagnostic clock")
        pair = self._pending
        if pair is None or diagnostic_world_step <= pair.observed_world_step:
            return None
        self._pending = None
        if diagnostic_world_step != pair.observed_world_step + 1:
            return None
        return pair

    def export_causal_state(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "pending_pair": None if self._pending is None else self._pending.as_dict(),
            "seen_pair_refs": sorted(self._seen_pair_refs),
            "seen_intents": sorted(self._seen_intents),
            "seen_judgements": sorted(self._seen_judgements),
            "last_observed_world_step": self._last_observed_world_step,
        }

    def restore_causal_state(self, state: object) -> None:
        if (type(state) is not dict or set(state) != {
            "schema", "pending_pair", "seen_pair_refs",
            "seen_intents", "seen_judgements", "last_observed_world_step",
        } or state["schema"] != self.schema
                or type(state["last_observed_world_step"]) is not int
                or state["last_observed_world_step"] < 0):
            raise ValueError("invalid canonical joined attribution custody")
        all_keys = ("seen_pair_refs", "seen_intents", "seen_judgements")
        for key in all_keys:
            values = state[key]
            if (type(values) is not list
                    or any(not _ref(v) for v in values)
                    or values != sorted(set(values))):
                raise ValueError("duplicated or malformed attribution pair provenance")
        count = len(state["seen_pair_refs"])
        if any(len(state[key]) != count for key in all_keys):
            raise ValueError("attribution receipt cardinalities contradict")
        if (bool(count) != (state["last_observed_world_step"] > 0)
                or self._pending is not None or self._seen_pair_refs
                or self._seen_intents or self._seen_judgements):
            raise ValueError("mortal metacognition attribution rewind forbidden")
        pending = None if state["pending_pair"] is None else LivedAttributionPair.from_dict(state["pending_pair"])
        if pending is not None and (
            pending.pair_ref not in state["seen_pair_refs"]
            or pending.intent_ref not in state["seen_intents"]
            or pending.agency_judgement_ref not in state["seen_judgements"]
            or pending.observed_world_step != state["last_observed_world_step"]
        ):
            raise ValueError("pending pair not grounded in the current unique ledger")
        self._pending = pending
        self._seen_pair_refs = set(state["seen_pair_refs"])
        self._seen_intents = set(state["seen_intents"])
        self._seen_judgements = set(state["seen_judgements"])
        self._last_observed_world_step = state["last_observed_world_step"]
