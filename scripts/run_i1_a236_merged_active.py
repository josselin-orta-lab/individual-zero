"""A2.36 merged-main I1 multiple-model activation experiment.

New I1 mortal births only; external lab priors are not lived knowledge.
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

PREREG = "324b04b6dd51395fd6ebdbcd1a23f843cf929621"
INPUT_LOCK = PREREG
STRATA = ("BERRY_LOCAL", "WATER_NEW_E_SAFE", "WATER_NEW_E_LETHAL", "WATER_VISIT_N_SAFE", "WATER_VISIT_N_CHANGED_LETHAL", "BERRY_EAST_HIDDEN_LETHAL")
ARMS = ("FULL","NO_RECALL","NO_D2")
LIVES_PER_ARM = 8
MAX_ACTUAL_STEPS = 12


def experiment(output: Path, *, head: str) -> dict[str, object]:
    output=output.resolve()
    output.mkdir(parents=True,exist_ok=False)
    with TemporaryDirectory(prefix="i1-a236-code-") as temp:
        generated=Path(temp)/"generated"
        generate(generated)
        sys.path.insert(0,str(generated))
        from i1.modules.stage12_detectors import Stage12DetectionPolicy
        from i1.equipment import EquipmentCorpus,EquipmentCorpusExample,SimulationNeighbor,SimulationState
        from i1.interfaces import PrimitiveCommand
        from i1.experimental.stage6_visible_delta_shadow import fit_external_lab_shadow
        from i1lab.stage11_reference_fixture import build_stage11_reference_runtime
        from i1lab.stage10_reference_fixture import build_stage10_reference_runtime
        from i1lab.i1_water_runtime import CONSIDER, ACQUIRE
        from i1lab.i1_d2_runtime import I1WaterPrudentRuntime, REVIEW
        from i1lab.world import Position,WorldBody
        from i1lab.injected_scenario import ScenarioEvent
        from i1lab.journal import HashChainedJournal
        from i1lab.independent_journal_audit import audit_export_bytes
        from i1lab.determinism import canonical_causal_bytes, sha256_hex

        s11=build_stage11_reference_runtime(
            enable_geography=True,autonomous_mortal=True)
        s10=build_stage10_reference_runtime(autonomous_mortal=True)
        orig=s11.world.config.initial_position
        # Pure external prebirth research prior. It never enters I1 Memory.
        def visible_lab(world,step):
            cap=world.capture_local(t_monde=step)
            return SimulationState(
                schema_version="simulation-state-v1",
                x=cap.position.x,y=cap.position.y,
                body=world.telemetry(),inventory=world.inventory(),
                current_water_source=cap.current_water_source,
                current_resources=cap.current_resources,
                adjacent=tuple(SimulationNeighbor(
                    direction=n.direction,x=n.position.x,y=n.position.y,
                    passable=n.passable,water_source=n.water_source,
                    resources=n.resources,creature=n.creature) for n in cap.adjacent),
                known_shelter_here=False,is_night=world.is_night(step))
        training=[]
        for action in ("MOVE_E","COLLECT_B"):
            for i in range(8):
                phy=replace(s11.world.config,
                    version=s11.world.config.version+"-a236-train",
                    initial_body=replace(s11.world.config.initial_body,
                        energy=60.0+i,food=28.0+i,water=70.0+i))
                local_resources=((orig,"berry_b",3+i),) if action=="COLLECT_B" else ()
                training_layout=replace(s11.world._layout,
                    obstacles=frozenset(),water_sources=frozenset(),
                    resources=local_resources,danger_zones=frozenset(),
                    lethal_zones=frozenset(),creatures=frozenset())
                w=WorldBody(config=phy,layout=training_layout)
                before=visible_lab(w,1)
                cmd=(PrimitiveCommand("se_deplacer",{"direction":"east"})
                    if action=="MOVE_E" else
                    PrimitiveCommand("collecter",{"target":"berry_b"}))
                delta=w.apply(cmd,t_monde=1)
                after=visible_lab(w,2)
                assert not delta.lethal
                training.append(EquipmentCorpusExample(
                    f"a236:{action}:{i}",before,cmd,after,False))
        corpus=EquipmentCorpus("a236-main-prebirth-external-physical-v1",tuple(training))
        model=fit_external_lab_shadow(corpus=corpus)
        if model.corpus_sha256!=corpus.digest() or dict(model.counts)!={"MOVE_E":8,"COLLECT_B":8}:
            raise RuntimeError("unsealed or incomplete external training prior")

        c11=s11._stage11_config
        c9=c11.stage9;c8=c9.stage8;c7=c8.stage7;c6=c7.stage6;c4=c6.stage4
        water_needs=replace(
            c4.value_needs,version="a236-water95-needs-v1",
            setpoints={**c4.value_needs.setpoints,"water":95.0})
        water_plan=replace(
            c6.planning,version="a236-water95-plan-v1",
            setpoints={**c6.planning.setpoints,"water":95.0})
        revised9=replace(c9,stage8=replace(c8,stage7=replace(
            c7,stage6=replace(c6,stage4=replace(
                c4,value_needs=water_needs),planning=water_plan))))
        revised11=replace(c11,stage9=revised9)
        sleep=replace(s10._stage10_config.sleep,version="a236-dev-zero-consolidation-weight",
            fatigue_gain=0.0,night_weight=0.0,consolidation_weight=0.0)
        revised10=replace(s10._stage10_config,stage9=revised9,sleep=sleep)
        policy=Stage12DetectionPolicy(version="a236-logged-v1",
            window=12,stagnation_steps=3,stagnation_tolerance=.05,
            loop_repetitions=2,loop_max_period=2,entropy_min_samples=3,
            entropy_warning_fraction=.25,bias_min_outcomes_each=2,
            attribution_bias_threshold=.75)
        records=[]
        with (output/"lives.jsonl").open("w",encoding="utf-8") as export:

            for stratum in STRATA:
                berry=stratum.startswith("BERRY")
                revisited=stratum.startswith("WATER_VISIT")
                direction="north" if revisited else "east"
                for idx in range(LIVES_PER_ARM):
                    remote=(orig if (revisited or berry) else Position(12+idx,12))
                    target=remote.moved(direction)
                    for arm in (ARMS if idx%2==0 else tuple(reversed(ARMS))):
                        enabled=True
                        life_id=f"i1:a236:{stratum}:{idx:02d}:{arm}"
                        life_dir=output/life_id.replace(":","-")
                        life_dir.mkdir()
                        config=replace(s11.world.config,
                            version="a236-main-active-world-v1",
                            initial_body=replace(s11.world.config.initial_body,
                                energy=float(65+idx%2),
                                food=(float(10+idx) if berry else 80.0),
                                water=(95.0 if berry else float(1+idx%3)),
                                integrity=100.0))
                        hazardous=stratum in (
                            "WATER_NEW_E_LETHAL","BERRY_EAST_HIDDEN_LETHAL")
                        layout=replace(s11.world._layout,
                            obstacles=frozenset(),creatures=frozenset(),
                            danger_zones=frozenset(),
                            water_sources=(frozenset() if berry else
                                frozenset({orig.moved("north"),target})),
                            resources=(
                                ((orig,"berry_b",16+idx%3),) if stratum=="BERRY_LOCAL"
                                else ((orig.moved("east"),"berry_b",16+idx%3),)
                                if stratum=="BERRY_EAST_HIDDEN_LETHAL" else ()),
                            lethal_zones=frozenset({target}) if hazardous
                                else frozenset())
                        layout.validate(config)
                        events=()
                        if not berry:
                            events=(ScenarioEvent(
                                t_monde=4,sequence=0,operation="set_position",
                                payload={"position":remote.as_dict()}),)
                            if stratum=="WATER_VISIT_N_CHANGED_LETHAL":
                                events+=(ScenarioEvent(
                                    t_monde=4,sequence=1,operation="set_lethal_zone",
                                    payload={"position":target.as_dict(),"active":True}),)
                        life=I1WaterPrudentRuntime(
                            world_config=config,layout=layout,
                            safety_config=s11.stage3.substrate.safety._config,
                            safety_facts=s11._canonical_safety._innate,
                            protected_integrity_threshold=(
                                s11.stage3.control._config.protected_integrity_threshold),
                            stage11_config=replace(
                                revised11,geographic=(None if berry else
                                    revised11.geographic)),
                            stage10_config=revised10,equipment=s11.equipment,
                            autonomous_mortal=True,
                            wal_path=str((life_dir/"life.wal").resolve()),
                            birth_life_id=life_id,detector_policy=policy,
                            diagnostic_sample_cost_uc=1,module_occupancy_cost_uc=1,
                            i1_model_enabled=True,i1_model=model,i1_forecast_cost_uc=2,
                            i1_lived_recall_enabled=(arm!="NO_RECALL"),
                            i1_recall_cost_uc=1,
                            i1_water_probe_enabled=True,
                            i1_water_learning_enabled=True,
                            i1_water_consider_uc=2,i1_water_acquire_uc=2,
                            i1_d2_prudence=(arm!="NO_D2"),i1_d2_review_uc=1,
                            **({"scenario_id":f"a236:{stratum}:{idx}:{arm}",
                                "scenario_version":"a236-main-integrated-scenario-v1",
                                "scenario_events":events} if events else {}),
                        )
                        birth_e_digest=life.equipment.artifact_digest
                        if not (life._i1_enabled and life._i1_water_probe_enabled
                                and life._i1_water_learning_enabled):
                            raise RuntimeError("I1 A2.36 active birth flags missing")
                        if life._i1_lived_recall_enabled!=(arm!="NO_RECALL"):
                            raise RuntimeError("A2.36 recall arm mismatch")
                        if life._d2_prudence!=(arm!="NO_D2"):
                            raise RuntimeError("A2.36 D2 arm mismatch")
                        steps=[]
                        failure=None
                        for _ in range(MAX_ACTUAL_STEPS):
                            start=len(life.journal.entries)
                            before_body=dict(life.world.telemetry())
                            before_inventory=dict(life.world.inventory())
                            water_before=float(before_body["water"])
                            position_before=life.world.position.as_dict()
                            try:
                                outcome=life.run_step()
                            except BaseException as exc:
                                failure={"class":type(exc).__name__,
                                    "detail":str(exc)[:350]}
                                break
                            after_body=dict(life.world.telemetry())
                            after_inventory=dict(life.world.inventory())
                            water_after=float(after_body["water"])
                            position_after=life.world.position.as_dict()
                            new_events=[entry.causal_event for entry in life.journal.entries[start:]]
                            actual_capture=next((
                                e.get("data",{}).get("position")
                                for e in new_events
                                if e.get("kind")=="perceptual_capture"),None)
                            physical_step=int(life.scheduler.t_monde)
                            steps.append({
                                "t_monde":physical_step,
                                "command":outcome.command_primitive,
                                "option_ref":outcome.option_ref,
                                "source":outcome.source,
                                "status":outcome.execution_status,
                                "position_before_open_step":position_before,
                                "authorized_preaction_position":actual_capture,
                                "position_after_action":position_after,
                                "water_before_world_step":water_before,
                                "water_after_world_step":water_after,
                                "integrity_after":after_body["integrity"],
                                "food_after":after_body["food"],
                                "berries_before":before_inventory.get("berry_b",0),
                                "berries_after":after_inventory.get("berry_b",0),
                                "positive_collection":bool(
                                    outcome.execution_status=="applied"
                                    and outcome.command_primitive=="collecter"
                                    and after_inventory.get("berry_b",0)>before_inventory.get("berry_b",0)),
                                "positive_drinking":bool(
                                    outcome.execution_status=="applied"
                                    and outcome.command_primitive=="boire"
                                    and water_after>water_before),
                            })
                            if outcome.execution_status!="applied":
                                break
                        entries=life.journal.entries
                        all_events=[dict(e.causal_event) for e in entries]
                        canonical=life.journal.canonical_bytes()
                        (life_dir/"canonical.jsonl").write_bytes(canonical)
                        audit_error=None
                        try:
                            attestation=HashChainedJournal.audit_durable_wal(
                                str((life_dir/"life.wal").resolve()))
                            if (attestation["head_hash"]!=life.journal.head_hash
                                    or attestation["verified_entries"]!=len(entries)
                                    or not life.journal.verify()):
                                raise ValueError("WAL and living journal diverged")
                            audit_export_bytes(canonical)
                        except Exception as exc:
                            audit_error=type(exc).__name__+": "+str(exc)
                        provenance=[{
                            "event_id":entry.event_id,
                            "world_step":entry.causal_event.get("t_monde"),
                            "data":entry.causal_event.get("data",{})
                        } for entry in entries if entry.causal_event.get("kind")
                            =="i1_water_lived_outcome_admitted"]
                        proposed=[{
                            "event_id":entry.event_id,
                            "world_step":entry.causal_event.get("t_monde"),
                            "data":entry.causal_event.get("data",{})
                        } for entry in entries if entry.causal_event.get("kind")
                            =="i1_water_option_proposed"]
                        admissions={
                            e.get("data",{}).get("option_ref")
                            for e in all_events if e.get("kind")=="command_admitted"}
                        learned_source_before_transfer=any(
                            e["world_step"] is not None
                            and e["world_step"]<4
                            and e["data"].get("admitted") is True
                            for e in provenance)
                        planned_transfer={
                            e["data"]["option_ref"] for e in proposed
                            if e["world_step"]>=4 and
                                e["data"].get("modality")=="lived_transfer"
                                and e["data"].get("command",{}).get("primitive")
                                    =="se_deplacer"}
                        moves=[s for s in steps
                            if s["status"]=="applied"
                            and s["command"]=="se_deplacer"
                            and s["option_ref"] in planned_transfer
                            and s["option_ref"] in admissions
                            and s["t_monde"]>=4
                            and s["authorized_preaction_position"]==remote.as_dict()
                            and s["position_after_action"]==target.as_dict()
                            and learned_source_before_transfer]
                        selected_move=min(
                            (s["t_monde"] for s in moves),default=None)
                        drinks=[s for s in steps if selected_move is not None
                            and s["t_monde"]>selected_move
                            and s["command"]=="boire"
                            and s["status"]=="applied"
                            and s["positive_drinking"]
                            and s["authorized_preaction_position"]==target.as_dict()]
                        successful_transfer=bool(drinks)
                        charges=[e.get("data",{}) for e in all_events
                            if e.get("kind")=="compute_charge"]
                        uc_charged=sum(
                            int(c.get("requested_uc") or 0)
                            for c in charges if c.get("accepted") is True)
                        uc_refused=sum(1 for c in charges
                                       if c.get("accepted") is False)
                        op_uc=Counter()
                        for c in charges:
                            if c.get("accepted") is True:
                                op_uc[str(c.get("operation"))] += int(
                                    c.get("requested_uc") or 0)
                        learner=life.lived_water_model
                        model_receipts=[e for e in all_events if e.get("kind")=="i1_partial_preaction_forecast"]
                        model_proposals=[e for e in all_events if e.get("kind")=="i1_partial_instrumental_option_proposed"]
                        reviews=[e for e in all_events if e.get("kind")=="i1_lived_recall_review"]
                        boosts=[e for e in all_events if e.get("kind")=="stage8_option_evaluation"
                            and e.get("data",{}).get("evidence")==0.45]
                        d2_reviews=[e for e in all_events if e.get("kind")=="i1_d2_movement_commitment_review"]
                        recall_charges=[e for e in charges if e.get("operation")=="i1_lived_recall_review"]
                        d2_charges=[e for e in charges if e.get("operation")==REVIEW]
                        false_certainty=[e for e in model_receipts
                            if any(e.get("data",{}).get("result",{}).get(k) is not None
                            for k in ("safe","terminal","next_adjacency","causal_responsibility"))]
                        hard_violations=[]
                        if learner["enabled"]!=enabled:
                            hard_violations.append("owner_wrong_arm")
                        if model.corpus_sha256!=corpus.digest():
                            hard_violations.append("training_artifact_modified")
                        if arm=="NO_RECALL" and (recall_charges or reviews or boosts):
                            hard_violations.append("recall_disabled_bypassed")
                        if arm=="NO_D2" and (d2_charges or d2_reviews):
                            hard_violations.append("d2_disabled_bypassed")
                        if false_certainty:
                            hard_violations.append("unearned_model_certainty")
                        if boosts and not any(
                            r.get("data",{}).get("source_event_refs") for r in reviews):
                            hard_violations.append("unattributed_recall_boost")
                        if any(
                            r.get("data",{}).get("decision")=="permit_historically_visited"
                            and r.get("data",{}).get("review_uc_paid") is not True
                            for r in d2_reviews):
                            hard_violations.append("d2_permit_without_uc")
                        if not enabled and learner["examples"]:
                            hard_violations.append("disabled_learner_updated")
                        if life.equipment.artifact_digest!=birth_e_digest:
                            hard_violations.append("exact_e_mutated")
                        if any(p["data"].get("safety_certificate") is not None
                               or p["data"].get("distal_causal_responsibility") is not None
                               for p in proposed):
                            hard_violations.append("unearned_certainty")
                        if successful_transfer and not (
                                enabled and learned_source_before_transfer and moves):
                            hard_violations.append("transfer_without_lived_proof")
                        if (audit_error or failure):
                            hard_violations.append("invalid_execution_or_audit")
                        record={
                            "schema":"i1-a236-life-v1",
                            "prereg_sha":PREREG,"input_lock_sha":INPUT_LOCK,
                            "source_sha":head,"life_id":life_id,
                            "stratum":stratum,"pair_index":idx,"arm":arm,
                            "remote_target_operator_only":target.as_dict(),
                            "external_relocation_operator_only":remote.as_dict(),
                            "birth_water":float(1+idx%3),
                            "physics_digest":sha256_hex(canonical_causal_bytes(config.as_dict())),
                            "world_layout_digest":sha256_hex(canonical_causal_bytes(layout.as_dict())),
                            "exact_e_birth_digest":birth_e_digest,
                            "exact_e_final_digest":life.equipment.artifact_digest,
                            "steps":steps,
                            "physical_steps":sum(x["status"] in ("applied","dead") for x in steps),
                            "initial_drinking":any(
                                s["positive_drinking"] and s["t_monde"]<4 for s in steps),
                            "firstperson_water_evidence":provenance,
                            "learner_final_state":learner,
                            "learning_before_transfer":learned_source_before_transfer,
                            "learned_transfer_candidates":len(planned_transfer),
                            "learned_origin_transfers_applied":len(moves),
                            "physical_transfer_drinks":len(drinks),
                            "successful_transfer":successful_transfer,
                            "uc_total_accepted":uc_charged,
                            "uc_refused_ops":uc_refused,
                            "uc_water_consider":op_uc[CONSIDER],
                            "uc_water_acquire":op_uc[ACQUIRE],
                            "mortal_status":life.stage3.substrate.mortal_status.value,
                            "external_scenario_receipts":sum(
                                e.get("kind")=="external_input_applied" for e in all_events),
                            "stage12_goal_followups":sum(
                                e.get("kind")=="stage12_goal_progress_followup" for e in all_events),
                            "journal_sha256":sha256(canonical).hexdigest(),
                            "journal_head":life.journal.head_hash,
                            "journal_entries":len(entries),
                            "hard_violations":hard_violations,
                            "failure":failure,"audit_error":audit_error,
                            "model_cannot_see_hidden_truth":True,
                        }
                        records.append(record)
                        (life_dir/"life-result.json").write_text(
                            json.dumps(record,indent=2,sort_keys=True)+"\n")
                        export.write(json.dumps(record,sort_keys=True)+"\n")
        groups={}
        for stratum in STRATA:
            groups[stratum]={}
            for arm in ("aggressive","prudence","probe_only"):
                rows=[x for x in records if x["stratum"]==stratum and x["arm"]==arm]
                groups[stratum][arm]={
                    "births":len(rows),
                    "physical_steps":sum(x["physical_steps"] for x in rows),
                    "first_drinking_lives":sum(x["initial_drinking"] for x in rows),
                    "firstperson_learning_lives":sum(bool(x["firstperson_water_evidence"])
                                                     for x in rows),
                    "transfer_moved_lives":sum(x["learned_origin_transfers_applied"]>0
                                               for x in rows),
                    "successful_transfer_lives":sum(x["successful_transfer"] for x in rows),
                    "deaths":sum(x["mortal_status"]=="dead" for x in rows),
                    "accepted_uc":sum(x["uc_total_accepted"] for x in rows),
                    "refused_uc_operations":sum(x["uc_refused_ops"] for x in rows),
                    "water_model_uc":sum(
                        x["uc_water_consider"]+x["uc_water_acquire"] for x in rows),
                    "technical_violations":sum(bool(x["hard_violations"]) for x in rows),
                }
        any_hard=sum(bool(r["hard_violations"]) for r in records)
        mechanism=(groups["novel_east_lethal"]["prudence"]["deaths"]==0
            and groups["novel_east_lethal"]["aggressive"]["deaths"]==8
            and groups["revisit_north_safe"]["prudence"]["successful_transfer_lives"]>=6)
        safety_alarm=(groups["revisit_north_changed_lethal"]["prudence"]["deaths"]>0
            or groups["novel_east_lethal"]["prudence"]["deaths"]>0)
        verdict=("HARD_NO_GO" if any_hard else
            "SAFETY_NO_GO" if safety_alarm else
            "MECHANISM_SUPPORTED_LIMITED" if mechanism else "NOT_DEMONSTRATED")
        summary={
            "schema":"i1-a236-summary-v1",
            "source_sha":head,"prereg_sha":PREREG,"input_lock_sha":INPUT_LOCK,
            "true_independent_births":len(records),"matched_triplets":40,
            "physical_steps":sum(r["physical_steps"] for r in records),
            "hard_violations":any_hard,
            "additional_hidden_lethal_on_deaths":safety_alarm,
            "by_stratum":groups,
            "development_600_physical_steps_reached":sum(
                r["physical_steps"] for r in records)>=600,
            "scientific_transfer_verdict":verdict,
            "stage12_scientific_acceptance":"PENDING",
            "i0_modified":False,
            "reproduction":"same frozen deterministic cohort under Python 3.11 and 3.12",
            "limits":"External relocation is NOT self movement or distant autonomous search.",
        }
        (output/"summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
        return summary


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--source-sha",required=True)
    args=parser.parse_args()
    summary=experiment(args.output,head=args.source_sha)
    print(json.dumps(summary,sort_keys=True))
    if summary["true_independent_births"]!=120 or summary["hard_violations"]:
        raise SystemExit(1)

if __name__=="__main__":
    main()
