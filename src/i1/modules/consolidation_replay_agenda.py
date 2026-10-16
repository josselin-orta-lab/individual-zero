"""Stage-10 pass-2 *interleaved replay work agenda*, not causal inference.

MVP 15.6 / P-42: the deterministic recent/old interleaving is computed ONLY
from the frozen autobiographical episode batch. Each experienced event reference
is one priced 'episode_replay' unit; actual event re-experience, procedural
learning and hypothesis extraction still need their canonical owner adapters.
This agenda never reads the technical journal, oracle or WorldBody.
"""
from __future__ import annotations

from dataclasses import dataclass

from lab.determinism import canonical_causal_bytes, sha256_hex
from .consolidation_transaction import ConsolidationTransaction, PASSES
from .consolidation_pass_runner import ConsolidationPassPlan, ConsolidationUnit
from .consolidation_budget import ConsolidationWorkBudget


@dataclass(frozen=True, slots=True)
class ReplayAgendaPolicy:
    version: str
    recent_window_steps: int
    start_with_recent: bool

    def validate(self) -> None:
        if (type(self.version) is not str or not self.version.strip()
                or type(self.recent_window_steps) is not int or self.recent_window_steps < 1
                or type(self.start_with_recent) is not bool):
            raise ValueError("versioned P-42 recent/old replay policy required")


@dataclass(frozen=True, slots=True)
class ReplayAgendaEntry:
    unit_ref: str
    episode_ref: str
    event_ref: str
    temporal_partition: str
    event_offset: int

    def as_dict(self) -> dict[str, object]:
        return {
            "unit_ref": self.unit_ref, "episode_ref": self.episode_ref,
            "event_ref": self.event_ref, "temporal_partition": self.temporal_partition,
            "event_offset": self.event_offset,
        }


class InterleavedReplayAgenda:
    """A fixed deterministic list of *event work*, not synthesized knowledge."""

    def __init__(self, *, tx: ConsolidationTransaction, policy: ReplayAgendaPolicy):
        policy.validate()
        if tx.status != "active" or tx.cursor != PASSES.index("interleaved_replay"):
            raise ValueError("replay agenda belongs only to the second pass")
        episodes = tx.frozen_episodes_copy()
        recent: list[tuple[int, str, tuple[str, ...]]] = []
        old: list[tuple[int, str, tuple[str, ...]]] = []
        seen_events: set[str] = set()
        for ref in tx.batch:
            item = episodes[ref]
            end = item.get("end_t_monde")
            refs = item.get("event_refs")
            if (type(end) is not int or end >= tx.cut.world_step
                    or type(refs) is not list or not refs
                    or any(type(ev) is not str or not ev for ev in refs)
                    or len(set(refs)) != len(refs)):
                raise ValueError("invalid closed Memory episode replay evidence")
            if seen_events.intersection(refs):
                raise ValueError("one lived event cannot belong to two frozen episodes")
            seen_events.update(refs)
            age = tx.cut.world_step - end
            record = (end, ref, tuple(refs))
            if age <= policy.recent_window_steps:
                recent.append(record)
            else:
                old.append(record)
        recent.sort(key=lambda item: (-item[0], item[1]))
        old.sort(key=lambda item: (item[0], item[1]))
        from collections import deque
        queues = {"recent": deque(recent), "old": deque(old)}
        primary = "recent" if policy.start_with_recent else "old"
        alternative = "old" if policy.start_with_recent else "recent"
        entries: list[ReplayAgendaEntry] = []
        while queues["recent"] or queues["old"]:
            partition = primary if queues[primary] else alternative
            end, episode_ref, events = queues[partition].popleft()
            for offset, event_ref in enumerate(events):
                entries.append(ReplayAgendaEntry(
                    unit_ref=f"replay:{len(entries):08d}",
                    episode_ref=episode_ref,
                    event_ref=event_ref,
                    temporal_partition=partition,
                    event_offset=offset,
                ))
            primary, alternative = alternative, primary
        self._entries = tuple(entries)
        self.policy_version = policy.version
        self.consolidation_id = tx.id
        self.batch_digest = tx.batch_digest
        self.source_candidate_digest = tx.candidate_digest
        self.digest = sha256_hex(canonical_causal_bytes({
            "id": tx.id, "batch": tx.batch_digest, "candidate": tx.candidate_digest,
            "policy": {"version": policy.version, "window": policy.recent_window_steps,
                       "recent_first": policy.start_with_recent},
            "entries": [entry.as_dict() for entry in entries],
        }))

    @property
    def entries(self) -> tuple[ReplayAgendaEntry, ...]:
        return self._entries

    def as_pass_plan(self) -> ConsolidationPassPlan:
        """Prepare explicit per-event UC units, not execute a semantic replay."""
        return ConsolidationPassPlan(
            consolidation_id=self.consolidation_id,
            pass_name="interleaved_replay",
            algorithm_version=self.policy_version,
            batch_digest=self.batch_digest,
            source_candidate_digest=self.source_candidate_digest,
            units=tuple(ConsolidationUnit(
                unit_ref=item.unit_ref,
                operation="episode_replay",
                episode_refs=(item.episode_ref,),
                data={
                    "event_ref": item.event_ref,
                    "event_offset": item.event_offset,
                    "temporal_partition": item.temporal_partition,
                    "agenda_digest": self.digest,
                },
            ) for item in self._entries),
        )


class ReplayAgendaBudgetError(ValueError):
    """No unpaid agenda preparation, and no unvalidated empty replay."""


def build_charged_replay_agenda(*, tx: ConsolidationTransaction,
                                policy: ReplayAgendaPolicy,
                                budget: ConsolidationWorkBudget) -> InterleavedReplayAgenda:
    """Charge P-42 per examined frozen episode BEFORE preparing the agenda.

    This currently requires the whole batch to fit one sleep work slot; a
    resumable agenda-construction cursor is still necessary for large batches.
    The future owner must charge work to *construct* higher-level hypotheses
    separately, rather than calling this scheduling helper for free.
    """
    if tx.status != "active" or tx.cursor != PASSES.index("interleaved_replay"):
        raise ValueError("replay agenda needs an active second pass")
    policy.validate()
    if budget.open_world_step is None or budget.active_period_ref is None:
        raise ValueError("replay agenda requires a sleeping work slot")
    if "replay_agenda_scan" not in budget.config.operation_costs:
        raise ValueError("versioned P-42 replay agenda scan price missing")
    if not tx.batch:
        raise ReplayAgendaBudgetError("no lived episode to replay")
    receipt = budget.charge(operation="replay_agenda_scan", count=len(tx.batch))
    if not receipt.accepted:
        raise ReplayAgendaBudgetError("replay agenda preparation suspended: " + str(receipt.reason))
    return InterleavedReplayAgenda(tx=tx, policy=policy)
