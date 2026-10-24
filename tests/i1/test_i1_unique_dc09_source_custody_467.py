"""#467: one physical source belongs to one committed autobiography."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class UniqueDc09SourceCustody467(unittest.TestCase):
    def test_generated_native_journal_refuses_cross_version_duplicates(self):
        with TemporaryDirectory() as tmp:
            dest = Path(tmp) / "generated"
            b = subprocess.run([sys.executable,
                str(ROOT / "scripts/build_i1_fork.py"), "--output", str(dest)],
                capture_output=True, text=True)
            self.assertEqual(b.returncode, 0, b.stderr)
            code = r"""
from i1lab.journal import HashChainedJournal
from i1lab.journal_views import JournalViews
from i1lab.stage7_runtime import STAGE7_AUTOBIOGRAPHICAL_POLICY as OLD
from i1lab.i1_natural_prebody_policy import LIVED_PREBODY_POLICY as NEW

j = HashChainedJournal()
v = JournalViews(journal=j)
def source(ref, step):
    j.append(event_id=ref, causal_event=dict(
        emitter="world_and_body", kind="world_transition_experienced",
        t_monde=step, attempt_ref="attempt:" + str(step),
        position_after=dict(x=1,y=1),
        body_before=dict(energy=20.,food=70.,water=60.,integrity=90.),
        body_after=dict(energy=30.,food=69.,water=59.,integrity=90.),
        effects={}))
source("physical:A", 1)
v.commit_autobiographical(t_monde=1,attempt_ref="attempt:1",
    event_refs=("physical:A",),policy=OLD)
try:
    v.commit_autobiographical(t_monde=1,attempt_ref="attempt:1",
        event_refs=("physical:A",),policy=NEW)
except ValueError as exc:
    assert "already committed" in str(exc)
else:
    raise AssertionError("retroactive policy upgrade of physical source")
source("physical:B", 2)
v.commit_autobiographical(t_monde=2,attempt_ref="attempt:2",
    event_refs=("physical:B",),policy=NEW)
reloaded = JournalViews(journal=j)
try:
    reloaded.commit_autobiographical(t_monde=2,attempt_ref="attempt:2",
        event_refs=("physical:B",),policy=OLD)
except ValueError:
    pass
else:
    raise AssertionError("cold restore reused already committed source")
policies={OLD.version:OLD, NEW.version:NEW}
rows=reloaded.autobiographical(policies=policies)
assert len(rows)==2
assert "body_before" not in rows[0]
assert rows[1]["body_before"]["energy"] == 20.
assert len([e for e in j.entries if e.causal_event.get("kind")
            =="auto_segment_commit"])==2
print("I1_467_UNIQUE_DC09_CUSTODY_OK")
"""
            r = subprocess.run([sys.executable,"-c",code],
                env={"PYTHONPATH":str(dest)},capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stderr)
            self.assertIn("I1_467_UNIQUE_DC09_CUSTODY_OK",r.stdout)


if __name__ == "__main__":
    unittest.main()
