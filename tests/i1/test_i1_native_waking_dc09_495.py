"""#495: only a physically applied, first-person postwake cue is committed."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class NativeWakingDC09495(unittest.TestCase):
    def test_generated_waking_commit_and_rejections(self):
        with TemporaryDirectory() as temp:
            build_dir = Path(temp)/"generated"
            built = subprocess.run(
                [sys.executable,str(ROOT/"scripts/build_i1_fork.py"),
                 "--output",str(build_dir)],capture_output=True,text=True)
            self.assertEqual(built.returncode,0,built.stdout+built.stderr)
            program = r"""
from i1lab.journal import HashChainedJournal
from i1lab.journal_views import JournalViews,AutobiographicalPolicy
from i1lab.i1_natural_prebody_policy import (
 LIVED_PREBODY_POLICY, LIVED_WAKING_BODY_POLICY,
 DORMANT_WAKING_BODY_POLICY)
from i1lab.stage7_runtime import STAGE7_AUTOBIOGRAPHICAL_POLICY as OLD
from i1lab.determinism import deterministic_id
from i1lab.world import Command,command_digest

def fixture(*,wake=True,broken=False):
 journal=HashChainedJournal()
 view=JournalViews(journal=journal)
 view.enable_i1_prebody_at_birth()
 t=4;attempt="attempt:4"
 digest=command_digest(Command("dormir"))
 body=dict(energy=40.,food=70.,water=60.,integrity=100.)
 def add(ref,kind,emitter,**kw):
  journal.append(event_id=ref,causal_event={
   "emitter":emitter,"kind":kind,"t_monde":t,
   "attempt_ref":attempt,**kw})
 add("reduced","stage10_reduced_capture","stage4-runtime",
     data=dict(full_cognitive_perception=False))
 if wake:
  add("wake","stage10_sleep_woke","stage4-runtime",data=dict(reason="alert"))
 add("capture","perceptual_capture","stage3-runtime",
     data=dict(capture_t_monde=t,
      dual_scope_capture_schema="stage12-dual-scope-body-cue-v1",
      position=dict(x=2,y=3),dual_scope_visible_body=body))
 add("admission","command_admitted","stage3-runtime",
     data=dict(command_hash=digest,primitive="dormir"))
 c=deterministic_id("journal-event-v1","action_control",t,attempt,digest,"send")
 add(c,"command_experienced","action_control",
     command_hash=digest,primitive="dormir",parameters={})
 p=deterministic_id("journal-event-v1","world",t,attempt,digest,"transition")
 prior=dict(body)
 if broken:prior["water"]=59.
 add(p,"world_transition_experienced","world_and_body",
     position_after=dict(x=2,y=3),body_before=prior,
     body_after=body,effects={})
 commitment=view.commit_autobiographical(
  t_monde=t,attempt_ref=attempt,event_refs=(c,p),policy=OLD)
 policies={v.version:v for v in (OLD,LIVED_PREBODY_POLICY,
                                   LIVED_WAKING_BODY_POLICY)}
 return journal,view,commitment,view.autobiographical(policies=policies)

j,view,commit,rows=fixture()
wake=[r for r in rows if r["kind"]=="waking_body_perceived"]
assert len(wake)==1,rows
assert wake[0]["body_perceived"]==dict(
 energy=40.,food=70.,water=60.,integrity=100.)
assert set(wake[0])=={
 "event_id","kind","t_monde","position","body_perceived"}
assert len(commit.event_refs)==3 and commit.filter_version==LIVED_WAKING_BODY_POLICY.version
assert "capture" not in view._committed_source_refs
assert wake[0]["event_id"] in view._committed_source_refs
assert all(r.get("kind")!="stage10_sleep_woke" for r in rows)
for kwargs in (dict(wake=False),dict(broken=True)):
 _,_,c,r=fixture(**kwargs)
 assert not any(row["kind"]=="waking_body_perceived" for row in r)
 assert c.filter_version!=LIVED_WAKING_BODY_POLICY.version
# A caller-provided policy must not commit a made-up cue event even if it
# uses the registered sensory kind. No technical wake oracle is accepted.
bad=HashChainedJournal()
v=JournalViews(journal=bad)
bad.append(event_id="fake",causal_event={
 "kind":"waking_body_perceived","emitter":"i1-first-person-wake",
 "t_monde":1,"attempt_ref":"attempt:1",
 "position":dict(x=1,y=1),
 "body_perceived":dict(energy=50,food=50,water=50,integrity=100)})
try:
 v.commit_autobiographical(t_monde=1,attempt_ref="attempt:1",
   event_refs=("fake",),policy=DORMANT_WAKING_BODY_POLICY)
except ValueError:pass
else:raise AssertionError("forged postwake sensory commit succeeded")
print("I1_495_NATIVE_WAKE_COMMIT_OK")
"""
            done = subprocess.run([sys.executable,"-c",program],
                                  env={"PYTHONPATH":str(build_dir)},
                                  text=True,capture_output=True)
            self.assertEqual(done.returncode,0,done.stdout+done.stderr)
            self.assertIn("I1_495_NATIVE_WAKE_COMMIT_OK",done.stdout)


if __name__=="__main__":
    unittest.main()
