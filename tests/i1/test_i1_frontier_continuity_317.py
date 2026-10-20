"""#317 falsification: a physically identical frontier must keep its decision identity.

The native/generated-I1 regression is synthetic, never a physical-world result.
It must FAIL against the timestamped frontier-option implementation. It does
not tune evidence, select motor commands, or weaken Action Control.
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


class FrontierEvidenceContinuity317Tests(unittest.TestCase):
    def test_identical_observed_frontier_retains_evidence_between_world_steps(self):
        with TemporaryDirectory(prefix="i1-317-frontier-") as folder:
            built = Path(folder) / "generated"
            generate(built)
            script = r"""
from types import SimpleNamespace
from i1.contracts import EvaluationOption
from i1.modules.competition import Competition,CompetitionConfig,OptionEvidenceInput
from i1.modules.geographic_exploration import GeographicTarget,GeographicExploration
from i1.modules.geographic_planning import propose_geographic_frontier

def proposal(t):
    target=GeographicTarget(
        ref="frontier:1:0:from:2:0",
        source_t_monde=t, origin=(2,0),destination=(1,0), direction="west")
    initial=SimpleNamespace(
        x=2,y=0,validate=lambda:None,
        adjacent=(SimpleNamespace(
            direction="west",passable=True,creature=False,x=1,y=0),))
    simulator=SimpleNamespace(rollout=lambda **k:
        SimpleNamespace(complete=False,reason="equipment_input_unseen"))
    candidate=propose_geographic_frontier(
        target=target,initial_state=initial,simulator=simulator,
        st_version=f"first-person-capture:t{t}",t_monde=t,ttl_steps=20)
    assert candidate is not None
    assert candidate.preliminary_admissibility=="indeterminate"
    return target,candidate

old_target,old=proposal(10)
fresh_target,fresh=proposal(11)
assert old.option.id==fresh.option.id, (
    "time stamp must not silently reset a materially identical frontier")
assert old.option.learning_signature==fresh.option.learning_signature
assert old.plan.steps==fresh.plan.steps
assert old.option.expires_at_step!=fresh.option.expires_at_step

c=Competition(CompetitionConfig(
    version="317-frontier-synthetic",c_max=5,urgency_max=2.0,
    urgency_scale_cycles=2.0,leak=0.0,noise_sigma=0.0,gain=1.0,
    base_threshold=0.5,threshold_floor=0.1,inertia=0.1,
    residual=0.5,options_max=8,substitution_evidence={}))
assert c.register(old,active_goal_id=None,t_monde=10)
evaluation=EvaluationOption(
    option_ref=old.option.id,option_version=old.option.version,
    cycle=1,t_monde=10,status="evaluated",learned_value_status="unlearned",
    learned_value=None,simulated_value_status="unavailable",
    simulated_value=None,intrinsic_status="applicable",intrinsic_value=0.03,
    risk_status="unknown",risk=None,safety_uncertainty=0.0,
    protection=False,signal_ids=("first-person-frontier",),
    producers=("synthetic-unit-only",))
evaluation.validate()
result=c.evaluate(
    cycle=1,t_monde=10,
    evidence_inputs={old.option.id:OptionEvidenceInput(evaluation,0.03)})
assert result.winner is None
remembered=c.accumulator_for(old.option.id)
assert 0<remembered<0.5
c.close_deliberation(None,adjudicated=False)
c.open_deliberation(active_goal_id=None,t_monde=11)
assert c.register(fresh,active_goal_id=None,t_monde=11)
assert abs(c.accumulator_for(fresh.option.id)-remembered)<1e-12, (
    "no Competition winner and unchanged material plan may not erase evidence")
# Current personally sensed offered target is still authoritative. Stale or
# newly visited destinations never gain a motor authorization through the key.
geo=GeographicExploration.__new__(GeographicExploration)
geo._offered=(fresh_target,)
geo._visits={}
assert geo.target_for(fresh.option)==fresh_target
geo._visits={(1,0):1}
assert geo.target_for(fresh.option) is None
geo._visits={}
geo._offered=()
assert geo.target_for(fresh.option) is None
print("I1_317_FRONTIER_IDENTITY_AND_COMPETITION_OK")
"""
            env = dict(os.environ)
            env["PYTHONPATH"] = str(built) + os.pathsep + str(ROOT / "src")
            p = subprocess.run(
                [sys.executable, "-B", "-c", script],
                env=env, cwd=ROOT, text=True, capture_output=True,
                check=False, timeout=120,
            )
            self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
            self.assertIn("I1_317_FRONTIER_IDENTITY_AND_COMPETITION_OK", p.stdout)


if __name__ == "__main__":
    unittest.main()
