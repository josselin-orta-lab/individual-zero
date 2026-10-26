"""#543: cold M11 recovery of actual naturally published Stage10 action fragments.

Only canonical I1 births. No action scripting, motor ablation, forced sleep,
oracle feedback, or temporal rewinding. A new independent life supplies the
uninterrupted comparison at exactly the same birth and world steps.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class ColdPaidStage10Fragments543(unittest.TestCase):
    def test_natural_postpublication_cold_parity(self):
        with TemporaryDirectory() as tmp:
            generated = Path(tmp) / "generated"
            built = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                 "--output", str(generated)],
                cwd=ROOT, capture_output=True, text=True, timeout=90,
            )
            self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
            code = r"""
from pathlib import Path
from tempfile import TemporaryDirectory
from run_i1_world_preset import load_preset, _birth_parameters
from i1lab.i1_birth import birth_i1_m11, recover_i1_m11
from i1lab.i1_natural_runtime import I1Runtime
from i1lab.sqlite_life_store import SQLiteLifeLedger
from i1.modules.paid_action_consolidation import validate_published_fragments

preset, _ = load_preset("oasis")
params, _ = _birth_parameters(preset)
identity = "i1:stage10:m11:real:543"
def factory():
    return I1Runtime(
        birth_life_id=identity, autonomous_mortal=True,
        m11_sqlite_custody=True, wal_path=None, **params,
    )
with TemporaryDirectory() as home:
    continuous_path = str(Path(home) / "continuous.sqlite")
    cold_path = str(Path(home) / "cold.sqlite")
    with birth_i1_m11(db_path=continuous_path,life_id=identity,**params) as live:
        for t in range(100):
            receipt=live.run_step()
            if receipt.status != "active":
                raise AssertionError("life terminated before paid Stage10 witness")
            history=live._runtime.slow_history.read_committed()
            fragments=history.get("lived_action_fragments",[])
            if fragments:
                break
        else:
            raise AssertionError("no naturally published action fragment within 100 steps")
        assert validate_published_fragments(fragments)
        observed_steps = receipt.world_step
        before_history=live._runtime.slow_history.export_causal_state()
        before_journal=live._runtime.journal.head_hash
        before_refs=live._runtime.slow_history.committed_episode_refs()
        after=live.run_step()
        assert after.status == "active"
        after_history=live._runtime.slow_history.export_causal_state()
        after_journal=live._runtime.journal.head_hash
        assert live._runtime.journal.verify()
    with birth_i1_m11(db_path=cold_path,life_id=identity,**params) as life:
        for _ in range(observed_steps):
            receipt=life.run_step()
            assert receipt.status=="active"
        assert life._runtime.slow_history.export_causal_state()==before_history
        assert life._runtime.journal.head_hash==before_journal
        assert life._runtime.slow_history.committed_episode_refs()==before_refs
    audit=SQLiteLifeLedger.audit_read_only(
        path=cold_path, expected_individual_id=identity)
    assert audit.journal_head==before_journal and audit.may_recover
    with recover_i1_m11(
        db_path=cold_path,life_id=identity,runtime_factory=factory
    ) as resumed:
        assert resumed._runtime.slow_history.export_causal_state()==before_history
        assert resumed._runtime.slow_history.committed_episode_refs()==before_refs
        assert resumed._runtime.journal.head_hash==before_journal
        restored=resumed._runtime.slow_history.read_committed().get("lived_action_fragments",[])
        assert restored==fragments
        assert validate_published_fragments(restored)
        after_cold=resumed.run_step()
        assert after_cold.status==after.status=="active"
        assert resumed._runtime.journal.head_hash==after_journal
        assert resumed._runtime.slow_history.export_causal_state()==after_history
        assert resumed._runtime.journal.verify()
print("I1_543_REAL_POSTCOMMIT_M11_COLD_PARITY_OK")
"""
            env = os.environ.copy()
            env["PYTHONPATH"] = os.pathsep.join(
                (str(generated), str(ROOT / "src"), str(ROOT / "tools"))
            )
            proc = subprocess.run(
                [sys.executable, "-c", code], cwd=ROOT, env=env,
                capture_output=True, text=True, timeout=330,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + "\n" + proc.stderr)
            self.assertIn("I1_543_REAL_POSTCOMMIT_M11_COLD_PARITY_OK", proc.stdout)


if __name__ == "__main__":
    unittest.main()
