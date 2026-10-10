"""Stage-11 Global Modulation: deterministic cycle-frozen profiles.

Normative EN MVP v1.2.1 §§3.3, 6.4, 16.4, P-23/P-24, INV-06.
Only the previous published S_t can determine a profile. Absence of an
alert is UNKNOWN, not independently verified disappearance of a threat.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Mapping

WEIGHT_TERMS = frozenset({"b", "n", "urg", "risk", "value"})
PROFILES = frozenset({"normal", "threat", "exploration", "recovery"})


@dataclass(frozen=True)
class ModulationConfig:
    version: str
    threat_enter: float
    threat_exit: float
    recovery_enter: float
    recovery_exit: float
    confirmation_steps: int
    multipliers: Mapping[str, Mapping[str, float]]

    def validate(self) -> None:
        if not self.version or type(self.confirmation_steps) is not int or self.confirmation_steps < 1:
            raise ValueError("P-24 version and confirmation in world steps required")
        for entry, exit_ in (
            (self.threat_enter, self.threat_exit),
            (self.recovery_enter, self.recovery_exit),
        ):
            if not (isfinite(entry) and isfinite(exit_) and 0 <= exit_ < entry <= 1):
                raise ValueError("P-24 exit threshold must be below entry")
        if set(self.multipliers) != PROFILES:
            raise ValueError("all four profile multipliers must be versioned")
        for profile, weights in self.multipliers.items():
            if set(weights) != WEIGHT_TERMS:
                raise ValueError("profile must declare all gatekeeper weight terms")
            if any(not isfinite(x) or x <= 0 for x in weights.values()):
                raise ValueError("P-23 weight multipliers must be finite and positive")
            if profile == "normal" and any(x != 1 for x in weights.values()):
                raise ValueError("normal must preserve the reference Gatekeeper")


@dataclass(frozen=True)
class ModulationSignals:
    threat_risk: float | None
    recovery_need: float | None
    needs_satisfied: bool | None
    boredom: bool | None

    def validate(self) -> None:
        for value in (self.threat_risk, self.recovery_need):
            if value is not None and (
                isinstance(value, bool) or not isinstance(value, (float, int))
                or not isfinite(value) or not 0 <= value <= 1
            ):
                raise ValueError("profile indicator must be measured in [0,1] or unknown")
        if any(v is not None and type(v) is not bool
               for v in (self.needs_satisfied, self.boredom)):
            raise ValueError("exploration indicators must be boolean or unknown")


class GlobalModulation:
    owner_id = "global_modulation"

    def __init__(self, config: ModulationConfig) -> None:
        config.validate()
        self.config = config
        self._profile = "normal"
        self._candidate: str | None = None
        self._candidate_steps = 0
        self._candidate_last_step: int | None = None
        self._last_cycle: tuple[int, int] | None = None

    @property
    def profile(self) -> str:
        return self._profile

    def multipliers(self) -> dict[str, float]:
        return dict(self.config.multipliers[self._profile])

    @staticmethod
    def indicators_from_st(st) -> ModulationSignals:
        if st is None:
            return ModulationSignals(None, None, None, None)
        fixed = st.fixed
        signals = fixed.get("modulation_signals", {})
        if not isinstance(signals, Mapping):
            signals = {}
        risk = [
            min(1.0, element.decomposition.get("risk", 0.0)
                * element.reliability)
            for element in st.competitive
            if element.preempted
        ]
        if risk:
            threat = max(risk)
        elif signals.get("threat_clear") is True:
            threat = 0.0
        else:
            threat = None
        body = fixed.get("body", {})
        if (isinstance(body, Mapping)
            and all(key in body for key in ("energy", "integrity"))
            and all(isinstance(body[k], (int, float))
                    and not isinstance(body[k], bool)
                    and isfinite(body[k]) and 0 <= body[k] <= 100
                    for k in ("energy", "integrity"))):
            recovery = max(1 - body["energy"] / 100, 1 - body["integrity"] / 100)
        else:
            recovery = None
        boredom = signals.get("boredom")
        satisfied = signals.get("needs_satisfied")
        return ModulationSignals(
            threat, recovery,
            satisfied if type(satisfied) is bool else None,
            boredom if type(boredom) is bool else None,
        )

    def _target(self, s: ModulationSignals) -> str:
        if s.threat_risk is not None and s.threat_risk >= self.config.threat_enter:
            return "threat"
        if self._profile == "threat" and (
            s.threat_risk is None or s.threat_risk > self.config.threat_exit
        ):
            return "threat"
        if s.recovery_need is not None and s.recovery_need >= self.config.recovery_enter:
            return "recovery"
        if self._profile == "recovery" and (
            s.recovery_need is None or s.recovery_need > self.config.recovery_exit
        ):
            return "recovery"
        if s.needs_satisfied is True and s.boredom is True:
            return "exploration"
        if self._profile == "exploration" and (
            s.needs_satisfied is None or s.boredom is None
        ):
            return "exploration"
        return "normal"

    def freeze(self, *, signals: ModulationSignals, world_step: int, cycle: int) -> str:
        """Fix the profile once per cycle; count confirmations in steps only."""
        signals.validate()
        if type(world_step) is not int or world_step < 1 or type(cycle) is not int or cycle < 1:
            raise ValueError("modulation requires valid world step and cognitive cycle")
        clock = (world_step, cycle)
        if self._last_cycle is not None:
            if clock == self._last_cycle:
                return self._profile
            if clock < self._last_cycle:
                raise ValueError("modulation cycle cannot move backward")
        target = self._target(signals)
        if target == self._profile:
            self._candidate = None
            self._candidate_steps = 0
            self._candidate_last_step = None
        elif target == "threat":
            # A retained urgent threat is a declared immediate priority transition.
            self._profile = target
            self._candidate = None
            self._candidate_steps = 0
            self._candidate_last_step = None
        else:
            if target != self._candidate:
                self._candidate = target
                self._candidate_steps = 0
                self._candidate_last_step = None
            if world_step != self._candidate_last_step:
                self._candidate_steps += 1
                self._candidate_last_step = world_step
            if self._candidate_steps >= self.config.confirmation_steps:
                self._profile = target
                self._candidate = None
                self._candidate_steps = 0
                self._candidate_last_step = None
        self._last_cycle = clock
        return self._profile

    def export_causal_state(self) -> object:
        return {
            "config_version": self.config.version,
            "profile": self._profile,
            "candidate": self._candidate,
            "candidate_steps": self._candidate_steps,
            "candidate_last_step": self._candidate_last_step,
            "last_cycle": self._last_cycle,
        }

    def restore_causal_state(self, state: object) -> None:
        if not isinstance(state, Mapping) or state.get("config_version") != self.config.version:
            raise ValueError("modulation snapshot version mismatch")
        profile, candidate = state.get("profile"), state.get("candidate")
        count = state.get("candidate_steps")
        when = state.get("candidate_last_step")
        clock = state.get("last_cycle")
        if (profile not in PROFILES or candidate not in PROFILES | {None}
            or type(count) is not int or not 0 <= count < self.config.confirmation_steps
            or (candidate is None) != (count == 0)
            or (candidate is None) != (when is None)
            or (when is not None and (type(when) is not int or when < 1))
            or (clock is not None and (
                not isinstance(clock, (list, tuple)) or len(clock) != 2
                or any(type(x) is not int or x < 1 for x in clock)))
            or (clock is not None and when is not None and when > clock[0])):
            raise ValueError("invalid modulation snapshot")
        self._profile = profile
        self._candidate = candidate
        self._candidate_steps = count
        self._candidate_last_step = when
        self._last_cycle = None if clock is None else tuple(clock)
