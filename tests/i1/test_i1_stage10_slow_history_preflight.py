"""Issue #283: exercise real natural Stage10 preflight and invalid h candidates.

Does not rewrite I1 physiology/cognition, use hidden world knowledge, or
revive any terminal identity. Every life has a new exclusive WAL path.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[2]


class I1Stage10SlowHistoryPreflightTests(unittest.TestCase):
    def test_exact_i1_parity_exception_rejects_unrelated_source_changes(self):
        spec = importlib.util.spec_from_file_location(
            "i1_parity_issue283", ROOT / "scripts/test_i1_artifact_parity.py"
        )
        parity = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(parity)
        old = (
            '        # Preflight exact staged state before touching any living owner.\n'
            '        # SlowHistory.restore_causal_state validates and detaches that state;\n'
            '        # the temporary constructor\'s birth payload is immediately discarded.\n'
            '        temp = SlowHistory(\n'
            '            birth_version=prepared.source_version,\n'
            '            birth_state={},\n'
            '        )'
        ).encode()
        new = (
            '        # Seed this throwaway validator with the genuine committed state.\n'
            '        # SlowHistory requires existing consolidated_episode_refs at birth;\n'
            '        # an invented empty mapping would crash before validation can start.\n'
            '        # The candidate is still checked before touching any living owner.\n'
            '        temp = SlowHistory(\n'
            '            birth_version=prepared.source_version,\n'
            '            birth_state=before_history["current_state"],\n'
            '        )'
        ).encode()
        self.assertTrue(parity._approved_i1_283_slow_history_preflight(old, new))
        self.assertFalse(
            parity._approved_i1_283_slow_history_preflight(old, new + b"\n# extra change")
        )
        self.assertFalse(
            parity._approved_i1_283_slow_history_preflight(old, old)
        )

    def test_malformed_staged_history_is_refused_without_mutating_existing_h(self):
        script = """from copy import deepcopy
from i1lab.consolidation_publication import SlowHistory
history = SlowHistory(
    birth_version="birth", birth_state={
        "forms": {}, "consolidated_episode_refs": ["lived-1"],
    },
)
initial = history.export_causal_state()
for bad in (
    {"forms": {}},
    {"forms": {}, "consolidated_episode_refs": ["lived-1", "lived-1"]},
):
    staged = deepcopy(initial)
    staged["current_state"] = bad
    try:
        history.restore_causal_state(staged)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid candidate was accepted")
    assert history.export_causal_state() == initial
    assert history.committed_episode_refs() == frozenset({"lived-1"})
print("SLOW_HISTORY_STAGED_CANDIDATE_REJECTION_OK")
"""
        with TemporaryDirectory(prefix="i1-283-source-") as folder:
            gen = Path(folder) / "built"
            build = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                 "--output", str(gen)],
                cwd=ROOT, capture_output=True, text=True, timeout=90,
            )
            self.assertEqual(build.returncode, 0, build.stderr)
            import os
            env = os.environ.copy()
            env["PYTHONPATH"] = str(gen) + os.pathsep + str(ROOT / "src")
            result = subprocess.run(
                [sys.executable, "-c", script], cwd=ROOT, env=env,
                capture_output=True, text=True, timeout=30,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(
                "SLOW_HISTORY_STAGED_CANDIDATE_REJECTION_OK", result.stdout
            )

    def test_real_oasis_life_reaches_stage10_publication_without_keyerror(self):
        with TemporaryDirectory(prefix="i1-283-oasis-") as folder:
            out = Path(folder) / "oasis-newborn"
            command = [
                sys.executable, str(ROOT / "tools/run_i1_world_preset.py"),
                "--preset", "oasis", "--seed", "246", "--steps", "60",
                "--lives", "1", "--custody", "wal",
                "--output-dir", str(out),
            ]
            run = subprocess.run(
                command, cwd=ROOT, capture_output=True, text=True,
                timeout=180,
            )
            self.assertEqual(
                run.returncode, 0,
                "natural life failed: " + run.stdout + "\n" + run.stderr
            )
            report = json.loads((out / "report.json").read_text(encoding="utf-8"))
            self.assertEqual(
                report["status"], "COMPLETED_WITHOUT_SCIENTIFIC_VERDICT"
            )
            self.assertEqual(len(report["lives"]), 1)
            recorded = report["lives"][0]
            self.assertGreater(len(recorded["steps"]), 0)
            wal = out / recorded["custody_file"]
            journal_events = [
                json.loads(line)["causal_event"]["kind"]
                for line in wal.read_text(encoding="utf-8").splitlines()
            ]
            self.assertIn("stage10_consolidation_version_activated", journal_events)
            self.assertIn("stage10_consolidation_committed", journal_events)
            self.assertEqual(report["scientific_gate"], "NOT_EVALUATED")


if __name__ == "__main__":
    unittest.main()
