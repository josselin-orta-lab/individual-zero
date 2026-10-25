"""#538: indexed scoped DC-09 projection cannot bypass touched custody."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class SelectedDc09Projection538(unittest.TestCase):
    def test_generated_i1_indexed_scoped_custody(self):
        with TemporaryDirectory() as folder:
            out = Path(folder)/"generated"
            build = subprocess.run([sys.executable, str(ROOT/"scripts/build_i1_fork.py"),
                                    "--output", str(out)],capture_output=True,text=True)
            self.assertEqual(build.returncode,0,build.stdout+build.stderr)
            code = r"""
from i1lab.journal import HashChainedJournal
from i1lab.journal_views import JournalViews
from i1lab.stage7_runtime import STAGE7_AUTOBIOGRAPHICAL_POLICY as P
j = HashChainedJournal()
v = JournalViews(journal=j)
for i in range(40):
    attempt = f"attempt:{i}"
    source = j.append(event_id=f"source:{i}",causal_event=dict(
        kind="command_experienced", emitter="world",
        t_monde=i+1, attempt_ref=attempt, primitive="boire",
        parameters={"target": "water"}, hidden_oracle="not lived"))
    v.commit_autobiographical(
        t_monde=i+1,attempt_ref=attempt,event_refs=(source.event_id,),
        policy=P)
policies={P.version:P}
selected=frozenset({"source:0","source:39"})
expected=v.autobiographical(policies=policies,selected_event_refs=selected)
rows=v.selected_committed_autobiography(
    policies=policies,selected_event_refs=selected)
assert rows == expected and len(rows)==2
assert all("hidden_oracle" not in row for row in rows)
cold=JournalViews(journal=j)
assert cold.selected_committed_autobiography(
    policies=policies,selected_event_refs=selected)==rows
rows[0]["parameters"]["target"]="changed"
assert v.selected_committed_autobiography(
    policies=policies,selected_event_refs=selected)==expected
assert v.selected_committed_autobiography(
    policies=policies,selected_event_refs=frozenset())==()
for bad in (frozenset({"missing"}),frozenset(str(i) for i in range(65))):
    try: v.selected_committed_autobiography(policies=policies,
                                            selected_event_refs=bad)
    except ValueError: pass
    else: raise AssertionError("uncommitted/oversized request accepted")
try: v.selected_committed_autobiography(
    policies={},selected_event_refs=selected)
except ValueError: pass
else: raise AssertionError("missing policy accepted")
# Source index derives from commitments; technical source ref cannot
# be requested by a caller who knows the ID.
j.append(event_id="technical",causal_event=dict(
    kind="technical_oracle",t_monde=41,secret="forbidden"))
try: v.selected_committed_autobiography(
    policies=policies,selected_event_refs=frozenset({"technical"}))
except ValueError: pass
else: raise AssertionError("uncommitted technical event accepted")
# The NEW scoped contract intentionally does not audit unrelated commits.
# The full historical API must retain its global provenance validation.
bad=HashChainedJournal()
bad.append(event_id="bad_commit",causal_event=dict(
    kind="auto_segment_commit", filter_version=P.version,
    t_monde=1,attempt_ref="a", event_refs=["missing"]))
corrupted=JournalViews(journal=bad)
try: corrupted.autobiographical(policies=policies,
                                 selected_event_refs=frozenset())
except ValueError: pass
else: raise AssertionError("full audit silently skipped corrupt commit")
# Touched commitments cannot hide malformed *unselected* DC-09 fields.
for invalid in ("future", "wrong_attempt", "wrong_time"):
    changed=HashChainedJournal()
    v2=JournalViews(journal=changed)
    step=51
    attempted="attempt:51"
    a=changed.append(event_id="pair:a",causal_event=dict(
        kind="command_experienced",t_monde=step,attempt_ref=attempted,
        primitive="boire",parameters={"target":"water"}))
    bad_data=dict(kind="command_experienced",
        t_monde=step,attempt_ref=attempted,
        primitive="boire",parameters={"target":"water"})
    if invalid=="wrong_attempt": bad_data["attempt_ref"]="other"
    if invalid=="wrong_time": bad_data["t_monde"]=step+1
    b=changed.append(event_id="pair:b",causal_event=bad_data)
    # The hash-chained journal is immutable: make a malformed historical
    # commitment *before* the future event rather than mutating its receipt.
    changed.append(event_id="pair:commit",causal_event=dict(
        kind="auto_segment_commit",filter_version=P.version,t_monde=step,
        attempt_ref=attempted,
        event_refs=["pair:a","future"] if invalid=="future"
                   else ["pair:a","pair:b"]))
    if invalid=="future":
        changed.append(event_id="future",causal_event=dict(
            kind="command_experienced",t_monde=step,attempt_ref=attempted,
            primitive="boire",parameters={"target":"water"}))
    v2=JournalViews(journal=changed)
    try: v2.selected_committed_autobiography(
        policies=policies,selected_event_refs=frozenset({"pair:a"}))
    except ValueError: pass
    else: raise AssertionError(("malformed touched commit",invalid))
print("I1_538_SCOPED_DC09_CUSTODY_OK")
"""
            run=subprocess.run([sys.executable,"-c",code],
                env={"PYTHONPATH":str(out)},capture_output=True,text=True)
            self.assertEqual(run.returncode,0,run.stdout+run.stderr)
            self.assertIn("I1_538_SCOPED_DC09_CUSTODY_OK",run.stdout)


if __name__=="__main__":
    unittest.main()
