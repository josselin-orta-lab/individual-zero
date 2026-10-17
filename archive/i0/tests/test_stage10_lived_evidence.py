"""Real hash-chain and DC-09 autobiographical custody for Stage10 cut."""
import unittest
from i0.modules.consolidation_transaction import ConsolidationTransaction,ConsolidationCut
from lab.journal import HashChainedJournal
from lab.journal_views import JournalViews
from lab.stage7_runtime import STAGE7_AUTOBIOGRAPHICAL_POLICY
from lab.consolidation_lived_evidence import FrozenLivedReplayEvidence

def fixture():
    journal=HashChainedJournal();views=JournalViews(journal=journal)
    journal.append(event_id="cmd:1",causal_event={
        "emitter":"action_control","kind":"command_experienced",
        "attempt_ref":"attempt:1","t_monde":1,
        "primitive":"boire","parameters":{},
    })
    journal.append(event_id="effect:1",causal_event={
        "emitter":"world_and_body","kind":"world_transition_experienced",
        "attempt_ref":"attempt:1","t_monde":1,
        "effects":{"drank":True},"position_after":{"x":2,"y":2},
        "body_after":{"water":50},
    })
    views.commit_autobiographical(
        t_monde=1,attempt_ref="attempt:1",
        event_refs=("cmd:1","effect:1"),policy=STAGE7_AUTOBIOGRAPHICAL_POLICY)
    anchor=journal.append(event_id="cut:3",causal_event={
        "emitter":"scheduler","kind":"step_opened","t_monde":3})
    cut=ConsolidationCut(world_step=3,journal_index=anchor.index,
                        journal_event_id=anchor.event_id,
                        journal_hash=anchor.event_hash,history_version="h:0")
    episodes={"ep:1":{"id":"ep:1","end_t_monde":1,
                      "event_refs":["cmd:1","effect:1"]}}
    tx=ConsolidationTransaction(
        consolidation_id="c1",cut=cut,episode_refs=("ep:1",),
        episode_payloads=episodes,history_candidate={"forms":{}},
    )
    return journal,views,tx

def read(journal,views,tx):
    return FrozenLivedReplayEvidence(
        journal=journal,views=views,transaction=tx,
        policies={STAGE7_AUTOBIOGRAPHICAL_POLICY.version:STAGE7_AUTOBIOGRAPHICAL_POLICY})

class LivedReplayCustodyTests(unittest.TestCase):
    def test_only_authorized_lived_projection_reaches_frozen_replay(self):
        journal,views,tx=fixture()
        selected=read(journal,views,tx)
        e=selected.episode_projections()["ep:1"]
        self.assertEqual([x["kind"] for x in e],
                         ["command_experienced","world_transition_experienced"])
        self.assertFalse(any("attempt_ref" in x for x in e))
        self.assertEqual(e[1]["effects"]["drank"],True)
        self.assertTrue(journal.verify())

    def test_postcut_events_are_not_exposed_or_replayed(self):
        journal,views,tx=fixture()
        journal.append(event_id="oracle",causal_event={
            "emitter":"bench","kind":"diagnostic","t_monde":3})
        result=read(journal,views,tx)
        self.assertNotIn("oracle",str(result.episode_projections()))

    def test_cut_digest_tamper_rejected(self):
        journal,views,tx=fixture()
        changed=ConsolidationCut(
            3,tx.cut.journal_index,tx.cut.journal_event_id,
            "a"*64,tx.cut.history_version)
        bogus=ConsolidationTransaction(
            consolidation_id="fake",cut=changed,
            episode_refs=tx.batch,episode_payloads=tx.frozen_episodes_copy(),
            history_candidate={"forms":{}},
        )
        with self.assertRaises(ValueError):
            read(journal,views,bogus)

    def test_unauthorized_episode_event_is_never_semantic_evidence(self):
        journal,views,tx=fixture()
        episode=tx.frozen_episodes_copy()
        episode["ep:1"]["event_refs"].append("cut:3")
        bogus=ConsolidationTransaction(
            consolidation_id="fake",cut=tx.cut,episode_refs=tx.batch,
            episode_payloads=episode,history_candidate={"forms":{}},
        )
        with self.assertRaises(ValueError):
            read(journal,views,bogus)

    def test_projection_is_detached_from_causal_history(self):
        journal,views,tx=fixture()
        original=read(journal,views,tx)
        detached=original.episode_projections()
        detached["ep:1"][1]["effects"]["drank"]=False
        self.assertTrue(original.episode_projections()["ep:1"][1]["effects"]["drank"])
        self.assertTrue(journal.verify())
if __name__=="__main__":unittest.main()
