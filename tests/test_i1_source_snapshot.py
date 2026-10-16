"""Verify I1's baseline snapshot without executing its unresolved I0 imports."""
from pathlib import Path
import unittest


class I1SnapshotTests(unittest.TestCase):
    def test_source_snapshot_is_exact_and_i0_remains_present(self):
        root = Path(__file__).resolve().parents[1] / "src"
        i0 = root / "i0"
        i1 = root / "i1"
        source = sorted(p.relative_to(i0) for p in i0.rglob("*") if p.is_file())
        copy = sorted(p.relative_to(i1) for p in i1.rglob("*") if p.is_file())
        extensions = set(copy) - set(source)
        self.assertEqual(extensions, {Path("experimental/lived_water.py")})
        self.assertEqual(source, [relative for relative in copy if relative in set(source)])
        self.assertEqual(len(source), 71)
        for relative in source:
            with self.subTest(path=str(relative)):
                self.assertEqual((i0 / relative).read_bytes(),
                                 (i1 / relative).read_bytes())

    def test_i1_is_not_yet_presented_as_an_independent_runtime(self):
        src = Path(__file__).resolve().parents[1] / "src"
        self.assertFalse((src / "i1_runtime").exists())
        self.assertTrue((src / "lab" / "stage12_runtime.py").exists())


if __name__ == "__main__":
    unittest.main()
