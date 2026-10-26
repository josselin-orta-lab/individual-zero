"""#557: test the real natural runtime's paid observer hook with L1 fixtures.

A real CycleComputeBudget charges P-43 UC, while the old episode and DC-09
sources are controlled fixtures. This is NOT a natural positive L2 life.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class OldRecallRuntimeHook557(unittest.TestCase):
    def test_generated_natural_hook_prices_before_selecting_old_sources(self):
        with TemporaryDirectory() as folder:
            generated = Path(folder) / "generated"
            built = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                 "--output", str(generated)],
                cwd=ROOT, capture_output=True, text=True, timeout=90,
            )
            self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
            program = r"""
from types import MethodType, SimpleNamespace
from unittest.mock import patch
from i1.contracts import Contribution
from i1lab.compute_budget import ComputeBudgetConfig, CycleComputeBudget
from i1lab.i1_d2_runtime import I1WaterPrudentRuntime
from i1lab.i1_natural_runtime import (
    I1Runtime, _OLD_RECALL_OPERATION, _OLD_RECALL_COST_UC,
    _SLEEP_RECALL_OPERATION, _H_RECALL_OPERATION,
)

assert _OLD_RECALL_COST_UC == 128
refs=frozenset({"cmd:1","transition:1"})
projected=({"event_id":"cmd:1"}, {"event_id":"transition:1"})
witness={"step":1,"primitive":"collecter","source_event_refs":tuple(sorted(refs)),
         "decision_evidence":False,"causal_attribution":False}
capture=SimpleNamespace(t_monde=35,x=2,y=3)
key="memory-recall:episode:0:35:1"

class Sources:
    def __init__(self,owner,selected):
        self.owner=owner
        self.selected=selected
        self.reads=[]
    def selected_committed_autobiography(self,*,policies,selected_event_refs):
        assert self.owner.compute_budget.consumed_module_uc("planning")==128
        assert selected_event_refs==refs
        assert len(policies)==4
        self.reads.append("dc09")
        return projected

class Memory:
    episode_count=34
    last_recalled_ref="episode:0"
    spatial_option_prospect_count=0
    lived_site_option_prospect_count=0
    def __init__(self,owner,selected):
        self.owner=owner
        self.selected=selected
        self.reads=[]
    def closed_sleep_recall_source_refs(self):
        return frozenset()
    def closed_last_recalled_episode_source_refs(self,*,now):
        assert now==35
        assert self.owner.compute_budget.consumed_module_uc("planning")==128
        self.reads.append("memory")
        return self.selected
    def closed_applied_action_witnesses(self,*,autobiography,now,
                                        recalled_episode_refs):
        assert autobiography==projected and now==35
        assert recalled_episode_refs==refs
        assert self.owner.compute_budget.consumed_module_uc("planning")==128
        self.reads.append("witness")
        return (witness,)

def make(cycle=1,available=128,fresh=True,selected=refs):
    actor=object.__new__(I1Runtime)
    cfg=ComputeBudgetConfig(
        version="test-557",cycle_ceiling=available,
        module_envelopes={"planning":available},protected_modules=frozenset(),
        protected_capacity=0,
        operation_costs={
            _OLD_RECALL_OPERATION:128,
            # Disable the independent recent read in this focused old-lane fixture.
            _SLEEP_RECALL_OPERATION:129,
            _H_RECALL_OPERATION:1,
        },
    )
    actor.compute_budget=CycleComputeBudget(config=cfg)
    actor.compute_budget.open_cycle(cycle)
    actor._cycle_degraded=False
    actor._pending_contributions={}
    actor.memory=Memory(actor,selected)
    views=Sources(actor,selected)
    actor.stage3=SimpleNamespace(substrate=SimpleNamespace(views=views))
    actor.slow_history=SimpleNamespace(current_version="h:birth:")
    writes=[]
    def write(self,*,kind,data,cycle=None):
        writes.append((kind,data,cycle))
        return f"fixture:{len(writes)}"
    actor._write=MethodType(write,actor)

    def base_hooks(self,*,cycle,capture,goal_for_planning,st_before_cycle):
        def memory(ctx):
            if fresh:
                actor._pending_contributions[key]=Contribution(
                    id=key,schema_version="mvp-v1.2.1",type="response",
                    summary="recalled episode",subject_ref="episode:episode:0",
                    emitter_module="memory",signal_family="memory_recall",
                    confidence=1.,urgency=0.,risk=0.,value=0.,
                    production_t=35,production_cycle=1,expires_at_step=36,
                    payload={"episode_ref":"episode:0"},
                )
        return {
            1:{"memory":memory,"planning":lambda ctx:None},
            3:{"competition":lambda ctx:None},
            4:{"action_control":lambda ctx:None},
        }

    with patch.object(I1WaterPrudentRuntime,"_phase_hooks",base_hooks):
        hooks=actor._phase_hooks(
            cycle=cycle,capture=capture,goal_for_planning=None,
            st_before_cycle=None,
        )
    hooks[1]["memory"](None)
    hooks[1]["planning"](None)
    return actor,views,writes

paid,view,writes=make()
charges=[d for k,d,c in writes if k=="compute_charge"]
observed=[d for k,d,c in writes if k=="i1_old_episode_paid_observation"]
assert len(charges)==1 and charges[0]["operation"]==_OLD_RECALL_OPERATION
assert charges[0]["requested_uc"]==128 and charges[0]["accepted"] is True
assert len(observed)==1 and observed[0]["episode_ref"]=="episode:0"
assert observed[0]["charged_uc"]==128
assert observed[0]["witnesses"]==[witness]
assert observed[0]["decision_evidence"] is False
assert observed[0]["motor_permission"] is False
assert observed[0]["q_or_p40_augmented"] is False
assert paid.memory.reads==["memory","witness"] and view.reads==["dc09"]
assert paid.compute_budget.consumed_module_uc("planning")==128
# A persisted last_recalled_ref without a same-cycle Memory contribution
# cannot consult old evidence or even charge the old lane.
stale,view,writes=make(fresh=False)
assert not writes and not stale.memory.reads and not view.reads
# The second cognitive cycle does not reuse a first-cycle receipt.
later,view,writes=make(cycle=2)
assert not writes and not later.memory.reads and not view.reads
# Refuse before reading old sources when 128 UC cannot be paid.
denied,view,writes=make(available=127)
assert not writes and not denied.memory.reads and not view.reads
# A charge does not authorize 3 source references or any DC-09 lookup.
wide,view,writes=make(selected=frozenset({"cmd:1","transition:1","extra"}))
assert len(writes)==1 and writes[0][0]=="compute_charge"
assert not view.reads
assert wide.memory.reads==["memory"]
print("I1_557_PAID_OLD_RUNTIME_HOOK_L1_OK")
"""
            env = os.environ.copy()
            env["PYTHONPATH"] = os.pathsep.join(
                (str(generated), str(ROOT / "src"), str(ROOT / "tools"))
            )
            run = subprocess.run(
                [sys.executable, "-c", program],
                cwd=ROOT, env=env, capture_output=True, text=True, timeout=120,
            )
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            self.assertIn("I1_557_PAID_OLD_RUNTIME_HOOK_L1_OK", run.stdout)


if __name__ == "__main__":
    unittest.main()
