"""Bounded, lived-only Stage12 persistent-warning alert ledger.

This is a facet of the existing Metacognition owner, never an independent
cognitive executor. It tracks *consecutive physical world steps* whose
already-charged Stage12 diagnostic signal is explicitly true. Unknown,
refused, skipped and false observations cannot sustain an alert. No Oracle,
Bench, hidden WorldBody cause or technical-journal read is possible here.
"""
from __future__ import annotations

from dataclasses import dataclass

from .stage12_detectors import Stage12DetectionReport


ALERT_SIGNALS = (
    "stagnation", "reasoning_loop", "low_context_entropy", "attribution_bias",
)


@dataclass(frozen=True, slots=True)
class Stage12AlertPolicy:
    version: str
    persistence_world_steps: int

    def validate(self) -> None:
        if (type(self.version) is not str or not self.version.strip()
                or type(self.persistence_world_steps) is not int
                or self.persistence_world_steps < 2):
            raise ValueError("Stage12 alerts require versioned persistence of at least two physical steps")


@dataclass(frozen=True, slots=True)
class Stage12OperatorAlert:
    signal: str
    first_world_step: int
    world_step: int
    consecutive_world_steps: int
    policy_version: str
    evidence_samples: int

    def as_dict(self) -> dict[str, object]:
        return {
            "schema": "stage12-persistent-operator-alert-v1",
            "signal": self.signal,
            "first_world_step": self.first_world_step,
            "world_step": self.world_step,
            "consecutive_world_steps": self.consecutive_world_steps,
            "policy_version": self.policy_version,
            "evidence_samples": self.evidence_samples,
            "operator_only_alert": True,
        }


class Stage12AlertLedger:
    """At most one alert per continuous episode of each lived warning."""

    schema = "stage12-alert-ledger-v1"

    def __init__(self, policy: Stage12AlertPolicy):
        policy.validate()
        self.policy = policy
        self._last_world_step = 0
        self._streaks = {signal: 0 for signal in ALERT_SIGNALS}
        self._first = {signal: None for signal in ALERT_SIGNALS}

    @staticmethod
    def _signals(report: Stage12DetectionReport) -> dict[str, bool | None]:
        if report.attribution_bias not in (
            None, "no_detected_pattern", "self_serving_pattern", "self_blame_pattern",
        ):
            raise ValueError("unsupported lived attribution diagnostic")
        out = {
            "stagnation": report.stagnation,
            "reasoning_loop": report.reasoning_loop,
            "low_context_entropy": report.low_context_entropy,
            "attribution_bias": (
                None if report.attribution_bias is None
                else report.attribution_bias in ("self_serving_pattern", "self_blame_pattern")
            ),
        }
        if any(type(item) not in (bool, type(None)) for item in out.values()):
            raise ValueError("invalid tri-state Stage12 detector")
        return out

    def observe(self, report: Stage12DetectionReport) -> tuple[Stage12OperatorAlert, ...]:
        if type(report) is not Stage12DetectionReport:
            raise TypeError("a lived Stage12 detector report is required")
        t = report.world_step
        if (type(t) is not int or t < 1
                or type(report.cycle) is not int or report.cycle < 1
                or type(report.evidence_samples) is not int
                or report.evidence_samples < 1
                or t <= self._last_world_step):
            raise ValueError("operator alert cannot repeat or rewind an observed physical step")
        signals = self._signals(report)
        gap = self._last_world_step and t != self._last_world_step + 1
        threshold = self.policy.persistence_world_steps
        alerts: list[Stage12OperatorAlert] = []
        for signal in ALERT_SIGNALS:
            if signals[signal] is not True:
                self._streaks[signal] = 0
                self._first[signal] = None
                continue
            if gap or self._streaks[signal] == 0:
                self._streaks[signal] = 1
                self._first[signal] = t
            elif self._streaks[signal] < threshold:
                self._streaks[signal] += 1
            # Saturation keeps exact O(1) state and prevents duplicate alerts
            # while the original episode remains active.
            if self._streaks[signal] == threshold and t == self._first[signal] + threshold - 1:
                alerts.append(Stage12OperatorAlert(
                    signal=signal,
                    first_world_step=self._first[signal],
                    world_step=t,
                    consecutive_world_steps=threshold,
                    policy_version=self.policy.version,
                    evidence_samples=report.evidence_samples,
                ))
        self._last_world_step = t
        return tuple(alerts)

    def export_causal_state(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "policy_version": self.policy.version,
            "persistence_world_steps": self.policy.persistence_world_steps,
            "last_world_step": self._last_world_step,
            "streaks": dict(self._streaks),
            "episode_first_steps": dict(self._first),
        }

    def restore_causal_state(self, state: object) -> None:
        if (type(state) is not dict or set(state) != {
            "schema", "policy_version", "persistence_world_steps",
            "last_world_step", "streaks", "episode_first_steps",
        } or state["schema"] != self.schema
                or state["policy_version"] != self.policy.version
                or state["persistence_world_steps"] != self.policy.persistence_world_steps
                or type(state["last_world_step"]) is not int
                or state["last_world_step"] < 0
                or type(state["streaks"]) is not dict
                or type(state["episode_first_steps"]) is not dict
                or set(state["streaks"]) != set(ALERT_SIGNALS)
                or set(state["episode_first_steps"]) != set(ALERT_SIGNALS)):
            raise ValueError("invalid Stage12 operator alert ledger state")
        last = state["last_world_step"]
        threshold = self.policy.persistence_world_steps
        for signal in ALERT_SIGNALS:
            count = state["streaks"][signal]
            first = state["episode_first_steps"][signal]
            if (type(count) is not int or not 0 <= count <= threshold
                    or (count == 0 and first is not None)
                    or (count > 0 and (
                        type(first) is not int or first < 1 or first > last
                        or (count < threshold and last - first + 1 != count)
                        or (count == threshold and last - first + 1 < threshold)
                    ))):
                raise ValueError("invalid alert episode continuation")
        if self._last_world_step and state != self.export_causal_state():
            raise ValueError("cannot replace a published lived alert ledger")
        self._last_world_step = last
        self._streaks = dict(state["streaks"])
        self._first = dict(state["episode_first_steps"])
