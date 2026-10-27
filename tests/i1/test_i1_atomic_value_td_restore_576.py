"""Reject malformed TD/ValueNeeds cold images without partial causal mutation.

Uses generated I1 only; no runtime behavior, world or motor fixtures are changed.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
from copy import deepcopy
import os
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from build_i1_fork import generate


class AtomicValueTDRestoreTests(unittest.TestCase):
    def test_generated_owner_rejects_late_invalid_snapshots_atomically(self):
        with TemporaryDirectory(prefix="i1-576-") as home:
            output = Path(home) / "generated"
            generate(output)
            code = r"""
from copy import deepcopy
from i1lab.stage11_reference_fixture import build_stage11_reference_runtime
from i1.modules.td_values import EvaluationState

runtime = build_stage11_reference_runtime(autonomous_mortal=True)
owner = runtime.value_needs
td = owner.td_values
assert td is not None
state = EvaluationState(
    body={"energy": 40.0, "food": 50.0, "water": 20.0, "integrity": 99.0},
    x=2, y=2, active_goal_type="drink", temporal_context="day",
)
td.arrive_decision(state=state, signature="primitive:boire", t_monde=1)
td.append_experienced_reward(2.5)
td.arrive_decision(state=state, signature="primitive:collecter", t_monde=2)
owner.assess(state.body)
before = deepcopy(owner.export_causal_state())
assert before["td_values"]["weights"]
assert before["td_values"]["pending"] is not None

def reject_td(change):
    original = deepcopy(td.export_causal_state())
    broken = deepcopy(original)
    broken["weights"]["primitive:boire"][0] += 12.0
    change(broken)
    try:
        td.restore_causal_state(broken)
    except (ValueError, TypeError, KeyError):
        pass
    else:
        raise AssertionError("invalid TD image accepted")
    assert td.export_causal_state() == original, "partial TD mutation"

reject_td(lambda row: row.update(traces={"x": "not-a-vector"}))
reject_td(lambda row: row.update(update_counts=[]))
reject_td(lambda row: row.update(pending={"state": {}}))
reject_td(lambda row: row.update(pending={"state": {"body": state.body, "x": 2,
    "y": 2, "active_goal_type": "drink", "temporal_context": "invalid"}}))

broken = deepcopy(before)
broken["previous_deviation"] = 765.0
broken["td_values"]["weights"]["primitive:boire"][0] += 10.0
broken["td_values"]["traces"] = {"bad": "not-a-vector"}
try:
    owner.restore_causal_state(broken)
except (ValueError, TypeError, KeyError):
    pass
else:
    raise AssertionError("invalid nested TD image accepted")
assert owner.export_causal_state() == before, "partial parent/child mutation"

broken = deepcopy(before)
broken["previous_deviation"] = 765.0
broken["last_state"] = {"body": 0, "deficits": {}, "pressures": {}, "deviation": 1.0}
try:
    owner.restore_causal_state(broken)
except (ValueError, TypeError, KeyError):
    pass
else:
    raise AssertionError("invalid parent image accepted")
assert owner.export_causal_state() == before, "parent mutated"

td.restore_causal_state(deepcopy(before["td_values"]))
owner.restore_causal_state(deepcopy(before))
assert owner.export_causal_state() == before
print("I1_ATOMIC_VALUE_TD_RESTORE_576_OK")
"""
            env = dict(os.environ, PYTHONPATH=os.pathsep.join(
                (str(output), str(ROOT / "src"))), PYTHONDONTWRITEBYTECODE="1")
            result = subprocess.run(
                [sys.executable, "-B", "-c", code], cwd=ROOT,
                env=env, capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("I1_ATOMIC_VALUE_TD_RESTORE_576_OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
