"""External evaluation bench for normative Stage 2.

Spec: 18, 19.1-19.5, DC-14, INV-02, INV-27-29.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .journal_views import EvaluationTrace
from .oracle import Oracle, OracleCapability


@dataclass(frozen=True, slots=True)
class BenchMetrics:
    lethal_transitions: int = 0
    lethal_rollbacks: int = 0
    safety_blocks: int = 0
    operator_alerts: int = 0

    def as_dict(self) -> dict[str, int]:
        return {
            "lethal_transitions": self.lethal_transitions,
            "lethal_rollbacks": self.lethal_rollbacks,
            "safety_blocks": self.safety_blocks,
            "operator_alerts": self.operator_alerts,
        }


class EvaluationBench:
    """Owns metrics and evaluation trace outside the individual."""

    owner_id = "evaluation_bench"

    def __init__(
        self,
        *,
        oracle: Oracle,
        capability: OracleCapability,
        trace: EvaluationTrace,
    ) -> None:
        self._oracle = oracle
        self._capability = capability
        self._trace = trace
        self._metrics = BenchMetrics()

    @property
    def metrics(self) -> BenchMetrics:
        return self._metrics

    def oracle_truth(self) -> Mapping[str, object]:
        truth = self._oracle.read_ground_truth(self._capability)
        self._trace.append(kind="oracle_read", data={"keys": sorted(truth)})
        return truth

    def _replace_metrics(self, **updates: int) -> None:
        current = self._metrics.as_dict()
        current.update(updates)
        self._metrics = BenchMetrics(**current)

    def count_lethal_transition(self, *, data: Mapping[str, object]) -> None:
        self._replace_metrics(
            lethal_transitions=self._metrics.lethal_transitions + 1
        )
        self._trace.append(kind="lethal_transition", data=dict(data))

    def count_lethal_rollback(self, *, data: Mapping[str, object]) -> None:
        self._replace_metrics(
            lethal_rollbacks=self._metrics.lethal_rollbacks + 1
        )
        self._trace.append(kind="lethal_rollback", data=dict(data))

    def count_safety_block(self, *, data: Mapping[str, object]) -> None:
        self._replace_metrics(
            safety_blocks=self._metrics.safety_blocks + 1
        )
        self._trace.append(kind="safety_block", data=dict(data))

    def alert_operator(self, *, data: Mapping[str, object]) -> None:
        self._replace_metrics(
            operator_alerts=self._metrics.operator_alerts + 1
        )
        self._trace.append(kind="operator_alert", data=dict(data))

    def export_causal_state(self) -> object:
        """Bench state is not individual causal state, but is replayable externally."""

        return {"metrics": self._metrics.as_dict()}

    def restore_causal_state(self, state: object) -> None:
        if not isinstance(state, Mapping):
            raise ValueError("bench state must be a mapping")
        raw = state.get("metrics")
        if not isinstance(raw, Mapping):
            raise ValueError("bench metrics are missing")
        self._metrics = BenchMetrics(
            lethal_transitions=int(raw["lethal_transitions"]),
            lethal_rollbacks=int(raw["lethal_rollbacks"]),
            safety_blocks=int(raw["safety_blocks"]),
            operator_alerts=int(raw["operator_alerts"]),
        )
