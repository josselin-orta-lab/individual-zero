"""Minimal Stage-4 Goal Manager.

It is the sole owner/writer of the active goal. Stage 4 implements need-driven
activation, satisfaction and hysteretic replacement. The full abandonment
machinery remains represented but becomes operational when Planning reports
full-budget failures.

Spec: 7.4, DC-03, NQ-01, 20.3 Stage 4.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from i0.contracts import Goal, GoalProposal


@dataclass(frozen=True, slots=True)
class GoalManagerConfig:
    version: str
    p_min: float
    replacement_hysteresis: float
    critical_pressure: float
    impossible_failures_required: int
    refractory_steps: int

    def validate(self) -> None:
        if not self.version:
            raise ValueError("Goal Manager config version must not be empty")
        if not 0.0 < self.p_min < 1.0:
            raise ValueError("p_min must lie in ]0,1[")
        if self.replacement_hysteresis < 0:
            raise ValueError("goal hysteresis must be non-negative")
        if not 0.0 < self.critical_pressure <= 1.0:
            raise ValueError("critical pressure must lie in ]0,1]")
        if self.impossible_failures_required < 1:
            raise ValueError("N_imp must be >= 1")
        if self.refractory_steps < 1:
            raise ValueError("T_refr must be >= 1")


class GoalManager:
    owner_id = "goal_manager"

    def __init__(self, config: GoalManagerConfig) -> None:
        config.validate()
        self._config = config
        self._active: Goal | None = None
        self._latest_pressure: dict[tuple[str, str], float] = {}
        self._refractory_until: dict[tuple[str, str], int] = {}
        self._impossible_failures: dict[tuple[str, str], tuple[str, int]] = {}
        self._visible_proposals: tuple[GoalProposal, ...] = ()
        self._next_proposals: tuple[GoalProposal, ...] = ()

    @property
    def active_goal(self) -> Goal | None:
        return self._active

    @property
    def visible_proposals(self) -> tuple[GoalProposal, ...]:
        return self._visible_proposals

    def defer_proposals(self, proposals: Sequence[GoalProposal]) -> None:
        for proposal in proposals:
            proposal.validate()
        self._next_proposals = tuple(proposals)

    def close_cycle_inputs(self) -> None:
        """Make current-cycle proposals visible to the next cycle."""
        self._visible_proposals = self._next_proposals
        self._next_proposals = ()

    @staticmethod
    def _condition_for(goal_type: str) -> tuple[str, str]:
        mapping = {
            "drink": ("water_at_setpoint", "water"),
            "eat": ("food_at_setpoint", "food"),
            "recover_energy": ("energy_at_setpoint", "energy"),
            "restore_integrity": ("integrity_at_setpoint", "integrity"),
        }
        return mapping.get(goal_type, (f"{goal_type}_satisfied", goal_type))

    def _eligible(
        self,
        proposal: GoalProposal,
        *,
        t_monde: int,
    ) -> bool:
        key = (proposal.goal_type, proposal.target)
        until = self._refractory_until.get(key)
        if until is None or t_monde >= until:
            return True
        return proposal.current_pressure >= self._config.critical_pressure

    def arbitrate(
        self,
        proposals: Sequence[GoalProposal],
        *,
        t_monde: int,
        cycle: int,
        satisfied: bool = False,
        invalid: bool = False,
    ) -> Goal | None:
        for proposal in proposals:
            proposal.validate()
            self._latest_pressure[(proposal.goal_type, proposal.target)] = (
                proposal.current_pressure
            )

        if self._active is not None and (satisfied or invalid):
            self._active = None
            # The visible proposal set belongs to the previous cycle and may
            # describe the pre-consequence body state. Do not reactivate from
            # that stale set in the same arbitration.
            return None

        eligible = [
            proposal
            for proposal in proposals
            if proposal.current_pressure >= self._config.p_min
            and self._eligible(proposal, t_monde=t_monde)
        ]
        eligible.sort(
            key=lambda p: (
                -p.current_pressure,
                p.goal_type,
                p.target,
                p.id,
            )
        )

        if self._active is None:
            if not eligible:
                return None
            chosen = eligible[0]
            satisfaction, measure = self._condition_for(chosen.goal_type)
            self._active = Goal(
                id=f"goal:{chosen.goal_type}:{chosen.target}:{t_monde}:{cycle}",
                goal_type=chosen.goal_type,
                target=chosen.target,
                satisfaction_condition=satisfaction,
                principal_measure=measure,
                current_pressure=chosen.current_pressure,
                state="active",
                activation_t=t_monde,
                activation_cycle=cycle,
            )
            self._active.validate()
            return self._active

        active_key = (self._active.goal_type, self._active.target)
        active_pressure = self._latest_pressure.get(
            active_key,
            self._active.current_pressure,
        )
        replacement = next(
            (
                proposal
                for proposal in eligible
                if (proposal.goal_type, proposal.target) != active_key
                and proposal.current_pressure
                >= active_pressure + self._config.replacement_hysteresis
            ),
            None,
        )

        if replacement is not None:
            satisfaction, measure = self._condition_for(replacement.goal_type)
            self._active = Goal(
                id=f"goal:{replacement.goal_type}:{replacement.target}:{t_monde}:{cycle}",
                goal_type=replacement.goal_type,
                target=replacement.target,
                satisfaction_condition=satisfaction,
                principal_measure=measure,
                current_pressure=replacement.current_pressure,
                state="active",
                activation_t=t_monde,
                activation_cycle=cycle,
            )
        else:
            self._active = Goal(
                id=self._active.id,
                goal_type=self._active.goal_type,
                target=self._active.target,
                satisfaction_condition=self._active.satisfaction_condition,
                principal_measure=self._active.principal_measure,
                current_pressure=active_pressure,
                state="active",
                activation_t=self._active.activation_t,
                activation_cycle=self._active.activation_cycle,
            )

        self._active.validate()
        return self._active

    def note_non_plannable(
        self,
        *,
        material_context_hash: str,
        t_monde: int,
    ) -> bool:
        if self._active is None:
            return False
        key = (self._active.goal_type, self._active.target)
        previous = self._impossible_failures.get(key)
        if previous is None or previous[0] != material_context_hash:
            count = 1
        else:
            count = previous[1] + 1
        self._impossible_failures[key] = (material_context_hash, count)

        if count < self._config.impossible_failures_required:
            return False

        self._refractory_until[key] = t_monde + self._config.refractory_steps
        self._active = None
        self._impossible_failures.pop(key, None)
        return True

    def export_causal_state(self) -> object:
        return {
            "config_version": self._config.version,
            "active": None
            if self._active is None
            else {
                "id": self._active.id,
                "goal_type": self._active.goal_type,
                "target": self._active.target,
                "satisfaction_condition": self._active.satisfaction_condition,
                "principal_measure": self._active.principal_measure,
                "current_pressure": self._active.current_pressure,
                "state": self._active.state,
                "activation_t": self._active.activation_t,
                "activation_cycle": self._active.activation_cycle,
            },
            "latest_pressure": [
                [goal_type, target, pressure]
                for (goal_type, target), pressure in sorted(self._latest_pressure.items())
            ],
            "refractory_until": [
                [goal_type, target, until]
                for (goal_type, target), until in sorted(self._refractory_until.items())
            ],
            "impossible_failures": [
                [goal_type, target, context_hash, count]
                for (goal_type, target), (context_hash, count)
                in sorted(self._impossible_failures.items())
            ],
            "visible_proposals": [
                {
                    "id": p.id,
                    "source": p.source,
                    "goal_type": p.goal_type,
                    "target": p.target,
                    "base_pressure": p.base_pressure,
                    "current_pressure": p.current_pressure,
                    "justification_ref": p.justification_ref,
                    "t_monde": p.t_monde,
                    "cycle": p.cycle,
                    "rule_version": p.rule_version,
                }
                for p in self._visible_proposals
            ],
            "next_proposals": [
                {
                    "id": p.id,
                    "source": p.source,
                    "goal_type": p.goal_type,
                    "target": p.target,
                    "base_pressure": p.base_pressure,
                    "current_pressure": p.current_pressure,
                    "justification_ref": p.justification_ref,
                    "t_monde": p.t_monde,
                    "cycle": p.cycle,
                    "rule_version": p.rule_version,
                }
                for p in self._next_proposals
            ],
        }

    def restore_causal_state(self, state: object) -> None:
        if not isinstance(state, Mapping):
            raise ValueError("Goal Manager state must be a mapping")
        if state.get("config_version") != self._config.version:
            raise ValueError("Goal Manager config version mismatch")

        raw_active = state.get("active")
        if raw_active is None:
            self._active = None
        elif isinstance(raw_active, Mapping):
            self._active = Goal(
                id=str(raw_active["id"]),
                goal_type=str(raw_active["goal_type"]),
                target=str(raw_active["target"]),
                satisfaction_condition=str(raw_active["satisfaction_condition"]),
                principal_measure=str(raw_active["principal_measure"]),
                current_pressure=float(raw_active["current_pressure"]),
                state=str(raw_active["state"]),
                activation_t=int(raw_active["activation_t"]),
                activation_cycle=int(raw_active["activation_cycle"]),
            )
        else:
            raise ValueError("invalid active goal state")

        self._latest_pressure = {
            (str(row[0]), str(row[1])): float(row[2])
            for row in state.get("latest_pressure", [])
        }
        self._refractory_until = {
            (str(row[0]), str(row[1])): int(row[2])
            for row in state.get("refractory_until", [])
        }
        self._impossible_failures = {
            (str(row[0]), str(row[1])): (str(row[2]), int(row[3]))
            for row in state.get("impossible_failures", [])
        }

        def decode_proposals(name: str) -> tuple[GoalProposal, ...]:
            raw_list = state.get(name, [])
            if not isinstance(raw_list, list):
                raise ValueError(f"invalid {name}")
            result: list[GoalProposal] = []
            for raw in raw_list:
                if not isinstance(raw, Mapping):
                    raise ValueError(f"invalid proposal in {name}")
                proposal = GoalProposal(
                    id=str(raw["id"]),
                    source=str(raw["source"]),
                    goal_type=str(raw["goal_type"]),
                    target=str(raw["target"]),
                    base_pressure=float(raw["base_pressure"]),
                    current_pressure=float(raw["current_pressure"]),
                    justification_ref=str(raw["justification_ref"]),
                    t_monde=int(raw["t_monde"]),
                    cycle=int(raw["cycle"]),
                    rule_version=str(raw["rule_version"]),
                )
                proposal.validate()
                result.append(proposal)
            return tuple(result)

        self._visible_proposals = decode_proposals("visible_proposals")
        self._next_proposals = decode_proposals("next_proposals")
