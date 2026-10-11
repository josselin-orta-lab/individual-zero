"""Stage-10 incremental *agenda* tests. No semantic learning or sleep admission."""
from __future__ import annotations

import json
import unittest
from copy import deepcopy

from lab.determinism import canonical_causal_bytes, sha256_hex
from i0.modules.consolidation_budget import ConsolidationBudgetConfig, ConsolidationWorkBudget
from i0.modules.consolidation_transaction import ConsolidationCut, ConsolidationTransaction
from i0.modules.consolidation_replay_agenda import InterleavedReplayAgenda, ReplayAgendaPolicy
from i0.modules.consolidation_replay_builder import IncrementalReplayAgendaBuilder


PRICES = {
    "replay_agenda_scan": 1,
    "replay_agenda_event": 1,
    "replay_agenda_compare": 1,
    "replay_agenda_insert": 1,
    "replay_agenda_emit": 1,
    "pass_prepare": 1,
    "pass_validate": 1,
    "episode_replay": 1,
}
TIMES = {"old:a": 1, "old:c": 3, "recent:b": 9, "recent:d": 8}


def transaction(refs=None, *, events_per_episode=2):
    if refs is None:
        refs = ("old:a", "recent:b", "old:c", "recent:d")
    cut = ConsolidationCut(10, 99, "journal:99", "3a" * 32, "h:0")
    episodes = {
        ref: {"id": ref, "start_t_monde": TIMES[ref], "end_t_monde": TIMES[ref],
              "event_refs": [f"{ref}:event:{n}" for n in range(events_per_episode)]}
        for ref in refs
    }
    tx = ConsolidationTransaction(
        consolidation_id="c:incremental", cut=cut, episode_refs=tuple(refs),
        episode_payloads=episodes, history_candidate={"learned": []},
    )
    # Synthetic pass-one checkpoint used only to enter the normative pass-two
    # boundary; this does not demonstrate a real selection semantic algorithm.
    tx.run_pass(name="episode_selection", executor=lambda candidate, *_: candidate,
                validator=lambda _: True)
    return tx


def policy(*, old_first=False):
    return ReplayAgendaPolicy(version="P42:replay-builder-test-v1",
                              recent_window_steps=3,
                              start_with_recent=not old_first)


def open_budget(*, price=None, step_slot=3, period=1000, ref="sleep:1", first_step=10):
    ledger = ConsolidationWorkBudget(ConsolidationBudgetConfig(
        version="P42:test-build-v1", period_capacity_uc=period,
        step_slot_uc=step_slot, operation_costs=price or PRICES,
    ))
    ledger.begin_period(period_ref=ref, entry_step=first_step)
    ledger.begin_step(world_step=first_step)
    return ledger


def drain(builder, *, max_steps=1000):
    """Simulate successive sleeping world steps without changing the world."""
    steps = 0
    accepted = []
    while steps < max_steps:
        before = builder.budget.consumed_period_uc
        outcome = builder.advance()
        if outcome.outcome == "ready":
            if outcome.operation is not None:
                accepted.append(outcome.operation)
            return accepted
        if outcome.outcome == "budget_blocked":
            assert outcome.charged_uc == 0
            assert builder.budget.consumed_period_uc == before
            if outcome.blocked_reason == "period_capacity":
                raise AssertionError("insufficient complete-sleep-period capacity")
            next_step = builder.budget.open_world_step + 1
            builder.budget.begin_step(world_step=next_step)
            steps += 1
            continue
        assert outcome.operation is not None
        accepted.append(outcome.operation)
    raise AssertionError("work did not finish in bounded simulated steps")


class IncrementalReplayBuilderTests(unittest.TestCase):
    def test_very_small_slots_produce_exact_reference_agenda_and_plan(self):
        tx = transaction()
        pol = policy()
        reference = InterleavedReplayAgenda(tx=tx, policy=pol)
        budget = open_budget(step_slot=2)
        builder = IncrementalReplayAgendaBuilder(transaction=tx, policy=pol, budget=budget)
        accepted = drain(builder)
        self.assertEqual([e.as_dict() for e in builder.entries],
                         [e.as_dict() for e in reference.entries])
        self.assertEqual(builder.as_pass_plan().export(), reference.as_pass_plan().export())
        self.assertGreater(budget.open_world_step, 10)
        self.assertEqual(len(accepted), builder.charged_operations)
        self.assertEqual(budget.consumed_period_uc, len(accepted))
        self.assertEqual(tx.cursor, 1)
        self.assertEqual(tx.candidate_copy(), {"learned": []})

    def test_old_first_and_permuted_frozen_batches(self):
        for refs in [
            ("recent:d", "old:c", "old:a", "recent:b"),
            ("recent:b", "recent:d"),
            ("old:a", "old:c"),
            ("old:c", "recent:d", "old:a", "recent:b"),
        ]:
            for old_first in (False, True):
                with self.subTest(refs=refs, old_first=old_first):
                    tx = transaction(refs)
                    pol = policy(old_first=old_first)
                    expected = InterleavedReplayAgenda(tx=tx, policy=pol)
                    budget = open_budget(step_slot=3)
                    builder = IncrementalReplayAgendaBuilder(
                        transaction=tx, policy=pol, budget=budget,
                    )
                    drain(builder)
                    self.assertEqual(builder.as_pass_plan().export(), expected.as_pass_plan().export())

    def test_each_event_and_comparison_is_individually_charged(self):
        tx = transaction(events_per_episode=4)
        budget = open_budget(step_slot=4)
        builder = IncrementalReplayAgendaBuilder(transaction=tx, policy=policy(), budget=budget)
        steps = drain(builder)
        self.assertEqual(steps.count("replay_agenda_scan"), 4)
        self.assertEqual(steps.count("replay_agenda_event"), 16)
        self.assertEqual(steps.count("replay_agenda_insert"), 4)
        self.assertEqual(steps.count("replay_agenda_emit"), 16)
        self.assertEqual(budget.consumed_period_uc, len(steps))
        self.assertGreater(steps.count("replay_agenda_compare"), 0)

    def test_no_private_preparation_visible_before_last_paid_emission(self):
        tx = transaction()
        budget = open_budget(step_slot=3)
        builder = IncrementalReplayAgendaBuilder(transaction=tx, policy=policy(), budget=budget)
        for _ in range(12):
            result = builder.advance()
            if result.outcome == "budget_blocked":
                budget.begin_step(world_step=budget.open_world_step + 1)
                continue
            self.assertEqual(tx.cursor, 1)
            self.assertEqual(tx.candidate_copy(), {"learned": []})
            with self.assertRaises(ValueError):
                builder.as_pass_plan()
            with self.assertRaises(ValueError):
                _ = builder.entries

    def test_progress_blocked_with_no_uc_and_no_work(self):
        tx = transaction()
        budget = open_budget(step_slot=1)
        builder = IncrementalReplayAgendaBuilder(transaction=tx, policy=policy(), budget=budget)
        self.assertEqual(builder.advance().charged_uc, 1)
        before = deepcopy(builder.export_causal_state())
        result = builder.advance()
        self.assertEqual(result.outcome, "budget_blocked")
        self.assertEqual(result.blocked_reason, "step_slot")
        self.assertEqual(result.charged_uc, 0)
        self.assertEqual(builder.export_causal_state(), before)
        budget.begin_step(world_step=11)
        self.assertEqual(builder.advance().outcome, "progressed")

    def test_snapshot_restoration_technical_replay_at_every_unit(self):
        tx = transaction(events_per_episode=3)
        budget = open_budget(step_slot=3)
        builder = IncrementalReplayAgendaBuilder(transaction=tx, policy=policy(), budget=budget)
        for _ in range(150):
            raw = json.loads(json.dumps(builder.export_causal_state()))
            before = budget.export_causal_state()
            restored = IncrementalReplayAgendaBuilder(
                transaction=tx, policy=policy(), budget=budget,
            )
            restored.restore_causal_state(raw)
            self.assertEqual(restored.export_causal_state(), raw)
            self.assertEqual(budget.export_causal_state(), before)
            builder = restored
            result = builder.advance()
            if result.outcome == "budget_blocked":
                budget.begin_step(world_step=budget.open_world_step + 1)
            elif result.outcome == "ready":
                self.assertEqual(builder.as_pass_plan().export(),
                                 InterleavedReplayAgenda(tx=tx, policy=policy()).as_pass_plan().export())
                break
        else:
            self.fail("snapshot sequence never completed")

    def test_restore_rejects_tampered_recomputed_digest_and_remains_atomic(self):
        tx = transaction()
        budget = open_budget(step_slot=10)
        builder = IncrementalReplayAgendaBuilder(transaction=tx, policy=policy(), budget=budget)
        for _ in range(5):
            builder.advance()
        baseline = builder.export_causal_state()
        for edit in (
            lambda s: s["history"].append("replay_agenda_emit"),
            lambda s: s["engine"].update({"episode_cursor": 99}),
            lambda s: s["engine"]["seen_events"].append("oracle:lie"),
            lambda s: s.update({"candidate_digest": "a" * 64}),
            lambda s: s["policy"].update({"start_with_recent": False}),
            lambda s: s["engine"].update({"phase": "ready"}),
        ):
            forgery = deepcopy(baseline)
            edit(forgery)
            without = {k: v for k, v in forgery.items() if k != "digest"}
            forgery["digest"] = sha256_hex(canonical_causal_bytes(without))
            with self.subTest(forgery=forgery["engine"].get("phase")):
                with self.assertRaises(ValueError):
                    builder.restore_causal_state(forgery)
                self.assertEqual(builder.export_causal_state(), baseline)

    def test_restore_rejects_different_budget_lineage_even_if_counters_equal(self):
        tx = transaction()
        budget = open_budget(step_slot=8)
        builder = IncrementalReplayAgendaBuilder(transaction=tx, policy=policy(), budget=budget)
        builder.advance()
        saved = builder.export_causal_state()
        altered = budget.export_causal_state()
        altered["used_period_refs"] = sorted(altered["used_period_refs"] + ["sleep:phantom"])
        budget.restore_causal_state(altered)
        with self.assertRaises(ValueError):
            builder.restore_causal_state(saved)
        self.assertEqual(builder.charged_operations, 1)

    def test_snapshot_restore_rejects_unfunded_history(self):
        tx = transaction()
        budget = open_budget(step_slot=10)
        builder = IncrementalReplayAgendaBuilder(transaction=tx, policy=policy(), budget=budget)
        state = builder.export_causal_state()
        state["history"] = ["replay_agenda_scan"]
        state["digest"] = sha256_hex(canonical_causal_bytes({k:v for k,v in state.items() if k != "digest"}))
        with self.assertRaises(ValueError):
            builder.restore_causal_state(state)

    def test_wake_cancels_all_unvalidated_work_without_refunding_uc(self):
        tx = transaction()
        budget = open_budget(step_slot=6)
        builder = IncrementalReplayAgendaBuilder(transaction=tx, policy=policy(), budget=budget)
        for _ in range(4):
            builder.advance()
        spent = budget.consumed_period_uc
        builder.cancel_for_waking()
        tx.interrupt()
        self.assertEqual(tx.cursor, 1)
        self.assertEqual(tx.status, "suspended")
        self.assertEqual(budget.consumed_period_uc, spent)
        self.assertEqual(builder.charged_operations, 0)
        with self.assertRaises(ValueError):
            builder.advance()
        budget.end_period()
        budget.begin_period(period_ref="sleep:2", entry_step=15)
        budget.begin_step(world_step=15)
        tx.resume()
        fresh = IncrementalReplayAgendaBuilder(transaction=tx, policy=policy(), budget=budget)
        drain(fresh)
        self.assertEqual(fresh.as_pass_plan().export(),
                         InterleavedReplayAgenda(tx=tx, policy=policy()).as_pass_plan().export())

    def test_cross_episode_physical_event_alias_fails_after_paid_event_check(self):
        tx = transaction()
        tx._frozen_episodes["old:a"]["event_refs"][0] = "reused-physical-event"
        tx._frozen_episodes["old:c"]["event_refs"][0] = "reused-physical-event"
        budget = open_budget(step_slot=5)
        builder = IncrementalReplayAgendaBuilder(transaction=tx, policy=policy(), budget=budget)
        with self.assertRaises(ValueError):
            drain(builder)
        self.assertGreater(budget.consumed_period_uc, 1)
        self.assertEqual(tx.cursor, 1)
        self.assertEqual(tx.candidate_copy(), {"learned": []})

    def test_bad_episode_is_not_silently_filled_from_oracle(self):
        tx = transaction()
        tx._frozen_episodes["old:a"]["event_refs"] = []
        budget = open_budget(step_slot=5)
        builder = IncrementalReplayAgendaBuilder(transaction=tx, policy=policy(), budget=budget)
        with self.assertRaises(ValueError):
            builder.advance()
        self.assertEqual(budget.consumed_period_uc, 1)
        self.assertEqual(tx.candidate_copy(), {"learned": []})

    def test_requires_explicit_affordable_cost_schedule_and_active_sleep(self):
        tx = transaction()
        for costs, slot in (
            ({k: v for k, v in PRICES.items() if k != "replay_agenda_event"}, 3),
            ({**PRICES, "replay_agenda_insert": 4}, 3),
        ):
            with self.subTest(costs=costs):
                budget = open_budget(price=costs, step_slot=slot)
                with self.assertRaises(ValueError):
                    IncrementalReplayAgendaBuilder(transaction=tx, policy=policy(), budget=budget)
        budget = ConsolidationWorkBudget(ConsolidationBudgetConfig(
            version="P42:nosleep", period_capacity_uc=10, step_slot_uc=3,
            operation_costs=PRICES))
        with self.assertRaises(ValueError):
            IncrementalReplayAgendaBuilder(transaction=tx, policy=policy(), budget=budget)

    def test_restore_rejects_forged_step_receipts_even_with_recomputed_digest(self):
        tx = transaction()
        budget = open_budget(step_slot=2)
        builder = IncrementalReplayAgendaBuilder(transaction=tx, policy=policy(), budget=budget)
        for _ in range(4):
            result = builder.advance()
            if result.outcome == "budget_blocked":
                budget.begin_step(world_step=budget.open_world_step + 1)
        snapshot = builder.export_causal_state()
        for alteration in (
            lambda v: v["history"][0].update({"world_step": 9}),
            lambda v: v["history"][1].update({"world_step": 12}),
            lambda v: v["history"][0].update({"charged_uc": 0}),
            lambda v: v["history"][0].update({"period_ref": "sleep:forged"}),
            lambda v: v["history"][2].update({"world_step": 10}),
        ):
            state = deepcopy(snapshot)
            alteration(state)
            state["digest"] = sha256_hex(canonical_causal_bytes({k:v for k,v in state.items() if k != "digest"}))
            with self.assertRaises(ValueError):
                builder.restore_causal_state(state)
            self.assertEqual(builder.export_causal_state(), snapshot)

    def test_failed_evidence_is_fatal_once_and_snapshot_is_reconstructable(self):
        tx = transaction()
        tx._frozen_episodes["old:a"]["event_refs"][0] = "cafe\u0301"
        budget = open_budget(step_slot=5)
        builder = IncrementalReplayAgendaBuilder(transaction=tx, policy=policy(), budget=budget)
        builder.advance()  # paid scan, no oracle
        spent = budget.consumed_period_uc
        with self.assertRaises(ValueError):
            builder.advance()  # paid invalid event
        self.assertEqual(budget.consumed_period_uc, spent + 1)
        self.assertEqual(builder.status, "invalid")
        saved = json.loads(json.dumps(builder.export_causal_state()))
        with self.assertRaises(ValueError):
            builder.advance()  # cannot repeatedly charge the same bad event
        self.assertEqual(budget.consumed_period_uc, spent + 1)
        restored = IncrementalReplayAgendaBuilder(transaction=tx, policy=policy(), budget=budget)
        restored.restore_causal_state(saved)
        self.assertEqual(restored.export_causal_state(), saved)
        self.assertEqual(tx.cursor, 1)

    def test_cancelled_builder_snapshot_survives_waking_and_budget_close(self):
        tx = transaction()
        budget = open_budget(step_slot=5)
        builder = IncrementalReplayAgendaBuilder(transaction=tx, policy=policy(), budget=budget)
        builder.advance()
        builder.cancel_for_waking()
        tx.interrupt()
        budget.end_period()
        saved = json.loads(json.dumps(builder.export_causal_state()))
        self.assertEqual(builder.status, "cancelled")
        builder.restore_causal_state(saved)
        self.assertEqual(builder.export_causal_state(), saved)
        with self.assertRaises(ValueError):
            builder.advance()

    def test_rejects_empty_batch_and_non_second_pass(self):
        tx = transaction()
        tx.run_pass(name="interleaved_replay", executor=lambda c,*_: c, validator=lambda _: True)
        with self.assertRaises(ValueError):
            IncrementalReplayAgendaBuilder(transaction=tx, policy=policy(), budget=open_budget())


if __name__ == "__main__":
    unittest.main()
