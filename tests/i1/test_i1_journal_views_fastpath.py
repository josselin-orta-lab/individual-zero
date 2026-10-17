"""Compare public and prevalidated I1 autobiographical projections."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class JournalViewsFastPathTests(unittest.TestCase):
    def test_exact_projection_and_forbidden_nested_fields(self):
        with TemporaryDirectory() as d:
            out = Path(d) / "generated"
            build = subprocess.run([sys.executable, str(ROOT/"scripts/build_i1_fork.py"),
                                    "--output", str(out)], capture_output=True, text=True)
            self.assertEqual(build.returncode, 0, build.stderr)
            code = r"""
from i1lab.journal_views import AutobiographicalPolicy
from i1lab.journal import HashChainedJournal
from i1lab.stage7_runtime import STAGE7_AUTOBIOGRAPHICAL_POLICY
journal = HashChainedJournal()
policy = STAGE7_AUTOBIOGRAPHICAL_POLICY
for i in range(60):
    entry = journal.append(event_id=f"test:{i}", causal_event={
        "kind": "command_experienced", "t_monde": i,
        "primitive": "observer", "parameters": {"direction": "north"},
        "attempt_ref": f"attempt:{i}",
    })
    assert policy.project(entry) == policy._project_validated(entry)
assert policy.allowed_fields_by_kind["command_experienced"]
invalid = journal.append(event_id="test:bad", causal_event={
    "kind": "technical_hidden_oracle", "t_monde": 1, "secret": "hidden",
})
for method in (policy.project, policy._project_validated):
    try: method(invalid)
    except ValueError: pass
    else: raise AssertionError("unauthorized technical event leaked")
# Public API must still validate before accepting any direct caller's policy.
untrusted = AutobiographicalPolicy(
    version="bad", allowed_fields_by_kind={"technical_hidden_oracle": ("secret",)})
try: untrusted.project(invalid)
except ValueError: pass
else: raise AssertionError("public policy bypassed validation")
print("JOURNAL_VIEWS_FASTPATH_EQUIVALENT")
"""
            r = subprocess.run([sys.executable, "-c", code], env={"PYTHONPATH": str(out)},
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("JOURNAL_VIEWS_FASTPATH_EQUIVALENT", r.stdout)


if __name__ == "__main__":
    unittest.main()
