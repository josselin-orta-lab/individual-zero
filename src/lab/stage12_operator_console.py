"""External Stage12 operator controls, not an Oracle or cognitive service.

All controls act at a closed Scheduler world-step boundary. Operator stop and
step cap are irreversible for this test identity, not evidence of physical
death. In diagnostic mode a *nonlethal* safety block may be resolved, never
a dead, halted or experiment-stopped world.
"""
from __future__ import annotations

from .determinism import canonical_causal_bytes, deterministic_id
from .mortal_execution import MortalStatus
from .stage2_runtime import ScriptedStage2Runtime


class Stage12OperatorConsole:
    owner_id = "operator_console"
    schema = "stage12-external-operator-control-v1"

    def __init__(
        self, *, substrate: ScriptedStage2Runtime,
        mode: str, policy_version: str,
        maximum_world_steps: int | None = None,
    ):
        if not isinstance(substrate, ScriptedStage2Runtime):
            raise TypeError("operator needs an actual I0 mortal substrate")
        if mode not in ("campaign", "diagnostic"):
            raise ValueError("operator mode must be campaign or diagnostic")
        if type(policy_version) is not str or not policy_version.strip():
            raise ValueError("versioned operator policy required")
        if maximum_world_steps is not None and (
            type(maximum_world_steps) is not int
            or maximum_world_steps < 1
            or maximum_world_steps < substrate.scheduler.t_monde
        ):
            raise ValueError("operator cannot cap a life to an earlier world step")
        self._substrate = substrate
        self._mode = mode
        self._policy_version = policy_version
        self._maximum_world_steps: int | None = None
        self._event_sequence = 0
        self._substrate.attach_operator_control(self)
        self._publish(
            "operator_console_configured",
            {"mode": mode, "policy_version": policy_version},
        )
        if maximum_world_steps is not None:
            self.plafonner(maximum_world_steps)

    @property
    def mode(self) -> str:
        return self._mode

    @property
    def maximum_world_steps(self) -> int | None:
        return self._maximum_world_steps

    def _require_live_boundary(self):
        sub = self._substrate
        if (sub.mortal_status is not MortalStatus.ACTIVE
                or sub.scheduler.active_attempt is not None):
            raise RuntimeError("operator control requires a living step boundary")

    def _publish(self, kind: str, data: dict[str, object]):
        self._require_live_boundary()
        sub = self._substrate
        t = sub.scheduler.t_monde
        event_id = deterministic_id(
            "stage12-external-operator-event-v1",
            self._policy_version, t, kind, self._event_sequence,
        )
        try:
            sub.journal.append(
                event_id=event_id,
                causal_event={
                    "emitter": "operator_console",
                    "kind": kind,
                    "t_monde": t,
                    "data": dict(data),
                },
            )
        except Exception:
            # A failed persistent control receipt makes continuing the
            # physical life ambiguous. Never restore a prior world/snapshot.
            sub._mortal_boundary.halt(failed_step=t)
            raise
        self._event_sequence += 1

    def plafonner(self, maximum_world_steps: int) -> None:
        """Set or tighten a physical-step cap; it cannot be raised or undone."""
        self._require_live_boundary()
        t = self._substrate.scheduler.t_monde
        if (type(maximum_world_steps) is not int
                or maximum_world_steps < 1
                or maximum_world_steps < t
                or (self._maximum_world_steps is not None
                    and maximum_world_steps > self._maximum_world_steps)):
            raise ValueError("operator cap must be a monotonic non-past bound")
        self._publish(
            "operator_step_cap_set",
            {"maximum_world_steps": maximum_world_steps,
             "previous_cap": self._maximum_world_steps,
             "policy_version": self._policy_version},
        )
        self._maximum_world_steps = maximum_world_steps
        if maximum_world_steps == t:
            self.arreter(reason="world_step_cap_reached")

    def arreter(self, *, reason: str) -> None:
        """Terminal experimental stop, never lethal death or restoration."""
        self._require_live_boundary()
        if type(reason) is not str or not reason.strip():
            raise ValueError("operator stop needs a reason")
        self._publish(
            "experiment_stopped",
            {
                "reason": reason, "policy_version": self._policy_version,
                "mode": self._mode,
                "maximum_world_steps": self._maximum_world_steps,
                "world_rewound": False,
                "physical_death": False,
            },
        )
        # The journal was durably acknowledged and sealed before WorldBody
        # becomes permanently frozen. Stop cannot append cognitive events.
        self._substrate._mortal_boundary.stop_experiment()

    def resoudre_blocage(self, *, decision: str, decision_ref: str) -> None:
        """Diagnostic only: release a technical block, not a physical death."""
        self._require_live_boundary()
        if self._mode != "diagnostic":
            raise RuntimeError("campaign blocks end experiments without resume")
        if type(decision_ref) is not str or not decision_ref:
            raise ValueError("operator decision identity required")
        if decision == "stop":
            self.arreter(reason="diagnostic_safety_block_stopped:" + decision_ref)
            return
        if decision != "resume":
            raise ValueError("diagnostic decision must be resume or stop")
        try:
            self._substrate.safety.resolve_diagnostic_block(
                decision_ref=decision_ref, policy_version=self._policy_version,
            )
        except Exception:
            self._substrate._mortal_boundary.halt(
                failed_step=self._substrate.scheduler.t_monde,
            )
            raise

    def before_open_step(self) -> None:
        """A cap or campaign block closes WITHOUT simulating an extra step."""
        self._require_live_boundary()
        sub = self._substrate
        if self._mode == "campaign" and sub.safety.blocked:
            self.arreter(reason="campaign_safety_block")
            raise RuntimeError("operator campaign closed at safety block")
        if (self._maximum_world_steps is not None
                and sub.scheduler.t_monde >= self._maximum_world_steps):
            self.arreter(reason="world_step_cap_reached")
            raise RuntimeError("operator stopped experiment at the world-step cap")

    def export_causal_state(self) -> dict[str, object]:
        return {
            "schema": self.schema, "policy_version": self._policy_version,
            "mode": self._mode,
            "maximum_world_steps": self._maximum_world_steps,
            "event_sequence": self._event_sequence,
            "observed_world_step": self._substrate.scheduler.t_monde,
            "status": self._substrate.mortal_status.value,
        }

    def restore_causal_state(self, state: object) -> None:
        if (type(state) is not dict
                or canonical_causal_bytes(state)
                != canonical_causal_bytes(self.export_causal_state())):
            raise ValueError("operator control cannot restore a stopped or older life")
