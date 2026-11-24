#!/usr/bin/env python3
"""PH1 F1M: one-pass, SHA-pinned, engine-free original competition witness audit.

POSTHOC ONLY. Reads the immutable 32-root F1M RAW GitHub Actions ZIP and
immortal cold report. Never imports World/Mind, changes the engine, or executes
new native steps. Exposes *actual* threshold witnesses, not speculative motor
counterfactuals. Uses stdlib Python 3.12 (3.11 compatible).

CLI:
  python tools/stage8f1m_ph1_archival_thresholds.py --raw-zip PATH \
       --cold-zip PATH --output PATH
"""
from __future__ import annotations

import argparse
from contextlib import ExitStack
from collections import Counter
import gzip
import hashlib
import json
import math
from pathlib import Path
import statistics
import tarfile
import zipfile

RAW_ZIP_SHA = "5421f48132ea2839114baa97199acdaa3cfe2f581610e733000308f99d5e6324"
RAW_TAR_SHA = "4e4888d00d5494f071d84d469e26f62d497dba8ce390bbe01101607a018992bc"
RAW_MANIFEST_SHA = "47ad255aaac32756a1777cbecfe4d3356b58beee4b7e4b1aaf403612a961a4af"
COLD_SHA = "85cc44b84075321f96114b14e8d1c6b52b592e0c44e8cb40180b568e9c1c8791"
FROZEN_MAIN_SHA = "a0d063402cad87d6dd255e2f842586b8f8f95267"
CONSUMED_SHA = "f6e213ca197c432b03907c3d8999ddf10bcac809"
ROOTS = tuple(f"M{i:02}" for i in range(1, 33))
CONTENTS = ("recent", "stale")
ARMS = tuple(f"{c}_{mode}" for c in CONTENTS for mode in ("carry", "zero"))
LEAK, GAIN, RESIDUAL = 0.2, 1.0, 0.5  # exact source-locked F1J/Mind constants
TOL = 2e-11
SCHEMA = "i3-stage8f1m-ph1-posthoc-original-threshold-witness-audit/v0"


def check(test, why):
    if not test:
        raise ValueError("F1M PH1 archive or witness invalid: " + why)


def canonical(d):
    return json.dumps(d, ensure_ascii=False, sort_keys=True,
                      allow_nan=False, separators=(",", ":")).encode("utf-8")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024*1024), b""):
            h.update(block)
    return h.hexdigest()


class HashReader:
    def __init__(self, f):
        self.source = f
        self.hash = hashlib.sha256()

    def read(self, count=-1):
        b = self.source.read(count)
        self.hash.update(b)
        return b

    def hex(self):
        return self.hash.hexdigest()


def _close(actual, expected):
    return math.isclose(actual, expected, abs_tol=TOL, rel_tol=2e-12)


def _keys_equal_numbers(a, b):
    return a.keys()==b.keys() and all(_close(a[k], b[k]) for k in a)


def _round_eligibility(activations, thresholds):
    """Actual F1J final-round threshold winner candidate set, no RNG or actor."""
    crossed = {key:(value-thresholds[key])/thresholds[key]
               for key,value in activations.items() if value>=thresholds[key]}
    if crossed:
        margin = max(crossed.values())
        winners = sorted(key for key,val in crossed.items() if val==margin)
        return {"mechanism":"final_round_threshold",
                "candidates":winners, "crossed":sorted(crossed),
                "best_margin":margin}
    highest = max(activations.values())
    winners = sorted(key for key,val in activations.items()
                     if val>=highest-1e-12)
    flat=(len(winners)==len(activations) and
          max(activations.values())-min(activations.values())<=1e-12)
    return {"mechanism":("all_activations_equal_raw_score_fallback" if flat
                          else "final_round_activation"),
            "candidates":winners, "crossed":[], "best_margin":None}


def validate_competition_witness(step, label):
    w = step["decision_info"]["observer"]["competition_witness"]
    keys = set(w["scored_order"])
    check(bool(keys) and len(keys)==len(w["scored_order"]),label+" duplicate scores")
    for k in ("normalized_evidence","thresholds","accumulators_before",
              "accumulators_before_residual", "accumulators_after_residual"):
        check(set(w[k])==keys,label+" broken witness keys "+k)
    for k,v in w["thresholds"].items():
        check(type(v) in (int,float) and math.isfinite(v) and v>0,
              label+" invalid nonpositive threshold")
    check(w["paid_competition_cycles"]==len(w["actual_substantive_round_snapshots"])
          and w["paid_competition_cycles"]>0,label+" inconsistent substantive rounds")
    check(w["paid_competition_cycles"] <= w["round_capacity_from_actual_body"],
          label+" unfunded rounds count")
    check(not w["budget_blocked_before_full_round_capacity"]
          and w["paid_competition_cycles"]==w["round_capacity_from_actual_body"],
          label+" incomplete paid rounds")
    before = w["accumulators_before"]
    thresholds=w["thresholds"]
    rounds=[]
    for number,snapshot in enumerate(w["actual_substantive_round_snapshots"],1):
        check(set(snapshot)==keys,label+" round options changed")
        for key in keys:
            expected=max(0.0,(1-LEAK)*before[key]+GAIN*w["normalized_evidence"][key])
            check(_close(snapshot[key],expected),
                  label+f" round={number} option={key} not substantive F1J")
        rounds.append(_round_eligibility(snapshot,thresholds))
        before=snapshot
    check(_keys_equal_numbers(before,w["accumulators_before_residual"]),
          label+" final snapshot differs from pre-residual")
    for key,val in before.items():
        predicted=0.0 if key==w["winner_before_control"] else RESIDUAL*val
        check(_close(predicted,w["accumulators_after_residual"][key]),
              label+" after-winner residual multiplier invalid")
    check(rounds[-1]["mechanism"]==w["selection_mechanism"],
          label+" final round threshold mechanism disagrees")
    if w["selection_mechanism"]!="all_activations_equal_raw_score_fallback":
        check(rounds[-1]["candidates"]==w["tie_candidates"],
              label+" final tie candidate witness disagrees")
    else:
        # Raw score tie-breaker has NO direct competition accumulator analog.
        # Witnessed tie candidates come from native score fall-back, not this auditor.
        check(set(w["tie_candidates"])<=keys,
              label+" invalid final raw-score fallback candidates")
    check(w["winner_before_control"] in w["tie_candidates"],
          label+" actual winner outside final ties")
    check(w["final_admitted_action"] == step["action"],
          label+" control action differs from native action")
    return w,rounds


def _first_round_crossing(rounds):
    return next((i for i,r in enumerate(rounds,1) if r["crossed"]),None)


def _first_round_final_winner_crossing(w,rounds):
    win=w["winner_before_control"]
    return next((i for i,r in enumerate(rounds,1) if win in r["crossed"]),None)


def _decisive_margin(w):
    """Final threshold-normalized winner surplus vs second-best eligible surplus."""
    finals=w["accumulators_before_residual"]
    thresholds=w["thresholds"]
    ratios={key:(act-thresholds[key])/thresholds[key]
            for key,act in finals.items()}
    high=sorted(ratios.values(),reverse=True)
    return {"winner_surplus":ratios[w["winner_before_control"]],
            "runner_up_surplus":high[1] if len(high)>1 else None,
            "winner_runner_up_gap":high[0]-high[1] if len(high)>1 else None,
            "crossed_count":sum(x>=0 for x in ratios.values())}


def _first_last_diff(sequence):
    return {"first":next((x for x,yes in sequence if yes),None),
            "last":next((x for x,yes in reversed(sequence) if yes),None),
            "ticks":sum(yes for _,yes in sequence)}


def analyze_pair(root,ecology,content,carry,zero,expected):
    cf,zf=carry["fork"],zero["fork"]
    check(cf["mode"]=="carry" and zf["mode"]=="zero",
          root+content+" fork treatment labels")
    check(cf["keys"]==zf["keys"] and cf["values_before"]==zf["values_before"],
          root+content+" not same personal residual source")
    check(cf["values_after"]==cf["values_before"] and
          set(zf["values_after"])==set(cf["values_before"]) and
          all(v==0 for v in zf["values_after"].values()),
          root+content+" fork not carry vs zero solely")
    raw_residual={k:v for k,v in cf["values_before"].items() if v!=0.0}
    a,b=carry["followup"]["steps"],zero["followup"]["steps"]
    check(len(a)==len(b)==55,root+content+" missing native T6..T60 steps")
    before_diff=[];after_diff=[];snapshot_diff=[];winner_diff=[];any_motor_diff=[]
    for tick,(left,right) in enumerate(zip(a,b),6):
        check(left["t"]==right["t"]==tick,root+content+" non-native step sequence")
        check(left["cognitive_work"]==right["cognitive_work"]
              and left["decision_remaining"]==right["decision_remaining"]
              and left["requested_native_cost"]==right["requested_native_cost"]
              and left["native_motor"]["cognitive_accounting"] ==
              right["native_motor"]["cognitive_accounting"],
              root+content+f" paid work parity at T{tick}")
        wl,rl=validate_competition_witness(left,root+"/"+content+f"/carry/T{tick}")
        wr,rr=validate_competition_witness(right,root+"/"+content+f"/zero/T{tick}")
        check(wl["scored_order"]==wr["scored_order"]
              and wl["normalized_evidence"]==wr["normalized_evidence"]
              and wl["thresholds"]==wr["thresholds"]
              and wl["round_capacity_from_actual_body"]==wr["round_capacity_from_actual_body"],
              root+content+f" changed scored inputs at T{tick}")
        before_diff.append((tick,wl["accumulators_before"] != wr["accumulators_before"]))
        after_diff.append((tick,wl["accumulators_after_residual"] != wr["accumulators_after_residual"]))
        snapshot_diff.append((tick,wl["actual_substantive_round_snapshots"]!=wr["actual_substantive_round_snapshots"]))
        winner_diff.append((tick,wl["winner_before_control"]!=wr["winner_before_control"]))
        any_motor_diff.append((tick,(left["action"],left["param"])!=(right["action"],right["param"])))
        if tick==6:
            first_w,first_r,first_a,first_b=wl,wr,rl,rr
            check(all(_close(wl["accumulators_before"][k],cf["values_after"].get(k,0.0))
                      and _close(wr["accumulators_before"][k],zf["values_after"].get(k,0.0))
                      for k in wl["accumulators_before"]),
                  root+content+" original fork not visible at T6")
    expected_pair=expected
    check(not any(z for _,z in winner_diff+any_motor_diff),
          root+content+" differs from frozen null scientific result")
    check(first_w["selection_mechanism"]==first_r["selection_mechanism"]=="final_round_threshold",
          root+content+" T6 unexpectedly not final-round threshold")
    check(first_w["control_order"]==first_r["control_order"],
          root+content+" actual control order differs")
    # Per-round candidates are mathematical witness-derived possibilities only.
    # They were not real actions or hypothetical interventions.
    per_round_comparison=[{
        "round":i,"carry_crossed":len(l["crossed"]),"zero_crossed":len(r["crossed"]),
        "crossed_sets_differ":l["crossed"]!=r["crossed"],
        "threshold_leader_candidates_differ":l["candidates"]!=r["candidates"],
        "both_above_threshold":bool(l["crossed"] and r["crossed"]),
    } for i,(l,r) in enumerate(zip(first_a,first_b),1)]
    active_scored=sorted(set(raw_residual)&set(first_w["scored_order"]))
    ranking=sorted(first_w["normalized_evidence"],key=lambda k:(-first_w["normalized_evidence"][k],k))
    margin_a=_decisive_margin(first_w)
    margin_b=_decisive_margin(first_r)
    rank_of_residual=[ranking.index(key)+1 for key in active_scored]
    return {
        "root":root,"content":content,"ecology":ecology,
        "active_residual":bool(raw_residual),
        "residual_key_count":len(raw_residual),
        "residual_scored_key_count":len(active_scored),
        "scored_key_count":len(ranking),
        "residual_key_evidence_ranks":rank_of_residual,
        "highest_rank_of_residual_key":min(rank_of_residual) if rank_of_residual else None,
        "residual_on_actual_winner":first_w["winner_before_control"] in raw_residual,
        "residual_sum_abs":sum(abs(v) for v in raw_residual.values()),
        "rounds_paid":len(first_a),
        "first_any_threshold_crossing_carry":_first_round_crossing(first_a),
        "first_any_threshold_crossing_zero":_first_round_crossing(first_b),
        "first_winner_threshold_crossing_carry":_first_round_final_winner_crossing(first_w,first_a),
        "first_winner_threshold_crossing_zero":_first_round_final_winner_crossing(first_r,first_b),
        "rounds_with_different_threshold_crossers":sum(x["crossed_sets_differ"] for x in per_round_comparison),
        "rounds_with_different_early_threshold_leader":sum(x["threshold_leader_candidates_differ"] for x in per_round_comparison),
        "final_threshold_candidates_equal":first_a[-1]["candidates"]==first_b[-1]["candidates"],
        "final_threshold_crossed_sets_equal":first_a[-1]["crossed"]==first_b[-1]["crossed"],
        "winner":first_w["winner_before_control"],
        "first_motor":first_w["final_admitted_action"],
        "final_winner_surplus_carry":margin_a["winner_surplus"],
        "final_winner_surplus_zero":margin_b["winner_surplus"],
        "final_winner_runner_gap_carry":margin_a["winner_runner_up_gap"],
        "final_winner_runner_gap_zero":margin_b["winner_runner_up_gap"],
        "final_crossed_count_carry":margin_a["crossed_count"],
        "final_crossed_count_zero":margin_b["crossed_count"],
        "final_rounds":per_round_comparison,
        "all_55_motor_commands_identical":not any(z for _,z in any_motor_diff),
        "all_55_winners_identical":not any(z for _,z in winner_diff),
        "initial_accumulator_difference":_first_last_diff(before_diff),
        "per_round_snapshots_difference":_first_last_diff(snapshot_diff),
        "post_residual_accumulator_difference":_first_last_diff(after_diff),
        "carry_raw_gzip_sha256":expected_pair["carry_original_gzip_sha256"],
        "zero_raw_gzip_sha256":expected_pair["zero_original_gzip_sha256"],
    }


def summary(pairs):
    check(len(pairs)==64,"not 64 contrasts")
    active=[p for p in pairs if p["active_residual"]]
    inactive=[p for p in pairs if not p["active_residual"]]
    check(len(active)==40 and len(inactive)==24,"non-zero residual count changed")
    check(len({p['root'] for p in pairs})==32 and len({p['ecology'] for p in pairs})==8,
          "original 32 roots/eight ecologies incomplete")
    counts_by_eco={}
    for eco in sorted({p['ecology'] for p in pairs}):
        q=[p for p in pairs if p['ecology']==eco]
        counts_by_eco[eco]={"pairs":len(q),"nonzero_pairs":sum(p["active_residual"] for p in q),
                            "roots":len({p["root"] for p in q}),
                            "roots_nonzero":len({p["root"] for p in q if p["active_residual"]}),
                            "early_leader_change_pairs":sum(p["rounds_with_different_early_threshold_leader"]>0 for p in q),
                            "final_crossed_sets_change_pairs":sum(not p["final_threshold_crossed_sets_equal"] for p in q)}
    def quant(vals):
        return {"min":min(vals),"median":statistics.median(vals),"max":max(vals)} if vals else None
    return {
        "root_count":32,"contrast_count":64,"ecology_count":8,
        "nonzero_R_pairs":len(active),"zero_R_pairs":len(inactive),
        "nonzero_R_root_count":len({p['root'] for p in active}),
        "nonzero_R_ecologies":len({p['ecology'] for p in active}),
        "active_pairs_with_reused_scored_keys":sum(p['residual_scored_key_count']>0 for p in active),
        "active_pairs_R_on_actual_winner":sum(p['residual_on_actual_winner'] for p in active),
        "active_pairs_R_on_only_losing_options":sum(not p['residual_on_actual_winner'] for p in active),
        "pairs_different_first_threshold_crossing_round":sum(p["first_any_threshold_crossing_carry"]!=p["first_any_threshold_crossing_zero"] for p in pairs),
        "pairs_different_first_winner_crossing_round":sum(p["first_winner_threshold_crossing_carry"]!=p["first_winner_threshold_crossing_zero"] for p in pairs),
        "pairs_different_crossed_set_any_round":sum(p['rounds_with_different_threshold_crossers']>0 for p in pairs),
        "pairs_different_early_round_threshold_leader":sum(p['rounds_with_different_early_threshold_leader']>0 for p in pairs),
        "pairs_different_final_threshold_candidate_set":sum(not p['final_threshold_candidates_equal'] for p in pairs),
        "pairs_different_final_crossed_set":sum(not p['final_threshold_crossed_sets_equal'] for p in pairs),
        "pairs_motor_changed_any_T6_T60":sum(not p['all_55_motor_commands_identical'] for p in pairs),
        "pairs_winner_changed_any_T6_T60":sum(not p['all_55_winners_identical'] for p in pairs),
        "active_early_round_leader_changes":sum(p['rounds_with_different_early_threshold_leader']>0 for p in active),
        "active_rounds_early_leader_difference_total":sum(p['rounds_with_different_early_threshold_leader'] for p in active),
        "active_first_winner_threshold_crossings_carry":Counter(str(p['first_winner_threshold_crossing_carry']) for p in active),
        "active_first_winner_threshold_crossings_zero":Counter(str(p['first_winner_threshold_crossing_zero']) for p in active),
        "active_final_winner_surplus_carry":quant([p['final_winner_surplus_carry'] for p in active]),
        "active_final_winner_surplus_zero":quant([p['final_winner_surplus_zero'] for p in active]),
        "active_final_winner_gap_carry":quant([p['final_winner_runner_gap_carry'] for p in active]),
        "active_final_winner_gap_zero":quant([p['final_winner_runner_gap_zero'] for p in active]),
        "active_residual_evidence_best_rank":Counter(str(p['highest_rank_of_residual_key']) for p in active),
        "active_acc_diff_last_tick":Counter(str(p['initial_accumulator_difference']['last']) for p in active),
        "active_after_residual_diff_last_tick":Counter(str(p['post_residual_accumulator_difference']['last']) for p in active),
        "by_ecology":counts_by_eco,
    }


def audit(raw_zip=None,cold_zip=None,raw_tar=None,manifest_file=None,cold_report=None):
    """Analyze original data from Actions ZIPs OR the two immutable Releases.

    The RAW source tar and its manifest are checked by pinned SHA256 either
    way. Actions ZIP mode additionally authenticates the outer GitHub artifact.
    """
    check((raw_zip is not None) != (raw_tar is not None),
          "provide exactly one original transport source")
    if raw_zip is not None:
        check(file_sha(raw_zip)==RAW_ZIP_SHA,"outer GitHub Actions original ZIP SHA")
    with ExitStack() as sources:
        if cold_zip is not None:
            check(cold_report is None,"ambiguous cold report inputs")
            cold_z=sources.enter_context(zipfile.ZipFile(cold_zip))
            cold_raw=cold_z.read("F1M_INDEPENDENT_COLD_T60.json")
        else:
            check(cold_report is not None,"missing signed independent cold report")
            cold_raw=Path(cold_report).read_bytes()
        check(sha(cold_raw)==COLD_SHA,"immutable independent cold report SHA")
        cold=json.loads(cold_raw)
        check(cold["verdicts"]["status"]=="F1M_COMPLETE_SEPARATE_SCIENTIFIC_VERDICTS"
              and cold["roots_verified"]==32 and cold["original_part_gzips_sha256_verified"]==384
              and cold["source_git_commit"]==FROZEN_MAIN_SHA
              and cold["byte_custody"]["raw_release_target"]==CONSUMED_SHA,
              "cold valid/provenance/cost gates not positive")
        check(cold['verdicts']['motor_changed_pairs']==0 and
              cold['verdicts']['survival_gain_pairs']==0,
              "never reclassify frozen scientific result")
    with ExitStack() as archive:
        if raw_zip is not None:
            original_zip=archive.enter_context(zipfile.ZipFile(raw_zip))
            man_raw=original_zip.read('f1m-originals/F1M_CUSTODY_MANIFEST.json')
            original=archive.enter_context(original_zip.open(
                'f1m-originals/F1M_ORIGINALS_384_GZIP.tar.gz'))
        else:
            check(manifest_file is not None and raw_tar is not None,
                  'missing original immutable Release manifest or tar')
            man_raw=Path(manifest_file).read_bytes()
            original=archive.enter_context(Path(raw_tar).open('rb'))
        check(sha(man_raw)==RAW_MANIFEST_SHA,
              "original immutable RAW manifest SHA")
        manifest=json.loads(man_raw)
        check(manifest['originals_tar_gzip_sha256']==RAW_TAR_SHA and
              manifest['original_part_count']==384 and
              manifest['roots']==list(ROOTS) and len(manifest['entries'])==384,
              "not complete original 32-root custody")
        expected={e['path']:e for e in manifest['entries']}
        check(len(expected)==384,"duplicate native original part paths")
        check({f'{root}/{arm}.json.gz' for root in ROOTS for arm in ARMS}<=set(expected),
              "missing original four arms")
        parts={root:{} for root in ROOTS}
        pair_records=[]
        inspected=0;compressed_checked=0;checkpoints=0;all_names=set()
        reader=HashReader(original)
        with tarfile.open(fileobj=reader,mode='r|gz') as tar:
            for item in tar:
                name=item.name
                check(item.isfile() and name not in all_names and
                      '..' not in Path(name).parts and not name.startswith('/'),
                      'unsafe/duplicated tar member')
                all_names.add(name)
                if name.startswith('_checkpoint_'):
                    check(item.size<150000,'checkpoint unreasonable size')
                    evidence=json.loads(tar.extractfile(item).read())
                    checkpoints+=1
                    n=int(name.removeprefix('_checkpoint_').removesuffix('.json'))
                    check(evidence['completed_roots']==list(ROOTS[:n]) and
                          len(evidence['entries'])==12*n,
                          'checkpoint provenance mismatch')
                    continue
                check(name in expected,'unexpected gzip file in immutable tar '+name)
                entry=expected[name]
                raw=tar.extractfile(item).read()
                check(len(raw)==entry['gzip_bytes'] and sha(raw)==entry['gzip_sha256'],
                      'compressed original SHA mismatched '+name)
                compressed_checked+=1
                root=name.split('/')[0]
                part=name.split('/')[1].removesuffix('.json.gz')
                if part not in ARMS:
                    continue
                content=gzip.decompress(raw)
                check(len(content)==entry['original_bytes'] and
                      sha(content)==entry['original_sha256'],
                      'original native JSON SHA mismatched '+name)
                doc=json.loads(content)
                check(doc['schema']=='i3-stage8f1m-incremental-original-part/v0'
                      and doc['id']==root and doc['part']==part,
                      'native original identity mismatched '+name)
                parts[root][part]=doc['native']
                inspected+=1
                if len(parts[root])==4:
                    eco=next(row['ecology'] for row in cold['per_root']
                             if row['root']==root)
                    for mode in CONTENTS:
                        left_name=f'{root}/{mode}_carry.json.gz'
                        right_name=f'{root}/{mode}_zero.json.gz'
                        prior={
                            'carry_original_gzip_sha256':expected[left_name]['gzip_sha256'],
                            'zero_original_gzip_sha256':expected[right_name]['gzip_sha256'],
                        }
                        pair_records.append(analyze_pair(
                            root,eco,mode,parts[root][f'{mode}_carry'],
                            parts[root][f'{mode}_zero'],prior))
                    parts[root].clear()
        # Drain any trailing zip-stream bytes so the raw tar hash is complete.
        for chunk in iter(lambda:reader.read(1024*1024),b''):
            pass
        check(reader.hex()==RAW_TAR_SHA,'immutable tar raw compressed SHA')
        check(compressed_checked==384 and inspected==128 and checkpoints==32,
              'not all immutable original parts/PH1 forks/checkpoints audited')
        check(all(not d for d in parts.values()),'not all root pairs processed')
        check(len(all_names)==416,'missing archived original/receipt checkpoint')
    pair_records.sort(key=lambda p:(p['root'],CONTENTS.index(p['content'])))
    totals=summary(pair_records)
    return {"schema":SCHEMA,
            "phase":"POSTHOC_ARCHIVAL_ONLY_NOT_PREREG_SCIENCE",
            "sources":{"original_run_id":45500772324,
                "source_main_git_sha":FROZEN_MAIN_SHA,
                "consumed_immutable_git_ref_sha":CONSUMED_SHA,
                "source_original_github_actions_zip_sha256":RAW_ZIP_SHA,
                "source_raw_original_tar_sha256":RAW_TAR_SHA,
                "source_raw_manifest_sha256":RAW_MANIFEST_SHA,
                "source_cold_independent_report_sha256":COLD_SHA},
            "native_world_steps_created":0,"independent_roots":32,
            "original_gzip_sha_checked":compressed_checked,
            "original_gzip_decoded_sha_checked":inspected,
            "native_sham_or_source_paths_parsed":False,
            "all_32_incremental_checkpoints_verified":True,
            "F1M_motor_verdict_immutable":cold['verdicts']['motor_verdict'],
            "F1M_survival_verdict_immutable":cold['verdicts']['survival_verdict'],
            "F1M_body_verdict_immutable":cold['verdicts']['body_verdict'],
            "methodological_caveat":(
                "Exploratory audit of witnessed threshold competition only; "
                "per-round candidate sets are algebraic from ORIGINAL "
                "substantive paid snapshots, not counterfactual actions. "
                "64 paired contrasts but 32 independent origins. "
                "No new scientific test, no reexecution, no subgroup promotion."),
            "summary":totals,"pairs":pair_records}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    group=p.add_mutually_exclusive_group(required=True)
    group.add_argument('--raw-zip',type=Path)
    group.add_argument('--raw-tar',type=Path)
    p.add_argument('--manifest',type=Path,
                   help='RAW immutable Release F1M_CUSTODY_MANIFEST.json')
    cg=p.add_mutually_exclusive_group(required=True)
    cg.add_argument('--cold-zip',type=Path)
    cg.add_argument('--cold-report',type=Path)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    result=audit(args.raw_zip,args.cold_zip,
                 args.raw_tar,args.manifest,args.cold_report)
    if args.output.exists():
        raise FileExistsError('refuse overwriting earlier PH1 findings')
    args.output.write_bytes(canonical(result)+b'\n')
    print(json.dumps({"status":"PH1_ARCHIVE_ONLY_COMPLETE_NOT_SCIENTIFIC_VERDICT",
                      "report_sha256":file_sha(args.output),
                      "original_gzip_checked":result['original_gzip_sha_checked'],
                      "T6_active_pairs":result['summary']['nonzero_R_pairs'],
                      "early_leader_shifts":result['summary']['pairs_different_early_round_threshold_leader'],
                      "final_candidate_shifts":result['summary']['pairs_different_final_threshold_candidate_set'],
                      "native_world_steps_created":0},sort_keys=True))


if __name__=='__main__':
    main()
