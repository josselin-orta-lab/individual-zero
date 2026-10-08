"""Stage-5 complete-state copies and lineage.

Copies are created only at coherent world-step boundaries. The parent is never
mutated by child execution. Prior technical history is referenced by the
parent's journal head hash rather than copied into the child journal.

Spec: 17.7, 20.3 Stage 5, INV-34.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Mapping, Sequence

from .injected_scenario import ScenarioEvent
from .stage5_runtime import Stage5Runtime


@dataclass(frozen=True, slots=True)
class LineageRecord:
    child_id: str
    parent_id: str
    copy_point_t_monde: int
    parent_journal_head: str
    battery_copy: bool


@dataclass(frozen=True, slots=True)
class Stage5Copy:
    runtime: Stage5Runtime
    lineage: LineageRecord


class Stage5CopyManager:
    """Bench-side copy administration. Never accessible to the individual."""

    def create_copy(
        self,
        *,
        parent: Stage5Runtime,
        child_id: str,
        battery_copy: bool,
        scenario_id: str | None = None,
        scenario_version: str | None = None,
        scenario_events: Sequence[ScenarioEvent] = (),
    ) -> Stage5Copy:
        if not child_id:
            raise ValueError("child_id must not be empty")
        if child_id == parent.individual_id:
            raise ValueError("copy must receive a new individual identifier")
        if parent.scheduler.active_attempt is not None:
            raise RuntimeError(
                "copies may be created only at a coherent world-step boundary"
            )

        owner_states = {
            owner.owner_id: deepcopy(owner.export_causal_state())
            for owner in parent.causal_owners
        }

        lineage = LineageRecord(
            child_id=child_id,
            parent_id=parent.individual_id,
            copy_point_t_monde=parent.scheduler.t_monde,
            parent_journal_head=parent.journal.head_hash,
            battery_copy=battery_copy,
        )

        child = Stage5Runtime(
            **parent.copy_constructor_kwargs(),
            individual_id=child_id,
            lineage_parent_id=parent.individual_id,
            lineage_copy_point=parent.journal.head_hash,
            battery_copy=battery_copy,
            scenario_id=scenario_id,
            scenario_version=scenario_version,
            scenario_events=tuple(scenario_events),
        )

        child_owners = {owner.owner_id: owner for owner in child.causal_owners}
        missing = sorted(set(owner_states) - set(child_owners))
        extra = sorted(set(child_owners) - set(owner_states))
        allowed_extra = {"scenario"} if scenario_id is not None else set()
        unexpected_extra = sorted(set(extra) - allowed_extra)
        if missing or unexpected_extra:
            raise ValueError(
                "copy owner mismatch; "
                f"missing={missing}, unexpected_extra={unexpected_extra}"
            )

        for owner_id in sorted(owner_states):
            state = deepcopy(owner_states[owner_id])

            # S_t is causal state, but the copied instance has a new identity.
            # Re-identification changes lineage metadata only, not cognitive
            # content, scores, timing, or decisions.
            if owner_id == "s_t":
                if not isinstance(state, Mapping):
                    raise ValueError("malformed S_t copy state")
                state = dict(state)
                state["individual_id"] = child_id
                raw_current = state.get("current")
                if isinstance(raw_current, Mapping):
                    current = dict(raw_current)
                    current["individual_id"] = child_id
                    state["current"] = current

            child_owners[owner_id].restore_causal_state(state)

        return Stage5Copy(runtime=child, lineage=lineage)
