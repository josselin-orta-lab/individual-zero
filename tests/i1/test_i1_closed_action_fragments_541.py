"""#541: contiguous first-person action fragments, without inferred sessions."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class ClosedActionFragments541(unittest.TestCase):
    def test_generated_i1_bounded_fragments(self):
        with TemporaryDirectory() as folder:
            output = Path(folder) / "generated"
            build = subprocess.run([sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                "--output", str(output)], capture_output=True, text=True)
            self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
            program = r"""
from i1.modules.action_fragments import closed_action_fragments
from copy import deepcopy

def body(energy, water=60):
    return dict(energy=energy, food=70, water=water, integrity=90)
def row(t, primitive, start, end, x=2, parameters=None, before=True):
    return dict(step=t, primitive=primitive, parameters=parameters or {},
        position_after=dict(x=x, y=3),
        source_event_refs=(f"c{t}", f"t{t}"),
        source_episode_refs=(f"e{t}",),
        body_before=body(start) if before else None,
        body_after=body(end, 60-t),
        observed_effects={"rest": primitive},
        causal_attribution=False, decision_evidence=False)
# A genuine two-step contiguous sleep fragment with signed water and
# energy changes. Each before-body must match the previous physical after.
one = row(1, "dormir", 20, 24)
two = row(2, "dormir", 24, 27)
two["body_before"] = deepcopy(one["body_after"])
three = row(3, "attendre", 27, 27)
three["body_before"] = deepcopy(two["body_after"])
four = row(4, "collecter", 27, 26)
four["body_before"] = deepcopy(three["body_after"])
fragments = closed_action_fragments([one, two, three, four])
assert [(r["primitive"], r["observed_steps"]) for r in fragments] == [
    ("dormir", 2), ("attendre", 1), ("collecter", 1)]
sleep = fragments[0]
assert sleep["observed_total_body_delta"]["energy"] == 7
assert sleep["observed_total_body_delta"]["water"] == -2
assert sleep["source_event_refs"] == ("c1", "t1", "c2", "t2")
assert not sleep["complete_subjective_session"]
assert not sleep["decision_evidence"] and not sleep["causal_attribution"]
assert fragments[1]["observed_total_body_delta"]["energy"] == 0
assert fragments[2]["observed_total_body_delta"]["energy"] == -1
# Pre-body absence, site shift, parameter shift, time gap: no joining.
missing = deepcopy(two)
missing["body_before"] = None
assert [r["observed_steps"] for r in closed_action_fragments([one, missing])] == [1, 1]
assert closed_action_fragments([missing])[0]["observed_total_body_delta"] is None
shifted = deepcopy(two)
shifted["position_after"]["x"] = 3
assert [r["observed_steps"] for r in closed_action_fragments([one, shifted])] == [1, 1]
shifted = deepcopy(two)
shifted["parameters"] = {"setting": "new"}
assert [r["observed_steps"] for r in closed_action_fragments([one, shifted])] == [1, 1]
shifted = deepcopy(two)
shifted["step"] = 5
assert [r["observed_steps"] for r in closed_action_fragments([one, shifted])] == [1, 1]
shifted = deepcopy(two)
shifted["body_before"]["energy"] = 2
assert [r["observed_steps"] for r in closed_action_fragments([one, shifted])] == [1, 1]
assert closed_action_fragments([one, deepcopy(one)]) == ()
shifted = deepcopy(two)
shifted["source_event_refs"] = one["source_event_refs"]
assert closed_action_fragments([one, shifted]) == ()
shifted = deepcopy(two)
shifted["body_before"]["energy"] = float("nan")
assert [r["observed_steps"] for r in closed_action_fragments([one, shifted])] == [1]
shifted = deepcopy(two)
shifted["decision_evidence"] = True
assert [r["observed_steps"] for r in closed_action_fragments([one, shifted])] == [1]
shifted = deepcopy(two)
shifted["oracle_truth"] = "safe"
# No unknown unverified attributes should be promoted into output.
assert "oracle_truth" not in closed_action_fragments([shifted])[0]
fragments[0]["body_after"]["water"] = -100
assert closed_action_fragments([one, two])[0]["body_after"]["water"] == 58
assert len(closed_action_fragments([one, two, three, four], max_fragments=2)) == 2
try:
    closed_action_fragments([one], max_fragments=17)
    raise AssertionError("unbounded fragment count accepted")
except ValueError:
    pass
print("I1_541_CLOSED_ACTION_FRAGMENTS_OK")
"""
            result = subprocess.run([sys.executable, "-c", program],
                env={"PYTHONPATH": str(output)}, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("I1_541_CLOSED_ACTION_FRAGMENTS_OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
