"""Guard I0 source integrity while allowing I1 to evolve independently.

The fixed I0 Git tree is a SOFTWARE baseline, not a scientific reference
for the validity of I1 behavior. I1 intentionally forks and optimizes modules.
"""
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[2]
I0_SOURCE_TREE = "e1c30c78e1f8c89339b6616c1808508d2265bf68"


class I1SnapshotTests(unittest.TestCase):
    def test_i0_reference_source_tree_is_unchanged(self):
        tree = subprocess.run(
            ["git", "rev-parse", "HEAD:src/i0"],
            cwd=ROOT, capture_output=True, text=True, check=True,
        ).stdout.strip()
        self.assertEqual(tree, I0_SOURCE_TREE, "I0 reference tree was modified")
        worktree = subprocess.run(
            ["git", "diff", "--exit-code", "HEAD", "--", "src/i0"],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        self.assertEqual(worktree.returncode, 0, worktree.stdout + worktree.stderr)

    def test_i1_is_an_independent_source_fork(self):
        src = ROOT / "src"
        i0, i1 = src / "i0", src / "i1"
        inherited = {p.relative_to(i0) for p in i0.rglob("*.py") if p.is_file()}
        present = {p.relative_to(i1) for p in i1.rglob("*.py") if p.is_file()}
        self.assertTrue(inherited.issubset(present), inherited - present)
        self.assertIn(Path("experimental/lived_water.py"), present - inherited)
        # A byte-for-byte I0 equality check is invalid for the active I1
        # fork: its own causal and memory implementations may diverge.
        self.assertNotEqual(
            (i0 / "modules/causal_model.py").read_bytes(),
            (i1 / "modules/causal_model.py").read_bytes(),
        )
        self.assertTrue((src / "i1" / "runtime" / "i1_natural_runtime.py").is_file())

    def test_generated_i1_runtime_does_not_replace_lab(self):
        src = ROOT / "src"
        self.assertFalse((src / "i1_runtime").exists())
        self.assertTrue((src / "i1" / "lab" / "stage12_runtime.py").is_file())
        self.assertTrue((ROOT / "archive/i0/lab/stage12_runtime.py").is_file())
        self.assertFalse((src / "lab").exists())


if __name__ == "__main__":
    unittest.main()
