"""Verify the archived I3 Stage-6-light Git history without running any World.

This test proves Git object/parent/file integrity relative to the supplied
bundle. Git author/committer timestamps cannot prove independent pre-execution
registration. The original P3 report explicitly declares an order deviation.
"""

from __future__ import annotations

import hashlib
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
STUDY = "src/i3/docs/studies/stage6-light-preparation"
BUNDLE = REPO / STUDY / "provenance" / "stage6-light-original-2026-11-13.bundle"
BUNDLE_SHA256 = "df63fea5b1399924d537f91b0d0924283a9eadd53048983c3116d23c82a947d3"
BUNDLE_REF = "refs/heads/research/i3-stage6-light-preparation-20261113"
HEAD = "8c616c101f34e5b01b0ae42b129f5b2be30d1b9c"

# Exact original object IDs and the parent links recorded in the supplied Git
# objects. The merge has two parents; do not flatten or rewrite this history.
HISTORY = (
    ("fdc9c0f7da478a0196bf28ef010bdc0c1e875eed", ("24dadc509e3a96339def0ddb5f68c257feeabf08",)),
    ("4474d997674e52476103149bc3dd313811aa4fc7", ("fdc9c0f7da478a0196bf28ef010bdc0c1e875eed",)),
    ("3992c1fb31cb757dbec5cfe02869887734426b9c", ("4474d997674e52476103149bc3dd313811aa4fc7",)),
    ("d1437b301793858170cfc5a3e989ca44e5c79d33", ("3992c1fb31cb757dbec5cfe02869887734426b9c",)),
    ("f05a444d6bf57d75c7eff60993498ca8f3c7c73c", ("d1437b301793858170cfc5a3e989ca44e5c79d33",)),
    ("8deb1b9bb68d41313f686b440146796b485e45d2", ("f05a444d6bf57d75c7eff60993498ca8f3c7c73c",)),
    ("3a4d0390035074d38e2341220dcdb396bd79a335", ("8deb1b9bb68d41313f686b440146796b485e45d2", "3f3a7efcbaecdd7dcd8ad401185619b177762f60")),
    ("b3ab3a29c8669282cc2f79f6b60a696d11f4fad6", ("3a4d0390035074d38e2341220dcdb396bd79a335",)),
    (HEAD, ("b3ab3a29c8669282cc2f79f6b60a696d11f4fad6",)),
)

# These exact blobs must occur in their claimed source commit, AND in the
# current checkout. This prevents an arbitrary bundle with matching messages
# from being treated as a provenance record for files actually merged to main.
PINNED_FILES = (
    (HISTORY[0][0], "P3_GENE_SHIFT_DESCRIPTIVE_PREFLIGHT_2026-11-13.md", "bcd2cd57f2e932433aa252e95c988e824a947d45", "study"),
    (HISTORY[1][0], "p3_gene_shift_descriptive.py", "5dc980e0f25aec067b1e05a268e282618cf391a7", "lab"),
    (HISTORY[2][0], "P3_GENE_SHIFT_DESCRIPTIVE_RESULTS_2026-11-13.md", "952bb768811c7cdf3e67d7d1b7c13026a864335f", "study"),
    (HISTORY[3][0], "STAGE6_LIGHT_DRIFT_NULL_PREFLIGHT_2026-11-13.md", "4781476f8d63c9cc4ef227d0e65a6afb5466bdf1", "study"),
    (HISTORY[4][0], "stage6_light_drift_null.py", "1f441665bbc0fc98296cde2fab5932c5108f5301", "lab"),
    (HISTORY[5][0], "STAGE6_LIGHT_DRIFT_NULL_RESULTS_2026-11-13.md", "23b1b9b58c1c76fdd2013529ff01d7e7ba0d14c2", "study"),
    (HEAD, "STAGE6_LIGHT_PROTOCOL_DRAFT_2026-11-13.md", "b20e4d126a96f3fe323d7ec443e369ee9afd2813", "study"),
)


def _run(*args: str) -> str:
    result = subprocess.run(args, text=True, capture_output=True, check=False, timeout=45)
    if result.returncode:
        raise AssertionError(
            f"Command returned {result.returncode}: {' '.join(args)}\n{result.stderr[-2000:]}"
        )
    return result.stdout.strip()


def _parents(raw_commit: str) -> tuple[str, ...]:
    return tuple(line[7:] for line in raw_commit.splitlines() if line.startswith("parent "))


def _relative_path(name: str, kind: str) -> str:
    if kind == "study":
        return f"{STUDY}/{name}"
    if kind == "lab":
        return f"src/i3/lab/{name}"
    raise AssertionError(f"Unexpected file kind: {kind}")


class Stage6OriginalBundleProvenanceTests(unittest.TestCase):
    def test_source_bundle_commit_chain_and_frozen_files(self) -> None:
        self.assertTrue(BUNDLE.is_file(), "original Git bundle must be archived in source")
        self.assertEqual(hashlib.sha256(BUNDLE.read_bytes()).hexdigest(), BUNDLE_SHA256)
        self.assertEqual(HISTORY[-1][0], HEAD)

        # A private bare clone uses the checkout's existing Git objects via
        # alternates. Importing the bundle cannot alter HEAD or worktree state.
        with tempfile.TemporaryDirectory(prefix="i3-stage6-source-history-") as directory:
            isolated = Path(directory) / "objects"
            _run("git", "clone", "--bare", "--shared", "--quiet", str(REPO), str(isolated))
            _run("git", "-C", str(isolated), "bundle", "verify", str(BUNDLE))
            _run(
                "git", "-C", str(isolated), "fetch", "--quiet", "--no-tags",
                str(BUNDLE), f"{BUNDLE_REF}:refs/heads/stage6-source-only",
            )
            self.assertEqual(_run("git", "-C", str(isolated), "rev-parse", "refs/heads/stage6-source-only"), HEAD)

            for sha, parents in HISTORY:
                with self.subTest(commit=sha):
                    self.assertEqual(_run("git", "-C", str(isolated), "cat-file", "-t", sha), "commit")
                    raw = _run("git", "-C", str(isolated), "cat-file", "-p", sha)
                    self.assertEqual(_parents(raw), parents)

            for sha, filename, expected_blob, kind in PINNED_FILES:
                path = _relative_path(filename, kind)
                with self.subTest(path=path, historical_commit=sha):
                    self.assertEqual(
                        _run("git", "-C", str(isolated), "rev-parse", f"{sha}:{path}"),
                        expected_blob,
                    )
                    current_blob = _run("git", "hash-object", str(REPO / path))
                    self.assertEqual(current_blob, expected_blob)

            for before, not_yet in ((HISTORY[0][0], "src/i3/lab/p3_gene_shift_descriptive.py"),
                                    (HISTORY[3][0], "src/i3/lab/stage6_light_drift_null.py")):
                missing = subprocess.run(
                    ("git", "-C", str(isolated), "cat-file", "-e", f"{before}:{not_yet}"),
                    capture_output=True, check=False,
                )
                self.assertNotEqual(missing.returncode, 0, f"{not_yet} already existed in preflight commit")

        # This test establishes the *bundle's internal Git chronology*, not
        # independent timing of a human/agent's first execution or analysis.


if __name__ == "__main__":
    unittest.main()
