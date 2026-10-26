"""#543: real natural birth publishes a nonempty paid Stage10 owner form.

This is an L1 custody test, not evidence of a learned motor effect or an
inferred beneficial consequence of sleep.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class NaturalPaidStage10Publication543(unittest.TestCase):
    def test_real_oasis_birth_publishes_authenticated_lived_fragments(self):
        with TemporaryDirectory() as directory:
            generated = Path(directory) / "generated"
            built = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                 "--output", str(generated)],
                cwd=ROOT, capture_output=True, text=True, timeout=90,
            )
            self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
            program = r"""
from pathlib import Path
from tempfile import TemporaryDirectory
from run_i1_world_preset import load_preset, _birth_parameters
from i1lab.i1_birth import birth_i1
from i1.modules.paid_action_consolidation import validate_published_fragments

preset, _ = load_preset("oasis")
params, _ = _birth_parameters(preset)
with TemporaryDirectory() as directory:
    life = birth_i1(
        life_id="i1:stage10:paid:real:543",
        wal_path=str(Path(directory) / "life.wal"), **params,
    )
    for _ in range(60):
        result = life.run_step()
        if result.execution_status == "dead":
            break
    assert life.journal.verify()
    events = life.journal.entries
    activations = [
        entry for entry in events
        if entry.causal_event["kind"] == "stage10_consolidation_version_activated"
    ]
    state = life.slow_history.read_committed()
    fragments = state.get("lived_action_fragments", [])
    assert activations, "no actual Stage10 synchronized publication"
    assert fragments, {
        "history_version": life.slow_history.current_version,
        "history_keys": sorted(state),
        "activations": len(activations),
        "physical_events": sum(
            entry.causal_event["kind"] == "world_transition_experienced"
            for entry in events),
    }
    assert validate_published_fragments(fragments)
    assert len(fragments) <= 16
    commits = [entry for entry in events
               if entry.causal_event["kind"] == "auto_segment_commit"]
    allowed = set()
    for commit in commits:
        allowed.update(commit.causal_event["event_refs"])
    for fragment in fragments:
        assert fragment["complete_subjective_session"] is False
        assert fragment["causal_attribution"] is False
        assert fragment["decision_evidence"] is False
        assert fragment["last_step"] < fragment["consolidation_cut_step"]
        for event_ref in fragment["source_event_refs"]:
            source = life.journal.get(event_ref)
            assert event_ref in allowed and source is not None
            assert source.causal_event["t_monde"] < fragment["consolidation_cut_step"]
    assert life.slow_history.current_version == activations[-1].causal_event["data"]["new_history_version"]
print("I1_543_LIVE_STAGE10_NONEMPTY_COMMITTED_OK")
"""
            env = os.environ.copy()
            env["PYTHONPATH"] = os.pathsep.join(
                (str(generated), str(ROOT / "src"), str(ROOT / "tools"))
            )
            result = subprocess.run(
                [sys.executable, "-c", program], cwd=ROOT, env=env,
                capture_output=True, text=True, timeout=210,
            )
            self.assertEqual(
                result.returncode, 0,
                result.stdout + "\n" + result.stderr,
            )
            self.assertIn(
                "I1_543_LIVE_STAGE10_NONEMPTY_COMMITTED_OK", result.stdout,
            )


if __name__ == "__main__":
    unittest.main()
