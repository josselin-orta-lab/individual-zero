"""#549: isolated P-43 budget guard, before any SlowHistory owner read."""
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]


class PublishedHBudgetGuard549(unittest.TestCase):
    def test_no_unpaid_h_read_and_no_budget_degradation(self):
        with TemporaryDirectory() as folder:
            generated=Path(folder)/"generated"
            build=subprocess.run([
                sys.executable,str(ROOT/"scripts/build_i1_fork.py"),
                "--output",str(generated)],
                cwd=ROOT,capture_output=True,text=True,timeout=90)
            self.assertEqual(build.returncode,0,build.stdout+build.stderr)
            program=r"""
from types import SimpleNamespace as S
from unittest.mock import patch
from i1lab.i1_natural_runtime import I1Runtime
from i1lab.i1_d2_runtime import I1WaterPrudentRuntime

def scenario(*,version="h:published:v1",affordable=True,
             charged=True,degraded=False,cycle=1):
    actor=object.__new__(I1Runtime)
    actor._cycle_degraded=degraded
    actor.memory=S(episode_count=0,spatial_option_prospect_count=0,
                   lived_site_option_prospect_count=0)
    counters=dict(quote=0,charge=0,read=0,normal=0)
    def read(*,before_step):
        counters["read"]+=1
        assert before_step==12
        return {"history_version":version,"fragments":[]}
    actor.slow_history=S(current_version=version,
                         read_published_action_fragments=read)
    def quote(*,module,operations):
        assert module=="planning"
        assert operations==("i1_published_action_recall",)
        counters["quote"]+=1
        return S(affordable=affordable)
    actor.compute_budget=S(quote_operations=quote)
    def charge(self,*,module,operation):
        assert module=="planning" and operation=="i1_published_action_recall"
        counters["charge"]+=1
        return charged
    def hooks(self,**kwargs):
        return {
            1:{"planning":lambda ctx:counters.__setitem__(
                "normal",counters["normal"]+1)},
            3:{"competition":lambda ctx:None},
            4:{"action_control":lambda ctx:None},
        }
    capture=S(t_monde=12,x=3,y=4)
    with patch.object(I1WaterPrudentRuntime,"_phase_hooks",hooks),\
         patch.object(I1Runtime,"_charge",charge,create=True):
        overridden=I1Runtime._phase_hooks(
            actor,cycle=cycle,capture=capture,
            goal_for_planning=None,st_before_cycle=None)
        overridden[1]["planning"](None)
    return actor,counters

actor,c=scenario(version="h:birth:default")
assert c==dict(quote=0,charge=0,read=0,normal=1),c
assert actor._i1_h_action_paid_context is None
actor,c=scenario(affordable=False)
assert c==dict(quote=1,charge=0,read=0,normal=1),c
assert actor._i1_h_action_paid_context is None
assert not actor._cycle_degraded
actor,c=scenario(charged=False)
assert c==dict(quote=1,charge=1,read=0,normal=1),c
assert actor._i1_h_action_paid_context is None
actor,c=scenario(degraded=True)
assert c==dict(quote=0,charge=0,read=0,normal=1),c
assert actor._i1_h_action_paid_context is None
actor,c=scenario(cycle=2)
assert c==dict(quote=0,charge=0,read=0,normal=1),c
assert actor._i1_h_action_paid_context is None
actor,c=scenario()
assert c==dict(quote=1,charge=1,read=1,normal=1),c
assert actor._i1_h_action_paid_context=={
    "step":12,"cycle":1,"site":(3,4),
    "history_version":"h:published:v1",
    "charged_operation":"i1_published_action_recall",
    "fragments":[],
}
print("I1_549_PUBLISHED_H_BUDGET_GUARD_OK")
"""
            env=os.environ.copy()
            env["PYTHONPATH"]=os.pathsep.join((str(generated),str(ROOT/"src")))
            result=subprocess.run([sys.executable,"-c",program],
                cwd=ROOT,env=env,capture_output=True,text=True,timeout=120)
            self.assertEqual(result.returncode,0,result.stdout+"\n"+result.stderr)
            self.assertIn("I1_549_PUBLISHED_H_BUDGET_GUARD_OK",result.stdout)


if __name__=="__main__":
    unittest.main()
