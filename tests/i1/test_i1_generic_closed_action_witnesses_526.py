"""#526: general closed applied-action memory witnesses, no motor/value override."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class ClosedGenericActionWitnesses526(unittest.TestCase):
    def test_generated_i1_generic_closed_custody(self):
        with TemporaryDirectory() as temp:
            generated = Path(temp) / "generated"
            build = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                 "--output", str(generated)],
                capture_output=True, text=True,
            )
            self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
            program = r"""
from i1.modules.memory import EpisodicMemory, Episode

def episode(i, refs):
    return Episode(
        id=f"episode:{i}", start_t_monde=i + 1,
        end_t_monde=i + 1, event_refs=tuple(refs),
        boundary_type="max_length", active_goal_ref=None,
        body_start=None, body_end=None, cumulative_reward=0.0,
        surprise=0.0, linked_previous_ref=None,
    )

m = object.__new__(EpisodicMemory)
m._episodes = [episode(0, ("c1", "t1")), episode(1, ("c2", "t2")),
               episode(2, ("c3", "t3"))]
m._seen_event_refs = {ref for ep in m._episodes for ref in ep.event_refs}
body = dict(energy=35, food=70, water=60, integrity=90)
def cmd(ref, step, primitive, parameters):
    return dict(event_id=ref, kind="command_experienced",
                t_monde=step, primitive=primitive, parameters=parameters)
def outcome(ref, step, position, before=None):
    result = dict(event_id=ref, kind="world_transition_experienced",
                  t_monde=step, position_after={"x": position, "y": 4},
                  body_after=body.copy(), effects={})
    if before is not None:
        result["body_before"] = before
    return result

events = [
    cmd("c1", 1, "boire", {"source": "local"}), outcome("t1", 1, 2, dict(
        energy=35, food=70, water=55, integrity=90)),
    cmd("c2", 2, "dormir", {}), outcome("t2", 2, 2),
    cmd("c3", 3, "deplacer", {"direction": "north"}),
    outcome("t3", 3, 3, dict(
        energy=40, food=72, water=65, integrity=91)),
]
rows = m.closed_applied_action_witnesses(autobiography=events, now=4)
assert [w["primitive"] for w in rows] == ["boire", "dormir", "deplacer"]
assert rows[0]["parameters"] == {"source": "local"}
assert rows[0]["same_step_body_delta"]["water"] == 5.0
assert rows[1]["body_before"] is None
assert rows[1]["same_step_body_delta"] is None
assert rows[2]["position_after"] == {"x": 3, "y": 4}
assert rows[2]["same_step_body_delta"]["energy"] == -5.0
assert all(w["decision_evidence"] is False and
           w["causal_attribution"] is False for w in rows)
assert m.closed_applied_action_witnesses(
    autobiography=events, now=4, primitive="boire"
) == (rows[0],)
assert [w["step"] for w in m.closed_applied_action_witnesses(
    autobiography=events, now=3)] == [1, 2]
assert [w["step"] for w in m.closed_applied_action_witnesses(
    autobiography=events, now=4, limit=1)] == [3]
assert m.closed_applied_action_witnesses(
    autobiography=events, now=1) == ()
# Copies may be freely mutated without writing into Memory source ownership.
rows[0]["body_after"]["water"] = -100
assert m.closed_applied_action_witnesses(
    autobiography=events, now=4)[0]["body_after"]["water"] == 60.0
# Unknown, future, unclosed or missing source is not a personal witness.
m._episodes = [episode(0, ("c1", "t1")), episode(1, ("c2", "t2"))]
assert [w["step"] for w in m.closed_applied_action_witnesses(
    autobiography=events, now=4)] == [1, 2]
m._episodes.append(episode(2, ("c3", "t3")))
m._seen_event_refs.remove("t3")
assert [w["step"] for w in m.closed_applied_action_witnesses(
    autobiography=events, now=4)] == [1, 2]
m._seen_event_refs.add("t3")
# Two references with the same event id, even if copied, are ambiguous.
assert [w["step"] for w in m.closed_applied_action_witnesses(
    autobiography=events + [events[0]], now=4)] == [2, 3]
m._episodes.append(episode(3, ("c2",)))
assert [w["step"] for w in m.closed_applied_action_witnesses(
    autobiography=events, now=4)] == [1, 3]
m._episodes.pop()
# Wrong same-step schema cannot acquire a prebody by inference.
wrong = [dict(e) for e in events]
wrong[1] = dict(wrong[1], body_before=dict(body, water=float("nan")))
assert [w["step"] for w in m.closed_applied_action_witnesses(
    autobiography=wrong, now=4)] == [2, 3]
wrong = [dict(e) for e in events]
wrong[1] = dict(wrong[1], hidden_oracle=True)
assert [w["step"] for w in m.closed_applied_action_witnesses(
    autobiography=wrong, now=4)] == [2, 3]
wrong = [dict(e) for e in events]
wrong[1] = dict(wrong[1], body_after={"energy": 10})
assert [w["step"] for w in m.closed_applied_action_witnesses(
    autobiography=wrong, now=4)] == [2, 3]
wrong = [dict(e) for e in events]
wrong[0] = dict(wrong[0], primitive="")
assert [w["step"] for w in m.closed_applied_action_witnesses(
    autobiography=wrong, now=4)] == [2, 3]
# Generic testimony does not alter the historical sleep/attendre contract.
sleep = m.closed_sleep_site_witnesses(
    autobiography=events, site=(2, 4), now=4)
assert len(sleep) == 1 and sleep[0]["step"] == 2
for bad in (True, 0, -1):
    try:
        m.closed_applied_action_witnesses(autobiography=events, now=bad)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid time allowed")
print("I1_526_GENERAL_CLOSED_ACTION_CONTRACT_OK")
"""
            result = subprocess.run(
                [sys.executable, "-c", program],
                env={"PYTHONPATH": str(generated)},
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0,
                             result.stdout + result.stderr)
            self.assertIn("I1_526_GENERAL_CLOSED_ACTION_CONTRACT_OK",
                          result.stdout)


if __name__ == "__main__":
    unittest.main()
