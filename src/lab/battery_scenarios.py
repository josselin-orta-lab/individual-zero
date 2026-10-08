"""Typed battery-scenario protocols for the normative MVP.

Stage 2 defines and versions the environmental mechanisms. Trait scoring and
copy administration belong to Stage 5.

Spec: 19.5, NQ-16, 20.3 Stage 2, P-54.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping

from .injected_scenario import ScenarioEvent
from .world import Position


class BatterySituation(str, Enum):
    PATIENCE = "patience"
    RISK_TAKING = "risk_taking"
    EXPLORATION = "exploration"
    THREAT_RESPONSE = "threat_response"
    PERSEVERANCE = "perseverance"


@dataclass(frozen=True, slots=True)
class BatteryScenarioPlan:
    situation: BatterySituation
    version: str
    events: tuple[ScenarioEvent, ...]
    mechanism: Mapping[str, object]
    termination: Mapping[str, object]

    def validate(self) -> None:
        if not self.version:
            raise ValueError("battery scenario version must not be empty")
        if not self.termination:
            raise ValueError("battery scenario termination must be explicit")
        if len({(e.t_monde, e.sequence) for e in self.events}) != len(self.events):
            raise ValueError("battery scenario event coordinates must be unique")


@dataclass(frozen=True, slots=True)
class BatteryScenarioConfig:
    """Explicit P-54 mechanism parameters with no hidden runtime defaults."""

    version: str
    patience_origin: Position
    patience_berry_kind: str
    risk_shortcut_zone: Position
    threat_creature_position: Position
    exploration_resource_position: Position
    exploration_resource_kind: str
    perseverance_failure_schedule: tuple[bool, ...]
    max_steps_by_situation: Mapping[str, int]

    def validate(self) -> None:
        if not self.version:
            raise ValueError("battery scenario config version must not be empty")
        if self.patience_berry_kind not in {"berry_a", "berry_b"}:
            raise ValueError("patience berry kind must be a berry")
        if self.exploration_resource_kind not in {
            "berry_a",
            "berry_b",
            "wood",
            "stone",
        }:
            raise ValueError("invalid exploration resource kind")
        required = {s.value for s in BatterySituation}
        if set(self.max_steps_by_situation) != required:
            raise ValueError("termination step bound required for every battery situation")
        if any(value < 1 for value in self.max_steps_by_situation.values()):
            raise ValueError("battery termination bounds must be >= 1")
        if not self.perseverance_failure_schedule:
            raise ValueError("perseverance failure schedule must be explicit")


def build_battery_scenario(
    *,
    situation: BatterySituation,
    config: BatteryScenarioConfig,
) -> BatteryScenarioPlan:
    config.validate()
    max_steps = config.max_steps_by_situation[situation.value]

    if situation is BatterySituation.PATIENCE:
        events = (
            ScenarioEvent(
                t_monde=1,
                sequence=0,
                operation="place_resource",
                payload={
                    "position": config.patience_origin.as_dict(),
                    "kind": config.patience_berry_kind,
                    "quantity": 1,
                },
            ),
            ScenarioEvent(
                t_monde=21,
                sequence=0,
                operation="place_resource",
                payload={
                    "position": config.patience_origin.as_dict(),
                    "kind": config.patience_berry_kind,
                    "quantity": 3,
                },
            ),
        )
        mechanism = {
            "immediate_quantity": 1,
            "delayed_quantity": 3,
            "delay_steps": 20,
            "condition": "delayed_offer_available_only_if_scenario_conditions_respected",
        }

    elif situation is BatterySituation.RISK_TAKING:
        events = (
            ScenarioEvent(
                t_monde=1,
                sequence=0,
                operation="set_danger_zone",
                payload={
                    "position": config.risk_shortcut_zone.as_dict(),
                    "active": True,
                },
            ),
        )
        mechanism = {
            "choice": "shortcut_or_safe_detour",
            "shortcut_zone": config.risk_shortcut_zone.as_dict(),
            "danger_semantics": "scenario_defined",
        }

    elif situation is BatterySituation.EXPLORATION:
        events = (
            ScenarioEvent(
                t_monde=1,
                sequence=0,
                operation="place_resource",
                payload={
                    "position": config.exploration_resource_position.as_dict(),
                    "kind": config.exploration_resource_kind,
                    "quantity": 1,
                },
            ),
        )
        mechanism = {
            "choice": "known_resource_or_unknown_zone",
            "unknown_zone_marker": config.exploration_resource_position.as_dict(),
        }

    elif situation is BatterySituation.THREAT_RESPONSE:
        events = (
            ScenarioEvent(
                t_monde=1,
                sequence=0,
                operation="place_creature",
                payload={"position": config.threat_creature_position.as_dict()},
            ),
        )
        mechanism = {
            "measure": "flight_distance",
            "creature_start": config.threat_creature_position.as_dict(),
        }

    elif situation is BatterySituation.PERSEVERANCE:
        events = ()
        mechanism = {
            "action_failure_schedule": list(config.perseverance_failure_schedule),
            "schedule_semantics": (
                "true means the scenario forces the tested action to fail; "
                "the schedule is external and replayable"
            ),
        }

    else:
        raise AssertionError("unreachable battery situation")

    plan = BatteryScenarioPlan(
        situation=situation,
        version=config.version,
        events=events,
        mechanism=mechanism,
        termination={"max_steps": max_steps},
    )
    plan.validate()
    return plan
