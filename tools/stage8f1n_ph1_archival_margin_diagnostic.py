"""F1N-PH1: descriptive read-only diagnosis of the consumed F1N originals.

Never imports or executes i3, a producer, an experimental policy, or a new
World.step. No threshold search or new simulated action. It measures only the
actual two observed paid T6 competitions and native continuation receipts.
The original preregistered M/A/B result remains immutable and negative.
"""
from __future__ import annotations

import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import statistics
import tarfile
import zipfile

RUN = '45824249204'
SOURCE = '89f58723789ad0c88336b6e5b0eb7ff3227348a1'
CONSUMED = '38d1c94a146d32bd89151fca906a26a775052560'
NATIVE_ZIP = 'd2f03adc52cb8da95d11036e0d0344978dbef193ff4177a775dfa0470d3b5820'
COLD_ZIP = '034c0476f5b3dc4c9a58e2d145ab1eab4ce976ba5f23933a27f6e7d357fbec33'
TAR = '8995e25ced26dceb85737da6b8e01fd94c3877421238f1fccc0c7dd0e3d01ea6'
MANIFEST = '72c3d13da7a3266e0b71e670cfb930ce08470778d227bc1d7728c447a4dbea50'
COLD = '650aee67b3d356bc4dd359721b0f279e8af6a5648d35bc4de9350aa128ac681b'
INDEX = '817b21bf5d1a5e2f19b1a07ab03fbb581d79327851a4054d09fc4288147ecb74'
ROOTS = [f'N{i:02}' for i in range(1,49)]
PARTS = ['source_t1_t4', 'self_paid_t5', 'self_paid_t5_sham',
         'margin_t6_t60', 'margin_t6_t60_sham', 'masked_t6_t60',
         'masked_t6_t60_sham']
EPS = 1e-10


def require(ok, why):
    if not ok:
        raise ValueError('F1N-PH1 ARCHIVAL: ' + why)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def file_sha(p):
    with Path(p).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def witness(step):
    return step['decision_info']['observer']['competition_witness']


def scores(step):
    return {s['option']: s for s in step['decision_info']['observer']['score_witness']}


def motor(step):
    return [step['action'], step['param']]


def diff(a, b):
    return [x-y for x,y in zip(a,b)]


def crossings(w, values):
    return sorted(k for k in values if values[k] >= w['thresholds'][k])


def first_cross(w, key):
    if key not in w['thresholds']:
        return None
    for n, values in enumerate(w['actual_substantive_round_snapshots'], 1):
        if values[key] >= w['thresholds'][key]:
            return n
    return None


def score_rank(scores_by_key, key):
    if key not in scores_by_key:
        return None
    return 1 + sum(r['total_score'] > scores_by_key[key]['total_score'] + EPS
                   for r in scores_by_key.values())


def final_surplus(w, key):
    if key not in w['thresholds']:
        return None
    return w['accumulators_before_residual'][key] / w['thresholds'][key] - 1


def pair_diagnostic(root, meta, parts, cold):
    t5 = parts['self_paid_t5']['step']
    a, b = [parts[k]['followup'] for k in ('margin_t6_t60','masked_t6_t60')]
    x, y = a['steps'][0], b['steps'][0]
    u, v, p = witness(x), witness(y), witness(t5)
    r, s = u['f1n_margin_read'], v['f1n_margin_read']
    key, q = r['own_key'], r['own_q']
    require(t5['t']==5 and x['t']==y['t']==6 and x['before_world']==y['before_world'], root+' unequal source')
    require(key==p['winner_before_control'] and key==p['final_admitted_option'] and q==s['own_q'] and q==cold['q'], root+' changed source margin')
    require(r['mode']=='margin' and s['mode']=='masked' and r['memory_read_paid'] and s['memory_read_paid'] and r['applied_q']==q and s['applied_q']==0., root+' wrong paid intervention')
    require(x['cognitive_work']==y['cognitive_work'] and x['decision_remaining']==y['decision_remaining'] and x['requested_native_cost']==y['requested_native_cost'] and x['native_motor']['cognitive_accounting']==y['native_motor']['cognitive_accounting'],root+' unequal actual costs')
    require(cold['source_valid'] and cold['shams_neutral'] and cold['t6_equal_paid'] and cold['all_native_continuations'], root+' quality gates')
    scored=key in u['scored_order']
    offered_count=x['decision_info']['observer']['offered_options']
    require(type(offered_count) is int and offered_count >= len(u['scored_order']) and offered_count==y['decision_info']['observer']['offered_options'],root+' invalid offered count')
    # The observer stores only offered option COUNT, not their exact keys.
    # Absence can be attributed to non-offer only when every offered option
    # was scored; otherwise the precise non-offer vs truncation is unknown.
    offered=True if scored else False if offered_count==len(u['scored_order']) else None
    require(scored==r['own_key_scored']==s['own_key_scored']==cold['reused_scored_key'],root+' changed option availability')
    require(u['scored_order']==v['scored_order'] and scores(x)==scores(y) and u['normalized_evidence']==v['normalized_evidence'] and u['accumulators_before']==v['accumulators_before'] and u['actual_substantive_round_snapshots']==v['actual_substantive_round_snapshots'] and u['accumulators_before_residual']==v['accumulators_before_residual'], root+' evidence, option or paid integration mismatch')
    expected=dict(v['thresholds'])
    if scored: expected[key]*=1-.5*q
    require(u['thresholds']==expected,root+' unexpected threshold manipulation')
    nrounds=u['paid_competition_cycles']; require(nrounds==v['paid_competition_cycles']==len(u['actual_substantive_round_snapshots']),root+' unequal paid rounds')
    changed_rounds=[i for i,(am,bm) in enumerate(zip(u['actual_substantive_round_snapshots'],v['actual_substantive_round_snapshots']),1) if crossings(u,am)!=crossings(v,bm)]
    cross_a=crossings(u,u['accumulators_before_residual']); cross_b=crossings(v,v['accumulators_before_residual'])
    winner_change=u['winner_before_control']!=v['winner_before_control']; motor_change=motor(x)!=motor(y)
    require(motor_change==cold['motor_changed']==meta['comparison']['motor_changed'] and winner_change==meta['comparison']['winner_changed'],root+' original motor comparator')
    terminal_a=a['metrics']['terminal_body'];terminal_b=b['metrics']['terminal_body']; body_delta=diff(terminal_a,terminal_b)
    require(body_delta==cold['body_delta'] and len(a['steps'])-len(b['steps'])==cold['delta_lived_ticks'], root+' terminal comparator')
    # Classification is exhaustive and descriptive, never a new success test.
    if not scored:
        mechanism='NOT_OFFERED' if offered is False else 'NOT_SCORED_OFFER_IDENTITY_UNKNOWN'
    elif motor_change:
        mechanism='MOTOR_CHANGED'
    elif winner_change:
        mechanism='WINNER_CHANGED_MOTOR_SAME'
    elif v['winner_before_control']==key:
        mechanism='ALREADY_WINNER_WITHOUT_MARGIN'
    elif first_cross(u,key) is None:
        mechanism='KEY_NEVER_CROSSES_EVEN_WITH_MARGIN'
    else:
        mechanism='KEY_CROSSES_BUT_DOES_NOT_WIN'
    sc=scores(y)
    result={'root':root,'ecology':cold['ecology'],'seed':cold['seed'], 'q':q,'t5_key':key,'t5_motor':motor(t5),'t6_key_offered':offered,'t6_offered_count':offered_count,'t6_key_scored':scored,
      'mechanism':mechanism,'t6_threshold_changed':u['thresholds']!=v['thresholds'],
      't6_paid_rounds':nrounds,'crossing_sets_different_rounds':changed_rounds,
      'final_crossing_set_changed':cross_a!=cross_b,'key_first_cross_round_margin':first_cross(u,key),'key_first_cross_round_masked':first_cross(v,key),
      'key_final_activation':u['accumulators_before_residual'].get(key), 'key_evidence':u['normalized_evidence'].get(key),
      'key_final_surplus_margin':final_surplus(u,key),'key_final_surplus_masked':final_surplus(v,key),
      'key_score_rank':score_rank(sc,key),'option_count':len(sc),'key_score':sc[key]['total_score'] if scored else None,
      'masked_winner_score':sc[v['winner_before_control']]['total_score'],
      't6_winner_margin':u['winner_before_control'],'t6_winner_masked':v['winner_before_control'], 'winner_changed':winner_change,
      't6_motor_margin':motor(x),'t6_motor_masked':motor(y),'motor_changed':motor_change,'key_threshold_margin':u['thresholds'].get(key),'key_threshold_masked':v['thresholds'].get(key),
      't5_body_delta_motor':diff(t5['after_motor_world']['body'],t5['before_world']['body']),
      't5_body_delta_after_learning':diff(t5['after_paid_learning_world']['body'],t5['before_world']['body']),
      't6_body_delta_margin_vs_masked_after_motor':diff(x['after_motor_world']['body'],y['after_motor_world']['body']),
      't6_body_delta_margin_vs_masked_after_learning':diff(x['after_paid_learning_world']['body'],y['after_paid_learning_world']['body']),
      'delta_lived_ticks':cold['delta_lived_ticks'],'terminal_body_delta':body_delta,'pareto':cold['pareto']}
    detail=None
    if motor_change:
        require(len(a['steps'])==len(b['steps'])==55,root+' non-T60 divergence')
        detail={'root':root,'t5_before_world':t5['before_world'],'t5_after_paid_learning_world':t5['after_paid_learning_world'], 't5_after_paid_write_world':parts['self_paid_t5']['t5_world'],
                't5_score_witness':scores(t5),'t5_witness':p,'t6_before_world':x['before_world'],'t6_score_witness':sc,
                't6_margin_witness':u,'t6_masked_witness':v,'t6_work':x['cognitive_work'],'t6_bill':x['native_motor']['cognitive_accounting'],
                'trajectory':[]}
        for m,n in zip(a['steps'],b['steps']):
            require(m['t']==n['t'],root+' divergent chronology')
            detail['trajectory'].append({'tick':m['t'],'margin_motor':motor(m),'masked_motor':motor(n),
                'margin_before_body':m['before_world']['body'],'masked_before_body':n['before_world']['body'],
                'margin_after_body':m['after_paid_learning_world']['body'],'masked_after_body':n['after_paid_learning_world']['body'],
                'body_delta':diff(m['after_paid_learning_world']['body'],n['after_paid_learning_world']['body']),
                'margin_position':m['after_paid_learning_world']['position'],'masked_position':n['after_paid_learning_world']['position'],
                'margin_water_cells':m['after_paid_learning_world']['water_cells'],'masked_water_cells':n['after_paid_learning_world']['water_cells'],
                'margin_food_cells':m['after_paid_learning_world']['food_cells'],'masked_food_cells':n['after_paid_learning_world']['food_cells'],
                'margin_work':m['cognitive_work'],'masked_work':n['cognitive_work']})
    return result,detail


def audit_assets(read_asset, open_tar, cold_raw):
    """Audit the literal immutable release assets (not a reconstructed life)."""
    require(sha(cold_raw)==COLD,'wrong cold report')
    cold=json.loads(cold_raw)
    with open_tar() as f:
        require(hashlib.file_digest(f,'sha256').hexdigest()==TAR,
                'wrong immutable original tar')
    require(cold['scientific_run_id']==RUN and cold['source_git_commit']==SOURCE and cold['immutable_raw_release_custody']['target']==CONSUMED and cold['original_tar_sha256']==TAR and cold['verdicts']['status']=='F1N_COMPLETE_SEPARATE_SCIENTIFIC_VERDICTS','wrong immutable cold origin')
    require([r['root'] for r in cold['per_root']]==ROOTS,'wrong cold roots')
    mraw=read_asset('F1N_CUSTODY_MANIFEST.json'); require(sha(mraw)==MANIFEST,'wrong manifest')
    iraw=read_asset('F1N_NATIVE_INDEX.json');require(sha(iraw)==INDEX,'wrong native index')
    m,idx=json.loads(mraw),json.loads(iraw)
    require(m['roots']==ROOTS and m['original_part_count']==336 and m['part_names']==PARTS and m['heldout_native_passes']==1 and m['original_tar_sha256']==TAR and m['checkpoint_count']==48,'wrong manifest contract')
    require([x['origin']['id'] for x in idx['rows']]==ROOTS,'wrong index origins')
    entries={x['path']:x for x in m['entries']}; required={f'{r}/{p}.json.gz' for r in ROOTS for p in PARTS}; checkpoints={f'_checkpoint_{n:02}.json' for n in range(1,49)}
    require(set(entries)==required and len(m['entries'])==336,'wrong manifest paths')
    rows=[]; details=[]; seen=set(); active={}; finished=[]; total_raw=0
    with open_tar() as f, tarfile.open(fileobj=f, mode='r|gz') as t:
        for member in t:
            name=member.name; require(member.isfile() and name in required|checkpoints and name not in seen,'unsafe or unexpected original member')
            seen.add(name); data=t.extractfile(member).read()
            if name in checkpoints:
                n=int(name[12:14]); ck=json.loads(data)
                require(ck['completed']==n and ck['roots']==ROOTS[:n] and ck['entries']==m['entries'][:n*7] and ck['cases']==idx['rows'][:n], 'wrong checkpoint '+name)
                continue
            e=entries[name]; require(len(data)==e['gzip_bytes'] and sha(data)==e['gzip_sha256'],'gzip changed '+name)
            raw=gzip.decompress(data); total_raw+=len(raw); require(len(raw)==e['raw_bytes'] and sha(raw)==e['raw_sha256'],'decoded bytes changed '+name)
            rid,kind=e['id'],e['part']; require(rid in ROOTS and name==f'{rid}/{kind}.json.gz','bad manifest identity')
            # All 336 parts verified at byte level; only three actual parts
            # per root parsed for this additional diagnostic (cold audited all 7).
            if kind in ('self_paid_t5','margin_t6_t60','masked_t6_t60'):
                d=json.loads(raw); require(d['id']==rid and d['part']==kind,'bad native identity')
                active.setdefault(rid,{})[kind]=d['native']
            if rid in active and len(active[rid])==3:
                i=len(finished); require(rid==ROOTS[i],'root order mismatch')
                row,detail=pair_diagnostic(rid,idx['rows'][i],active.pop(rid),cold['per_root'][i]); rows.append(row); finished.append(rid)
                if detail is not None:details.append(detail)
    require(seen==required|checkpoints and not active and finished==ROOTS,'missing originals/checkpoints/roots')
    counts=Counter(r['mechanism'] for r in rows)
    scored=[r for r in rows if r['t6_key_scored']]
    summary={'roots':len(rows),'q_positive':sum(r['q']>0 for r in rows),'q_saturated':sum(r['q']==1. for r in rows),
        'key_known_offered':sum(r['t6_key_offered'] is True for r in rows),'key_offer_unknown':sum(r['t6_key_offered'] is None for r in rows),'key_scored':len(scored),'thresholds_changed':sum(r['t6_threshold_changed'] for r in rows),
        'any_round_crossing_sets_changed':sum(bool(r['crossing_sets_different_rounds']) for r in rows),'final_crossing_sets_changed':sum(r['final_crossing_set_changed'] for r in rows),
        'key_first_cross_round_changed':sum(r['key_first_cross_round_margin']!=r['key_first_cross_round_masked'] for r in scored),
        'key_positive_evidence_when_scored':sum(r['key_evidence']>0 for r in scored),'key_zero_activation_when_scored':sum(r['key_final_activation']==0 for r in scored),
        'all_offered_options_scored_roots':sum(r['t6_offered_count']==r['option_count'] for r in rows),
        'all_pairs_identical_evidence_and_round_snapshots':True,
        'n26_different_actual_motor_ticks':[v['tick'] for d in details if d['root']=='N26' for v in d['trajectory'] if v['margin_motor']!=v['masked_motor']],
        'winner_changed':sum(r['winner_changed'] for r in rows),'motor_changed':sum(r['motor_changed'] for r in rows), 'mechanism_counts':dict(sorted(counts.items())),
        't5_key_counts':dict(sorted(Counter(r['t5_key'] for r in rows).items())),
        'key_scored_root_ids':[r['root'] for r in scored], 'any_round_crossing_sets_changed_roots':[r['root'] for r in rows if r['crossing_sets_different_rounds']],
        'motor_changed_roots':[r['root'] for r in rows if r['motor_changed']],
        'q_median':statistics.median(r['q'] for r in rows), 'q_scored_median':statistics.median(r['q'] for r in scored), 'q_not_scored_median':statistics.median(r['q'] for r in rows if not r['t6_key_scored'])}
    require(summary['motor_changed']==cold['verdicts']['motor_changed_roots'],'diagnostic changed scientific result')
    return {'schema':'i3-stage8f1n-ph1-posthoc-archival-margin/v0','phase':'POSTHOC_DESCRIPTIVE_ARCHIVE_ONLY','run':RUN,'source':SOURCE,'consumed':CONSUMED,
            'known_native_zip_mirror_sha256':NATIVE_ZIP,'known_cold_zip_mirror_sha256':COLD_ZIP,'tar_sha256':TAR,'cold_report_sha256':COLD,
            'verified_original_gzip_count':336,'verified_checkpoint_count':48,'verified_decoded_bytes':total_raw,
            'native_world_steps_executed_by_diagnostic':0,'new_lives_created':0,'scientific_verdict_unchanged':cold['verdicts'],
            'summary':summary,'per_root':rows,'motor_divergence_details':details}


def audit_zip(native_zip, cold_zip):
    require(file_sha(native_zip)==NATIVE_ZIP,'wrong original native artifact ZIP')
    require(file_sha(cold_zip)==COLD_ZIP,'wrong original cold artifact ZIP')
    with zipfile.ZipFile(cold_zip) as z:
        raw=z.read('F1N_INDEPENDENT_COLD_T60.json')
    with zipfile.ZipFile(native_zip) as z:
        return audit_assets(
            lambda name:z.read('f1n-originals/'+name),
            lambda:z.open('f1n-originals/F1N_ORIGINALS_336_GZIP.tar.gz'), raw)


def audit_release(raw_dir, cold_report):
    raw_dir=Path(raw_dir)
    return audit_assets(lambda name:(raw_dir/name).read_bytes(),
        lambda:(raw_dir/'F1N_ORIGINALS_336_GZIP.tar.gz').open('rb'),
        Path(cold_report).read_bytes())


def main():
    p=argparse.ArgumentParser(description=__doc__)
    source=p.add_mutually_exclusive_group(required=True)
    source.add_argument('--native-zip',type=Path)
    source.add_argument('--raw-dir',type=Path)
    p.add_argument('--cold-zip',type=Path)
    p.add_argument('--cold-report',type=Path)
    p.add_argument('--output',required=True,type=Path)
    a=p.parse_args()
    if a.native_zip is not None and a.cold_zip is not None and a.cold_report is None:
        result=audit_zip(a.native_zip,a.cold_zip)
    elif a.raw_dir is not None and a.cold_report is not None and a.cold_zip is None:
        result=audit_release(a.raw_dir,a.cold_report)
    else:
        p.error('use --native-zip with --cold-zip, or --raw-dir with --cold-report')
    with a.output.open('x',encoding='utf-8') as f: json.dump(result,f,indent=2,sort_keys=True,allow_nan=False);f.write('\n')
    print(json.dumps(result['summary'],sort_keys=True));print('F1N_PH1_ARCHIVE_ONLY_PASS',file_sha(a.output))


if __name__=='__main__':
    main()
