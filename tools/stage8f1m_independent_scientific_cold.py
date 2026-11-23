"""F1M independent 32-root science cold audit, Python 3.12 stdlib only.

NO imports of i3 modules, the F1M producer, or DEV_M native producer.
Reconstruct all 32 paid origins, 32 x T5 variants/sham, and 128 x 2
fully paid T6..T60 trajectories from SHA-verified original gzip receipts.
Scientific M, A and secondary B verdicts are always separate.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
import json

from tools import stage8f1c_independent_postaction_audit as I
from tools import stage8f1k_independent_policy_value_cold_audit as K
from tools import stage8f1l_independent_paid_content_cold_audit as L
from tools import stage8f1m_independent_dev_cold as D
from tools import stage8f1m_prereg_static_guard as Frozen

CONTENT=("recent","stale")
MODES=("carry","zero")
BODY_LABELS=("energy","food","water","integrity","vigilance")


def check(ok,message):
    if not ok:
        raise AssertionError("F1M ENGINE_FREE SCIENCE COLD: "+message)


def science_grid():
    Frozen.check_files()
    L.source_gate()   # F1L original reference still authentic; NO native rerun.
    return json.loads(Frozen.GRID.read_bytes())


def origin_world(grid,origin):
    w=K.origin_world(grid,origin)
    w["world_spec"]["name"]=(
        "F1M_HELDOUT_ORIGIN_"+origin["id"]+"_"+origin["ecology"])
    return w


def _funded(step):
    if step["decision_info"].get("funding")!="FUNDED":
        return False
    bills=step["native_motor"]["cognitive_accounting"]
    requested=step["requested_native_cost"]
    for coin in ("energy","vigilance"):
        r=bills[coin]
        if (abs(r["requested"]-requested[coin])>1e-9
                or abs(r["paid"]-requested[coin])>1e-9
                or abs(r["unpaid"])>1e-9):
            return False
    return True


def _followup(native,world,mind,arm):
    check(native["policy"]=="F1M_HELDOUT_"+arm,
          "science continuation mistaken for DEV_M or another arm")
    current,individual=deepcopy(world),deepcopy(mind)
    total=0
    for tick,step in enumerate(native["steps"],6):
        check(step["t"]==tick and tick<=60,"reordered or missing T6..T60 step")
        current,individual,rounds=L.verify_step(
            step,current,individual,arm="full",horizon=60)
        total+=rounds
    check(native["last_mind"]==individual,"wrong learned terminal mind")
    K.world_eq(native["last_world"],current,"F1M real T60 world")
    check(native["metrics"]==K.metrics(
        native["steps"],current,native["metrics"]["native_error"],60),
        "forged lived ticks, five body states or learning")
    check(current["t"]==60 or current["dead"] or
          native["metrics"]["native_error"] is not None,
          "truncated or suppressed native T60")
    return len(native["steps"]),total


def _body(x,y):
    return D._body(x,y)


def _t5_equal(x,y):
    return D._t5_equal(x,y) and _funded(x) and _funded(y)


def _t6_equal(x,y):
    return D._t6_equal(x,y) and _funded(x) and _funded(y)


def _semantic_t5(step):
    return D._strip_sham(step)


def cold_root(grid,metadata,parts):
    """A single original M root, checked without instantiating Mind/World."""
    origin=metadata["origin"]
    check(origin in grid["origins"],"not a literal preregistered root")
    identity=origin["id"]
    check(set(parts)=={
       "source","recent_t5","stale_t5","recent_sham_t5",
       "recent_carry","recent_zero","stale_carry","stale_zero",
       "recent_carry_sham","recent_zero_sham",
       "stale_carry_sham","stale_zero_sham"}, "case part was filtered")
    src=parts["source"]
    world=origin_world(grid,origin)
    K.world_eq(src["genesis"]["world"],world,"native birth")
    mind=src["genesis"]["mind"]
    state=K.private(mind,"F1JFixedRoundMind")
    check(K.effects(mind)=={} and
          state["buffer"]=={"__deque__":[],"maxlen":None} and
          all(all(v==0 for v in row) for row in state["values"]),
          "synthetic personal memory / TD at birth")
    t1=None
    steps_reconstructed=rounds_reconstructed=0
    check(len(src["source_steps"])<=4,"source lifetime includes extra ticks")
    for tick,step in enumerate(src["source_steps"],1):
        check(step["t"]==tick,"non-native T1..T4 tick")
        world,mind,used=L.verify_step(step,world,mind,arm="full",horizon=4)
        steps_reconstructed+=1;rounds_reconstructed+=used
        if tick==1:
            t1=K.effects(step["after_paid_learning_mind"])
    K.world_eq(src["tick4_world"],world,"source T4 physiological state")
    check(src["tick4_mind"]==mind,"source T4 mind changed")
    anchor=([{"key":list(k),"stat":deepcopy(v)}
         for k,v in sorted(t1.items(),key=lambda item:repr(item[0]))]
         if t1 is not None else [])
    check(src["paid_t1_mean_anchor"]==anchor,
          "T1 means are not those paid by same individual")
    valid=(len(src["source_steps"])==4 and world["t"]==4
           and not world["dead"] and t1 is not None and bool(t1)
           and src["source_error"] is None and
           all(s["postaction"]["status"]=="PAID_LEARNED"
               for s in src["source_steps"]))
    check(src["source_valid"] is bool(valid) and
          src["source_receipt_sha256"]==I.h(
          {k:v for k,v in src.items() if k!="source_receipt_sha256"}),
          "source payment/custody statement wrong")

    row={"origin":origin,"source":src,
         "content_t5":{},"arms":{},"shams":{},"sham_arms":{},
         "comparison":{}}
    detail={"root":identity,"ecology":origin["ecology"],"source_valid":valid,
            "t5_sham_neutral":False,"all_native_continuations":False,
            "t5_equal_paid":False,"body_deltas":[]}
    if not valid:
        check(metadata["source_valid"] is False and
              metadata["comparison"]=={},
              "metadata omitted a source failure")
        for part in parts:
            if part=="source":
                continue
            expected={"status":"NOT_EXECUTED_UNFUNDED_OR_INCOMPLETE_SOURCE",
                      "source_sha256":src["source_receipt_sha256"],
                      "no_fabricated_native":True}
            check(parts[part]==expected,
                  "fabricated science trajectory for invalid source")
        check(metadata["case_sha256"]==I.h(row),
              "source-only case hash changed")
        return detail,steps_reconstructed,rounds_reconstructed

    check(metadata["source_valid"] is True,"source validity mismatch")
    t5={}
    for content in CONTENT:
        w,m=deepcopy(world),deepcopy(mind)
        step=parts[content+"_t5"]
        mode="full" if content=="recent" else "stale_owned_t1_means"
        w,m,r=L.verify_step(step,w,m,arm=mode,t1=t1,horizon=5)
        steps_reconstructed+=1;rounds_reconstructed+=r
        t5[content]=(w,m)
        row["content_t5"][content]=step
    w,m=deepcopy(world),deepcopy(mind)
    sham5=parts["recent_sham_t5"]
    w,m,r=L.verify_step(sham5,w,m,arm="full_sham",horizon=5)
    steps_reconstructed+=1;rounds_reconstructed+=r
    neutral=(w==t5["recent"][0] and m==t5["recent"][1] and
             _semantic_t5(sham5)==_semantic_t5(parts["recent_t5"]))
    row["shams"]["t5_recent_full_sham"]=sham5
    row["comparison"]["t5_full_sham_neutral"]=neutral
    detail["t5_sham_neutral"]=neutral
    equal_t5=_t5_equal(parts["recent_t5"],parts["stale_t5"])
    row["comparison"]["equal_t5_real_decision_cost"]=equal_t5
    detail["t5_equal_paid"]=equal_t5
    shim=[]
    valid_arms=[]
    for content in CONTENT:
        before_world,before_mind=t5[content]
        for mode in MODES:
            arm=content+"/"+mode
            kind=content+"_"+mode
            native=parts[kind]
            check(set(native)=={"fork","followup"},
                  "missing or additional mediator intervention")
            after=D._cold_fork(before_mind,native["fork"],mode)
            steps,rounds=_followup(native["followup"],
                                   before_world,after,arm)
            steps_reconstructed+=steps;rounds_reconstructed+=rounds
            row["arms"][arm]=native
            sham=parts[kind+"_sham"]
            ss,sr=_followup(sham,before_world,after,arm)
            steps_reconstructed+=ss;rounds_reconstructed+=sr
            row["sham_arms"][arm]=sham
            eq=(native["followup"]["steps"]==sham["steps"]
                and native["followup"]["last_world"]==sham["last_world"]
                and native["followup"]["last_mind"]==sham["last_mind"]
                and native["followup"]["metrics"]==sham["metrics"])
            row["shams"][arm+"_neutral"]=eq
            shim.append(eq)
            valid_arms.append(
                native["followup"]["metrics"]["native_error"] is None
                and len(native["followup"]["steps"])>0
                and ss>0 and steps>0)
        carry=row["arms"][content+"/carry"]["followup"]
        zero=row["arms"][content+"/zero"]["followup"]
        x,y=carry["steps"],zero["steps"]
        if not x or not y:
            row["comparison"][content]={"error":"MISSING_NATIVE_T6"}
            detail[content]={"cost_equal":False,"motor_changed":False,
                "winner_changed":False,"body":None,"delta_lived_ticks":None}
            continue
        a,b=x[0],y[0]
        wc=a["decision_info"]["observer"]["competition_witness"]["winner_before_control"]
        wz=b["decision_info"]["observer"]["competition_witness"]["winner_before_control"]
        effect={
            "equal_t6_real_decision_cost":_t6_equal(a,b),
            "winner_changed":wc!=wz,
            "motor_changed":(a["action"],a["param"])!=(b["action"],b["param"]),
            "carry_t6_motor":[a["action"],a["param"]],
            "zero_t6_motor":[b["action"],b["param"]],
            "carry_t6_winner":wc,"zero_t6_winner":wz,
            "carry_t6_work":a["cognitive_work"],
            "zero_t6_work":b["cognitive_work"],
            "carry_t6_billing":a["requested_native_cost"],
            "zero_t6_billing":b["requested_native_cost"],
            "t6_body_delta_after_paid_learning":[u-v for u,v in zip(
                  a["postaction"]["body_after_any_learning"],
                  b["postaction"]["body_after_any_learning"])],
            "t6_body_delta_after_motor":[u-v for u,v in zip(
                  a["native_motor"]["body"],b["native_motor"]["body"])],
            "body":_body(carry,zero)}
        # The DEV prototype's T6 cost comparison permits unpaid twins;
        # deliberately use the STRICT science cost only as a gate, while
        # validating producer's raw equal-field witness separately.
        raw_equal=D._t6_equal(a,b)
        native_effect=deepcopy(effect)
        native_effect["equal_t6_real_decision_cost"]=raw_equal
        check(metadata["comparison"].get(content)==native_effect,
              "producer's case-level T6 choice/physical summary forged")
        row["comparison"][content]=native_effect
        detail[content]={
            "cost_equal":effect["equal_t6_real_decision_cost"],
            "winner_changed":effect["winner_changed"],
            "motor_changed":effect["motor_changed"],
            "actual_motor_carry":effect["carry_t6_motor"],
            "actual_motor_zero":effect["zero_t6_motor"],
            "delta_lived_ticks":effect["body"]["delta_lived_ticks_t6_t60"],
            "body":effect["body"]}
        detail["body_deltas"].append(effect["body"])
    check(metadata["comparison"]==row["comparison"],
          "producer comparison metadata differs from native receipts")
    check(metadata["sham_t5_neutral"]==neutral,
          "T5 neutral sham not preserved")
    check(metadata["case_sha256"]==I.h(row),
          "F1M case canonical SHA from all 12 native receipts differs")
    detail["all_native_continuations"]=all(valid_arms)
    detail["all_shams_neutral"]=neutral and all(shim)
    return detail,steps_reconstructed,rounds_reconstructed


def classify(rows):
    """Predeclared M (motor) / A (survival) / B (body) without reclassifying."""
    if len(rows)!=32 or [r["root"] for r in rows]!=[
            "M%02d" % i for i in range(1,33)]:
        return {"status":"INCONCLUSIVE_PROVENANCE_OR_NATIVE_CUSTODY",
                "reason":"incomplete independent 32-root science audit"}
    if any(not r["source_valid"] or not r.get("all_shams_neutral",False)
           for r in rows):
        return {"status":"INCONCLUSIVE_PAID_SOURCE_OR_SHAM",
                "reason":"self-paid source invalid or full-native sham unequal"}
    if any(not r["all_native_continuations"] for r in rows):
        return {"status":"INCONCLUSIVE_PROVENANCE_OR_NATIVE_CUSTODY",
                "reason":"native continuation missing, error or partial"}
    if any(not r["t5_equal_paid"] or
           not all(r[c]["cost_equal"] for c in CONTENT)
           for r in rows):
        return {"status":"INCONCLUSIVE_REAL_DECISION_COST",
                "reason":"32 T5 and 64 T6 genuine four-work/two-coin parity required"}

    pairs=[(r,r[c]) for r in rows for c in CONTENT]
    motor=[(r,c) for r in rows for c in CONTENT if r[c]["motor_changed"]]
    motor_roots={r["root"] for r,c in motor}
    motor_ecologies={r["ecology"] for r,c in motor}
    m_ok=(len(motor)>=6 and len(motor_roots)>=6 and
          len(motor_ecologies)>=3)
    gains=[(r,c) for r,c in pairs if c["delta_lived_ticks"]>0]
    losses=[(r,c) for r,c in pairs if c["delta_lived_ticks"]<0]
    roots_gain={r["root"] for r,c in gains}
    ecology_gain={r["ecology"] for r,c in gains}
    a_ok=(len(roots_gain)>=6 and len(ecology_gain)>=3 and not losses)
    all_survival_zero=not gains and not losses
    dominated=[(r,c) for r,c in pairs if c["body"]["pareto"]==
               "CARRY_FIVE_CHANNEL_DOMINANCE"]
    inverse=[(r,c) for r,c in pairs if c["body"]["pareto"]==
             "ZERO_FIVE_CHANNEL_DOMINANCE"]
    roots_dom={r["root"] for r,c in dominated}
    ecology_dom={r["ecology"] for r,c in dominated}
    both_alive=all(c["body"]["pareto"]!="NOT_COMPARABLE_HORIZON"
                   for r,c in pairs)
    body_ok=(all_survival_zero and both_alive
             and len(roots_dom)>=8 and len(ecology_dom)>=3
             and not inverse)
    body_status=("BODY_PARETO_ONLY_NOT_SURVIVAL_ADAPTATION" if body_ok
        else "NOT_APPLICABLE_SURVIVAL_DIFFERS" if not all_survival_zero
        else "NO_REPRODUCIBLE_LOCAL_BODY_PARETO_SUPPORT")
    return {
        "status":"F1M_COMPLETE_SEPARATE_SCIENTIFIC_VERDICTS",
        "motor_verdict":("REPRODUCIBLE_LOCAL_T6_RESIDUAL_MOTOR_EFFECT"
                         if m_ok else "NO_REPRODUCIBLE_LOCAL_T6_RESIDUAL_MOTOR_EFFECT"),
        "survival_verdict":("LOCAL_T60_SURVIVAL_ADAPTIVE_ADVANTAGE"
                            if a_ok else "NO_REPRODUCIBLE_LOCAL_T60_SURVIVAL_ADVANTAGE"),
        "body_verdict":body_status,
        "paired_comparisons":64,
        "independent_roots":32,
        "motor_changed_pairs":len(motor),
        "motor_changed_distinct_roots":len(motor_roots),
        "motor_changed_ecologies":len(motor_ecologies),
        "survival_gain_pairs":len(gains),
        "survival_gain_distinct_roots":len(roots_gain),
        "survival_gain_ecologies":len(ecology_gain),
        "survival_loss_pairs":len(losses),
        "body_carry_pareto_pairs":len(dominated),
        "body_carry_pareto_distinct_roots":len(roots_dom),
        "body_carry_pareto_ecologies":len(ecology_dom),
        "body_reverse_pareto_pairs":len(inverse),
        "no_stage2_promotion":True,
    }


def audit_originals(on_archive):
    grid=science_grid()
    rows=[];steps=rounds=0
    for metadata,parts in on_archive:
        detail,inc,r=cold_root(grid,metadata,parts)
        rows.append(detail)
        steps+=inc;rounds+=r
    conclusion=classify(rows)
    return {"schema":"i3-stage8f1m-independent-scientific-cold-v0",
            "phase":"F1M_HELDOUT_RELEASE",
            "root_count":len(rows),
            "native_world_steps_verified":steps,
            "f1j_substantive_rounds_verified":rounds,
            "preexposure_grid_git_blob":Frozen.GRID_BLOB,
            "preexposure_protocol_git_blob":Frozen.PROTOCOL_BLOB,
            "no_engine_imports_or_heldout_reexecution":True,
            "verdicts":conclusion,
            "per_root":rows}
