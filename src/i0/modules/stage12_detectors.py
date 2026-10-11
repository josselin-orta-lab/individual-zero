"""Stage-12 metacognitive diagnostics from *lived* cognitive observations.

No WorldBody, Lab, journal, Oracle, Bench or evaluator imports. Detectors are
read-only warnings: they never change Competition values, Action Control,
physical outcomes, κ, or the motivational goal vector. The single canonical
Metacognition owner may embed this facet in a later integrated runtime.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, log
from typing import Mapping


def _finite(value: object) -> bool:
    return type(value) in (int, float) and isfinite(value)


@dataclass(frozen=True, slots=True)
class Stage12DetectionPolicy:
    version: str
    window: int
    stagnation_steps: int
    stagnation_tolerance: float
    loop_repetitions: int
    loop_max_period: int
    entropy_min_samples: int
    entropy_warning_fraction: float
    bias_min_outcomes_each: int
    attribution_bias_threshold: float

    def validate(self) -> None:
        if type(self.version) is not str or not self.version.strip():
            raise ValueError("versioned metacognitive detector policy required")
        for name in (
            "window", "stagnation_steps", "loop_repetitions",
            "loop_max_period", "entropy_min_samples", "bias_min_outcomes_each",
        ):
            value = getattr(self, name)
            if type(value) is not int or value < 1:
                raise ValueError("detector count/window must be a positive integer")
        if (self.window < max(
                self.stagnation_steps, self.entropy_min_samples,
                self.loop_repetitions * self.loop_max_period,
            ) or self.loop_repetitions < 2):
            raise ValueError("detector windows cannot certify unavailable observations")
        if (not _finite(self.stagnation_tolerance)
                or self.stagnation_tolerance < 0.0):
            raise ValueError("invalid stagnation tolerance")
        if not all(
            _finite(x) and 0 <= x <= 1 for x in (
                self.entropy_warning_fraction, self.attribution_bias_threshold,
            )
        ):
            raise ValueError("normalized detection thresholds must lie in [0,1]")


@dataclass(frozen=True, slots=True)
class LivedCognitiveObservation:
    """Explicit, public S_t-derived facts; unknown progress is NOT zero.

    `context_signature` is a versioned projection of accessible S_t occupancy,
    never hidden WorldBody truth. `attribution_ref` identifies a distinct lived
    verification, NOT an Oracle verdict.
    """

    world_step: int
    cycle: int
    context_signature: str
    active_goal_ref: str | None
    option_ref: str | None
    progress_delta: float | None
    outcome: str = "unknown"
    agency: str = "unknown"
    attribution_ref: str | None = None
    verification_origin: str = "none"

    def validate(self) -> None:
        if (type(self.world_step) is not int or self.world_step < 1
                or type(self.cycle) is not int or self.cycle < 1
                or type(self.context_signature) is not str
                or not self.context_signature.strip()):
            raise ValueError("lived observation requires positive causal time and a visible context")
        if any(value is not None and (type(value) is not str or not value)
               for value in (self.active_goal_ref, self.option_ref, self.attribution_ref)):
            raise ValueError("invalid voluntary choice or attribution identity")
        if self.progress_delta is not None and (
                not _finite(self.progress_delta) or self.progress_delta < 0):
            raise ValueError("progress must be finite, positive or explicitly unknown")
        if self.outcome not in ("success", "failure", "unknown"):
            raise ValueError("only subjectively verified outcome types are accepted")
        if self.agency not in ("self", "world", "unknown"):
            raise ValueError("agency is known, external or explicitly unknown")
        if self.verification_origin not in (
            "none", "lived_physical", "independent_lived_modality",
        ):
            raise ValueError("Oracle/Bench evidence cannot calibrate attribution")
        filled = self.attribution_ref is not None
        if filled != (self.verification_origin != "none"):
            raise ValueError("attribution identity requires genuine verification provenance")
        if filled and (self.outcome == "unknown" or self.agency == "unknown"):
            raise ValueError("a verified attribution needs an observable result and agency")
        if not filled and (
            self.outcome != "unknown" or self.agency != "unknown"
        ):
            raise ValueError("unverified outcomes cannot become attribution evidence")

    def as_dict(self) -> dict[str, object]:
        return {name: getattr(self, name) for name in self.__dataclass_fields__}


@dataclass(frozen=True, slots=True)
class Stage12DetectionReport:
    world_step: int
    cycle: int
    stagnation: bool | None
    reasoning_loop: bool | None
    low_context_entropy: bool | None
    attribution_bias: str | None
    verified_successes: int
    verified_failures: int
    evidence_samples: int


class Stage12LivedDetectors:
    """Bounded sequential diagnosis, not an additional causal state owner.

    Integration must embed exported state in the *existing* Metacognition
    custody rather than adding a second owner named metacognition_health.
    """

    schema = "stage12-lived-detectors-v1"

    def __init__(self, policy: Stage12DetectionPolicy):
        policy.validate()
        self.policy = policy
        self._rows: list[LivedCognitiveObservation] = []
        self._verified_refs: set[str] = set()

    def observe(self, record: LivedCognitiveObservation) -> Stage12DetectionReport:
        if type(record) is not LivedCognitiveObservation:
            raise TypeError("lived cognitive observation required")
        record.validate()
        if self._rows and (
            (record.world_step, record.cycle) <=
            (self._rows[-1].world_step, self._rows[-1].cycle)
        ):
            raise ValueError("out-of-order or duplicate metacognition cycle")
        if (record.attribution_ref is not None
                and record.attribution_ref in self._verified_refs):
            raise ValueError("duplicate lived attribution cannot inflate bias")
        self._rows.append(record)
        self._rows = self._rows[-self.policy.window:]
        if record.attribution_ref is not None:
            self._verified_refs.add(record.attribution_ref)
        return self.detecteurs()

    def detecteurs(self) -> Stage12DetectionReport:
        """All unavailable evidence is reported as None, never a false negative."""
        p = self.policy
        rows = self._rows
        recent = rows[-p.stagnation_steps:]
        stagnation = None
        if len(recent) >= p.stagnation_steps and all(
            row.progress_delta is not None for row in recent
        ):
            stagnation = sum(row.progress_delta for row in recent) <= p.stagnation_tolerance

        loop: bool | None = None
        if len(rows) >= p.loop_repetitions:
            valid = [r for r in rows if r.progress_delta is not None]
            if len(valid) == len(rows):
                loop = False
                for period in range(1, p.loop_max_period + 1):
                    required = period * p.loop_repetitions
                    if len(rows) < required:
                        continue
                    tail = rows[-required:]
                    identities = [
                        (r.context_signature, r.active_goal_ref, r.option_ref)
                        for r in tail
                    ]
                    if (all(r.option_ref is not None for r in tail)
                            and all(r.progress_delta <= p.stagnation_tolerance for r in tail)
                            and all(identities[i] == identities[i % period]
                                    for i in range(len(identities)))):
                        loop = True
                        break

        low_entropy: bool | None = None
        if len(rows) >= p.entropy_min_samples:
            population = len(rows)
            counts: dict[str, int] = {}
            for row in rows:
                counts[row.context_signature] = counts.get(row.context_signature, 0) + 1
            entropy = -sum(
                (n / population) * log(n / population)
                for n in counts.values()
            )
            # Normalized Shannon occupancy entropy: 0 = one repeatedly
            # encountered context; 1 = every observed context distinct.
            maximum = log(population)
            low_entropy = (entropy / maximum if maximum else 0.0) <= p.entropy_warning_fraction

        verified = [row for row in rows if row.attribution_ref is not None]
        successes = [row for row in verified if row.outcome == "success"]
        failures = [row for row in verified if row.outcome == "failure"]
        bias: str | None = None
        if (len(successes) >= p.bias_min_outcomes_each
                and len(failures) >= p.bias_min_outcomes_each):
            self_when_success = sum(r.agency == "self" for r in successes) / len(successes)
            self_when_failure = sum(r.agency == "self" for r in failures) / len(failures)
            difference = self_when_success - self_when_failure
            if difference >= p.attribution_bias_threshold:
                bias = "self_serving_pattern"
            elif difference <= -p.attribution_bias_threshold:
                bias = "self_blame_pattern"
            else:
                bias = "no_detected_pattern"
        step, cycle = ((0, 0) if not rows
                       else (rows[-1].world_step, rows[-1].cycle))
        return Stage12DetectionReport(
            world_step=step, cycle=cycle, stagnation=stagnation,
            reasoning_loop=loop, low_context_entropy=low_entropy,
            attribution_bias=bias,
            verified_successes=len(successes),
            verified_failures=len(failures), evidence_samples=len(rows),
        )

    def export_causal_state(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "policy_version": self.policy.version,
            "observations": [r.as_dict() for r in self._rows],
            "verified_attribution_refs": sorted(self._verified_refs),
        }

    def restore_causal_state(self, raw: object) -> None:
        if (type(raw) is not dict or set(raw) != {
            "schema", "policy_version", "observations",
            "verified_attribution_refs",
        } or raw["schema"] != self.schema
                or raw["policy_version"] != self.policy.version
                or type(raw["observations"]) is not list
                or len(raw["observations"]) > self.policy.window
                or type(raw["verified_attribution_refs"]) is not list):
            raise ValueError("invalid Stage12 diagnostic state")
        restored = Stage12LivedDetectors(self.policy)
        for data in raw["observations"]:
            if type(data) is not dict or set(data) != set(LivedCognitiveObservation.__dataclass_fields__):
                raise ValueError("invalid lived diagnostic projection")
            restored.observe(LivedCognitiveObservation(**data))
        refs = raw["verified_attribution_refs"]
        if (any(type(ref) is not str or not ref for ref in refs)
                or sorted(set(refs)) != refs
                or not all(r.attribution_ref in refs for r in restored._rows
                           if r.attribution_ref is not None)):
            raise ValueError("invalid diagnostic verification ledger")
        # Only a snapshot of the same verified ledger may replace this facet;
        # no already accepted attribution may silently disappear.
        if not self._verified_refs.issubset(set(refs)):
            raise ValueError("cannot forget previously integrated verifications")
        self._rows = list(restored._rows)
        self._verified_refs = set(refs)
