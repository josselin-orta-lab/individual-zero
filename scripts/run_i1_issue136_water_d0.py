"""Issue #136 D0: fixed prospective 32 mortal I1 lives, no learned-transfer claim.

Protocol frozen at commit ecd2370cf3d785d200c9facca8a0eb7413132557.
This runner may observe external truth only in saved operator-side reports.
"""
from __future__ import annotations
import argparse
from collections import Counter
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from build_i1_fork import generate

PREREG_SHA = "ecd2370cf3d785d200c9facca8a0eb7413132557"
LAYOUTS = ("local", "north", "east", "south2")

def run(output: Path, head: str) -> dict:
    output=output.resolve()
    output.mkdir(parents=True,exist_ok=False)
    with TemporaryDirectory(prefix="i1-136-d0-") as folder:
        generated=Path(folder)/"generated"
        generate(generated)
        sys.path.insert(0,str(generated))
        from i1.interfaces import PrimitiveCommand
        from i1.equipment import EquipmentCorpus,EquipmentCorpusExample,SimulationState,SimulationNeighbor
        from i1.experimental.stage6_visible_delta_shadow import fit_external_lab_shadow
        from i1.modules.stage12_detectors import Stage12DetectionPolicy
        from i1lab.world import WorldBody
        from i1lab.stage11_reference_fixture import build_stage11_reference_runtime
        from i1lab.stage10_reference_fixture import build_stage10_reference_runtime
        from i1lab.i1_active_runtime import ExperimentalI1Stage12Runtime
        from i1lab.journal import HashChainedJournal
        from i1lab.independent_journal_audit import audit_export_bytes
        s11=build_stage11_reference_runtime(enable_geography=True,autonomous_mortal=True)
        s10=build_stage10_reference_runtime(autonomous_mortal=True)
        base=s11.world.config
        origin=base.initial_position
        def observable(world,t):
            cap=world.capture_local(t_monde=t)
            return SimulationState(
                schema_version="simulation-state-v1",x=cap.position.x,y=cap.position.y,
                body=world.telemetry(),inventory=world.inventory(),
                current_water_source=cap.current_water_source,
                current_resources=cap.current_resources,
                adjacent=tuple(SimulationNeighbor(
                    direction=n.direction,x=n.position.x,y=n.position.y,
                    passable=n.passable,water_source=n.water_source,
                    resources=n.resources,creature=n.creature) for n in cap.adjacent),
                known_shelter_here=False,is_night=world.is_night(t))
        training=[]
        for action in ("MOVE_E","COLLECT_B"):
            for i in range(8):
                cfg=replace(base,version=base.version+"-136-training",
                    initial_body=replace(base.initial_body,
                        energy=float(60+i),food=float(28+i),water=float(70+i)))
                resources=((origin,"berry_b",3+i),) if action=="COLLECT_B" else ()
                layout=replace(s11.world._layout,obstacles=frozenset(),
                    water_sources=frozenset(),resources=resources,
                    creatures=frozenset(),danger_zones=frozenset(),lethal_zones=frozenset())
                world=WorldBody(config=cfg,layout=layout)
                before=observable(world,1)
                command=(PrimitiveCommand("se_deplacer",{"direction":"east"})
                         if action=="MOVE_E" else PrimitiveCommand("collecter",{"target":"berry_b"}))
                transition=world.apply(command,t_monde=1)
                if transition.lethal:
                    raise RuntimeError("unexpected training mortality")
                training.append(EquipmentCorpusExample(
                    "i136:"+action+":"+str(i),before,command,observable(world,2),False))
        corpus=EquipmentCorpus("i136-d0-external-only",tuple(training))
        model=fit_external_lab_shadow(corpus=corpus)
        sleep=replace(s10._stage10_config.sleep,
            fatigue_gain=0.0,night_weight=0.0,consolidation_weight=0.0)
        s10cfg=replace(s10._stage10_config,stage9=s11._stage11_config.stage9,sleep=sleep)
        policy=Stage12DetectionPolicy(version="i136-d0-stage12-v1",
            window=12,stagnation_steps=3,stagnation_tolerance=.05,
            loop_repetitions=2,loop_max_period=2,entropy_min_samples=3,
            entropy_warning_fraction=.25,bias_min_outcomes_each=2,
            attribution_bias_threshold=.75)
        records=[]
        raw=output/"lives.jsonl"
        with raw.open("w",encoding="utf-8") as stream:
            for place in LAYOUTS:
                for idx in range(4):
                    for on in ((idx%2)==0,(idx%2)!=0):
                        arm="on" if on else "off"
                        lifeid=f"i1:i136:d0:{place}:{idx:02d}:{arm}"
                        dest=output/lifeid.replace(":","-")
                        dest.mkdir()
                        source={"local":origin,"north":origin.moved("north"),
                                "east":origin.moved("east"),
                                "south2":origin.moved("south").moved("south")}[place]
                        cfg=replace(base,version=base.version+"-136-d0",
                            initial_body=replace(base.initial_body,
                                energy=float(65+idx%2),food=80.0,
                                water=float(20+idx),integrity=100.0))
                        layout=replace(s11.world._layout,
                            water_sources=frozenset({source}),resources=(),
                            obstacles=frozenset(),creatures=frozenset(),
                            danger_zones=frozenset(),lethal_zones=frozenset())
                        layout.validate(cfg)
                        life=ExperimentalI1Stage12Runtime(
                            world_config=cfg,layout=layout,
                            safety_config=s11.stage3.substrate.safety._config,
                            safety_facts=s11._canonical_safety._innate,
                            protected_integrity_threshold=s11.stage3.control._config.protected_integrity_threshold,
                            stage11_config=s11._stage11_config,
                            stage10_config=s10cfg,equipment=s11.equipment,
                            autonomous_mortal=True,wal_path=str(dest/"life.wal"),
                            birth_life_id=lifeid,
                            diagnostic_sample_cost_uc=1,module_occupancy_cost_uc=1,
                            detector_policy=policy,
                            i1_model_enabled=on,i1_model=model if on else None,
                            i1_forecast_cost_uc=2)
                        initial_e=life.equipment.artifact_digest
                        transitions=[]
                        error=None
                        for _ in range(8):
                            before=float(life.world.telemetry()["water"])
                            try:
                                result=life.run_step()
                            except Exception as exc:
                                error={"type":type(exc).__name__,"message":str(exc)[:300]}
                                break
                            after=float(life.world.telemetry()["water"])
                            transitions.append({"status":result.execution_status,
                                "primitive":result.command_primitive,
                                "option":result.option_ref,"source":result.source,
                                "water_before":before,"water_after":after,
                                "physically_drunk":bool(result.execution_status=="applied"
                                    and result.command_primitive=="boire" and after>before)})
                            if result.execution_status!="applied":
                                break
                        events=[dict(item.causal_event) for item in life.journal.entries]
                        payload=life.journal.canonical_bytes()
                        (dest/"canonical.jsonl").write_bytes(payload)
                        audit_error=None
                        try:
                            proof=HashChainedJournal.audit_durable_wal(str((dest/"life.wal").resolve()))
                            if proof["head_hash"]!=life.journal.head_hash or proof["verified_entries"]!=len(events):
                                raise ValueError("WAL head/count mismatch")
                            if not life.journal.verify():
                                raise ValueError("broken in-memory hash chain")
                            audit_export_bytes(payload)
                        except Exception as exc:
                            audit_error=type(exc).__name__+": "+str(exc)
                        forecast=[e for e in events if e.get("kind")=="i1_partial_preaction_forecast"]
                        proposed=[e for e in events if e.get("kind")=="i1_partial_instrumental_option_proposed"]
                        uc=[e["data"] for e in events if e.get("kind")=="compute_charge"
                            and e.get("data",{}).get("operation")=="i1_partial_model_forecast"]
                        water_proposals=[e for e in proposed if (
                            e.get("data",{}).get("command",{}).get("primitive")=="boire"
                            or ":drink:" in e.get("data",{}).get("option_ref",""))]
                        row={
                            "schema":"i1-issue136-d0-life-v1","prereg_sha":PREREG_SHA,
                            "source_sha":head,"life_id":lifeid,"layout":place,
                            "pair_index":idx,"arm":arm,
                            "model_training_scope":"external_lab" if on else "none",
                            "model_corpus_sha":model.corpus_sha256 if on else None,
                            "equipment_birth_sha":initial_e,
                            "equipment_final_sha":life.equipment.artifact_digest,
                            "steps":transitions,"executed_steps":sum(
                                x["status"] in ("applied","dead") for x in transitions),
                            "actual_drinks":sum(x["physically_drunk"] for x in transitions),
                            "birth_water":float(20+idx),
                            "final_water":float(life.world.telemetry()["water"]),
                            "mortal_status":life.stage3.substrate.mortal_status.value,
                            "forecast_count":len(forecast),"model_proposals":len(proposed),
                            "model_water_proposals":len(water_proposals),
                            "uc_model_accepted":sum(x.get("accepted") is True for x in uc),
                            "uc_model_refused":sum(x.get("accepted") is False for x in uc),
                            "goal_followups":sum(e.get("kind")=="stage12_goal_progress_followup" for e in events),
                            "stage6_planning_results":sum(e.get("kind")=="stage6_planning_result" for e in events),
                            "journal_sha256":sha256(payload).hexdigest(),
                            "journal_head":life.journal.head_hash,
                            "journal_entries":len(events),
                            "audit_error":audit_error,"exception":error,
                            "external_truth_scoring_only":True,
                        }
                        records.append(row)
                        (dest/"result.json").write_text(json.dumps(row,indent=2,sort_keys=True)+"\n")
                        stream.write(json.dumps(row,sort_keys=True)+"\n")
        groups={}
        for place in LAYOUTS:
            groups[place]={}
            for arm in ("on","off"):
                rows=[r for r in records if r["layout"]==place and r["arm"]==arm]
                groups[place][arm]={
                    "lives":len(rows),"physical_steps":sum(r["executed_steps"] for r in rows),
                    "drinking_lives":sum(r["actual_drinks"]>0 for r in rows),
                    "drinks":sum(r["actual_drinks"] for r in rows),
                    "deaths":sum(r["mortal_status"]=="dead" for r in rows),
                    "uc_model_accepted":sum(r["uc_model_accepted"] for r in rows),
                    "uc_model_refused":sum(r["uc_model_refused"] for r in rows),
                    "technical_errors":sum(bool(r["exception"] or r["audit_error"]) for r in rows),
                }
        errors=sum(bool(r["exception"] or r["audit_error"]) for r in records)
        violations=sum(bool(r["model_water_proposals"] or
                            r["equipment_birth_sha"]!=r["equipment_final_sha"]) for r in records)
        summary={"protocol":"i1-issue136-d0-v1","prereg_sha":PREREG_SHA,
            "source_sha":head,"cohort":"one deterministic cohort per Python version",
            "pairs":16,"lives":len(records),"physical_steps":sum(r["executed_steps"] for r in records),
            "technical_errors":errors,"contract_violations":violations,
            "by_layout":groups,"first_person_water_learning":"NOT_DEMONSTRATED",
            "heldout_water_transfer":"NOT_TESTED","stage12_science":"PENDING"}
        (output/"summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
        return summary

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--source-sha",required=True)
    args=p.parse_args()
    summary=run(args.output,args.source_sha)
    print(json.dumps(summary,sort_keys=True))
    if summary["lives"]!=32 or summary["technical_errors"] or summary["contract_violations"]:
        raise SystemExit(1)

if __name__=="__main__":
    main()
