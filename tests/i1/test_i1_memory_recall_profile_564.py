"""#564: profile the authentic generated Memory source, not synthetic CPU models.

Synthetic closed episodes are an L1 workload. They are never injected into a
naturally born I1 life and do not constitute L2/L3 evidence. Timing is
informational only; exact score/threshold/cold parity is the actual test.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[2]

PROGRAM = r"""
import json
from statistics import median
from time import perf_counter_ns
from types import SimpleNamespace
from i1.modules.memory import (
    EpisodicMemory, Episode, MemoryConfig, RecallResult,
)


def config():
    return MemoryConfig(
        version="i1-memory-recall-564-work-profile",
        prediction_error_multiplier=1.0, max_episode_steps=8,
        link_delta_steps=0, recall_threshold=0.55,
        recall_weight_recency=0.15,
        recall_weight_importance=0.4,
        recall_weight_relevance=0.7,
        recall_recency_scale_steps=64, contribution_ttl_steps=2,
    )


class CountingEpisodes(list):
    def __init__(self, values):
        super().__init__(values)
        self.inspected = 0

    def __iter__(self):
        for episode in super().__iter__():
            self.inspected += 1
            yield episode


class CountingMemory(EpisodicMemory):
    def __init__(self):
        super().__init__(config(), atomic_world_step_length_boundary=True)
        self.relevance_calls = 0

    def _relevance(
        self, episode, st, current_refs=None, active_goal_id=...,
    ):
        self.relevance_calls += 1
        return super()._relevance(
            episode, st, current_refs, active_goal_id,
        )


def build(n):
    memory = CountingMemory()
    episodes = []
    for i in range(n):
        episodes.append(Episode(
            id="episode:" + str(i),
            start_t_monde=i + 1, end_t_monde=i + 1,
            event_refs=("src:" + str(i),),
            boundary_type="max_length",
            active_goal_ref=("goal:water" if i % 19 == 1 else None),
            body_start=None, body_end=None,
            cumulative_reward=(0.9 if i % 11 == 0 else 0.0),
            surprise=(4.0 if i == 0 else 0.0),
            linked_previous_ref=(
                None if i == 0 else "episode:" + str(i - 1)),
        ))
    memory._episodes = CountingEpisodes(episodes)
    memory._episode_sequence = n
    memory._seen_event_refs = set(
        ref for episode in episodes for ref in episode.event_refs)
    return memory


def exhaustive_reference(memory, st, t):
    # Independent exact mathematical equation; no prefilter or heap.
    cfg = memory._config
    refs = (
        None if st is None
        else {item.contribution_ref for item in st.competitive}
    )
    active = None if st is None else st.fixed.get("active_goal")
    active_id = active.get("id") if isinstance(active, dict) else None
    result = []
    for episode in memory._episodes:
        recency = max(
            0.0, 1.0 - max(0, t - episode.end_t_monde)
            / cfg.recall_recency_scale_steps,
        )
        importance = abs(episode.cumulative_reward) + episode.surprise
        relevance = (
            0.0 if st is None else float(
                episode.active_goal_ref is not None
                and episode.active_goal_ref == active_id
                or bool(refs and not refs.isdisjoint(episode.event_refs))
            )
        )
        score = (
            cfg.recall_weight_recency * recency
            + cfg.recall_weight_importance * importance
            + cfg.recall_weight_relevance * relevance
        )
        if score >= cfg.recall_threshold:
            result.append(RecallResult(
                episode.id, score, recency, importance, relevance,
            ))
    return tuple(sorted(
        result, key=lambda item: (-item.score, item.episode_ref),
    ))


situated = SimpleNamespace(
    fixed={"active_goal": {"id": "goal:water"}},
    competitive=(SimpleNamespace(contribution_ref="src:1"),),
)
metrics = []
for n in (0, 1, 32, 128, 512, 2048):
    memory = build(n)
    t = n + 100
    for st in (None, situated):
        expected = exhaustive_reference(memory, st, t)
        memory._episodes.inspected = 0
        memory.relevance_calls = 0
        full = memory.recall(st=st, t_monde=t)
        assert full == expected, ("full recall parity", n, st)
        assert memory._episodes.inspected == n
        memory._episodes.inspected = 0
        bounded = memory.recall(st=st, t_monde=t, limit=8)
        assert bounded == expected[:8], ("bounded recall parity", n, st)
        assert memory._episodes.inspected == n

    # Exact causal state transition, including newly eligible ancient refs.
    for st in (None, situated, None, situated):
        previous = set(memory._recall_above_threshold)
        expected = exhaustive_reference(memory, st, t)
        newly = next(
            (item for item in expected
             if item.episode_ref not in previous), None,
        )
        memory._episodes.inspected = 0
        memory.relevance_calls = 0
        contribution = memory.spontaneous_contribution(
            st=st, t_monde=t, cycle=1,
        )
        assert memory._episodes.inspected == n
        assert memory._recall_above_threshold == {
            item.episode_ref for item in expected
        }
        assert (None if contribution is None
                else contribution.payload["episode_ref"]) == (
                    None if newly is None else newly.episode_ref
                ), ("threshold-crossing parity", n)
        if contribution is not None:
            assert contribution.payload["score"] == newly.score

    # The threshold-crossing set is causal: M11 cold replay cannot repeat a
    # transition that was already observed before committing the snapshot.
    snapshot = memory.export_causal_state()
    cold = CountingMemory()
    cold.restore_causal_state(snapshot)
    assert cold.export_causal_state() == snapshot
    for st in (None, situated):
        original = memory.spontaneous_contribution(
            st=st, t_monde=t, cycle=1,
        )
        restored = cold.spontaneous_contribution(
            st=st, t_monde=t, cycle=1,
        )
        assert original == restored, ("M11 cold recall parity", n)
        assert (
            memory._recall_above_threshold
            == cold._recall_above_threshold
        )

    # Work measurement: authentic source, informational timing only.
    samples = []
    for _ in range(9):
        memory._episodes.inspected = 0
        memory.relevance_calls = 0
        start = perf_counter_ns()
        admitted = tuple(memory._iter_scored_recall(
            st=situated, t_monde=t,
        ))
        elapsed = perf_counter_ns() - start
        assert memory._episodes.inspected == n
        samples.append({
            "elapsed_ns": elapsed,
            "episodes_inspected": memory._episodes.inspected,
            "symbolic_relevance_calls": memory.relevance_calls,
            "admitted": len(admitted),
            "threshold_set_size": len(memory._recall_above_threshold),
        })
    metrics.append({
        "n": n,
        "median_ns": int(median(x["elapsed_ns"] for x in samples)),
        "episodes_inspected": samples[-1]["episodes_inspected"],
        "symbolic_relevance_calls": samples[-1]["symbolic_relevance_calls"],
        "admitted": samples[-1]["admitted"],
        "threshold_set_size": samples[-1]["threshold_set_size"],
    })
print("I1_MEMORY_RECALL_PROFILE_564=" + json.dumps(
    {"workload": "synthetic-L1-only", "engine": "generated-i1",
     "time_gate": False, "samples": metrics},
    sort_keys=True,
))
"""


class GeneratedMemoryRecallWorkProfile564(unittest.TestCase):
    def test_source_recall_work_exact_parity_and_cold_restore(self):
        with TemporaryDirectory() as folder:
            target = Path(folder) / "i1-generated"
            build = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                 "--output", str(target)],
                cwd=ROOT, text=True, capture_output=True, timeout=180,
            )
            self.assertEqual(build.returncode, 0,
                             build.stdout + build.stderr)
            env = dict(os.environ, PYTHONPATH=str(target))
            test = subprocess.run(
                [sys.executable, "-c", PROGRAM], cwd=ROOT,
                env=env, text=True, capture_output=True, timeout=180,
            )
            self.assertEqual(test.returncode, 0,
                             test.stdout + test.stderr)
            lines = [line for line in test.stdout.splitlines()
                     if line.startswith("I1_MEMORY_RECALL_PROFILE_564=")]
            self.assertEqual(len(lines), 1, test.stdout)
            data = json.loads(lines[0].split("=", 1)[1])
            self.assertEqual(data["workload"], "synthetic-L1-only")
            self.assertFalse(data["time_gate"])
            self.assertEqual(
                [row["n"] for row in data["samples"]],
                [0, 1, 32, 128, 512, 2048],
            )
            for row in data["samples"]:
                self.assertEqual(row["episodes_inspected"], row["n"])
                self.assertGreaterEqual(
                    row["symbolic_relevance_calls"], 0)
                self.assertLessEqual(
                    row["symbolic_relevance_calls"], row["n"])
                self.assertGreaterEqual(row["admitted"], 0)
                self.assertLessEqual(row["admitted"], row["n"])
            print(lines[0])


if __name__ == "__main__":
    unittest.main()
