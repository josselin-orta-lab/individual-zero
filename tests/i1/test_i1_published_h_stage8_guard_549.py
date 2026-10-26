"""#549: Stage8 paid published-history context is observational and fail-closed.

Adversarial probe of the real natural-I1 pre-Competition observer. No forged
history is added to a born individual or to persisted owner state.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class PaidHStage8Guard549(unittest.TestCase):
    def test_current_option_paid_history_guard(self):
        with TemporaryDirectory() as tmp:
            output=Path(tmp)/"generated"
            built=subprocess.run([sys.executable,str(ROOT/"scripts/build_i1_fork.py"),
                                  "--output",str(output)],cwd=ROOT,
                                 capture_output=True,text=True,timeout=90)
            self.assertEqual(built.returncode,0,built.stdout+built.stderr)
            program=r"""
from types import SimpleNamespace as S
from unittest.mock import patch
from copy import deepcopy
from i1lab.i1_natural_runtime import I1Runtime
from i1lab.i1_d2_runtime import I1WaterPrudentRuntime
from i1.modules.paid_action_consolidation import (
    record_paid_source, merge_paid_fragments, validate_published_fragments,
)

before={"energy":42,"food":65,"water":58,"integrity":91}
after={"energy":42,"food":65,"water":57,"integrity":91}
command=dict(event_id="cmd:2",kind="command_experienced",t_monde=2,
             primitive="attendre",parameters={})
effect=dict(event_id="result:2",kind="world_transition_experienced",
            t_monde=2,position_after={"x":3,"y":4},body_before=before,
            body_after=after,effects={})
sources=[]
for n,item in enumerate((command,effect)):
    sources=record_paid_source(
        sources,episode_ref="closed:ep2",event_offset=n,
        event=item,before_step=8)
fragments=merge_paid_fragments(sources,[],cut_step=8)
assert len(fragments)==1 and validate_published_fragments(fragments)

probe=object.__new__(I1Runtime)
probe._cycle_degraded=False
probe._i1_sleep_site_paid_context=None
probe._i1_generic_action_paid_context=None
probe.slow_history=S(current_version="h:committed")
capture=S(t_monde=10,x=9,y=10)
option=S(id="opt:h",version="v1",expires_at_step=11,
         motive_ref=S(type="local_opportunity"))
plan=S(id="plan:one",steps=(S(command=S(primitive="attendre",parameters={})),))
proposal=S(option=option,plan=plan)
probe.competition=S(candidate_proposals=(proposal,),
                    is_engaged=lambda x:x==option.id)
probe.stage3=S(control=S(current_step=(None,None,0)))
evaluation=S(status="evaluated",option_ref=option.id,option_version="v1",
             cycle=1,t_monde=10)
supplied=S(evaluation=evaluation,evidence={"q_source":"unchanged"})
inputs={option.id:supplied}
paid=dict(step=10,cycle=1,site=(9,10),
          history_version="h:committed",
          charged_operation="i1_published_action_recall",
          fragments=deepcopy(fragments))
probe._i1_h_action_paid_context=paid
receipts=[]
def write(self,*,kind,cycle,data):
    receipts.append((kind,cycle,data))
def observe():
    receipts.clear()
    I1Runtime._before_competition_accumulation(
        probe,capture=capture,cycle=1,evidence_inputs=inputs)
    return [x for x in receipts
            if x[0]=="i1_published_action_stage8_context_observed"]
with patch.object(I1WaterPrudentRuntime,
                  "_before_competition_accumulation",
                  lambda self,**kwargs:None,create=True),\
     patch.object(I1Runtime,"_write",write,create=True):
    result=observe()
    assert len(result)==1,result
    row=result[0][2]
    assert row["owner"]=="SlowHistory"
    assert row["history_version"]=="h:committed"
    assert row["charged_operation"]=="i1_published_action_recall"
    assert row["new_uc_debit_at_stage8"] is False
    assert row["source_event_refs"]==["cmd:2","result:2"]
    assert row["source_episode_refs"]==["closed:ep2"]
    assert row["historical_sites"]==[{"x":3,"y":4}]
    assert row["current_site"]==[9,10]
    assert row["observed_body_deltas"][0]["water"]==-1
    assert row["decision_evidence"] is False
    assert row["causal_attribution"] is False
    assert row["motor_permission"] is False
    assert row["q_or_p40_augmented"] is False
    assert supplied.evidence=={"q_source":"unchanged"}
    # A stale cycle, site, h-version, or wrong charge may not lend
    # this witness to an option, even if its action would match.
    for changed in (
        dict(paid,step=9),dict(paid,cycle=2),
        dict(paid,site=(3,4)),dict(paid,history_version="h:older"),
        dict(paid,charged_operation="i1_closed_sleep_recall"),
    ):
        probe._i1_h_action_paid_context=changed
        assert observe()==[],changed
    probe._i1_h_action_paid_context=None
    assert observe()==[]
    probe._i1_h_action_paid_context=paid
    probe._cycle_degraded=True
    assert observe()==[]
    probe._cycle_degraded=False
    # Only a true current evaluated Stage8 candidate may consult h.
    for changes in (
        {"status":"rejected"},{"option_ref":"someone-else"},
        {"option_version":"old"},{"t_monde":9},{"cycle":2},
    ):
        originals={k:getattr(evaluation,k) for k in changes}
        for key,val in changes.items():setattr(evaluation,key,val)
        assert observe()==[],changes
        for key,val in originals.items():setattr(evaluation,key,val)
    original_expiry=option.expires_at_step
    option.expires_at_step=10
    assert observe()==[]
    option.expires_at_step=original_expiry
    original_params=plan.steps[0].command.parameters
    plan.steps[0].command.parameters={"new":True}
    assert observe()==[]
    plan.steps[0].command.parameters=original_params
    plan.steps[0].command.primitive="dormir"
    assert observe()==[]
    plan.steps[0].command.primitive="attendre"
    # A resumed option follows the actually engaged next command.
    second=S(command=S(primitive="dormir",parameters={}))
    plan.steps=(plan.steps[0],second)
    probe.stage3.control.current_step=(option.id,plan.id,1)
    assert observe()==[]
    second.command.primitive="attendre"
    assert len(observe())==1
    probe.stage3.control.current_step=("another-option",plan.id,1)
    second.command.primitive="dormir"
    assert len(observe())==1  # non-engaged candidates use first command
    probe.stage3.control.current_step=(option.id,"another-plan",1)
    assert len(observe())==1
    assert supplied.evidence=={"q_source":"unchanged"}
print("I1_549_STAGE8_PAID_H_GUARD_OK")
"""
            env=os.environ.copy()
            env["PYTHONPATH"]=os.pathsep.join((str(output),str(ROOT/"src")))
            result=subprocess.run([sys.executable,"-c",program],cwd=ROOT,env=env,
                                  capture_output=True,text=True,timeout=120)
            self.assertEqual(result.returncode,0,result.stdout+"\n"+result.stderr)
            self.assertIn("I1_549_STAGE8_PAID_H_GUARD_OK",result.stdout)


if __name__=="__main__":
    unittest.main()
