"""Stage-8 Lab-only online-learning and physical-verification measurements.

Normative v1.2.1: 11.1, 11.4, 20.3 Stage 8; DC-06/DC-15; INV-03/05/07/26.
This module reads physical outcomes and published active states. It never writes
bench metrics, observation labels, or target values into the individual.

Protocol v1: scripted two-command water cycle measures inspectable Q convergence.
Calibration measurements use physical Action Control comparisons actually credited
by Metacognition, with reliability frozen *before* the corresponding world step.
These are software acceptance probes, not Stage-13 campaign calibration.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from math import sqrt
from typing import TYPE_CHECKING

from i0.interfaces import PrimitiveCommand
from i0.modules.td_values import (
    EvaluationState, LinearTDValues, TDLearningConfig, ValueFeatureConfig,
)
from lab.world import BodyState, Position, WorldBody, WorldLayout

if TYPE_CHECKING:
    from lab.stage8_runtime import Stage8Runtime

PROTOCOL_VERSION = "stage8-online-learning-benchmark-v1"


@dataclass(frozen=True, slots=True)
class TDPoint:
    observed_steps: int
    q_drink: float
    q_wait: float
    rmse_against_observed_return: float


@dataclass(frozen=True, slots=True)
class TDWorldLearningCurve:
    protocol_version: str
    world_version: str
    measured_reward_drink: float
    measured_reward_wait: float
    sample_count: int
    points: tuple[TDPoint, ...]


def world_learning_curve(*, pairs: int = 80, interval: int = 20) -> TDWorldLearningCurve:
    """Observe real WorldBody transitions, then update a Value-and-Needs-owned Q.

    One nonlethal individual world, no oracle and no terminal reward. A scripted
    drink/wait sequence repeatedly revisits two observable states. A constant
    reward target is inferred by the *bench* from the first observed pair and
    used only for measuring the resulting Q curve, never passed to the learner.
    """
    if pairs < 2 or interval < 1:
        raise ValueError("preregistered benchmark requires repeated observations")

    from lab.stage8_reference_fixture import build_stage8_reference_runtime

    reference = build_stage8_reference_runtime()
    original = reference.world.config
    costs = dict(original.action_energy_costs)
    costs["boire"] = 0.0
    costs["attendre"] = 0.0
    config = replace(
        original,
        version="stage8-learning-water-cycle-physics-v1",
        initial_position=Position(2, 2),
        initial_body=BodyState(50.0, 60.0, 40.0, 100.0),
        food_decay_per_step=0.0,
        water_decay_per_step=10.0,
        drink_water_gain=20.0,
        action_energy_costs=costs,
    )
    world = WorldBody(
        config=config,
        layout=WorldLayout(water_sources=frozenset({Position(2, 2)})),
    )
    td_reference = reference.q_active.config
    # Fixed, versioned benchmark constants. A scalar intercept isolates the
    # TD update rule from feature generalization and changing world context.
    learner = LinearTDValues(TDLearningConfig(
        version="stage8-learning-curve-td-v1",
        eta=0.1,
        lambda_e=0.0,
        beta=td_reference.beta,
        evidence_scale=td_reference.evidence_scale,
        features=ValueFeatureConfig(
            version="stage8-learning-curve-phi-v1",
            feature_names=("bias",),
            position_scale_x=31.0,
            position_scale_y=31.0,
        ),
    ))
    rewards: list[float] = []
    states: dict[str, EvaluationState] = {}
    points: list[TDPoint] = []

    def append_point(step: int) -> None:
        drink_reward, wait_reward = rewards[:2]
        beta = learner.config.beta
        q_star_drink = (drink_reward + beta * wait_reward) / (1.0 - beta * beta)
        q_star_wait = (wait_reward + beta * drink_reward) / (1.0 - beta * beta)
        q_drink = learner.q(states["drink"], "drink")
        q_wait = learner.q(states["wait"], "wait")
        points.append(TDPoint(
            observed_steps=step,
            q_drink=q_drink,
            q_wait=q_wait,
            rmse_against_observed_return=sqrt((
                (q_drink - q_star_drink) ** 2
                + (q_wait - q_star_wait) ** 2
            ) / 2.0),
        ))

    for step in range(1, pairs * 2 + 1):
        signature = "drink" if step % 2 else "wait"
        command = PrimitiveCommand("boire" if signature == "drink" else "attendre")
        before = world.telemetry()
        # The learner receives accessible telemetry only, not WorldLayout or
        # any benchmark target. Both signatures are genuine decisions.
        state = EvaluationState(
            body=before,
            x=world.position.x,
            y=world.position.y,
            active_goal_type="drink",
            temporal_context="day",
        )
        states[signature] = state
        learner.arrive_decision(state=state, signature=signature, t_monde=step)
        outcome = world.apply(command, t_monde=step)
        if outcome.lethal:
            raise AssertionError("controlled water scenario unexpectedly lethal")
        reward = reference.value_needs.reward_between(
            outcome.body_before.as_dict(),
            outcome.body_after.as_dict(),
        )
        learner.append_experienced_reward(reward)
        rewards.append(reward)
        if step > 2 and reward != rewards[(step - 1) % 2]:
            raise AssertionError("benchmark states are not stationary")
        if step == 2:
            # Birth Q=0 is evaluated retrospectively by the *bench*. The
            # learner cannot read this diagnostic or its Bellman target.
            q_star_drink = (rewards[0] + learner.config.beta * rewards[1]) / (
                1 - learner.config.beta ** 2
            )
            q_star_wait = (rewards[1] + learner.config.beta * rewards[0]) / (
                1 - learner.config.beta ** 2
            )
            points.append(TDPoint(
                observed_steps=0, q_drink=0.0, q_wait=0.0,
                rmse_against_observed_return=sqrt(
                    (q_star_drink ** 2 + q_star_wait ** 2) / 2.0
                ),
            ))
        if step >= 2 and step % interval == 0:
            append_point(step)
    learner.external_stop()  # DC-15: external stop is not a terminal reward.
    return TDWorldLearningCurve(
        protocol_version=PROTOCOL_VERSION,
        world_version=config.version,
        measured_reward_drink=rewards[0],
        measured_reward_wait=rewards[1],
        sample_count=len(rewards),
        points=tuple(points),
    )


@dataclass(frozen=True, slots=True)
class CalibrationSample:
    observation_ref: str
    observed_step: int
    confidence_before_verification: float
    confirmed: bool


@dataclass(frozen=True, slots=True)
class CalibrationCurve:
    protocol_version: str
    samples: tuple[CalibrationSample, ...]
    initial_brier: float | None
    late_brier: float | None
    baseline_brier: float | None


def brier_score(samples: tuple[CalibrationSample, ...]) -> float | None:
    if not samples:
        return None
    return sum((
        sample.confidence_before_verification
        - float(sample.confirmed)
    ) ** 2 for sample in samples) / len(samples)


class Stage8PhysicalCalibrationRecorder:
    """Bench-only prequential calibration from non-oracle physical comparisons.

    The recorder observes but never injects verifications or changes κ. It
    counts only observations actually credited by the active κ state.
    """

    def __init__(self) -> None:
        self._reported: set[str] = set()
        self._pending: dict[str, CalibrationSample] = {}
        self._samples: list[CalibrationSample] = []

    def before_step(self, runtime: Stage8Runtime) -> float:
        return runtime.kappa_active.reliability(
            version=runtime.equipment.version,
            module="simulator",
            contribution_type="prediction",
            family="equipment_predictor",
            confidence=1.0,
        )

    def after_step(self, runtime: Stage8Runtime, probability_before: float) -> None:
        if not 0.0 <= probability_before <= 1.0:
            raise ValueError("invalid pre-verification reliability")
        comparison = runtime.stage3.control.last_comparison
        if comparison is not None:
            for effect in comparison.effects:
                if effect.get("status") not in {"conforming", "nonconforming"}:
                    continue
                if effect.get("observed") is None or effect.get("predicted") is None:
                    continue
                ref = (
                    f"physical-capture:{comparison.observed_t_monde}:"
                    f"{effect.get('variable')}"
                )
                if ref in self._reported or ref in self._pending:
                    continue
                self._pending[ref] = CalibrationSample(
                    observation_ref=ref,
                    observed_step=comparison.observed_t_monde,
                    confidence_before_verification=probability_before,
                    confirmed=effect["status"] == "conforming",
                )
        credited = {
            tuple(row) for row in runtime.kappa_active.export_causal_state()[
                "credited_observations"
            ]
        }
        root_key = (
            runtime.equipment.version, "simulator", "prediction", "equipment_predictor",
        )
        for ref, sample in tuple(sorted(self._pending.items())):
            if (*root_key, ref) not in credited:
                continue
            self._samples.append(sample)
            self._reported.add(ref)
            del self._pending[ref]

    def curve(self) -> CalibrationCurve:
        samples = tuple(sorted(
            self._samples,
            key=lambda s: (s.observed_step, s.observation_ref),
        ))
        if not samples:
            return CalibrationCurve(PROTOCOL_VERSION, (), None, None, None)
        midpoint = len(samples) // 2
        early, late = samples[:midpoint], samples[midpoint:]
        return CalibrationCurve(
            protocol_version=PROTOCOL_VERSION,
            samples=samples,
            initial_brier=brier_score(early),
            late_brier=brier_score(late),
            baseline_brier=sum((0.5 - float(v.confirmed)) ** 2 for v in samples)
            / len(samples),
        )
