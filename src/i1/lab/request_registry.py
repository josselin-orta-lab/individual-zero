"""Stage-7 request registry owned by Bus and Contract.

The registry validates request chains and tracks status. It does not interpret
questions or mutate recipient state.

Spec: 4.5, 5.3, 20.3 Stage 7, INV-20.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from i0.requests import Request, Response


@dataclass(frozen=True, slots=True)
class RequestRegistryConfig:
    version: str
    recency_window_steps: int

    def validate(self) -> None:
        if not self.version:
            raise ValueError("request registry version must not be empty")
        if self.recency_window_steps < 1:
            raise ValueError("request recency window must be >= 1")


@dataclass(frozen=True, slots=True)
class RequestStatus:
    request_ref: str
    state: str
    accepted_t_monde: int
    closed_t_monde: int | None
    response_status: str | None


class RequestRegistry:
    owner_id = "bus.request_registry"

    def __init__(self, config: RequestRegistryConfig) -> None:
        config.validate()
        self._config = config
        self._requests: dict[str, Request] = {}
        self._statuses: dict[str, RequestStatus] = {}
        self._recent_questions: dict[tuple[str, str], int] = {}

    @property
    def statuses(self) -> Mapping[str, RequestStatus]:
        return dict(self._statuses)

    def _trim_recency(self, *, t_monde: int) -> None:
        cutoff = t_monde - self._config.recency_window_steps + 1
        self._recent_questions = {
            key: step
            for key, step in self._recent_questions.items()
            if step >= cutoff
        }

    def register(self, request: Request, *, t_monde: int) -> None:
        request.validate()
        if request.id in self._requests:
            raise ValueError("duplicate request id")
        if t_monde < 0:
            raise ValueError("request time must be non-negative")
        self._trim_recency(t_monde=t_monde)

        if request.depth == 1:
            parent = self._requests.get(str(request.parent_ref))
            if parent is None:
                raise ValueError("subrequest parent is unknown")
            if parent.root_ref != request.root_ref:
                raise ValueError("subrequest root_ref differs from parent chain")
            if request.budget_uc > parent.budget_uc:
                raise ValueError("subrequest exceeds parent UC budget")
            if request.budget_cycles > parent.budget_cycles:
                raise ValueError("subrequest exceeds parent cycle budget")
            if request.deadline_unit != parent.deadline_unit:
                raise ValueError("subrequest deadline unit must match parent")
            if request.deadline_value > parent.deadline_value:
                raise ValueError("subrequest exceeds parent deadline")
            # With depth bounded to one, a return edge to the root emitter is
            # the only possible two-node cycle.
            if request.recipient == parent.emitter:
                raise ValueError("cyclic request dependency")

        key = (request.recipient, request.question)
        if key in self._recent_questions:
            raise ValueError("duplicate_recent_question")

        self._requests[request.id] = request
        self._statuses[request.id] = RequestStatus(
            request_ref=request.id,
            state="pending",
            accepted_t_monde=t_monde,
            closed_t_monde=None,
            response_status=None,
        )
        self._recent_questions[key] = t_monde

    def cancel(self, request_ref: str, *, t_monde: int) -> None:
        if request_ref not in self._requests:
            raise KeyError(f"unknown request: {request_ref}")
        status = self._statuses[request_ref]
        if status.state != "pending":
            return
        self._statuses[request_ref] = RequestStatus(
            request_ref=request_ref,
            state="cancelled",
            accepted_t_monde=status.accepted_t_monde,
            closed_t_monde=t_monde,
            response_status=None,
        )

    def deliver(
        self,
        response: Response,
        *,
        t_monde: int,
    ) -> Response | None:
        response.validate()
        request = self._requests.get(response.request_ref)
        if request is None:
            raise KeyError(f"unknown request: {response.request_ref}")
        status = self._statuses[response.request_ref]
        if status.state == "cancelled":
            return None
        if status.state != "pending":
            raise ValueError("request is already closed")

        effective = response
        if request.deadline_unit == "pas" and t_monde > request.deadline_value:
            effective = Response(
                request_ref=response.request_ref,
                status="late",
                shareable=response.shareable,
                produced_t_monde=response.produced_t_monde,
                content=response.content,
                refusal_reason=response.refusal_reason,
                validity_step=response.validity_step,
            )
            effective.validate()

        self._statuses[response.request_ref] = RequestStatus(
            request_ref=response.request_ref,
            state="closed",
            accepted_t_monde=status.accepted_t_monde,
            closed_t_monde=t_monde,
            response_status=effective.status,
        )
        return effective

    def export_causal_state(self) -> object:
        return {
            "config_version": self._config.version,
            "requests": [
                {
                    "id": request.id,
                    "individual_id": request.individual_id,
                    "emitter": request.emitter,
                    "recipient": request.recipient,
                    "question": request.question,
                    "context_refs": list(request.context_refs),
                    "budget_uc": request.budget_uc,
                    "budget_cycles": request.budget_cycles,
                    "deadline_value": request.deadline_value,
                    "deadline_unit": request.deadline_unit,
                    "expected_format": request.expected_format,
                    "depth": request.depth,
                    "root_ref": request.root_ref,
                    "parent_ref": request.parent_ref,
                }
                for _, request in sorted(self._requests.items())
            ],
            "statuses": [
                {
                    "request_ref": status.request_ref,
                    "state": status.state,
                    "accepted_t_monde": status.accepted_t_monde,
                    "closed_t_monde": status.closed_t_monde,
                    "response_status": status.response_status,
                }
                for _, status in sorted(self._statuses.items())
            ],
            "recent_questions": [
                [recipient, question, step]
                for (recipient, question), step
                in sorted(self._recent_questions.items())
            ],
        }

    def restore_causal_state(self, state: object) -> None:
        if not isinstance(state, Mapping):
            raise ValueError("request registry state must be a mapping")
        if state.get("config_version") != self._config.version:
            raise ValueError("request registry config version mismatch")
        self._requests = {}
        for raw in state.get("requests", []):
            if not isinstance(raw, Mapping):
                raise ValueError("invalid request registry row")
            request = Request(
                id=str(raw["id"]),
                individual_id=str(raw["individual_id"]),
                emitter=str(raw["emitter"]),
                recipient=str(raw["recipient"]),
                question=str(raw["question"]),
                context_refs=tuple(str(x) for x in raw["context_refs"]),
                budget_uc=int(raw["budget_uc"]),
                budget_cycles=int(raw["budget_cycles"]),
                deadline_value=int(raw["deadline_value"]),
                deadline_unit=str(raw["deadline_unit"]),
                expected_format=str(raw["expected_format"]),
                depth=int(raw["depth"]),
                root_ref=str(raw["root_ref"]),
                parent_ref=(
                    None if raw.get("parent_ref") is None
                    else str(raw["parent_ref"])
                ),
            )
            request.validate()
            self._requests[request.id] = request

        self._statuses = {}
        for raw in state.get("statuses", []):
            if not isinstance(raw, Mapping):
                raise ValueError("invalid request status row")
            status = RequestStatus(
                request_ref=str(raw["request_ref"]),
                state=str(raw["state"]),
                accepted_t_monde=int(raw["accepted_t_monde"]),
                closed_t_monde=(
                    None if raw.get("closed_t_monde") is None
                    else int(raw["closed_t_monde"])
                ),
                response_status=(
                    None if raw.get("response_status") is None
                    else str(raw["response_status"])
                ),
            )
            self._statuses[status.request_ref] = status

        self._recent_questions = {
            (str(row[0]), str(row[1])): int(row[2])
            for row in state.get("recent_questions", [])
        }
