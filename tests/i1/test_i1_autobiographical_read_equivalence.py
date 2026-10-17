"""End-to-end first-person JournalViews parity and optional CPU benchmark.

Exercise committed autobiographical segments, not only a policy.project helper.
The former per-event validation path is an independent reference. Never inject
technical/oracle events into the individual.
"""
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class AutobiographicalReadEquivalenceTests(unittest.TestCase):
    def test_segment_projections_match_strict_reference(self):
        with TemporaryDirectory(prefix="i1-autobio-reads-") as directory:
            generated = Path(directory) / "generated"
            build = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                 "--output", str(generated)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(build.returncode, 0, build.stderr)
            program = r"""
import json
import os
import statistics
import sys
import time
from i1lab.journal import HashChainedJournal
from i1lab.journal_views import JournalViews, AutobiographicalPolicy
from i1lab.stage2_runtime import STAGE2_AUTOBIOGRAPHICAL_POLICY as P2
from i1lab.stage7_runtime import STAGE7_AUTOBIOGRAPHICAL_POLICY as P7

POLICIES = {P2.version: P2, P7.version: P7}

def strict_reference(views, *, policies, selected_event_refs=None):
    # Pre-optimization contract: validate each version on every commitment,
    # validate all sources, project requested events with PUBLIC API.
    if selected_event_refs is not None and (
        type(selected_event_refs) is not frozenset
        or any(type(ref) is not str or not ref for ref in selected_event_refs)
    ):
        raise ValueError("invalid scoped autobiographical refs")
    projected = []
    for commit_event_id in views._commit_event_ids:
        entry = views._journal.get(commit_event_id)
        if entry is None:
            raise ValueError("autobiographical commit index references unknown event")
        version = entry.causal_event.get("filter_version")
        refs = entry.causal_event.get("event_refs")
        attempt = entry.causal_event.get("attempt_ref")
        t_monde = entry.causal_event.get("t_monde")
        if (entry.causal_event.get("kind") != "auto_segment_commit"
            or not isinstance(version, str)
            or not isinstance(attempt, str) or not attempt
            or type(t_monde) is not int
            or not isinstance(refs, list)
            or any(not isinstance(ref, str) for ref in refs)
            or len(refs) != len(set(refs))):
            raise ValueError("malformed AutoSegmentCommit in technical journal")
        policy = policies.get(version)
        if policy is None:
            raise ValueError("missing autobiographical policy version")
        policy.validate()
        for event_ref in refs:
            source = views._journal.get(event_ref)
            if source is None or source.index >= entry.index:
                raise ValueError("AutoSegmentCommit references missing/future event")
            if (source.causal_event.get("attempt_ref") != attempt
                or source.causal_event.get("t_monde") != t_monde
                or not policy.allows(source)):
                raise ValueError("illegal autobiographical source provenance")
            if selected_event_refs is None or event_ref in selected_event_refs:
                projected.append(policy.project(source))
    return tuple(projected)

journal = HashChainedJournal()
views = JournalViews(journal=journal)
ref_ids = []
stats = []
for limit in (16, 128, 512):
    for i in range(len(ref_ids), limit):
        policy = P2 if i % 2 else P7
        ref = f"lived:command:{i}"
        attempt = f"attempt:{i}"
        source = journal.append(event_id=ref, causal_event={
            "kind": "command_experienced",
            "emitter": "world",
            "attempt_ref": attempt,
            "t_monde": i + 1,
            "primitive": "move",
            "parameters": {"direction": ("north" if i % 3 else "south"),
                           "unapproved_but_nonoracle": 3},
            "oracle_canary": "not_autobiographical",
        })
        views.commit_autobiographical(
            t_monde=i + 1, attempt_ref=attempt,
            event_refs=(source.event_id,), policy=policy,
        )
        ref_ids.append(ref)
    selected = frozenset(ref_ids[::7])
    for scope in (None, selected, frozenset(), frozenset(ref_ids)):
        previous = strict_reference(views, policies=POLICIES,
                                    selected_event_refs=scope)
        current = views.autobiographical(policies=POLICIES,
                                        selected_event_refs=scope)
        assert current == previous, (limit, scope is None)
        assert all("oracle_canary" not in e for e in current)
        assert all("hidden_operator_truth" not in
                   e.get("parameters", {}) for e in current)
    if os.environ.get("I1_AUTOBIO_BENCH") == "1":
        earlier, faster = [], []
        for rep in range(5):
            candidates = [
                (lambda: strict_reference(views, policies=POLICIES), earlier),
                (lambda: views.autobiographical(policies=POLICIES), faster),
            ]
            if rep % 2:
                candidates.reverse()
            for callback, series in candidates:
                start = time.perf_counter_ns()
                for _ in range(3):
                    callback()
                series.append((time.perf_counter_ns() - start) / 3)
        a, b = statistics.median(earlier), statistics.median(faster)
        stats.append({
            "committed_events": limit,
            "former_median_us": round(a/1000, 2),
            "current_median_us": round(b/1000, 2),
            "speedup": round(a/b, 2) if b else None,
        })

# A denied or inconsistent commit must not disappear under a scoped request:
# all earlier commitments remain provenance-validated, even unselected.
for error_mode in ("unknown-policy", "missing-source", "wrong-attempt"):
    corrupt = HashChainedJournal()
    if error_mode == "wrong-attempt":
        corrupt.append(event_id="event:valid", causal_event={
            "kind": "command_experienced", "t_monde": 1,
            "attempt_ref": "other", "primitive": "move",
            "parameters": {"direction": "north"},
        })
        ref = "event:valid"
    else:
        ref = "event:missing"
    corrupt.append(event_id=f"commit:{error_mode}", causal_event={
        "kind": "auto_segment_commit", "t_monde": 1,
        "attempt_ref": "expected", "event_refs": [ref],
        "filter_version": "unknown" if error_mode == "unknown-policy" else P2.version,
    })
    bad = JournalViews(journal=corrupt)
    for operation in (strict_reference, JournalViews.autobiographical):
        try:
            operation(bad, policies=POLICIES, selected_event_refs=frozenset())
        except ValueError:
            pass
        else:
            raise AssertionError("invalid commit passed: " + error_mode)

# Public direct policy methods still validate custom allowed-fields rules.
invalid_policy = AutobiographicalPolicy(
    version="untrusted", allowed_fields_by_kind={
        "technical_hidden_oracle": ("secret",),
    },
)
try:
    invalid_policy.validate()
except ValueError:
    pass
else:
    raise AssertionError("unapproved technical kind validated")

if stats:
    print("I1_AUTOBIO_READ_BENCH_JSON " + json.dumps({
        "kind": "synthetic_CPU_only_no_scientific_GO",
        "python": sys.version.split()[0],
        "repetitions": 5,
        "reads_per_repetition": 3,
        "workloads": stats,
    }, sort_keys=True))
print("I1_AUTOBIO_READ_PARITY_OK")
"""
            proc = subprocess.run(
                [sys.executable, "-c", program],
                capture_output=True, text=True, check=False,
                env={"PYTHONPATH": str(generated),
                     "I1_AUTOBIO_BENCH": os.environ.get("I1_AUTOBIO_BENCH", "0")},
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("I1_AUTOBIO_READ_PARITY_OK", proc.stdout)
            if os.environ.get("I1_AUTOBIO_BENCH") == "1":
                self.assertIn("I1_AUTOBIO_READ_BENCH_JSON ", proc.stdout)
                print(proc.stdout.split("I1_AUTOBIO_READ_BENCH_JSON ", 1)[1].splitlines()[0],
                      flush=True)


if __name__ == "__main__":
    unittest.main()
