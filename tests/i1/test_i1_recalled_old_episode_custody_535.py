"""#535: an old personally recalled closed episode can expose bounded source refs."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class RecalledEpisodeCustody535(unittest.TestCase):
    def test_generated_i1_old_recalled_episode_is_bounded_and_authentic(self):
        with TemporaryDirectory() as folder:
            out = Path(folder) / "generated"
            build = subprocess.run([sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                                    "--output", str(out)], capture_output=True, text=True)
            self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
            code = r"""
from i1.modules.memory import EpisodicMemory, Episode, MemoryConfig
def config():
    return MemoryConfig(
        version="i1-535-test", prediction_error_multiplier=1.,
        max_episode_steps=8, link_delta_steps=0, recall_threshold=0.,
        recall_weight_recency=1., recall_weight_importance=0.,
        recall_weight_relevance=0., recall_recency_scale_steps=8,
        contribution_ttl_steps=2)
def ep(i):
    return Episode(id=f"episode:{i}", start_t_monde=i+1,
        end_t_monde=i+1, event_refs=(f"c{i}",f"t{i}"),
        boundary_type="max_length", active_goal_ref=None,
        body_start=None, body_end=None, cumulative_reward=0.,
        surprise=0., linked_previous_ref=None)
m = EpisodicMemory(config(), atomic_world_step_length_boundary=True)
m._episodes = [ep(i) for i in range(34)]
m._seen_event_refs = {ref for e in m._episodes for ref in e.event_refs}
m._episode_sequence = 34
m._episode_ids_dense = True
m._closed_ref_owners = {}
for episode in m._episodes:
    m._claim_closed_refs(m._closed_ref_owners, episode)
m._last_recalled_ref = "episode:0"
assert {"c0","t0"}.isdisjoint(m.closed_sleep_recall_source_refs())
assert m.closed_last_recalled_episode_source_refs(now=35) == frozenset({"c0","t0"})
# Merely knowing another episode string is not a paid recall.
m._last_recalled_ref = None
assert not m.closed_last_recalled_episode_source_refs(now=35)
m._last_recalled_ref = "episode:0"
assert not m.closed_last_recalled_episode_source_refs(now=1)
try:\n    m.closed_last_recalled_episode_source_refs(now=0)\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError("invalid time accepted")
state = m.export_causal_state()
cold = EpisodicMemory(config(), atomic_world_step_length_boundary=True)
cold.restore_causal_state(state)
assert cold.export_causal_state() == state
assert cold.closed_last_recalled_episode_source_refs(now=35) == frozenset({"c0","t0"})
# Duplicate ownership elsewhere is no longer an authentic unique witness.
cold._episodes.append(Episode(id="episode:34",start_t_monde=35,
    end_t_monde=35,event_refs=("c0","t34"),boundary_type="max_length",
    active_goal_ref=None,body_start=None,body_end=None,
    cumulative_reward=0.,surprise=0.,linked_previous_ref=None))
cold._seen_event_refs.add("t34")
cold._claim_closed_refs(cold._closed_ref_owners,cold._episodes[-1])
assert not cold.closed_last_recalled_episode_source_refs(now=36)
# An oversized episode cannot become a cost-free historical selection.
cold._episodes.pop()
cold._last_recalled_ref="episode:2"
large = Episode(id="episode:2",start_t_monde=3,end_t_monde=3,
    event_refs=tuple(f"big:{i}" for i in range(65)),
    boundary_type="max_length",active_goal_ref=None,body_start=None,
    body_end=None,cumulative_reward=0.,surprise=0.,linked_previous_ref=None)
cold._episodes[2]=large
assert not cold.closed_last_recalled_episode_source_refs(now=36)
# A restored noncanonical historical order cannot claim ordinal lookup.
bad = dict(state, episodes=list(reversed(state["episodes"])))
unusual=EpisodicMemory(config(), atomic_world_step_length_boundary=True)
unusual.restore_causal_state(bad)
assert not unusual.closed_last_recalled_episode_source_refs(now=35)
print("I1_535_OLD_RECALLED_EPISODE_CUSTODY_OK")
"""
            run = subprocess.run([sys.executable, "-c", code],
                                 env={"PYTHONPATH": str(out)},
                                 capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            self.assertIn("I1_535_OLD_RECALLED_EPISODE_CUSTODY_OK", run.stdout)


if __name__ == "__main__":
    unittest.main()
