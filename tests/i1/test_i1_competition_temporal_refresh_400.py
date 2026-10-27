"""A Competition candidate cannot be re-registered with an earlier proposal time."""
import os
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from build_i1_fork import generate


class CompetitionTemporalRefresh(unittest.TestCase):
    def test_generated_owner_rejects_regression_and_roundtrips(self):
        with TemporaryDirectory(prefix="i1-400-") as root:
            generated = Path(root) / "generated"
            generate(generated)
            program = r"""
from i1.modules.competition import Competition, CompetitionConfig
config=CompetitionConfig(
 version="400", c_max=2, urgency_max=1., urgency_scale_cycles=1.,
 leak=0., noise_sigma=0., gain=1., base_threshold=.5,
 threshold_floor=.1, inertia=0., residual=.5, options_max=5,
 substitution_evidence={})
owner=Competition(config)
owner.ensure_wait(t_monde=5,st_version="st:5")
proposal=next(x for x in owner.candidate_proposals
              if x.option.id=="permanent:attendre")
before=owner.export_causal_state()
assert owner.register(proposal,active_goal_id=None,t_monde=4) is False
assert owner.export_causal_state()==before
assert owner.register(proposal,active_goal_id=None,t_monde=5) is True
assert owner.export_causal_state()==before
assert owner.register(proposal,active_goal_id=None,t_monde=6) is True
updated=owner.export_causal_state()
assert updated!=before
cold=Competition(config)
cold.restore_causal_state(updated)
assert cold.export_causal_state()==updated
assert cold.register(proposal,active_goal_id=None,t_monde=5) is False
assert cold.export_causal_state()==updated
print("I1_400_TEMPORAL_REFRESH_OK")
"""
            env = dict(os.environ, PYTHONPATH=os.pathsep.join((
                str(generated), str(ROOT / "src"))), PYTHONDONTWRITEBYTECODE="1")
            proc = subprocess.run([sys.executable, "-B", "-c", program],
                                  cwd=ROOT, env=env, text=True, capture_output=True)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertIn("I1_400_TEMPORAL_REFRESH_OK", proc.stdout)
