"""#473: situated option identity without a learned-Q or motor shortcut."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class SituatedSleepIdentity473(unittest.TestCase):
    def test_real_generated_stage10_contract(self):
        with TemporaryDirectory() as folder:
            generated = Path(folder) / "generated"
            build = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                 "--output", str(generated)],
                capture_output=True, text=True, check=False)
            self.assertEqual(build.returncode, 0, build.stderr)
            code = r"""
from types import SimpleNamespace
from i1.modules.sleep_competition import (
    create_sleep_proposal, _valid_sleep_shape,
    assemble_sleep_evidence, _sleep_site_ref,
)
from i1.modules.competition import OptionEvidenceInput
from i1.contracts import EvaluationOption

charge = SimpleNamespace(accepted=True, module="metacognition_health",
    operation="sleep_option_prepare", requested_uc=1,
    consumed_cycle_uc=1, consumed_module_uc=1)
health = SimpleNamespace(
    rules=SimpleNamespace(config=SimpleNamespace(version="living-sleep")),
    frozen_world_step=9,
    frozen=SimpleNamespace(intrinsic_status="applicable",
                           intrinsic_value=0.3))
def make(site, t=9):
    health.frozen_world_step = t
    return create_sleep_proposal(health=health, t_monde=t,
        st_version="S:9", charged_preparation=charge, site=site)
a = make((2,4))
b = make((8,4))
revisit = make((2,4))
assert a.option.id == revisit.option.id != b.option.id
assert a.option.id != b.option.id
assert a.option.learning_signature == b.option.learning_signature == "primitive:dormir"
assert _sleep_site_ref((2,4)) == "sleep-site:2:4"
assert _valid_sleep_shape(a, health=health, t_monde=9, site=(2,4))
assert not _valid_sleep_shape(a, health=health, t_monde=9, site=(8,4))
def evidence(proposal):
    ev = EvaluationOption(option_ref=proposal.option.id,
        option_version=proposal.option.version, cycle=1, t_monde=9,
        status="not_evaluated", learned_value_status="unlearned",
        learned_value=None, simulated_value_status="unavailable",
        simulated_value=None, intrinsic_status="not_applicable",
        intrinsic_value=None, risk_status="unknown", risk=None,
        safety_uncertainty=1.0, protection=False,
        signal_ids=(), producers=("test",))
    return OptionEvidenceInput(ev, None)
ok = assemble_sleep_evidence(proposal=a, base=evidence(a),
    health=health,t_monde=9,cycle=1,intrinsic_weight=0.9,site=(2,4))
stale = assemble_sleep_evidence(proposal=a,base=evidence(a),
    health=health,t_monde=9,cycle=1,intrinsic_weight=0.9,site=(8,4))
assert ok.evidence == 0.27
assert stale.evidence is None and stale.evaluation.status == "not_evaluated"
for invalid in ((True,4), (-1,4), (2,4,7)):
    try: make(invalid)
    except ValueError: pass
    else: raise AssertionError("invalid captured site accepted")
print("I1_473_SLEEP_SITE_IDENTITY_OK")
"""
            result = subprocess.run([sys.executable, "-c", code],
                env={"PYTHONPATH": str(generated) + ":" + str(ROOT / "src")},
                capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("I1_473_SLEEP_SITE_IDENTITY_OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
