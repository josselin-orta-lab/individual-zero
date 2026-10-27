"""#562: first-ingestion operator index exactness and malformed history guards."""
import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from i1_m11_ingestion_delta import update_first_memory_ingestion


class IngestionDelta562(unittest.TestCase):
    def test_first_steps_and_duplicate_sources(self):
        history = {}
        seen = set()
        for step, additions in enumerate((("a", "b"), (), ("c",), ("c", "d"), ()), 1):
            seen.update(additions)
            before = dict(history)
            novel = update_first_memory_ingestion(history, set(seen), world_step=step)
            self.assertEqual(novel, len(seen - before.keys()))
        self.assertEqual(history, {"a": 1, "b": 1, "c": 3, "d": 4})

    def test_parity_with_full_historical_scan(self):
        for size in (0, 1, 2, 32, 128, 512):
            index = {}
            reference = {}
            seen = set()
            for step in range(1, size + 1):
                seen.update((f"c:{step}", f"t:{step}"))
                update_first_memory_ingestion(index, set(seen), world_step=step)
                for ref in seen:
                    reference.setdefault(ref, step)
                self.assertEqual(index, reference)

    def test_regression_and_malformed_inputs_do_not_mutate_index(self):
        first = {"a": 1, "b": 2}
        for seen in ({"a"}, {"a", "b", ""}, {"a", "b", 5}):
            with self.subTest(seen=seen), self.assertRaises(RuntimeError):
                update_first_memory_ingestion(first, seen, world_step=3)
            self.assertEqual(first, {"a": 1, "b": 2})
        for step in (0, -1, True, "3"):
            with self.subTest(step=step), self.assertRaises(RuntimeError):
                update_first_memory_ingestion(first, {"a", "b"}, world_step=step)
        self.assertEqual(first, {"a": 1, "b": 2})


if __name__ == "__main__":
    unittest.main()
