"""Isolated Stage-10 *waking-health* integration, not full sleep or consolidation.

Based on the complete Stage-9 software runtime, so Stage-10 may be tested
independently of Stage-11 Exploration. Only the already existing canonical
Metacognition and Health owner holds mutable F_cog and frozen sleep pressure.

Normative English MVP v1.2.1 sections 15.1, 16, DC-13, INV-01/08/14.
This runtime is development-only and does not run held-out campaigns.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from i0.modules.sleep_pressure import SleepPressureConfig
from .stage9_runtime import Stage9Config, Stage9Runtime


@dataclass(frozen=True, slots=True)
class Stage10HealthConfig:
    version: str
    stage9: Stage9Config
    sleep: SleepPressureConfig
    memory_reference_capacity: int

    def validate(self) -> None:
        if not isinstance(self.version, str) or not self.version.strip():
            raise ValueError("Stage-10 software configuration version required")
        self.stage9.validate()
        self.sleep.validate()
        if (
            type(self.memory_reference_capacity) is not int
            or self.memory_reference_capacity < 1
        ):
            raise ValueError("memory occupancy reference must be positive")


class Stage10HealthRuntime(Stage9Runtime):
    """Waking pressure producer; intentionally has no sleeping mode."""

    individual_id = "i0-vnext-stage10-health"

    def __init__(
        self, *, world_config, layout, safety_config, safety_facts,
        protected_integrity_threshold, config: Stage10HealthConfig,
        equipment, scenario_id=None, scenario_version=None, scenario_events=(),
    ):
        config.validate()
        self._stage10_health_config = config
        super().__init__(
            world_config=world_config,
            layout=layout,
            safety_config=safety_config,
            safety_facts=safety_facts,
            protected_integrity_threshold=protected_integrity_threshold,
            config=config.stage9,
            equipment=equipment,
            scenario_id=scenario_id,
            scenario_version=scenario_version,
            scenario_events=scenario_events,
        )
        self.metacognition.attach_sleep_health(config.sleep)

    @property
    def sleep_health(self):
        return self.metacognition.sleep_health

    def _st_additional_fixed(self) -> Mapping[str, object]:
        """Read-only snapshot of frozen pressure, not a sleep command."""
        health = self.sleep_health
        assessment = health.frozen
        if assessment is None:
            return {}
        return {
            "sleep_readiness": {
                "version": self._stage10_health_config.sleep.version,
                "world_step": health.frozen_world_step,
                "fatigue_before_step": assessment.fatigue,
                "consolidation_pressure": assessment.consolidation_pressure,
                "sleep_pressure": assessment.sleep_pressure,
                "intrinsic_status": assessment.intrinsic_status,
                "intrinsic_value": assessment.intrinsic_value,
                "enabled_for_action": False,
            }
        }

    def _phase_hooks(
        self, *, cycle, capture, goal_for_planning, st_before_cycle,
    ):
        hooks = super()._phase_hooks(
            cycle=cycle,
            capture=capture,
            goal_for_planning=goal_for_planning,
            st_before_cycle=st_before_cycle,
        )
        earlier_freeze = hooks[0]["global_modulation"]
        earlier_close = hooks[5]["metacognition_health"]
        health = self.sleep_health

        def freeze_sleep_pressure(ctx):
            if health.frozen_world_step != capture.t_monde:
                # No consolidation exists at this stage: every closed
                # Memory episode is currently unconsolidated. The reference
                # capacity is a declared development parameter (not a
                # fabricated physical maximum of EpisodicMemory).
                episodes = len(self.memory.episodes)
                occupancy = min(
                    1.0,
                    episodes / self._stage10_health_config.memory_reference_capacity,
                )
                frozen = health.begin_waking_step(
                    world_step=capture.t_monde,
                    unconsolidated_episodes=episodes,
                    memory_occupancy=occupancy,
                    is_night=self.world.is_night(capture.t_monde),
                )
                self._write(
                    kind="stage10_sleep_pressure_frozen", cycle=cycle,
                    data={
                        "version": self._stage10_health_config.sleep.version,
                        "world_step": capture.t_monde,
                        "source": "metacognition_health",
                        "unconsolidated_episodes": episodes,
                        "memory_occupancy": occupancy,
                        "night": self.world.is_night(capture.t_monde),
                        "f_cog_before": frozen.fatigue,
                        "p_cons": frozen.consolidation_pressure,
                        "p_sleep": frozen.sleep_pressure,
                        "sleep_action_enabled": False,
                    },
                )
            earlier_freeze(ctx)

        def close_waking_fatigue(ctx):
            # Stage-4 budget accounting and Stage-8 kappa publication
            # remain in their exact original order.
            earlier_close(ctx)
            before = health.fatigue
            after = health.close_waking_cycle(
                world_step=capture.t_monde,
                cycle=cycle,
                consumed_uc=self.compute_budget.consumed_cycle_uc,
                cycle_ceiling=self._config.compute_budget.cycle_ceiling,
                c_max=self._config.competition.c_max,
            )
            self._write(
                kind="stage10_fatigue_cycle_closed", cycle=cycle,
                data={
                    "version": self._stage10_health_config.sleep.version,
                    "source": "metacognition_health",
                    "f_cog_before": before,
                    "f_cog_after": after,
                    "logical_uc": self.compute_budget.consumed_cycle_uc,
                    "c_max": self._config.competition.c_max,
                    "cycle_budget_uc": self._config.compute_budget.cycle_ceiling,
                    "simulated_world_step": capture.t_monde,
                },
            )

        hooks[0]["global_modulation"] = freeze_sleep_pressure
        hooks[5]["metacognition_health"] = close_waking_fatigue
        return hooks
