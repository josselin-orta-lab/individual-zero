"""Controlled Stage-8 calibration stress test, strictly external to cognition.

Physical world and ActionControl compare a predeclared imperfect predictor against
later observations. Metacognition owns the κ updates; Lab owns only statistics.
The regime is preregistered and is NOT evidence of campaign-wide calibration.
"""
from __future__ import annotations

from dataclasses import dataclass, replace

from i0.contracts import PredictedConsequence
from i0.interfaces import PrimitiveCommand
from i0.modules.action_control import ActionControl, ActionControlConfig, PreparedCommand
from i0.modules.active_kappa import ActiveKappa, KappaConfig, physical_verifications_from_comparison
from i0.modules.perception import SymbolicPerception
from lab.world import Position, WorldBody, WorldLayout

from .stage8_learning_benchmark import (
    CalibrationCurve, CalibrationSample, PROTOCOL_VERSION, brier_score
)
from .stage8_reference_fixture import build_stage8_reference_runtime


@dataclass(frozen=True, slots=True)
class StressCalibrationResult:
    version: str
    samples: tuple[CalibrationSample, ...]
    early_brier: float
    late_brier: float
    baseline_brier: float
    confirmations: int
    contradictions: int
    credited_observations: int


def controlled_physical_calibration(*, trials: int = 80) -> StressCalibrationResult:
    if trials != 80:
        raise ValueError("calibration protocol fixes exactly 80 predeclared trials")
    reference = build_stage8_reference_runtime()
    version = "stage8-controlled-predictor-v1"
    physics = replace(
        reference.world.config,
        version="stage8-physical-calibration-physics-v1",
        initial_position=Position(2, 2),
        food_decay_per_step=0.0,
        water_decay_per_step=0.0,
        action_energy_costs={key: 0.0 for key in reference.world.config.action_energy_costs},
    )
    # Four out of every five moves succeed, one is blocked. The blocking
    # coordinates are fixed before trial 1 and never depend on κ or the score.
    blocked = frozenset(Position(x, 3) for x in (6, 11, 16, 21))
    world = WorldBody(config=physics, layout=WorldLayout(obstacles=blocked))
    perception = SymbolicPerception()
    control = ActionControl(
        config=ActionControlConfig(
            safety_policy_version="mvp-v1.2.1",
            protected_integrity_threshold=reference.stage3.control._config.protected_integrity_threshold,
        ),
        safety_facts=reference.stage3.control._facts,
        protocol_mask=lambda command: False,
    )
    kappa = ActiveKappa(KappaConfig(
        version="stage8-controlled-calibration-prior-v1",
        classes=5, prior_strength=2.0, equipment_priors={},
    ))
    samples = []
    confirmations = 0
    contradictions = 0
    # Each trial generates a unique world-step physical measurement.
    for step in range(1, trials + 1):
        pos = world.position
        command = PrimitiveCommand("se_deplacer", {"direction": "east" if step % 2 else "west"})
        # Imperfect preregistered predictor: unchanged position; on each
        # paired movement one leg deliberately predicts the wrong coordinate.
        actual_target = pos.moved(str(command.parameters["direction"]))
        predicted_x = (
            actual_target.x if step % 5 != 0 else pos.x
        )
        pre = kappa.reliability(
            version=version, module="simulator",
            contribution_type="prediction", family="equipment_predictor",
            confidence=1.0,
        )
        prepared = PreparedCommand(
            command=command, source="decision", option_ref=f"trial:{step}",
            predicted_consequences=(
                PredictedConsequence(
                    variable="position_x", value_or_delta=float(predicted_x), precision=0.0
                ),
            ),
            observation_window_steps=1,
        )
        control.record_sent_prediction(prepared=prepared, t_monde=step)
        transition = world.apply(command, t_monde=step)
        if transition.lethal:
            raise AssertionError("controlled physical calibration unexpectedly lethal")
        local = world.capture_local(t_monde=step + 1)
        capture = perception.capture(
            local_state=local.as_dict(), telemetry=world.telemetry()
        )
        comparison = control.compare_capture(capture)
        if comparison is None:
            raise AssertionError("physical consequence was not compared")
        verifications = physical_verifications_from_comparison(
            comparison=comparison, equipment_version=version
        )
        if len(verifications) != 1:
            raise AssertionError("expected one independently observed physical effect")
        for verification in verifications:
            kappa.integrate(verification)
        credited = kappa.publish()
        if len(credited) != 1:
            raise AssertionError("independent physical consequence was not credited")
        confirmed = verifications[0].outcome == "confirmee"
        confirmations += int(confirmed)
        contradictions += int(not confirmed)
        samples.append(CalibrationSample(
            observation_ref=verifications[0].observation_ref,
            observed_step=step + 1,
            confidence_before_verification=pre,
            confirmed=confirmed,
        ))
    half = len(samples) // 2
    return StressCalibrationResult(
        version=PROTOCOL_VERSION + "-physical-stress-v1",
        samples=tuple(samples),
        early_brier=brier_score(tuple(samples[:half])),
        late_brier=brier_score(tuple(samples[half:])),
        baseline_brier=0.25,
        confirmations=confirmations,
        contradictions=contradictions,
        credited_observations=len(kappa.export_causal_state()["credited_observations"]),
    )
