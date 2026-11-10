"""Original-only G/R 24 new matched F0 real-state replay fork DEVELOPMENT, one execution.

Both policies use the historical paid GATE count rule, comparing the TD
priority vs independently HMAC-random memory identities. A full-policy effect
is descriptive; it does not fix realized replay count or certify ecological
iid. This source must be permanently closed after its first original archive.
"""
from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys

from . import stage2_survival_b1_sampling as SAMPLE
from . import stage2_survival_b1_worldspec_audit as SPECS
from . import stage2_survival_b1_engineering as SOURCE
from . import stage2_admission as GUARD
from . import two_phase_panel as TP
from ..modules.genome import generation_zero
from ..runtime.life import run_life

I3=Path(__file__).resolve().parents[1]
PLAN=I3/"docs/studies/stage2-replay-gate-selected-design/REALSTATE_FORK_24_PLAN.json"
SCHEMA="i3-stage2-1-realstate-fork-24-development-gr/v1"
PROTOCOL="I3_REALSTATE_FIRST_REPLAY_CONTENT_FORK_24_DEVELOPMENT_20261110"
FIRST=540000
PAIRS=24
HORIZON=400
POLICIES=("p13_replay_gate_v1","p13_replay_gate_random_content_v1")
WITNESS="2a1457a112752e0e9143059169db87fb11f4ec0730a48549d3159b371f925e43"
WITNESS_SHA="669af6b56e4dd055bad08d8c38f58de90d8e51a33a7cb8d6a861e078b1df21dd"
CLAIM_BRANCH="custody/i3-realstate-fork-24-development-20261110-claimed"
EVIDENCE_BRANCH="evidence/i3-realstate-fork-24-development-20261110-originals"


def _sha(data:bytes)->str:
    return sha256(data).hexdigest()


def _canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),
                      allow_nan=False).encode()


def plan():
    out=json.loads(PLAN.read_bytes())
    key=SAMPLE._key(WITNESS)
    expected={
        "schema":"i3-stage2-1-realstate-content-first-fork-development-24/v1",
        "status":"FROZEN_PROSPECTIVE_BEFORE_FIRST_WORLD",
        "protocol":PROTOCOL,"unit_index_start":FIRST,
        "matched_units":PAIRS,"planned_original_lives":2*PAIRS,
        "horizon":HORIZON,"cohort":"development",
        "arms":list(POLICIES),"new_witness":WITNESS,
        "witness_sha256":WITNESS_SHA,
        "independent_iid_ecology_attested":False,
        "scientific_registration":False,"noninferiority_margin":None,
        "selection_validation_reserve":False,"stage2_2":False,
        "scientific_go":False,"independent_methodological_signoff":False,
        "source_claim":CLAIM_BRANCH,"evidence_branch":EVIDENCE_BRANCH,
        "observer_scope":"external random-content arm only; first actually paid different replay memory subset; two detached Mind copies; unchanged actual GATE count rule and World; no survival mediation claim",
    }
    if _sha(key)!=WITNESS_SHA or WITNESS==SAMPLE.PREVIEW_WITNESS:
        raise PermissionError("invalid source-locked witness")
    if any(out.get(k)!=v for k,v in expected.items()):
        raise PermissionError("frozen replay-fork plan modified")
    return out


def cases():
    plan()
    key=SAMPLE._key(WITNESS)
    units=[{"pair_id":f"fork-dev-{i:06d}","index":FIRST+i,
            "cohort":"development","family":SAMPLE._family(key,i),
            "world_seed":SAMPLE._seed(key,i,"world",SAMPLE.WORLD_BASE),
            "genome_seed":SAMPLE._seed(key,i,"genome",SAMPLE.GENOME_BASE),
            "life_seed":SAMPLE._seed(key,i,"life",SAMPLE.LIFE_BASE)}
           for i in range(PAIRS)]
    SAMPLE._check_separation(units)
    from . import stage2_b1_development as B1
    from . import stage2_three_arm_development as THREE
    from . import stage2_content_48_development as OLD
    from . import stage2_water_divergence_24_development as WATER
    used=(B1.cases()[::2]+THREE.cases()[::3]+
          OLD.cases()[::2]+WATER.cases()[::2])
    used+=SAMPLE.preview(SAMPLE.PREVIEW_WITNESS)["proposed_units"]
    for domain in ("world_seed","genome_seed","life_seed"):
        if {u[domain] for u in units} & {u[domain] for u in used}:
            raise PermissionError("scientific or public-engineering seed collision; no reroll")
    return [{**r,"policy":p} for r in units for p in POLICIES]


def match_case(case,fingerprint):
    if type(case) is not dict or type(case.get("index")) is not int:
        raise PermissionError("exact developmental case required")
    offset=case["index"]-FIRST
    if not 0<=offset<PAIRS or case.get("policy") not in POLICIES:
        raise PermissionError("index/policy outside new content DEVELOPMENT allocation")
    if case!=cases()[2*offset+POLICIES.index(case["policy"])]:
        raise PermissionError("case identity changed from frozen source")
    if fingerprint!=SOURCE.source_fingerprint():
        raise PermissionError("content developmental source footprint mismatch")


def _run_case(scheduled,fingerprint):
    def run(case):
        match_case(case,fingerprint)
        index=case["index"]-FIRST
        if case!=scheduled[2*index+POLICIES.index(case["policy"])]:
            raise PermissionError("case not in original fixed pair order")
        spec=SPECS._construct_f0_spec(case["family"],case["world_seed"])
        ticket=GUARD.admit_realstate_fork_newworld_development(
            case=case,spec=spec,transport_fingerprint=fingerprint)
        life=run_life(generation_zero(case["genome_seed"]),spec,
                      case["life_seed"],HORIZON,protocol=PROTOCOL,
                      decision_policy=case["policy"],admission=ticket,
                      observer_realstate_content_fork=(case["policy"]==POLICIES[1]))
        life["admission_receipt"]=ticket.receipt()
        return life
    return run


def _reduce(identity,life,fingerprint):
    m=life["manifest"]
    account=life["cognitive_accounting"]
    r=life["admission_receipt"]
    n=life["steps_lived"]
    is_random=identity["policy"]==POLICIES[1]
    checks={
        "cohort":identity["cohort"]=="development" and
                 FIRST<=identity["index"]<FIRST+PAIRS,
        "policy":m["experimental_policy"]["name"]==identity["policy"],
        "paid_energy":account["totals"]["energy"]["unpaid"]<=1e-12,
        "paid_vigilance":account["totals"]["vigilance"]["unpaid"]<=1e-12,
        "no_shortfall":account["shortfall_steps"]==0,
        "settled":account["status"]=="SETTLED_FOR_DECLARED_WORK",
        "terminal":life["terminal"] in ("dead","censored"),
        "horizon":type(n) is int and 1<=n<=HORIZON,
        "censoring":life["terminal"]!="censored" or n==HORIZON,
        "gate_count":life["replay_gate"]["mode"]==
                     ("gate_random_content" if is_random else "gate"),
        "ticket":r["cohort"]=="development" and
                 r["index"]==identity["index"] and
                 r["family"]==identity["family"] and
                 r["world_seed"]==identity["world_seed"] and
                 r["world_sha256"]==m["world_sha256"] and
                 r["world_name"]==life["world"],
        "source":r["transport_fingerprint"]==fingerprint,
        "life_seed":m["life_seed"]==identity["life_seed"],
    }
    rc=None
    if is_random:
        rc=life["replay_gate"].get("random_content",{})
        o=rc.get("paid_replay_opportunities")
        paid=rc.get("selected_replays_paid")
        sleep=rc.get("lived_sleep_ordinals")
        diff=rc.get("distinct_from_priority_subsets")
        valid=all(type(x) is int and x>=0 for x in (o,paid,sleep,diff))
        checks["selection_receipt"]=(
            valid and 0<=diff<=o<=sleep<=life["actions"].get("dormir",0)
            and o<=paid<=16*o
            and paid==account["replays_executed"]
            and rc.get("count_rule")=="EXACT_ORIGINAL_GATE")
        fork=life.get("observer_realstate_content_fork")
        if not isinstance(fork,dict):
            checks["fork_report"]=False
        else:
            first=fork.get("first_fork")
            status=fork.get("status")
            if status=="FIRST_DIFFERING_REPLAY_CAPTURED":
                checks["fork_receipt"]=(
                    isinstance(first,dict) and
                    first.get("schema")=="i3-stage2.1-realstate-first-content-fork/v1" and
                    type(first.get("prepaid_replays_in_each_detached_arm")) is int and
                    1<=first["prepaid_replays_in_each_detached_arm"]<=16 and
                    first.get("observer_physical_debit") is False and
                    first.get("world_or_life_clone_created") is False and
                    type(first.get("l1_value_difference_between_detached_updates")) in (int,float) and
                    0<=first["l1_value_difference_between_detached_updates"]<float("inf") and
                    set(first.get("priority_memory_indices",[]))!=
                    set(first.get("random_memory_indices",[])))
            else:
                checks["fork_null"]=(first is None and
                    status=="NO_DIFFERING_FUNDED_REPLAY_OBSERVED")
            checks["fork_opportunity_bounds"]=(
                type(fork.get("prepaid_replay_opportunities_seen")) is int and
                type(fork.get("differing_replay_opportunities_seen")) is int and
                0<=fork["differing_replay_opportunities_seen"]<=
                fork["prepaid_replay_opportunities_seen"]<=o and
                (status!="FIRST_DIFFERING_REPLAY_CAPTURED" or
                 fork["differing_replay_opportunities_seen"]>0))
    else:
        checks["no_random_selection_receipt"]=(
            "random_content" not in life["replay_gate"])
        checks["no_fork_in_priority"]=(
            "observer_realstate_content_fork" not in life)
    if not all(checks.values()):
        raise ValueError("invalid original: "+",".join(k for k,v in checks.items() if not v))
    return {
        **identity,
        "terminal":life["terminal"],"steps_lived":n,
        "dead_at_horizon":life["terminal"]=="dead" and n==HORIZON,
        "death_causes":life["death_causes"],
        "paid_energy":account["totals"]["energy"]["paid"],
        "paid_vigilance":account["totals"]["vigilance"]["paid"],
        "replays_paid":account["replays_executed"],
        "sleep_steps":life["actions"].get("dormir",0),
        "random_content_receipt":(None if rc is None else {
            k:rc[k] for k in ("paid_replay_opportunities",
                             "selected_replays_paid","lived_sleep_ordinals",
                             "distinct_from_priority_subsets")}),
        "realstate_fork_receipt":(None if not is_random else {
            "status":fork["status"],
            "prepaid_replay_opportunities_seen":
                fork["prepaid_replay_opportunities_seen"],
            "differing_replay_opportunities_seen":
                fork["differing_replay_opportunities_seen"],
            "first_fork":fork["first_fork"]}),
        "world_sha256":m["world_sha256"],
        "genome_sha256":_sha(_canonical(m["genome"])),
        "source_sha256":m["source"]["sha256"],
    }


def analyze(scheduled,rows):
    if len(scheduled)!=2*PAIRS or len(rows)!=2*PAIRS:
        raise ValueError("missing assigned original rows; no scientific verdict")
    pairs=[]
    for i in range(PAIRS):
        a,b=rows[2*i:2*i+2]
        for row,case in zip((a,b),scheduled[2*i:2*i+2]):
            if any(row.get(k)!=case[k] for k in (
                    "pair_id","index","cohort","family","policy",
                    "world_seed","genome_seed","life_seed")):
                raise ValueError("original assigned life identity changed")
        if any(a[k]!=b[k] for k in (
                "index","pair_id","family","world_seed","genome_seed",
                "life_seed","world_sha256","genome_sha256","source_sha256")):
            raise ValueError("pair does not start from same World/G0/source")
        pairs.append((a,b))
    def by_arm(blocks,j):
        selected=[t[j] for t in blocks]
        n=len(selected)
        if not n:
            return {"assigned":0}
        outcome={"assigned":n,"survivors":sum(r["terminal"]=="censored" for r in selected),
                 "deaths_at_step_400":sum(r["dead_at_horizon"] for r in selected),
                 "mean_lived_steps":sum(r["steps_lived"] for r in selected)/n,
                 "mean_energy_paid":sum(r["paid_energy"] for r in selected)/n,
                 "mean_vigilance_paid":sum(r["paid_vigilance"] for r in selected)/n,
                 "mean_replays_paid":sum(r["replays_paid"] for r in selected)/n,
                 "mean_sleep_steps":sum(r["sleep_steps"] for r in selected)/n}
        if j==1:
            outcome["random_content_distinct_subsets"]=sum(
                r["random_content_receipt"]["distinct_from_priority_subsets"]
                for r in selected)
            outcome["random_content_replay_opportunities"]=sum(
                r["random_content_receipt"]["paid_replay_opportunities"]
                for r in selected)
        return outcome
    def paired(blocks):
        n=len(blocks)
        if not n:return {"assigned_pairs":0}
        a=[x[0] for x in blocks]
        b=[x[1] for x in blocks]
        ap=[x["terminal"]=="censored" for x in a]
        bp=[x["terminal"]=="censored" for x in b]
        first_only=sum(x and not y for x,y in zip(ap,bp))
        second_only=sum(y and not x for x,y in zip(ap,bp))
        return {
            "assigned_pairs":n,
            "both_survive":sum(x and y for x,y in zip(ap,bp)),
            "priority_only_survives":first_only,
            "random_content_only_survives":second_only,
            "neither_survives":sum(not x and not y for x,y in zip(ap,bp)),
            "paired_risk_difference_priority_minus_random":
                (first_only-second_only)/n,
            "mean_lived_step_difference_priority_minus_random":
                sum(x["steps_lived"]-y["steps_lived"] for x,y in zip(a,b))/n,
            "priority_longer":sum(x["steps_lived"]>y["steps_lived"] for x,y in zip(a,b)),
            "random_longer":sum(x["steps_lived"]<y["steps_lived"] for x,y in zip(a,b)),
        }
    first=[b["realstate_fork_receipt"]["first_fork"]
           for a,b in pairs
           if b["realstate_fork_receipt"]["first_fork"] is not None]
    positives=sum(x["l1_value_difference_between_detached_updates"]>1e-12
                  for x in first)
    mechanism={
        "assigned_pairs":PAIRS,"first_fork_captured":len(first),
        "first_fork_absent":PAIRS-len(first),
        "positive_learned_value_difference":positives,
        "zero_learned_value_difference":len(first)-positives,
        "primary_fraction_per_assigned_pair":positives/PAIRS,
        "sum_first_fork_L1":sum(x["l1_value_difference_between_detached_updates"]
                                for x in first),
        "all_assigned_included":True,"observer_external_only":True,
        "no_second_world":True,"biological_mediation_claim":False,
        "by_family":{fam:{
            "assigned":sum(a["family"]==fam for a,b in pairs),
            "captured":sum(a["family"]==fam and
                           b["realstate_fork_receipt"]["first_fork"] is not None
                           for a,b in pairs),
            "positive":sum(a["family"]==fam and
                           b["realstate_fork_receipt"]["first_fork"] is not None and
                           b["realstate_fork_receipt"]["first_fork"]
                           ["l1_value_difference_between_detached_updates"]>1e-12
                           for a,b in pairs),
        } for fam in SAMPLE.FAMILIES}}
    return {
        "status":"COMPLETE_EXPLORATORY_DEVELOPMENT_ONLY",
        "primary":"FIRST_REALSTATE_DIFFERENT_CONTENT_DETACHED_TD_L1_PER_24_ASSIGNED",
        "mechanism":mechanism,
        "overall":paired(pairs),
        "by_arm":{p:by_arm(pairs,j) for j,p in enumerate(POLICIES)},
        "by_family":{fam:{
            "paired":paired([x for x in pairs if x[0]["family"]==fam]),
            "by_arm":{p:by_arm([x for x in pairs if x[0]["family"]==fam],j)
                      for j,p in enumerate(POLICIES)}
        } for fam in SAMPLE.FAMILIES},
        "independent_iid_ecology_attested":False,
        "causal_fixed_replay_count_claim":False,
        "noninferiority_margin_approved":False,
        "selection_validation_reserve_executed":False,
        "scientific_go":False,
        "scientific_verdict":"NOT_ISSUED",
    }


def _claim_trusted_main():
    if (os.getenv("GITHUB_EVENT_NAME")!="push" or
            os.getenv("GITHUB_REF")!="refs/heads/main" or
            os.getenv("GITHUB_RUN_ATTEMPT")!="1" or
            os.getenv("I3_REALSTATE_FORK_CLAIM_BRANCH")!=CLAIM_BRANCH):
        raise PermissionError("content developmental World requires one trusted-main claim")
    sha=os.getenv("GITHUB_SHA","")
    if len(sha)!=40 or any(c not in "0123456789abcdef" for c in sha):
        raise PermissionError("exact source SHA missing")
    def git(*args):
        return subprocess.run(["git",*args],capture_output=True,text=True,check=True).stdout.strip()
    if git("rev-parse","HEAD")!=sha or git("status","--porcelain"):
        raise PermissionError("source dirty or mismatched")
    if not git("ls-remote","--heads","origin",CLAIM_BRANCH):
        raise PermissionError("claim branch not pushed before first birth")
    if git("ls-remote","--heads","origin",EVIDENCE_BRANCH):
        raise PermissionError("originals already published; no replay")
    return sha


def execute(destination):
    sha=_claim_trusted_main()
    root=Path(destination).resolve()
    if root.exists() and any(root.iterdir()):
        raise PermissionError("original destination occupied, never retry")
    root.mkdir(parents=True,exist_ok=True)
    scheduled=cases()
    fingerprint=SOURCE.source_fingerprint()
    lock={
        "schema":SCHEMA+"/claim","status":"CONSUMED_BEFORE_FIRST_BIRTH",
        "source_sha":sha,"source_fingerprint":fingerprint,
        "plan_sha256":_sha(PLAN.read_bytes()),"witness_sha256":WITNESS_SHA,
        "claim_branch":CLAIM_BRANCH,"evidence_branch":EVIDENCE_BRANCH,
        "pairs":PAIRS,"lives":2*PAIRS,"no_retry":True,
        "confirmatory_science_authorized":False}
    (root/"SOURCE_LOCK.json").write_text(
        json.dumps(lock,sort_keys=True,indent=2)+"\n")
    g=TP.generate(scheduled,_run_case(scheduled,fingerprint),root/"originals")
    report={
        "schema":SCHEMA,"status":"GENERATION_INCOMPLETE_NO_RETRY",
        "planned":2*PAIRS,"generated":g["generated"],"reduced":0,
        "phase_G":g["status"],"phase_R":None,
        "source_sha":sha,"source_fingerprint":fingerprint,
        "plan_sha256":lock["plan_sha256"],
        "scientific_verdict":"NOT_ISSUED","no_retry":True}
    if g["status"]!="GENERATED":
        report["failure"]=g["failure"]
    else:
        r=TP.reduce(root/"originals",
                    lambda case,life:_reduce(case,life,fingerprint))
        report["phase_R"]=r["status"]
        if r["status"]!="COMPLETE":
            report["status"]="REDUCTION_DEFECT_PENDING_REPAIR"
            report["failure"]=r.get("failure")
        else:
            report["reduced"]=len(r["rows"])
            report["analysis"]=analyze(scheduled,r["rows"])
            report["status"]="COMPLETE_EXPLORATORY_DEVELOPMENT_ONLY"
            (root/"REDUCED_ROWS.json").write_text(
                json.dumps(r["rows"],sort_keys=True,indent=2)+"\n")
    (root/"EXECUTION_REPORT.json").write_text(
        json.dumps(report,sort_keys=True,indent=2)+"\n")
    return report


def main(argv=None):
    argv=sys.argv if argv is None else argv
    if len(argv)!=3 or argv[1]!="execute":
        raise SystemExit("usage: python -m i3.lab.stage2_realstate_fork_24_development execute FRESH_DIR")
    r=execute(argv[2])
    print(json.dumps({k:v for k,v in r.items() if k!="failure"},
                     sort_keys=True,indent=2))
    if r["status"]!="COMPLETE_EXPLORATORY_DEVELOPMENT_ONLY":
        raise SystemExit("original content study incomplete, NO RETRY")


if __name__=="__main__":
    main()
