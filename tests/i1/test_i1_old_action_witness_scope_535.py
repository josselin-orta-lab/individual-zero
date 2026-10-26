"""#535 L2 prerequisite: a closed old episode's real effect is owner-scoped."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class OldActionWitnessScope535(unittest.TestCase):
    def test_generated_memory_rejects_unrecalled_or_spoofed_old_sources(self):
        with TemporaryDirectory() as folder:
            out = Path(folder)/"generated"
            built = subprocess.run(
                [sys.executable,str(ROOT/"scripts/build_i1_fork.py"),
                 "--output",str(out)],capture_output=True,text=True)
            self.assertEqual(built.returncode,0,built.stdout+built.stderr)
            script=r"""
from i1.modules.memory import EpisodicMemory, Episode, MemoryConfig
config=MemoryConfig(version="scope-535",prediction_error_multiplier=1.0,
    max_episode_steps=8,link_delta_steps=0,recall_threshold=0.0,
    recall_weight_recency=1.0,recall_weight_importance=0.0,
    recall_weight_relevance=0.0,recall_recency_scale_steps=8,
    contribution_ttl_steps=2)
m=EpisodicMemory(config,atomic_world_step_length_boundary=True)
m._episodes=[Episode(id=f"episode:{i}",start_t_monde=i+1,
    end_t_monde=i+1,event_refs=(f"c{i}",f"t{i}"),
    boundary_type="max_length",active_goal_ref=None,body_start=None,
    body_end=None,cumulative_reward=0.,surprise=0.,
    linked_previous_ref=None) for i in range(34)]
m._seen_event_refs={ref for ep in m._episodes for ref in ep.event_refs}
m._episode_ids_dense=True
m._closed_ref_owners={}
for ep in m._episodes: m._claim_closed_refs(m._closed_ref_owners,ep)
m._last_recalled_ref="episode:0"
refs=m.closed_last_recalled_episode_source_refs(now=35)
assert refs==frozenset(("c0","t0"))
a=[dict(event_id="c0",kind="command_experienced",t_monde=1,
        primitive="collecter",parameters={"target":"wood"}),
   dict(event_id="t0",kind="world_transition_experienced",t_monde=1,
        position_after={"x":2,"y":3},
        body_after={"energy":30,"food":60,"water":50,"integrity":90},
        effects={"collected":{"kind":"wood","quantity":0}})]
assert m.closed_applied_action_witnesses(autobiography=a,now=35)==()
rows=m.closed_applied_action_witnesses(
    autobiography=a,now=35,recalled_episode_refs=refs)
assert len(rows)==1
assert rows[0]["observed_effects"]["collected"]["quantity"]==0
assert rows[0]["source_episode_refs"]==("episode:0",)
assert rows[0]["decision_evidence"] is False
for wrong in (frozenset(),frozenset({"c0"}),
              frozenset({"c0","t0","madeup"})):
    try: m.closed_applied_action_witnesses(
        autobiography=a,now=35,recalled_episode_refs=wrong)
    except ValueError: pass
    else: raise AssertionError("unauthorized source accepted")
m._last_recalled_ref=None
try: m.closed_applied_action_witnesses(
    autobiography=a,now=35,recalled_episode_refs=refs)
except ValueError: pass
else: raise AssertionError("stale recall accepted")
print("I1_535_OLD_ACTION_WITNESS_SCOPE_OK")
"""
            p=subprocess.run([sys.executable,"-c",script],
                env={"PYTHONPATH":str(out)},capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stdout+p.stderr)
            self.assertIn("I1_535_OLD_ACTION_WITNESS_SCOPE_OK",p.stdout)


if __name__=="__main__":
    unittest.main()
