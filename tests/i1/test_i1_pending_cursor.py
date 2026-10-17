"""Stage10 pending-index fast cursor regression on generated natural I1 code."""
from pathlib import Path
from tempfile import TemporaryDirectory
import importlib.util
import os
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class PendingCursorTests(unittest.TestCase):
    def test_exact_parity_exception_rejects_extra_changes(self):
        spec = importlib.util.spec_from_file_location("parity", ROOT / "scripts/test_i1_artifact_parity.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        source = (ROOT / "src/i1/modules/consolidation_pending_index.py").read_bytes()
        self.assertFalse(module._approved_pending_index_cursor(source, source))
        self.assertFalse(module._approved_pending_index_cursor(source, source + b"\n# drift"))

    def test_cursor_preserves_order_after_rebuild_and_retirement(self):
        with TemporaryDirectory() as directory:
            output = Path(directory) / "generated"
            build = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_i1_fork.py"), "--output", str(output)],
                capture_output=True, text=True, check=False)
            self.assertEqual(build.returncode, 0, build.stderr)
            script = """
from i1.modules.consolidation_pending_index import ChargedPendingEpisodeIndex
from types import SimpleNamespace
idx = ChargedPendingEpisodeIndex(policy_version="p1")
payloads = {f"episode:{n}":{"id":f"episode:{n}"} for n in range(200)}
idx._pending = dict(payloads)
idx._pending_order = list(payloads)
idx._rank_cursor = 70
idx._ranked = [payloads[k] for k in list(payloads)[:70]]
idx._seen_count = 200
idx._history_version = "h:0"
idx._cut = SimpleNamespace(world_step=300)
idx._target = 200
class Budget:
    config = SimpleNamespace(step_slot_uc=8, period_capacity_uc=8,
                             operation_costs={"episode_scan":1})
    open_world_step = 300
    consumed_step_uc = 0
    consumed_period_uc = 0
    def charge(self, *, operation, count):
        assert operation == "episode_scan" and count <= 8
        self.consumed_step_uc += count
        self.consumed_period_uc += count
        return SimpleNamespace(accepted=True, count=count)
budget = Budget()
selector = SimpleNamespace(policy=SimpleNamespace(version="p1", scan_uc_per_episode=1))
read_calls = []
def forbidden_reader(start, end):
    read_calls.append((start,end))
    raise AssertionError("rank may not read unseen episode payloads")
assert idx.advance(budget=budget, episode_count=200,
                   read_paid_slice=forbidden_reader, selector=selector) == 8
assert idx._rank_cursor == 78
assert idx._ranked == list(payloads.values())[:78]
assert budget.consumed_step_uc == 8
assert not read_calls
# The indexed slice and original insertion-order slice must be exactly equal.
for cursor in (0, 1, 70, 99, 199):
    for count in (1, 7, 30):
        expected = list(idx._pending.values())[cursor:cursor + count]
        actual = [idx._pending[k] for k in idx._pending_order[cursor:cursor + count]]
        assert expected == actual
# Retirement rebuild preserves the remaining ranked order, and is uncharged
# only here in a deliberately isolated, synthetic index fixture.
for key in ("episode:0", "episode:11", "episode:180"):
    del idx._pending[key]
removed = {"episode:0", "episode:11", "episode:180"}
idx._pending_order = [k for k in idx._pending_order if k not in removed]
assert idx._pending_order == list(idx._pending)
assert len(idx._pending_order) == 197

# Exercise the real P-42 ledger, paid discovery, multi-step ranking,
# intermediate cold-state rebuild, and priced published retirement.
from i1.modules.consolidation_budget import ConsolidationBudgetConfig, ConsolidationWorkBudget
from i1.modules.consolidation_batch import BatchSelectionPolicy, ConsolidationBatchSelector
from i1.modules.consolidation_transaction import ConsolidationCut
from i1.modules.memory import Episode
from itertools import islice
import json, os, random, statistics, sys, time

episodes = [
    Episode(
        id=f"episode:{i}", start_t_monde=i+1, end_t_monde=i+1,
        event_refs=(f"event:{i}",), boundary_type="max_length",
        active_goal_ref="goal:known" if i % 3 == 0 else None,
        body_start=None, body_end=None, cumulative_reward=(i % 11) / 20,
        surprise=(i % 17) / 100, linked_previous_ref=None,
    )
    for i in range(64)
]
policy = BatchSelectionPolicy(
    version="i1-paid-rank-test-v1", maximum_episodes=5,
    consequence_reference=1.0, surprise_reference=1.0,
    recency_window_steps=256, repetition_reference=4,
    weight_consequence=1.0, weight_surprise=0.3,
    weight_recency=0.2, weight_repetition=0.1,
    ageing_gain_per_step=0.001, scan_uc_per_episode=1,
)
selector = ConsolidationBatchSelector(policy)
cut = ConsolidationCut(
    world_step=200, journal_index=3, journal_event_id="test:cut",
    journal_hash="a" * 64, history_version="h:0",
)
sleep = ConsolidationWorkBudget(ConsolidationBudgetConfig(
    version="i1-paid-rank-test-v1", period_capacity_uc=150,
    step_slot_uc=7, operation_costs={"episode_scan": 1, "index_maintenance": 1},
))
index = ChargedPendingEpisodeIndex(policy_version=policy.version)
index.begin(cut=cut, total=len(episodes))
sleep.begin_period(period_ref="test:sleep:200", entry_step=200)
step, restored, recorded_rank_refs = 200, False, []
while not index.complete:
    sleep.begin_step(world_step=step)
    rank_phase = index.seen_count == len(episodes)
    previous_rank = index._rank_cursor
    baseline = (list(islice(index._pending.values(), previous_rank, previous_rank + 7))
                if rank_phase else None)
    before_uc = sleep.consumed_period_uc
    reads = []
    def read_paid_slice(start, stop):
        assert not rank_phase, "ranking must not request new Memory reads"
        reads.append((start, stop))
        return episodes[start:stop]
    charged = index.advance(
        budget=sleep, episode_count=len(episodes),
        read_paid_slice=read_paid_slice, selector=selector,
    )
    assert 0 < charged <= 7
    assert sleep.consumed_period_uc - before_uc == charged
    assert sleep.consumed_step_uc == charged
    if rank_phase:
        assert not reads, reads
        assert index._ranked[-charged:] == baseline[:charged]
        recorded_rank_refs.extend(p["id"] for p in baseline[:charged])
    else:
        assert len(reads) == 1 and reads[0][1] - reads[0][0] == charged
    if not index.complete and charged == sleep.config.step_slot_uc:
        snapshot = index.export_causal_state()
        assert index.advance(
            budget=sleep, episode_count=len(episodes),
            read_paid_slice=read_paid_slice, selector=selector,
        ) == 0, "exhausted sleep step must not create uncharged work"
        assert index.export_causal_state() == snapshot
    if index._rank_cursor and not restored:
        snapshot = index.export_causal_state()
        restored_owner = ChargedPendingEpisodeIndex(policy_version=policy.version)
        restored_owner.restore_causal_state(snapshot)
        assert restored_owner.export_causal_state() == snapshot
        assert restored_owner._pending_order == list(restored_owner._pending)
        index, restored = restored_owner, True
    step += 1
assert restored
assert sleep.consumed_period_uc == 2 * len(episodes)
assert recorded_rank_refs == [ep.id for ep in episodes]
receipt = index.finalize(selector=selector)
reference = selector.select(
    cut=cut, episodes=episodes,
    pending_episode_refs=tuple(ep.id for ep in episodes),
    reserved_scan_uc=selector.quote_scan_uc(examined_episode_count=len(episodes)),
)
assert receipt.digest == reference.digest
assert receipt.episode_refs == reference.episode_refs
sleep.begin_step(world_step=step)
published = index.charge_committed_removal(budget=sleep, refs=receipt.episode_refs)
assert published and published.accepted
assert sleep.consumed_period_uc == 2 * len(episodes) + len(receipt.episode_refs)
index.acknowledge_published(
    refs=receipt.episode_refs, charged=published,
    source_version="h:0", new_version="h:1",
)
assert index._pending_order == list(index._pending)
assert len(index._pending_order) == len(episodes) - len(receipt.episode_refs)
post_commit = index.export_causal_state()
cold = ChargedPendingEpisodeIndex(policy_version=policy.version)
cold.restore_causal_state(post_commit)
assert cold.export_causal_state() == post_commit
assert cold._pending_order == list(cold._pending)
sleep.end_period()
print("STAGE10_PENDING_CURSOR_REAL_P42_AND_RESTORE_OK")

if os.environ.get("I1_STAGE10_BENCH") == "1":
    metrics = []
    rng = random.Random(256)
    for size in (64, 512, 4096, 16384):
        pending = {f"episode:{i}": {"id": f"episode:{i}"} for i in range(size)}
        ordered = list(pending)
        offsets = (size // 4, size // 2, 3 * size // 4)
        def former(offset):
            return list(islice(pending.values(), offset, offset + 8))
        def improved(offset):
            return [pending[k] for k in ordered[offset:offset + 8]]
        for offset in offsets:
            assert former(offset) == improved(offset)
        older, newer = [], []
        for rep in range(7):
            runners = [(former, older), (improved, newer)]
            if rep % 2:
                runners.reverse()
            for runner, values in runners:
                start = time.perf_counter_ns()
                for j in range(80):
                    runner(offsets[j % len(offsets)])
                values.append((time.perf_counter_ns() - start) / 80)
        old_ns, new_ns = statistics.median(older), statistics.median(newer)
        metrics.append({
            "pending_episodes": size,
            "old_median_us": round(old_ns / 1000, 3),
            "indexed_median_us": round(new_ns / 1000, 3),
            "ratio": round(old_ns / new_ns, 2) if new_ns else None,
        })
    print("I1_STAGE10_PENDING_BENCH_JSON " + json.dumps({
        "kind": "CPU_microbenchmark_not_cognitive_or_scientific_evidence",
        "python": sys.version.split()[0],
        "rank_slice": 8,
        "repetitions": 7,
        "operations_per_repetition": 80,
        "workloads": metrics,
    }, sort_keys=True))

print("STAGE10_PENDING_CURSOR_ORDER_OK")
"""
            p = subprocess.run(
                [sys.executable, "-c", script], capture_output=True, text=True,
                check=False, env={"PYTHONPATH": str(output),
                                  "I1_STAGE10_BENCH": os.environ.get("I1_STAGE10_BENCH", "0")})
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertIn("STAGE10_PENDING_CURSOR_ORDER_OK", p.stdout)
            self.assertIn("STAGE10_PENDING_CURSOR_REAL_P42_AND_RESTORE_OK", p.stdout)
            if os.environ.get("I1_STAGE10_BENCH") == "1":
                self.assertIn("I1_STAGE10_PENDING_BENCH_JSON ", p.stdout)
                print(p.stdout.split("I1_STAGE10_PENDING_BENCH_JSON ", 1)[1].splitlines()[0], flush=True)


if __name__ == "__main__":
    unittest.main()
