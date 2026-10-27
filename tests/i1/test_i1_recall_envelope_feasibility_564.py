"""#564: L1-only feasibility of an exact, ancient-safe recall candidate envelope.

The candidate index lives exclusively inside this test's disposable generated
I1 process. It is NOT installed in EpisodicMemory, does not alter any natural
birth, and is not exported into Memory or M11. Its role is to falsify a proposed
algorithm before anyone changes the cognitive owner or P-43 accounting.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[2]

PROGRAM = r'''
import json
import math
from bisect import bisect_right
from collections import defaultdict
from dataclasses import replace
from types import SimpleNamespace
from i1.modules.memory import EpisodicMemory, Episode, MemoryConfig


class ConservativeEnvelope:
    """Noncausal derived superset, never a truncated memory window."""

    def __init__(self, config, episodes=()):
        self.config = config
        self.records = []
        self.ends = []
        self.always = set()
        self.by_goal = defaultdict(set)
        self.by_ref = defaultdict(set)
        self.trusted = all(math.isfinite(x) and x >= 0 for x in (
            config.recall_threshold,
            config.recall_weight_recency,
            config.recall_weight_importance,
            config.recall_weight_relevance,
        )) and type(config.recall_recency_scale_steps) is int \
           and config.recall_recency_scale_steps > 0
        for episode in episodes:
            self.append(episode)

    def append(self, episode):
        ordinal = len(self.records)
        self.records.append(episode)
        if (
            not self.trusted or episode.id != "episode:" + str(ordinal)
            or type(episode.end_t_monde) is not int
            or self.ends and episode.end_t_monde < self.ends[-1]
            or not math.isfinite(episode.importance)
            or any(type(ref) is not str for ref in episode.event_refs)
            or (episode.active_goal_ref is not None
                and type(episode.active_goal_ref) is not str)
        ):
            self.trusted = False
        if not self.trusted:
            return
        self.ends.append(episode.end_t_monde)
        if (
            self.config.recall_weight_importance * episode.importance
            >= self.config.recall_threshold
        ):
            self.always.add(ordinal)
        if episode.active_goal_ref is not None:
            self.by_goal[episode.active_goal_ref].add(ordinal)
        for ref in episode.event_refs:
            self.by_ref[ref].add(ordinal)

    def select(self, *, st, t_monde):
        n = len(self.records)
        if not self.trusted or type(t_monde) is not int:
            return tuple(range(n))
        if st is None:
            goal = None
            visible = ()
        else:
            active = st.fixed.get("active_goal")
            goal = active.get("id") if isinstance(active, dict) else None
            visible = tuple(x.contribution_ref for x in st.competitive)
            if (goal is not None and type(goal) is not str
                    or any(type(ref) is not str for ref in visible)):
                return tuple(range(n))
        # With zero relevance, an episode older than the recency window
        # can qualify only if weighted importance itself reaches threshold.
        # The strict time cutoff is safe at the exactly-zero recency boundary.
        cutoff = bisect_right(
            self.ends, t_monde - self.config.recall_recency_scale_steps
        )
        selected = set(self.always)
        selected.update(range(cutoff, n))
        if goal is not None:
            selected.update(self.by_goal.get(goal, ()))
        for ref in visible:
            selected.update(self.by_ref.get(ref, ()))
        return tuple(sorted(selected))


def config(kind):
    base = MemoryConfig(
        version="i1-564-envelope-" + kind,
        prediction_error_multiplier=1.0,
        max_episode_steps=8, link_delta_steps=0,
        recall_threshold=0.55,
        recall_weight_recency=0.15,
        recall_weight_importance=0.4,
        recall_weight_relevance=0.7,
        recall_recency_scale_steps=64,
        contribution_ttl_steps=2,
    )
    if kind == "canonical":
        return replace(
            base, recall_threshold=0.25,
            recall_weight_recency=0.5,
            recall_weight_importance=0.25,
            recall_weight_relevance=1.0,
            recall_recency_scale_steps=20,
        )
    if kind == "low-relevance":
        return replace(
            base, recall_threshold=0.8,
            recall_weight_recency=0.3,
            recall_weight_relevance=0.15,
            recall_recency_scale_steps=50,
        )
    if kind == "all-eligible":
        return replace(base, recall_threshold=0.0)
    return base


def build(n, cfg):
    memory = EpisodicMemory(
        cfg, atomic_world_step_length_boundary=True)
    episodes = [
        Episode(
            id="episode:" + str(i),
            start_t_monde=i + 1,
            end_t_monde=i + 1,
            event_refs=("src:" + str(i), "common:" + str(i % 17)),
            boundary_type="max_length",
            active_goal_ref=(
                "goal:ancient" if i == 0 else
                "goal:water" if i % 19 == 1 else None),
            body_start=None, body_end=None,
            cumulative_reward=(2.0 if i % 97 == 0 else
                               0.4 if i % 11 == 0 else 0.0),
            surprise=(2.0 if i % 251 == 0 else 0.0),
            linked_previous_ref=(
                None if i == 0 else "episode:" + str(i - 1)),
        ) for i in range(n)
    ]
    memory._episodes = episodes
    memory._episode_sequence = n
    memory._seen_event_refs = {
        ref for ep in episodes for ref in ep.event_refs
    }
    return memory


def context(*, goal=None, refs=()):
    return SimpleNamespace(
        fixed={
            "active_goal": None if goal is None else {"id": goal}
        },
        competitive=tuple(
            SimpleNamespace(contribution_ref=ref) for ref in refs),
    )


def subset(original, indices):
    # L1-only disposable scorer using the exact unmodified I1 scoring
    # method, rather than a reimplementation of the scoring equation.
    result = EpisodicMemory(
        original._config, atomic_world_step_length_boundary=True)
    result._episodes = [original._episodes[i] for i in indices]
    result._episode_ids_dense = False
    result._recall_above_threshold = set(original._recall_above_threshold)
    result._last_recalled_ref = original._last_recalled_ref
    return result


metrics = []
contexts = (
    None, context(), context(goal="goal:ancient"),
    context(refs=("src:0",)),
    context(goal="goal:water", refs=("common:3",)),
    context(goal="unseen", refs=("never-visible",)),
)
for kind in ("canonical", "sparse", "low-relevance", "all-eligible"):
    cfg = config(kind)
    for n in (0, 1, 32, 128, 512, 2048):
        full = build(n, cfg)
        indexed = ConservativeEnvelope(cfg, full._episodes)
        assert indexed.trusted
        for now in (max(1, n), n + 200):
            for st in contexts:
                selected = indexed.select(st=st, t_monde=now)
                assert tuple(sorted(selected)) == selected
                assert all(0 <= i < n for i in selected)
                short = subset(full, selected)
                assert short.recall(st=st, t_monde=now) == full.recall(
                    st=st, t_monde=now,
                ), ("full rank", kind, n, now, st)
                assert short.recall(st=st, t_monde=now, limit=8) == full.recall(
                    st=st, t_monde=now, limit=8,
                ), ("bounded rank", kind, n, now, st)
        now = n + 200
        if n >= 2 and kind in ("canonical", "sparse"):
            assert 0 in indexed.select(
                st=context(goal="goal:ancient"), t_monde=now)
            assert 0 in indexed.select(
                st=context(refs=("src:0",)), t_monde=now)
        # Compare causal threshold-crossing transitions across changing
        # contexts, with exactly identical previous causal recall sets.
        for step, st in enumerate((
            None, context(goal="goal:ancient"), None,
            context(refs=("src:0",)), context(), context(goal="goal:water"),
        ), 1):
            current_t = now + step
            short = subset(full, indexed.select(st=st, t_monde=current_t))
            a = full.spontaneous_contribution(
                st=st, t_monde=current_t, cycle=1)
            b = short.spontaneous_contribution(
                st=st, t_monde=current_t, cycle=1)
            assert a == b, ("spontaneous selection", kind, n, step)
            assert (
                full._recall_above_threshold
                == short._recall_above_threshold
            ), ("threshold transitions", kind, n, step)
            assert full._last_recalled_ref == short._last_recalled_ref
        # M11-style cold Memory import must derive exactly the same index;
        # the index itself is neither causal nor included in the snapshot.
        image = full.export_causal_state()
        cold = EpisodicMemory(
            cfg, atomic_world_step_length_boundary=True)
        cold.restore_causal_state(image)
        assert cold.export_causal_state() == image
        rebuilt = ConservativeEnvelope(cfg, cold._episodes)
        assert rebuilt.trusted
        for st in contexts:
            assert rebuilt.select(st=st, t_monde=now + 9) == indexed.select(
                st=st, t_monde=now + 9)
            assert cold.recall(st=st, t_monde=now + 9) == full.recall(
                st=st, t_monde=now + 9)
        sparse_count = len(indexed.select(st=context(), t_monde=now))
        metrics.append({
            "config": kind, "episodes": n,
            "candidate_count_at_old_time_no_context": sparse_count,
        })

# Unsafe imported ordering, malformed numeric weights and altered historical
# identities must select all episodes, never silently drop an old candidate.
ordinary = build(128, config("canonical"))
bad_order = list(ordinary._episodes)
bad_order[0], bad_order[1] = bad_order[1], bad_order[0]
untrusted = ConservativeEnvelope(config("canonical"), bad_order)
assert not untrusted.trusted
assert untrusted.select(st=context(), t_monde=1000) == tuple(range(128))
bad_times = list(ordinary._episodes)
bad_times[10] = replace(bad_times[10], end_t_monde=1)
untrusted = ConservativeEnvelope(config("canonical"), bad_times)
assert not untrusted.trusted
assert untrusted.select(st=context(), t_monde=1000) == tuple(range(128))
unsafe_cfg = replace(
    config("canonical"), recall_weight_relevance=float("nan"))
untrusted = ConservativeEnvelope(unsafe_cfg, ordinary._episodes)
assert not untrusted.trusted
assert untrusted.select(st=context(), t_monde=1000) == tuple(range(128))

print("I1_RECALL_ENVELOPE_L1_564=" + json.dumps({
    "evidence": "synthetic-L1-design-only",
    "engine_modified": False,
    "index_serialized": False,
    "l2_positive_not_observed": True,
    "l3_not_established": True,
    "metrics": metrics,
}, sort_keys=True))
'''


class L1ConservativeRecallEnvelope564(unittest.TestCase):
    def test_reference_equivalence_and_cold_derivation(self):
        with TemporaryDirectory() as folder:
            generated = Path(folder) / "generated"
            build = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                 "--output", str(generated)],
                cwd=ROOT, capture_output=True, text=True, timeout=180)
            self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
            env = dict(os.environ, PYTHONPATH=str(generated))
            result = subprocess.run(
                [sys.executable, "-c", PROGRAM], cwd=ROOT, env=env,
                capture_output=True, text=True, timeout=180)
            self.assertEqual(
                result.returncode, 0, result.stdout + result.stderr)
            lines = [
                x for x in result.stdout.splitlines()
                if x.startswith("I1_RECALL_ENVELOPE_L1_564=")
            ]
            self.assertEqual(len(lines), 1, result.stdout)
            report = json.loads(lines[0].split("=", 1)[1])
            self.assertEqual(report["evidence"], "synthetic-L1-design-only")
            self.assertFalse(report["engine_modified"])
            self.assertFalse(report["index_serialized"])
            self.assertEqual(len(report["metrics"]), 4 * 6)
            sample = next(x for x in report["metrics"]
                          if x["config"] == "sparse" and x["episodes"] == 2048)
            self.assertLess(
                sample["candidate_count_at_old_time_no_context"], 2048,
                "conservative selection never reduces the historical scan")
            print(lines[0])


if __name__ == "__main__":
    unittest.main()
