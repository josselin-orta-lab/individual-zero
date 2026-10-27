"""Atomic GoalManager restoration from the generated canonical I1 owner."""
from copy import deepcopy
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from build_i1_fork import generate


class GoalManagerAtomicRestore578(unittest.TestCase):
    def test_generated_natural_goal_manager_rejects_late_corruption(self):
        with TemporaryDirectory(prefix="i1-578-") as root:
            generated = Path(root) / "generated"
            generate(generated)
            program = r"""
from copy import deepcopy
from i1lab.stage11_reference_fixture import build_stage11_reference_runtime
from i1.contracts import GoalProposal

runtime = build_stage11_reference_runtime(autonomous_mortal=True)
owner = runtime.goal_manager

def proposed(t, goal="drink"):
    return GoalProposal(
        id="goal-proposal:%s:%s" % (goal, t), source="value_needs",
        goal_type=goal, target="water" if goal == "drink" else "energy",
        base_pressure=.5, current_pressure=.5,
        justification_ref="need:%s" % t,
        t_monde=t, cycle=1, rule_version="test",
    )
owner.arbitrate([proposed(1)], t_monde=1, cycle=1)
owner.defer_proposals([proposed(1)])
owner.close_cycle_inputs()
owner.defer_proposals([proposed(2)])
owner.note_non_plannable(material_context_hash="a", t_monde=2)
baseline = deepcopy(owner.export_causal_state())
assert baseline["active"] is not None
assert baseline["visible_proposals"] and baseline["next_proposals"]
assert baseline["impossible_failures"]
def reject(change):
    bad = deepcopy(baseline)
    bad["active"]["current_pressure"] = .42
    bad["latest_pressure"].append(["eat","food",.75])
    change(bad)
    try:
        owner.restore_causal_state(bad)
    except (ValueError, KeyError, TypeError, IndexError):
        pass
    else:
        raise AssertionError("bad GoalManager image accepted")
    assert owner.export_causal_state() == baseline, "partial GoalManager state"
reject(lambda s: s.update(next_proposals=[{"invalid": True}]))
reject(lambda s: s.update(visible_proposals=[{"invalid": True}]))
reject(lambda s: s.update(refractory_until=[["drink"]]))
reject(lambda s: s.update(impossible_failures=[["drink"]]))
owner.restore_causal_state(deepcopy(baseline))
assert owner.export_causal_state() == baseline
print("I1_GOAL_MANAGER_ATOMIC_RESTORE_578_OK")
"""
            env = dict(os.environ, PYTHONPATH=os.pathsep.join(
                (str(generated), str(ROOT / "src"))), PYTHONDONTWRITEBYTECODE="1")
            run = subprocess.run([sys.executable, "-B", "-c", program],
                cwd=ROOT, env=env, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            self.assertIn("I1_GOAL_MANAGER_ATOMIC_RESTORE_578_OK", run.stdout)
