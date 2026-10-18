"""Regression #287: both authentic autobiography formats in natural sleep."""
import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]

class Stage10AuthenticAutobiographyTests(unittest.TestCase):
    def test_hazard_edge_natural_life_reaches_sleep_after_stage2_commit(self):
        with TemporaryDirectory() as tmp:
            path=Path(tmp)/"hazard"
            result=subprocess.run([sys.executable,str(ROOT/"tools/run_i1_world_preset.py"),
                "--preset","hazard-edge","--seed","246","--steps","12","--lives","1",
                "--custody","wal","--output-dir",str(path)],
                cwd=ROOT,capture_output=True,text=True,timeout=180)
            self.assertEqual(result.returncode,0,result.stdout+"\n"+result.stderr)
            report=json.loads((path/"report.json").read_text())
            self.assertEqual(report["status"],"COMPLETED_WITHOUT_SCIENTIFIC_VERDICT")
            events=[json.loads(line)["causal_event"] for line in
                    (path/"life-01.wal").read_text().splitlines()]
            self.assertIn("stage2-autobio-v1",
                {e.get("filter_version") for e in events if e.get("kind")=="auto_segment_commit"})
            self.assertIn("stage10_sleep_entered",{e["kind"] for e in events})
    def test_unregistered_version_rejected_by_autobiographical_projection(self):
        with TemporaryDirectory() as tmp:
            generated=Path(tmp)/"generated"
            build=subprocess.run([sys.executable,str(ROOT/"scripts/build_i1_fork.py"),
                "--output",str(generated)],capture_output=True,text=True,timeout=90)
            self.assertEqual(build.returncode,0,build.stderr)
            code="""from i1lab.journal import HashChainedJournal
from i1lab.journal_views import JournalViews
from i1lab.stage2_runtime import STAGE2_AUTOBIOGRAPHICAL_POLICY
journal=HashChainedJournal()
journal.append(event_id="bad",causal_event={"kind":"auto_segment_commit",
    "emitter":"journal","t_monde":1,"attempt_ref":"a",
    "event_refs":[],"filter_version":"unknown-policy"})
views=JournalViews(journal=journal)
try:
    views.autobiographical(policies={STAGE2_AUTOBIOGRAPHICAL_POLICY.version:STAGE2_AUTOBIOGRAPHICAL_POLICY})
except ValueError as error:
    assert "missing autobiographical policy version" in str(error)
else: raise AssertionError("unregistered autobiography accepted")
"""
            import os
            env=os.environ.copy();env["PYTHONPATH"]=str(generated)+os.pathsep+str(ROOT/"src")
            check=subprocess.run([sys.executable,"-c",code],env=env,capture_output=True,text=True,timeout=60)
            self.assertEqual(check.returncode,0,check.stderr)
