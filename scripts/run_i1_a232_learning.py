"""A2.32: preregistered paired I1 first-person learning opportunity audit.

Scientific results are external diagnostics, not I1 memories or Stage GO.
Protocol: docs/research/i1-a232-prereg-2026-10-16.en.md
"""
from __future__ import annotations
import argparse
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

from build_i1_fork import generate

STRATA=("CUE","INJURY","FAILURE","INDISTINGUISHABLE")


def experiment(output: Path, *, head: str) -> dict:
    output=output.resolve()
    with TemporaryDirectory(prefix="i1-a232-code-") as temp:
        generated=Path(temp)/"generated"
        generate(generated)
        sys.path.insert(0,str(generated))
        from i1.equipment import (EquipmentCorpus,EquipmentCorpusExample,
                                  SimulationNeighbor,SimulationState)
        from i1.interfaces import PrimitiveCommand
        from i1.experimental.stage6_visible_delta_shadow import fit_external_lab_shadow
        from i1lab.world import WorldBody, Position
        from i1lab.stage11_reference_fixture import build_stage11_reference_runtime
        from i1lab.stage10_reference_fixture import build_stage10_reference_runtime
        from i1lab.i1_active_runtime import ExperimentalI1Stage12Runtime
        from i1.modules.stage12_detectors import Stage12DetectionPolicy

        stage11=build_stage11_reference_runtime(autonomous_mortal=True)
        stage10=build_stage10_reference_runtime(autonomous_mortal=True)
        base=stage11.world.config
        origin=base.initial_position
        east=origin.moved("east")
        def visible(world,t):
            capture=world.capture_local(t_monde=t)
            return SimulationState(
                schema_version="simulation-state-v1",
                x=capture.position.x,y=capture.position.y,
                body=world.telemetry(),inventory=world.inventory(),
                current_water_source=capture.current_water_source,
                current_resources=capture.current_resources,
                adjacent=tuple(SimulationNeighbor(
                    direction=n.direction,x=n.position.x,y=n.position.y,
                    passable=n.passable,water_source=n.water_source,
                    resources=n.resources,creature=n.creature,
                ) for n in capture.adjacent),
                known_shelter_here=False,is_night=world.is_night(t),
            )
        training=[]
        for action in ("MOVE_E","COLLECT_B"):
            for i in range(8):
                cfg=replace(base,version=base.version+"-a232-training",
                    initial_body=replace(base.initial_body,
                        energy=60.0+i,food=28.0+i,water=70.0+i))
                resources=((origin,"berry_b",3+i),) if action=="COLLECT_B" else ()
                layout=replace(stage11.world._layout,obstacles=frozenset(),
                    water_sources=frozenset(),resources=resources,
                    danger_zones=frozenset(),lethal_zones=frozenset(),creatures=frozenset())
                w=WorldBody(config=cfg,layout=layout)
                before=visible(w,1)
                command=(PrimitiveCommand("se_deplacer",{"direction":"east"})
                         if action=="MOVE_E" else
                         PrimitiveCommand("collecter",{"target":"berry_b"}))
                transition=w.apply(command,t_monde=1)
                after=visible(w,2)
                assert not transition.lethal
                training.append(EquipmentCorpusExample(
                    f"a232:{action}:{i}",before,command,after,False))
        corpus=EquipmentCorpus("a232-prebirth-physical-training-v1",tuple(training))
        model=fit_external_lab_shadow(corpus=corpus)
        assert model.corpus_sha256==corpus.digest()

        policy=Stage12DetectionPolicy(version="a232-stage12-observer-v1",
            window=12,stagnation_steps=3,stagnation_tolerance=.05,
            loop_repetitions=2,loop_max_period=2,entropy_min_samples=3,
            entropy_warning_fraction=.25,bias_min_outcomes_each=2,
            attribution_bias_threshold=.75)
        sleep=replace(stage10._stage10_config.sleep,
            fatigue_gain=0.0,night_weight=0.0,consolidation_weight=0.0)
        stage10config=replace(stage10._stage10_config,
            stage9=stage11._stage11_config.stage9,sleep=sleep)
        output.mkdir(parents=True,exist_ok=True)
        raw_file=output/"lives.jsonl"
        results=[]
        with raw_file.open("w",encoding="utf-8") as out:
            for stratum in STRATA:
                for index in range(8):
                    common=f"a232:{stratum}:{index:02d}"
                    cfg=replace(base,version=base.version+"-a232-heldout-"+stratum,
                        initial_body=replace(base.initial_body,
                            energy=float(60+index%3),food=float(14+index),
                            water=float(75+index%4),integrity=100.0))
                    local=stratum=="FAILURE"
                    layout=replace(stage11.world._layout,
                        water_sources=frozenset(),
                        creatures=(frozenset({east}) if stratum=="CUE" and index%2==0
                            else frozenset()),
                        danger_zones=(frozenset({east}) if stratum=="INJURY" and index%2==0
                            else frozenset()),
                        lethal_zones=(frozenset({east}) if stratum=="INDISTINGUISHABLE" and index%2==0
                            else frozenset()),
                        obstacles=frozenset(),
                        resources=(((origin if local else east),"berry_b",4+index%3),))
                    layout.validate(cfg)
                    # Paired arm labels alternate execution order while
                    # maintaining separate worlds and I1 identities.
                    for exposed in ((index%2)==0,(index%2)!=0):
                        enabled=True
                        arm="exposed" if exposed else "control"
                        life_id="i1:"+common+":"+arm
                        exposed_world=(arm=="exposed")
                        own_layout=replace(layout,
                            creatures=(frozenset({east}) if stratum=="CUE" and exposed_world else frozenset()),
                            danger_zones=(frozenset({east}) if stratum=="INJURY" and exposed_world else frozenset()),
                            lethal_zones=(frozenset({east}) if stratum=="INDISTINGUISHABLE" and exposed_world else frozenset()))
                        wal=output/(stratum+"-"+str(index)+"-"+arm+".wal")
                        life=ExperimentalI1Stage12Runtime(
                            world_config=cfg,layout=own_layout,
                            safety_config=stage11.stage3.substrate.safety._config,
                            safety_facts=stage11._canonical_safety._innate,
                            protected_integrity_threshold=stage11.stage3.control._config.protected_integrity_threshold,
                            stage11_config=replace(stage11._stage11_config,local_threat_alerts=(stratum=="CUE")),
                            stage10_config=stage10config,
                            equipment=stage11.equipment,
                            autonomous_mortal=True,wal_path=str(wal),
                            birth_life_id=life_id,
                            diagnostic_sample_cost_uc=1,module_occupancy_cost_uc=1,
                            detector_policy=policy,i1_model_enabled=enabled,
                            i1_model=model,
                            i1_forecast_cost_uc=2,
                            **({
                                "scenario_id":"a232-forced-collect-"+str(index)+"-"+arm,
                                "scenario_version":"a232-forced-v1",
                                "scenario_events":(
                                    __import__("i1lab.injected_scenario",fromlist=["ScenarioEvent"]).ScenarioEvent(
                                        t_monde=1,sequence=0,
                                        operation="set_action_failure_schedule",
                                        payload={"primitive":"collecter","schedule":[True]},
                                        phase="before_step",
                                    ),
                                ),
                            } if stratum=="local_forced_failure" else {}),
                        )
                        steps=[]
                        failure=None
                        observed_body=[]
                        for _ in range(4):
                            try:
                                result=life.run_step()
                            except Exception as exc:
                                failure={"class":type(exc).__name__,"message":str(exc)[:300]}
                                break
                            observed_body.append(dict(life.world.telemetry()))
                            steps.append({"status":result.execution_status,
                                "command":result.command_primitive,
                                "option_ref":result.option_ref,
                                "source":result.source})
                            if result.execution_status!="applied":
                                break
                        events=[dict(x.causal_event) for x in life.journal.entries]
                        model_receipts=[e for e in events if e.get("kind")=="i1_partial_preaction_forecast"]
                        proposed={e["data"]["option_ref"] for e in events
                            if e.get("kind")=="i1_partial_instrumental_option_proposed"}
                        crossed={t["option_ref"] for e in events if e.get("kind")=="competition_cycle"
                            for t in e.get("data",{}).get("traces",())
                            if t.get("crossed") and t.get("option_ref") in proposed}
                        admissions={e["data"]["option_ref"] for e in events
                            if e.get("kind")=="command_admitted"}
                        applied={s["option_ref"] for s in steps if s["status"]=="applied"}
                        charges=[e["data"] for e in events if e.get("kind")=="compute_charge"
                            and e.get("data",{}).get("operation")=="i1_partial_model_forecast"]
                        prediction_violations=[
                            e for e in model_receipts if
                            any(e["data"]["result"].get(k) is not None
                            for k in ("safe","terminal","next_adjacency","causal_responsibility"))]
                        item={
                            "protocol":"a232-v1","git_source_head":head,"life_id":life_id,
                            "world_id":common,"arm":arm,"stratum":stratum,
                            "training_sha256":corpus.digest(),"model_version":model.version,
                            "steps":steps,
                            "operator_body_after_each_step":observed_body,
                            "capture_events":sum(e.get("kind")=="perceptual_capture" for e in events),
                            "creature_alerts":sum(e.get("kind")=="stage11_local_threat_alert_proposed" for e in events),
                            "lived_evidence_events":sum(e.get("kind") in ("causal_lived_evidence_admitted","causal_lived_intervention_staged","causal_applied_action_memory_verified") for e in events),"physical_steps":sum(s["status"] in ("applied","dead")
                                for s in steps),"death":any(s["status"]=="dead" for s in steps),
                            "exception":failure,
                            "model_forecasts":len(model_receipts),
                            "model_proposals":len(proposed),
                            "model_crossed":len(crossed),
                            "model_admissions":len(admissions & proposed),
                            "model_applied":len(applied & proposed),
                            "model_complete_chain":bool(proposed & crossed & admissions & applied),
                            "uc_model_charges_accepted":sum(x.get("accepted") is True for x in charges),
                            "uc_model_charges_refused":sum(x.get("accepted") is False for x in charges),
                            "false_epistemic_claims":len(prediction_violations),
                            "journal_valid":life.journal.verify(),
                            "journal_sha256":sha256(life.journal.canonical_bytes()).hexdigest(),
                            "physical_truth_external_only":life.world.ground_truth(),
                        }
                        results.append(item)
                        out.write(json.dumps(item,sort_keys=True,separators=(",",":"))+"\n")
        lookup={(r["world_id"],r["arm"]):r for r in results}
        grouped={}
        for stratum in STRATA:
            arms={a:[r for r in results if r["stratum"]==stratum and r["arm"]==a]
                  for a in ("exposed","control")}
            grouped[stratum]={
                "pairs":8,
                "deaths":{a:sum(r["death"] for r in rows) for a,rows in arms.items()},
                "first_actions":{a:[r["steps"][0]["command"] if r["steps"] else None
                                     for r in rows] for a,rows in arms.items()},
                "creature_alerts":{a:sum(r["creature_alerts"] for r in rows)
                                    for a,rows in arms.items()},
                "model_applied":{a:sum(r["model_applied"] for r in rows)
                                 for a,rows in arms.items()},
                "lived_evidence_events":{a:sum(r["lived_evidence_events"] for r in rows)
                                          for a,rows in arms.items()},
                "followup_capture_pairs":sum(
                    lookup[(f"a232:{stratum}:{i:02d}","exposed")]["capture_events"]>=2
                    and lookup[(f"a232:{stratum}:{i:02d}","control")]["capture_events"]>=2
                    for i in range(8)),
            }
        failures=[r for r in results if r["exception"] or not r["journal_valid"]]
        leaks=sum(r["false_epistemic_claims"] for r in results)
        # Explicit physical and epistemic comparisons; do not reinterpret
        # external truth as an I1 memory, cause judgement or learned hazard.
        summary={
            "protocol":"a232-v1","source_sha":head,
            "training_sha256":corpus.digest(),
            "world_pairs":32,"mortal_lives":len(results),
            "total_physical_steps":sum(r["physical_steps"] for r in results),
            "strata":grouped,
            "exceptions_or_invalid_journals":len(failures),
            "false_epistemic_claims":leaks,
            "cognitive_deployment":"NO-GO",
            "learning_status":"NOT_DEMONSTRATED_UNLESS_VERIFIED_WITH_LIVED_EVIDENCE",
            "replay_independence":"one deterministic cohort repeated under two Python versions",
        }
        (output/"summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
        return summary


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--source-sha",required=True)
    args=parser.parse_args()
    result=experiment(args.output,head=args.source_sha)
    print(json.dumps(result,sort_keys=True))
    if result["mortal_lives"]!=64 or result["exceptions_or_invalid_journals"] or result["false_epistemic_claims"]:
        raise SystemExit(1)


if __name__=="__main__":
    main()
