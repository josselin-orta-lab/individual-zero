"""#317: synthetic admission gates only; physical proof needs independent WAL lives."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from build_i1_fork import generate


class SleepAdmission317Tests(unittest.TestCase):
    def test_generated_i1_motive_independent_but_physically_gated(self):
        with TemporaryDirectory(prefix="i1-317-sleep-entry-") as directory:
            generated = Path(directory) / "generated"
            generate(generated)
            script = r"""
from dataclasses import replace
from types import SimpleNamespace
from i1.interfaces import PrimitiveCommand
from i1.modules.action_control import AdmissionResult, PreparedCommand
from i1.modules.sleep_session import SleepSession
from i1lab.stage4_runtime import Stage4StepResult
from i1lab.stage10_runtime import Stage10Runtime

command = PrimitiveCommand("dormir")
option_ref, plan_ref = "option:energy", "plan:energy"
prepared = PreparedCommand(command=command, source="decision", option_ref=option_ref)
admission = AdmissionResult(
    ok=True, reason=None, scope=None, rule_id=None, rule_type=None,
    policy_version="unit-only", command=command,
)
result = Stage4StepResult(
    source="decision", execution_status="applied", command_primitive="dormir",
    option_ref=option_ref, st_version="S_t:test", cycles_used=3,
    reflex_triggered=False, fallback_used=False,
)

def proposal(motive_type="active_goal"):
    return SimpleNamespace(
        option=SimpleNamespace(
            id=option_ref, plan_ref=plan_ref,
            motive_ref=SimpleNamespace(type=motive_type)),
        plan=SimpleNamespace(
            id=plan_ref, option_ref=option_ref,
            steps=(SimpleNamespace(command=command),)),
    )

def verify_provenance(r=result, p=prepared, q=None):
    Stage10Runtime._verify_ordinary_sleep_provenance(
        result=r, prepared=p, proposal=proposal() if q is None else q,
    )

def must_reject_provenance(r=result, p=prepared, q=None):
    try:
        verify_provenance(r, p, q)
    except RuntimeError:
        return
    raise AssertionError("invalid ordinary sleep provenance admitted")

# Motivation is explanatory, not a second admission policy. Energy-goal
# and ordinary physiological-pressure options both remain genuine choices.
for motive in ("active_goal", "sleep_pressure"):
    verify_provenance(q=proposal(motive))
    session = SleepSession(wake_policy_version="unit-only")
    assert session.open_world_step(1) == "awake"
    session.record_applied_sleep_decision(
        world_step=1, admission=admission, prepared=prepared,
        execution_status="applied",
    )
    state = session.export_causal_state()
    assert state["admitted_sleep_step"] == 1 and state["entry_step"] is None
    assert session.open_world_step(2) == "sleeping"
    assert session.entry_step == 2
    try:
        session.record_applied_sleep_decision(
            world_step=2, admission=admission, prepared=prepared,
            execution_status="applied",
        )
    except ValueError:
        pass
    else:
        raise AssertionError("sleep cannot be re-armed while sleeping")

# A selected plan must remain the very plan Action Control prepared and
# physically applied; neither a fallback nor a reflex can impersonate it.
must_reject_provenance(r=replace(result, source="fallback"))
must_reject_provenance(r=replace(result, fallback_used=True))
must_reject_provenance(r=replace(result, source="reflex"))
must_reject_provenance(r=replace(result, execution_status="dead"))
must_reject_provenance(r=replace(result, command_primitive="attendre"))
must_reject_provenance(r=replace(result, option_ref="option:other"))
must_reject_provenance(p=replace(prepared, option_ref="option:other"))
bad_plan = proposal()
bad_plan.plan.option_ref = "option:other"
must_reject_provenance(q=bad_plan)
bad_plan = proposal()
bad_plan.plan.steps = (SimpleNamespace(command=PrimitiveCommand("attendre")),)
must_reject_provenance(q=bad_plan)

# Synthetic Action Control receipts do not prove a world transition.
# Fail closed if their fields or the applied transition are absent.
invalid = (
    (replace(admission, ok=False), prepared, "applied"),
    (replace(admission, command=PrimitiveCommand("attendre")), prepared, "applied"),
    (admission, replace(prepared, source="reflex", trigger_ref="reflex:1"), "applied"),
    (admission, replace(prepared, source="sleep"), "applied"),
    (admission, replace(prepared, option_ref=None), "applied"),
    (admission, prepared, "proposed"),
    (admission, prepared, "dead"),
)
for admission_case, prepared_case, status in invalid:
    session = SleepSession(wake_policy_version="unit-only")
    session.open_world_step(1)
    try:
        session.record_applied_sleep_decision(
            world_step=1, admission=admission_case,
            prepared=prepared_case, execution_status=status,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("non-applied or non-decision sleep admitted")
    assert session.export_causal_state()["admitted_sleep_step"] is None
print("I1_317_SLEEP_ADMISSION_SYNTHETIC_PASS")
"""
            proc = subprocess.run(
                [sys.executable, "-c", script],
                env={"PYTHONPATH": str(generated) + ":" + str(ROOT / "src")},
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn(
                "I1_317_SLEEP_ADMISSION_SYNTHETIC_PASS", proc.stdout
            )


if __name__ == "__main__":
    unittest.main()
