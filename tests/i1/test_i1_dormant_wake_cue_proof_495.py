"""Dormant L1 postwake cue must never authorize technical wake knowledge."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]

class WakeCueEligibility495(unittest.TestCase):
    def test_generated_gate_and_negative_receipts(self):
        with TemporaryDirectory() as tmp:
            out=Path(tmp)/"gen"
            built=subprocess.run([sys.executable,str(ROOT/"scripts/build_i1_fork.py"),
                                  "--output",str(out)],capture_output=True,text=True)
            self.assertEqual(built.returncode,0,built.stderr)
            script=r"""
from i1lab.journal import HashChainedJournal
from i1lab.world import Command,command_digest
from i1lab.determinism import deterministic_id
from i1lab.i1_natural_prebody_policy import (
 attested_postwake_perceptual_body as choose,
 candidate_versioned_waking_perception as versioned,
)

def check(*, omit=None, cross=False, corrupt=False, reverse=False):
 j=HashChainedJournal()
 t=4;attempt="attempt:4";digest=command_digest(Command("dormir"))
 body=dict(energy=40.,food=70.,water=60.,integrity=100.)
 def add(ref,kind,emitter,**kw):
  j.append(event_id=ref,causal_event=dict(
   kind=kind,emitter=emitter,t_monde=t,
   attempt_ref=("attempt:other" if cross and kind=="stage10_sleep_woke" else attempt),
   **kw))
 def reduced():
  add("reduced","stage10_reduced_capture","stage4-runtime",
      data=dict(full_cognitive_perception=False))
 def woke():
  add("wake","stage10_sleep_woke","stage4-runtime",data=dict(reason="alert"))
 for kind,fn in (("reduced",reduced),("wake",woke)):
  if kind!=omit:
   fn()
 if reverse:
  return choose(journal=j,t_monde=t,attempt_ref=attempt,
                command_ref="no-command",physical_ref="none")
 if omit!="capture":
  add("capture","perceptual_capture","stage3-runtime",
      data=dict(capture_t_monde=t,
       dual_scope_capture_schema="stage12-dual-scope-body-cue-v1",
       dual_scope_visible_body=body,position=dict(x=2,y=3)))
 add("admission","command_admitted","stage3-runtime",
     data=dict(command_hash=digest,primitive="dormir"))
 cref=deterministic_id("journal-event-v1","action_control",t,attempt,digest,"send")
 add(cref,"command_experienced","action_control",
     command_hash=digest,primitive="dormir",parameters={})
 pref=deterministic_id("journal-event-v1","world",t,attempt,digest,"transition")
 before=dict(body)
 if corrupt: before["water"]=59.
 add(pref,"world_transition_experienced","world_and_body",
     body_before=before,body_after=body,position_after=dict(x=2,y=3),effects={})
 return choose(journal=j,t_monde=t,attempt_ref=attempt,
               command_ref=cref,physical_ref=pref)
p=check()
assert p==dict(source_event_ref="capture",t_monde=4,
               position=dict(x=2,y=3),
               body_perceived=dict(energy=40.,food=70.,water=60.,integrity=100.))
for kwargs in (dict(omit="reduced"),dict(omit="wake"),
               dict(omit="capture"),dict(cross=True),
               dict(corrupt=True),dict(reverse=True)):
 assert check(**kwargs) is None,kwargs
assert not any(k in p for k in ("wake_reason","sleep_duration","attempt_ref","consolidation"))
# Exact versioned candidate returns only the same first-person fields.
# The old synthetic gate checks failure separately; use its authentic
# fixture shape without exposing any Stage10 wake reason or sleep duration.
from i1lab.journal import HashChainedJournal
j=HashChainedJournal()
body=dict(energy=40.,food=70.,water=60.,integrity=100.)
t=4;attempt="attempt:4";digest=command_digest(Command("dormir"))
def append(ref,kind,emitter,**fields):
 j.append(event_id=ref,causal_event=dict(
  kind=kind,emitter=emitter,t_monde=t,attempt_ref=attempt,**fields))
append("reduced","stage10_reduced_capture","stage4-runtime",
       data=dict(full_cognitive_perception=False))
append("wake","stage10_sleep_woke","stage4-runtime",data=dict(reason="alert"))
append("capture","perceptual_capture","stage3-runtime",
       data=dict(capture_t_monde=t,
                 dual_scope_capture_schema="stage12-dual-scope-body-cue-v1",
                 dual_scope_visible_body=body,position=dict(x=2,y=3)))
append("admission","command_admitted","stage3-runtime",
       data=dict(command_hash=digest,primitive="dormir"))
cr=deterministic_id("journal-event-v1","action_control",t,attempt,digest,"send")
append(cr,"command_experienced","action_control",
       command_hash=digest,primitive="dormir",parameters={})
pr=deterministic_id("journal-event-v1","world",t,attempt,digest,"transition")
append(pr,"world_transition_experienced","world_and_body",
       body_before=body,body_after=body,position_after=dict(x=2,y=3),effects={})
payload=versioned(journal=j,t_monde=t,attempt_ref=attempt,
                  command_ref=cr,physical_ref=pr)
assert payload==dict(schema="i1-perceived-waking-body-candidate-v1",
 source_event_ref="capture",t_monde=4,position=dict(x=2,y=3),
 body_perceived=body),payload
assert versioned(journal=j,t_monde=t,attempt_ref="foreign",
                 command_ref=cr,physical_ref=pr) is None
assert not set(payload)&set(("reason","wake_reason","wake_policy",
                             "sleep_duration","attempt_ref","restored_energy"))
print("I1_495_VERSIONED_WAKE_CANDIDATE_OK")
print("I1_495_DORMANT_WAKE_GATE_OK")
"""
            checked=subprocess.run([sys.executable,"-c",script],
                 env={"PYTHONPATH":str(out)},capture_output=True,text=True)
            self.assertEqual(checked.returncode,0,checked.stdout+checked.stderr)
            self.assertIn("I1_495_DORMANT_WAKE_GATE_OK",checked.stdout)

if __name__=="__main__":
    unittest.main()
