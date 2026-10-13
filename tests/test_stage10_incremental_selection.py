"""Independent regression tests: paid per-sleep-step chunks and exact frozen ranking."""
import unittest

from i0.modules.consolidation_budget import ConsolidationBudgetConfig, ConsolidationWorkBudget
from i0.modules.consolidation_batch import BatchSelectionPolicy, ConsolidationBatchSelector
from i0.modules.consolidation_incremental_scan import IncrementalChargedSelection
from i0.modules.consolidation_transaction import ConsolidationCut


class FakeEpisode:
    def __init__(self, i):
        self.data = {
            "id": f"episode:{i}", "start_t_monde":i+1, "end_t_monde":i+1,
            "event_refs":[f"event:{i}"], "boundary_type":"length",
            "active_goal_ref":None, "body_start":None, "body_end":None,
            "cumulative_reward":float(i%3),"surprise":float(i%2),
            "linked_previous_ref":None,
        }

    def as_dict(self):
        return dict(self.data)


class IncrementalPaidSelectionTests(unittest.TestCase):
    def test_resumable_scanning_pays_before_read_and_matches_full_scan(self):
        policy=BatchSelectionPolicy(
            version="issue133-incremental-test-v1", maximum_episodes=3,
            consequence_reference=1.0,surprise_reference=1.0,
            recency_window_steps=8,repetition_reference=1,
            weight_consequence=1.0,weight_surprise=1.0,weight_recency=1.0,
            weight_repetition=1.0,ageing_gain_per_step=0.1,
            scan_uc_per_episode=1,
        )
        selector=ConsolidationBatchSelector(policy)
        episodes=tuple(FakeEpisode(i) for i in range(8))
        cut=ConsolidationCut(world_step=20, journal_index=0,
                             journal_event_id="start", journal_hash="00"*32,
                             history_version="h:birth")
        cfg=ConsolidationBudgetConfig(
            version="issue133-chunked-price-v1",period_capacity_uc=3,
            step_slot_uc=3,operation_costs={"episode_scan":1},
        )
        scan=IncrementalChargedSelection(policy_version=policy.version)
        scan.begin(cut=cut,total=8,already_consolidated=("episode:2",))
        for i in range(3):
            budget=ConsolidationWorkBudget(cfg)
            budget.begin_period(period_ref=f"period:{i}",entry_step=20+i)
            budget.begin_step(world_step=20+i)
            def paid_slice(lo, hi):
                self.assertEqual(budget.consumed_step_uc, (hi - lo))
                return episodes[lo:hi]
            paid=scan.advance(
                budget=budget, episode_count=len(episodes),
                read_paid_slice=paid_slice, selector=selector)
            self.assertEqual(paid, (3,3,2)[i])
            self.assertEqual(budget.consumed_step_uc,paid)
            if i<2:
                with self.assertRaises(ValueError):
                    scan.finalize(selector=selector)
                recovered=IncrementalChargedSelection(policy_version=policy.version)
                recovered.restore_causal_state(scan.export_causal_state())
                self.assertEqual(recovered.cursor,scan.cursor)
                scan=recovered
        self.assertTrue(scan.complete)
        full=selector.select(cut=cut,episodes=episodes,
            pending_episode_refs=tuple(e.data["id"] for e in episodes if
                                       e.data["id"]!="episode:2"),
            reserved_scan_uc=8)
        actual=scan.finalize(selector=selector)
        self.assertEqual(actual.episode_refs,full.episode_refs)
        self.assertFalse(scan.active)

    def test_insufficient_budget_never_reads_episodic_payload(self):
        policy = BatchSelectionPolicy(
            version="issue133-no-unpaid-scan-v1", maximum_episodes=1,
            consequence_reference=1.0, surprise_reference=1.0,
            recency_window_steps=8, repetition_reference=1,
            weight_consequence=1.0, weight_surprise=1.0,
            weight_recency=1.0, weight_repetition=1.0,
            ageing_gain_per_step=0.1, scan_uc_per_episode=1,
        )
        cfg = ConsolidationBudgetConfig(
            version="issue133-zero-work-v1", step_slot_uc=0,
            period_capacity_uc=0, operation_costs={"episode_scan": 1})
        work = ConsolidationWorkBudget(cfg)
        work.begin_period(period_ref="period:zero", entry_step=20)
        work.begin_step(world_step=20)
        cut = ConsolidationCut(world_step=20, journal_index=0,
            journal_event_id="start", journal_hash="00"*32,
            history_version="h:birth")
        scanner = IncrementalChargedSelection(policy_version=policy.version)
        scanner.begin(cut=cut, total=2, already_consolidated=())
        reads = []
        def forbidden_read(lo, hi):
            reads.append((lo, hi))
            raise AssertionError("unpaid episodic data was accessed")
        self.assertEqual(scanner.advance(
            budget=work, episode_count=2,
            read_paid_slice=forbidden_read,
            selector=ConsolidationBatchSelector(policy)), 0)
        self.assertEqual(reads, [])
        self.assertEqual(scanner.cursor, 0)
        self.assertEqual(work.consumed_step_uc, 0)

    def test_snapshot_and_price_fail_closed(self):
        scan=IncrementalChargedSelection(policy_version="v1")
        raw=scan.export_causal_state()
        raw["total"]=4
        with self.assertRaises(ValueError):
            scan.restore_causal_state(raw)
        with self.assertRaises(ValueError):
            scan.begin(cut=ConsolidationCut(world_step=1,journal_index=0,
                journal_event_id="e",journal_hash="00"*32,
                history_version="h"),total=0,already_consolidated=())


if __name__=="__main__":
    unittest.main()
