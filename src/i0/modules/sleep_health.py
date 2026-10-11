"""Stage-10 sleeping-readiness state owned by Metacognition and Health.

Software-only integration slice for normative MVP v1.2.1 section 15,
DC-13 P-39/P-40. No independent causal owner, sleep execution, learning
reward, Energy/D double counting or consolidation is introduced here.
"""
from __future__ import annotations

from dataclasses import asdict
from math import isfinite
from typing import Mapping

from .sleep_pressure import (
    SleepPressureAssessment, SleepPressureConfig, SleepPressureRules,
)


class SleepHealth:
    """Optional, snapshot-owned extension of the existing metacognition owner.

    Only actual logical UC from completed waking cognitive cycles changes
    F_cog. Sleep pressure is frozen once per simulated world step from
    earlier state and existing Memory, never recomputed mid-deliberation.
    """

    snapshot_schema = "stage10-sleep-health-dev-v1"

    def __init__(self, config: SleepPressureConfig) -> None:
        self.rules = SleepPressureRules(config)
        self._fatigue = 0.0
        self._step: int | None = None
        self._frozen: SleepPressureAssessment | None = None
        self._last_cycle: tuple[int, int] | None = None
        self._last_recovered_step: int | None = None

    @property
    def fatigue(self) -> float:
        return self._fatigue

    @property
    def frozen(self) -> SleepPressureAssessment | None:
        return self._frozen

    @property
    def frozen_world_step(self) -> int | None:
        return self._step

    def begin_waking_step(
        self, *, world_step: int, unconsolidated_episodes: int,
        memory_occupancy: float, is_night: bool,
    ) -> SleepPressureAssessment:
        if type(world_step) is not int or world_step < 1:
            raise ValueError("world-step clock required")
        if self._step is not None and world_step < self._step:
            raise ValueError("cannot rewind sleep-pressure world step")
        if world_step == self._step:
            assert self._frozen is not None
            return self._frozen
        # Validate all inputs, then atomically publish the new frozen value.
        assessment = self.rules.assess_step(
            f_cog=self._fatigue,
            unconsolidated_episodes=unconsolidated_episodes,
            memory_occupancy=memory_occupancy,
            is_night=is_night,
            awake=True,
        )
        self._step = world_step
        self._frozen = assessment
        return assessment

    def close_waking_cycle(
        self, *, world_step: int, cycle: int, consumed_uc: int,
        cycle_ceiling: int, c_max: int,
    ) -> float:
        if (
            type(world_step) is not int or world_step != self._step
            or type(cycle) is not int or cycle < 1 or cycle > c_max
            or type(c_max) is not int or c_max < 1
        ):
            raise ValueError("fatigue update requires current waking cycle")
        clock = (world_step, cycle)
        if self._last_cycle is not None and clock <= self._last_cycle:
            raise ValueError("fatigue cycle may not be counted twice")
        updated = self.rules.waking_cycle_fatigue(
            f_cog=self._fatigue,
            consumed_uc=consumed_uc,
            c_max=c_max,
            b_cycle_uc=cycle_ceiling,
        )
        self._fatigue = updated
        self._last_cycle = clock
        return updated

    def recover_sleep_step(self, *, world_step: int) -> float:
        """One recovery for an actually completed physical sleeping step.

        Call only after the admitted command advances WorldBody. No budget
        credit and no energy/body reward is manufactured here.
        """
        if (type(world_step) is not int or world_step < 1
                or self._step is None or world_step <= self._step
                or (self._last_recovered_step is not None
                    and world_step <= self._last_recovered_step)):
            raise ValueError("sleep recovery requires a fresh physical world step")
        self._fatigue = self.rules.sleep_step_fatigue(f_cog=self._fatigue)
        self._last_recovered_step = world_step
        return self._fatigue

    def export_causal_state(self) -> dict[str, object]:
        return {
            "state_schema": self.snapshot_schema,
            "config_version": self.rules.config.version,
            "fatigue": self._fatigue,
            "frozen_world_step": self._step,
            "frozen": None if self._frozen is None else asdict(self._frozen),
            "last_cycle": self._last_cycle,
            "last_recovered_step": self._last_recovered_step,
        }

    def restore_causal_state(self, state: object) -> None:
        if (
            not isinstance(state, Mapping)
            or set(state) != {
                "state_schema", "config_version", "fatigue",
                "frozen_world_step", "frozen", "last_cycle",
                "last_recovered_step",
            }
            or state.get("state_schema") != self.snapshot_schema
            or state.get("config_version") != self.rules.config.version
        ):
            raise ValueError("stage10 health snapshot incompatible")
        fatigue = state.get("fatigue")
        if (
            type(fatigue) not in (int, float)
            or not isfinite(fatigue) or not 0 <= fatigue <= 1
        ):
            raise ValueError("invalid restored cognitive fatigue")
        recovered = state.get("last_recovered_step")
        if (recovered is not None and (
                type(recovered) is not int or recovered < 1
                or (state.get("frozen_world_step") is not None
                    and recovered <= state["frozen_world_step"]))):
            raise ValueError("invalid sleep-recovery chronology")
        step, raw, clock = (
            state.get("frozen_world_step"),
            state.get("frozen"),
            state.get("last_cycle"),
        )
        if (step is None) != (raw is None):
            raise ValueError("incoherent frozen step and pressure")
        if step is not None and (type(step) is not int or step < 1):
            raise ValueError("invalid frozen world-step clock")
        frozen = None
        if raw is not None:
            if (
                not isinstance(raw, Mapping)
                or set(raw) != {
                    "fatigue", "consolidation_pressure",
                    "sleep_pressure", "intrinsic_status", "intrinsic_value",
                }
            ):
                raise ValueError("invalid frozen pressure snapshot")
            for k in ("fatigue", "consolidation_pressure", "sleep_pressure",
                      "intrinsic_value"):
                v = raw[k]
                if (
                    type(v) not in (int, float) or not isfinite(v)
                    or not 0 <= v <= 1
                ):
                    raise ValueError("nonphysical frozen pressure")
            if raw["intrinsic_status"] != "applicable" or (
                raw["intrinsic_value"] != raw["sleep_pressure"]
                or (raw["fatigue"] > fatigue and recovered is None)
            ):
                raise ValueError("incoherent waking intrinsic sleep pressure")
            frozen = SleepPressureAssessment(**raw)
        if clock is not None:
            if (
                step is None
                or not isinstance(clock, (tuple, list))
                or len(clock) != 2
                or type(clock[0]) is not int or type(clock[1]) is not int
                or not 1 <= clock[0] <= step or clock[1] < 1
            ):
                raise ValueError("invalid waking-cycle chronology")
            clock = tuple(clock)
        # No partial mutation on a malformed snapshot.
        self._fatigue = float(fatigue)
        self._step = step
        self._frozen = frozen
        self._last_cycle = clock
        self._last_recovered_step = recovered
