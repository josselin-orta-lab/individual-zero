"""#562: the derived incremental M11 source index must preserve the natural audit."""
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[2]


class M11IncrementalClosedIndex562(unittest.TestCase):
    def test_incremental_index_matches_full_reconstruction(self):
        sys.path.insert(0, str(ROOT / "tools"))
        from i1_m11_closed_index import ClosedSourceOccurrenceIndex
        index = ClosedSourceOccurrenceIndex()
        closed = []
        generations = [
            [{"id": "episode:0", "event_refs": ["a", "b"]}],
            [],
            [{"id": "episode:1", "event_refs": []},
             {"id": "episode:2", "event_refs": ["b", "c", "c"]}],
            [{"id": "episode:3", "event_refs": ["x"]}],
        ]
        for generation in generations:
            before = {}
            for episode in closed:
                for ref in episode["event_refs"]:
                    before[ref] = before.get(ref, 0) + 1
            self.assertEqual(index.before_step(episode_count=len(closed)), before)
            with self.assertRaises(RuntimeError):
                index.before_step(episode_count=len(closed) + 1)
            index.extend_committed(generation)
            closed.extend(generation)
            after = {}
            for episode in closed:
                for ref in episode["event_refs"]:
                    after[ref] = after.get(ref, 0) + 1
            self.assertEqual(index.before_step(episode_count=len(closed)), after)
        self.assertEqual(index.inspected_refs, 6)

    def test_canonical_m11_life_with_incremental_observer_index(self):
        with TemporaryDirectory() as folder:
            output = Path(folder) / "report"
            proc = subprocess.run([
                sys.executable, str(ROOT / "tools/run_i1_world_preset.py"),
                "--preset", "empty-land", "--custody", "m11",
                "--steps", "3", "--lives", "1",
                "--output-dir", str(output),
            ], cwd=ROOT, env=os.environ.copy(), capture_output=True,
               text=True, timeout=150)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            report = json.loads((output / "report.json").read_text())
            self.assertEqual(report["status"], "COMPLETED_WITHOUT_SCIENTIFIC_VERDICT")
            self.assertEqual(len(report["lives"]), 1)
            life = report["lives"][0]
            self.assertTrue(life["steps"])
            self.assertEqual(
                life["journal_head"], life["steps"][-1]["journal_head"])
            for step in life["steps"]:
                custody = step["autobiographical_sleep_custody_467"]
                self.assertGreaterEqual(custody["memory_seen_after"],
                                        custody["memory_seen_before"])
                self.assertGreaterEqual(custody["auto_commit_count"], 0)
                self.assertIn(step["lifecycle"], ("active", "dead"))


if __name__ == "__main__":
    unittest.main()
