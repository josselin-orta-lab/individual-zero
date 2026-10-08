"""Stage-5 disposable trait-battery administration.

This is bench-side protocol code. It creates an isolated battery copy, attaches
a fresh logged external scenario, runs only that copy to a deterministic stop,
and scores observable behavior. Scores never feed back into cognition.

Spec: 17.7, 19.5, 20.3 Stage 5, INV-34.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .battery_scenarios import (
    BatteryScenarioPlan,
    BatterySituation,
)
from .determinism import deterministic_id
from .injected_scenario import ScenarioEvent
from .stage5_runtime import Stage5Runtime


@dataclass(frozen=True, slots=True)
class BatteryScore:
    situation: BatterySituation
    status: str
    value: float | None
    measure: str
    detail: Mapping[str, object]


@dataclass(frozen=True, slots=True)
class BatteryAdministration:
    copy_id: str
    copy_snapshot_id: str
    situation: BatterySituation
    scenario_version: str
    start_t_monde: int
    stop_t_monde: int
    steps_run: int
    stop_reason: str
    score: BatteryScore


def _rebase_events(
    events: tuple[ScenarioEvent, ...],
    *,
    start_t_monde: int,
) -> tuple[ScenarioEvent, ...]:
    """Treat BatteryScenarioPlan event times as 1-based test-local steps."""
    return tuple(
        ScenarioEvent(
            t_monde=start_t_monde + event.t_monde,
            sequence=event.sequence,
            operation=event.operation,
            payload=dict(event.payload),
        )
        for event in events
    )


def _technical_events(runtime: Stage5Runtime) -> list[Mapping[str, object]]:
    return [entry.causal_event for entry in runtime.journal.entries]


def _positions(events: list[Mapping[str, object]]) -> list[tuple[int, int, int]]:
    result: list[tuple[int, int, int]] = []
    for event in events:
        if event.get("kind") != "world_transition_experienced":
            continue
        raw = event.get("position_after")
        if not isinstance(raw, Mapping):
            continue
        result.append(
            (
                int(event.get("t_monde", 0)),
                int(raw["x"]),
                int(raw["y"]),
            )
        )
    return result


def score_battery_copy(
    runtime: Stage5Runtime,
    *,
    plan: BatteryScenarioPlan,
    start_t_monde: int,
    steps_run: int,
) -> BatteryScore:
    events = _technical_events(runtime)
    positions = _positions(events)

    if plan.situation is BatterySituation.PATIENCE:
        first_berry_use: int | None = None
        for event in events:
            if event.get("kind") != "world_transition_experienced":
                continue
            effects = event.get("effects")
            if not isinstance(effects, Mapping):
                continue
            used = False
            collected = effects.get("collected")
            if isinstance(collected, Mapping):
                used = str(collected.get("kind", "")).startswith("berry")
            ate = effects.get("ate")
            if isinstance(ate, str) and ate.startswith("berry"):
                used = True
            if used:
                first_berry_use = int(event.get("t_monde", 0))
                break

        delayed_at = start_t_monde + int(plan.mechanism["delay_steps"])
        if first_berry_use is None:
            return BatteryScore(
                situation=plan.situation,
                status="no_choice_observed",
                value=None,
                measure="delayed_choice",
                detail={"delayed_available_at": delayed_at},
            )
        return BatteryScore(
            situation=plan.situation,
            status="scored",
            value=1.0 if first_berry_use >= delayed_at else 0.0,
            measure="delayed_choice",
            detail={
                "first_berry_use_t": first_berry_use,
                "delayed_available_at": delayed_at,
            },
        )

    if plan.situation is BatterySituation.RISK_TAKING:
        raw = plan.mechanism["shortcut_zone"]
        if not isinstance(raw, Mapping):
            raise ValueError("risk scenario shortcut zone is malformed")
        shortcut = (int(raw["x"]), int(raw["y"]))
        used = any((x, y) == shortcut for _, x, y in positions)
        return BatteryScore(
            situation=plan.situation,
            status="scored",
            value=1.0 if used else 0.0,
            measure="shortcut_choice",
            detail={"shortcut_zone": dict(raw), "visited": used},
        )

    if plan.situation is BatterySituation.EXPLORATION:
        raw = plan.mechanism["unknown_zone_marker"]
        if not isinstance(raw, Mapping):
            raise ValueError("exploration marker is malformed")
        marker = (int(raw["x"]), int(raw["y"]))
        explored = any((x, y) == marker for _, x, y in positions)
        return BatteryScore(
            situation=plan.situation,
            status="scored",
            value=1.0 if explored else 0.0,
            measure="unknown_zone_entry",
            detail={"unknown_zone_marker": dict(raw), "visited": explored},
        )

    if plan.situation is BatterySituation.THREAT_RESPONSE:
        raw = plan.mechanism["creature_start"]
        if not isinstance(raw, Mapping):
            raise ValueError("threat creature start is malformed")
        cx, cy = int(raw["x"]), int(raw["y"])
        if not positions:
            return BatteryScore(
                situation=plan.situation,
                status="no_movement_observed",
                value=0.0,
                measure="flight_distance",
                detail={"creature_start": dict(raw)},
            )
        distances = [abs(x - cx) + abs(y - cy) for _, x, y in positions]
        return BatteryScore(
            situation=plan.situation,
            status="scored",
            value=float(max(distances)),
            measure="flight_distance",
            detail={
                "creature_start": dict(raw),
                "max_manhattan_distance": max(distances),
            },
        )

    if plan.situation is BatterySituation.PERSEVERANCE:
        # Stage 2 defined the external failure schedule but the current Stage-5
        # world does not yet expose a scenario operation that forces a named
        # tested action to fail. Returning a value would manufacture behavior.
        return BatteryScore(
            situation=plan.situation,
            status="mechanism_not_expressible_stage5",
            value=None,
            measure="attempts_before_abandonment",
            detail={
                "failure_schedule": list(
                    plan.mechanism["action_failure_schedule"]
                ),
                "reason": (
                    "no versioned tested-action failure operation exists in "
                    "the current world/scenario contract"
                ),
            },
        )

    raise AssertionError("unreachable battery situation")


def administer_battery_situation(
    parent: Stage5Runtime,
    *,
    plan: BatteryScenarioPlan,
    administration_ref: str,
) -> BatteryAdministration:
    plan.validate()
    if not administration_ref:
        raise ValueError("administration_ref must not be empty")
    if parent.scheduler.active_attempt is not None:
        raise RuntimeError("battery administration requires a step boundary")

    start_t = parent.scheduler.t_monde
    max_steps = int(plan.termination["max_steps"])
    rebased = _rebase_events(plan.events, start_t_monde=start_t)
    copy_ref = f"battery:{plan.situation.value}:{administration_ref}"

    child, snapshot = parent.create_copy(
        copy_ref=copy_ref,
        battery_copy=True,
        scenario_id=copy_ref,
        scenario_version=plan.version,
        scenario_events=rebased,
    )

    steps_run = 0
    stop_reason = "max_steps"
    for _ in range(max_steps):
        if child.stage3.substrate.safety.blocked:
            stop_reason = "safety_block"
            break
        child.run_step()
        steps_run += 1

    score = score_battery_copy(
        child,
        plan=plan,
        start_t_monde=start_t,
        steps_run=steps_run,
    )

    child.journal.append(
        event_id=deterministic_id(
            "journal-event-v1",
            "stage5.battery",
            child.individual_id,
            plan.situation.value,
            administration_ref,
            "stop",
        ),
        causal_event={
            "emitter": "stage5.battery",
            "kind": "battery_copy_stopped",
            "t_monde": child.scheduler.t_monde,
            "individual": child.individual_id,
            "parent_individual": parent.individual_id,
            "situation": plan.situation.value,
            "scenario_version": plan.version,
            "administration_ref": administration_ref,
            "steps_run": steps_run,
            "stop_reason": stop_reason,
            "score_status": score.status,
            "score_value": score.value,
            "score_measure": score.measure,
        },
    )

    return BatteryAdministration(
        copy_id=child.individual_id,
        copy_snapshot_id=snapshot.id,
        situation=plan.situation,
        scenario_version=plan.version,
        start_t_monde=start_t,
        stop_t_monde=child.scheduler.t_monde,
        steps_run=steps_run,
        stop_reason=stop_reason,
        score=score,
    )
