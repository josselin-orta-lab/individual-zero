"""Minimal Stage-4 metacognitive compute accounting.

The full normalized cognitive-fatigue dynamics belongs to Stage 10 / DC-13 and
requires P-39. Stage 4 therefore retains only the causal counter of UC actually
consumed plus the synthetic budget state required in S_t.

Spec: 16.1-16.3, 20.4 Stage 4.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True, slots=True)
class MinimalMetacognitionState:
    f_cog_uc_counter: int
    last_cycle_uc: int
    budget_state: str


class MinimalMetacognition:
    owner_id = "metacognition_health"

    def __init__(self) -> None:
        self._f_cog_uc_counter = 0
        self._last_cycle_uc = 0
        self._budget_state = "normal"

    @property
    def state(self) -> MinimalMetacognitionState:
        return MinimalMetacognitionState(
            f_cog_uc_counter=self._f_cog_uc_counter,
            last_cycle_uc=self._last_cycle_uc,
            budget_state=self._budget_state,
        )

    def close_cycle(
        self,
        *,
        consumed_uc: int,
        cycle_ceiling: int,
        degraded: bool,
        protected_capacity: int,
    ) -> None:
        if consumed_uc < 0 or cycle_ceiling < 0:
            raise ValueError("compute counters must be non-negative")
        if consumed_uc > cycle_ceiling:
            raise ValueError("consumed UC cannot exceed cycle ceiling")
        self._last_cycle_uc = consumed_uc
        self._f_cog_uc_counter += consumed_uc

        if degraded:
            self._budget_state = "degraded"
        elif (
            cycle_ceiling > 0
            and consumed_uc >= max(0, cycle_ceiling - protected_capacity)
        ):
            self._budget_state = "constrained"
        else:
            self._budget_state = "normal"

    def export_causal_state(self) -> object:
        return {
            "f_cog_uc_counter": self._f_cog_uc_counter,
            "last_cycle_uc": self._last_cycle_uc,
            "budget_state": self._budget_state,
        }

    def restore_causal_state(self, state: object) -> None:
        if not isinstance(state, Mapping):
            raise ValueError("metacognition state must be a mapping")
        total = state.get("f_cog_uc_counter")
        last = state.get("last_cycle_uc")
        budget_state = state.get("budget_state")
        if not isinstance(total, int) or total < 0:
            raise ValueError("invalid F_cog UC counter")
        if not isinstance(last, int) or last < 0:
            raise ValueError("invalid last-cycle UC")
        if budget_state not in {"normal", "constrained", "degraded"}:
            raise ValueError("invalid synthetic budget state")
        self._f_cog_uc_counter = total
        self._last_cycle_uc = last
        self._budget_state = str(budget_state)
