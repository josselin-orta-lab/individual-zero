"""Verify Stage8 evidence belongs to the exact Competition option and cycle."""
import os, subprocess, sys, unittest
from pathlib import Path
from tempfile import TemporaryDirectory
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from build_i1_fork import generate

class CompetitionEvidenceIdentity(unittest.TestCase):
 def test_generated_owner_rejects_foreign_evidence_atomically(self):
  with TemporaryDirectory(prefix="i1-402-") as temp:
   generated=Path(temp)/"generated";generate(generated)
   source=r"""
from dataclasses import replace
from i1.modules.competition import Competition,CompetitionConfig,OptionEvidenceInput
cfg=CompetitionConfig(version="402",c_max=2,urgency_max=1.,
 urgency_scale_cycles=1.,leak=0.,noise_sigma=0.,gain=1.,
 base_threshold=.5,threshold_floor=.1,inertia=0.,residual=.5,
 options_max=5,substitution_evidence={})
owner=Competition(cfg)
owner.ensure_wait(t_monde=3,st_version="st:3")
base=owner.evaluate(cycle=1,t_monde=3)
evaluation=base.evaluations[0]
assert evaluation.option_ref=="permanent:attendre"
image=owner.export_causal_state()
def reject(**changes):
 forged=replace(evaluation,**changes)
 before=owner.export_causal_state()
 try:owner.evaluate(cycle=1,t_monde=3,evidence_inputs={
  "permanent:attendre":OptionEvidenceInput(forged,0.25)})
 except ValueError:pass
 else:raise AssertionError("misattributed evidence accepted: "+repr(changes))
 assert owner.export_causal_state()==before
reject(option_ref="other-candidate")
reject(option_version="different")
reject(cycle=2)
reject(t_monde=2)
reject(t_monde=4)
# A missing entry must not partially mutate owner state.
before=owner.export_causal_state()
try:owner.evaluate(cycle=1,t_monde=3,evidence_inputs={})
except ValueError:pass
else:raise AssertionError("missing evidence accepted")
assert owner.export_causal_state()==before
good=OptionEvidenceInput(evaluation,0.25)
result=owner.evaluate(cycle=1,t_monde=3,evidence_inputs={
 "permanent:attendre":good})
assert len(result.traces)==1 and result.traces[0].evidence==0.25
state=owner.export_causal_state()
cold=Competition(cfg);cold.restore_causal_state(state)
assert cold.export_causal_state()==state
print("I1_402_EVIDENCE_PROVENANCE_OK")
"""
   env=dict(os.environ,PYTHONPATH=os.pathsep.join((str(generated),str(ROOT/"src"))),PYTHONDONTWRITEBYTECODE="1")
   p=subprocess.run([sys.executable,"-B","-c",source],cwd=ROOT,env=env,text=True,capture_output=True)
   self.assertEqual(p.returncode,0,p.stdout+p.stderr)
   self.assertIn("I1_402_EVIDENCE_PROVENANCE_OK",p.stdout)
