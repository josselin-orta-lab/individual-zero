"""Short authentic A2-R M11/TD Q smoke, not part of the 96-life cohort.

Generates a disposable fork, runs four independently born technical lives
(two berry roles times two reward policies) for at most FOUR natural steps,
then calls the unchanged cold observer on original M11 journals. The 96
confirmatory identities are *never archived as evidence* by this test.
No forced commands, introspection affecting an actor, Q patch or long CI.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
from build_i1_fork import generate

_CHILD = r'''
from pathlib import Path
from tempfile import TemporaryDirectory
from i1lab.i1_birth import birth_i1_m11
from i1_eco_a1_worlds import a1_world_parameters
from i1_eco_a2r_birth import (
    CANONICAL_ABS, RESEARCH_DEFICIT, IDENTITIES, MODES,
    a2r_matched_reward_birth, verify_born_reward_owner,
)
from i1_a2r_q_replay import cold_replay_m11
from i1_a2r_pair_witness import cold_compare_pair
from i1_a2r_stage8_evidence import attest_native_stage8
from i1_a2r_affordance_cold import audit_native_affordance_evidence
from i1_a2r_postflight import (
    reconcile_native_evidence, reconcile_stage11_intrinsic_provenance,
)
from i1_a2r_intrinsic_cold import audit_stage11_intrinsic_magnitude
from i1_a2r_geographic_history_cold import replay_geographic_history
from i1_a2r_geo_intrinsic_join import reconcile_geographic_intrinsic
from i1_a2r_source_birth_audit import reconstruct_pristine_birth
from i1_a2r_m11_cold import evidence_life, compare_pre_reward, inspect_m11
from run_i1_world_preset import load_preset, _birth_parameters

SEED=2001
MAX_STEPS=4
results={}
with TemporaryDirectory(prefix="i1-a2r-native-cold-smoke-") as work:
    root=Path(work)
    base,preset_sha=load_preset("oasis")
    params,_=_birth_parameters(base)
    for role in ("native","reversed"):
        configured,_=a1_world_parameters(params,role=role)
        configured={**configured,"diagnostic_sample_cost_uc":1,
                    "module_occupancy_cost_uc":1}
        for mode in MODES:
            identity=IDENTITIES[(role,SEED,mode)]
            db=root/(role+"_"+mode+".sqlite")
            with a2r_matched_reward_birth(
                life_id=identity,role=role,seed=SEED,mode=mode):
                actor=birth_i1_m11(db_path=str(db),life_id=identity,**configured)
            with actor:
                runtime=actor._runtime
                verify_born_reward_owner(runtime.value_needs,mode=mode)
                td=runtime.q_active.config
                td_birth={
                    "version":td.version, "beta":td.beta, "eta":td.eta,
                    "lambda_e":td.lambda_e,
                    "feature_version":td.features.version,
                    "feature_names":list(td.features.feature_names),
                    "position_scale_x":td.features.position_scale_x,
                    "position_scale_y":td.features.position_scale_y,
                }
                physical=runtime.world.config
                clock={"day_steps":physical.day_steps,
                       "night_steps":physical.night_steps,
                       "night_start_step":physical.night_start_step}
                born_setpoints=dict(runtime.value_needs.config.setpoints)
                born_weights=dict(runtime.value_needs.config.weights)
                born_scales=dict(runtime.value_needs.config.normalization_scales)
                initial_body=dict(runtime.world.body.as_dict())
                initial_perception=runtime.world.capture_local(t_monde=1).as_dict()
                assert not runtime.q_active.export_causal_state()["weights"]
                observed=[]
                for _ in range(MAX_STEPS):
                    rc=actor.run_step()
                    observed.append(rc)
                    if rc.status=="dead":
                        break
                assert 1<=len(observed)<=MAX_STEPS
                assert observed[-1].generation==len(observed)
            cold=cold_replay_m11(
                path=str(db),identity=identity,mode=mode,
                setpoints=born_setpoints,weights=born_weights,
                born_td=td_birth,world_clock=clock,allow_incomplete=True)
            assert cold["full_q_replay_verified"] is True
            assert cold["birth_source_provenance_verified"] is False
            assert cold["adaptive_learning_go"]=="NOT_ESTABLISHED"
            assert cold["study_admissible"] is False
            assert cold["m11_identity"]==identity
            assert cold["generation"]==len(observed)
            assert cold["td_updates"]==len(cold["td_recurrences"])
            assert cold["native_q_checks"]>=0
            raw=inspect_m11(path=str(db),identity=identity,mode=mode,
                            allow_incomplete=True)
            pre=evidence_life(raw["events"],generation=raw["receipt"]["generation"],
                 status=raw["receipt"]["status"],mode=mode,
                 setpoints=born_setpoints,weights=born_weights)
            assert pre["td_returns_checked"]==cold["td_updates"]
            history=replay_geographic_history(
                raw["events"],final_exploration=raw["final_exploration"],
                birth=reconstruct_pristine_birth(
                    role=role,seed=SEED,mode=mode,preset_sha256=preset_sha),
                generation=raw["receipt"]["generation"])
            assert history["historic_visits_match_sealed_final_owner"] is True
            assert history["study_admissible"] is False
            reconstructed_birth=reconstruct_pristine_birth(
                role=role,seed=SEED,mode=mode,preset_sha256=preset_sha)
            assert reconstructed_birth["born_td"]==td_birth
            assert reconstructed_birth["setpoints"]==born_setpoints
            assert reconstructed_birth["weights"]==born_weights
            try:
                stage8=attest_native_stage8(
                    raw["events"],q_replay=cold,
                    calibration=reconstructed_birth["stage8_evaluation"],
                    td_version=reconstructed_birth["born_td"]["version"])
            except ValueError as exc:
                failed=[{"t":e.get("t_monde"),"cycle":e.get("cycle"),
                         "data":e.get("data")} for e in raw["events"]
                        if e.get("kind")=="stage8_option_evaluation"
                        and e.get("data",{}).get("learned_value_status")=="unlearned"
                        and e.get("data",{}).get("simulated_value_status")!="computed"]
                raise AssertionError(
                    "native Stage8 mismatch: "+str(exc)
                    +" candidate_events="+repr(failed[:3])) from exc
            assert (stage8["stage8_evaluations_recomputed"]
                    + stage8["stage8_other_evaluations_unreplayed"]
                    == cold["stage8_read_count"])
            assert stage8["all_native_evidence_recomputed"] is False
            assert stage8["learned_q_reads_recomputed"]<=cold["learned_stage8_reads"]
            assert stage8["preregistered_mechanism_exposed"] is False
            local=audit_native_affordance_evidence(
                raw["events"],q_replay=cold,birth=reconstructed_birth)
            assert local["preregistered_mechanism_exposed"] is False
            intrinsic=audit_stage11_intrinsic_magnitude(
                raw["events"],q_replay=cold,stage8_audit=stage8,
                birth=reconstructed_birth)
            joined=reconcile_stage11_intrinsic_provenance(
                stage8=stage8,intrinsic=intrinsic)
            geo_intrinsic=reconcile_geographic_intrinsic(
                geography=history,intrinsic=intrinsic,
                stage11_join=joined)
            assert geo_intrinsic["study_admissible"] is False
            assert joined["study_admissible"] is False
            assert (joined["still_quarantined_without_frontier_admissibility"]
                    == intrinsic["stage11_intrinsic_occurrences"])
            coverage=reconcile_native_evidence(
                stage8=stage8,local=local,replay=cold,
                require_complete=False)
            assert coverage["study_admissible"] is False
            assert coverage["preregistered_mechanism_exposed"] is False
            other=(CANONICAL_ABS if mode==RESEARCH_DEFICIT else RESEARCH_DEFICIT)
            try:
                cold_replay_m11(path=str(db),identity=identity,mode=other,
                    setpoints=born_setpoints,weights=born_weights,
                    born_td=td_birth,world_clock=clock,allow_incomplete=True)
            except ValueError:
                pass
            else:
                raise AssertionError("cold Q reader accepted wrong born reward policy")
            results[(role,mode)]=dict(
                pre=pre,body=initial_body,local=initial_perception,
                td=td_birth,setpoints=born_setpoints,weights=born_weights,
                scales=born_scales,
                journal_head=cold["m11_journal_head"],
                db_path=str(db), individual_id=identity,
                td_updates=cold["td_updates"],
                q_reads=cold["native_q_checks"],
                stage8_evidence=stage8["stage8_evaluations_recomputed"],
                stage8_blends=stage8["q_simulation_blends_recomputed"],
                local_recomputed=local["native_local_affordance_recomputed"],
                stage11_checked=joined["stage11_original_events_reconciled"],
            )
    for role in ("native","reversed"):
        c=results[(role,CANONICAL_ABS)]
        d=results[(role,RESEARCH_DEFICIT)]
        for key in ("body","local","td","setpoints","weights","scales"):
            assert c[key]==d[key], "pre-birth pair mismatch: "+key
        comparison=compare_pre_reward(canonical=c["pre"],candidate=d["pre"],
                                      setpoints=c["setpoints"],weights=c["weights"])
        assert comparison["pre_reward_prefix_equal"] is True
        assert comparison["full_q_replay_verified"] is False
        assert comparison["mechanism_exposed"] is False
        pair=cold_compare_pair(
            canonical_path=c["db_path"],candidate_path=d["db_path"],
            canonical_id=c["individual_id"],candidate_id=d["individual_id"],
            setpoints=c["setpoints"],weights=c["weights"],born_td=c["td"],
            world_clock=clock,allow_incomplete=True)
        assert pair["scope"]=="COLD_PAIRED_L1_DIAGNOSTIC_NOT_L3"
        assert pair["study_admissible"] is False
        assert pair["preregistered_mechanism_exposed"] is False
        assert pair["general_L3"]=="NOT_ESTABLISHED"
    assert sum(row["local_recomputed"] for row in results.values()) > 0
    print("A2R_NATIVE_M11_FOUR_SHORT_TECHNICAL_LIVES_Q_REPLAY_OK",
          sum(row["td_updates"] for row in results.values()),
          sum(row["q_reads"] for row in results.values()),
          sum(row["stage8_evidence"] for row in results.values()),
          sum(row["stage8_blends"] for row in results.values()))
'''


class NativeShortM11QReplay(unittest.TestCase):
    def test_four_short_lives_two_roles_two_modes(self):
        with TemporaryDirectory(prefix="i1-a2r-fork-only-") as folder:
            target=Path(folder)/"generated"
            generate(target)
            env=dict(os.environ,PYTHONDONTWRITEBYTECODE="1")
            env["PYTHONPATH"]=os.pathsep.join((
                str(target),str(ROOT/"src"),
                str(ROOT/"tools"),str(ROOT/"tools/research"),
            ))
            result=subprocess.run(
                [sys.executable,"-B","-c",_CHILD],
                cwd=ROOT,env=env,capture_output=True,
                text=True,timeout=240)
            self.assertEqual(result.returncode,0,
                             result.stderr[-8000:]+result.stdout[-2000:])
            self.assertIn("A2R_NATIVE_M11_FOUR_SHORT_TECHNICAL_LIVES_Q_REPLAY_OK",
                          result.stdout)


if __name__=="__main__":
    unittest.main()
