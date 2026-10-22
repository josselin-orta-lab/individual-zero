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
# Independent replay of the same personally witnessed site under changing
# CURRENT bodily needs. No physical effect, Q, policy or reward is injected.
# Observed site retains both favorable and adverse signs in the same owner.
hungry_and_thirsty=dict(energy=70.,food=55.,water=20.,integrity=80.)
needs_satisfied=dict(energy=80.,food=70.,water=70.,integrity=90.)
v_needy,ref_needy=evaluation._experienced_site_context(
    target=target,body=hungry_and_thirsty,t_monde=4)
v_full,ref_full=evaluation._experienced_site_context(
    target=target,body=needs_satisfied,t_monde=4)
assert ref_needy==ref_full==source
assert v_needy>0 and v_full<0, (
    "same mixed lived site must be positive for an actual deficit and "
    "adverse after needs are satisfied")
# A fully favorable historical site must not have an artificial positive
# utility if no relevant need exists; no synthetic need or causal prediction.
positive=GeographicExploration(cfg)
assert positive.observe_capture(SimpleNamespace(t_monde=1,x=3,y=4))
assert positive.note_applied_local_action(
    world_step=1,position=site,body_before=body1,
    primitive="collecter",option_ref="witnessed-favorable")
good=positive.observe_lived_site_followup(
    world_step=2,position=site,
    body_after=dict(body1,water=45.))
assert good and good.favorable[2]>0 and all(x==0 for x in good.adverse)
evaluation._exploration=SimpleNamespace(geographic=positive)
v_good,ref_good=evaluation._experienced_site_context(
    target=target,body=hungry_and_thirsty,t_monde=3)
v_good_full,ref_good_full=evaluation._experienced_site_context(
    target=target,body=needs_satisfied,t_monde=3)
assert v_good>0 and ref_good is not None
assert v_good_full==0 and ref_good_full is None, (
    "unneeded favorable history cannot acquire an automatic positive score")
# Negative witnesses remain negative even when their associated channel
# has no current deficit. Risk is neither erased nor turned into reward.
adverse=GeographicExploration(cfg)
assert adverse.observe_capture(SimpleNamespace(t_monde=1,x=3,y=4))
assert adverse.note_applied_local_action(
    world_step=1,position=site,body_before=body2,
    primitive="manger",option_ref="witnessed-adverse")
bad=adverse.observe_lived_site_followup(
    world_step=2,position=site,
    body_after=dict(body2,water=15.))
assert bad and bad.adverse[2]>0 and all(x==0 for x in bad.favorable)
evaluation._exploration=SimpleNamespace(geographic=adverse)
v_bad,ref_bad=evaluation._experienced_site_context(
    target=target,body=hungry_and_thirsty,t_monde=3)
v_bad_full,ref_bad_full=evaluation._experienced_site_context(
    target=target,body=needs_satisfied,t_monde=3)
assert v_bad<0 and v_bad_full<0 and ref_bad and ref_bad_full
# Absence of previously witnessed data is not a new motivational source.
unwitnessed=GeographicExploration(cfg)
evaluation._exploration=SimpleNamespace(geographic=unwitnessed)
v_unseen,ref_unseen=evaluation._experienced_site_context(
    target=target,body=hungry_and_thirsty,t_monde=3)
assert v_unseen==0 and ref_unseen is None
# A genuinely sourced lived-site route may be retained as a cognitive
# prospect, but must not create motor authority or learned reward.
from i1.modules.memory import Memory, MemoryConfig
from i1lab.stage11_reference_fixture import build_stage11_reference_runtime
memory=build_stage11_reference_runtime(autonomous_mortal=True).memory
signature="lived_site_return:3:4"
offered="option:lived-site:lived-site:3:4:observed-t2:from:5:4:via:4:4"
assert memory.remember_considered_option(
 signature=signature,source_option_ref=offered,considered_step=5,cost_uc=1)
assert memory.lived_site_option_prospect_count==1
assert memory.recalled_applied_option(signature=signature,world_step=6)
snapshot=memory.export_causal_state()
restored=type(memory)(memory._config,atomic_world_step_length_boundary=True)
restored.restore_causal_state(snapshot)
assert restored.export_causal_state()==snapshot
assert restored.reconcile_option_intentions(
 available_signatures=frozenset(),world_step=6,namespace="lived_site_return:")
assert not restored.recalled_applied_option(signature=signature,world_step=6)
assert restored.reconcile_option_intentions(
 available_signatures=frozenset({signature}),world_step=7,
 namespace="lived_site_return:")
assert restored.recalled_applied_option(signature=signature,world_step=7)
for forged in (
 "option:lived-site:lived-site:3:4:observed-t8:from:5:4:via:4:4",
 "option:lived-site:lived-site:4:3:observed-t2:from:5:4:via:4:4",
 "option:lived-site:lived-site:3:4:observed-t2:from:5:4:via:3:4",
 "option:lived-site:lived-site:3:4:observed-t2:from:5:4:via:2:4",
):
 try:
  memory.remember_considered_option(
   signature="lived_site_return:3:4",
   source_option_ref=forged,considered_step=5,cost_uc=1)
 except ValueError:
  pass
 else:
  raise AssertionError("forged prospective spatial source accepted")
assert memory.export_causal_state()==snapshot
print("I1_328_LIVED_SITE_PROSPECT_CONTRACT_OK")
print("I1_328_SIGNED_NEED_DEPENDENT_CONTEXT_OK")
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
        # M11 commits a private copied runtime; pre-run owner references are stale.
        observed=life._runtime.exploration.geographic.export_causal_state()
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
