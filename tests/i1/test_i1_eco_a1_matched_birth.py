"""A1 research birth pairing: real M11, no steps or adaptive claim."""
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from build_i1_fork import generate


class A1MatchedBirthContract(unittest.TestCase):
    def test_two_distinct_mortal_births_share_only_innate_temperament(self):
        with TemporaryDirectory(prefix="i1-eco-a1-matching-") as tmp:
            generated = Path(tmp) / "generated"
            generate(generated)
            script = r"""
from pathlib import Path
from tempfile import TemporaryDirectory
from i1lab.i1_birth import birth_i1_m11, recover_i1_m11
from i1lab.i1_natural_runtime import I1Runtime
from i1lab.i1_birth_temperament import temperament_for_life
from i1lab.sqlite_life_store import SQLiteLifeLedger
from run_i1_world_preset import load_preset, _birth_parameters
from i1_eco_a1_matched_birth import a1_matched_temperament_birth

preset, _ = load_preset("oasis")
params, _ = _birth_parameters(preset)
ids = ("i1:eco:a1:contract:canonical",
       "i1:eco:a1:contract:td_read_masked")
assert ids[0] != ids[1]
assert temperament_for_life(ids[0]) != temperament_for_life(ids[1])

with TemporaryDirectory() as d:
    results = []
    for i, identity in enumerate(ids):
        path = str(Path(d) / ("arm" + str(i) + ".sqlite"))
        # A0 canonical interface is preserved; the scope touches only one
        # temporary birth projection and never patches the living instance.
        with a1_matched_temperament_birth(life_id=identity, seed=1):
            actor = birth_i1_m11(db_path=path, life_id=identity, **params)
        with actor:
            rt = actor._runtime
            t = rt.temperament_parameters
            initial = t.as_dict()
            cfg = rt._stage11_config.stage9.stage8.stage7.stage6.stage4
            measures = (
                dict(cfg.gatekeeper.weights),
                dict(cfg.value_needs.weights),
                cfg.competition.inertia,
                rt._stage11_config.stage9.stage8.evaluation.extrinsic_gain,
                rt.world.config.digest(),
                dict(rt.world.body.as_dict()),
            )
            assert rt.scheduler.t_monde == 0
            assert rt.journal.entry_count == 0
            receipt = actor.run_step()
            assert receipt.status in ("active", "dead")
            assert actor._runtime.scheduler.t_monde == 1
        audit = SQLiteLifeLedger.audit_read_only(path=path,
                                                 expected_individual_id=identity)
        assert audit.generation == 1
        assert audit.journal_head == receipt.journal_head
        assert audit.status == receipt.status
        results.append((initial, measures, audit, path))
    assert results[0][0] == results[1][0]
    assert results[0][1] == results[1][1]
    assert results[0][2].individual_id != results[1][2].individual_id
    # No cold resurrection: a dead life cannot be recovered.
    if results[0][2].status == "active":
        identity = ids[0]
        def factory():
            # A fresh separately constructed canonical I1Runtime, same source
            # selected only before the owner is created.
            with a1_matched_temperament_birth(life_id=identity, seed=1):
                return I1Runtime(
                    birth_life_id=identity, **params,
                    autonomous_mortal=True, wal_path=None,
                    m11_sqlite_custody=True,
                )
        with recover_i1_m11(
            db_path=results[0][3], life_id=identity, runtime_factory=factory
        ) as cold:
            assert cold._runtime.temperament_parameters.as_dict() == results[0][0]
            assert cold._runtime.world.config.digest() == results[0][1][4]
    with __import__("unittest").TestCase().assertRaises(ValueError):
        with a1_matched_temperament_birth(life_id=ids[0], seed=99):
            pass
"""
            env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
                       PYTHONPATH=os.pathsep.join((
                           str(generated), str(ROOT / "src"), str(ROOT / "tools"))))
            completed = subprocess.run(
                [sys.executable, "-B", "-c", script], cwd=ROOT, env=env,
                text=True, capture_output=True, timeout=180)
            self.assertEqual(completed.returncode, 0,
                             completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
