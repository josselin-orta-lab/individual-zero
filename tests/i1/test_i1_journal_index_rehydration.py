"""Differential test for rebuilding I1 autobiographical indices from technical journals."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class JournalIndexRehydrationTests(unittest.TestCase):
    def test_index_order_and_projection_survive_rehydration(self):
        with TemporaryDirectory() as folder:
            out = Path(folder) / "built"
            build = subprocess.run([sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                                    "--output", str(out)], capture_output=True, text=True)
            self.assertEqual(build.returncode, 0, build.stderr)
            script = r"""
from i1lab.journal import HashChainedJournal
from i1lab.journal_views import JournalViews
from i1lab.stage7_runtime import STAGE7_AUTOBIOGRAPHICAL_POLICY as policy

for size in (0, 1, 16, 128, 512):
    j = HashChainedJournal()
    view = JournalViews(journal=j)
    for i in range(size):
        attempt = f"attempt:{i}"
        entry = j.append(event_id=f"source:{i}", causal_event={
            "kind": "command_experienced", "t_monde": i+1,
            "attempt_ref": attempt, "primitive": "move",
            "parameters": {"direction": "north"},
        })
        j.append(event_id=f"other:{i}", causal_event={
            "kind": "technical_test", "t_monde": i+1,
            "attempt_ref": attempt,
        })
        view.commit_autobiographical(
            t_monde=i+1, attempt_ref=attempt,
            event_refs=(entry.event_id,), policy=policy,
        )
    old = [entry.event_id for entry in j.entries
           if entry.causal_event.get("kind") == "auto_segment_commit"]
    fresh = JournalViews(journal=j)
    assert fresh._commit_event_ids == old
    assert fresh._commit_sequence == len(old)
    policies = {policy.version: policy}
    assert fresh.autobiographical(policies=policies) == view.autobiographical(policies=policies)
    assert j.verify()
print("I1_JOURNAL_INDEX_REHYDRATION_OK")
"""
            run = subprocess.run([sys.executable, "-c", script],
                                 env={"PYTHONPATH": str(out)}, text=True,
                                 capture_output=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertIn("I1_JOURNAL_INDEX_REHYDRATION_OK", run.stdout)


if __name__ == "__main__":
    unittest.main()
