"""#549: owner isolation, exact version, detached forms, and bounded paid cost."""
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class PublishedHRecall549(unittest.TestCase):
    def test_generated_owner_projection_is_detached_and_bounded(self):
        with TemporaryDirectory() as tmp:
            generated=Path(tmp)/"generated"
            build=subprocess.run(
                [sys.executable,str(ROOT/"scripts/build_i1_fork.py"),
                 "--output",str(generated)],cwd=ROOT,capture_output=True,
                text=True,timeout=90)
            self.assertEqual(build.returncode,0,build.stdout+build.stderr)
            code=r"""
from copy import deepcopy
from i1lab.consolidation_publication import SlowHistory
from i1.modules.paid_action_consolidation import (
    validate_published_fragments, merge_paid_fragments, record_paid_source,
)
def body(e):return dict(energy=e,food=60,water=50,integrity=90)
command=dict(event_id="c1",kind="command_experienced",t_monde=1,
             primitive="attendre",parameters={})
result=dict(event_id="t1",kind="world_transition_experienced",t_monde=1,
            position_after={"x":2,"y":3},body_before=body(20),
            body_after=body(19),effects={})
sources=[]
for i,event in enumerate((command,result)):
    sources=record_paid_source(sources,episode_ref="e1",
       event_offset=i,event=event,before_step=10)
fragments=merge_paid_fragments(sources,[],cut_step=10)
assert validate_published_fragments(fragments)
history=SlowHistory(birth_version="h:published:synthetic",birth_state={
  "forms":{"private_sentinel":{"secret":"do_not_expose"}},
  "consolidated_episode_refs":["e1"],
  "lived_action_fragments":deepcopy(fragments)})
projected=history.read_published_action_fragments(before_step=11)
assert projected["history_version"]=="h:published:synthetic"
assert projected["fragments"]==fragments
assert "forms" not in projected and "secret" not in str(projected)
projected["fragments"][0]["body_after"]["energy"]=-50
assert history.read_published_action_fragments(before_step=11)["fragments"]==fragments
assert history.read_published_action_fragments(before_step=9)["fragments"]==[]
bad=history.export_causal_state()
bad["current_state"]["lived_action_fragments"][0]["observed_steps"]=20
history.restore_causal_state(bad)
try:
    history.read_published_action_fragments(before_step=11)
    raise AssertionError("malformed h read accepted")
except ValueError:
    pass
print("I1_549_DETACHED_H_RECALL_OK")
"""
            env=os.environ.copy()
            env["PYTHONPATH"]=os.pathsep.join((str(generated),str(ROOT/"src")))
            out=subprocess.run([sys.executable,"-c",code],cwd=ROOT,env=env,
                capture_output=True,text=True,timeout=90)
            self.assertEqual(out.returncode,0,out.stdout+"\n"+out.stderr)
            self.assertIn("I1_549_DETACHED_H_RECALL_OK",out.stdout)


if __name__=="__main__":
    unittest.main()
