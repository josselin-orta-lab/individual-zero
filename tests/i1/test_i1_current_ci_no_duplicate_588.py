"""#588: retain every I1 test while refusing redundant targeted CI steps.

This checks workflow source, not the scientific efficacy of an I1 run.
No extra dependency on a YAML parser: the registered workflow's normal
job-step indentation is an explicit, fail-closed part of this check.
"""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/i1-current-ci.yml"
ENGINE = ROOT / "src/i1/engine.json"
TESTS = ROOT / "tests/i1"
TARGET = re.compile(
    r"python -m unittest discover -s tests/i1 -p (test_[A-Za-z0-9_*.-]+\.py) -v"
)
STEP = re.compile(r"(?=^      - name: )", re.MULTILINE)
BENCH_ENV = {
    "I1_CAPTURE_BENCH", "I1_STAGE10_BENCH", "I1_AUTOBIO_BENCH",
    "I1_STAGE6_BFS_BENCH", "I1_AGENCY_INDEX_BENCH",
    "I1_AGENCY_PUBLICATION_BENCH",
}


class CurrentCiNoDuplicate588(unittest.TestCase):
    def test_single_full_discovery_retains_every_registered_i1_test(self):
        engine = json.loads(ENGINE.read_text(encoding="utf-8"))
        structure = engine["validation"]["suites"]["structure"]
        commands = [row for row in structure
                    if row[:3] == ["-m", "unittest", "discover"]]
        self.assertEqual(commands, [
            ["-m", "unittest", "discover", "-s", "tests/i1",
             "-p", "test_*.py", "-v"]
        ])
        self.assertTrue(list(TESTS.glob("test_*.py")),
                        "no tests to discover; false-green would be possible")

    def test_no_ordinary_duplicate_steps_and_six_benchmark_modes_preserved(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("python tools/run_engine_checks.py --engine I1 --suite structure --execute", workflow)
        chunks = STEP.split(workflow)
        seen = {}
        for chunk in chunks:
            found = TARGET.findall(chunk)
            if not found:
                continue
            self.assertTrue(chunk.startswith("      - name: "),
                            "targeted tests must reside in a named job step")
            self.assertEqual(len(found), 1,
                             "unexpected grouped targeted test executions")
            for env in BENCH_ENV:
                if ("          " + env + ': "1"') in chunk:
                    self.assertNotIn(env, seen, "duplicated benchmark mode")
                    seen[env] = found[0]
            self.assertTrue(any(env in chunk for env in BENCH_ENV),
                            "ordinary targeted unittest duplicates full discovery")
        self.assertEqual(set(seen), BENCH_ENV)
        self.assertEqual(len(seen), 6)
        self.assertEqual(len(set(seen.values())), 6,
                         "benchmarks must retain distinct modules")


if __name__ == "__main__":
    unittest.main()
