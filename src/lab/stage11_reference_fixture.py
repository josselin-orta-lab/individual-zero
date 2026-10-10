"""Public I0-vNext P-48 software fixture, not scientific calibration."""
from i0.modules.exploration import ExplorationConfig
from i0.modules.global_modulation import ModulationConfig
from i0.modules.lived_prediction import LivedPredictionConfig
from .stage5_reference_fixture import build_stage5_reference_runtime
from .stage9_reference_fixture import build_stage9_reference_runtime
from .stage11_runtime import Stage11Config, Stage11Runtime


def build_stage11_reference_runtime(*, enable_lived_prediction: bool = False):
    # An opt-in public diagnostic, never a trained Equipment replacement.
    if type(enable_lived_prediction) is not bool:
        raise ValueError("development predictor flag must be boolean")
    baseline = build_stage9_reference_runtime()
    temperament = build_stage5_reference_runtime().temperament_parameters
    return Stage11Runtime(
        world_config=baseline.world.config,
        layout=baseline.world._layout,
        safety_config=baseline.stage3.substrate.safety._config,
        safety_facts=baseline._canonical_safety._innate,
        protected_integrity_threshold=(
            baseline.stage3.control._config.protected_integrity_threshold
        ),
        config=Stage11Config(
            version="i0-vnext-stage11-dev-v1",
            stage9=baseline._stage9_config,
            exploration=ExplorationConfig(
                version="p48-development-v2",
                novelty_weight=0.5, progress_weight=0.3,
                habituation_visits=2, stagnant_visit_limit=2,
            ),
            modulation=ModulationConfig(
                version="p23-p24-development-v1",
                threat_enter=0.7, threat_exit=0.25,
                recovery_enter=0.65, recovery_exit=0.35,
                confirmation_steps=2,
                multipliers={
                    "normal": {"b": 1.0, "n": 1.0, "urg": 1.0,
                               "risk": 1.0, "value": 1.0},
                    "threat": {"b": 1.0, "n": 0.5, "urg": 1.5,
                               "risk": 1.5, "value": 1.0},
                    "exploration": {"b": 1.0, "n": 1.5, "urg": 1.0,
                                    "risk": 1.0, "value": 1.0},
                    "recovery": {"b": 1.0, "n": 0.5, "urg": 1.0,
                                 "risk": 1.0, "value": 1.2},
                },
            ),
            temperament_parameters=temperament,
            intrinsic_weight=0.75,
            exploration_envelope_uc=4,
            exploration_observe_cost_uc=1,
            prospective_water=(
                LivedPredictionConfig(
                    version="p47-prior-lived-observation-dev-v1",
                    min_distinct_episodes=1,
                    maximum_spread=0.5,
                    precision_floor=0.0,
                    max_precision=1.0,
                ) if enable_lived_prediction else None
            ),
        ),
        equipment=baseline.equipment,
    )
