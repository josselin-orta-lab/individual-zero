"""Normative request/response causal contracts.

Spec: 4.5, 5.2, INV-20.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True, slots=True)
class Request:
    id: str
    individual_id: str
    emitter: str
    recipient: str
    question: str
    context_refs: tuple[str, ...]
    budget_uc: int
    budget_cycles: int
    deadline_value: int
    deadline_unit: str
    expected_format: str
    depth: int
    root_ref: str
    parent_ref: str | None = None

    def validate(self) -> None:
        if not all(
            (self.id, self.individual_id, self.emitter, self.recipient,
             self.question, self.expected_format, self.root_ref)
        ):
            raise ValueError("request identity/routing fields are required")
        if self.budget_uc < 0 or self.budget_cycles < 1:
            raise ValueError("request budget must be explicit and non-negative")
        if self.deadline_value < 0:
            raise ValueError("request deadline must be non-negative")
        if self.deadline_unit not in {"pas", "cycle", "jour"}:
            raise ValueError("request deadline unit must be explicit")
        if self.depth not in {0, 1}:
            raise ValueError("request depth must be 0 or 1")
        if self.depth == 0 and self.parent_ref is not None:
            raise ValueError("root request cannot have a parent")
        if self.depth == 1 and self.parent_ref is None:
            raise ValueError("subrequest must name its parent")


@dataclass(frozen=True, slots=True)
class Response:
    request_ref: str
    status: str
    shareable: bool
    produced_t_monde: int
    content: object | None = None
    refusal_reason: str | None = None
    validity_step: int | None = None

    def validate(self) -> None:
        if not self.request_ref:
            raise ValueError("response request_ref is required")
        if self.status not in {
            "delivered",
            "late",
            "refused",
            "empty",
            "validation_rejected",
        }:
            raise ValueError("invalid response status")
        if self.produced_t_monde < 0:
            raise ValueError("response production time must be non-negative")
        if self.status == "refused" and not self.refusal_reason:
            raise ValueError("refused response requires a reason")
