"""#549: natural post-Stage10 UC-paid h consultation at evaluated Stage8.

Natural I1 controls every action. A positive receipt is read-only evidence
availability, not proof of an improved choice or a subjective sleep session.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class NaturalPublishedHRecall549(unittest.TestCase):
    def test_natural_evaluated_stage8_recall_of_committed_h(self):
        with TemporaryDirectory() as tmp:
            out = Path(tmp) / "generated"
            built = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                 "--output", str(out)], cwd=ROOT,
                capture_output=True, text=True, timeout=90,
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
with TemporaryDirectory() as home:
    life = birth_i1(
        life_id="i1:stage8:h:paid:natural:549",
        wal_path=str(Path(home) / "life.wal"), **params,
    )
    kinds = ("i1_published_action_stage8_context_observed",
             "stage10_consolidation_version_activated")
    for step in range(140):
        result = life.run_step()
        events = life.journal.entries
        observed = [row for row in events
                    if row.causal_event["kind"] == kinds[0]]
        if observed or result.execution_status == "dead":
            break
    assert life.journal.verify()
    activated = {
        row.causal_event["data"]["new_history_version"]
        for row in events if row.causal_event["kind"] == kinds[1]
    }
    assert activated, "no naturally committed Stage10 history"
    assert observed, {
        "steps": step + 1, "death": result.execution_status == "dead",
        "history_version": life.slow_history.current_version,
        "published_fragments": len(life.slow_history.read_committed().get(
            "lived_action_fragments", [])),
    }
    for row in observed:
        data = row.causal_event["data"]
        assert data["owner"] == "SlowHistory"
        assert data["history_version"] in activated
        assert data["charged_operation"] == "i1_published_action_recall"
        assert data["option_ref"]
        assert data["primitive"] and isinstance(data["parameters"], dict)
        assert data["fragment_count"] >= 1
        assert data["historical_fragment_ids"] == [
            item["id"] for item in data["historical_fragments"]]
        assert data["decision_evidence"] is False
        assert data["motor_permission"] is False
        assert data["causal_attribution"] is False
        assert data["q_or_p40_augmented"] is False
        assert validate_published_fragments(data["historical_fragments"])
        for item in data["historical_fragments"]:
            assert item["primitive"] == data["primitive"]
            assert item["parameters"] == data["parameters"]
            assert item["last_step"] < item["consolidation_cut_step"]
            for ref in item["source_event_refs"]:
                assert life.journal.get(ref) is not None
print("I1_549_NATURAL_PAID_PUBLISHED_H_STAGE8_OK")
"""
            env = os.environ.copy()
            env["PYTHONPATH"] = os.pathsep.join((
                str(out), str(ROOT / "src"), str(ROOT / "tools"),
            ))
            result = subprocess.run(
                [sys.executable, "-c", program], cwd=ROOT, env=env,
                capture_output=True, text=True, timeout=330,
            )
            self.assertEqual(result.returncode, 0,
                             result.stdout + "\n" + result.stderr)
            self.assertIn("I1_549_NATURAL_PAID_PUBLISHED_H_STAGE8_OK",
                          result.stdout)


if __name__ == "__main__":
    unittest.main()
