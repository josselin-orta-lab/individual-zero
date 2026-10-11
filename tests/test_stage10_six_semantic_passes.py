"""Six private Stage-10 semantic passes with real DC-09, P-42 and snapshots."""
import unittest

from i0.modules.consolidation_transaction import (
    ConsolidationTransaction,ConsolidationCut,PASSES,
)
from i0.modules.consolidation_budget import (
    ConsolidationBudgetConfig,ConsolidationWorkBudget,
)
from i0.modules.consolidation_pass_runner import ConsolidationPassRunner
from i0.modules.consolidation_replay_agenda import (
    ReplayAgendaPolicy,build_charged_replay_agenda,
)
from i0.modules.consolidation_semantics import (
    LivedSixPassAlgorithm,SemanticPassPolicy,
)
from lab.journal import HashChainedJournal
from lab.journal_views import JournalViews
from lab.stage7_runtime import STAGE7_AUTOBIOGRAPHICAL_POLICY
from lab.consolidation_lived_evidence import FrozenLivedReplayEvidence


def inputs():
    j=HashChainedJournal();v=JournalViews(journal=j)
    j.append(event_id="command:1",causal_event={
        "kind":"command_experienced","emitter":"action_control",
        "attempt_ref":"a:1","t_monde":1,
        "primitive":"boire","parameters":{},
    })
    j.append(event_id="transition:1",causal_event={
        "kind":"world_transition_experienced","emitter":"world_and_body",
        "attempt_ref":"a:1","t_monde":1,
        "effects":{"drank":True},"position_after":{"x":2,"y":2},
        "body_after":{"water":48},
    })
    v.commit_autobiographical(
        t_monde=1,attempt_ref="a:1",event_refs=("command:1","transition:1"),
        policy=STAGE7_AUTOBIOGRAPHICAL_POLICY,
    )
    e=j.append(event_id="cut:3",causal_event={
        "kind":"step_opened","emitter":"scheduler","t_monde":3,
    })
    cut=ConsolidationCut(world_step=3,journal_index=e.index,
                        journal_event_id=e.event_id,journal_hash=e.event_hash,
                        history_version="h:0")
    tx=ConsolidationTransaction(
        consolidation_id="cons:test",cut=cut,
        episode_refs=("ep:1",),
        episode_payloads={"ep:1":{
            "id":"ep:1","end_t_monde":1,
            "event_refs":["command:1","transition:1"]}},
        history_candidate={
            "forms":{}, "consolidated_episode_refs":[],
            "hypotheses":[], "procedural":[], "indices":{},
        },
    )
    receipt=FrozenLivedReplayEvidence(
        journal=j,views=v,transaction=tx,policies={
            STAGE7_AUTOBIOGRAPHICAL_POLICY.version:STAGE7_AUTOBIOGRAPHICAL_POLICY,
        },
    )
    config=ConsolidationBudgetConfig(
        version="p42:semantic:test",period_capacity_uc=120,step_slot_uc=12,
        operation_costs={
            "semantic_plan_build":1,"pass_prepare":1,"pass_validate":1,
            "episode_scan":1,"episode_replay":1,"rule_extraction":1,
            "skill_compilation":1,"kappa_recalibration":1,
            "index_maintenance":1,"replay_agenda_scan":1,
        },
    )
    budget=ConsolidationWorkBudget(config)
    budget.begin_period(period_ref="sleep-period:3",entry_step=3)
    algorithm=LivedSixPassAlgorithm(
        transaction=tx,evidence=receipt,
        policy=SemanticPassPolicy(
            version="semantic-passes-test-v1",
            replay=ReplayAgendaPolicy(
                version="agenda:test",recent_window_steps=2,
                start_with_recent=True,
            ),
            skill_success_threshold=2,nearby_context_radius=1,
            rule_expiry_steps=12,
        ),
    )
    return j,tx,budget,algorithm


def pass_once(tx,budget,algorithm,runner,step):
    budget.begin_step(world_step=step)
    if PASSES[tx.cursor]=="interleaved_replay":
        replay=build_charged_replay_agenda(
            tx=tx,policy=algorithm.policy.replay,budget=budget,
        )
        plan=algorithm.make_plan(budget=budget,replay_plan=replay.as_pass_plan())
    else:
        plan=algorithm.make_plan(budget=budget)
    assert plan is not None
    assert runner.start_pass(plan)
    for _ in plan.units:
        advance=runner.advance_unit(algorithm.handle)
        assert advance.outcome in {"processed","pass_ready"}
    assert runner.finalize_pass(algorithm.validate)


class SixPassSemanticTests(unittest.TestCase):
    def test_six_passes_do_real_lived_replay_without_unsupported_certainty(self):
        journal,tx,budget,algo=inputs()
        runner=ConsolidationPassRunner(transaction=tx,budget=budget)
        for i in range(6):
            pass_once(tx,budget,algo,runner,3+i)
            self.assertEqual(tx.cursor,i+1)
        result=tx.validated_candidate(validator=algo.validate)
        self.assertEqual(result["selected_episode_refs"],["ep:1"])
        self.assertEqual(result["replayed_event_refs"],
                         ["command:1","transition:1"])
        self.assertEqual(len(result["hypotheses"]),1)
        rule=result["hypotheses"][0]
        self.assertEqual(rule["status"],"hypothese_causale")
        self.assertFalse(rule["validated_for_safety"])
        self.assertEqual(rule["source_event_refs"],
                         ["command:1","transition:1"])
        self.assertEqual(result["procedural"],[])
        self.assertEqual(result["consolidated_episode_refs"],["ep:1"])
        self.assertEqual(result["kappa_recalibration_status"],
                         "no_new_independent_verifications")
        self.assertTrue(journal.verify())

    def test_interruption_discards_only_unvalidated_private_work(self):
        journal,tx,budget,algo=inputs()
        runner=ConsolidationPassRunner(transaction=tx,budget=budget)
        pass_once(tx,budget,algo,runner,3)
        baseline=tx.candidate_digest
        budget.begin_step(world_step=4)
        agenda=build_charged_replay_agenda(
            tx=tx,policy=algo.policy.replay,budget=budget,
        )
        plan=algo.make_plan(budget=budget,replay_plan=agenda.as_pass_plan())
        self.assertTrue(runner.start_pass(plan))
        runner.advance_unit(algo.handle)
        runner.interrupt_for_waking()
        self.assertEqual(tx.status,"suspended")
        self.assertEqual(tx.cursor,1)
        self.assertEqual(tx.candidate_digest,baseline)
        budget.end_period()
        budget.begin_period(period_ref="sleep-period:9",entry_step=9)
        runner.resume_after_sleep_entry()
        budget.begin_step(world_step=9)
        replay=build_charged_replay_agenda(
            tx=tx,policy=algo.policy.replay,budget=budget,
        )
        new=algo.make_plan(budget=budget,replay_plan=replay.as_pass_plan())
        self.assertTrue(runner.start_pass(new))
        self.assertEqual(runner.unit_cursor,0)

    def test_cannot_pretend_unverified_event_mapping_is_lived_evidence(self):
        _,tx,_,_=inputs()
        with self.assertRaises(ValueError):
            LivedSixPassAlgorithm(
                transaction=tx,evidence={"ep:1":[]},
                policy=SemanticPassPolicy(
                    version="x",replay=ReplayAgendaPolicy(
                        version="x",recent_window_steps=1,start_with_recent=True),
                    skill_success_threshold=2,nearby_context_radius=1,
                    rule_expiry_steps=4,
                ),
            )

if __name__=="__main__":unittest.main()
