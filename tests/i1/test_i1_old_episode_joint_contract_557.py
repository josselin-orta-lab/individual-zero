"""#557 L1 prerequisite: indexed DC-09 and Memory agree on an OLD owned episode.

Synthetic owner fixtures, NOT a claim of natural birth, paid recall or L2.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class OldEpisodeJoinedCustody557(unittest.TestCase):
    def test_generated_i1_owner_and_index_joint_contract(self):
        with TemporaryDirectory() as temporary:
            target = Path(temporary) / "generated"
            built = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                 "--output", str(target)],
                cwd=ROOT, capture_output=True, text=True, timeout=90,
            )
            self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
            program = r"""
from i1.modules.memory import EpisodicMemory, Episode, MemoryConfig
from i1lab.journal import HashChainedJournal
from i1lab.journal_views import JournalViews
from i1lab.stage7_runtime import STAGE7_AUTOBIOGRAPHICAL_POLICY as P

cfg=MemoryConfig(version="joint-557",prediction_error_multiplier=1.,
    max_episode_steps=8,link_delta_steps=0,recall_threshold=0.,
    recall_weight_recency=1.,recall_weight_importance=0.,
    recall_weight_relevance=0.,recall_recency_scale_steps=8,
    contribution_ttl_steps=2)
memory=EpisodicMemory(cfg,atomic_world_step_length_boundary=True)
journal=HashChainedJournal()
views=JournalViews(journal=journal)
episodes=[]
for i in range(34):
    t=i+1
    attempt=f"attempt:{t}"
    cmd=f"cmd:{t}"
    transition=f"transition:{t}"
    journal.append(event_id=cmd,causal_event=dict(
        kind="command_experienced",t_monde=t,attempt_ref=attempt,
        primitive="collecter",parameters={"target":"wood"}))
    journal.append(event_id=transition,causal_event=dict(
        kind="world_transition_experienced",t_monde=t,attempt_ref=attempt,
        position_after={"x":2,"y":3},
        body_after={"energy":30,"food":60,"water":50,"integrity":90},
        effects={"collected":{"kind":"wood","quantity":0}}))
    views.commit_autobiographical(t_monde=t,attempt_ref=attempt,
        event_refs=(cmd,transition),policy=P)
    episodes.append(Episode(id=f"episode:{i}",start_t_monde=t,
        end_t_monde=t,event_refs=(cmd,transition),
        boundary_type="max_length",active_goal_ref=None,
        body_start=None,body_end=None,cumulative_reward=0.,
        surprise=0.,linked_previous_ref=None))
memory._episodes=episodes
memory._episode_sequence=34
memory._episode_ids_dense=True
memory._seen_event_refs={ref for ep in episodes for ref in ep.event_refs}
memory._closed_ref_owners={}
for ep in episodes: memory._claim_closed_refs(memory._closed_ref_owners,ep)
assert not {"cmd:1","transition:1"}.intersection(
    memory.closed_sleep_recall_source_refs())
assert memory.closed_last_recalled_episode_source_refs(now=35)==frozenset()
memory._last_recalled_ref="episode:0"
refs=memory.closed_last_recalled_episode_source_refs(now=35)
assert refs==frozenset({"cmd:1","transition:1"})
selected=views.selected_committed_autobiography(
    policies={P.version:P},selected_event_refs=refs)
assert len(selected)==2
assert {row["event_id"] for row in selected}==refs
assert memory.closed_applied_action_witnesses(
    autobiography=selected,now=35)==()
witnesses=memory.closed_applied_action_witnesses(
    autobiography=selected,now=35,recalled_episode_refs=refs)
assert len(witnesses)==1
w=witnesses[0]
assert w["primitive"]=="collecter"
assert w["source_episode_refs"]==("episode:0",)
assert set(w["source_event_refs"])==refs
assert w["observed_effects"]["collected"]["quantity"]==0
assert w["causal_attribution"] is False
assert w["decision_evidence"] is False
assert views.selected_committed_autobiography(
    policies={P.version:P},selected_event_refs=refs)==selected
cold=JournalViews(journal=journal)
assert cold.selected_committed_autobiography(
    policies={P.version:P},selected_event_refs=refs)==selected
image=memory.export_causal_state()
restored=EpisodicMemory(cfg,atomic_world_step_length_boundary=True)
restored.restore_causal_state(image)
assert restored.closed_last_recalled_episode_source_refs(now=35)==refs
assert restored.closed_applied_action_witnesses(
    autobiography=selected,now=35,recalled_episode_refs=refs)==witnesses
for bad in (frozenset(),frozenset({"cmd:1"}),
            frozenset({"cmd:1","transition:1","uncommitted"})):
    try:
        memory.closed_applied_action_witnesses(
            autobiography=selected,now=35,recalled_episode_refs=bad)
    except ValueError:
        pass
    else:
        raise AssertionError("unauthorized Memory selection")
memory._last_recalled_ref=None
try:
    memory.closed_applied_action_witnesses(
        autobiography=selected,now=35,recalled_episode_refs=refs)
except ValueError:
    pass
else:
    raise AssertionError("nonrecalled episode accepted")
print("I1_557_JOINED_OLD_EPISODE_L1_OK")
"""
            run = subprocess.run(
                [sys.executable, "-c", program],
                cwd=ROOT, capture_output=True, text=True, timeout=90,
                env={"PYTHONPATH": str(target)},
            )
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            self.assertIn("I1_557_JOINED_OLD_EPISODE_L1_OK", run.stdout)


if __name__ == "__main__":
    unittest.main()
