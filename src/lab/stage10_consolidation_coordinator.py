"""Stage-10 sleeping-slot consolidation coordinator, with one canonical slot.

One simulated step opens exactly one priced P-42 slot. All semantic evidence
is verified against the pre-cut autobiographical journal, and never includes
later events. The active work plan, incremental replay agenda, suspension, and
private six-pass candidate remain invisible until the separate atomic commit.
"""
from __future__ import annotations

from copy import deepcopy
from json import loads
from typing import Mapping
from .determinism import canonical_causal_bytes, sha256_hex
from typing import Callable

from i0.modules.consolidation_batch import (
    BatchSelectionPolicy, ConsolidationBatchSelector, BatchSelectionBudgetError,
)
from i0.modules.consolidation_budget import (
    ConsolidationWorkBudget, select_batch_with_charged_work,
)
from i0.modules.consolidation_pass_runner import ConsolidationPassRunner
from i0.modules.consolidation_replay_builder import IncrementalReplayAgendaBuilder
from i0.modules.consolidation_semantics import LivedSixPassAlgorithm, SemanticPassPolicy
from i0.modules.consolidation_transaction import (
    ConsolidationTransaction, ConsolidationCut, ConsolidationSlot, PASSES,
)
from .consolidation_lived_evidence import FrozenLivedReplayEvidence
from .consolidation_publication import SlowHistory
from .determinism import deterministic_id
from .journal import HashChainedJournal
from .journal_views import JournalViews, AutobiographicalPolicy

EventSink = Callable[[str, dict[str, object]], None]


class Stage10ConsolidationCoordinator:
    """Scheduler-owned control facet; no independent cognitive knowledge."""

    owner_id = "consolidation_driver"
    schema = "stage10-consolidation-driver-v1"

    def __init__(
        self, *,
        journal: HashChainedJournal,
        views: JournalViews,
        memory,
        history: SlowHistory,
        slot: ConsolidationSlot,
        budget: ConsolidationWorkBudget,
        batch_policy: BatchSelectionPolicy,
        semantic_policy: SemanticPassPolicy,
        projection_policies: dict[str, AutobiographicalPolicy],
    ):
        if not isinstance(journal, HashChainedJournal) or not isinstance(views, JournalViews):
            raise TypeError("real technical journal and autobiographical view required")
        if not isinstance(history, SlowHistory) or not isinstance(slot, ConsolidationSlot):
            raise TypeError("single canonical consolidated history/transaction owner required")
        batch_policy.validate()
        semantic_policy.validate()
        if not projection_policies or any(
            key != value.version for key, value in projection_policies.items()
        ):
            raise ValueError("exact versioned DC-09 projection policies required")
        self.journal, self.views, self.memory = journal, views, memory
        self.history, self.slot, self.budget = history, slot, budget
        self.selector = ConsolidationBatchSelector(batch_policy)
        self.semantic_policy = semantic_policy
        self.projection_policies = dict(projection_policies)
        self._runner: ConsolidationPassRunner | None = None
        self._algorithm: LivedSixPassAlgorithm | None = None
        self._builder: IncrementalReplayAgendaBuilder | None = None
        self._evidence_digest: str | None = None

    @property
    def active_pass(self) -> str | None:
        return None if self._runner is None else self._runner.active_pass

    @property
    def done(self) -> bool:
        tx = self.slot.current
        return bool(tx is not None and tx.status == "active"
                    and tx.cursor == len(PASSES))

    def _construct(self) -> None:
        tx = self.slot.current
        if tx is None:
            self._runner = self._algorithm = self._builder = None
            self._evidence_digest = None
            return
        if tx.status != "active":
            raise ValueError("construct private semantic state only after resume")
        lived = FrozenLivedReplayEvidence(
            journal=self.journal, views=self.views, transaction=tx,
            policies=self.projection_policies,
        )
        if self._evidence_digest is not None and lived.digest != self._evidence_digest:
            raise ValueError("frozen autobiographical projection changed after cut")
        self._evidence_digest = lived.digest
        self._algorithm = LivedSixPassAlgorithm(
            transaction=tx, evidence=lived, policy=self.semantic_policy,
        )
        self._runner = ConsolidationPassRunner(
            transaction=tx, budget=self.budget,
        )

    def start_if_eligible(
        self, *, world_step: int, consolidation_pressure: float,
        threshold: float, on_event: EventSink,
        owner_form_snapshot: Mapping[str, object] | None = None,
    ) -> bool:
        if self.slot.current is not None:
            return False
        if (type(world_step) is not int or world_step < 1
                or not 0 <= consolidation_pressure <= 1
                or not 0 <= threshold <= 1
                or self.budget.open_world_step != world_step):
            raise ValueError("consolidation start requires physical sleep slot")
        if consolidation_pressure < threshold:
            return False
        committed = set(self.history.read_committed().get("consolidated_episode_refs", []))
        available = tuple(ep for ep in self.memory.episodes if ep.end_t_monde < world_step)
        pending = tuple(ep.id for ep in available if ep.id not in committed)
        if not pending:
            return False
        head = self.journal.entries[-1]
        cut = ConsolidationCut(
            world_step=world_step, journal_index=head.index,
            journal_event_id=head.event_id, journal_hash=head.event_hash,
            history_version=self.history.current_version,
        )
        try:
            batch = select_batch_with_charged_work(
                budget=self.budget, selector=self.selector,
                cut=cut, episodes=available, pending_episode_refs=pending,
            )
        except BatchSelectionBudgetError:
            # Work cannot execute without paying the complete scan.
            on_event("stage10_consolidation_batch_deferred", {
                "reason":"insufficient_scan_uc", "world_step":world_step,
                "examined_episode_count":len(available),
            })
            return False
        if not batch.episode_refs:
            return False
        candidate = self.history.read_committed()
        if owner_form_snapshot is not None:
            required = {"value_needs","metacognition_health","perception","causal_model"}
            if not isinstance(owner_form_snapshot, Mapping) or not required.issubset(owner_form_snapshot):
                raise ValueError("cut-point forms require all canonical owner snapshots")
            # Canonical owner snapshots may contain tuples (for example
            # Causal Model witnesses); the frozen private transaction accepts
            # exact JSON trees. Normalize without changing their information.
            forms = loads(canonical_causal_bytes(dict(owner_form_snapshot)).decode("utf-8"))
            candidate["forms"] = forms
            candidate["form_source"] = "owner_active_causal_cut"
            candidate["form_cut_digest"] = sha256_hex(canonical_causal_bytes(forms))
        tx = ConsolidationTransaction(
            consolidation_id=deterministic_id(
                "stage10-consolidation-v1",batch.digest,self.history.current_version,
            ),
            cut=cut, episode_refs=batch.episode_refs,
            episode_payloads=batch.episode_payloads_copy(),
            history_candidate=candidate,
        )
        self.slot.begin(tx)
        self._construct()
        on_event("stage10_consolidation_started", {
            "consolidation_id":tx.id,"cut_index":cut.journal_index,
            "cut_hash":cut.journal_hash,"source_history":cut.history_version,
            "batch_digest":tx.batch_digest,"batch":list(tx.batch),
            "selection_version":batch.policy_version,
            "scan_uc":batch.scan_uc,
        })
        return True

    def resume(self, *, on_event: EventSink) -> bool:
        tx = self.slot.current
        if tx is None or tx.status != "suspended":
            return False
        tx.resume()
        self._construct()
        on_event("stage10_consolidation_resumed", {
            "consolidation_id":tx.id,"completed_passes":list(tx.completed_passes),
            "cursor":tx.cursor,"source_version":tx.cut.history_version,
        })
        return True

    def run_slot(self, *, on_event: EventSink) -> int:
        if self.budget.open_world_step is None:
            raise ValueError("consolidation work outside physical sleep step")
        tx = self.slot.current
        if tx is None:
            return 0
        if tx.status != "active":
            raise ValueError("cannot work on suspended transaction")
        if self._runner is None or self._algorithm is None:
            self._construct()
        budget = self.budget
        runner = self._runner
        algorithm = self._algorithm
        done_units = 0
        # Every mutation requires a strictly positive, charged logical UC.
        # Bound attempts even when a caller supplied malformed pricing.
        max_steps = budget.config.step_slot_uc + len(PASSES) * 3 + 1
        for _ in range(max_steps):
            if tx.cursor == len(PASSES):
                return done_units
            if runner.active_pass is None:
                if PASSES[tx.cursor] == "interleaved_replay":
                    if self._builder is None:
                        self._builder = IncrementalReplayAgendaBuilder(
                            transaction=tx, policy=self.semantic_policy.replay,
                            budget=budget,
                        )
                    if self._builder.status != "ready":
                        state = self._builder.advance()
                        if state.outcome == "budget_blocked":
                            return done_units
                        done_units += int(state.charged_uc > 0)
                        on_event("stage10_consolidation_work_charged",{
                            "operation":state.operation,"charged_uc":state.charged_uc,
                            "pass":PASSES[tx.cursor],"cursor":tx.cursor,
                            "unit_cursor":state.accepted_operations,
                        })
                        continue
                    plan = algorithm.make_plan(
                        budget=budget, replay_plan=self._builder.as_pass_plan(),
                    )
                else:
                    plan = algorithm.make_plan(budget=budget)
                    if plan is None:
                        return done_units
                if not runner.start_pass(plan):
                    return done_units
                on_event("stage10_consolidation_pass_opened", {
                    "pass":PASSES[tx.cursor], "units":len(plan.units),
                    "consolidation_id":tx.id,
                })
            assert runner.active_pass is not None
            # If all units were processed in a previous sleeping slot,
            # validation is its own separately charged work.
            if runner.unit_cursor == len(runner._plan.units):
                if not runner.finalize_pass(algorithm.validate):
                    return done_units
                on_event("stage10_consolidation_pass_validated", {
                    "pass":PASSES[tx.cursor-1], "cursor":tx.cursor,
                    "candidate_digest":tx.candidate_digest,
                })
                self._builder = None
                continue
            result = runner.advance_unit(algorithm.handle)
            if result.outcome == "budget_blocked":
                return done_units
            done_units += int(result.charged_uc > 0)
            on_event("stage10_consolidation_work_charged", {
                "operation":runner._plan.units[result.unit_cursor-1].operation,
                "charged_uc":result.charged_uc,"pass":result.pass_name,
                "unit_cursor":result.unit_cursor,
            })
        raise RuntimeError("P-42 invariant: too many charged operations for one step")

    def interrupt_for_waking(self, *, on_event: EventSink) -> bool:
        tx = self.slot.current
        if tx is None or tx.status != "active":
            return False
        if self._runner is not None:
            self._runner.interrupt_for_waking()
        else:
            tx.interrupt()
        if self._builder is not None:
            self._builder.cancel_for_waking()
        self._builder = None
        self._runner = self._algorithm = None
        on_event("stage10_consolidation_suspended",{
            "consolidation_id":tx.id,"completed_passes":list(tx.completed_passes),
            "next_pass":None if tx.cursor==len(PASSES) else PASSES[tx.cursor],
        })
        return True

    def committed(self) -> None:
        """Release orphaned private engine state only after a real receipt."""
        if self.slot.current is not None:
            raise ValueError("cannot retire uncommitted private work")
        self._runner = self._algorithm = self._builder = None
        self._evidence_digest = None

    def export_causal_state(self):
        tx = self.slot.current
        raw = {
            "schema":self.schema,
            "batch_policy_version":self.selector.policy.version,
            "semantic_policy_version":self.semantic_policy.version,
            "transaction_id":None if tx is None else tx.id,
            "evidence_digest":self._evidence_digest,
            "runner":None if self._runner is None else self._runner.export_causal_state(),
            "builder":None if self._builder is None else self._builder.export_causal_state(),
        }
        return deepcopy(raw)

    def restore_causal_state(self, state):
        if (type(state) is not dict
                or set(state) != {
                    "schema","batch_policy_version","semantic_policy_version",
                    "transaction_id","evidence_digest","runner","builder",
                } or state["schema"] != self.schema
                or state["batch_policy_version"] != self.selector.policy.version
                or state["semantic_policy_version"] != self.semantic_policy.version):
            raise ValueError("incompatible consolidation driver snapshot")
        tx = self.slot.current
        if state["transaction_id"] != (None if tx is None else tx.id):
            raise ValueError("driver snapshot mismatches the one canonical transaction")
        self._runner = self._algorithm = self._builder = None
        self._evidence_digest = state["evidence_digest"]
        if tx is None:
            if state["runner"] is not None or state["builder"] is not None:
                raise ValueError("snapshot has dangling consolidation subowner")
            return
        if tx.status == "suspended":
            if state["runner"] is not None or state["builder"] is not None:
                raise ValueError("suspended transaction must have no active work plan")
            return
        self._construct()
        if state["runner"] is not None:
            self._runner.restore_causal_state(state["runner"])
        if state["builder"] is not None:
            self._builder = IncrementalReplayAgendaBuilder(
                transaction=tx, policy=self.semantic_policy.replay,
                budget=self.budget,
            )
            self._builder.restore_causal_state(state["builder"])
