"""#512: discriminating non-scoring site memory/Q/P-40 overlap contract."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class SleepMemoryQOverlap512(unittest.TestCase):
    def test_situated_memory_is_not_a_second_value_signal(self):
        with TemporaryDirectory() as folder:
            output = Path(folder) / "generated"
            built = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                 "--output", str(output)], text=True, capture_output=True)
            self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
            proof = r"""
from types import SimpleNamespace
from i1.modules.td_values import (
    EvaluationState, LinearTDValues, ValueFeatureConfig, TDLearningConfig,
)
from i1.modules.sleep_competition import (
    create_sleep_proposal, assemble_sleep_evidence,
)
from i1.modules.competition import OptionEvidenceInput
from i1.contracts import EvaluationOption

features=ValueFeatureConfig(
    version="sleep-q-features-v1",
    feature_names=("bias","energy","food","water","integrity",
                   "x","y","is_night","goal_recover_energy"),
    position_scale_x=10.,position_scale_y=10.)
q=LinearTDValues(TDLearningConfig(
    version="sleep-q-test-v1",eta=.1,lambda_e=.5,beta=.9,
    evidence_scale=1.,features=features))
def state(x,y):
    return EvaluationState(
        body=dict(energy=40.,food=65.,water=55.,integrity=95.),
        x=x,y=y,active_goal_type="recover_energy",
        temporal_context="night")
a=state(2,3)
b=state(2,30)
c=state(9,3)
assert q.learned_value(a,"primitive:dormir").status=="unlearned"
assert q.learned_value(b,"primitive:dormir").status=="unlearned"
assert q.features(a) != q.features(b) != q.features(c)
assert q.q(a,"primitive:dormir")==q.q(b,"primitive:dormir")==0.
# Q can encode location already; it does not need a second site bonus.
q._weights["primitive:dormir"]=[0.,0.,0.,0.,0.,1.,-.5,0.,0.]
q._update_counts["primitive:dormir"]=1
assert q.learned_value(a,"primitive:dormir").value != q.learned_value(b,"primitive:dormir").value
assert q.learned_value(a,"primitive:dormir").value != q.learned_value(c,"primitive:dormir").value
charge=SimpleNamespace(accepted=True,module="metacognition_health",
    operation="sleep_option_prepare",requested_uc=1,
    consumed_cycle_uc=1,consumed_module_uc=1)
health=SimpleNamespace(rules=SimpleNamespace(
    config=SimpleNamespace(version="living-sleep")),
    frozen_world_step=9,frozen=SimpleNamespace(
        intrinsic_status="applicable",intrinsic_value=.3))
def proposal(site):
    return create_sleep_proposal(
        health=health,t_monde=9,st_version="S:9",
        charged_preparation=charge,site=site)
def base(p,extrinsic=None):
    e=EvaluationOption(
        option_ref=p.option.id,option_version=p.option.version,
        cycle=1,t_monde=9,status="not_evaluated",
        learned_value_status="unlearned",learned_value=None,
        simulated_value_status="unavailable",simulated_value=None,
        intrinsic_status="not_applicable",intrinsic_value=None,
        risk_status="unknown",risk=None,safety_uncertainty=1.,
        protection=False,signal_ids=(),producers=("test:stage8",))
    return OptionEvidenceInput(e,extrinsic)
pa,pb,pc=proposal((2,3)),proposal((2,30)),proposal((9,3))
assert len({p.option.id for p in (pa,pb,pc)})==3
assert {p.option.learning_signature for p in (pa,pb,pc)}=={"primitive:dormir"}
for p,site in ((pa,(2,3)),(pb,(2,30)),(pc,(9,3))):
    z=assemble_sleep_evidence(
        proposal=p,base=base(p),health=health,t_monde=9,cycle=1,
        intrinsic_weight=.9,site=site)
    assert z.evidence==.27
    assert z.evaluation.producers[-1]=="metacognition_health:p40_sleep_pressure"
    assert not any("memory" in marker for marker in z.evaluation.signal_ids)
# Context-only histories can differ even when the score is fixed.
# They may inform a later *independent* judgment; this test must not
# silently convert them into a numeric preference.
site_histories={
    (2,3): {"energy":{"increase":3,"decrease":0,"stable":0,"unknown":1}},
    (2,30):{"energy":{"increase":0,"decrease":3,"stable":0,"unknown":1}},
}
assert site_histories[(2,3)] != site_histories[(2,30)]
assert assemble_sleep_evidence(
    proposal=pa,base=base(pa),health=health,t_monde=9,cycle=1,
    intrinsic_weight=.9,site=(2,30)).evaluation.status=="not_evaluated"
print("I1_512_SLEEP_Q_CONTEXT_NO_DOUBLE_SCORE_OK")
"""
            completed = subprocess.run(
                [sys.executable, "-c", proof],
                env={"PYTHONPATH": str(output)},
                capture_output=True, text=True,
            )
            self.assertEqual(completed.returncode, 0,
                             completed.stdout + completed.stderr)
            self.assertIn("I1_512_SLEEP_Q_CONTEXT_NO_DOUBLE_SCORE_OK",
                          completed.stdout)


if __name__ == "__main__":
    unittest.main()
