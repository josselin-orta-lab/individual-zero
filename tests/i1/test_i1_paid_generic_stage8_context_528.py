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


    def test_stage8_guard_rejects_stale_mismatched_unpaid_options(self):
        """Isolate the observer-only hook; no forged signal can be scored."""
        with TemporaryDirectory() as folder:
            generated = Path(folder) / "generated"
            build = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                 "--output", str(generated)],
                capture_output=True, text=True,
            )
            self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
            code = r"""
from types import SimpleNamespace as S
from unittest.mock import patch
from i1lab.i1_natural_runtime import I1Runtime
from i1lab.i1_d2_runtime import I1WaterPrudentRuntime

probe = object.__new__(I1Runtime)
probe._cycle_degraded = False
capture = S(t_monde=10, x=3, y=4)
option = S(id="option:ordinary", version="v1", expires_at_step=11,
           motive_ref=S(type="local_opportunity"))
command = S(primitive="boire", parameters={"target": "water"})
proposal = S(option=option, plan=S(steps=(S(command=command),)))
probe.competition = S(candidate_proposals=(proposal,))
evaluation = S(option_ref=option.id, option_version="v1",
               cycle=1, t_monde=10, status="evaluated")
evidence = S(evaluation=evaluation, evidence=0.23)
inputs = {option.id: evidence}
paid = dict(step=10, cycle=1, site=(3,4),
            charged_operation="i1_closed_sleep_recall")
witness = dict(step=8, primitive="boire",
               parameters={"target": "water"},
               position_after={"x":3,"y":4},
               source_event_refs=("c8","t8"),
               source_episode_refs=("episode:8",),
               body_before=None,
               body_after={"energy":40.0, "food":60.0,
                           "water":80.0, "integrity":90.0},
               same_step_body_delta=None)
probe._i1_sleep_site_paid_context = paid.copy()
probe._i1_generic_action_paid_context = dict(paid, witnesses=(witness,))
out = []
def write(self, *, kind, cycle, data):
    out.append((kind, cycle, data))
def observe():
    out.clear()
    I1Runtime._before_competition_accumulation(
        probe, capture=capture, cycle=1, evidence_inputs=inputs)
    return [row for row in out
            if row[0] == "i1_generic_lived_action_stage8_context_observed"]
with patch.object(I1WaterPrudentRuntime,
                  "_before_competition_accumulation",
                  lambda self, **kwargs: None, create=True), \
     patch.object(I1Runtime, "_write", write, create=True):
    rows = observe()
    assert len(rows) == 1
    assert rows[0][2]["stage8_evidence_unchanged"] == 0.23
    assert rows[0][2]["witnesses"][0]["source_event_refs"] == ["c8","t8"]
    assert evidence.evidence == 0.23
    assert rows[0][2]["new_uc_debit"] is False
    # No in-cycle paid source or no current valid proposal: fail closed.
    for altered in (
        dict(paid, cycle=2),
        dict(paid, step=9),
        dict(paid, site=(9,9)),
        dict(paid, charged_operation="unpaid"),
    ):
        probe._i1_generic_action_paid_context = dict(
            altered, witnesses=(witness,))
        assert observe() == []
    probe._i1_generic_action_paid_context = None
    assert observe() == []
    probe._i1_generic_action_paid_context = dict(paid, witnesses=(witness,))
    probe._cycle_degraded = True
    assert observe() == []
    probe._cycle_degraded = False
    old = probe.competition.candidate_proposals
    probe.competition.candidate_proposals = ()
    assert observe() == []
    probe.competition.candidate_proposals = old
    old_input = inputs.pop(option.id)
    assert observe() == []
    inputs[option.id] = old_input
    old_status = evaluation.status
    evaluation.status = "not_evaluated"
    assert observe() == []
    evaluation.status = old_status
    evaluation.option_version = "old"
    assert observe() == []
    evaluation.option_version = "v1"
    evaluation.cycle = 2
    assert observe() == []
    evaluation.cycle = 1
    option.expires_at_step = 10
    assert observe() == []
    option.expires_at_step = 11
    command.primitive = "manger"
    assert observe() == []
    command.primitive = "boire"
    command.parameters = {"target": "different"}
    assert observe() == []
    command.parameters = {"target": "water"}
    assert len(observe()) == 1
print("I1_528_STAGE8_GUARD_NEGATIVE_OK")
"""
            result = subprocess.run(
                [sys.executable, "-c", code],
                env={"PYTHONPATH": str(generated) + ":" + str(ROOT / "src")},
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("I1_528_STAGE8_GUARD_NEGATIVE_OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
