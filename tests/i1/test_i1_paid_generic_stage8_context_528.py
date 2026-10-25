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
probe.competition = S(candidate_proposals=(proposal,), is_engaged=lambda ref: ref == option.id)
probe.stage3 = S(control=S(current_step=(None, None, 0)))
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
               observed_effects={"drank": False}, same_step_body_delta=None)
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
    assert rows[0][2]["witnesses"][0]["observed_effects"] == {"drank": False}
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
    # A resumed multi-step option must match the *next* command, not
    # reuse its previously executed first step.
    second = S(command=S(primitive="manger", parameters={"target": "berries"}))
    proposal.plan.steps = (proposal.plan.steps[0], second)
    proposal.plan.id = "plan:resumable"
    probe.stage3.control.current_step = (option.id, "plan:resumable", 1)
    assert observe() == []
    probe._i1_generic_action_paid_context = dict(
        paid, witnesses=(dict(witness, primitive="manger",
                              parameters={"target": "berries"}),))
    assert len(observe()) == 1
    # Another motor option cannot inherit this continuation index.
    probe.stage3.control.current_step = ("other-option", "plan:resumable", 1)
    assert observe() == []
    probe.stage3.control.current_step = (option.id, "other-plan", 1)
    assert observe() == []
    probe.stage3.control.current_step = (option.id, "plan:resumable", 1)
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


    def test_natural_cold_recovery_preserves_paid_generic_receipts(self):
        """One real M11 life, uninterrupted versus step-28 cold recovery."""
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
from i1lab.i1_birth import birth_i1_m11, recover_i1_m11
from i1lab.i1_natural_runtime import I1Runtime
from i1lab.sqlite_life_store import SQLiteLifeLedger
preset, _ = load_preset("empty-land")
params, _ = _birth_parameters(preset)
life_id = "i1:preset:empty-land:246:0"

def factory():
    return I1Runtime(
        birth_life_id=life_id, autonomous_mortal=True,
        m11_sqlite_custody=True, wal_path=None,
        diagnostic_sample_cost_uc=1, module_occupancy_cost_uc=1,
        **params,
    )
def snapshot(rt):
    events = [row.causal_event for row in rt.journal.entries]
    generic = tuple(
        (row["t_monde"], row.get("cycle"), row["data"])
        for row in events
        if row.get("kind") == "i1_generic_lived_action_stage8_context_observed"
    )
    closed = {ref for ep in rt.memory.export_causal_state()["episodes"]
              for ref in ep["event_refs"]}
    commits = {ref for row in events if row.get("kind") == "auto_segment_commit"
               for ref in row["event_refs"]}
    assert closed <= commits
    for _, _, receipt in generic:
        for witness in receipt["witnesses"]:
            assert set(witness["source_event_refs"]) <= closed
    return (rt.journal.head_hash, rt.memory.export_causal_state(), generic)
def step(actor, count, terminal=False):
    for i in range(count):
        receipt = actor.run_step()
        expected = "dead" if terminal and i == count-1 else "active"
        assert receipt.status == expected, (receipt.status, expected)

with TemporaryDirectory() as tmp:
    straight = str(Path(tmp)/"straight.sqlite")
    cold = str(Path(tmp)/"cold.sqlite")
    with birth_i1_m11(db_path=straight, life_id=life_id, **params) as actor:
        step(actor, 28)
        midpoint = snapshot(actor._runtime)
        step(actor, 25, terminal=True)
        baseline = snapshot(actor._runtime)
    with birth_i1_m11(db_path=cold, life_id=life_id, **params) as actor:
        step(actor, 28)
        assert snapshot(actor._runtime) == midpoint
    audit = SQLiteLifeLedger.audit_read_only(
        path=cold, expected_individual_id=life_id,
    )
    assert audit.generation == 28 and audit.may_recover
    with recover_i1_m11(db_path=cold, life_id=life_id,
                         runtime_factory=factory) as actor:
        assert snapshot(actor._runtime) == midpoint
        step(actor, 25, terminal=True)
        restored = snapshot(actor._runtime)
    assert restored == baseline
    assert baseline[2], "no naturally paid general Stage8 testimony"
    final = SQLiteLifeLedger.audit_read_only(
        path=cold, expected_individual_id=life_id,
    )
    assert final.generation == 53 and final.status == "dead"
    assert not final.may_recover
    assert final.journal_head == baseline[0]
    print("I1_528_GENERIC_M11_COLD_PARITY_OK", len(baseline[2]))
"""
            result = subprocess.run(
                [sys.executable, "-c", code],
                env={"PYTHONPATH": str(generated) + ":" + str(ROOT / "tools")},
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("I1_528_GENERIC_M11_COLD_PARITY_OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
