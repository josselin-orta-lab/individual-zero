"""Observer-only v4 M11 body/reward attribution on unforced natural oasis lives.

No action control, reward, UC, physiology or owner edits; never infer a motor GO.
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


class NaturalV4RewardAudit306(unittest.TestCase):
    def test_natural_oasis_m11_water_reward_and_cold_parity(self):
        with TemporaryDirectory(prefix="i1-306-reward-") as home:
            generated = Path(home) / "generated"
            generate(generated)
            code = r"""
import json
from collections import Counter
from math import isclose
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from i1.modules.value_needs import BODY_VARIABLES, ValueAndNeeds
from i1lab.i1_birth import birth_i1_m11, recover_i1_m11
from i1lab.i1_natural_runtime import I1Runtime
from i1lab.sqlite_life_store import SQLiteLifeLedger
from run_i1_world_preset import load_preset, _birth_parameters

preset, _ = load_preset("oasis")
params, _ = _birth_parameters(preset)
params = dict(params, diagnostic_sample_cost_uc=1, module_occupancy_cost_uc=1)
identity = "i1:306:natural-v4-reward-observer"
TOTAL, SPLIT = 12, 6
original = ValueAndNeeds.reward_between

def factory():
    return I1Runtime(birth_life_id=identity, wal_path=None,
                     autonomous_mortal=True, m11_sqlite_custody=True, **params)

def arm(path, cold):
    observed = []
    current = []
    def wrapped(self, before, after):
        result = original(self, before, after)
        weights, setpoints = self.config.weights, self.config.setpoints
        components = {name: float(weights[name]) * (
            abs(float(before[name]) - float(setpoints[name]))
            - abs(float(after[name]) - float(setpoints[name])))
            for name in BODY_VARIABLES}
        assert isclose(result, sum(components.values()), abs_tol=1e-9)
        current.append({"before": dict(before), "after": dict(after),
                        "reward": result, "components": components})
        return result

    def drive(life, count):
        for _ in range(count):
            before = dict(life._runtime.world.body.as_dict())
            current.clear()
            receipt = life.run_step()
            assert receipt.status == "active", receipt
            rt = life._runtime
            after = dict(rt.world.body.as_dict())
            # Exactly one reward registered for each truly applied step.
            assert len(current) == 1, (receipt.world_step, current)
            row = dict(current[0])
            assert row["before"] == before and row["after"] == after
            assert "i1-living-physical-defaults-v4-metabolic-coupling" in rt.world.config.version
            experienced = [e.causal_event for e in rt.journal.entries_since(0)
                           if e.causal_event.get("kind") == "command_experienced"
                           and e.causal_event.get("t_monde") == receipt.world_step]
            assert len(experienced) == 1, (receipt.world_step, experienced)
            row.update(step=receipt.world_step, primitive=experienced[0]["primitive"],
                       head=receipt.journal_head, generation=receipt.generation)
            observed.append(row)

    with patch.object(ValueAndNeeds, "reward_between", wrapped):
        with birth_i1_m11(db_path=path, life_id=identity, **params) as life:
            drive(life, SPLIT if cold else TOTAL)
            if cold:
                before_cold = life._runtime.q_active.export_causal_state()
                head = life._runtime.journal.head_hash
        if cold:
            audit = SQLiteLifeLedger.audit_read_only(path=path, expected_individual_id=identity)
            assert audit.may_recover and audit.generation == SPLIT and not audit.pending_intent
            with recover_i1_m11(db_path=path, life_id=identity,
                                runtime_factory=factory) as life:
                assert life._runtime.q_active.export_causal_state() == before_cold
                assert life._runtime.journal.head_hash == head
                drive(life, TOTAL - SPLIT)
        audit = SQLiteLifeLedger.audit_read_only(path=path, expected_individual_id=identity)
        assert audit.may_recover and audit.generation == TOTAL and not audit.pending_intent
        assert audit.journal_head == observed[-1]["head"]
    return observed

with TemporaryDirectory(prefix="i1-306-m11-") as home:
    control = arm(str(Path(home) / "control.sqlite"), False)
    cold = arm(str(Path(home) / "cold.sqlite"), True)
assert cold == control, "observer altered reward, physical outcomes or M11 continuity"
drinks = [x for x in control if x["primitive"] == "boire"]
assert drinks, "this natural birth no longer exposes any drink witness"
for x in drinks:
    assert x["after"]["water"] > x["before"]["water"]
print("I1_306_NATURAL_V4_REWARD_AUDIT=" + json.dumps({
    "steps": len(control), "drinks": len(drinks),
    "primitives": dict(Counter(x["primitive"] for x in control)),
    "drink_water_components": [x["components"]["water"] for x in drinks],
    "drink_total_rewards": [x["reward"] for x in drinks],
    "cold_exact_parity": True, "owner_mutated_by_observer": False,
    "causal_motor_learning": "NOT_ESTABLISHED",
}, sort_keys=True))
"""
            env = dict(os.environ,
                       PYTHONPATH=os.pathsep.join((str(generated),
                                                   str(ROOT / "src"),
                                                   str(ROOT / "tools"))),
                       PYTHONDONTWRITEBYTECODE="1")
            proc = subprocess.run([sys.executable, "-B", "-c", code],
                                  cwd=ROOT, env=env, text=True, capture_output=True)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertIn("I1_306_NATURAL_V4_REWARD_AUDIT=", proc.stdout)
            print(proc.stdout, flush=True)


if __name__ == "__main__":
    unittest.main()
