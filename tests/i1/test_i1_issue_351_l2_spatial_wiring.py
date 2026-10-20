"""Contract smoke for L2 spatial continuation on the built I1 generation."""
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from build_i1_fork import generate


class SpatialIntentionL2Tests(unittest.TestCase):
    def test_generated_wiring_and_fail_closed(self):
        with TemporaryDirectory(prefix="i1-351-") as tmp:
            output = Path(tmp) / "generated"
            generate(output)
            code = '''
from i1.modules.competition import Competition, CompetitionConfig
from i1.runtime.stage11_runtime import Stage11Runtime
from i1.experimental.intention_continuity import IntentEvidence, bounded_continuation
assert hasattr(Stage11Runtime, "_phase_hooks")
assert "i1_place_memory_intention_reconsidered" in Stage11Runtime._phase_hooks.__code__.co_consts or any(
    "i1_place_memory_intention_reconsidered" in str(c) for c in Stage11Runtime._phase_hooks.__code__.co_consts
)
cfg=CompetitionConfig(
    version="l2-check", c_max=2, urgency_max=1.0,
    urgency_scale_cycles=1.0, leak=0.0, noise_sigma=0.0, gain=1.0,
    base_threshold=0.5, threshold_floor=0.1, inertia=0.0,
    residual=0.5, options_max=4, substitution_evidence={}
)
comp=Competition(cfg)
assert comp.last_proposed_step_for("unregistered") is None
assert comp.retain_bounded_intention_evidence(option_ref="unknown", t_monde=2, evidence=0.2) is False
for bad in (float("nan"), float("inf"), -0.1, True):
    try:
        comp.retain_bounded_intention_evidence(option_ref="unknown", t_monde=2, evidence=bad)
        raise AssertionError("accepted invalid evidence")
    except ValueError:
        pass
prior=IntentEvidence("memory_place_return:site", 1, (1,0), 0.4)
assert bounded_continuation(prior,intended_ref="memory_place_return:site",now_step=2,
    observed_origin=(1,0),ceiling=0.5,residual=0.5,applied=True)==0.25
'''
            env = dict(os.environ, PYTHONPATH=str(output) + os.pathsep + str(ROOT / "src"),
                       PYTHONDONTWRITEBYTECODE="1")
            proc = subprocess.run([sys.executable, "-B", "-c", code],
                                  cwd=ROOT, env=env, capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
