"""#473: adversarial paid Stage8 site summary custody, with no motor effect."""
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class SituatedSleepStage8Guard473(unittest.TestCase):
    def test_non_scoring_situated_sleep_observer_rejects_stale_contexts(self):
        with TemporaryDirectory() as tmp:
            built_root = Path(tmp) / "generated"
            built = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                 "--output", str(built_root)],
                cwd=ROOT, capture_output=True, text=True, timeout=90,
            )
            self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
            program = r"""
from copy import deepcopy
from types import SimpleNamespace as S
from unittest.mock import patch
from i1lab.i1_natural_runtime import I1Runtime
from i1lab.i1_d2_runtime import I1WaterPrudentRuntime
from i1.modules.paid_action_consolidation import record_paid_source, merge_paid_fragments

def body(e,w):return dict(energy=e,food=72,water=w,integrity=91)
sources=[]
# A has stable, negative and positive energy observations. B has positive
# and unknown-before observations. Waiting at A is not sleep testimony.
for step,primitive,site,before,after in (
    (1,"dormir",(2,3),body(100,80),body(100,79)),
    (3,"dormir",(4,5),body(55,70),body(60,69)),
    (5,"dormir",(2,3),body(45,60),body(44,59)),
    (7,"attendre",(2,3),body(30,55),body(29,54)),
    (9,"dormir",(4,5),None,body(35,49)),
    (11,"dormir",(2,3),body(40,40),body(42,39)),
):
    command=dict(event_id=f"c{step}",kind="command_experienced",
        t_monde=step,primitive=primitive,parameters={})
    transition=dict(event_id=f"w{step}",kind="world_transition_experienced",
        t_monde=step,position_after={"x":site[0],"y":site[1]},
        body_after=after,effects={})
    if before is not None:transition["body_before"]=before
    for offset,event in enumerate((command,transition)):
        sources=record_paid_source(sources,episode_ref=f"ep:{step}",
            event_offset=offset,event=event,before_step=14)
fragments=merge_paid_fragments(sources,[],cut_step=14)
assert len(fragments)==6
source_copy=deepcopy(fragments)

actor=object.__new__(I1Runtime)
actor._cycle_degraded=False
actor._i1_sleep_site_paid_context=None
actor._i1_generic_action_paid_context=None
actor.slow_history=S(current_version="h:published:cut14")
capture=S(t_monde=16,x=2,y=3)
sleep_option=S(id="sleep:16:A",version="v1",expires_at_step=17)
wait_option=S(id="wait:16:A",version="v1",expires_at_step=17)
sleep_plan=S(id="plan:sleep",steps=(
    S(command=S(primitive="dormir",parameters={})),))
wait_plan=S(id="plan:wait",steps=(
    S(command=S(primitive="attendre",parameters={})),))
sleep_proposal=S(option=sleep_option,plan=sleep_plan)
wait_proposal=S(option=wait_option,plan=wait_plan)
actor.competition=S(candidate_proposals=(sleep_proposal,wait_proposal),
                    is_engaged=lambda x:x==sleep_option.id)
actor.stage3=S(control=S(current_step=(None,None,0)))
inputs={
    sleep_option.id:S(
        evaluation=S(status="evaluated",option_ref=sleep_option.id,
                     option_version="v1",t_monde=16,cycle=1),
        evidence={"original":0.23},
    ),
    wait_option.id:S(
        evaluation=S(status="evaluated",option_ref=wait_option.id,
                     option_version="v1",t_monde=16,cycle=1),
        evidence={"original":0.31},
    ),
}
context=dict(step=16,cycle=1,site=(2,3),
             history_version="h:published:cut14",
             charged_operation="i1_published_action_recall",
             fragments=fragments)
actor._i1_h_action_paid_context=context
written=[]
def write(self,*,kind,cycle,data):
    written.append((kind,cycle,data))
def evaluate():
    written.clear()
    I1Runtime._before_competition_accumulation(actor,capture=capture,cycle=1,
                                              evidence_inputs=inputs)
    return [row[2] for row in written if row[0] ==
            "i1_situated_sleep_h_context_observed"]

with (
    patch.object(I1WaterPrudentRuntime,"_before_competition_accumulation",
                 lambda self,**kwargs:None,create=True),
    patch.object(I1Runtime,"_write",write,create=True),
):
    receipts=evaluate()
    assert len(receipts)==1,receipts
    receipt=receipts[0]
    h=receipt["situated"]
    assert receipt["option_ref"]==sleep_option.id
    assert receipt["owner"]=="SlowHistory"
    assert receipt["charged_operation"]=="i1_published_action_recall"
    assert receipt["history_version"]=="h:published:cut14"
    assert receipt["q_or_p40_augmented"] is False
    assert receipt["motor_permission"] is False
    assert receipt["stage8_evidence_unchanged"]=={"original":0.23}
    assert h["current_site_ref"]=="sleep-site:2:3"
    assert h["current_site_record_status"]=="observed_in_bounded_h"
    assert (h["same_site_fragment_count"],h["other_site_fragment_count"])==(3,2)
    assert h["historical_fragment_count"]==5
    assert h["historical_site_count"]==2
    a,b=h["site_observations"]
    assert a["site_ref"]=="sleep-site:2:3"
    assert b["site_ref"]=="sleep-site:4:5"
    assert a["sign_counts_by_fragment"]["energy"]==dict(
        positive=1,negative=1,zero=1,unknown=0,contradictory=True)
    assert a["observed_full_energy_before_count"]==1
    assert b["sign_counts_by_fragment"]["energy"]["unknown"]==1
    assert h["expected_consequence"] is None
    assert h["site_safety_inferred"] is False
    assert h["decision_evidence"] is False
    assert h["causal_attribution"] is False
    assert inputs[sleep_option.id].evidence=={"original":0.23}
    assert inputs[wait_option.id].evidence=={"original":0.31}
    assert len([e for e in written if e[0]=="i1_published_action_stage8_context_observed"])==2
    assert fragments==source_copy
    # A detached journal event cannot edit h's source fragments.
    h["site_observations"][0]["experiences"][0]["observed_body_after"]["energy"]=-5
    assert fragments==source_copy

    for changed in (
        dict(context,step=15),dict(context,cycle=2),
        dict(context,site=(4,5)),dict(context,history_version="h:stale"),
        dict(context,charged_operation="i1_closed_sleep_recall"),
    ):
        actor._i1_h_action_paid_context=changed
        assert evaluate()==[],changed
    actor._i1_h_action_paid_context=None
    assert evaluate()==[]
    actor._i1_h_action_paid_context=context
    actor._cycle_degraded=True
    assert evaluate()==[]
    actor._cycle_degraded=False

    sleep_eval=inputs[sleep_option.id].evaluation
    for key,value in (
        ("status","rejected"),("option_ref","wrong"),
        ("option_version","old"),("t_monde",15),("cycle",2)
    ):
        old=getattr(sleep_eval,key)
        setattr(sleep_eval,key,value)
        assert evaluate()==[],(key,value)
        setattr(sleep_eval,key,old)
    old_expiry=sleep_option.expires_at_step
    sleep_option.expires_at_step=16
    assert evaluate()==[]
    sleep_option.expires_at_step=old_expiry

    # A sleep plan whose ACTUAL next command is wait cannot borrow the
    # plan's first-command sleep memory.
    sleep_plan.steps=(sleep_plan.steps[0],
                      S(command=S(primitive="attendre",parameters={})))
    actor.stage3.control.current_step=(sleep_option.id,sleep_plan.id,1)
    assert evaluate()==[]
    sleep_plan.steps=sleep_plan.steps[:1]
    actor.stage3.control.current_step=(None,None,0)
    sleep_plan.steps[0].command.parameters={"unseen":True}
    assert evaluate()==[]
    sleep_plan.steps[0].command.parameters={}

    # Moving after paid preparation invalidates the old site/cycle.
    capture.x,capture.y=7,8
    assert evaluate()==[]
    actor._i1_h_action_paid_context=dict(context,site=(7,8))
    other=evaluate()
    assert len(other)==1
    assert other[0]["situated"]["current_site_record_status"]=="not_observed_in_bounded_h"
    assert other[0]["situated"]["site_safety_inferred"] is False
    assert other[0]["situated"]["expected_consequence"] is None

    assert fragments==source_copy
    assert inputs[sleep_option.id].evidence=={"original":0.23}
    assert inputs[wait_option.id].evidence=={"original":0.31}
print("I1_473_SITUATED_SLEEP_STAGE8_GUARD_OK")
"""
            env = os.environ.copy()
            env["PYTHONPATH"] = os.pathsep.join((
                str(built_root), str(ROOT / "src"),
            ))
            result = subprocess.run(
                [sys.executable, "-c", program],
                cwd=ROOT, env=env, capture_output=True,
                text=True, timeout=120,
            )
            self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
            self.assertIn("I1_473_SITUATED_SLEEP_STAGE8_GUARD_OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
