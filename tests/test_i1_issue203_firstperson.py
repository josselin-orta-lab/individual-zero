"""Issue #203: active I1 local perception regression on frozen experimental fork."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_i1_fork import generate


class I1Issue203Regression(unittest.TestCase):
    def test_inherited_stage4_stage5_and_stage9_perception(self):
        root = Path(__file__).resolve().parents[1]
        with TemporaryDirectory() as d:
            p = Path(d)
            generated = p / "generated"
            generate(generated)
            suite_dir = p / "suite"
            suite_dir.mkdir()
            for file in ("test_stage4_runtime.py", "test_stage5_trait_battery.py",
                         "test_stage9_concurrent_cause_audit.py"):
                source = (root / "tests" / file).read_text()
                source = source.replace("from i0.", "from i1.").replace(
                    "import i0.", "import i1.").replace(
                    "from lab.", "from i1lab.").replace("import lab.", "import i1lab.")
                # Stage9's external subprocess auditor is intentionally an I0-only
                # independent verifier; run that original test unmodified separately.
                if file == "test_stage9_concurrent_cause_audit.py":
                    source = source.replace(
                        "def test_standalone_operator_verifier_checks_both_contrast_histories(self):",
                        "def disabled_i0_only_operator_verifier(self):"
                    )
                (suite_dir / file).write_text(source)
            env = {**os.environ, "PYTHONPATH": str(generated) + os.pathsep + str(root / "src")}
            result = subprocess.run(
                [sys.executable, "-m", "unittest", "discover", "-s", str(suite_dir),
                 "-p", "test_stage*.py", "-v"],
                cwd=root, env=env, capture_output=True, text=True, timeout=240)
            print(result.stdout)
            print(result.stderr)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Ran 25 tests", result.stderr)

    def test_real_active_model_birth_stays_local(self):
        root = Path(__file__).resolve().parents[1]
        with TemporaryDirectory() as d:
            p = Path(d)
            generated = p / "generated"
            generate(generated)
            env = {**os.environ, "PYTHONPATH": str(generated) + os.pathsep + str(root / "src")}
            experiment = r"""
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from i1lab.world import Position
from i1lab.stage11_reference_fixture import build_stage11_reference_runtime
from i1lab.stage10_reference_fixture import build_stage10_reference_runtime
from i1lab.i1_active_runtime import ExperimentalI1Stage12Runtime
from i1.modules.stage12_detectors import Stage12DetectionPolicy
from i1.experimental.stage6_visible_delta_shadow import ShadowVisibleDeltaModel, FIELDS

s11 = build_stage11_reference_runtime(autonomous_mortal=True)
s10 = build_stage10_reference_runtime(autonomous_mortal=True)
origin = s11.world.position
east = origin.moved("east")
far = east.moved("east")
deltas = tuple((a, tuple((k, int(k == "x" and a == "MOVE_E"))
                 for k in FIELDS)) for a in ("MOVE_E", "COLLECT_B"))
model = ShadowVisibleDeltaModel("stage6-visible-deltas-shadow-v1", "a"*64,
                               deltas, (("MOVE_E", 8), ("COLLECT_B", 8)))
policy = Stage12DetectionPolicy(
    version="issue203-i1-active-v1", window=12, stagnation_steps=3,
    stagnation_tolerance=.05, loop_repetitions=2, loop_max_period=2,
    entropy_min_samples=3, entropy_warning_fraction=.25,
    bias_min_outcomes_each=2, attribution_bias_threshold=.75)
sleep = replace(s10._stage10_config.sleep, fatigue_gain=0.0,
                night_weight=0.0, consolidation_weight=0.0)
cfg = replace(s10._stage10_config, stage9=s11._stage11_config.stage9, sleep=sleep)
world = replace(s11.world.config, version="issue203-i1-active-world",
                initial_body=replace(s11.world.config.initial_body,
                                     food=10.0, water=85.0, energy=60.0))
with TemporaryDirectory() as d:
    for name, resources, water_sources, creatures in (
        ("hidden_food", ((far,"berry_b",3),), frozenset(), frozenset()),
        ("visible_food", ((east,"berry_b",3),), frozenset(), frozenset()),
        ("hidden_water", (), frozenset({far}), frozenset()),
        ("visible_water", (), frozenset({east}), frozenset()),
        ("distant_creature", (), frozenset(), frozenset({Position(origin.x+5,origin.y)})),
    ):
        layout = replace(s11.world._layout, resources=resources,
                         water_sources=water_sources, creatures=creatures,
                         obstacles=frozenset(), lethal_zones=frozenset(),
                         danger_zones=frozenset())
        life = ExperimentalI1Stage12Runtime(
            world_config=world,layout=layout,
            safety_config=s11.stage3.substrate.safety._config,
            safety_facts=s11._canonical_safety._innate,
            protected_integrity_threshold=s11.stage3.control._config.protected_integrity_threshold,
            stage11_config=s11._stage11_config,stage10_config=cfg,
            equipment=s11.equipment,autonomous_mortal=True,
            wal_path=str(Path(d)/(name+".wal")),
            birth_life_id="i1:issue203:"+name,
            diagnostic_sample_cost_uc=1,module_occupancy_cost_uc=1,
            detector_policy=policy,i1_model_enabled=True,i1_model=model)
        capture=life.world.capture_local(t_monde=1)
        visible={(e.entity_type,e.position.x,e.position.y)
                 for e in capture.visible_entities}
        assert all(abs(x-origin.x)+abs(y-origin.y)<=1 for _,x,y in visible)
        if name=="hidden_food":
            assert not any(e.entity_type=="berry_b" for e in capture.visible_entities)
        if name=="visible_food":
            assert ("berry_b",east.x,east.y) in visible
        if name=="hidden_water":
            assert not any(e.entity_type=="water_source" for e in capture.visible_entities)
        if name=="visible_water":
            assert ("water_source",east.x,east.y) in visible
        if name=="distant_creature":
            assert not any(e.entity_type=="creature" for e in capture.visible_entities)
        for step in range(3):
            result=life.run_step()
            if result.execution_status=="dead": break
        assert life.journal.verify()
        import json
        events=[json.loads(line)["causal_event"] for line in
                life.journal.canonical_bytes().splitlines()]
        proposals=[e for e in events if e["kind"]=="i1_partial_instrumental_option_proposed"]
        if name in ("hidden_food","hidden_water","visible_water","distant_creature"):
            assert not proposals, (name, proposals)
        if name=="visible_food":
            assert proposals, "visible food must be actionable by enabled I1"
            assert any(e["kind"]=="command_admitted" and
                e["data"]["option_ref"] in {p["data"]["option_ref"] for p in proposals}
                for e in events), "model option must be admitted"
        for e in events:
            if e["kind"]=="i1_partial_preaction_forecast":
                f=e["data"]["result"]
                assert f["safe"] is None and f["terminal"] is None
                assert f["causal_responsibility"] is None
        print(name,"PASS", "model_proposals",len(proposals))
"""
            result = subprocess.run(
                [sys.executable, "-c", experiment], cwd=root, env=env,
                capture_output=True,text=True,timeout=180)
            print(result.stdout)
            print(result.stderr)
            self.assertEqual(result.returncode,0,result.stderr+"\n"+result.stdout)


if __name__ == "__main__":
    unittest.main()
