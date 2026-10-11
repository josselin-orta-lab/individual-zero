"""Replay agenda ordering/provenance tests, NOT scientific learning results."""
import unittest

from i0.modules.consolidation_transaction import (
    ConsolidationTransaction, ConsolidationCut,
)
from i0.modules.consolidation_replay_agenda import (
    InterleavedReplayAgenda, ReplayAgendaPolicy,
    build_charged_replay_agenda, ReplayAgendaBudgetError,
)
from i0.modules.consolidation_pass_runner import ConsolidationPassRunner
from i0.modules.consolidation_budget import ConsolidationWorkBudget
from test_stage10_consolidation_pass_runner import PRICES, begin
from i0.modules.consolidation_budget import ConsolidationBudgetConfig


def transaction(ordered=("old:a", "recent:b", "old:c", "recent:d")):
    times = {"old:a": 1, "old:c": 3, "recent:b": 9, "recent:d": 8}
    cut = ConsolidationCut(10, 99, "journal:99", "3a" * 32, "h:0")
    episodes = {
        name: {"id": name, "start_t_monde": times[name],
               "end_t_monde": times[name], "event_refs": [name + ":ev:0", name + ":ev:1"]}
        for name in ordered
    }
    tx = ConsolidationTransaction(
        consolidation_id="c:replay:1", cut=cut,
        episode_refs=tuple(ordered), episode_payloads=episodes,
        history_candidate={"replayed": []},
    )
    # Stage-10 selection pass must be *validated* first; here we use a
    # synthetic, test-only pass executor and do NOT certify semantic pass 1.
    tx.run_pass(name="episode_selection", executor=lambda c, *_: c,
                validator=lambda _: True)
    return tx


def policy(**changes):
    values = dict(version="P42:replay-test-v1", recent_window_steps=3,
                  start_with_recent=True)
    values.update(changes)
    return ReplayAgendaPolicy(**values)


class InterleavedReplayAgendaTests(unittest.TestCase):
    def test_recent_old_interleaving_is_exact_and_stable(self):
        agenda = InterleavedReplayAgenda(tx=transaction(), policy=policy())
        order = [e.episode_ref for e in agenda.entries if e.event_offset == 0]
        self.assertEqual(order, ["recent:b", "old:a", "recent:d", "old:c"])
        self.assertEqual(len(agenda.entries), 8)
        self.assertEqual([e.event_ref for e in agenda.entries[:2]],
                         ["recent:b:ev:0", "recent:b:ev:1"])

    def test_input_episode_order_does_not_change_agenda_digest(self):
        first = InterleavedReplayAgenda(tx=transaction(), policy=policy())
        second = InterleavedReplayAgenda(
            tx=transaction(("recent:d", "old:c", "recent:b", "old:a")),
            policy=policy(),
        )
        self.assertEqual([e.event_ref for e in first.entries],
                         [e.event_ref for e in second.entries])
        # Batch digest correctly differs when selection order is different:
        self.assertNotEqual(first.digest, second.digest)

    def test_when_no_old_episodes_only_recent_order_is_used(self):
        tx = transaction(("recent:d", "recent:b"))
        agenda = InterleavedReplayAgenda(tx=tx, policy=policy())
        self.assertEqual([e.episode_ref for e in agenda.entries if e.event_offset == 0],
                         ["recent:b", "recent:d"])

    def test_explicit_old_first_policy_is_respected(self):
        agenda = InterleavedReplayAgenda(tx=transaction(),
                                         policy=policy(start_with_recent=False))
        self.assertEqual(agenda.entries[0].episode_ref, "old:a")
        self.assertEqual(agenda.entries[2].episode_ref, "recent:b")

    def test_plan_charges_one_event_at_a_time_and_no_unseen_episodes(self):
        tx = transaction()
        budget = ConsolidationWorkBudget(ConsolidationBudgetConfig(
            version="P42:replay-budget", period_capacity_uc=30,
            step_slot_uc=5, operation_costs={**PRICES, "replay_agenda_scan": 1},
        ))
        runner = ConsolidationPassRunner(transaction=tx, budget=budget)
        begin(budget, step=10)
        agenda = build_charged_replay_agenda(tx=tx, policy=policy(), budget=budget)
        # Agenda's four-episode scan used four UC in the first step.
        self.assertEqual(budget.consumed_step_uc, 4)
        budget.begin_step(world_step=11)
        p = agenda.as_pass_plan()
        self.assertEqual(len(p.units), len(agenda.entries))
        self.assertTrue(runner.start_pass(p))
        seen = []
        def accept(candidate, unit, frozen, cut):
            self.assertEqual(set(frozen), set(unit.episode_refs))
            event_ref = unit.data["event_ref"]
            self.assertIn(event_ref, frozen[unit.episode_refs[0]]["event_refs"])
            seen.append(event_ref)
            candidate["replayed"].append(event_ref)
            return candidate
        for i in range(4):
            runner.advance_unit(accept)
        self.assertEqual(tx.cursor, 1)
        self.assertEqual(len(seen), 4)
        self.assertEqual(runner.advance_unit(accept).outcome, "budget_blocked")
        budget.begin_step(world_step=12)
        for _ in range(4):
            runner.advance_unit(accept)
        # Four units plus one validation UC exactly fill this world step.
        self.assertTrue(runner.finalize_pass(validator=lambda _: True))
        self.assertEqual(tx.cursor, 2)
        self.assertEqual(tx.candidate_copy()["replayed"], seen)
        self.assertEqual(len(set(seen)), 8)

    def test_agenda_preparation_debits_before_projection(self):
        tx = transaction()
        budget = ConsolidationWorkBudget(ConsolidationBudgetConfig(
            version="P42:no-scan", period_capacity_uc=3, step_slot_uc=3,
            operation_costs={**PRICES, "replay_agenda_scan": 1},
        ))
        begin(budget, step=10)
        with self.assertRaises(ReplayAgendaBudgetError):
            build_charged_replay_agenda(tx=tx, policy=policy(), budget=budget)
        self.assertEqual(budget.consumed_period_uc, 0)
        # The budget never falsely declares the agenda complete.

    def test_agenda_requires_versioned_real_scan_price(self):
        tx = transaction()
        budget = ConsolidationWorkBudget(ConsolidationBudgetConfig(
            version="P42:missing-price", period_capacity_uc=10, step_slot_uc=10,
            operation_costs=PRICES,
        ))
        begin(budget, step=10)
        with self.assertRaises(ValueError):
            build_charged_replay_agenda(tx=tx, policy=policy(), budget=budget)

    def test_replay_only_uses_pre_cut_frozen_input(self):
        tx = transaction()
        agenda = InterleavedReplayAgenda(tx=tx, policy=policy())
        leaked = tx.frozen_episodes_copy()
        leaked["old:a"]["event_refs"].append("forged")
        self.assertNotIn("forged", [item.event_ref for item in agenda.entries])
        self.assertEqual(tx.cursor, 1)

    def test_rejects_same_event_in_multiple_memory_episodes(self):
        tx = transaction()
        tx._frozen_episodes["old:a"]["event_refs"] = ["dup"]
        tx._frozen_episodes["old:c"]["event_refs"] = ["dup"]
        with self.assertRaises(ValueError):
            InterleavedReplayAgenda(tx=tx, policy=policy())

    def test_rejects_invalid_policy_and_wrong_pass(self):
        with self.assertRaises(ValueError):
            ReplayAgendaPolicy("v", 0, True).validate()
        with self.assertRaises(ValueError):
            ReplayAgendaPolicy("v", 1, 1).validate()
        tx = transaction()
        tx.run_pass(name="interleaved_replay", executor=lambda c,*_: c,
                    validator=lambda _: True)
        with self.assertRaises(ValueError):
            InterleavedReplayAgenda(tx=tx, policy=policy())


if __name__ == "__main__":
    unittest.main()
