"""#467: physically applied before-body may not bypass first-person custody."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]

class PrebodySelector467(unittest.TestCase):
    def test_generated_gate(self):
        with TemporaryDirectory() as temp:
            out=Path(temp)/"gen"
            b=subprocess.run([sys.executable,str(ROOT/"scripts/build_i1_fork.py"),
                "--output",str(out)],capture_output=True,text=True)
            self.assertEqual(b.returncode,0,b.stderr)
            code=r"""
from i1lab.journal import HashChainedJournal
from i1lab.determinism import deterministic_id
from i1lab.i1_natural_prebody_policy import (
 policy_for_proven_prebody_transition as choose,LIVED_PREBODY_POLICY as NEW)
from i1lab.stage7_runtime import STAGE7_AUTOBIOGRAPHICAL_POLICY as OLD
def check(*, body_delta=0, omit_capture=False, wrong_hash=False):
 j=HashChainedJournal(); t=3; attempt="attempt:3"
 digest="a"*64
 before=dict(energy=35.,food=60.,water=70.,integrity=99.)
 def write(ref,kind,emitter,**kw):
  j.append(event_id=ref,causal_event=dict(kind=kind,emitter=emitter,
   t_monde=t,attempt_ref=attempt,**kw))
 if not omit_capture:
  write("capture", "perceptual_capture","stage3-runtime",
   data=dict(capture_t_monde=t,dual_scope_capture_schema="stage12-dual-scope-body-cue-v1",
    dual_scope_visible_body=before))
 write("admitted","command_admitted","stage3-runtime",
  data=dict(command_hash=digest if not wrong_hash else "b"*64,primitive="dormir"))
 write("cmd","command_experienced","action_control",
  command_hash=digest,primitive="dormir")
 physical=deterministic_id("journal-event-v1","world",t,attempt,digest,"transition")
 new_before=dict(before);new_before["water"]+=body_delta
 write(physical,"world_transition_experienced","world_and_body",
  body_before=new_before,body_after=dict(before),
  position_after=dict(x=1,y=1),effects={})
 return choose(journal=j,t_monde=t,attempt_ref=attempt,
  command_ref="cmd",physical_ref=physical)
assert check() is NEW
assert check(body_delta=1) is OLD
assert check(omit_capture=True) is OLD
assert check(wrong_hash=True) is OLD
# A completed authentic prefix remains eligible after a long legitimate
# technical tail; post-command entries are not provenance scan work.
j=HashChainedJournal();t=5;attempt="attempt:5";digest="b"*64
body=dict(energy=35.,food=60.,water=70.,integrity=99.)
def append(ref,kind,emitter,**data):
 j.append(event_id=ref,causal_event=dict(
  kind=kind,emitter=emitter,t_monde=t,attempt_ref=attempt,**data))
append("capture5","perceptual_capture","stage3-runtime",
 data=dict(capture_t_monde=t,
  dual_scope_capture_schema="stage12-dual-scope-body-cue-v1",
  dual_scope_visible_body=body))
append("admit5","command_admitted","stage3-runtime",
 data=dict(command_hash=digest,primitive="dormir"))
append("command5","command_experienced","action_control",
 command_hash=digest,primitive="dormir")
physical=deterministic_id("journal-event-v1","world",t,attempt,digest,"transition")
append(physical,"world_transition_experienced","world_and_body",
 body_before=body,body_after=body)
for i in range(4097):
 append("later:"+str(i),"observer_event","operator",data=dict(i=i))
assert choose(journal=j,t_monde=t,attempt_ref=attempt,
 command_ref="command5",physical_ref=physical) is NEW
print("I1_467_PREBODY_PROVEN_SELECTOR_OK")
"""
            r=subprocess.run([sys.executable,"-c",code],
                env={"PYTHONPATH":str(out)},capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stderr)
            self.assertIn("I1_467_PREBODY_PROVEN_SELECTOR_OK",r.stdout)

    def test_real_natural_m11_receipts_and_cold_recovery(self):
        """An unforced natural birth must emit verifiable receipts; no DC-09 activation."""
        with TemporaryDirectory() as temp:
            out = Path(temp) / "gen"
            build = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                 "--output", str(out)], capture_output=True, text=True)
            self.assertEqual(build.returncode, 0, build.stderr)
            program = r"""
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from i1lab.i1_birth import birth_i1_m11, recover_i1_m11
from i1lab.i1_natural_runtime import I1Runtime
from i1lab.i1_natural_prebody_policy import (
    policy_for_proven_prebody_transition as choose, LIVED_PREBODY_POLICY as NEW)
from i1lab.stage11_reference_fixture import build_stage11_reference_runtime
from i1lab.stage10_reference_fixture import build_stage10_reference_runtime
from i1lab.stage2_runtime import STAGE2_AUTOBIOGRAPHICAL_POLICY as P2
from i1lab.stage7_runtime import STAGE7_AUTOBIOGRAPHICAL_POLICY as P7
from i1.modules.stage12_detectors import Stage12DetectionPolicy

base = build_stage11_reference_runtime(autonomous_mortal=True)
sleep = build_stage10_reference_runtime(autonomous_mortal=True)
stage10 = replace(sleep._stage10_config, stage9=base._stage11_config.stage9)
detector = Stage12DetectionPolicy(
    version="i1-prebody-natural-test-v1", window=12, stagnation_steps=3,
    stagnation_tolerance=.05, loop_repetitions=2, loop_max_period=2,
    entropy_min_samples=3, entropy_warning_fraction=.25,
    bias_min_outcomes_each=2, attribution_bias_threshold=.75)
life_id = "i1:467:prebody:probe"
params = dict(
    world_config=base.world.config, layout=base.world._layout,
    safety_config=base.stage3.substrate.safety._config,
    safety_facts=base._canonical_safety._innate,
    protected_integrity_threshold=base.stage3.control._config.protected_integrity_threshold,
    stage11_config=base._stage11_config, stage10_config=stage10,
    equipment=base.equipment, detector_policy=detector,
    diagnostic_sample_cost_uc=1, module_occupancy_cost_uc=1)
def fresh():
    return I1Runtime(birth_life_id=life_id, autonomous_mortal=True,
                     m11_sqlite_custody=True, wal_path=None, **params)
def inspect(runtime):
    receipts = tuple(runtime.journal.entries)
    commands = {
        (e.causal_event.get("t_monde"), e.causal_event.get("attempt_ref")): e
        for e in receipts if e.causal_event.get("kind") == "command_experienced"
    }
    proved = []
    for physical in receipts:
        p = physical.causal_event
        if p.get("kind") != "world_transition_experienced":
            continue
        command = commands.get((p.get("t_monde"), p.get("attempt_ref")))
        if command is None:
            continue
        verdict = choose(journal=runtime.journal, t_monde=p["t_monde"],
                         attempt_ref=p["attempt_ref"],
                         command_ref=command.event_id, physical_ref=physical.event_id)
        proved.append((physical.event_id, verdict is NEW))
    assert proved, "no natural applied physical command to examine"
    assert any(flag for _, flag in proved), ("natural awake receipts rejected", proved)
    # This selector is still dormant; current births commit old projections.
    projected = runtime.stage3.substrate.views.autobiographical(
        policies={P2.version: P2, P7.version: P7})
    assert all("body_before" not in row for row in projected)
    return proved
with TemporaryDirectory() as directory:
    db = str(Path(directory) / "natural.sqlite")
    with birth_i1_m11(db_path=db, life_id=life_id, **params) as individual:
        for _ in range(2):
            result = individual.run_step()
            assert result.status == "active", result
        before = inspect(individual._runtime)
    with recover_i1_m11(db_path=db, life_id=life_id,
                         runtime_factory=fresh) as cold:
        after = inspect(cold._runtime)
    assert before == after
print("I1_467_NATURAL_PREBODY_SELECTABLE_M11_COLD_OK")
"""
            done = subprocess.run(
                [sys.executable, "-c", program], env={"PYTHONPATH": str(out)},
                capture_output=True, text=True)
            self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
            self.assertIn("I1_467_NATURAL_PREBODY_SELECTABLE_M11_COLD_OK", done.stdout)

if __name__=="__main__":
    unittest.main()
