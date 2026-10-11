"""Stage-10 sleep-mode custody boundary, NOT a physical command executor.

MVP v1.2.1 sections 15.1-15.5, DC-13, INV-39/47/52/53.
Only an *applied* Action Control-admitted ordinary Competition sleep option
can arm entry on the next world step. Reduced capture, reflex admission,
world advancement, journaling and cognition are supplied by their owners.
This object owns only pending/active sleep-mode timing; it never dispatches.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Mapping

from lab.determinism import canonical_causal_bytes, sha256_hex


@dataclass(frozen=True, slots=True)
class SleepStepDecision:
    """Internal control request; NEVER grants Action Control admission."""
    world_step: int
    mode: str  # sleeping | waking
    woke: bool
    reason: str | None
    interrupt_consolidation: bool
    resume_cognition: bool
    require_sleep_command: bool


class SleepSession:
    """One causal sleep-mode owner. Scheduler advances the clock externally."""

    schema = "stage10-sleep-session-v1"
    owner_id = "individual.sleep_mode"

    def __init__(self, *, wake_policy_version: str):
        if type(wake_policy_version) is not str or not wake_policy_version.strip():
            raise ValueError("versioned DC-13 policy required")
        self._wake_policy_version = wake_policy_version
        self._mode = "awake"
        self._last_world_step = 0
        self._admitted_sleep_step: int | None = None
        self._entry_step: int | None = None
        self._pending_result: SleepStepDecision | None = None
        self._last_wake_step: int | None = None

    @property
    def mode(self) -> str:
        return self._mode

    @property
    def entry_step(self) -> int | None:
        return self._entry_step

    @property
    def last_world_step(self) -> int:
        return self._last_world_step

    @property
    def sleep_duration(self) -> int:
        if self._mode != "sleeping" or self._entry_step is None:
            return 0
        return self._last_world_step - self._entry_step + 1

    @staticmethod
    def _applied_admission(*, admission: object, prepared: object,
                           expected_primitive: str | None = None,
                           expected_source: str | None = None) -> bool:
        """Require the *exact same* command accepted by Action Control.

        The caller must supply real Action Control objects. This local
        guard cannot cryptographically attest the scheduler's command-send
        journal; integration must verify that externally.
        """
        command = getattr(admission, "command", None)
        planned = getattr(prepared, "command", None)
        return (
            getattr(admission, "ok", None) is True
            and command is not None
            and planned is not None
            and command == planned
            and (expected_primitive is None
                 or getattr(command, "primitive", None) == expected_primitive)
            and (expected_source is None or getattr(prepared, "source", None) == expected_source)
            and (getattr(prepared, "source", None) != "decision"
                 or getattr(prepared, "option_ref", None) is not None)
            and (getattr(prepared, "source", None) != "reflex"
                 or getattr(prepared, "trigger_ref", None) is not None)
        )

    def record_applied_sleep_decision(
        self, *, world_step: int, admission: object, prepared: object,
        motive_type: str, execution_status: str,
    ) -> None:
        """Call AFTER the nonlethal step and Action Control send (never at proposal)."""
        if (type(world_step) is not int or world_step < 1
                or world_step != self._last_world_step
                or self._mode != "awake"
                or self._admitted_sleep_step is not None
                or self._pending_result is not None
                or execution_status != "applied"
                or motive_type != "sleep_pressure"
                or not self._applied_admission(
                    admission=admission, prepared=prepared,
                    expected_primitive="dormir", expected_source="decision")):
            raise ValueError("sleep entry requires actually applied ordinary admitted dormir")
        self._admitted_sleep_step = world_step

    def open_world_step(self, world_step: int) -> str:
        """One chronological opening, with sleep entry delayed to next step.

        A wake at step t allows normal cognition at t, not a second sleep
        command. Caller records distinct sleep_entered and consolidation_started
        events: this state machine never starts consolidation on its own.
        """
        if (type(world_step) is not int or world_step != self._last_world_step + 1
                or self._pending_result is not None):
            raise ValueError("sleep step must be opened exactly once in world order")
        if self._admitted_sleep_step is not None:
            if self._mode != "awake" or world_step != self._admitted_sleep_step + 1:
                raise ValueError("invalid delayed sleep admission chronology")
            self._mode = "sleeping"
            self._entry_step = world_step
            self._admitted_sleep_step = None
        self._last_world_step = world_step
        return self._mode

    def evaluate_sleep_step(
        self, *, signals: object, frozen_sleep_pressure: float, wake_rule: object,
    ) -> SleepStepDecision:
        """Wake decision uses ONLY reduced/authorized signals, never oracle.

        Caller evaluates Perception.reduite and ActionControl.reflex/admit prior
        to calling this method. A wake does not retroactively create captures.
        """
        if self._mode != "sleeping" or self._pending_result is not None:
            raise ValueError("dedicated wake evaluation requires one open sleep step")
        if getattr(getattr(wake_rule, "config", None), "version", None) != self._wake_policy_version:
            raise ValueError("DC-13 wake rule config version changed during sleep")
        if getattr(signals, "consecutive_sleep_steps", None) != self.sleep_duration:
            raise ValueError("wake rule must use exact simulated sleeping duration")
        wake_reason = wake_rule.wake_reason(
            signals=signals, frozen_sleep_pressure=frozen_sleep_pressure,
        )
        allowed = {None, "reflex", "alert", "dated_intention", "maximum_duration", "natural_end"}
        if wake_reason not in allowed:
            raise ValueError("unrecognized dedicated wake rule reason")
        if wake_reason == "reflex" and getattr(signals, "admitted_reflex", None) is not True:
            raise ValueError("reflex wake requires admitted reflex")
        if wake_reason is not None:
            self._mode = "awake"
            self._entry_step = None
            self._last_wake_step = self._last_world_step
        result = SleepStepDecision(
            world_step=self._last_world_step,
            mode=self._mode,
            woke=wake_reason is not None,
            reason=wake_reason,
            interrupt_consolidation=(wake_reason is not None
                                     and getattr(signals, "consolidation_active", False) is True),
            resume_cognition=wake_reason is not None and wake_reason != "reflex",
            require_sleep_command=wake_reason is None,
        )
        self._pending_result = result
        return result

    def finish_sleep_step(
        self, *, decision: SleepStepDecision, admission: object | None = None,
        prepared: object | None = None, command_sent: bool,
        world_advanced: bool, consolidation_interrupted: bool = False,
    ) -> None:
        """Verify caller's single-step evidence, NOT dispatch or advance.

        On waking, a direct reflex or ordinary deliberation is responsible
        for the one command. A blocked step must be handled by scheduler and
        cannot be misreported as a normally completed sleep step.
        """
        if self._pending_result != decision:
            raise ValueError("sleep decision no longer matches current step")
        if type(command_sent) is not bool or type(world_advanced) is not bool:
            raise ValueError("world transition evidence must be explicit")
        if not command_sent or not world_advanced:
            raise ValueError("completed sleep/wake step requires one applied world command")
        if decision.interrupt_consolidation != consolidation_interrupted:
            raise ValueError("waking must interrupt consolidation before cognition")
        if not self._applied_admission(admission=admission, prepared=prepared):
            raise ValueError("every completed command needs fresh Action Control admission")
        actual_primitive = getattr(admission.command, "primitive", None)
        actual_source = getattr(prepared, "source", None)
        if decision.require_sleep_command:
            if actual_primitive != "dormir" or actual_source not in {"sleep", "decision"}:
                raise ValueError("sleep step needs an admitted sleep command")
        elif decision.reason == "reflex":
            if actual_source != "reflex" or actual_primitive == "dormir":
                raise ValueError("a reflex wake needs an admitted direct reflex command")
        elif actual_source != "decision":
            raise ValueError("nonreflex wake must deliberate an ordinary admitted command")
        self._pending_result = None

    def export_causal_state(self) -> dict[str, object]:
        raw = {
            "schema": self.schema,
            "wake_policy_version": self._wake_policy_version,
            "mode": self._mode,
            "last_world_step": self._last_world_step,
            "admitted_sleep_step": self._admitted_sleep_step,
            "entry_step": self._entry_step,
            "last_wake_step": self._last_wake_step,
            "pending_result": None if self._pending_result is None else {
                field: getattr(self._pending_result, field)
                for field in self._pending_result.__dataclass_fields__
            },
        }
        raw["digest"] = sha256_hex(canonical_causal_bytes(raw))
        return deepcopy(raw)

    def restore_causal_state(self, state: object) -> None:
        if (type(state) is not dict or set(state) != {
            "schema", "wake_policy_version", "mode", "last_world_step",
            "admitted_sleep_step", "entry_step", "last_wake_step",
            "pending_result", "digest",
        } or state["schema"] != self.schema
                or state["wake_policy_version"] != self._wake_policy_version):
            raise ValueError("incompatible sleep session snapshot")
        if (sha256_hex(canonical_causal_bytes({k: v for k, v in state.items() if k != "digest"}))
                != state["digest"]):
            raise ValueError("sleep snapshot digest mismatch")
        step, admitted, entry, wake = (
            state["last_world_step"], state["admitted_sleep_step"],
            state["entry_step"], state["last_wake_step"],
        )
        if (type(step) is not int or step < 0
                or any(x is not None and (type(x) is not int or not 1 <= x <= step)
                       for x in (admitted, entry, wake))
                or state["mode"] not in {"awake", "sleeping"}):
            raise ValueError("invalid sleep-session chronology")
        if (state["mode"] == "sleeping" and (entry is None or admitted is not None)
                or state["mode"] == "awake" and entry is not None
                or admitted is not None and admitted != step):
            raise ValueError("incoherent sleep-mode transition snapshot")
        raw = state["pending_result"]
        pending = None
        if raw is not None:
            if (type(raw) is not dict or set(raw) != {
                "world_step", "mode", "woke", "reason",
                "interrupt_consolidation", "resume_cognition", "require_sleep_command",
            }):
                raise ValueError("invalid pending sleep decision schema")
            pending = SleepStepDecision(**raw)
            if (type(pending.world_step) is not int or pending.world_step != step
                    or type(pending.woke) is not bool
                    or type(pending.interrupt_consolidation) is not bool
                    or type(pending.resume_cognition) is not bool
                    or type(pending.require_sleep_command) is not bool
                    or pending.mode != state["mode"]
                    or pending.woke == pending.require_sleep_command
                    or (pending.woke and wake != step)
                    or (pending.require_sleep_command and entry is None)):
                raise ValueError("incoherent pending sleep decision")
        self._last_world_step = step
        self._admitted_sleep_step = admitted
        self._entry_step = entry
        self._last_wake_step = wake
        self._mode = state["mode"]
        self._pending_result = pending
