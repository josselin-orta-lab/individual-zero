"""No external scientific trace is loaded by journal projection alone."""
from __future__ import annotations

import subprocess
import sys
import unittest

from lab.evaluation_trace import EvaluationTrace
from lab.journal_views import EvaluationTrace as LegacyEvaluationTrace
from lab.journal_views import JournalViews
from lab.journal import HashChainedJournal


class SeparatedEvaluationTraceTests(unittest.TestCase):
    def test_historical_import_is_identical_to_external_trace(self):
        self.assertIs(EvaluationTrace, LegacyEvaluationTrace)
        trace = EvaluationTrace()
        self.assertEqual(trace.append(kind="external_only", data={"x": 1}).sequence, 0)
        self.assertEqual(len(trace.records), 1)

    def test_autobiographical_journal_works_without_loading_scientific_trace(self):
        program = r'''
import importlib.abc
import sys
class BlockScientificTrace(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname in ("lab.evaluation_trace", "lab.oracle", "lab.bench"):
            raise ImportError("external scientific dependency forbidden")
        return None
sys.meta_path.insert(0, BlockScientificTrace())
from lab.journal import HashChainedJournal
from lab.journal_views import JournalViews, AutobiographicalPolicy
j = HashChainedJournal()
views = JournalViews(journal=j)
assert views.autobiographical(policies={}) == ()
assert j.verify()
assert "lab.evaluation_trace" not in sys.modules
assert "lab.oracle" not in sys.modules
assert "lab.bench" not in sys.modules
print("journal_without_scientific_trace:OK")
'''
        result = subprocess.run(
            [sys.executable, "-c", program], capture_output=True,
            text=True, timeout=40,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("journal_without_scientific_trace:OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
