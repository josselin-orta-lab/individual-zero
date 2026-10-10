"""Stage-10 pure sleep-pressure and waking rules, normative MVP v1.2.1.

Sections 15.1-15.4 and DC-13 (P-39/P-40/P-41). This module owns NO
mutable state and does NOT execute sleep or consolidation. Metacognition
and Health is the sole owner of F_cog and sleep pressure in the eventual
integrated runtime; Action Control remains sole command authority.

All coefficients are injected, explicitly versioned development parameters.
Never count homeostatic energy, D(x), machine time, or compute savings as
intrinsic motivation for the sleep option (INV-14).
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


def _finite_nonnegative(value: object) -> bool:
    return (
        type(value) in (int, float)
        and isfinite(value)
        and value >= 0.0
    )


@dataclass(frozen=True, slots=True)
class SleepPressureConfig:
    version: str
    fatigue_gain: float                     # P-39 a_F
    sleep_fatigue_recovery: float           # P-39 b_F
    waking_recovery_profile_relief: float   # P-39 b_F^rec
    fatigue_weight: float                  # P-40 w_F
    consolidation_weight: float            # P-40 w_C
    night_weight: float                    # P-40 w_N
    unconsolidated_episode_reference: float  # P-40 E_ref
    memory_saturation_reference: float     # P-40 S_ref
    natural_wake_threshold: float          # P-41 p_reveil
    alert_wake_threshold: float            # P-41 s_reveil
    max_consecutive_sleep_steps: int       # P-41 L_sommeil_max

    def validate(self) -> None:
        if not isinstance(self.version, str) or not self.version.strip():
            raise ValueError("versioned P-39/P-40/P-41 policy required")
        for value in (
            self.fatigue_gain, self.sleep_fatigue_recovery,
            self.waking_recovery_profile_relief, self.fatigue_weight,
            self.consolidation_weight, self.night_weight,
        ):
            if not _finite_nonnegative(value):
                raise ValueError("sleep coefficients must be finite and nonnegative")
        if not (
            _finite_nonnegative(self.unconsolidated_episode_reference)
            and self.unconsolidated_episode_reference > 0
            and _finite_nonnegative(self.memory_saturation_reference)
            and self.memory_saturation_reference > 0
        ):
            raise ValueError("reference denominators must be positive")
        if not all(
            type(x) in (int, float) and isfinite(x) and 0.0 < x <= 1.0
            for x in (self.natural_wake_threshold, self.alert_wake_threshold)
        ):
            raise ValueError("P-41 wake thresholds must be in (0,1]")
        if (
            type(self.max_consecutive_sleep_steps) is not int
            or self.max_consecutive_sleep_steps < 1
        ):
            raise ValueError("sleep-duration cap must be >= 1 simulated step")


@dataclass(frozen=True, slots=True)
class SleepPressureAssessment:
    fatigue: float
    consolidation_pressure: float
    sleep_pressure: float
    intrinsic_status: str
    intrinsic_value: float | None


@dataclass(frozen=True, slots=True)
class WakeSignals:
    admitted_reflex: bool
    reduced_perception_alert: float | None   # physically grounded f * rsk
    authorized_dated_intention_due: bool
    consecutive_sleep_steps: int
    consolidation_active: bool

    def validate(self) -> None:
        if any(
            type(v) is not bool
            for v in (
                self.admitted_reflex, self.authorized_dated_intention_due,
                self.consolidation_active,
            )
        ):
            raise ValueError("wake flags must be explicit booleans")
        if (
            type(self.consecutive_sleep_steps) is not int
            or self.consecutive_sleep_steps < 0
        ):
            raise ValueError("sleep duration must be nonnegative world steps")
        if (
            self.reduced_perception_alert is not None
            and (
                type(self.reduced_perception_alert) not in (int, float)
                or not isfinite(self.reduced_perception_alert)
                or not 0 <= self.reduced_perception_alert <= 1
            )
        ):
            raise ValueError("wake-alert evidence must be in [0,1] or unknown")


class SleepPressureRules:
    """Stateless DC-13 equations; not an independent fatigue/goal owner."""

    def __init__(self, config: SleepPressureConfig) -> None:
        config.validate()
        self.config = config

    @staticmethod
    def _bounded_fatigue(f_cog: float) -> float:
        if (
            type(f_cog) not in (float, int)
            or not isfinite(f_cog)
            or not 0.0 <= f_cog <= 1.0
        ):
            raise ValueError("F_cog must be normalized in [0,1]")
        return float(f_cog)

    def waking_cycle_fatigue(
        self, *, f_cog: float, consumed_uc: int,
        c_max: int, b_cycle_uc: int,
    ) -> float:
        """F <- min(1, F + a_F * UC_cycle / (C_max * B_cycle))."""
        current = self._bounded_fatigue(f_cog)
        if (
            type(consumed_uc) is not int or consumed_uc < 0
            or type(c_max) is not int or c_max < 1
            or type(b_cycle_uc) is not int or b_cycle_uc < 0
            or consumed_uc > b_cycle_uc
        ):
            raise ValueError("fatigue requires real bounded logical UC")
        if b_cycle_uc == 0:
            # A fully disabled computation budget cannot accrue synthetic
            # fatigue, and division by zero is not a physical signal.
            return current
        return min(
            1.0,
            current + self.config.fatigue_gain
            * consumed_uc / (c_max * b_cycle_uc),
        )

    def sleep_step_fatigue(self, *, f_cog: float) -> float:
        return max(0.0, self._bounded_fatigue(f_cog)
                   - self.config.sleep_fatigue_recovery)

    def close_waking_step_fatigue(
        self, *, f_cog: float, recovery_profile: bool,
    ) -> float:
        if type(recovery_profile) is not bool:
            raise ValueError("recovery profile is a frozen boolean indicator")
        current = self._bounded_fatigue(f_cog)
        return (
            max(0.0, current - self.config.waking_recovery_profile_relief)
            if recovery_profile else current
        )

    def assess_step(
        self, *, f_cog: float, unconsolidated_episodes: int,
        memory_occupancy: float, is_night: bool, awake: bool,
    ) -> SleepPressureAssessment:
        """Freeze once at world-step opening; caller owns that lifetime.

        m_a(dormir) is ONLY P-39/P-40 fatigue, consolidation pressure and
        night context. It is never a second vote for variables already in D.
        """
        fatigue = self._bounded_fatigue(f_cog)
        if (
            type(unconsolidated_episodes) is not int
            or unconsolidated_episodes < 0
            or type(memory_occupancy) not in (float, int)
            or not isfinite(memory_occupancy)
            or not 0.0 <= memory_occupancy <= 1.0
            or type(is_night) is not bool or type(awake) is not bool
        ):
            raise ValueError("invalid physically meaningful sleep inputs")
        cfg = self.config
        p_cons = min(
            1.0,
            unconsolidated_episodes / cfg.unconsolidated_episode_reference
            + memory_occupancy / cfg.memory_saturation_reference,
        )
        p_sleep = min(
            1.0,
            cfg.fatigue_weight * fatigue
            + cfg.consolidation_weight * p_cons
            + (cfg.night_weight if is_night else 0.0),
        )
        return SleepPressureAssessment(
            fatigue=fatigue, consolidation_pressure=p_cons,
            sleep_pressure=p_sleep,
            intrinsic_status="applicable" if awake else "not_applicable",
            intrinsic_value=p_sleep if awake else None,
        )

    def wake_reason(
        self, *, signals: WakeSignals, frozen_sleep_pressure: float,
    ) -> str | None:
        """DC-13 precedence. Returns a reason, NEVER an executable command.

        A wake reason alone does not interrupt an active consolidation
        transaction or perform a world step. Stage-10 runtime will enforce
        these boundaries when sleep is integrated.
        """
        signals.validate()
        pressure = self._bounded_fatigue(frozen_sleep_pressure)
        if signals.admitted_reflex:
            return "reflex"
        if (
            signals.reduced_perception_alert is not None
            and signals.reduced_perception_alert
            >= self.config.alert_wake_threshold
        ):
            return "alert"
        if signals.authorized_dated_intention_due:
            return "dated_intention"
        if (
            signals.consecutive_sleep_steps
            >= self.config.max_consecutive_sleep_steps
        ):
            return "maximum_duration"
        if (
            pressure <= self.config.natural_wake_threshold
            and not signals.consolidation_active
        ):
            return "natural_end"
        return None
