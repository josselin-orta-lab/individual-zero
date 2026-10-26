"""#557: old-memory pricing must not mint dormant I1 planning or cycle UC.

A canonical newborn's actual parent-produced budget is compared against the
final runtime budget. This is a structural contract, not a behavioral cohort
or a claim of positive old-episode natural recall.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class OldMemoryNoUcSubsidy557(unittest.TestCase):
    def test_generated_canonical_birth_old_recall_has_no_passive_uc_grant(self):
        with TemporaryDirectory() as directory:
            generated = Path(directory) / "generated"
            built = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                 "--output", str(generated)],
                cwd=ROOT, capture_output=True, text=True, timeout=90,
            )
            self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
            program = r"""
from unittest.mock import patch
from run_i1_world_preset import load_preset, _birth_parameters
from i1lab.i1_d2_runtime import I1WaterPrudentRuntime
from i1lab.i1_natural_runtime import (
    I1Runtime, I1_AFFORDANCE_OPERATION, _OLD_RECALL_OPERATION,
    _OLD_RECALL_COST_UC, _H_RECALL_OPERATION, _SLEEP_RECALL_OPERATION,
    _PRIVATE_RECALL_OPERATION, _OPTION_INTENTION_OPERATION,
)

preset,_ = load_preset("empty-land")
params,_ = _birth_parameters(preset)
original_parent = I1WaterPrudentRuntime._parent_runtime_config
parents = []

def witness_parent(self, config):
    parent = original_parent(self, config)
    parents.append(parent)
    return parent

with patch.object(I1WaterPrudentRuntime, "_parent_runtime_config",
                  witness_parent):
    actor = I1Runtime(
        birth_life_id="i1:557:no-dormant-uc",
        autonomous_mortal=True, m11_sqlite_custody=True, wal_path=None,
        diagnostic_sample_cost_uc=1, module_occupancy_cost_uc=1,
        **params,
    )
assert len(parents) == 1, len(parents)

def budget_of(config):
    return config.stage9.stage8.stage7.stage6.stage4.compute_budget

base = budget_of(parents[0])
actual = actor.compute_budget._config
costs = actual.operation_costs
assert _OLD_RECALL_OPERATION not in base.operation_costs
assert _OLD_RECALL_COST_UC == costs[_OLD_RECALL_OPERATION] == 8

# The preexisting I1 producer allowances are retained. An old-episode
# observer may spend already-existing spare UC but gains no private budget.
other_planning = sum(costs[op] for op in (
    _H_RECALL_OPERATION, _SLEEP_RECALL_OPERATION,
    _PRIVATE_RECALL_OPERATION, _OPTION_INTENTION_OPERATION,
)) + base.operation_costs[I1_AFFORDANCE_OPERATION]
other_competition = sum(base.operation_costs[op] for op in (
    "competition_register", "competition_evaluate",
))
assert actual.cycle_ceiling - base.cycle_ceiling == (
    other_planning + other_competition
), (actual.cycle_ceiling, base.cycle_ceiling, other_planning,
    other_competition)
assert (actual.module_envelopes["planning"]
        - base.module_envelopes["planning"]) == other_planning
assert (actual.module_envelopes["competition"]
        - base.module_envelopes["competition"]) == other_competition
for module in set(base.module_envelopes) - {"planning", "competition"}:
    assert actual.module_envelopes[module] == base.module_envelopes[module]
assert actual.protected_capacity == base.protected_capacity
assert actual.protected_modules == base.protected_modules
assert _OLD_RECALL_OPERATION not in (
    _SLEEP_RECALL_OPERATION, _H_RECALL_OPERATION,
    _PRIVATE_RECALL_OPERATION, _OPTION_INTENTION_OPERATION,
)
print("I1_557_NO_DORMANT_OLD_RECALL_UC_SUBSIDY_OK")
"""
            env = os.environ.copy()
            env["PYTHONPATH"] = os.pathsep.join(
                (str(generated), str(ROOT / "src"), str(ROOT / "tools"))
            )
            result = subprocess.run(
                [sys.executable, "-c", program],
                cwd=ROOT, capture_output=True, text=True, env=env,
                timeout=120,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("I1_557_NO_DORMANT_OLD_RECALL_UC_SUBSIDY_OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
