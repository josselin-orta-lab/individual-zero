"""#495/#490: next-step waking association is closed-source only."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class ClosedWakingAdjacency(unittest.TestCase):
    def test_waking_boundaries_and_fail_closed(self):
        with TemporaryDirectory() as directory:
            out = Path(directory) / "generated"
            built = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                 "--output", str(out)],
                text=True, capture_output=True,
            )
            self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
            program = r'''
from i1.modules.memory import EpisodicMemory, Episode
def episode(n, refs):
    return Episode(id=f"episode:{n}",start_t_monde=n,end_t_monde=n,
      event_refs=tuple(refs),boundary_type="max_length",
      active_goal_ref=None,body_start=None,body_end=None,
      cumulative_reward=0.,surprise=0.,linked_previous_ref=None)
def memory(closed):
    m=object.__new__(EpisodicMemory)
    m._episodes=[episode(i,refs) for i,refs in enumerate(closed)]
    m._seen_event_refs={r for refs in closed for r in refs}
    return m
def body(e=40):
    return dict(energy=e,food=70,water=60,integrity=100)
def cmd(ref,step,primitive="dormir"):
    return dict(event_id=ref,kind="command_experienced",
       t_monde=step,primitive=primitive,parameters={})
def trans(ref,step,pre=None,after=None,site=(2,3)):
    return dict(event_id=ref,kind="world_transition_experienced",
       t_monde=step,position_after=dict(x=site[0],y=site[1]),
       body_before=body() if pre is None else pre,
       body_after=body(45) if after is None else after,effects={})
def wake(ref,step,site=(2,3),state=None):
    return dict(event_id=ref,kind="waking_body_perceived",
       t_monde=step,position=dict(x=site[0],y=site[1]),
       body_perceived=body() if state is None else state)
events=[cmd("sleep",1),trans("sleep-out",1),
        cmd("readmit",2),trans("readmit-out",2),wake("cue",2)]
m=memory([("sleep","sleep-out"),("readmit","readmit-out","cue")])
def recall(ev=events,owner=m,now=4,site=(2,3)):
    return owner.closed_sleep_site_witnesses(
        autobiography=ev,site=site,now=now)
row=recall()[0]
assert row["step"]==1
assert row["continuous_sleep_session"] is None
assert row["next_step_waking"]=={
 "step":2,"cue_event_ref":"cue","cue_episode_ref":"episode:1",
 "applied_command_ref":"readmit","applied_transition_ref":"readmit-out",
 "applied_primitive":"dormir","body_perceived":body(),
 "relation":"immediate_next_step_only"}
assert recall()[1]["next_step_waking"] is None
assert recall(now=2)==(row | {"next_step_waking":None},)
# Later closure / ingestion cannot be backfilled as personal knowledge.
assert recall(owner=memory([("sleep","sleep-out"),
                            ("readmit","readmit-out")]))[0]["next_step_waking"] is None
assert recall(owner=memory([("sleep","sleep-out"),
                            ("cue",)]))[0]["next_step_waking"] is None
assert recall(owner=memory([("sleep","sleep-out"),
                            ("readmit","readmit-out","cue"),("cue",)]))[0]["next_step_waking"] is None
# Duplicate projection, displaced site, missing/altered perceptual or
# physical prebody, non-adjacent step, and foreign command fail closed.
assert recall(ev=events+[wake("cue",2)])[0]["next_step_waking"] is None
assert recall(ev=events[:-1]+[wake("cue",2,site=(8,3))])[0]["next_step_waking"] is None
assert recall(ev=events[:-1]+[wake("cue",2,state=body(99))])[0]["next_step_waking"] is None
assert recall(ev=events[:3]+[trans("readmit-out",2,pre=body(99)),events[-1]])[0]["next_step_waking"] is None
assert recall(ev=events[:2]+[cmd("readmit",3),trans("readmit-out",3),wake("cue",3)])[0]["next_step_waking"] is None
assert recall(ev=events[:2]+[trans("readmit-out",2),wake("cue",2)])[0]["next_step_waking"] is None
# Waking perception may precede an ordinary awake action, not just sleep.
awake=[events[0],events[1],cmd("readmit",2,"avancer"),
       events[3],events[4]]
assert recall(ev=awake)[0]["next_step_waking"]["applied_primitive"]=="avancer"
# A waking cue cannot manufacture a sleep witness at another site.
assert recall(site=(8,3))==()
print("CLOSED_WAKING_ADJACENCY_OK")
'''
            result = subprocess.run(
                [sys.executable, "-c", program],
                env={"PYTHONPATH": str(out)},
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("CLOSED_WAKING_ADJACENCY_OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
