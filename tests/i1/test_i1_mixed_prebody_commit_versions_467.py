"""#467: old and new DC-09 commitments never reinterpret each other."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class VersionedPrebodyReplayIsolation467(unittest.TestCase):
    def test_distinct_commits_and_historical_projection(self):
        with TemporaryDirectory() as tmp:
            generated = Path(tmp) / "generated"
            build = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                 "--output", str(generated)], capture_output=True, text=True)
            self.assertEqual(build.returncode, 0, build.stderr)
            code = r"""
from i1lab.journal import HashChainedJournal
from i1lab.journal_views import JournalViews
from i1lab.stage2_runtime import STAGE2_AUTOBIOGRAPHICAL_POLICY as P2
from i1lab.stage7_runtime import STAGE7_AUTOBIOGRAPHICAL_POLICY as P7
from i1lab.i1_natural_prebody_policy import LIVED_PREBODY_POLICY as NEW
journal = HashChainedJournal()
views = JournalViews(journal=journal)
before = dict(energy=25., food=55., water=60., integrity=95.)
after = dict(energy=35., food=54., water=59., integrity=95.)
def source(ref, step):
    journal.append(event_id=ref, causal_event=dict(
        emitter="world_and_body", kind="world_transition_experienced",
        t_monde=step, attempt_ref="attempt:" + str(step),
        position_after=dict(x=2, y=4), body_before=dict(before),
        body_after=dict(after), effects={},
    ))
source("old-physical", 1)
old = views.commit_autobiographical(t_monde=1, attempt_ref="attempt:1",
    event_refs=("old-physical",), policy=P7)
source("new-physical", 2)
new = views.commit_autobiographical(t_monde=2, attempt_ref="attempt:2",
    event_refs=("new-physical",), policy=NEW)
assert old.filter_version == P7.version
assert new.filter_version == NEW.version
policies = {P2.version: P2, P7.version: P7, NEW.version: NEW}
rows = views.autobiographical(policies=policies)
assert [row["event_id"] for row in rows] == ["old-physical", "new-physical"]
assert "body_before" not in rows[0]
assert rows[1]["body_before"] == before
assert rows[1]["body_after"] == after
old_only = views.autobiographical(
    policies=policies, selected_event_refs=frozenset({"old-physical"}))
assert len(old_only) == 1 and "body_before" not in old_only[0]
new_only = views.autobiographical(
    policies=policies, selected_event_refs=frozenset({"new-physical"}))
assert len(new_only) == 1 and new_only[0]["body_before"] == before
try:
    views.autobiographical(policies={P2.version: P2, P7.version: P7})
except ValueError as exc:
    assert "missing autobiographical policy version" in str(exc)
else:
    raise AssertionError("unknown policy silently reinterpreted")
assert len([e for e in journal.entries
            if e.causal_event.get("kind") == "auto_segment_commit"]) == 2
print("I1_467_MIXED_DC09_REPLAY_ISOLATION_OK")
"""
            x = subprocess.run([sys.executable, "-c", code],
                env={"PYTHONPATH": str(generated)},
                capture_output=True, text=True)
            self.assertEqual(x.returncode, 0, x.stderr)
            self.assertIn("I1_467_MIXED_DC09_REPLAY_ISOLATION_OK", x.stdout)


if __name__ == "__main__":
    unittest.main()
