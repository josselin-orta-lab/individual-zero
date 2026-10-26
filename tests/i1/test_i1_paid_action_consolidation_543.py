"""#543: paid Stage10 fragment extraction, source and identity regression."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest
ROOT = Path(__file__).resolve().parents[2]

class PaidActionConsolidation543(unittest.TestCase):
    def test_generated_bounded_paid_fragment_contract(self):
        with TemporaryDirectory() as tmp:
            out = Path(tmp) / "generated"
            built = subprocess.run([sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                "--output", str(out)], capture_output=True, text=True)
            self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
            code = r"""
from i1.modules.paid_action_consolidation import (
    record_paid_source, merge_paid_fragments, validate_published_fragments)
from copy import deepcopy
def body(e, w):
    return dict(energy=e, food=70, water=w, integrity=90)
def source(t, primitive, before, after, params=None):
    return [
        dict(event_id="c"+str(t), kind="command_experienced",
             t_monde=t, primitive=primitive, parameters=params or {}),
        dict(event_id="t"+str(t), kind="world_transition_experienced",
             t_monde=t, position_after=dict(x=2,y=3),
             body_before=before, body_after=after, effects={}),
    ]
s1=source(1,"dormir",body(20,60),body(24,59))
s2=source(2,"dormir",body(24,59),body(27,58))
s3=source(3,"attendre",body(27,58),body(27,57))
rows=[]
for step,sources in enumerate([s1,s2,s3],1):
    for offset, event in enumerate(sources):
        rows=record_paid_source(rows, episode_ref="e"+str(step),
            event_offset=offset,event=event,before_step=10)
out=merge_paid_fragments(rows,[],cut_step=10)
# Adjacent actions may span two separately authenticated Memory episodes.
# The evidence is continuous across source episodes, not a sleep session.
assert len(out)==2, out
assert [x["primitive"] for x in out]==["dormir","attendre"]
assert [x["observed_steps"] for x in out]==[2,1]
assert out[0]["source_episode_refs"]==["e1","e2"]
assert out[0]["observed_total_body_delta"]["energy"]==7
assert out[0]["observed_total_body_delta"]["water"]==-2
assert out[1]["observed_total_body_delta"]["water"]==-1
assert all(x["complete_subjective_session"] is False for x in out)
assert all(x["causal_attribution"] is False and x["decision_evidence"] is False for x in out)
assert validate_published_fragments(out)
assert merge_paid_fragments([],out,cut_step=12)==out
try:
    merge_paid_fragments(rows,out,cut_step=12)
except ValueError:
    pass
else: raise AssertionError("duplicate source retained")
tampered=deepcopy(out);tampered[0]["body_after"]["energy"]=-99
assert not validate_published_fragments(tampered)
try:
    record_paid_source(rows,episode_ref="e1",event_offset=0,event=s1[0],before_step=10)
except ValueError: pass
else: raise AssertionError("duplicate paid ref accepted")
try:
    record_paid_source(rows,episode_ref="future",event_offset=0,
        event=dict(s1[0],t_monde=10,event_id="future"),before_step=10)
except ValueError: pass
else: raise AssertionError("post-cut source accepted")
same=[]
for offset, event in enumerate([*s1, *s2]):
    same=record_paid_source(same, episode_ref="one-episode",
        event_offset=offset, event=event, before_step=10)
continuous=merge_paid_fragments(same,[],cut_step=10)
assert len(continuous)==1 and continuous[0]["observed_steps"]==2
assert continuous[0]["observed_total_body_delta"]["energy"]==7
# Source fields may include unknown scenario effects without granting
# the individual any presupposed causal semantics.
scenario=source(4,"attendre",body(27,58),body(27,57))
scenario[1]["effects"]={"scenario_forced_failure":"attendre"}
observed=[]
for offset, event in enumerate(scenario):
    observed=record_paid_source(observed,episode_ref="scenario",
        event_offset=offset,event=event,before_step=10)
assert merge_paid_fragments(observed,[],cut_step=10)[0]["observed_effects_by_step"]==[{}]
# A genuine discontinuity must not become a fabricated continuous rest.
broken=deepcopy(s2)
broken[1]["body_before"]=body(12,12)
different=[]
for offset,event in enumerate([*s1,*broken]):
    different=record_paid_source(different,episode_ref="break",
        event_offset=offset,event=event,before_step=10)
assert [row["observed_steps"] for row in merge_paid_fragments(
    different,[],cut_step=10)]==[1,1]
gap=deepcopy(s2)
for event in gap: event["t_monde"]=5
gapped=[]
for offset,event in enumerate([*s1,*gap]):
    gapped=record_paid_source(gapped,episode_ref="gap",
        event_offset=offset,event=event,before_step=10)
assert [row["observed_steps"] for row in merge_paid_fragments(
    gapped,[],cut_step=10)]==[1,1]
assert merge_paid_fragments([],[],cut_step=10)==[]
print("I1_543_PAID_STAGE10_FRAGMENTS_OK")
"""
            result=subprocess.run([sys.executable,"-c",code],
                env={"PYTHONPATH": str(out)},capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertIn("I1_543_PAID_STAGE10_FRAGMENTS_OK",result.stdout)
