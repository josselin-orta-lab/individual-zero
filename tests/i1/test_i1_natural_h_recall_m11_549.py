"""#549: M11 cold parity after a naturally paid SlowHistory Stage8 recall.

A receipt from committed h is required before the cold cut. Neither run
scripts commands, alters action values, or bypasses Competition.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class NaturalPaidHRecallM11549(unittest.TestCase):
    def test_cold_recovery_preserves_paid_h_recall_and_subsequent_life(self):
        with TemporaryDirectory() as tmp:
            generated = Path(tmp) / "generated"
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
from i1lab.i1_birth import birth_i1_m11, recover_i1_m11
from i1lab.i1_natural_runtime import I1Runtime
from i1lab.sqlite_life_store import SQLiteLifeLedger
from i1.modules.paid_action_consolidation import validate_published_fragments

preset, _ = load_preset("oasis")
params, _ = _birth_parameters(preset)
identity = "i1:stage8:h:m11:real:549"
kind = "i1_published_action_stage8_context_observed"

def factory():
    return I1Runtime(
        birth_life_id=identity, autonomous_mortal=True,
        m11_sqlite_custody=True, wal_path=None,
        diagnostic_sample_cost_uc=1, module_occupancy_cost_uc=1,
        **params,
    )

def receipts(life):
    return [row.causal_event for row in life._runtime.journal.entries
            if row.causal_event["kind"] == kind]

with TemporaryDirectory() as home:
    continuous_path = str(Path(home) / "continuous.sqlite")
    cold_path = str(Path(home) / "cold.sqlite")
    with birth_i1_m11(db_path=continuous_path,life_id=identity,**params) as live:
        for _ in range(140):
            result=live.run_step()
            if receipts(live):
                break
            assert result.status=="active", "died before a charged h consultation"
        else:
            raise AssertionError("no naturally observed published-h consultation")
        initial_receipts=receipts(live)
        assert initial_receipts
        before_state=live._runtime.slow_history.export_causal_state()
        before_journal=live._runtime.journal.head_hash
        before_refs=live._runtime.slow_history.committed_episode_refs()
        before_step=result.world_step
        for ev in initial_receipts:
            data=ev["data"]
            assert data["owner"]=="SlowHistory"
            assert data["charged_operation"]=="i1_published_action_recall"
            assert data["fragment_count"]==len(data["historical_fragments"])>0
            assert data["decision_evidence"] is False
            assert data["causal_attribution"] is False
            assert data["motor_permission"] is False
            assert validate_published_fragments(data["historical_fragments"])
        next_step=live.run_step()
        assert next_step.status=="active"
        after_state=live._runtime.slow_history.export_causal_state()
        after_journal=live._runtime.journal.head_hash
        after_receipts=receipts(live)
        assert live._runtime.journal.verify()
    with birth_i1_m11(db_path=cold_path,life_id=identity,**params) as cold:
        for _ in range(before_step):
            state=cold.run_step()
            assert state.status=="active"
        assert cold._runtime.slow_history.export_causal_state()==before_state
        assert cold._runtime.slow_history.committed_episode_refs()==before_refs
        assert cold._runtime.journal.head_hash==before_journal
        assert receipts(cold)==initial_receipts
    audit=SQLiteLifeLedger.audit_read_only(
        path=cold_path, expected_individual_id=identity,
    )
    assert audit.may_recover and audit.journal_head==before_journal
    with recover_i1_m11(
        db_path=cold_path, life_id=identity, runtime_factory=factory,
    ) as resumed:
        assert resumed._runtime.slow_history.export_causal_state()==before_state
        assert resumed._runtime.journal.head_hash==before_journal
        assert resumed._runtime.slow_history.committed_episode_refs()==before_refs
        assert receipts(resumed)==initial_receipts
        observed=resumed.run_step()
        assert observed.status==next_step.status=="active"
        assert resumed._runtime.slow_history.export_causal_state()==after_state
        assert resumed._runtime.journal.head_hash==after_journal
        assert receipts(resumed)==after_receipts
        assert resumed._runtime.journal.verify()
print("I1_549_POST_RECALL_M11_COLD_PARITY_OK")
"""
            env = os.environ.copy()
            env["PYTHONPATH"] = os.pathsep.join((
                str(generated), str(ROOT / "src"), str(ROOT / "tools"),
            ))
            outcome = subprocess.run(
                [sys.executable, "-c", program], cwd=ROOT, env=env,
                capture_output=True, text=True, timeout=420,
            )
            self.assertEqual(
                outcome.returncode, 0, outcome.stdout + "\n" + outcome.stderr,
            )
            self.assertIn("I1_549_POST_RECALL_M11_COLD_PARITY_OK", outcome.stdout)


if __name__ == "__main__":
    unittest.main()
