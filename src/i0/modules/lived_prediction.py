"""Stage-11 descriptive prospective water prediction from lived memory witnesses.

Read-only projection of the *canonical* causal owner, not an independent
causal model or an Equipment correction. May inform prospective DC-09/P-47
comparison only. Never accepts bench/oracle or the current action's outcome.

Normative EN MVP v1.2.1 sections 9.5/9.6, 12.3, 13.2; INV-14/25/33.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Mapping

from i0.contracts import PredictedConsequence


@dataclass(frozen=True, slots=True)
class LivedPredictionConfig:
    version: str
    min_distinct_episodes: int
    maximum_spread: float
    precision_floor: float
    max_precision: float

    def validate(self) -> None:
        if not self.version or type(self.min_distinct_episodes) is not int or self.min_distinct_episodes < 1:
            raise ValueError("prospective prediction requires explicit positive sample count")
        for name in ("maximum_spread", "precision_floor", "max_precision"):
            value = getattr(self, name)
            if (type(value) not in (float, int)
                or not isfinite(value) or value < 0 or value > 100):
                raise ValueError("invalid versioned prediction tolerance")
        if self.precision_floor > self.max_precision or self.maximum_spread > self.max_precision:
            raise ValueError("prediction tolerances conflict")


@dataclass(frozen=True, slots=True)
class LivedWaterForecast:
    """Descriptive forecast, never causal attribution nor simulated value."""

    consequence: PredictedConsequence
    source_transition_refs: tuple[str, ...]
    source_episode_refs: tuple[str, ...]
    source_steps: tuple[int, ...]
    config_version: str

    def validate(self) -> None:
        n = len(self.source_transition_refs)
        if (n == 0 or n != len(self.source_episode_refs)
            or n != len(self.source_steps)
            or len(set(self.source_transition_refs)) != n
            or len(set(self.source_episode_refs)) != n
            or len(set(self.source_steps)) != n
            or self.consequence.variable != "water"
            or not isfinite(self.consequence.value_or_delta)
            or not 0 <= self.consequence.value_or_delta <= 100
            or not isfinite(self.consequence.precision)
            or self.consequence.precision < 0):
            raise ValueError("invalid independent lived prediction witnesses")


class LivedWaterPredictor:
    """Stateless; no private learned causal copy and no simulator mutation."""

    def __init__(self, config: LivedPredictionConfig) -> None:
        config.validate()
        self.config = config

    def predict(
        self, *, canonical_state: Mapping[str, object],
        t_monde: int, water_before: float, position: tuple[int, int],
    ) -> LivedWaterForecast | None:
        if (not isinstance(canonical_state, Mapping)
            or type(t_monde) is not int or t_monde < 1
            or type(water_before) not in (int, float)
            or not isfinite(water_before) or not 0 <= water_before < 100
            or not isinstance(position, tuple) or len(position) != 2
            or any(type(v) is not int for v in position)):
            raise ValueError("prospective input must be an accessible frozen capture")
        if not isinstance(canonical_state.get("lived_causal_actions"), list):
            raise ValueError("canonical owner must publish a lived action collection")
        samples: list[tuple[int, str, str, float]] = []
        used_transitions: set[str] = set()
        used_episodes: set[str] = set()
        used_steps: set[int] = set()
        sources = (
            *canonical_state["lived_causal_actions"],
            *canonical_state.get("causal_action_witnesses", ()),
        )
        for record in sources:
            if not isinstance(record, Mapping):
                raise ValueError("invalid canonical memory witness")
            if (record.get("contingency_ref") != "causal:hydration"
                or record.get("motive_type") not in ("test_causal", "active_goal")
                or record.get("position") not in (position, list(position))):
                continue
            issued, followed = record.get("sent_t_monde"), record.get("observed_t_monde")
            command_ref = record.get("command_event_ref")
            transition_ref = record.get("transition_event_ref")
            episode_ref = record.get("physical_episode_ref")
            before, after = record.get("water_before"), record.get("water_observed")
            # Closed physical episode AND exact independent command/transition
            # must predate the current decision; missing/ambiguous evidence
            # is not a numeric training example.
            if (type(issued) is not int or type(followed) is not int
                or followed != issued + 1 or followed >= t_monde
                or not all(isinstance(v, str) and v for v in
                           (command_ref, transition_ref, episode_ref))
                or command_ref == transition_ref
                or type(before) not in (float, int)
                or type(after) not in (float, int)
                or not (isfinite(before) and isfinite(after)
                        and 0 <= before < 100 and 0 <= after <= 100)):
                continue
            if (transition_ref in used_transitions
                or episode_ref in used_episodes or issued in used_steps):
                # A duplicated physical transition cannot create another
                # independent sample; contradictory duplicate labels fail.
                raise ValueError("reused lived prediction physical source")
            used_transitions.add(transition_ref)
            used_episodes.add(episode_ref)
            used_steps.add(issued)
            samples.append((issued, transition_ref, episode_ref, float(after - before)))
        if len(samples) < self.config.min_distinct_episodes:
            return None
        samples.sort()
        deltas = [row[3] for row in samples]
        spread = max(deltas) - min(deltas)
        if spread > self.config.maximum_spread:
            return None
        estimate = min(100.0, max(0.0, water_before + sum(deltas) / len(deltas)))
        precision = self.config.precision_floor + spread / 2
        if precision > self.config.max_precision:
            return None
        forecast = LivedWaterForecast(
            consequence=PredictedConsequence(
                variable="water", value_or_delta=estimate, precision=precision,
            ),
            source_transition_refs=tuple(row[1] for row in samples),
            source_episode_refs=tuple(row[2] for row in samples),
            source_steps=tuple(row[0] for row in samples),
            config_version=self.config.version,
        )
        forecast.validate()
        return forecast
