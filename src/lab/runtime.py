"""Neutral execution loop for an Individual."""

from __future__ import annotations

from dataclasses import dataclass

from i0.interfaces import Individual

from .events import LabEvent
from .scenarios import SmokeScenario
from .sinks import EventSink


@dataclass(frozen=True, slots=True)
class RunConfig:
    """Configuration for one deterministic Lab run."""

    run_id: str = "bootstrap-run"
    seed: int = 0
    cycles: int = 3

    def validate(self) -> None:
        if not self.run_id.strip():
            raise ValueError("run_id must not be empty")
        if self.cycles < 0:
            raise ValueError("cycles must be non-negative")


@dataclass(frozen=True, slots=True)
class RunSummary:
    """Compact summary returned by the Lab after a run."""

    run_id: str
    seed: int
    cycles_requested: int
    cycles_completed: int
    action_kinds: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "run_id": self.run_id,
            "seed": self.seed,
            "cycles_requested": self.cycles_requested,
            "cycles_completed": self.cycles_completed,
            "action_kinds": list(self.action_kinds),
        }


def run_individual(
    *,
    individual: Individual,
    scenario: SmokeScenario,
    config: RunConfig,
    sink: EventSink,
) -> RunSummary:
    """Run an Individual under a deterministic technical smoke scenario."""

    config.validate()
    individual.reset(seed=config.seed)

    sink.emit(
        LabEvent(
            run_id=config.run_id,
            kind="run_started",
            data={
                "seed": config.seed,
                "cycles_requested": config.cycles,
                "scenario": scenario.label,
            },
        )
    )

    action_kinds: list[str] = []

    for cycle in range(config.cycles):
        observation = scenario.observation(cycle)
        sink.emit(
            LabEvent(
                run_id=config.run_id,
                kind="observation",
                cycle=cycle,
                data={
                    "observation_kind": observation.kind,
                    "observation_data": dict(observation.data),
                },
            )
        )

        result = individual.step(observation)
        action_kinds.append(result.action.kind)

        sink.emit(
            LabEvent(
                run_id=config.run_id,
                kind="step_completed",
                cycle=cycle,
                data={
                    "action_kind": result.action.kind,
                    "action_data": dict(result.action.data),
                    "state": dict(result.state),
                },
            )
        )

    summary = RunSummary(
        run_id=config.run_id,
        seed=config.seed,
        cycles_requested=config.cycles,
        cycles_completed=config.cycles,
        action_kinds=tuple(action_kinds),
    )

    sink.emit(
        LabEvent(
            run_id=config.run_id,
            kind="run_completed",
            data=summary.as_dict(),
        )
    )

    return summary
