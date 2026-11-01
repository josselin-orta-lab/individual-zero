"""A2-R no-cohort source/preset -> fresh born config -> M11 parity.

Two disposable one-step technical lives, one in each reward mode. The
repo/source lock is obtained from an actual CI checkout, not a cohort report.
"""
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
from build_i1_fork import generate

CHILD = r'''
import os
from pathlib import Path
from tempfile import TemporaryDirectory

from i1lab.i1_birth import birth_i1_m11
from i1lab.sqlite_life_store import RecoveryBlocked
from i1_eco_a1_worlds import a1_world_parameters
from i1_eco_a2r_birth import IDENTITIES, a2r_matched_reward_birth
from i1_a2r_source_birth_audit import (
    reconstruct_pristine_birth, verify_native_birth, verify_source_checkout,
    verify_generated_fork,
)
from run_i1_world_preset import load_preset, _birth_parameters

root=Path(os.environ["A2R_SOURCE_ROOT"]).resolve()
generated=Path(os.environ["A2R_GENERATED_ROOT"]).resolve()
sha=os.environ["A2R_COMMIT"]
tree=os.environ["A2R_TREE"]
preset=os.environ["A2R_PRESET"]
assert verify_source_checkout(root=root, expected_commit=sha,
                               expected_tree=tree,
                               expected_preset=preset)["checkout_clean_and_pinned"]
assert verify_generated_fork(root=root,generated=generated)["source_and_built_files_match"]
base, _=load_preset("oasis")
params,_=_birth_parameters(base)
with TemporaryDirectory(prefix="a2r-source-born-m11-smoke-") as folder:
    for mode in ("CANONICAL_ABS","RESEARCH_DEFICIT"):
        role="native"
        seed=2001
        identity=IDENTITIES[(role,seed,mode)]
        src=reconstruct_pristine_birth(role=role,seed=seed,mode=mode,
                                        preset_sha256=preset)
        assert src["identity"]==identity and src["q_at_birth_empty"]
        config,_=a1_world_parameters(params,role=role)
        config={**config,"diagnostic_sample_cost_uc":1,
                "module_occupancy_cost_uc":1}
        db=str(Path(folder)/(mode+".sqlite"))
        with a2r_matched_reward_birth(
            life_id=identity,role=role,seed=seed,mode=mode):
            actor=birth_i1_m11(db_path=db,life_id=identity,**config)
        with actor:
            step=actor.run_step()
            assert step.generation==1
        result=verify_native_birth(
            db_path=db,role=role,seed=seed,mode=mode,
            expected_source_commit=sha,expected_source_tree=tree,
            expected_preset_sha256=preset,checkout_root=root,
            generated_root=generated,allow_incomplete=True)
        assert result["m11_runtime_contract_verified"]
        assert result["m11_q_td_full_vector_reconciled"]
        assert result["original_archive_sha_bound"] is False
        assert result["external_run_event_sha_attested"] is False
        assert result["study_admissible"] is False
        assert result["general_L3"]=="NOT_ESTABLISHED"
        try:
            verify_native_birth(
                db_path=db,role=role,seed=seed,
                mode=("CANONICAL_ABS" if mode=="RESEARCH_DEFICIT"
                      else "RESEARCH_DEFICIT"),
                expected_source_commit=sha,expected_source_tree=tree,
                expected_preset_sha256=preset,checkout_root=root,
                generated_root=generated,allow_incomplete=True)
        except (ValueError, RecoveryBlocked):
            pass
        else:
            raise AssertionError("accepted signed M11 under an incompatible reward-mode source")
print("A2R_SOURCE_TO_BIRTH_TO_M11_TWO_NATIVE_ZERO_PRIOR_LIVES_OK")
'''


class NativeSourceBirthAttestation(unittest.TestCase):
    def test_source_to_pristine_birth_and_m11_original(self):
        with TemporaryDirectory(prefix="a2r-source-build-") as folder:
            generated=Path(folder).resolve()/"generated"
            generate(generated)
            sha=subprocess.check_output(
                ["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
            tree=subprocess.check_output(
                ["git","rev-parse","HEAD^{tree}"],cwd=ROOT,text=True).strip()
            from hashlib import sha256
            preset=sha256((ROOT/"src/i1/lab/world_presets/oasis.json").read_bytes()).hexdigest()
            env=dict(os.environ,PYTHONDONTWRITEBYTECODE="1",
                     A2R_SOURCE_ROOT=str(ROOT),A2R_GENERATED_ROOT=str(generated),
                     A2R_COMMIT=sha,A2R_TREE=tree,A2R_PRESET=preset)
            env["PYTHONPATH"]=os.pathsep.join(
                (str(generated),str(ROOT/"src"),
                 str(ROOT/"tools"),str(ROOT/"tools/research")))
            run=subprocess.run([sys.executable,"-B","-c",CHILD],cwd=ROOT,env=env,
                               capture_output=True,text=True,timeout=240)
            self.assertEqual(run.returncode,0,run.stderr[-7000:]+run.stdout[-2000:])
            self.assertIn("A2R_SOURCE_TO_BIRTH_TO_M11_TWO_NATIVE_ZERO_PRIOR_LIVES_OK",
                          run.stdout)


if __name__=="__main__":
    unittest.main()
