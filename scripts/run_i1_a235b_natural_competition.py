"""A2.35-B: preregistered paired I1 first-person learning opportunity audit.

Scientific results are external diagnostics, not I1 memories or Stage GO.
Protocol: docs/research/i1-a235b-prereg-2026-10-16.en.md
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

STRATA=("LOCAL","GEO_LOCAL","GEO_FAILURE","HIDDEN_LETHAL")


def experiment(output: Path, *, head: str) -> dict:
    output=output.resolve()
    with TemporaryDirectory(prefix="i1-a235b-code-") as temp:
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
        from i1.modules.geographic_exploration import GeographicExplorationConfig

        stage11=build_stage11_reference_runtime(autonomous_mortal=True)
        geography=GeographicExplorationConfig(version="a235b-geography-v1",novelty_weight=0.7,max_distinct_sites=1024,max_targets_per_cycle=1)
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
                cfg=replace(base,version=base.version+"-a235b-training",
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
                    f"a235b:{action}:{i}",before,command,after,False))
        corpus=EquipmentCorpus("a235b-prebirth-physical-training-v1",tuple(training))
        model=fit_external_lab_shadow(corpus=corpus)
        assert model.corpus_sha256==corpus.digest()

        policy=Stage12DetectionPolicy(version="a235b-stage12-observer-v1",
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
                    common=f"a235b:{stratum}:{index:02d}"
                    cfg=replace(base,version=base.version+"-a235b-heldout-"+stratum,
                        initial_body=replace(base.initial_body,
                            energy=float(70+index%3),food=float(12+index),
                            water=float(76+index%4),integrity=100.0))
                    local=stratum!="HIDDEN_LETHAL"
                    layout=replace(stage11.world._layout,
                        water_sources=frozenset(),
                        creatures=frozenset(),
                        danger_zones=frozenset(),
                        lethal_zones=(frozenset({east}) if stratum=="HIDDEN_LETHAL" else frozenset()),
                        obstacles=frozenset(),
                        resources=(((origin if local else east),"berry_b",16+index%3),))
                    layout.validate(cfg)
                    # Paired arm labels alternate execution order while
                    # maintaining separate worlds and I1 identities.
                    for exposed in ((index%2)==0,(index%2)!=0):
                        enabled=True
                        arm="on" if exposed else "off"
                        life_id="i1:"+common+":"+arm
                        exposed_world=(arm=="on")
                        own_layout=replace(layout,
                            creatures=frozenset(),
                            danger_zones=frozenset(),
                            lethal_zones=(frozenset({east}) if stratum=="HIDDEN_LETHAL" else frozenset()))
                        wal=output/(stratum+"-"+str(index)+"-"+arm+".wal")
                        life=ExperimentalI1Stage12Runtime(
                            world_config=cfg,layout=own_layout,
                            safety_config=stage11.stage3.substrate.safety._config,
                            safety_facts=stage11._canonical_safety._innate,
                            protected_integrity_threshold=stage11.stage3.control._config.protected_integrity_threshold,
                            stage11_config=replace(stage11._stage11_config,geographic=(geography if stratum in ("GEO_LOCAL","GEO_FAILURE") else None)),
                            stage10_config=stage10config,
                            equipment=stage11.equipment,
                            autonomous_mortal=True,wal_path=str(wal),
                            birth_life_id=life_id,
                            diagnostic_sample_cost_uc=1,module_occupancy_cost_uc=1,
                            detector_policy=policy,i1_model_enabled=enabled,
                            i1_model=model,
                            i1_forecast_cost_uc=2,
                            i1_lived_recall_enabled=exposed_world,i1_recall_cost_uc=1,
                            **({
                                "scenario_id":"a235b-forced-collect-"+str(index)+"-"+arm,
                                "scenario_version":"a235b-forced-v1",
                                "scenario_events":(
                                    __import__("i1lab.injected_scenario",fromlist=["ScenarioEvent"]).ScenarioEvent(
                                        t_monde=1,sequence=0,
                                        operation="set_action_failure_schedule",
                                        payload={"primitive":"collecter","schedule":[True]},
                                        phase="before_step",
                                    ),
                                ),
                            } if stratum=="GEO_FAILURE" else {}),
                        )
                        captures=[]
                        original_capture=life._on_open_step_capture
                        def record_capture(cap):
                            captures.append({"step":cap.t_monde,
                              "position":[cap.x,cap.y],"body":dict(cap.body),
                              "inventory":dict(cap.inventory),
                              "adjacent":[{"direction":a.direction,"creature":a.creature,
                                "passable":a.passable,"resources":list(a.resources)}
                                for a in cap.adjacent]})
                            return original_capture(cap)
                        life._on_open_step_capture=record_capture
                        steps=[]
                        failure=None
                        observed_body=[]
                        for _ in range(12):
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
                            "protocol":"a235b-v1","git_source_head":head,"life_id":life_id,
                            "world_id":common,"arm":arm,"stratum":stratum,
                            "training_sha256":corpus.digest(),"model_version":model.version,
                            "steps":steps,
                            "review":[e["data"] for e in events if e.get("kind")=="i1_lived_recall_review"],
                            "review_charges":[e["data"] for e in events if e.get("kind")=="compute_charge" and e.get("data",{}).get("operation")=="i1_lived_recall_review"],
                            "competition_traces":[e["data"].get("traces",[]) for e in events if e.get("kind")=="competition_cycle"],
                            "boost_events":[e["data"] for e in events if e.get("kind")=="stage8_option_evaluation" and e.get("data",{}).get("evidence")==0.45],
                            "recalls":[e["data"] for e in events if e.get("kind")=="memory_recall_proposed"],
                            "evaluations":[e["data"] for e in events if e.get("kind")=="stage8_option_evaluation"],
                            "st_publications":[e["data"] for e in events if e.get("kind")=="s_t_published"],
                            "autobiographical_commits":[e for e in events if e.get("kind")=="auto_segment_commit"],
                            "firstperson_captures":captures,
                            "closed_memory_episodes":[ep.as_dict() for ep in life.memory.episodes],
                            "reflex_events":sum(e.get("kind")=="reflex_proposed" for e in events),
                            "memory_access_events":sum(e.get("kind")=="memory_autobiographical_access" for e in events),
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
        pairs={}
        for stratum in STRATA:
            details=[]
            for k in range(8):
                on=lookup[(f"a235b:{stratum}:{k:02d}","on")]
                off=lookup[(f"a235b:{stratum}:{k:02d}","off")]
                def contests(r):
                    sig={e["option_ref"]:e.get("learning_signature","") for e in r["evaluations"] if e["status"]=="evaluated"}
                    for trace in r["competition_traces"]:
                        ids={t["option_ref"] for t in trace if t.get("evidence") is not None}
                        if any(sig.get(x,"").startswith("i1_partial:collecter") for x in ids) and any(sig.get(x,"").startswith("geographic_") for x in ids):
                            return True
                    return False
                steps_on=[x["command"] for x in on["steps"]]
                steps_off=[x["command"] for x in off["steps"]]
                details.append({"case":k,"both_natural_contest":contests(on) and contests(off),
                    "on_boosted":bool(on["boost_events"]),"on_actions":steps_on,"off_actions":steps_off,
                    "first_action_difference":next((q+1 for q,(a,b) in enumerate(zip(steps_on,steps_off)) if a!=b),None),
                    "on_review_source_receipts":sum(bool(x.get("source_event_refs")) for x in on["review"]),
                    "off_review_charges":len(off["review_charges"])})
            pairs[stratum]=details
        result={"protocol":"a235b-v1","source_sha":head,
            "training_sha256":corpus.digest(),"world_pairs":32,"mortal_lives":len(results),
            "physical_steps":sum(r["physical_steps"] for r in results),
            "deaths":{s:{arm:sum(r["death"] for r in results if r["stratum"]==s and r["arm"]==arm) for arm in ("on","off")} for s in STRATA},
            "natural_competition_pairs":{s:sum(x["both_natural_contest"] for x in p) for s,p in pairs.items()},
            "any_action_difference_pairs":{s:sum(x["first_action_difference"] is not None for x in p) for s,p in pairs.items()},
            "boosted_on_lives":sum(bool(r["boost_events"]) for r in results if r["arm"]=="on"),
            "off_review_charges":sum(len(r["review_charges"]) for r in results if r["arm"]=="off"),
            "review_uc_accepted":sum(sum(x.get("accepted") is True for x in r["review_charges"]) for r in results),
            "review_uc_refused":sum(sum(x.get("accepted") is False for x in r["review_charges"]) for r in results),
            "exceptions_or_invalid_journals":sum(bool(r["exception"]) or not r["journal_valid"] for r in results),
            "false_epistemic_claims":sum(r["false_epistemic_claims"] for r in results),
            "pairs":pairs,"cognitive_deployment":"NO-GO","behavioral_efficacy":"UNDEMONSTRATED"}
        (output/"summary.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
        return result


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
