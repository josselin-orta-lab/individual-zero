"""Fallback is not a decision; genuine winners still apply residual decay."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from build_i1_fork import generate


class FallbackContract(unittest.TestCase):
    def test_generated_competition_fallback_does_not_decay(self):
        with TemporaryDirectory(prefix="i1-fallback-decision-") as folder:
            generated=Path(folder)/"generated"
            generate(generated)
            script=r"""
from i1.modules.competition import Competition,CompetitionConfig
c=Competition(CompetitionConfig(
    version='fallback-regression',c_max=5,urgency_max=2.0,
    urgency_scale_cycles=2.0,leak=0.0,noise_sigma=0.0,gain=1.0,
    base_threshold=0.5,threshold_floor=0.1,inertia=0.1,residual=0.5,
    options_max=8,substitution_evidence={}))
c.ensure_wait(t_monde=1,st_version='test-version')
p=c.fallback()
state=c._registry[p.option.id]
state.accumulator=0.25
before=c.export_causal_state()
c.close_deliberation(p,adjudicated=False)
assert c.export_causal_state()==before
assert c.engaged_option_id is None
c.close_deliberation(None,adjudicated=True)
assert abs(state.accumulator-0.125)<1e-10
state.accumulator=0.25
c.close_deliberation(p,adjudicated=True)
assert c.engaged_option_id==p.option.id
assert state.accumulator==0.25
try:c.close_deliberation(p,adjudicated='no')
except ValueError:pass
else:raise AssertionError('bad adjudication accepted')
print('I1_COMPETITION_FALLBACK_ADJUDICATION_OK')
"""
            r=subprocess.run([sys.executable,"-c",script],
                cwd=ROOT,env={"PYTHONPATH":str(generated)+":"+str(ROOT/"src")},
                text=True,capture_output=True,check=False)
            self.assertEqual(r.returncode,0,r.stderr)
            self.assertIn("I1_COMPETITION_FALLBACK_ADJUDICATION_OK",r.stdout)


if __name__=="__main__":
    unittest.main()
