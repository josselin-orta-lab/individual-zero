"""M11 must reject forged prospective intentions without partial Memory mutation."""
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from build_i1_fork import generate

class MemoryIntentionRestoreTests(unittest.TestCase):
    def test_generated_atomic_intention_restore(self):
        with TemporaryDirectory() as tmp:
            out=Path(tmp)/"generated"
            generate(out)
            script="""
from copy import deepcopy
from i1.modules.memory import EpisodicMemory,Intention
from i1lab.stage11_reference_fixture import build_stage11_reference_runtime
rt=build_stage11_reference_runtime(autonomous_mortal=True)
memory=rt.memory
before=memory.export_causal_state()
intent=dict(id='intention:sample',goal_type='explore',target='witnessed',
 trigger_type='time',trigger_value=9,deadline_step=15,base_pressure=.3,
 monitoring='strategic',cost_uc=1,wake_authorized=False,
 state='pending',candidacy_active=False)
positive=deepcopy(before)
positive['intentions']=[intent]
memory.restore_causal_state(positive)
assert memory.export_causal_state()==positive
frozen=memory.export_causal_state()
for row in [
 dict(intent,wake_authorized='false'),
 dict(intent,candidacy_active=1),
 dict(intent,cost_uc=True),
 dict(intent,base_pressure=float('nan')),
 dict(intent,state='bogus'),
]:
 broken=deepcopy(frozen)
 broken['intentions']=[row]
 try: memory.restore_causal_state(broken);raise AssertionError('bad image accepted')
 except ValueError: pass
 assert memory.export_causal_state()==frozen, 'owner mutated before rejecting image'
duplicate=deepcopy(frozen)
duplicate['intentions']=[intent,intent]
try: memory.restore_causal_state(duplicate);raise AssertionError('duplicate accepted')
except ValueError: pass
assert memory.export_causal_state()==frozen
print('I1_MEMORY_359_ATOMIC_OK')
"""
            env=dict(os.environ,PYTHONPATH=os.pathsep.join((str(out),str(ROOT/"src"))),PYTHONDONTWRITEBYTECODE="1")
            p=subprocess.run([sys.executable,"-B","-c",script],cwd=ROOT,env=env,capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stdout+p.stderr)
            self.assertIn("I1_MEMORY_359_ATOMIC_OK",p.stdout)

if __name__=="__main__": unittest.main()
