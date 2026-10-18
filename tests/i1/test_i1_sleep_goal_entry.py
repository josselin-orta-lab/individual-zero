"""Regress real I1 sleep-session motive validation from the generated fork.

Build and import exclusively in a subprocess: no I0 imports or .pyc pollution
inside the engine's source-fork structural test process.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from build_i1_fork import generate


class SleepGoalEntryTests(unittest.TestCase):
    def test_legitimate_motives_and_refusal_of_forged_commands(self):
        with TemporaryDirectory(prefix="i1-sleep-motive-") as temp:
            built = Path(temp) / "generated"
            generate(built)
            probe = """
from types import SimpleNamespace
from i0.interfaces import PrimitiveCommand
from i1.modules.sleep_session import SleepSession

def attempt(motive, *, admitted=True, applied=True, source="decision", primitive="dormir", option_ref="opt"):
    session = SleepSession(wake_policy_version="i1-goal-sleep-entry")
    assert session.open_world_step(1) == "awake"
    command = PrimitiveCommand(primitive)
    admission = SimpleNamespace(ok=admitted, command=command)
    prepared = SimpleNamespace(command=command, source=source, option_ref=option_ref)
    session.record_applied_sleep_decision(
        world_step=1, admission=admission, prepared=prepared,
        motive_type=motive, execution_status="applied" if applied else "safety_block")
    assert session.open_world_step(2) == "sleeping"

for motive in ("sleep_pressure", "active_goal"):
    attempt(motive)
for kwargs in (
    {"motive":"recovery_goal"},
    {"motive":"unknown"},
    {"motive":""},
    {"motive":"active_goal","admitted":False},
    {"motive":"active_goal","applied":False},
    {"motive":"active_goal","source":"reflex"},
    {"motive":"active_goal","primitive":"boire"},
    {"motive":"active_goal","option_ref":None},
):
    try:
        attempt(**kwargs)
    except ValueError as exc:
        assert "sleep entry requires" in str(exc)
    else:
        raise AssertionError("unadmitted or unrelated motive incorrectly entered sleep")
"""
            env = dict(os.environ)
            env["PYTHONPATH"] = os.pathsep.join((str(built), str(ROOT / "src")))
            env["PYTHONDONTWRITEBYTECODE"] = "1"
            done = subprocess.run(
                [sys.executable, "-c", probe],
                cwd=ROOT, env=env, capture_output=True, text=True, timeout=90,
            )
            self.assertEqual(done.returncode, 0, done.stdout + "\n" + done.stderr)


if __name__ == "__main__":
    unittest.main()
