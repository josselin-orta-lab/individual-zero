"""Scheduler-driven P-42 consolidation from actual pre-cut autobiographical Memory.

The coordinator never decides to sleep or accesses WorldBody. These scenarios
simulate already-open, Action Control-admitted sleeping work slots in isolation.
"""
import unittest
from types import SimpleNamespace

from i0.modules.memory import Episode
from i0.modules.consolidation_transaction import ConsolidationSlot
from i0.modules.consolidation_budget import ConsolidationBudgetConfig, ConsolidationWorkBudget
from i0.modules.consolidation_batch import BatchSelectionPolicy
from i0.modules.consolidation_semantics import SemanticPassPolicy
from i0.modules.consolidation_replay_agenda import ReplayAgendaPolicy
from lab.journal import HashChainedJournal
from lab.journal_views import JournalViews
from lab.stage7_runtime import STAGE7_AUTOBIOGRAPHICAL_POLICY
from lab.consolidation_publication import SlowHistory
from lab.stage10_consolidation_coordinator import Stage10ConsolidationCoordinator


def setup():
    journal = HashChainedJournal()
    views = JournalViews(journal=journal)
    journal.append(event_id="physical:command:1",causal_event={
        "kind":"command_experienced","emitter":"action_control",
        "t_monde":1,"attempt_ref":"step:1",
        "primitive":"boire","parameters":{},
    })
    journal.append(event_id="physical:transition:1",causal_event={
        "kind":"world_transition_experienced","emitter":"world_and_body",
        "t_monde":1,"attempt_ref":"step:1",
        "position_after":{"x":2,"y":2},
        "body_after":{"energy":48,"food":57,"water":62,"integrity":100},
        "effects":{"drank":True},
    })
    views.commit_autobiographical(
        t_monde=1,attempt_ref="step:1",
        event_refs=("physical:command:1","physical:transition:1"),
        policy=STAGE7_AUTOBIOGRAPHICAL_POLICY,
    )
    episode=Episode(
        id="ep:1",start_t_monde=1,end_t_monde=1,
        event_refs=("physical:command:1","physical:transition:1"),
        boundary_type="goal_change",active_goal_ref=None,
        body_start={"energy":50,"food":60,"water":40,"integrity":100},
        body_end={"energy":48,"food":57,"water":62,"integrity":100},
        cumulative_reward=0.5,surprise=0.2,linked_previous_ref=None,
    )
    slot=ConsolidationSlot()
    budget=ConsolidationWorkBudget(ConsolidationBudgetConfig(
        version="sleep-budget:test",period_capacity_uc=100,
        step_slot_uc=6,operation_costs={
            "episode_scan":1,"semantic_plan_build":1,
            "pass_prepare":1,"pass_validate":1,"episode_replay":1,
            "rule_extraction":1,"skill_compilation":1,
            "kappa_recalibration":1,"index_maintenance":1,
            "replay_agenda_scan":1,"replay_agenda_event":1,
            "replay_agenda_compare":1,"replay_agenda_insert":1,
            "replay_agenda_emit":1,
        },
    ))
    history=SlowHistory(birth_version="h:test",birth_state={
        "forms":{}, "consolidated_episode_refs":[],
        "hypotheses":[], "procedural":[], "indices":{},
    })
    obj=Stage10ConsolidationCoordinator(
        journal=journal,views=views,
        memory=SimpleNamespace(episodes=(episode,)),
        history=history,slot=slot,budget=budget,
        batch_policy=BatchSelectionPolicy(
            version="batch:test",maximum_episodes=1,
            consequence_reference=1,surprise_reference=1,
            recency_window_steps=10,repetition_reference=2,
            weight_consequence=1,weight_surprise=1,
            weight_recency=1,weight_repetition=1,
            ageing_gain_per_step=0.01,scan_uc_per_episode=1,
        ),
        semantic_policy=SemanticPassPolicy(
            version="semantic:test",replay=ReplayAgendaPolicy(
                version="replay:test",recent_window_steps=10,
                start_with_recent=True,
            ),
            skill_success_threshold=2,nearby_context_radius=1,
            rule_expiry_steps=30,
        ),
        projection_policies={
            STAGE7_AUTOBIOGRAPHICAL_POLICY.version:STAGE7_AUTOBIOGRAPHICAL_POLICY,
        },
    )
    return journal,history,slot,budget,obj


class SleepingConsolidationIntegrationTests(unittest.TestCase):
    def test_six_private_passes_respect_step_uc_and_wake_checkpoint(self):
        journal,history,slot,budget,driver=setup()
        messages=[]
        step=[3]
        def send(kind,data):
            journal.append(event_id="stage10:"+str(len(messages)),causal_event={
                "emitter":"scheduler","kind":kind,"t_monde":step[0],
                "data":data,
            })
            messages.append(kind)
        budget.begin_period(period_ref="sleep:3",entry_step=3)
        for step[0] in (3,4,5):
            budget.begin_step(world_step=step[0])
            if step[0] == 3:
                started=driver.start_if_eligible(
                    world_step=3,consolidation_pressure=1.0,
                    threshold=0.5,on_event=send,
                )
                self.assertTrue(started)
            driver.run_slot(on_event=send)
            self.assertLessEqual(budget.consumed_step_uc,6)
        tx=slot.current
        self.assertIsNotNone(tx)
        self.assertEqual(history.current_version,"h:test")
        progress=tx.cursor
        self.assertGreater(progress,0)
        driver.interrupt_for_waking(on_event=send)
        self.assertEqual(tx.status,"suspended")
        self.assertEqual(tx.cursor,progress)
        budget.end_period()
        budget.begin_period(period_ref="sleep:9",entry_step=9)
        for step[0] in range(9,29):
            budget.begin_step(world_step=step[0])
            if step[0] == 9:
                self.assertTrue(driver.resume(on_event=send))
            driver.run_slot(on_event=send)
            self.assertLessEqual(budget.consumed_step_uc,6)
            if driver.done:
                break
        self.assertTrue(driver.done)
        result=tx.validated_candidate(validator=driver._algorithm.validate)
        self.assertEqual(result["consolidated_episode_refs"],["ep:1"])
        self.assertEqual(len(result["hypotheses"]),1)
        self.assertEqual(result["hypotheses"][0]["status"],"hypothese_causale")
        self.assertEqual(history.current_version,"h:test")
        self.assertTrue(journal.verify())
        self.assertIn("stage10_consolidation_pass_validated",messages)
        self.assertIn("stage10_consolidation_suspended",messages)
        self.assertIn("stage10_consolidation_resumed",messages)

    def test_active_midpass_snapshot_roundtrip(self):
        journal,history,slot,budget,driver=setup()
        budget.begin_period(period_ref="sleep:3",entry_step=3)
        budget.begin_step(world_step=3)
        def send(kind,data):
            journal.append(event_id="stage10:"+str(len(journal.entries)),causal_event={
                "kind":kind,"emitter":"scheduler","t_monde":3,"data":data,
            })
        driver.start_if_eligible(world_step=3,consolidation_pressure=1,
                                 threshold=0.5,on_event=send)
        driver.run_slot(on_event=send)
        frozen=driver.export_causal_state()
        driver.restore_causal_state(frozen)
        self.assertEqual(driver.export_causal_state(),frozen)

    def test_absent_memory_cannot_start_a_fabricated_batch(self):
        journal,history,slot,budget,driver=setup()
        driver.memory.episodes=()
        budget.begin_period(period_ref="sleep:3",entry_step=3)
        budget.begin_step(world_step=3)
        self.assertFalse(driver.start_if_eligible(
            world_step=3,consolidation_pressure=1,threshold=0.5,
            on_event=lambda *_:None,
        ))
        self.assertIsNone(slot.current)
        self.assertEqual(history.current_version,"h:test")

if __name__=="__main__":
    unittest.main()
