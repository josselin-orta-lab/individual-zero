"""Dormant DC-09 sensory allowlist must not authorize technical wake labels."""
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[2]

class DormantWakingPolicy495(unittest.TestCase):
    def test_generated_projector_fail_closed(self):
        with TemporaryDirectory() as tmp:
            out = Path(tmp)/"build"
            result = subprocess.run([sys.executable,str(ROOT/"scripts/build_i1_fork.py"),
                                     "--output",str(out)],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            code = """
from i1lab.i1_natural_prebody_policy import DORMANT_WAKING_BODY_POLICY as P
from i1lab.journal_views import AutobiographicalPolicy
from i1lab.journal import HashChainedJournal
P.validate()
j=HashChainedJournal()
j.append(event_id="sensory",causal_event=dict(
    kind="waking_body_perceived",emitter="i1-waking-perception",
    t_monde=4,attempt_ref="attempt:4",position=dict(x=2,y=3),
    body_perceived=dict(energy=40,food=70,water=60,integrity=100)))
projected=P.project(j.get("sensory"))
assert projected==dict(event_id="sensory",kind="waking_body_perceived",
 t_monde=4,position=dict(x=2,y=3),
 body_perceived=dict(energy=40,food=70,water=60,integrity=100))
for kind in ("stage10_sleep_woke","stage10_reduced_capture",
             "perceptual_capture","command_admitted"):
 try:
  AutobiographicalPolicy(version="forged",allowed_fields_by_kind={
   kind:("t_monde",)}).validate()
 except ValueError:pass
 else:raise AssertionError(kind)
for field in ("wake_reason","sleep_duration","attempt_ref","technical_counter"):
 try:
  AutobiographicalPolicy(version="forged",allowed_fields_by_kind={
   "waking_body_perceived":("t_monde",field)}).validate()
 except ValueError:pass
 else:raise AssertionError(field)
assert not any(key in projected for key in ("reason","sleep_duration","attempt_ref"))
print("I1_495_DORMANT_SENSORY_DC09_OK")
"""
            x=subprocess.run([sys.executable,"-c",code],capture_output=True,
                             text=True,env={"PYTHONPATH":str(out)})
            self.assertEqual(x.returncode,0,x.stdout+x.stderr)
            self.assertIn("I1_495_DORMANT_SENSORY_DC09_OK",x.stdout)

if __name__=="__main__":
    unittest.main()
