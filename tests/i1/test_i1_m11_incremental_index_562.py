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

    def test_readonly_index_and_failed_batch_are_atomic(self):
        sys.path.insert(0, str(ROOT / "tools"))
        from i1_m11_closed_index import ClosedSourceOccurrenceIndex
        index = ClosedSourceOccurrenceIndex()
        index.extend_committed([{"id": "episode:0", "event_refs": ["a"]}])
        view = index.before_step(episode_count=1)
        with self.assertRaises(TypeError):
            view["a"] = 99
        for malformed in (
            [{"id": "episode:1", "event_refs": ["b"]},
             {"id": "episode:1", "event_refs": ["c"]}],
            [{"id": "episode:1", "event_refs": ["b"]},
             {"id": "episode:2", "event_refs": [["unhashable"]]}],
            [{"id": "episode:0", "event_refs": ["duplicate-id"]}],
        ):
            with self.subTest(batch=malformed), self.assertRaises(ValueError):
                index.extend_committed(malformed)
            self.assertEqual(dict(view), {"a": 1})
            self.assertEqual(index.episode_count, 1)
            self.assertEqual(index.inspected_refs, 1)
        index.extend_committed([{"id": "episode:1", "event_refs": ["b"]}])
        self.assertEqual(dict(view), {"a": 1, "b": 1})

    def test_same_natural_m11_life_has_identical_full_scan_report(self):
        """The reference algorithm must produce the same complete life audit.

        Two genuinely born, identically seeded lives are executed independently,
        with only the operator-side indexing algorithm swapped. This is NOT a
        benchmark and does not assert a particular chosen behavior.
        """
        from unittest.mock import patch
        sys.path.insert(0, str(ROOT / "tools"))
        import i1_m11_closed_index
        import run_i1_world_preset as runner

        class ReferenceFullScanIndex:
            def __init__(self):
                self.episodes = []

            def before_step(self, *, episode_count):
                if episode_count != len(self.episodes):
                    raise RuntimeError("full scan reference count drift")
                occurrences = {}
                for episode in self.episodes:
                    for ref in episode["event_refs"]:
                        occurrences[ref] = occurrences.get(ref, 0) + 1
                return occurrences

            def extend_committed(self, newly_closed):
                self.episodes.extend(newly_closed)

        with TemporaryDirectory() as directory:
            def natural_run(folder, reference=False):
                out = Path(directory) / folder
                if reference:
                    with patch.object(
                        i1_m11_closed_index, "ClosedSourceOccurrenceIndex",
                        ReferenceFullScanIndex,
                    ):
                        report = runner.execute(
                            preset_name="empty-land", seed=246, steps=3,
                            lives=1, custody="m11", output_dir=out,
                        )
                else:
                    report = runner.execute(
                        preset_name="empty-land", seed=246, steps=3,
                        lives=1, custody="m11", output_dir=out,
                    )
                self.assertEqual(report["status"],
                                 "COMPLETED_WITHOUT_SCIENTIFIC_VERDICT")
                self.assertEqual(len(report["lives"]), 1)
                return report
            old = natural_run("reference", reference=True)
            new = natural_run("incremental")
            self.assertEqual(
                json.dumps(old, sort_keys=True, ensure_ascii=False),
                json.dumps(new, sort_keys=True, ensure_ascii=False),
                "incremental M11 changed a complete natural life report",
            )

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
