"""Real full Perception must update place intention before reflex/Competition.

Controlled owner fixture for the prior action; no spontaneous return is claimed.
"""
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from build_i1_fork import generate


class FullCaptureIntentTests(unittest.TestCase):
    def test_generated_owner_capture_seam_and_negative_cases(self):
        with TemporaryDirectory(prefix="i1-389-") as folder:
            generated = Path(folder) / "generated"
            generate(generated)
            script = r"""
from dataclasses import replace
from types import SimpleNamespace

from i1.modules.competition import Competition, CompetitionConfig, AppliedMemoryIntention
from i1lab.stage11_runtime import Stage11Runtime

cfg=CompetitionConfig(version="i1-389-test",c_max=2,urgency_max=1.0,
    urgency_scale_cycles=1.0,leak=0.0,noise_sigma=0.0,gain=1.0,
    base_threshold=0.5,threshold_floor=0.1,inertia=0.0,residual=0.5,
    options_max=6,substitution_evidence={})
def fresh():
    c=Competition(cfg)
    c._applied_memory_intent=AppliedMemoryIntention(
        semantic_ref="memory_place_return:observed-object",
        source_option_ref=("option:place-memory:place:observed-object:at:4:0"
                           ":from:1:0:via:2:0"),
        goal_ref="goal:own", expected_position=(2,0), observed_site=(4,0),
        applied_step=1, expires_at_step=7, evidence=0.7)
    c._applied_memory_intent.validate()
    return c

def capture(c,step,position):
    # Exercise the real Stage11 capture seam with isolated owners.
    # No fake world command, Step8 election, or M11 life is claimed.
    instance=object.__new__(Stage11Runtime)
    instance.competition=c
    events=[]
    instance._write=lambda **kw:events.append(kw)
    instance.exploration=SimpleNamespace(geographic=None)
    # The normal parent hook is observational; call the same boundary
    # body directly to isolate the Competition update from the costly world.
    from unittest.mock import patch
    with patch("i1lab.stage9_runtime.Stage9Runtime._on_open_step_capture",
               lambda self, observed: None):
        Stage11Runtime._on_open_step_capture(instance,
            SimpleNamespace(t_monde=step,x=position[0],y=position[1]))
    return events

c=fresh()
events=capture(c,2,(2,0))
assert c.applied_memory_intention.confirmed_step==2
assert len(events)==1 and events[0]["data"]["confirmed_arrival"] is True
assert events[0]["data"]["motor_admission_inherited"] is False
assert events[0]["data"]["source"]=="full_physical_perception_before_reflex"
image=c.export_causal_state()
cold=Competition(cfg);cold.restore_causal_state(image)
assert cold.export_causal_state()==image
assert cold.applied_memory_intention.confirmed_step==2
assert capture(cold,4,(2,0))[0]["data"]["status"]=="suspended"
assert cold.applied_memory_intention.confirmed_step==2
assert cold.accumulator_for("unregistered") is None

contradicted=fresh()
events=capture(contradicted,2,(1,0))
assert contradicted.applied_memory_intention is None
assert len(events)==1 and events[0]["data"]["status"]=="contradicted"
late=fresh()
assert capture(late,4,(2,0))[0]["data"]["status"]=="suspended"
assert late.applied_memory_intention.confirmed_step is None
expired=fresh()
assert capture(expired,7,(2,0))[0]["data"]["status"]=="expired"
assert expired.applied_memory_intention is None

import inspect
source=inspect.getsource(Stage11Runtime._phase_hooks)
assert "observe_memory_intention(" not in source, (
    "Competition phase must not reobserve an already captured step")
assert "intent.confirmed_step == capture.t_monde" in source
print("I1_389_FULL_CAPTURE_SPATIAL_INTENTION_OK")
"""
            env=dict(os.environ, PYTHONPATH=os.pathsep.join((
                str(generated),str(ROOT / "src"),str(ROOT / "tools"))),
                PYTHONDONTWRITEBYTECODE="1")
            proc=subprocess.run([sys.executable,"-B","-c",script],
                cwd=ROOT,env=env,capture_output=True,text=True)
            self.assertEqual(proc.returncode,0,proc.stdout+proc.stderr)
            self.assertIn("I1_389_FULL_CAPTURE_SPATIAL_INTENTION_OK",proc.stdout)


if __name__=="__main__":
    unittest.main()
