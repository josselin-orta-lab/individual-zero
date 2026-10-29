"""A1 two-path read instrument: paired mortal M11, no A1 pilot births."""
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from build_i1_fork import generate


class A1DecisionReadContract(unittest.TestCase):
    def test_both_real_m11_arms_and_learned_read_mask_without_td_owner_change(self):
        with TemporaryDirectory(prefix="i1-eco-a1-read-") as tmp:
            generated = Path(tmp) / "generated"
            generate(generated)
            script = r"""
from pathlib import Path
from tempfile import TemporaryDirectory
from dataclasses import replace
from i1lab.stage11_reference_fixture import build_stage11_reference_runtime
from i1lab.stage10_reference_fixture import build_stage10_reference_runtime
from i1.modules.stage12_detectors import Stage12DetectionPolicy
from i1lab.i1_birth import birth_i1_m11
from i1lab.sqlite_life_store import SQLiteLifeLedger
from i1_eco_a1_matched_birth import a1_matched_temperament_birth
from i1_eco_a1_td_mask import a1_decision_read_scope, _decision_value
from i1_eco_a1_decision_join import audited_a1_decision_alignment
from i1_eco_m11_reader import audited_life_metrics
from i1.modules.td_values import LearnedValue

actual = LearnedValue(signature="test:learned", status="learned",
                      value=0.5, evidence=0.2, update_count=2)
neutral = _decision_value(actual, masked=True, signature=actual.signature)
assert neutral.status == "unlearned" and neutral.value is None
assert _decision_value(actual, masked=False, signature=actual.signature) is actual
unknown = LearnedValue(signature="unknown", status="unlearned",
                       value=None, evidence=None, update_count=0)
assert _decision_value(unknown, masked=True, signature="unknown") is unknown
try:
    _decision_value(actual, masked=True, signature="wrong")
except ValueError:
    pass
else:
    raise AssertionError("cross-signature learned read accepted")

base = build_stage11_reference_runtime(autonomous_mortal=True)
sleep = build_stage10_reference_runtime(autonomous_mortal=True)
detector = Stage12DetectionPolicy(
    version="i1-world-preset-diagnostic-v1",
    window=12, stagnation_steps=3, stagnation_tolerance=0.05,
    loop_repetitions=2, loop_max_period=2, entropy_min_samples=3,
    entropy_warning_fraction=0.25, bias_min_outcomes_each=2,
    attribution_bias_threshold=0.75)
params = dict(
    world_config=base.world.config, layout=base.world._layout,
    safety_config=base.stage3.substrate.safety._config,
    safety_facts=base._canonical_safety._innate,
    protected_integrity_threshold=(
        base.stage3.control._config.protected_integrity_threshold),
    stage11_config=base._stage11_config,
    stage10_config=replace(sleep._stage10_config,
                           stage9=base._stage11_config.stage9),
    equipment=base.equipment, detector_policy=detector,
    diagnostic_sample_cost_uc=1, module_occupancy_cost_uc=1,
)
with TemporaryDirectory() as folder:
    reports = []
    for mode in ("canonical", "td_read_masked"):
        identity = "i1:eco:a1:contract:" + mode
        path = str(Path(folder) / (mode + ".sqlite"))
        with a1_matched_temperament_birth(life_id=identity, seed=1):
            actor = birth_i1_m11(db_path=path, life_id=identity, **params)
        rows, adapters = [], []
        with actor:
            initial = actor._runtime.temperament_parameters.as_dict()
            setpoints = dict(actor._runtime.value_needs.config.setpoints)
            scales = dict(actor._runtime.value_needs.config.normalization_scales)
            with a1_decision_read_scope(
                mode=mode, reads=rows, adapters=adapters
            ):
                for _ in range(24):
                    receipt = actor.run_step()
                    if receipt.status == "dead":
                        break
        audited = SQLiteLifeLedger.audit_read_only(
            path=path, expected_individual_id=identity)
        assert audited.generation == receipt.generation
        assert audited.journal_head == receipt.journal_head
        cold = audited_life_metrics(
            path=path, individual_id=identity, horizon=24,
            setpoints=setpoints, scales=scales,
        )
        alignment = audited_a1_decision_alignment(
            path=path, identity=identity, audited=cold,
            reads=rows, adapters=adapters, mode=mode,
        )
        assert alignment["read_count"] == len(rows)
        assert alignment["stage8_direct_joined"] > 0
        assert alignment["pending_adapters_joined"] > 0
        assert alignment["planning_winners_joined"] > 0
        assert alignment["scope"] == (
            "M11_ANCHORED_EXTERNAL_OBSERVER_NOT_INDEPENDENT_CAUSAL_GO")
        assert any(x["source"] == "planning_local" for x in rows)
        assert any(x["source"] == "stage8_direct" for x in rows)
        assert any(x["original_status"] == "learned" for x in rows)
        assert adapters, "pending Stage8 adapter not reached"
        if mode == "canonical":
            assert not any(x["masked"] for x in rows)
        else:
            assert any(x["masked"] for x in rows)
            assert not any(x["delivered_status"] == "learned"
                           for x in adapters)
        reports.append((initial, rows, audited))
    assert reports[0][0] == reports[1][0]
    assert reports[0][2].individual_id != reports[1][2].individual_id
"""
            env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
                       PYTHONPATH=os.pathsep.join((
                           str(generated), str(ROOT / "src"), str(ROOT / "tools"))))
            result = subprocess.run(
                [sys.executable, "-B", "-c", script], cwd=ROOT,
                env=env, text=True, capture_output=True, timeout=240)
            self.assertEqual(result.returncode, 0,
                             result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
