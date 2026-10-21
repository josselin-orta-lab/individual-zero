"""Expired first-person intentions require new evidence, not resurrection."""
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from build_i1_fork import generate


class ExpiredOptionLifecycle(unittest.TestCase):
    def test_generated_memory_expiry_and_cold_restore(self):
        with TemporaryDirectory(prefix="i1-369-") as directory:
            built = Path(directory) / "generated"
            generate(built)
            program = r"""
from copy import deepcopy
from i1lab.stage11_reference_fixture import build_stage11_reference_runtime

memory = build_stage11_reference_runtime(autonomous_mortal=True).memory
sig = "i1:affordance:collecter:target=x"
def src(step): return f"option:i1:local:t{step}:collecter:target=x"
before = dict(energy=50., food=50., water=50., integrity=50.)
assert memory.remember_considered_option(
    signature=sig,source_option_ref=src(2),considered_step=2,cost_uc=1)
old = next(i for i in memory.intentions if i.target == sig)
deadline = old.deadline_step
assert not memory.remember_considered_option(
    signature=sig,source_option_ref=src(3),considered_step=3,cost_uc=1)
assert memory.reconcile_option_intentions(
    available_signatures=frozenset(),world_step=3)
assert memory.reconcile_option_intentions(
    available_signatures=frozenset({sig}),world_step=4)
assert memory.reconcile_option_intentions(
    available_signatures=frozenset({sig}),world_step=deadline+1)
assert not memory.recalled_applied_option(signature=sig,world_step=deadline+1)
assert memory.remember_considered_option(
    signature=sig,source_option_ref=src(deadline+2),
    considered_step=deadline+2,cost_uc=1)
fresh = next(i for i in memory.intentions if i.target == sig)
assert fresh.trigger_value["considered_step"] == deadline+2
assert fresh.deadline_step > deadline
assert not memory.remember_considered_option(
    signature=sig,source_option_ref=src(deadline+3),
    considered_step=deadline+3,cost_uc=1)
# Once genuinely APPLIED, the old history must not be overwritten by a
# consideration, even after expiry.
step = deadline+3
assert memory.remember_applied_option(
    signature=sig, source_option_ref=src(step),applied_step=step,
    cost_uc=1, body_before=before)
assert memory.observe_applied_option_followups(
    world_step=step+1,body_after=dict(before,water=40.))
applied = next(i for i in memory.intentions if i.target == sig)
assert not memory.remember_considered_option(
    signature=sig,source_option_ref=src(applied.deadline_step+2),
    considered_step=applied.deadline_step+2,cost_uc=1)
# New personally applied event after old expiry is legitimate, but must not
# inherit stale adversities or favorable witnesses from the old lifetime.
after_expiry = applied.deadline_step+2
assert memory.remember_applied_option(
    signature=sig,source_option_ref=src(after_expiry),
    applied_step=after_expiry,cost_uc=1,body_before=before)
assert memory.observed_option_witnesses(
    signature=sig,world_step=after_expiry) == ()
assert memory.observe_applied_option_followups(
    world_step=after_expiry+1,body_after=dict(before,water=60.))
rows = memory.observed_option_witnesses(
    signature=sig,world_step=after_expiry+1)
assert len(rows) == 1 and rows[0]["applied_step"] == after_expiry
assert rows[0]["body_delta"]["water"] == 10.
image = memory.export_causal_state()
restored = type(memory)(
    memory._config,atomic_world_step_length_boundary=True)
restored.restore_causal_state(image)
assert restored.export_causal_state() == image
for invalid in ("nan","future","duplicate"):
    forged = deepcopy(image)
    rec = next(i for i in forged["intentions"] if i["target"] == sig)
    if invalid == "nan":
        rec["trigger_value"]["body_delta"]["water"] = float("nan")
    elif invalid == "future":
        rec["trigger_value"]["observed_step"] += 1
    else:
        forged["intentions"].append(deepcopy(rec))
    baseline = restored.export_causal_state()
    try: restored.restore_causal_state(forged)
    except ValueError: pass
    else: raise AssertionError(invalid)
    assert restored.export_causal_state() == baseline
print("I1_369_EXPIRED_OPTION_LIFECYCLE_OK")
"""
            env = dict(os.environ, PYTHONPATH=os.pathsep.join(
                (str(built),str(ROOT/"src"))),PYTHONDONTWRITEBYTECODE="1")
            p = subprocess.run([sys.executable,"-B","-c",program],
                cwd=ROOT,env=env,text=True,capture_output=True)
            self.assertEqual(p.returncode,0,p.stdout+p.stderr)
            self.assertIn("I1_369_EXPIRED_OPTION_LIFECYCLE_OK",p.stdout)


if __name__ == "__main__":
    unittest.main()
