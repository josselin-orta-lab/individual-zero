"""Scripted Stage-1 runtime used to close the normative replay gate.

This is not a cognitive implementation. It wires the execution substrate with
scripted producers and a scalar technical world so that restoration and exact
continuation can be tested before Stage 2.

Spec: 20.3 Stage 1, 17.1-17.8, DC-08, DC-11, INV-22, INV-33, INV-44.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from i0.config import (
    MVP_CYCLE_PHASE_COMPONENT_ORDER,
    MVP_PHASE1_PRODUCER_ORDER,
    build_ontology_registry,
    build_schema_registry,
)
from .bus import InMemoryBus, ProducerBuffer
from .determinism import RandomStreamRegistry, deterministic_id
from .journal import HashChainedJournal
from .scheduler import CyclePhase, PhaseContext, Scheduler
from .snapshots import SnapshotManager, SnapshotRecord, SnapshotType


@dataclass(slots=True)
class ScalarWorld:
    """Stage-1 technical world stub with one scalar causal state."""

    value: int = 0

    @property
    def owner_id(self) -> str:
        return "stage1.scalar_world"

    def export_causal_state(self) -> object:
        return {"value": self.value}

    def restore_causal_state(self, state: object) -> None:
        if not isinstance(state, Mapping):
            raise ValueError("scalar world state must be a mapping")
        value = state.get("value")
        if not isinstance(value, int):
            raise ValueError("scalar world value must be an integer")
        self.value = value

    def apply_wait(self) -> None:
        """Technical Stage-1 command: deterministic one-step scalar advance."""

        self.value += 1


class ScriptedStage1Runtime:
    """Minimal integrated substrate proving deterministic restore and replay."""

    def __init__(self, *, campaign_seed: int) -> None:
        self.journal = HashChainedJournal()
        self.rng = RandomStreamRegistry(campaign_seed=campaign_seed)
        self.scheduler = Scheduler(
            journal=self.journal,
            phase_component_order=MVP_CYCLE_PHASE_COMPONENT_ORDER,
        )
        self.bus = InMemoryBus(
            schemas=build_schema_registry(),
            ontology=build_ontology_registry(),
            producer_order=MVP_PHASE1_PRODUCER_ORDER,
            journal=self.journal,
        )
        self.snapshots = SnapshotManager(journal=self.journal)
        self.world = ScalarWorld()
        self._buffers = {
            producer: ProducerBuffer(producer)
            for producer in MVP_PHASE1_PRODUCER_ORDER
        }

    @property
    def causal_owners(self):
        return (
            self.scheduler,
            self.rng,
            self.bus,
            self.world,
            *(self._buffers[name] for name in MVP_PHASE1_PRODUCER_ORDER),
        )

    def _script_payload(
        self,
        *,
        producer: str,
        context: PhaseContext,
    ) -> dict[str, object]:
        """Create a deterministic technical message with no cognitive meaning."""

        draw = self.rng.stream(f"stage1:{producer}").random()
        return {
            "n": context.cycle,
            "type": "stage1_scripted",
            "charge": {
                "producer": producer,
                "world_value": self.world.value,
                "draw": draw,
            },
            "provenance": [producer],
            "emp_prec": "0" * 64,
            "emp": "0" * 64,
            "t_monde": context.t_monde,
            "cycle": context.cycle,
            "attempt_ref": context.attempt_ref,
        }

    def _hooks(self):
        hooks = {}
        for phase_value, component_names in MVP_CYCLE_PHASE_COMPONENT_ORDER.items():
            phase = CyclePhase(phase_value)
            hooks[phase] = {}

            for component_name in component_names:
                if phase is CyclePhase.PRODUCTION and component_name in self._buffers:
                    def make_producer(name: str):
                        def producer(context: PhaseContext) -> None:
                            self._buffers[name].publish(
                                schema_name="JournalEvent",
                                schema_version="1.0",
                                payload=self._script_payload(
                                    producer=name,
                                    context=context,
                                ),
                                semantic_terms=("individual",),
                            )
                        return producer
                    hooks[phase][component_name] = make_producer(component_name)
                elif phase is CyclePhase.PRODUCTION and component_name == "bus":
                    def pour(context: PhaseContext) -> None:
                        self.bus.pour(
                            buffers=tuple(
                                self._buffers[name]
                                for name in reversed(MVP_PHASE1_PRODUCER_ORDER)
                            ),
                            t_monde=context.t_monde,
                            cycle=context.cycle,
                            attempt_ref=context.attempt_ref,
                        )
                    hooks[phase][component_name] = pour
                else:
                    hooks[phase][component_name] = lambda context: None
        return hooks

    def run_step(self, *, cycle: int = 1) -> None:
        """Execute one normal scripted world step."""

        self.scheduler.open_step()
        self.scheduler.run_cycle(cycle=cycle, hooks=self._hooks())

        attempt = self.scheduler.active_attempt
        if attempt is None:
            raise RuntimeError("scripted step lost active attempt")

        command_id = deterministic_id(
            "stage1-command-v1",
            attempt.t_monde,
            attempt.attempt_ref,
            "attendre",
        )
        self.journal.append(
            event_id=deterministic_id(
                "journal-event-v1",
                "stage1-runtime",
                attempt.t_monde,
                attempt.attempt_ref,
                "command",
            ),
            causal_event={
                "emitter": "stage1-runtime",
                "kind": "command_applied",
                "t_monde": attempt.t_monde,
                "attempt_ref": attempt.attempt_ref,
                "command_id": command_id,
                "primitive": "attendre",
                "world_before": self.world.value,
            },
        )
        self.world.apply_wait()
        self.journal.append(
            event_id=deterministic_id(
                "journal-event-v1",
                "stage1-runtime",
                attempt.t_monde,
                attempt.attempt_ref,
                "world_transition",
            ),
            causal_event={
                "emitter": "stage1-runtime",
                "kind": "world_transition",
                "t_monde": attempt.t_monde,
                "attempt_ref": attempt.attempt_ref,
                "world_after": self.world.value,
            },
        )
        self.bus.drain_available()
        self.scheduler.close_step(
            outcome="normal",
            applied_command_count=1,
            world_advance_count=1,
        )

    def take_snapshot(
        self,
        *,
        snapshot_type: SnapshotType = SnapshotType.PERIODIC,
    ) -> SnapshotRecord:
        attempt = self.scheduler.active_attempt
        return self.snapshots.take(
            snapshot_type=snapshot_type,
            individual_id="stage1-scripted",
            t_monde=self.scheduler.t_monde,
            cycle=0,
            attempt_ref=None if attempt is None else attempt.attempt_ref,
            owners=self.causal_owners,
            versions={"runtime": "mvp-v1.2.1"},
        )

    def restore(self, snapshot_id: str) -> SnapshotRecord:
        return self.snapshots.restore(
            snapshot_id,
            owners=self.causal_owners,
        )

    def causal_fingerprint(self) -> dict[str, object]:
        return {
            "scheduler": self.scheduler.export_causal_state(),
            "rng": self.rng.export_causal_state(),
            "bus": self.bus.export_causal_state(),
            "world": self.world.export_causal_state(),
        }
