"""#467 contract only: bounded sleep-site recall, no natural L2/L3 claim."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class ClosedSleepWitnessTests(unittest.TestCase):
    def test_bounded_closed_episode_pairs_and_negative_controls(self):
        with TemporaryDirectory() as folder:
            generated = Path(folder) / "generated"
            build = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                 "--output", str(generated)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(build.returncode, 0, build.stderr)
            program = r"""
from i1.modules.memory import EpisodicMemory, Episode

memory = object.__new__(EpisodicMemory)
def episode(n, refs):
    return Episode(id=f"episode:{n}", start_t_monde=n,
        end_t_monde=n, event_refs=tuple(refs), boundary_type="max_length",
        active_goal_ref=None, body_start=None, body_end=None,
        cumulative_reward=0.0, surprise=0.0, linked_previous_ref=None)
memory._episodes = [
    episode(0, ("c1", "t1")),
    episode(1, ("c2",)),
    episode(2, ("t2",)),
    episode(3, ("c3", "t3")),
]
memory._seen_event_refs = set(("c1", "t1", "c2", "t2", "c3", "t3"))
assert memory.closed_sleep_recall_source_refs() == frozenset({
    "c1", "t1", "c2", "t2", "c3", "t3",
})
def command(ref, step):
    return dict(event_id=ref, kind="command_experienced",
                t_monde=step, primitive="dormir", parameters={})
def outcome(ref, step, x, energy):
    return dict(event_id=ref, kind="world_transition_experienced",
                t_monde=step, position_after={"x": x, "y": 4},
                body_after=dict(energy=energy, food=70, water=60,
                                integrity=90), effects={"rest": True})
events = [
    command("c1", 1), outcome("t1", 1, 2, 40),
    command("c2", 2), outcome("t2", 2, 8, 55),
    command("c3", 3), outcome("t3", 3, 2, 56),
]
a = memory.closed_sleep_site_witnesses(
    autobiography=events, site=(2, 4), now=5)
b = memory.closed_sleep_site_witnesses(
    autobiography=events, site=(8, 4), now=5)
assert [row["step"] for row in a] == [1, 3]
assert [row["step"] for row in b] == [2]
assert a[0]["site_ref"] == a[1]["site_ref"] != b[0]["site_ref"]
assert len(b[0]["source_episode_refs"]) == 2
assert a[0]["adjacent_after_state_delta"] is None
assert b[0]["adjacent_after_state_delta"] is None  # site changed A -> B
assert a[1]["adjacent_after_state_delta"] is None  # site changed B -> A
assert a[0]["previous_step_after_ref"] is None
assert all(row["body_before"] is None for row in a + b)
# Witness of adjacent same-site states, not a causal before-body claim.
events2 = [command("c1", 1), outcome("t1", 1, 2, 40),
           command("c2", 2), outcome("t2", 2, 2, 45),
           command("c3", 3), outcome("t3", 3, 2, 56)]
same = memory.closed_sleep_site_witnesses(
    autobiography=events2, site=(2, 4), now=5)
assert same[1]["adjacent_after_state_delta"] == dict(
    energy=5.0, food=0.0, water=0.0, integrity=0.0)
assert same[1]["previous_step_after_ref"] == "t1"
assert same[1]["previous_step_after_episode_ref"] == "episode:0"
assert same[1]["body_before"] is None
balance = memory.describe_closed_sleep_site(witnesses=same, site=(2, 4))
assert balance["witness_count"] == 3
assert balance["channels"]["energy"] == dict(
    increase=2, decrease=0, stable=0, unknown=1)
assert balance["channels"]["water"] == dict(
    increase=0, decrease=0, stable=2, unknown=1)
assert balance["decision_evidence"] is False
assert balance["causal_attribution"] is False
assert balance["continuous_sleep_session"] is None
assert memory.describe_closed_sleep_site(
    witnesses=same, site=(8, 4))["witness_count"] == 0
assert memory.describe_closed_sleep_site(
    witnesses=list(same) + [same[1]], site=(2, 4)
)["witness_count"] == 3
contradictory = [dict(same[1],
    source_event_refs=("other:c", "other:t"),
    adjacent_after_state_delta=dict(
        energy=-3.0, food=-2.0, water=-1.0, integrity=-4.0))]
mixed = memory.describe_closed_sleep_site(
    witnesses=list(same) + contradictory, site=(2, 4))
assert mixed["channels"]["energy"]["increase"] == 2
assert mixed["channels"]["energy"]["decrease"] == 1
invalid = [dict(same[1], source_event_refs=("bad:c", "bad:t"),
    adjacent_after_state_delta=dict(energy=float("nan"),
        food=1, water=1, integrity=1))]
unknown = memory.describe_closed_sleep_site(
    witnesses=invalid, site=(2, 4))
assert all(unknown["channels"][k]["unknown"] == 1
           for k in ("energy", "food", "water", "integrity"))

assert all(row["body_before"] is None
           and row["continuous_sleep_session"] is None for row in a + b)
assert memory.closed_sleep_site_witnesses(
    autobiography=events, site=(2, 4), now=3)[0]["step"] == 1
assert memory.closed_sleep_site_witnesses(
    autobiography=events, site=(2, 4), now=1) == ()
assert memory.closed_sleep_site_witnesses(
    autobiography=events + [events[0]], site=(2, 4), now=5)[0]["step"] == 3
memory._episodes.append(episode(4, ("c3",)))
assert [row["step"] for row in memory.closed_sleep_site_witnesses(
    autobiography=events, site=(2, 4), now=5)] == [1]
memory._episodes.pop()
# Older duplicate must invalidate a selected recent source even after
# the 256-ref exposure cap. Excessive scanning fails closed entirely.
memory._episodes = [episode(0, ("c1", "t1"))] + [
    episode(i + 1, tuple(f"noise:{i}:{j}" for j in range(10)))
    for i in range(28)
] + [episode(30, ("c1", "c3", "t3"))]
memory._seen_event_refs.update(
    ref for ep in memory._episodes for ref in ep.event_refs)
assert "c1" not in memory.closed_sleep_recall_source_refs()
memory._episodes = [episode(0, ("c1", "t1", "c2", "t2", "c3", "t3"))]
memory._episodes.append(episode(1, tuple(
    f"many:{i}" for i in range(4097))))
memory._seen_event_refs.update(f"many:{i}" for i in range(4097))
assert not memory.closed_sleep_recall_source_refs()
memory._episodes = [episode(0, ("c1", "t1")),
                    episode(1, ("c2",)), episode(2, ("t2",)),
                    episode(3, ("c3", "t3"))]
memory._seen_event_refs.remove("c3")
assert [row["step"] for row in memory.closed_sleep_site_witnesses(
    autobiography=events, site=(2, 4), now=5)] == [1]
memory._episodes = [
    episode(0, ("c1", "t1")), episode(1, ("c2",)),
    episode(2, ("t2",)), episode(3, ("c3", "t3")),
]
memory._seen_event_refs = set(("c1", "t1", "c2", "t2", "c3", "t3"))
# Authorized new DC-09 projection may preserve same-step pre-action
# state, separately from adjacent after->after contextual observations.
events_new = [dict(item) for item in events]
events_new[1]["body_before"] = dict(energy=35,food=72,water=61,integrity=90)
new = memory.closed_sleep_site_witnesses(
    autobiography=events_new, site=(2,4), now=5)
assert new[0]["body_before"] == dict(
    energy=35.0,food=72.0,water=61.0,integrity=90.0)
assert new[0]["same_step_body_delta"] == dict(
    energy=5.0,food=-2.0,water=-1.0,integrity=0.0)
assert all(item["same_step_body_delta"] is None for item in a + b)
invalid_new = [dict(item) for item in events_new]
invalid_new[1] = dict(events_new[1], body_before=dict(
    energy=float("nan"),food=72,water=61,integrity=90))
assert memory.closed_sleep_site_witnesses(
    autobiography=invalid_new, site=(2,4), now=5) == (
    memory.closed_sleep_site_witnesses(
        autobiography=events, site=(2,4), now=5)[-1],
)
print("I1_467_CLOSED_SITE_CONTRACT_OK")
"""
            result = subprocess.run(
                [sys.executable, "-c", program],
                env={"PYTHONPATH": str(generated)},
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("I1_467_CLOSED_SITE_CONTRACT_OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
