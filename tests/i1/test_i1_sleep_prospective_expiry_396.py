"""Reduced sleep expires only overdue prospective Memory options, not wake rights."""
import os
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from build_i1_fork import generate


class SleepProspectiveExpiry(unittest.TestCase):
    def test_generated_memory_owner_and_sleep_boundary(self):
        with TemporaryDirectory(prefix="i1-396-") as home:
            generated = Path(home) / "generated"
            generate(generated)
            script = r"""
from i1lab.stage11_reference_fixture import build_stage11_reference_runtime
from i1lab.stage10_runtime import Stage10Runtime
from i1.modules.memory import EpisodicMemory
import inspect

memory = build_stage11_reference_runtime(autonomous_mortal=True).memory
local = "i1:affordance:collecter:target=x"
spatial = "memory_place_return:observed-site"
assert memory.remember_considered_option(
 signature=local, source_option_ref="option:i1:local:t2:collecter:target=x",
 considered_step=2,cost_uc=1)
assert memory.remember_considered_option(
 signature=spatial,
 source_option_ref="option:place-memory:place:observed-site:at:3:0:from:1:0:via:2:0",
 considered_step=2,cost_uc=1)
deadline=next(i.deadline_step for i in memory.intentions if i.target==spatial)
assert not memory.expire_option_intentions(world_step=deadline)
assert memory.reconcile_option_intentions(
 available_signatures=frozenset(),world_step=3,namespace="memory_place_return:")
before = memory.export_causal_state()
for invalid in (True,False,0,1.2,"4"):
 try:memory.expire_option_intentions(world_step=invalid)
 except ValueError:pass
 else:raise AssertionError("invalid clock accepted")
assert memory.export_causal_state()==before
expired=memory.expire_option_intentions(world_step=deadline+1)
assert len(expired)==2,expired
assert not memory.expire_option_intentions(world_step=deadline+2)
assert all(i.state=="abandoned" for i in memory.intentions if i.trigger_type=="option")
assert not memory.recalled_applied_option(signature=spatial,world_step=deadline+2)
assert not memory.reconcile_option_intentions(
 available_signatures=frozenset({spatial}),world_step=deadline+2,
 namespace="memory_place_return:")
assert all(i.state=="abandoned" for i in memory.intentions if i.trigger_type=="option")
image=memory.export_causal_state()
cold=EpisodicMemory(memory._config,atomic_world_step_length_boundary=True)
cold.restore_causal_state(image)
assert cold.export_causal_state()==image
code=inspect.getsource(Stage10Runtime._sleep_step)
assert code.index("expire_option_intentions(")<code.index("open_world_step(t)")
assert '"full_cognitive_perception": False' in code
assert '"motor_admission_inherited": False' in code
print("I1_396_SLEEP_PROSPECTIVE_EXPIRY_OK")
"""
            env = dict(os.environ, PYTHONPATH=os.pathsep.join((
                str(generated), str(ROOT / "src"))), PYTHONDONTWRITEBYTECODE="1")
            result = subprocess.run([sys.executable, "-B", "-c", script],
                                    cwd=ROOT,env=env,text=True,capture_output=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertIn("I1_396_SLEEP_PROSPECTIVE_EXPIRY_OK",result.stdout)
