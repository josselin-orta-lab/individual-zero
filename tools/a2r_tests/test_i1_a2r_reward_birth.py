"""L1 only: birth-scoped TD reward policy and cold M11 checks; NO cohort."""
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from build_i1_fork import generate

_CHILD = r'''
from pathlib import Path
from tempfile import TemporaryDirectory
from copy import deepcopy
from i1.modules.value_needs import ValueAndNeeds, ValueNeedsConfig
from i1lab.i1_birth import birth_i1_m11, recover_i1_m11
from i1lab.i1_natural_runtime import I1Runtime
from i1lab.sqlite_life_store import SQLiteLifeLedger, RecoveryBlocked
from i1lab import i1_natural_runtime, i1_active_value_needs
from run_i1_world_preset import load_preset, _birth_parameters
from i1_eco_a1_worlds import a1_world_parameters
from i1_eco_a2r_birth import (
    A2RDeficitValueNeeds, CANONICAL_ABS, RESEARCH_DEFICIT, MODES, ROLES, SEEDS,
    MATRIX, ORDER, IDENTITIES, REWARD_STATE_KEY, REWARD_STATE_SCHEMA,
    REWARD_VERSION_SUFFIX, a2r_matched_reward_birth, verify_born_reward_owner,
)

assert len(MATRIX) == len(ORDER) == 96 and set(MATRIX) == set(ORDER)
assert len(set(IDENTITIES.values())) == 96
assert tuple(SEEDS) == tuple(range(2001, 2025))

names = ('energy', 'food', 'water', 'integrity')
setpoints = dict.fromkeys(names, 60.)
weights = dict.fromkeys(names, 1.)
scales = dict.fromkeys(names, 100.)
config = ValueNeedsConfig(version='a2r-standalone-test' + REWARD_VERSION_SUFFIX,
    setpoints=setpoints, weights=weights, normalization_scales=scales,
    p_min=.1, contribution_ttl_steps=1)
owner = A2RDeficitValueNeeds(config)
assert owner.owner_id == 'value_needs'
before = dict.fromkeys(names, 60.)
after = dict(before)
before['water'], after['water'] = 48., 88.
assert owner.reward_between(before, after) == 12.
assert ValueAndNeeds(config).reward_between(before, after) == -16.
state = owner.export_causal_state()
assert state[REWARD_STATE_KEY] == REWARD_STATE_SCHEMA
owner.restore_causal_state(deepcopy(state))
for key, value in ((REWARD_STATE_KEY, 'forged'), ('config_version', 'wrong')):
    forged = deepcopy(state)
    forged[key] = value
    try:
        owner.restore_causal_state(forged)
    except ValueError:
        pass
    else:
        raise AssertionError('research reward owner accepted forged birth mode/state')
assert owner.export_causal_state() == state
try:
    A2RDeficitValueNeeds(ValueNeedsConfig(version='unregistered', setpoints=setpoints,
        weights=weights, normalization_scales=scales, p_min=.1,
        contribution_ttl_steps=1))
except ValueError:
    pass
else:
    raise AssertionError('deficit reward owner accepted unversioned canonical config')

base, _ = load_preset('oasis')
params, _ = _birth_parameters(base)
params, local = a1_world_parameters(params, role='native')
params = {**params, 'diagnostic_sample_cost_uc': 1,
          'module_occupancy_cost_uc': 1}
seed = 2001
role = 'native'

def new_runtime(mode):
    identity = IDENTITIES[(role, seed, mode)]
    with a2r_matched_reward_birth(life_id=identity, role=role, seed=seed, mode=mode):
        actor = I1Runtime(birth_life_id=identity, autonomous_mortal=True,
            m11_sqlite_custody=True, wal_path=None, **params)
        verify_born_reward_owner(actor.value_needs, mode=mode)
        assert actor.value_needs.config.weights == actor.temperament_parameters.body_weights
        return actor

def born(db_path, mode):
    identity = IDENTITIES[(role, seed, mode)]
    with a2r_matched_reward_birth(life_id=identity, role=role, seed=seed, mode=mode):
        actor = birth_i1_m11(db_path=str(db_path), life_id=identity, **params)
        verify_born_reward_owner(actor._runtime.value_needs, mode=mode)
    assert i1_natural_runtime.configure_birth_temperament is original_temperament
    assert i1_active_value_needs.I1ActiveValueNeeds is original_owner
    return actor

original_temperament = i1_natural_runtime.configure_birth_temperament
original_owner = i1_active_value_needs.I1ActiveValueNeeds
try:
    with a2r_matched_reward_birth(life_id='i1:wrong', role=role, seed=seed, mode=RESEARCH_DEFICIT):
        pass
except ValueError:
    pass
else:
    raise AssertionError('A2-R accepted nonpreregistered identity')
try:
    with a2r_matched_reward_birth(life_id=IDENTITIES[(role, seed, RESEARCH_DEFICIT)],
                                  role=role, seed=seed, mode=RESEARCH_DEFICIT):
        pass
except RuntimeError:
    pass
else:
    raise AssertionError('A2-R accepted birth scope without a birth')
assert i1_natural_runtime.configure_birth_temperament is original_temperament
assert i1_active_value_needs.I1ActiveValueNeeds is original_owner

with TemporaryDirectory() as td:
    td = Path(td)
    virgin = {}
    for mode in MODES:
        identity = IDENTITIES[(role, seed, mode)]
        db = td / (mode + '.sqlite')
        with born(db, mode) as actor:
            rt = actor._runtime
            virgin[mode] = (dict(rt.world.body.as_dict()), rt.world.capture_local(t_monde=1).as_dict(),
                            dict(rt.world.inventory()))
            assert len(rt.q_active.export_causal_state()['weights']) == 0
            first = actor.run_step()
            assert first.generation == 1 and first.status == 'active'
            snap = actor._runtime.value_needs.export_causal_state()
            assert (REWARD_STATE_KEY in snap) == (mode == RESEARCH_DEFICIT)
            assert (REWARD_VERSION_SUFFIX in snap['config_version']) == (mode == RESEARCH_DEFICIT)
        receipt = SQLiteLifeLedger.audit_read_only(path=str(db), expected_individual_id=identity)
        assert receipt.generation == 1 and receipt.journal_head == first.journal_head
        if mode == RESEARCH_DEFICIT and first.status == 'active':
            with recover_i1_m11(db_path=str(db), life_id=identity,
                                runtime_factory=lambda: new_runtime(mode)) as resumed:
                second = resumed.run_step()
                assert second.generation == 2
                assert resumed._runtime.value_needs.export_causal_state()[REWARD_STATE_KEY] == REWARD_STATE_SCHEMA
            assert SQLiteLifeLedger.audit_read_only(path=str(db),
                        expected_individual_id=identity).generation == 2
            try:
                with recover_i1_m11(db_path=str(db), life_id=identity,
                      runtime_factory=lambda: I1Runtime(birth_life_id=identity,
                          autonomous_mortal=True, m11_sqlite_custody=True,
                          wal_path=None, **params)):
                    pass
            except RecoveryBlocked:
                pass
            else:
                raise AssertionError('M11 accepted a natural rather than registered reward-mode birth')
    assert virgin[CANONICAL_ABS] == virgin[RESEARCH_DEFICIT], 'reward intervention changed born physical/perception or inventory state'
print('I1_A2R_BIRTH_OWNER_AND_COLD_M11_L1_OK')
'''

class A2RBirthL1Tests(unittest.TestCase):
    def test_reward_owner_origin_and_cold_m11_two_step_smoke(self):
        with TemporaryDirectory() as folder:
            output = Path(folder) / "i1build"
            generate(output)
            env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
            env["PYTHONPATH"] = os.pathsep.join((
                str(output), str(ROOT / "src"), str(ROOT / "tools")))
            run = subprocess.run([sys.executable, "-B", "-c", _CHILD],
                                 cwd=ROOT, env=env, capture_output=True,
                                 text=True, timeout=240)
            self.assertEqual(run.returncode, 0, run.stderr[-6500:] + run.stdout[-2000:])
            self.assertIn("I1_A2R_BIRTH_OWNER_AND_COLD_M11_L1_OK", run.stdout)

if __name__ == "__main__":
    unittest.main()
