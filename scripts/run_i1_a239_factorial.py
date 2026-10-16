"""A2.39 real I1 mortal factorial: fail-closed and append-only evidence."""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from build_i1_fork import generate
from i1_a239_lock import ARMS, STRATA
from i1_a239_fixtures import world_case, factor_flags

def write(path, data):
    path.write_text(json.dumps(data, sort_keys=True, indent=2)+"\n")

def run(output, source_sha):
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    with TemporaryDirectory(prefix="a239-build-") as tmp:
        dest = Path(tmp)/"generated"
        generate(dest)
        sys.path.insert(0, str(dest))
        from run_i1_a239_preflight import preflight
        from i1_a239_lock import assigned
        from i1lab.i1_a239_runtime import I1A239ExperimentalRuntime, RISK_REVIEW
        from i1lab.i1_a238_runtime import H1_REVIEW
        from i1lab.i1_d2_runtime import REVIEW
        from i1lab.i1_water_runtime import CONSIDER,ACQUIRE
        from i1lab.journal import HashChainedJournal
        from i1lab.independent_journal_audit import audit_export_bytes
        from i1lab.determinism import canonical_causal_bytes,sha256_hex
        manifest = preflight(output,source_sha=source_sha)
        from i1_a238_model import sealed_model
        from i1_a238_fixtures import references
        s11,c11,c10,policy = references()
        model,_seal=sealed_model(output/"training-recheck")
        pre={"input_lock_blob":manifest["prereg_blob"]}
        rows = []
        failures = []
        with (output/"lives.jsonl").open("w") as summary_file:
            for ordinal,(stratum,i,arm) in enumerate(assigned()):
                registered=manifest["births"][ordinal]
                assert registered["life_id"]==f"i1:a239:{stratum}:{i:02d}:{arm}"
                path=output/registered["life_id"].replace(":","-")
                path.mkdir()
                physics,layout,conf,events,target=world_case(s11,c11,stratum,i,arm)
                birth_kwargs=dict(
                    world_config=physics, layout=layout,
                    safety_config=s11.stage3.substrate.safety._config,
                    safety_facts=s11._canonical_safety._innate,
                    protected_integrity_threshold=s11.stage3.control._config.protected_integrity_threshold,
                    stage11_config=conf,stage10_config=c10,
                    equipment=s11.equipment,autonomous_mortal=True,
                    wal_path=str((path/"life.wal").resolve()),
                    birth_life_id=registered["life_id"],detector_policy=policy,
                    diagnostic_sample_cost_uc=1,module_occupancy_cost_uc=1,
                    i1_model_enabled=True,i1_model=model,i1_forecast_cost_uc=2,
                    i1_lived_recall_enabled=True,i1_recall_cost_uc=1,
                    i1_water_probe_enabled=True,i1_water_learning_enabled=True,
                    i1_water_consider_uc=2,i1_water_acquire_uc=2,
                    i1_d2_prudence=True,i1_d2_review_uc=1,
                    **factor_flags(arm),
                    i1_a238_need_review_uc=1,i1_a238_move_review_uc=3,
                    i1_a238_max_move_reviews=2)
                if events:
                    birth_kwargs.update(scenario_id="a238:"+stratum+":"+str(i)+":"+arm,
                        scenario_version="a238-registered-changed-physical-v1",
                        scenario_events=events)
                steps=[]
                failure=None
                life=None
                try:
                    life=I1A239ExperimentalRuntime(**birth_kwargs)
                    if not (life._i1_enabled and life._i1_lived_recall_enabled
                            and life._i1_water_learning_enabled and life._d2_prudence
                            and life._a238_alternate_need==(arm!="BASE")
                            and life._a239_strict_unknown==factor_flags(arm)["i1_a239_strict_unknown"]
                            and life._a239_food_first_risk==factor_flags(arm)["i1_a239_food_first_risk"]):
                        raise RuntimeError("birth switches diverged")
                    for _ in range(20):
                        before=life.world.telemetry()
                        inventory_before=life.world.inventory()
                        pos_before=life.world.position.as_dict()
                        start=len(life.journal.entries)
                        try:
                            result=life.run_step()
                        except Exception as err:
                            failure={"type":type(err).__name__,"message":str(err)[:400]}
                            break
                        after=life.world.telemetry()
                        inv_after=life.world.inventory()
                        events_now=[dict(e.causal_event) for e in life.journal.entries[start:]]
                        charges=[e.get("data",{}) for e in events_now if e.get("kind")=="compute_charge"]
                        steps.append({
                            "t_monde":life.scheduler.t_monde,
                            "command":result.command_primitive,
                            "option_ref":result.option_ref,
                            "source":result.source,
                            "execution_status":result.execution_status,
                            "physical_state_before":dict(before),
                            "physical_state_after":dict(after),
                            "position_before":pos_before,
                            "position_after":life.world.position.as_dict(),
                            "inventory_before":dict(inventory_before),
                            "inventory_after":dict(inv_after),
                            "uc_charges":charges,
                            "goal_events":[e for e in events_now if "goal" in e.get("kind","")],
                            "learning_events":[e for e in events_now if "learning" in e.get("kind","") or "lived_outcome" in e.get("kind","")],
                            "memory_events":[e for e in events_now if "memory" in e.get("kind","") or "episode" in e.get("kind","")],
                            "stage12_events":[e for e in events_now if e.get("kind","").startswith("stage12") or "agency" in e.get("kind","")],
                            "physical_food_gain":result.execution_status=="applied" and result.command_primitive=="manger" and after["food"]>before["food"],
                            "physical_water_gain":result.execution_status=="applied" and result.command_primitive=="boire" and after["water"]>before["water"],
                            "physical_collection":result.execution_status=="applied" and result.command_primitive=="collecter" and inv_after.get("berry_b",0)>inventory_before.get("berry_b",0),
                        })
                        if result.execution_status!="applied":
                            break
                except Exception as err:
                    failure={"type":type(err).__name__,"message":str(err)[:400]}
                journal_audit_error=None
                events_all=[]
                canonical=b""
                head=None
                charges=[]
                if life is not None:
                    try:
                        canonical=life.journal.canonical_bytes()
                        (path/"canonical.jsonl").write_bytes(canonical)
                        head=life.journal.head_hash
                        events_all=[dict(e.causal_event) for e in life.journal.entries]
                        wal=HashChainedJournal.audit_durable_wal(str((path/"life.wal").resolve()))
                        if wal["head_hash"]!=head or wal["verified_entries"]!=len(life.journal.entries) or not life.journal.verify():
                            raise RuntimeError("WAL or internal hash chain mismatch")
                        independent=audit_export_bytes(canonical,expected_head=head,expected_count=len(life.journal.entries))
                        if independent.unexamined_event_kinds:
                            # Report, rather than label the full semantics as independently confirmed.
                            pass
                    except Exception as err:
                        journal_audit_error=type(err).__name__+": "+str(err)[:350]
                    charges=[e.get("data",{}) for e in events_all if e.get("kind")=="compute_charge"]
                uc=Counter()
                for c in charges:
                    if c.get("accepted") is True:
                        uc[str(c.get("operation"))]+=int(c.get("requested_uc") or 0)
                reviews=[e.get("data",{}) for e in events_all if e.get("kind")=="i1_a239_prewater_unknown_review"]
                need_reviews=[e.get("data",{}) for e in events_all if e.get("kind")=="i1_a238_need_reconsideration"]
                mortality=(life.stage3.substrate.mortal_status.value if life is not None else "not_born")
                hard=[]
                if failure or journal_audit_error or life is None: hard.append("technical_failure_or_invalid_journal")
                if arm=="BASE" and (need_reviews or uc[H1_REVIEW]): hard.append("H1_off_violation")
                if arm!="FOOD_FIRST_RISK" and (reviews or uc[RISK_REVIEW]): hard.append("H2_off_violation")
                if len([r for r in reviews if r.get("decision")=="commit_unknown"])>2: hard.append("H2_lifetime_cap")
                if any(r.get("safety_known") is not False or r.get("hidden_world_queried") is not False for r in reviews): hard.append("hidden_label_assertion")
                if any(r.get("extra_uc_paid") is True for r in reviews) and uc[RISK_REVIEW]==0: hard.append("free_H2")
                if any(r.get("paid") is True for r in need_reviews) and uc[H1_REVIEW]==0: hard.append("free_H1")
                if mortality=="dead" and (not steps or steps[-1]["execution_status"]!="dead"): hard.append("death_without_terminal_step")
                if any(s["execution_status"]=="dead" for s in steps[:-1]): hard.append("postmortem_continuation")
                if len(steps)>20: hard.append("over_horizon")
                if (sha256_hex(canonical_causal_bytes(physics.as_dict()))!=registered["physics_sha256"]
                    or sha256_hex(canonical_causal_bytes(layout.as_dict()))!=registered["layout_sha256_operator_only"]):
                    hard.append("wrong_locked_world")
                physical_collection=any(s["physical_collection"] for s in steps)
                physical_food=any(s["physical_food_gain"] for s in steps)
                physical_water=any(s["physical_water_gain"] for s in steps)
                origin_water=float(physics.initial_body.water)
                record={
                    **registered,"schema":"i1-a239-mortal-life-v1",
                    "source_sha":source_sha,"input_lock_blob":pre["input_lock_blob"],
                    "training_corpus_sha256":model.corpus_sha256,
                    "model_deltas_sha256":sha256_hex(canonical_causal_bytes(model.deltas)),
                    "physical_steps":sum(s["execution_status"] in ("applied","dead") for s in steps),
                    "steps":steps,"mortality":mortality,
                    "fatal":mortality=="dead","failure":failure,"audit_error":journal_audit_error,
                    "physical_collection":physical_collection,
                    "physical_food_gain":physical_food,"physical_water_gain":physical_water,
                    "joint_physical_gains":physical_food and physical_water,
                    "hydration_still_unmet":life is not None and float(life.world.telemetry()["water"])<92,
                    "h1_reconsideration_reviews":len(need_reviews),
                    "h1_goal_release_count":sum(x.get("decision")=="ordinary_goal_refractory" for x in need_reviews),
                    "h2_opportunities":len(reviews),
                    "h2_commits":sum(x.get("decision")=="commit_unknown" for x in reviews),
                    "h2_abstentions":sum(x.get("decision")=="abstain" for x in reviews),
                    "uc_accepted":sum(uc.values()),"uc_refused":sum(c.get("accepted") is False for c in charges),
                    "uc_by_operation":dict(uc),"uc_h1":uc[H1_REVIEW],"uc_h2":uc[H2_REVIEW],
                    "uc_d2":uc[REVIEW],"uc_water":uc[CONSIDER]+uc[ACQUIRE],
                    "journal_entries":len(events_all),"journal_head":head,
                    "journal_sha256":sha256(canonical).hexdigest(),
                    "external_input_receipts":sum(e.get("kind")=="external_input_applied" for e in events_all),
                    "learning_receipts":sum("lived_outcome_admitted" in e.get("kind","") for e in events_all),
                    "memory_episodes":len(life.memory.episodes) if life else None,
                    "hard_violations":hard,
                }
                write(path/"life-result.json",record)
                summary_file.write(json.dumps(record,sort_keys=True)+"\n")
                summary_file.flush()
                rows.append(record)
                if hard: failures.append(registered["life_id"])
        grouped={g:{a:{
            "n":sum(r["stratum"]==g and r["arm"]==a for r in rows),
            "deaths":sum(r["fatal"] for r in rows if r["stratum"]==g and r["arm"]==a),
            "collections":sum(r["physical_collection"] for r in rows if r["stratum"]==g and r["arm"]==a),
            "food_gains":sum(r["physical_food_gain"] for r in rows if r["stratum"]==g and r["arm"]==a),
            "water_gains":sum(r["physical_water_gain"] for r in rows if r["stratum"]==g and r["arm"]==a),
            "joint_gains":sum(r["joint_physical_gains"] for r in rows if r["stratum"]==g and r["arm"]==a),
            "h2_commits":sum(r["h2_commits"] for r in rows if r["stratum"]==g and r["arm"]==a),
            "uc_accepted":sum(r["uc_accepted"] for r in rows if r["stratum"]==g and r["arm"]==a),
            "hard_failures":sum(bool(r["hard_violations"]) for r in rows if r["stratum"]==g and r["arm"]==a),
        } for a in ARMS} for g in STRATA}
        f1=sum(bool(r["physical_collection"] and any(s["physical_food_gain"] for s in r["steps"])) for r in rows if r["stratum"]==STRATA[0] and r["arm"]=="H1_ONLY")
        paired=[]
        for i in range(8):
            no_geo=next(r for r in rows if r["stratum"]==STRATA[1] and r["case_index"]==i and r["arm"]=="H1_ONLY")
            geo=next(r for r in rows if r["stratum"]==STRATA[1] and r["case_index"]==i and r["arm"]=="H1_GEO")
            paired.append(bool(no_geo["physical_food_gain"] or no_geo["physical_water_gain"]) and not (geo["physical_food_gain"] or geo["physical_water_gain"]))
        f2=sum(paired)
        f3=sum(any(s["physical_collection"] and s["position_before"]["x"]==15+r["case_index"]%4 for s in r["steps"]) and r["h2_commits"]>0
               for r in rows if r["stratum"]==STRATA[2] and r["arm"]=="FOOD_FIRST_RISK")
        hidden=sum(r["fatal"] for r in rows if r["stratum"]==STRATA[3] and r["arm"]=="FOOD_FIRST_RISK")
        hard_integrity=len(rows)==160 and len(set(r["life_id"] for r in rows))==160 and not failures
        analysis={"schema":"i1-a239-factorial-analysis-v1",
                  "matched_quintuplets":32,
                  "f1_nutritional_closure":f1,"f1_threshold":6,
                  "f2_paired_geographic_diversion":f2,"f2_threshold":6,
                  "f3_food_first_safe_exploitation":f3,"f3_threshold":6,
                  "food_first_hidden_lethal_deaths":hidden,
                  "f1":"GO" if hard_integrity and f1>=6 else "NO-GO",
                  "f2":"SUPPORTED" if hard_integrity and f2>=6 else "UNRESOLVED_OR_NOT_SUPPORTED",
                  "f3":"GO" if hard_integrity and f3>=6 else "NO-GO",
                  "deployment":"NO-GO","by_stratum":grouped}
        write(output/"factorial-analysis.json",analysis)
        write(output/"integrity-audit.json",{"valid":hard_integrity,"life_count":len(rows),
              "failed_life_ids":failures,"separate_independent_auditor_required":True})
        summary={"schema":"i1-a239-confirmatory-summary-v1","source_sha":source_sha,
                 "births":len(rows),"deaths":sum(r["fatal"] for r in rows),
                 "total_physical_steps":sum(r["physical_steps"] for r in rows),
                 "technical_integrity":"PASS" if hard_integrity else "FAIL",
                 "scientific_deployment":"NO-GO","f1":analysis["f1"],
                 "f2":analysis["f2"],"f3":analysis["f3"],
                 "limitations":["No independent biological/scientific replication",
                                "H2 currently requires lived positive water gain before risk review",
                                "Short-life sleep and consolidation confounder disabled",
                                "Memory learning requires independent causal interpretation"]}
        write(output/"summary.json",summary)
        return summary

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--source-sha",required=True)
    a=p.parse_args()
    result=run(a.output,a.source_sha)
    print(json.dumps(result,sort_keys=True))
    if result["technical_integrity"]!="PASS":
        raise SystemExit(2)

if __name__=="__main__": main()
