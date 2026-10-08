"""Integrated Stage-3 reflex/control runtime.

The runtime orchestrates only. SymbolicPerception creates one immutable capture
per step. ActionControl alone invokes the admitted-command sender callback.

Spec: 3.4, 6.1, 9.1-9.4, 20.3 Stage 3, DC-12, INV-12, INV-13, INV-52.
"""

from __future__ import annotations

from dataclasses import dataclass

from i0.interfaces import PrimitiveCommand
from i0.modules import (
    ActionControl,
    ActionControlConfig,
    AdmissionResult,
    PerceptualCapture,
    PreparedCommand,
    StaticSafetyFacts,
    SymbolicPerception,
)

from .determinism import deterministic_id
from .injected_scenario import ScenarioEvent
from .safety_protocol import SafetyProtocolConfig
from .stage2_runtime import CommandExecution, ScriptedStage2Runtime
from .world import WorldLayout, WorldPhysicsConfig, command_digest


@dataclass(frozen=True, slots=True)
class Stage3StepResult:
    source: str
    command: PrimitiveCommand | None
    execution_status: str
    reflex_triggered: bool
    admission: AdmissionResult | None


class Stage3Runtime:
    """Shortest normative loop: local capture -> reflex/control -> world."""

    def __init__(
        self,
        *,
        config: WorldPhysicsConfig,
        layout: WorldLayout,
        phase_component_order,
        safety_config: SafetyProtocolConfig,
        safety_facts: StaticSafetyFacts,
        protected_integrity_threshold: float,
        scenario_id: str | None = None,
        scenario_version: str | None = None,
        scenario_events: tuple[ScenarioEvent, ...] = (),
    ) -> None:
        self.substrate = ScriptedStage2Runtime(
            config=config,
            layout=layout,
            phase_component_order=phase_component_order,
            safety_config=safety_config,
            scenario_id=scenario_id,
            scenario_version=scenario_version,
            scenario_events=scenario_events,
        )
        self.perception = SymbolicPerception()
        self.control = ActionControl(
            config=ActionControlConfig(
                safety_policy_version="mvp-v1.2.1",
                protected_integrity_threshold=protected_integrity_threshold,
            ),
            safety_facts=safety_facts,
            protocol_mask=self.substrate.safety.is_masked,
        )
        self._capture: PerceptualCapture | None = None
        self._capture_attempt_ref: str | None = None
        self._captures_this_step = 0
        self._event_sequence = 0

    @property
    def journal(self):
        return self.substrate.journal

    @property
    def world(self):
        return self.substrate.world

    @property
    def scheduler(self):
        return self.substrate.scheduler

    @property
    def bench(self):
        return self.substrate.bench

    def open_step(self) -> PerceptualCapture:
        self.substrate.open_step()
        attempt = self.scheduler.active_attempt
        if attempt is None:
            raise RuntimeError("step opening failed")

        local = self.world.capture_local(t_monde=attempt.t_monde)
        self._capture = self.perception.capture(
            local_state=local.as_dict(),
            telemetry=self.world.telemetry(),
        )
        self._capture_attempt_ref = attempt.attempt_ref
        self._captures_this_step = 1
        self._write(
            kind="perceptual_capture",
            data={
                "capture_t_monde": self._capture.t_monde,
                "position": {"x": self._capture.x, "y": self._capture.y},
                "adjacent_creature_count": len(self._capture.adjacent_creatures),
            },
        )
        return self._capture

    def _write(self, *, kind: str, data: dict[str, object]) -> None:
        attempt = self.scheduler.active_attempt
        if attempt is None:
            raise RuntimeError("Stage 3 event requires active step")
        event_id = deterministic_id(
            "journal-event-v1",
            "stage3-runtime",
            attempt.t_monde,
            attempt.attempt_ref,
            self._event_sequence,
            kind,
        )
        self._event_sequence += 1
        self.journal.append(
            event_id=event_id,
            causal_event={
                "emitter": "stage3-runtime",
                "kind": kind,
                "t_monde": attempt.t_monde,
                "attempt_ref": attempt.attempt_ref,
                "data": data,
            },
        )

    def _capture_required(self) -> PerceptualCapture:
        if self._capture is None:
            raise RuntimeError("open_step must capture before control")
        return self._capture

    def _trace_admission(
        self,
        *,
        prepared: PreparedCommand,
        admission: AdmissionResult,
    ) -> None:
        self._write(
            kind="command_admitted" if admission.ok else "command_vetoed",
            data={
                "command_hash": command_digest(admission.command),
                "primitive": admission.command.primitive,
                "source": prepared.source,
                "trigger_ref": prepared.trigger_ref,
                "option_ref": prepared.option_ref,
                "st_version_ref": prepared.st_version_ref,
                "reason": admission.reason,
                "scope": admission.scope,
                "rule_id": admission.rule_id,
                "rule_type": admission.rule_type,
                "policy_version": admission.policy_version,
            },
        )

    def _dispatch(
        self,
        *,
        prepared: PreparedCommand,
    ) -> tuple[AdmissionResult, CommandExecution | None]:
        capture = self._capture_required()

        admission, execution = self.control.dispatch_if_admitted(
            capture=capture,
            prepared=prepared,
            on_admission=lambda result: self._trace_admission(
                prepared=prepared,
                admission=result,
            ),
            sender=lambda command: self.substrate.send_admitted_command(
                command,
                source="action_control",
            ),
        )
        if execution is not None and not isinstance(execution, CommandExecution):
            raise TypeError("unexpected command execution result")
        return admission, execution

    def attempt_prepared(
        self,
        prepared: PreparedCommand,
    ) -> tuple[AdmissionResult, CommandExecution | None]:
        """Expose the Stage-3 controlled path for contract/integration tests."""

        return self._dispatch(prepared=prepared)

    def attempt_reflex(self):
        """Attempt only the direct reflex path, with no ordinary fallback.

        Returns (proposal, admission, execution). A refused or rolled-back
        reflex leaves the current world step open for cognitive deliberation.
        """

        capture = self._capture_required()
        reflex = self.control.reflex(capture)
        if reflex is None:
            return None, None, None

        self._write(
            kind="reflex_proposed",
            data={
                "stimulus": reflex.stimulus,
                "command_hash": command_digest(reflex.prepared.command),
            },
        )
        admission, execution = self._dispatch(prepared=reflex.prepared)
        if not admission.ok:
            self._write(
                kind="reflex_refused",
                data={
                    "reason": admission.reason,
                    "rule_id": admission.rule_id,
                },
            )
        return reflex, admission, execution

    def run_step(self) -> Stage3StepResult:
        reflex, admission, execution = self.attempt_reflex()

        if reflex is not None and admission is not None:
            if admission.ok and execution is not None:
                if execution.status == "applied":
                    self._capture = None
                    return Stage3StepResult(
                        source="reflex",
                        command=reflex.prepared.command,
                        execution_status="applied",
                        reflex_triggered=True,
                        admission=admission,
                    )
                if execution.status == "safety_block":
                    self._capture = None
                    return Stage3StepResult(
                        source="reflex",
                        command=reflex.prepared.command,
                        execution_status="safety_block",
                        reflex_triggered=True,
                        admission=admission,
                    )
                # Lethal rollback: reflex is not replayed. Continue to wait stub.

        wait = PreparedCommand(
            command=PrimitiveCommand("attendre"),
            source="stage3_wait_stub",
            option_ref="permanent_attendre",
        )
        admission, execution = self._dispatch(prepared=wait)
        if not admission.ok or execution is None:
            self.substrate.safety.enter_safety_block(
                reason="no_admissible_safe_command",
            )
            self.scheduler.close_step(
                outcome="blocked",
                applied_command_count=0,
                world_advance_count=0,
            )
            self._capture = None
            return Stage3StepResult(
                source="stage3_wait_stub",
                command=None,
                execution_status="safety_block",
                reflex_triggered=reflex is not None,
                admission=admission,
            )

        self._capture = None
        return Stage3StepResult(
            source="stage3_wait_stub",
            command=wait.command,
            execution_status=execution.status,
            reflex_triggered=reflex is not None,
            admission=admission,
        )

    @property
    def captures_this_step(self) -> int:
        return self._captures_this_step
