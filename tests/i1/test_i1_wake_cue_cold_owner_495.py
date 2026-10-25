"""#495: dormant wake-cue eligibility survives authentic M11 cold recovery.

A waking *capture* remains technical, never a projected Memory event. The
only permitted autobiographical source is its separately committed applied
physical transition. No cue is activated by this test.
"""
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[2]


class WakeCueColdOwner495(unittest.TestCase):
    def test_natural_replay_preserves_dormant_wake_proofs(self):
        with TemporaryDirectory() as directory:
            out = Path(directory) / "generated"
            built = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                 "--output", str(out)], text=True, capture_output=True)
            self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
            proof = r"""
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from i1lab.i1_birth import birth_i1_m11, recover_i1_m11
from i1lab.i1_natural_runtime import I1Runtime
from i1lab.i1_natural_prebody_policy import attested_postwake_perceptual_body
from i1lab.stage11_reference_fixture import build_stage11_reference_runtime
from i1lab.stage10_reference_fixture import build_stage10_reference_runtime
from i1.modules.stage12_detectors import Stage12DetectionPolicy

base=build_stage11_reference_runtime(autonomous_mortal=True)
sleep=build_stage10_reference_runtime(autonomous_mortal=True)
stage10=replace(sleep._stage10_config,stage9=base._stage11_config.stage9)
detector=Stage12DetectionPolicy(
    version="i1-495-cold-eligibility-v1", window=12, stagnation_steps=3,
    stagnation_tolerance=.05, loop_repetitions=2, loop_max_period=2,
    entropy_min_samples=3, entropy_warning_fraction=.25,
    bias_min_outcomes_each=2, attribution_bias_threshold=.75)
life="i1:495:cold-proof"
params=dict(
 world_config=base.world.config,layout=base.world._layout,
 safety_config=base.stage3.substrate.safety._config,
 safety_facts=base._canonical_safety._innate,
 protected_integrity_threshold=base.stage3.control._config.protected_integrity_threshold,
 stage11_config=base._stage11_config,stage10_config=stage10,
 equipment=base.equipment,detector_policy=detector,
 diagnostic_sample_cost_uc=1,module_occupancy_cost_uc=1)
def fresh():
 return I1Runtime(birth_life_id=life,autonomous_mortal=True,
                  m11_sqlite_custody=True,wal_path=None,**params)
def witness(runtime):
 rows=tuple(runtime.journal.entries)
 commands={(e.causal_event.get("t_monde"),e.causal_event.get("attempt_ref")):e
  for e in rows if e.causal_event.get("kind")=="command_experienced"}
 commitments={r for e in rows
  if e.causal_event.get("kind")=="auto_segment_commit"
  for r in e.causal_event["event_refs"]}
 memory=runtime.memory.export_causal_state()
 seen=set(memory["seen_event_refs"])
 closed={r for episode in memory["episodes"] for r in episode["event_refs"]}
 owned=[]
 eligible=[]
 for physical in rows:
  p=physical.causal_event
  if p.get("kind")!="world_transition_experienced":
   continue
  cmd=commands.get((p.get("t_monde"),p.get("attempt_ref")))
  if cmd is None:continue
  cue=attested_postwake_perceptual_body(
   journal=runtime.journal,t_monde=p["t_monde"],
   attempt_ref=p["attempt_ref"],command_ref=cmd.event_id,
   physical_ref=physical.event_id)
  owned.append(physical.event_id)
  if cue is None:continue
  ref=cue["source_event_ref"]
  assert ref not in commitments and ref not in seen and ref not in closed
  assert physical.event_id in owned
  assert set(cue)=={"source_event_ref","t_monde","position","body_perceived"}
  eligible.append((physical.event_id,ref,cue["body_perceived"]))
 assert owned,"no natural applied transitions"
 assert closed<=seen and seen<=commitments
 return (tuple(owned),tuple(eligible),frozenset(commitments),
         frozenset(seen),frozenset(closed))
with TemporaryDirectory() as directory:
 db=str(Path(directory)/"life.sqlite")
 with birth_i1_m11(db_path=db,life_id=life,**params) as actor:
  for _ in range(4):
   result=actor.run_step()
   assert result.status=="active",result
  before=witness(actor._runtime)
 with recover_i1_m11(db_path=db,life_id=life,runtime_factory=fresh) as cold:
  after=witness(cold._runtime)
 assert before==after,"cold wake cue / Memory ownership changed"
print("I1_495_DORMANT_WAKE_COLD_OWNERSHIP_OK")
"""
            done = subprocess.run(
                [sys.executable, "-c", proof], text=True, capture_output=True,
                env={"PYTHONPATH": str(out)})
            self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
            self.assertIn("I1_495_DORMANT_WAKE_COLD_OWNERSHIP_OK", done.stdout)


if __name__ == "__main__":
    unittest.main()
