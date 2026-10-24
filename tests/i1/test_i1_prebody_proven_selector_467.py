"""#467: physically applied before-body may not bypass first-person custody."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]

class PrebodySelector467(unittest.TestCase):
    def test_generated_gate(self):
        with TemporaryDirectory() as temp:
            out=Path(temp)/"gen"
            b=subprocess.run([sys.executable,str(ROOT/"scripts/build_i1_fork.py"),
                "--output",str(out)],capture_output=True,text=True)
            self.assertEqual(b.returncode,0,b.stderr)
            code=r"""
from i1lab.journal import HashChainedJournal
from i1lab.determinism import deterministic_id
from i1lab.i1_natural_prebody_policy import (
 policy_for_proven_prebody_transition as choose,LIVED_PREBODY_POLICY as NEW)
from i1lab.stage7_runtime import STAGE7_AUTOBIOGRAPHICAL_POLICY as OLD
def check(*, body_delta=0, omit_capture=False, wrong_hash=False):
 j=HashChainedJournal(); t=3; attempt="attempt:3"
 digest="a"*64
 before=dict(energy=35.,food=60.,water=70.,integrity=99.)
 def write(ref,kind,emitter,**kw):
  j.append(event_id=ref,causal_event=dict(kind=kind,emitter=emitter,
   t_monde=t,attempt_ref=attempt,**kw))
 if not omit_capture:
  write("capture", "perceptual_capture","stage3-runtime",
   data=dict(capture_t_monde=t,dual_scope_capture_schema="stage12-dual-scope-body-cue-v1",
    dual_scope_visible_body=before))
 write("admitted","command_admitted","stage3-runtime",
  data=dict(command_hash=digest if not wrong_hash else "b"*64,primitive="dormir"))
 write("cmd","command_experienced","action_control",
  command_hash=digest,primitive="dormir")
 physical=deterministic_id("journal-event-v1","world",t,attempt,digest,"transition")
 new_before=dict(before);new_before["water"]+=body_delta
 write(physical,"world_transition_experienced","world_and_body",
  body_before=new_before,body_after=dict(before),
  position_after=dict(x=1,y=1),effects={})
 return choose(journal=j,t_monde=t,attempt_ref=attempt,
  command_ref="cmd",physical_ref=physical)
assert check() is NEW
assert check(body_delta=1) is OLD
assert check(omit_capture=True) is OLD
assert check(wrong_hash=True) is OLD
print("I1_467_PREBODY_PROVEN_SELECTOR_OK")
"""
            r=subprocess.run([sys.executable,"-c",code],
                env={"PYTHONPATH":str(out)},capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stderr)
            self.assertIn("I1_467_PREBODY_PROVEN_SELECTOR_OK",r.stdout)
if __name__=="__main__":
    unittest.main()
