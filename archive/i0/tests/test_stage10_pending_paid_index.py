"""Issue 133: indexed P-42 discovery, exact ranking and fail-closed snapshots."""
import unittest
from i0.modules.consolidation_pending_index import ChargedPendingEpisodeIndex
from i0.modules.consolidation_batch import BatchSelectionPolicy, ConsolidationBatchSelector
from i0.modules.consolidation_budget import ConsolidationBudgetConfig, ConsolidationWorkBudget
from i0.modules.consolidation_transaction import ConsolidationCut


class Episode:
    def __init__(self, i):
        self.data = dict(
            id=f"episode:{i}", start_t_monde=i + 1, end_t_monde=i + 1,
            event_refs=[f"event:{i}"], boundary_type="length",
            active_goal_ref="goal:a" if i % 3 else "goal:b",
            body_start=None, body_end=None, cumulative_reward=float(i % 5),
            surprise=float(i % 7), linked_previous_ref=None)
    def as_dict(self):
        return dict(self.data)


def selector():
    return ConsolidationBatchSelector(BatchSelectionPolicy(
        version="issue133-paid-index-test-v1", maximum_episodes=4,
        consequence_reference=4.0, surprise_reference=6.0,
        recency_window_steps=8, repetition_reference=3,
        weight_consequence=1.0, weight_surprise=1.0,
        weight_recency=1.0, weight_repetition=1.0,
        ageing_gain_per_step=0.1, scan_uc_per_episode=1))


def work(limit=3):
    budget = ConsolidationWorkBudget(ConsolidationBudgetConfig(
        version="issue133-index-charge-v1", period_capacity_uc=limit,
        step_slot_uc=limit, operation_costs={
            "episode_scan": 1, "index_maintenance": 1}))
    return budget


def cut(step, version):
    return ConsolidationCut(
        world_step=step, journal_index=1,
        journal_event_id="anchor", journal_hash="00" * 32,
        history_version=version)


class PendingIndexTests(unittest.TestCase):
    def paid_run(self, index, episodes, selector_obj, step, version):
        index.begin(cut=cut(step, version), total=len(episodes))
        n = 0
        while not index.complete:
            budget = work(3)
            budget.begin_period(period_ref=f"period:{step}:{n}", entry_step=step+n)
            budget.begin_step(world_step=step+n)
            def read(lo, hi):
                self.assertGreaterEqual(budget.consumed_step_uc, hi-lo)
                return episodes[lo:hi]
            advanced = index.advance(
                budget=budget, episode_count=len(episodes),
                read_paid_slice=read, selector=selector_obj)
            self.assertGreater(advanced, 0)
            restored = ChargedPendingEpisodeIndex(policy_version=selector_obj.policy.version)
            restored.restore_causal_state(index.export_causal_state())
            index = restored
            n += 1
        return index, index.finalize(selector=selector_obj)

    def test_rank_matches_full_scan_across_commits_and_new_episodes(self):
        sel = selector()
        episodes = [Episode(i) for i in range(12)]
        index = ChargedPendingEpisodeIndex(policy_version=sel.policy.version)
        indexed, result = self.paid_run(index, episodes, sel, 20, "h:birth")
        baseline = sel.select(
            cut=cut(20, "h:birth"), episodes=episodes,
            pending_episode_refs=tuple(e.data["id"] for e in episodes),
            reserved_scan_uc=12)
        self.assertEqual(result.episode_refs, baseline.episode_refs)
        budget = work(10)
        budget.begin_period(period_ref="retire:1", entry_step=99)
        budget.begin_step(world_step=99)
        charged = indexed.charge_committed_removal(budget=budget, refs=result.episode_refs)
        self.assertIsNotNone(charged)
        indexed.acknowledge_published(
            refs=result.episode_refs, charged=charged,
            source_version="h:birth", new_version="h:one")
        self.assertEqual(indexed.pending_count, 8)
        new = episodes + [Episode(i) for i in range(12, 18)]
        indexed, result2 = self.paid_run(indexed, new, sel, 30, "h:one")
        baseline2 = sel.select(
            cut=cut(30, "h:one"), episodes=new,
            pending_episode_refs=tuple(
                e.data["id"] for e in new if e.data["id"] not in result.episode_refs),
            reserved_scan_uc=len(new))
        self.assertEqual(result2.episode_refs, baseline2.episode_refs)

    def test_zero_budget_performs_no_reads_or_changes(self):
        sel=selector()
        index=ChargedPendingEpisodeIndex(policy_version=sel.policy.version)
        index.begin(cut=cut(10,"h:0"), total=2)
        budget=work(0)
        budget.begin_period(period_ref="zero",entry_step=10)
        budget.begin_step(world_step=10)
        def forbidden(lo,hi):
            raise AssertionError("unpaid Memory read")
        before=index.export_causal_state()
        self.assertEqual(index.advance(
            budget=budget, episode_count=2,
            read_paid_slice=forbidden, selector=sel),0)
        self.assertEqual(before,index.export_causal_state())

    def test_retirement_denial_and_snapshot_fail_closed(self):
        sel=selector()
        idx=ChargedPendingEpisodeIndex(policy_version=sel.policy.version)
        idx,result=self.paid_run(idx,[Episode(0),Episode(1)],sel,10,"h:birth")
        budget=work(0)
        budget.begin_period(period_ref="zero",entry_step=12)
        budget.begin_step(world_step=12)
        self.assertIsNone(idx.charge_committed_removal(
            budget=budget,refs=result.episode_refs))
        before=idx.export_causal_state()
        bad=idx.export_causal_state()
        bad["seen_count"]=0
        with self.assertRaises(ValueError):
            idx.restore_causal_state(bad)
        self.assertEqual(before,idx.export_causal_state())


if __name__ == "__main__":
    unittest.main()
