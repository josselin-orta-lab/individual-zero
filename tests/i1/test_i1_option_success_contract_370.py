"""Applied action and contextual body change cannot certify option success."""
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from build_i1_fork import generate


class OptionSuccessContract(unittest.TestCase):
    def test_generated_owner_rejects_unwitnessed_success(self):
        with TemporaryDirectory(prefix="i1-370-") as d:
            built = Path(d) / "generated"
            generate(built)
            code = r"""
from copy import deepcopy
from i1lab.stage11_reference_fixture import build_stage11_reference_runtime
memory = build_stage11_reference_runtime(autonomous_mortal=True).memory
signature = "i1:affordance:collecter:target=x"
ref = "intention:i1:option:" + signature
source = "option:i1:local:t2:collecter:target=x"
body = dict(energy=50.,food=50.,water=50.,integrity=50.)
assert memory.remember_considered_option(
    signature=signature,source_option_ref=source,considered_step=2,cost_uc=1)
for stage in ("considered","applied","observed"):
    if stage == "applied":
        assert memory.remember_applied_option(
            signature=signature,source_option_ref=source,
            applied_step=2,cost_uc=1,body_before=body)
    if stage == "observed":
        assert memory.observe_applied_option_followups(
            world_step=3,body_after=dict(body,water=60.))
    snapshot = memory.export_causal_state()
    try: memory.complete_intention(ref)
    except ValueError: pass
    else: raise AssertionError(stage)
    assert memory.export_causal_state() == snapshot
    forged = deepcopy(snapshot)
    item = next(x for x in forged["intentions"] if x["id"] == ref)
    item["state"] = "done"
    try: memory.restore_causal_state(forged)
    except ValueError: pass
    else: raise AssertionError("M11 accepted unverified completion: "+stage)
    assert memory.export_causal_state() == snapshot
assert memory.recalled_applied_option(signature=signature,world_step=4)
assert len(memory.observed_option_witnesses(signature=signature,world_step=4)) == 1
cold = type(memory)(memory._config,atomic_world_step_length_boundary=True)
cold.restore_causal_state(memory.export_causal_state())
assert cold.export_causal_state() == memory.export_causal_state()
assert memory.check_intentions(
    st=None,t_monde=4,cycle=1,pressure_fn=lambda **kw: .5) == ()
print("I1_370_OPTION_COMPLETION_GUARD_OK")
"""
            env = dict(os.environ,PYTHONPATH=os.pathsep.join(
                (str(built),str(ROOT/"src"))),PYTHONDONTWRITEBYTECODE="1")
            p = subprocess.run([sys.executable,"-B","-c",code],
                cwd=ROOT,env=env,capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stdout+p.stderr)
            self.assertIn("I1_370_OPTION_COMPLETION_GUARD_OK",p.stdout)


if __name__ == "__main__":
    unittest.main()
