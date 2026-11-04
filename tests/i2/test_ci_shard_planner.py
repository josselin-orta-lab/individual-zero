"""CI scheduling contracts; no science, no changed I2 test assertions."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "i2_ci_shards", ROOT / "tools" / "i2_ci_shards.py")
shards = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(shards)


class Dummy:
    def __init__(self, test_id):
        self.test_id = test_id

    def id(self):
        return self.test_id


class I2CIShardPlannerTests(unittest.TestCase):
    def test_exhaustive_disjoint_stable_and_order_preserving(self):
        ids = ["test_slow.A.test_one", "test_tiny.X.test_one",
               "test_slow.A.test_two", "test_other.B.test_three",
               "test_tiny.X.test_two"]
        cases = [Dummy(value) for value in ids]
        first = shards.partition(cases)
        self.assertEqual(first, shards.partition(cases))
        self.assertEqual(set(first[0]) | set(first[1]), set(ids))
        self.assertFalse(set(first[0]) & set(first[1]))
        for group in first:
            self.assertEqual(group, [value for value in ids if value in group])
        for module in ("test_slow", "test_tiny", "test_other"):
            self.assertEqual(sum(any(name.startswith(module + ".") for name in group)
                                 for group in first), 1)

    def test_duplicate_case_is_not_silently_dropped(self):
        cases = [Dummy("test_a.A.test_same"), Dummy("test_a.A.test_same"),
                 Dummy("test_b.B.test_other")]
        with self.assertRaisesRegex(RuntimeError, "exhaustive and disjoint"):
            shards.partition(cases)

    def test_empty_or_unsplittable_suite_is_rejected(self):
        for cases in ([], [Dummy("test_a.A.test_one")]):
            with self.subTest(length=len(cases)):
                with self.assertRaisesRegex(RuntimeError, "exhaustive and disjoint"):
                    shards.partition(cases)


if __name__ == "__main__":
    unittest.main()
