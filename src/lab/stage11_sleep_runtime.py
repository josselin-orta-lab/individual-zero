"""One autonomous mortal I0 with Stage-10 sleep and Stage-11 exploration.

The historical Stage-10 and Stage-11 development fixtures stay unchanged.
Multiple inheritance here is cooperative rather than parallel execution:
one Stage-9 substrate constructs one Scheduler, WorldBody, journal and
Memory. Stage-11 awake hooks and Stage-10 sleep hooks share that substrate.
This is a software integration entrypoint, not scientific stage acceptance.
"""
from __future__ import annotations

from dataclasses import replace

from .mortal_execution import MortalStatus
from .stage10_runtime import Stage10Config, Stage10Runtime
from .stage11_runtime import Stage11Config, Stage11Runtime


class Stage11SleepRuntime(Stage11Runtime, Stage10Runtime):
    """Single physical and causal authority for awake exploration and sleep."""

    individual_id = "i0-v1.3.1-stage11-sleep-integrated"

    def __init__(
        self, *, stage11_config: Stage11Config,
        stage10_config: Stage10Config, wal_path: str | None,
        m11_sqlite_custody: bool = False, **kwargs,
    ):
        stage11_config.validate()
        stage10_config.validate()
        if stage11_config.stage9 != stage10_config.stage9:
            raise ValueError("Stages 10 and 11 must share the same Stage-9 baseline")
        if kwargs.get("autonomous_mortal") is not True:
            raise ValueError("integrated v1.3.1 I0 must be autonomous and mortal")
        if type(m11_sqlite_custody) is not bool:
            raise ValueError("SQLite custody must be explicitly opted into")
        if m11_sqlite_custody:
            if wal_path is not None:
                raise ValueError("M11 owns the ONLY durable journal; no secondary WAL")
        elif not wal_path:
            raise ValueError("integrated mortal I0 requires an exclusive durable WAL path")
        self._m11_sqlite_custody = m11_sqlite_custody
        self._m11_step_capability = False
        self._combined_sleep_config = stage10_config
        super().__init__(config=stage11_config, **kwargs)
        if self.journal.entries:
            raise RuntimeError("integrated I0 was already born without WAL custody")
        if not m11_sqlite_custody:
            self.journal.enable_durable_wal(path=wal_path)
            if not self.journal.durable_wal_enabled:
                raise RuntimeError("integrated I0 requires fsynced causal journal custody")
        elif self.journal.durable_wal_enabled:
            raise RuntimeError("M11 candidate must not own a parallel WAL")
        if self.stage3.substrate.mortal_status is None:
            raise RuntimeError("integrated runtime was not born mortal")
        if self.stage3.substrate.bench is not None:
            raise RuntimeError("integrated runtime must not load an evaluation bench")
        if self.stage3.substrate.evaluation_trace is not None:
            raise RuntimeError("integrated runtime must not load an oracle trace")
        ids = [owner.owner_id for owner in self.causal_owners]
        if len(ids) != len(set(ids)):
            raise RuntimeError("integrated runtime has duplicate causal custody")

    def _parent_runtime_config(self, config: Stage11Config) -> Stage10Config:
        """Stage-11 UC amendments precede Stage-10 UC amendments at birth."""
        if config != self._stage11_config:
            raise ValueError("unexpected Stage-11 configuration during construction")
        return replace(
            self._combined_sleep_config,
            stage9=config.with_budget(),
        )

    def run_step(self):
        """Fail closed on every uncertain unified mortal cognitive step.

        An exception after opening a world step might have consumed UCs,
        published learning or even committed a physical transition. We can
        neither rewind nor retry that life. Preserve the available WAL prefix,
        freeze WorldBody and refuse further cognitive/physical execution.

        A *previously recorded* safety block is an expected waiting state:
        the independent diagnostic console may later resolve it from a
        verified zero-advance closure. It is not a technical corruption.
        """
        if self._m11_sqlite_custody and self._m11_step_capability is not True:
            raise RuntimeError("M11-owned runtime is not directly dispatchable")
        substrate = self.stage3.substrate
        boundary = substrate._mortal_boundary
        if boundary is None or substrate.mortal_status is not MortalStatus.ACTIVE:
            raise RuntimeError("dead, halted or stopped individual cannot execute")
        if substrate.safety.blocked:
            # The EXTERNAL campaign console must still see this blocked
            # boundary so it can durably publish experiment_stopped. In
            # diagnostic mode the console only observes it and the distinct
            # safety block remains eligible for a verified operator release.
            console = getattr(substrate, "_operator_control", None)
            if console is not None:
                console.before_open_step()
            raise RuntimeError("mortal individual is in an unresolved safety block")
        try:
            result = super().run_step()
            # DC-14 requires immediate campaign termination at a nonlethal
            # safety block. A second run_step() invocation is not necessary:
            # there must be no gap where the completed campaign can appear
            # active despite an already closed zero-advance world attempt.
            console = getattr(substrate, "_operator_control", None)
            if console is not None and substrate.mortal_status is MortalStatus.ACTIVE:
                if result.execution_status == "safety_block" and console.mode == "campaign":
                    console.arreter(reason="campaign_safety_block")
                elif (result.execution_status in ("applied", "safety_block")
                      and console.maximum_world_steps is not None
                      and self.scheduler.t_monde >= console.maximum_world_steps):
                    # The last allowed physical command has just been
                    # durably closed. Publish the operator stop at this same
                    # boundary, never by opening a fictitious next step.
                    console.arreter(reason="world_step_cap_reached")
            return result
        except Exception:
            # Do not mask a confirmed physical death or authorized operator
            # stop with a fake technical halt. Otherwise the state is now
            # uncertain, even when no actual command reached WorldBody.
            if substrate.mortal_status is MortalStatus.ACTIVE:
                boundary.halt(failed_step=self.scheduler.t_monde)
            raise
