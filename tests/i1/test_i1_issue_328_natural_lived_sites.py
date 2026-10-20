"""Bounded first-person site consequence memory and canonical M11 activation.

These are contract/short physical-recovery tests, not population experiments or
evidence that learned site values improve life outcomes.
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


class LivedSiteIntegration(unittest.TestCase):
    def generated(self, code):
        with TemporaryDirectory(prefix="i1-328-built-") as tmp:
            output = Path(tmp) / "generated"
            generate(output)
            env = dict(
                os.environ,
                PYTHONPATH=os.pathsep.join((str(output), str(ROOT / "src"), str(ROOT / "tools"))),
                PYTHONDONTWRITEBYTECODE="1",
            )
            proc = subprocess.run(
                [sys.executable, "-B", "-c", code], cwd=ROOT,
                env=env, capture_output=True, text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            return proc.stdout

    def test_generic_lived_positive_negative_and_atomic_restore(self):
        self.assertIn("I1_328_GENERIC_OWNER_OK", self.generated(r'''
from copy import deepcopy
from types import SimpleNamespace
from i1.modules.geographic_exploration import GeographicExploration,GeographicExplorationConfig
from i1.modules.stage11_evaluator import Stage11OptionEvaluator
from i1.modules.value_needs import ValueNeedsConfig

cfg=GeographicExplorationConfig(
    version="lived-site-test",novelty_weight=.2,max_distinct_sites=10,
    max_targets_per_cycle=1,observe_routes=True,remember_entities=True,
    experienced_site_effects=True,max_place_candidates=2,
)
geo=GeographicExploration(cfg)
site=(3,4)
body1=dict(energy=75.,food=50.,water=20.,integrity=80.)
body2=dict(energy=74.,food=49.,water=45.,integrity=80.)
body3=dict(energy=73.,food=60.,water=38.,integrity=80.)
assert geo.observe_capture(SimpleNamespace(t_monde=1,x=3,y=4)) is True
assert geo.note_applied_local_action(
    world_step=1,position=site,body_before=body1,primitive="se_deplacer",
    option_ref="test:move"
) is False
assert geo.note_applied_local_action(
    world_step=1,position=site,body_before=body1,primitive="collecter",
    option_ref="test:physically-applied"
) is True
genesis=geo.export_causal_state()
assert genesis["pending_site_action"]["step"]==1
restored=GeographicExploration(cfg)
restored.restore_causal_state(genesis)
assert restored.export_causal_state()==genesis, "M11 pending action must round trip"
seen=restored.observe_lived_site_followup(
    world_step=2,position=site,body_after=body2,
)
assert seen is not None and seen.samples==1
assert seen.favorable[2]==25 and seen.adverse[0]==1 and seen.adverse[1]==1
assert restored.observe_capture(SimpleNamespace(t_monde=2,x=3,y=4)) is False
assert restored.note_applied_local_action(
    world_step=2,position=site,body_before=body2,
    primitive="manger",option_ref="test:other-applied"
) is True
again=restored.observe_lived_site_followup(
    world_step=3,position=site,body_after=body3,
)
assert again.samples==2
assert again.favorable[2]>0 and again.adverse[2]>0
assert again.favorable[1]>0 and again.adverse[1]>0
assert restored.observe_capture(SimpleNamespace(t_monde=3,x=3,y=4)) is False
image=restored.export_causal_state()
cold=GeographicExploration(cfg)
cold.restore_causal_state(image)
assert cold.export_causal_state()==image
corrupted=deepcopy(image)
corrupted["lived_site_effects"][0]["last_observed_step"]=99
original=cold.export_causal_state()
try:
    cold.restore_causal_state(corrupted)
    raise AssertionError("future site report accepted")
except ValueError:
    pass
assert cold.export_causal_state()==original, "corrupt owner restore mutated prior state"
needs=ValueNeedsConfig(
    version="needs",setpoints=dict(energy=80.,food=70.,water=70.,integrity=90.),
    weights=dict(energy=1.,food=1.,water=1.,integrity=1.),
    normalization_scales=dict(energy=80.,food=70.,water=70.,integrity=90.),
    p_min=.1,contribution_ttl_steps=2,
)
evaluation=object.__new__(Stage11OptionEvaluator)
evaluation._site_needs_config=needs
evaluation._exploration=SimpleNamespace(geographic=cold)
target=SimpleNamespace(observed_position=site,confidence=.8,
                       visited_path=((2,4),(3,4)))
val,source=evaluation._experienced_site_context(
    target=target,body=dict(energy=70.,food=55.,water=20.,integrity=80.),
    t_monde=4,
)
assert source.startswith("lived-site:3:4:observed-t3")
assert -0.25<=val<=0.25
empty,source2=evaluation._experienced_site_context(
    target=target,body=body3,t_monde=3,
)
assert empty==0 and source2 is None, "same-capture data must not self-credit"
other=SimpleNamespace(observed_position=(9,9),confidence=.8,
                      visited_path=((8,9),(9,9)))
nothing,_=evaluation._experienced_site_context(
    target=other,body=body1,t_monde=4,
)
assert nothing==0, "same resource kind at another site has no borrowed knowledge"
print("I1_328_GENERIC_OWNER_OK")
'''))

    def test_canonical_birth_m11_and_short_perceptual_step(self):
        self.assertIn("I1_328_CANONICAL_M11_OK", self.generated(r'''
from pathlib import Path
from tempfile import TemporaryDirectory
from i1lab.i1_birth import birth_i1_m11,recover_i1_m11
from i1lab.i1_natural_runtime import I1Runtime
from run_i1_world_preset import load_preset,_birth_parameters
source,_=load_preset("oasis")
params,_=_birth_parameters(source)
params=dict(params,diagnostic_sample_cost_uc=1,module_occupancy_cost_uc=1)
life_id="i1:328:technical-witness"
def fresh():
    return I1Runtime(birth_life_id=life_id,wal_path=None,
                     autonomous_mortal=True,m11_sqlite_custody=True,**params)
with TemporaryDirectory() as tmp:
    db=str(Path(tmp)/"lived.sqlite")
    with birth_i1_m11(db_path=db,life_id=life_id,**params) as life:
        rt=life._runtime
        geo=rt.exploration.geographic
        assert geo.config.experienced_site_effects is True
        assert geo.site_effect_for((8,8)) is None
        before=life.run_step()
        assert before.status=="active"
        observed=geo.export_causal_state()
        assert observed["schema"]=="geographic-exploration-v6-lived-sites"
        assert isinstance(observed["lived_site_effects"],list)
    with recover_i1_m11(db_path=db,life_id=life_id,runtime_factory=fresh) as recovered:
        restored=recovered._runtime.exploration.geographic
        assert restored.export_causal_state()==observed, "M11 owner mismatch"
        after=recovered.run_step()
        assert after.status=="active" and after.generation==before.generation+1
        assert restored.config.experienced_site_effects is True
print("I1_328_CANONICAL_M11_OK")
'''))


if __name__ == "__main__":
    unittest.main()
