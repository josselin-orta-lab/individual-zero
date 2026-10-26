"""#553: real Stage8 hook rejects stale and foreign generic action testimony."""
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class GeneralSituatedStage8553(unittest.TestCase):
    def test_generic_evaluated_stage8_receipt_is_paid_nonmotor(self):
        with TemporaryDirectory() as tmp:
            output = Path(tmp) / "generated"
            built = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                 "--output", str(output)], cwd=ROOT, capture_output=True,
                text=True, timeout=90,
            )
            self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
            code = r"""
from types import SimpleNamespace as S
from unittest.mock import patch
from copy import deepcopy
from i1lab.i1_natural_runtime import I1Runtime
from i1lab.i1_d2_runtime import I1WaterPrudentRuntime
from i1.modules.paid_action_consolidation import record_paid_source, merge_paid_fragments

def body(energy,water):
    return dict(energy=energy,food=70,water=water,integrity=90)
rows=[]
for t,action,xy,a,b in (
    (1,"attendre",(2,3),body(45,80),body(44,79)),
    (3,"dormir",(2,3),body(44,79),body(49,78)),
    (5,"attendre",(4,5),body(42,70),body(43,69)),
):
    pair=(
        dict(event_id=f"cmd{t}",kind="command_experienced",t_monde=t,
             primitive=action,parameters={}),
        dict(event_id=f"world{t}",kind="world_transition_experienced",t_monde=t,
             position_after={"x":xy[0],"y":xy[1]},body_before=a,
             body_after=b,effects={}),
    )
    for index,event in enumerate(pair):
        rows=record_paid_source(rows,episode_ref=f"ep{t}",event_offset=index,
                                event=event,before_step=10)
fragments=merge_paid_fragments(rows,[],cut_step=10)
copy=deepcopy(fragments)
actor=object.__new__(I1Runtime)
actor._cycle_degraded=False
actor._i1_sleep_site_paid_context=None
actor._i1_generic_action_paid_context=None
actor.slow_history=S(current_version="h:published")
capture=S(t_monde=12,x=2,y=3)
wait=S(id="wait",version="v1",expires_at_step=13)
sleep=S(id="sleep",version="v1",expires_at_step=13)
wait_plan=S(id="wait-plan",steps=(S(command=S(primitive="attendre",parameters={})),))
sleep_plan=S(id="sleep-plan",steps=(S(command=S(primitive="dormir",parameters={})),))
actor.competition=S(candidate_proposals=(S(option=wait,plan=wait_plan),
                                         S(option=sleep,plan=sleep_plan)),
                    is_engaged=lambda ref:ref==wait.id)
actor.stage3=S(control=S(current_step=(None,None,0)))
inputs={
  wait.id:S(evaluation=S(status="evaluated",option_ref=wait.id,
          option_version="v1",t_monde=12,cycle=1),evidence=0.25),
  sleep.id:S(evaluation=S(status="evaluated",option_ref=sleep.id,
          option_version="v1",t_monde=12,cycle=1),evidence=0.19),
}
paid=dict(step=12,cycle=1,site=(2,3),history_version="h:published",
          charged_operation="i1_published_action_recall",fragments=fragments)
actor._i1_h_action_paid_context=paid
written=[]
def write(self,*,kind,cycle,data):written.append((kind,cycle,data))
def evaluate():
    written.clear()
    I1Runtime._before_competition_accumulation(
        actor,capture=capture,cycle=1,evidence_inputs=inputs)
    return [d for k,c,d in written if k=="i1_situated_action_h_context_observed"]
with (patch.object(I1WaterPrudentRuntime,"_before_competition_accumulation",
                   lambda self,**kwargs:None,create=True),
      patch.object(I1Runtime,"_write",write,create=True)):
    observed=evaluate()
    assert len(observed)==1,observed
    data=observed[0]
    assert data["option_ref"]=="wait"
    assert data["charged_operation"]=="i1_published_action_recall"
    assert data["new_uc_debit_at_stage8"] is False
    assert data["stage8_evidence_unchanged"]==0.25
    assert data["decision_evidence"] is False
    assert data["causal_attribution"] is False
    assert data["motor_permission"] is False
    assert data["q_or_p40_augmented"] is False
    h=data["situated"]
    assert h["primitive"]=="attendre"
    assert h["historical_fragment_count"]==2
    assert h["same_site_fragment_count"]==1
    assert h["other_site_fragment_count"]==1
    assert h["current_site_ref"]=="observed-site:2:3"
    assert inputs["wait"].evidence==0.25 and inputs["sleep"].evidence==0.19
    assert len([d for k,c,d in written
                if k=="i1_situated_sleep_h_context_observed"])==1
    h["site_observations"][0]["experiences"][0]["observed_body_after"]["energy"]=-99
    assert fragments==copy
    for wrong in (
        dict(paid,step=11),dict(paid,cycle=2),
        dict(paid,site=(4,5)),dict(paid,history_version="h:wrong"),
        dict(paid,charged_operation="i1_closed_sleep_recall"),
    ):
        actor._i1_h_action_paid_context=wrong
        assert evaluate()==[],wrong
    actor._i1_h_action_paid_context=paid
    actor._cycle_degraded=True
    assert evaluate()==[]
    actor._cycle_degraded=False
    ev=inputs["wait"].evaluation
    for key,new in (("status","rejected"),("option_ref","other"),
                    ("option_version","old"),("cycle",2),("t_monde",11)):
        old=getattr(ev,key)
        setattr(ev,key,new)
        assert evaluate()==[],(key,new)
        setattr(ev,key,old)
    wait.expires_at_step=12
    assert evaluate()==[]
    wait.expires_at_step=13
    wait_plan.steps=(wait_plan.steps[0],
                     S(command=S(primitive="dormir",parameters={})))
    actor.stage3.control.current_step=(wait.id,wait_plan.id,1)
    assert evaluate()==[]
    actor.stage3.control.current_step=(None,None,0)
    wait_plan.steps=(wait_plan.steps[0],)
    wait_plan.steps[0].command.parameters={"target":"unobserved"}
    assert evaluate()==[]
    wait_plan.steps[0].command.parameters={}
    capture.x,capture.y=7,8
    assert evaluate()==[]
    actor._i1_h_action_paid_context=dict(paid,site=(7,8))
    unseen=evaluate()
    assert len(unseen)==1
    assert unseen[0]["situated"]["current_site_record_status"]=="not_observed_in_bounded_h"
    assert unseen[0]["situated"]["site_safety_inferred"] is False
    assert inputs["wait"].evidence==0.25
    assert fragments==copy
print("I1_553_GENERAL_STAGE8_GUARD_OK")
"""
            env = os.environ.copy()
            env["PYTHONPATH"] = os.pathsep.join((str(output), str(ROOT / "src")))
            result = subprocess.run(
                [sys.executable, "-c", code], cwd=ROOT, env=env,
                text=True, capture_output=True, timeout=150,
            )
            self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
            self.assertIn("I1_553_GENERAL_STAGE8_GUARD_OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
