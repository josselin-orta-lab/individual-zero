"""Memory uncertainty does not turn exclusively adverse experience into preference."""
import os
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from build_i1_fork import generate


class AdverseLivedPlanningRegression(unittest.TestCase):
    def test_generated_natural_owner_and_ranking(self):
        with TemporaryDirectory(prefix="i1-368-") as tmp:
            built = Path(tmp) / "generated"
            generate(built)
            code = r"""
from i1lab.i1_natural_runtime import _rank_current_local_opportunity, I1Runtime
from i1lab.stage11_reference_fixture import build_stage11_reference_runtime
import inspect

memory = build_stage11_reference_runtime(autonomous_mortal=True).memory
signature = "i1:affordance:collecter:target=x"
body = dict(energy=50., food=50., water=50., integrity=50.)
def record(step, delta):
    assert memory.remember_applied_option(
        signature=signature,
        source_option_ref=f"option:i1:local:t{step}:collecter:target=x",
        applied_step=step, cost_uc=1, body_before=body,
    )
    assert memory.observe_applied_option_followups(
        world_step=step+1, body_after=dict(body, water=50.+delta)
    )
def rank(remembered, witnesses=(), q=None, rotation=0):
    return _rank_current_local_opportunity(
        learned_evidence=q, remembered=remembered,
        witnesses=witnesses, rotation=rotation,
    )
neutral = rank(False)
assert rank(True) < neutral  # Prospective possibility: no result invented.
record(2, -10.)
adverse = memory.observed_option_witnesses(signature=signature, world_step=4)
assert len(adverse) == 1
assert rank(True, adverse) == neutral  # Adverse context must not be rewarded.
assert rank(True, adverse, q=.4) < rank(False, q=.2)
assert rank(True, adverse, q=-.4) > rank(False, q=.2)
record(4, 10.)
mixed = memory.observed_option_witnesses(signature=signature, world_step=6)
assert rank(True, mixed) == neutral
record(6, 0.)
mixed_neutral = memory.observed_option_witnesses(signature=signature, world_step=8)
assert rank(True, mixed_neutral) == neutral
image = memory.export_causal_state()
cold = type(memory)(memory._config, atomic_world_step_length_boundary=True)
cold.restore_causal_state(image)
assert cold.export_causal_state() == image
assert rank(True, cold.observed_option_witnesses(signature=signature, world_step=8)) == neutral
assert memory.observed_option_witnesses(signature=signature, world_step=100) == ()
assert rank(True, (), rotation=1) > rank(False, (), rotation=0)
# The natural producer, not a standalone utility, calls this function after
# a paid Memory lookup. No new Stage8, Q/TD, or physical command owner.
source = inspect.getsource(I1Runtime._propose_independent_local)
assert "self._charge(" in source
assert "self.memory.observed_option_witnesses(" in source
assert "_rank_current_local_opportunity(" in source
assert "self.q_active.learned_value(" in source
assert "self.planning.candidate_commands(" in source
assert "self._i1_pending[\"local_opportunity_evidence\"]" in source
assert "self.competition" in source
print("I1_368_ADVERSE_MEMORY_RANKING_OK")
"""
            env = dict(os.environ, PYTHONPATH=os.pathsep.join((
                str(built), str(ROOT / "src"),
            )), PYTHONDONTWRITEBYTECODE="1")
            result = subprocess.run(
                [sys.executable, "-B", "-c", code],
                cwd=ROOT, env=env, text=True, capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("I1_368_ADVERSE_MEMORY_RANKING_OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
