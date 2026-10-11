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
        stage10_config: Stage10Config, wal_path: str, **kwargs,
    ):
        stage11_config.validate()
        stage10_config.validate()
        if stage11_config.stage9 != stage10_config.stage9:
            raise ValueError("Stages 10 and 11 must share the same Stage-9 baseline")
        if kwargs.get("autonomous_mortal") is not True:
            raise ValueError("integrated v1.3.1 I0 must be autonomous and mortal")
        if not wal_path:
            raise ValueError("integrated mortal I0 requires an exclusive durable WAL path")
        self._combined_sleep_config = stage10_config
        super().__init__(config=stage11_config, **kwargs)
        if self.journal.entries:
            raise RuntimeError("integrated I0 was already born without WAL custody")
        self.journal.enable_durable_wal(path=wal_path)
        if not self.journal.durable_wal_enabled:
            raise RuntimeError("integrated I0 requires fsynced causal journal custody")
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
        substrate = self.stage3.substrate
        boundary = substrate._mortal_boundary
        if boundary is None or substrate.mortal_status is not MortalStatus.ACTIVE:
            raise RuntimeError("dead, halted or stopped individual cannot execute")
        if substrate.safety.blocked:
            raise RuntimeError("mortal individual is in an unresolved safety block")
        try:
            return super().run_step()
        except Exception:
            # Do not mask a confirmed physical death or authorized operator
            # stop with a fake technical halt. Otherwise the state is now
            # uncertain, even when no actual command reached WorldBody.
            if substrate.mortal_status is MortalStatus.ACTIVE:
                boundary.halt(failed_step=self.scheduler.t_monde)
            raise
