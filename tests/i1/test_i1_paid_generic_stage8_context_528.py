"""#528 born I1: one UC-paid closed Memory scan reaches real Stage8 options."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class GenericPaidStage8Context528(unittest.TestCase):
    def test_natural_m11_paid_generic_receipts_are_nonmotor(self):
        with TemporaryDirectory() as folder:
            generated = Path(folder) / "generated"
            build = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                 "--output", str(generated)],
                capture_output=True, text=True,
            )
            self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
            code = r"""
from pathlib import Path
from tempfile import TemporaryDirectory
from run_i1_world_preset import load_preset, _birth_parameters
from i1lab.i1_birth import birth_i1_m11

preset, _ = load_preset("empty-land")
params, _ = _birth_parameters(preset)
life_id = "i1:preset:empty-land:246:0"
with TemporaryDirectory() as tmp:
    with birth_i1_m11(db_path=str(Path(tmp)/"born.sqlite"),
                       life_id=life_id, **params) as actor:
        for step in range(53):
            receipt = actor.run_step()
            assert receipt.status == ("dead" if step == 52 else "active")
        rt = actor._runtime  # post-COMMIT M11 pointer, not pre-step runtime
        state = rt.memory.export_causal_state()
        closed = {ref for episode in state["episodes"]
                  for ref in episode["event_refs"]}
        committed = {ref for entry in rt.journal.entries
                     if entry.causal_event.get("kind") == "auto_segment_commit"
                     for ref in entry.causal_event["event_refs"]}
        assert closed <= committed
        events = [entry.causal_event for entry in rt.journal.entries]
        paid = {(e["t_monde"], e.get("cycle"))
                for e in events if e.get("kind") == "i1_sleep_site_recall_consulted"}
        generic = [e for e in events
                   if e.get("kind") == "i1_generic_lived_action_stage8_context_observed"]
        assert generic, "no natural Stage8 option matched paid autobiographical testimony"
        distinct = set()
        for event in generic:
            row = event["data"]
            assert (event["t_monde"], event["cycle"]) in paid
            assert row["charged_operation"] == "i1_closed_sleep_recall"
            assert row["new_uc_debit"] is False
            assert row["context_score_applied"] is False
            assert row["causal_attribution"] is False
            assert row["motor_admission_inherited"] is False
            assert row["witness_count"] == len(row["witnesses"]) > 0
            for witness in row["witnesses"]:
                assert witness["step"] < event["t_monde"]
                assert len(witness["source_event_refs"]) == 2
                assert set(witness["source_event_refs"]) <= closed
                assert witness["source_episode_refs"]
                assert set(witness["source_episode_refs"]) <= {
                    ep["id"] for ep in state["episodes"]}
                distinct.add(tuple(witness["source_event_refs"]))
        assert distinct
        assert not ({"operator_motor_override", "injected_reward"} &
                    {e.get("kind") for e in events})
        print("I1_528_PAID_GENERIC_STAGE8_OK", len(generic), len(distinct))
"""
            result = subprocess.run(
                [sys.executable, "-c", code],
                env={"PYTHONPATH": str(generated) + ":" + str(ROOT / "tools")},
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("I1_528_PAID_GENERIC_STAGE8_OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
