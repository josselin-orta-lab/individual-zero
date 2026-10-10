"""I0-vNext incremental Stage-11 Exploration runtime.

The historical Stage-9 implementation, results and scientific NO-GO are
untouched. The scheduler, Competition and Action Control retain authority.
"""
from dataclasses import dataclass, replace
from math import isfinite

from i0.modules.exploration import Exploration, ExplorationConfig
from i0.modules.global_modulation import GlobalModulation, ModulationConfig
from i0.modules.stage11_evaluator import Stage11OptionEvaluator
from i0.temperament import ParametresTemperament

from .stage9_runtime import Stage9Config, Stage9Runtime


@dataclass(frozen=True)
class Stage11Config:
    version: str
    stage9: Stage9Config
    exploration: ExplorationConfig
    modulation: ModulationConfig
    temperament_parameters: ParametresTemperament
    intrinsic_weight: float
    exploration_envelope_uc: int
    exploration_observe_cost_uc: int

    def validate(self):
        if not self.version:
            raise ValueError("Stage-11 runtime version required")
        self.stage9.validate()
        self.exploration.validate()
        self.modulation.validate()
        self.temperament_parameters.validate()
        if not isfinite(self.intrinsic_weight) or self.intrinsic_weight < 0:
            raise ValueError("invalid P-15")
        if (type(self.exploration_envelope_uc) is not int
            or type(self.exploration_observe_cost_uc) is not int
            or self.exploration_envelope_uc < 0
            or self.exploration_observe_cost_uc < 0):
            raise ValueError("invalid P-43 Exploration envelope/cost")

    def with_budget(self):
        stage8 = self.stage9.stage8
        stage7 = stage8.stage7
        stage6 = stage7.stage6
        stage4 = stage6.stage4
        budget = stage4.compute_budget
        amended = replace(
            budget, version=budget.version + "+" + self.version,
            module_envelopes={
                **budget.module_envelopes,
                "exploration": self.exploration_envelope_uc,
            },
            operation_costs={
                **budget.operation_costs,
                "exploration_observe": self.exploration_observe_cost_uc,
            },
        )
        return replace(self.stage9, stage8=replace(
            stage8, stage7=replace(
                stage7, stage6=replace(
                    stage6, stage4=replace(stage4, compute_budget=amended),
                ),
            ),
        ))


class Stage11Runtime(Stage9Runtime):
    individual_id = "i0-vnext-stage11"

    def __init__(self, *, world_config, layout, safety_config, safety_facts,
                 protected_integrity_threshold, config: Stage11Config, equipment,
                 scenario_id=None, scenario_version=None, scenario_events=()):
        config.validate()
        self._stage11_config = config
        super().__init__(
            world_config=world_config, layout=layout,
            safety_config=safety_config, safety_facts=safety_facts,
            protected_integrity_threshold=protected_integrity_threshold,
            config=config.with_budget(), equipment=equipment,
            scenario_id=scenario_id, scenario_version=scenario_version,
            scenario_events=scenario_events,
        )
        self.exploration = Exploration(
            config.exploration,
            coefficient=config.temperament_parameters.exploration_coefficient,
        )
        self.modulation = GlobalModulation(config.modulation)
        self._stage11_modulation_signals = {
            "boredom": False, "needs_satisfied": False,
        }
        self.stage8_option_evaluator = Stage11OptionEvaluator(
            config=config.stage9.stage8.evaluation,
            stage6=self.option_evaluator, q_values=self.q_active,
            exploration=self.exploration, intrinsic_weight=config.intrinsic_weight,
        )

    @property
    def causal_owners(self):
        return (*super().causal_owners, self.exploration, self.modulation)

    def _gatekeeper_profile_multipliers(self):
        # P-23: per-cycle coefficients; Gatekeeper retains sole scoring state.
        return self.modulation.multipliers()

    def _profile_state(self):
        return {
            "name": self.modulation.profile,
            "version": self._stage11_config.modulation.version,
        }

    def _st_additional_fixed(self):
        # Captured before phase 1. The next cycle reads it via frozen S_t.
        return {"modulation_signals": dict(self._stage11_modulation_signals)}

    def _phase_hooks(self, *, cycle, capture, goal_for_planning, st_before_cycle):
        # Frozen input precedes all producers of phase 1 (INV-08).
        frozen = self.causal_model.export_causal_state()
        # These phase-2 S_t fields are captured BEFORE phase-1 producers run.
        # The current step's physical needs and previous Exploration state
        # cannot influence the profile until S_t publishes for a NEXT cycle.
        need_state = self._step_need_state
        self._stage11_modulation_signals = {
            "boredom": self.exploration.boredom_detected(),
            "needs_satisfied": (
                False if need_state is None
                else all(float(v) == 0.0 for v in need_state.deficits.values())
            ),
        }
        hooks = super()._phase_hooks(
            cycle=cycle, capture=capture, goal_for_planning=goal_for_planning,
            st_before_cycle=st_before_cycle,
        )

        previous_modulation_hook = hooks[0]["global_modulation"]

        def modulation_hook(ctx):
            previous_modulation_hook(ctx)
            old = self.modulation.profile
            indicators = self.modulation.indicators_from_st(st_before_cycle)
            new = self.modulation.freeze(
                signals=indicators, world_step=capture.t_monde, cycle=cycle,
            )
            if old != new:
                self._write(
                    kind="stage11_modulation_transition", cycle=cycle,
                    data={
                        "before": old, "after": new,
                        "profile_version": self._stage11_config.modulation.version,
                        "source_st_version": (
                            None if st_before_cycle is None
                            else st_before_cycle.version
                        ),
                    },
                )
        hooks[0]["global_modulation"] = modulation_hook

        def exploration_hook(_context):
            if not self._charge(module="exploration", operation="exploration_observe"):
                return
            previous = self.exploration.export_causal_state()
            self.exploration.observe_causal_state(frozen)
            current = self.exploration.export_causal_state()
            if current != previous:
                self._write(
                    kind="stage11_exploration_updated", cycle=cycle,
                    data={
                        "version": self._stage11_config.exploration.version,
                        "question_refs": [ref for ref, _ in current["questions"]],
                        "verified_visits": sum(
                            q["visits"] for _, q in current["questions"]
                        ),
                    },
                )

        hooks[1]["exploration"] = exploration_hook
        return hooks

    def _evaluate_competition_cycle(self, *, capture, cycle):
        result = super()._evaluate_competition_cycle(capture=capture, cycle=cycle)
        for assessment in result.evaluations:
            if assessment.intrinsic_status == "applicable":
                self._write(
                    kind="stage11_intrinsic_evaluation", cycle=cycle,
                    data={
                        "option_ref": assessment.option_ref,
                        "status": assessment.status,
                        "intrinsic_value": assessment.intrinsic_value,
                        "signal_ids": list(assessment.signal_ids),
                        "intrinsic_producers": list(assessment.producers),
                        "P15_intrinsic_weight": self._stage11_config.intrinsic_weight,
                    },
                )
        return result
